from django.db.models import Case, When, Value, IntegerField
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.opportunity.models import Opportunity
from apps.enterprise.models import Enterprise
from apps.feed.models import Feed
from .serializers import (
    SearchOpportunitySerializer,
    SearchEnterpriseSerializer,
    SearchFeedSerializer,
)

PAGE_SIZE = 20
VALID_TABS = {'opp', 'ent', 'feed'}


class SearchView(APIView):
    """Global search across opportunities, enterprises, and feeds.

    GET /api/v1/search?keyword=xxx&tab=opp|ent|feed&page=1&page_size=20

    Permission: AllowAny (public).
    """

    permission_classes = [AllowAny]

    def get(self, request):
        keyword = request.query_params.get('keyword', '').strip()
        tab = request.query_params.get('tab', '').strip().lower()
        page = self._positive_int(request.query_params.get('page', '1'), default=1)
        page_size = self._positive_int(
            request.query_params.get('page_size', str(PAGE_SIZE)),
            default=PAGE_SIZE,
            max_val=PAGE_SIZE,
        )

        if not keyword:
            return Response(
                {'code': 400, 'message': 'keyword is required'},
                status=400,
            )

        if tab and tab not in VALID_TABS:
            return Response(
                {'code': 400, 'message': f'invalid tab: {tab}'},
                status=400,
            )

        data = {}

        if not tab or tab == 'opp':
            data['opp'] = self._search_opportunities(keyword, page, page_size)

        if not tab or tab == 'ent':
            data['ent'] = self._search_enterprises(keyword, page, page_size)

        if not tab or tab == 'feed':
            data['feed'] = self._search_feeds(keyword, page, page_size)

        return Response({'code': 200, 'data': data})

    def _search_opportunities(self, keyword, page, page_size):
        """Search ACTIVE opportunities by title (ICONTAINS).

        Relevance sorting: exact match first, then partial match.
        """
        qs = (
            Opportunity.objects
            .filter(status=Opportunity.OppStatus.ACTIVE)
            .filter(title__icontains=keyword)
            .select_related('enterprise')
            .annotate(
                _relevance=Case(
                    When(title__iexact=keyword, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by('_relevance', '-created_at')
        )
        total = qs.count()
        start = (page - 1) * page_size
        items = qs[start:start + page_size]
        serializer = SearchOpportunitySerializer(items, many=True)
        return {'items': serializer.data, 'total': total}

    def _search_enterprises(self, keyword, page, page_size):
        """Search VERIFIED enterprises by name (ICONTAINS).

        Relevance sorting: exact match first, then partial match.
        """
        qs = (
            Enterprise.objects
            .filter(auth_status=Enterprise.AuthStatus.VERIFIED)
            .filter(name__icontains=keyword)
            .annotate(
                _relevance=Case(
                    When(name__iexact=keyword, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by('_relevance', '-created_at')
        )
        total = qs.count()
        start = (page - 1) * page_size
        items = qs[start:start + page_size]
        serializer = SearchEnterpriseSerializer(items, many=True)
        return {'items': serializer.data, 'total': total}

    def _search_feeds(self, keyword, page, page_size):
        """Search ACTIVE feeds by content (ICONTAINS).

        Relevance sorting: exact match first, then partial match.
        """
        qs = (
            Feed.objects
            .filter(status=Feed.FeedStatus.ACTIVE)
            .filter(content__icontains=keyword)
            .select_related('publisher', 'enterprise')
            .annotate(
                _relevance=Case(
                    When(content__iexact=keyword, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by('_relevance', '-created_at')
        )
        total = qs.count()
        start = (page - 1) * page_size
        items = qs[start:start + page_size]
        serializer = SearchFeedSerializer(items, many=True)
        return {'items': serializer.data, 'total': total}

    @staticmethod
    def _positive_int(value, default=1, max_val=None):
        """Parse a positive integer from a string, with bounds."""
        try:
            result = int(value)
            if result < 1:
                return default
            if max_val and result > max_val:
                return max_val
            return result
        except (ValueError, TypeError):
            return default
