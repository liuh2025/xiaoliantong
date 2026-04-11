import logging

from django.db import connection
from django.db.models import Count, F, OuterRef, Q, Subquery
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.enterprise.models import Enterprise
from apps.opportunity.models import Opportunity, ContactLog
from apps.opportunity.serializers import (
    OpportunityListSerializer,
    OpportunityDetailSerializer,
    OpportunityCreateSerializer,
    OpportunityUpdateSerializer,
)

logger = logging.getLogger(__name__)


def _success_response(data=None):
    """Build a standard success response."""
    return Response(
        {'code': 200, 'message': 'success', 'data': data},
        status=status.HTTP_200_OK,
    )


def _error_response(message, code=400):
    """Build a standard error response."""
    return Response(
        {'code': code, 'message': message, 'data': None},
        status=status.HTTP_200_OK,
    )


def _get_user_profile(user):
    """Return UserProfile for *user*, or None."""
    try:
        return user.ent_user_profile
    except Exception:
        return None


def _get_user_enterprise(user):
    """Return the VERIFIED Enterprise bound to *user*, or None."""
    profile = _get_user_profile(user)
    if not profile or not profile.enterprise_id:
        return None
    try:
        return Enterprise.objects.get(
            id=profile.enterprise_id,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
    except Enterprise.DoesNotExist:
        return None


# ==================== OPP-002: Opportunity List + OPP-004: Create ====================


class OpportunityListView(APIView):
    """GET/POST /opp/opportunity - List opportunities (GET) or create (POST)."""

    def get_permissions(self):
        """GET (list) is public; POST (create) requires authentication."""
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def get(self, request):
        """List ACTIVE opportunities with filtering, keyword search and pagination."""
        queryset = Opportunity.objects.filter(
            status=Opportunity.OppStatus.ACTIVE,
        )

        queryset = self._apply_filters(queryset, request.query_params)

        # Keyword search on title and detail
        keyword = request.query_params.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(detail__icontains=keyword),
            )

        queryset = queryset.order_by('-created_at')

        # Manual pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        total = queryset.count()
        offset = (page - 1) * page_size
        items = queryset[offset:offset + page_size]

        serializer = OpportunityListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })

    def post(self, request):
        """Create an opportunity for the user's verified enterprise."""
        enterprise = _get_user_enterprise(request.user)
        if not enterprise:
            return _error_response('用户未绑定已认证企业', 403)

        serializer = OpportunityCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        try:
            opp = Opportunity(
                type=serializer.validated_data['type'],
                title=serializer.validated_data['title'],
                enterprise=enterprise,
                publisher=request.user,
                industry_id=serializer.validated_data['industry_id'],
                sub_industry_id=serializer.validated_data['sub_industry_id'],
                category_id=serializer.validated_data['category_id'],
                province_id=serializer.validated_data['province_id'],
                region_id=serializer.validated_data['region_id'],
                detail=serializer.validated_data['detail'],
                tags=serializer.validated_data.get('tags', []),
                contact_name=serializer.validated_data['contact_name'],
                contact_phone=serializer.validated_data['contact_phone'],
                contact_wechat=serializer.validated_data.get('contact_wechat', ''),
            )
            opp.save()
        except Exception as exc:
            logger.error(f"Failed to create opportunity: {exc}")
            return _error_response('创建失败，请稍后重试', 500)

        return _success_response({'id': opp.id, 'status': opp.status})

    def _apply_filters(self, queryset, params):
        """Apply field-based filters from query params."""
        filter_mapping = {
            'type': 'type',
            'industry_id': 'industry_id',
            'sub_industry_id': 'sub_industry_id',
            'category_id': 'category_id',
            'province_id': 'province_id',
            'region_id': 'region_id',
        }
        for param_name, field_name in filter_mapping.items():
            value = params.get(param_name)
            if value is not None:
                if field_name == 'type':
                    queryset = queryset.filter(type=value)
                else:
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        continue
                    queryset = queryset.filter(**{field_name: value})

        # Tags filter (OR logic for comma-separated values)
        tags_param = params.get('tags')
        if tags_param:
            tag_list = [t.strip() for t in tags_param.split(',') if t.strip()]
            if tag_list:
                queryset = self._filter_by_tags(queryset, tag_list)

        return queryset

    @staticmethod
    def _filter_by_tags(queryset, tag_list):
        """Filter by tags JSON field, compatible with MySQL and SQLite."""
        if connection.vendor == 'sqlite':
            matching_ids = []
            for opp in queryset.only('id', 'tags'):
                if opp.tags and isinstance(opp.tags, list):
                    if any(tag in opp.tags for tag in tag_list):
                        matching_ids.append(opp.id)
            return queryset.filter(id__in=matching_ids)
        else:
            q = Q()
            for tag in tag_list:
                q |= Q(tags__contains=[tag])
            return queryset.filter(q)


# ==================== OPP-003/005/006: Detail / Update / Delete ====================


class OpportunityDetailView(APIView):
    """GET/PUT/DELETE /opp/opportunity/{id} - Detail, update, or delete."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Return detail and atomically increment view_count."""
        try:
            opp = Opportunity.objects.select_related(
                'enterprise', 'publisher',
            ).get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        # Atomically increment view_count
        Opportunity.objects.filter(pk=opp.pk).update(
            view_count=F('view_count') + 1,
        )
        opp.refresh_from_db()

        serializer = OpportunityDetailSerializer(
            opp, context={'request': request},
        )
        return _success_response(serializer.data)

    def put(self, request, pk):
        """Update opportunity (publisher or enterprise admin only; type immutable)."""
        try:
            opp = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        # Permission check: publisher or enterprise admin
        if not self._can_edit(request.user, opp):
            return _error_response('无权操作', 403)

        serializer = OpportunityUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        updatable_fields = [
            'title', 'industry_id', 'sub_industry_id', 'category_id',
            'province_id', 'region_id', 'detail', 'tags',
            'contact_name', 'contact_phone', 'contact_wechat',
        ]
        validated = serializer.validated_data
        update_fields = ['updated_at']
        for field in updatable_fields:
            if field in validated:
                setattr(opp, field, validated[field])
                update_fields.append(field)

        opp.save(update_fields=update_fields)
        return _success_response({'id': opp.id, 'status': opp.status})

    def delete(self, request, pk):
        """Delete opportunity (publisher or enterprise admin only)."""
        try:
            opp = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        if not self._can_edit(request.user, opp):
            return _error_response('无权操作', 403)

        opp.delete()
        return _success_response({'message': '删除成功'})

    def _can_edit(self, user, opp):
        """Check whether *user* can edit/delete *opp* (publisher or enterprise admin)."""
        if opp.publisher == user:
            return True
        profile = _get_user_profile(user)
        if (
            profile
            and profile.enterprise_id == opp.enterprise_id
            and profile.role_code == 'enterprise_admin'
        ):
            return True
        return False


# ==================== OPP-007: Offline / Republish ====================


class OpportunityOfflineView(APIView):
    """PUT /opp/opportunity/{id}/offline - Toggle ACTIVE <-> OFFLINE."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """Toggle opportunity status between ACTIVE and OFFLINE."""
        try:
            opp = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        if not self._can_toggle(request.user, opp):
            return _error_response('无权操作', 403)

        if opp.status == Opportunity.OppStatus.ACTIVE:
            opp.status = Opportunity.OppStatus.OFFLINE
        else:
            opp.status = Opportunity.OppStatus.ACTIVE

        opp.save(update_fields=['status', 'updated_at'])
        return _success_response({'id': opp.id, 'status': opp.status})

    def _can_toggle(self, user, opp):
        """Check whether *user* can toggle *opp* status."""
        if opp.publisher == user:
            return True
        profile = _get_user_profile(user)
        if (
            profile
            and profile.enterprise_id == opp.enterprise_id
            and profile.role_code == 'enterprise_admin'
        ):
            return True
        return False


# ==================== OPP-008: Get Contact Info ====================


class OpportunityContactView(APIView):
    """POST /opp/opportunity/{id}/contact - Get full contact info and log it."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Return full contact info for an ACTIVE opportunity and create ContactLog."""
        # 1. Check user has verified enterprise
        enterprise = _get_user_enterprise(request.user)
        if not enterprise:
            return _error_response('用户未绑定已认证企业', 403)

        # 2. Fetch opportunity
        try:
            opp = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        # 3. Check opportunity is ACTIVE
        if opp.status != Opportunity.OppStatus.ACTIVE:
            return _error_response('商机已下架，无法获取联系方式', 400)

        # 4. Create ContactLog record
        ContactLog.objects.create(
            opportunity=opp,
            getter_user=request.user,
            getter_enterprise=enterprise,
            status=ContactLog.ContactStatus.COMPLETED,
        )

        # 5. Return full (non-masked) contact info
        return _success_response({
            'contact_name': opp.contact_name or '',
            'contact_phone': opp.contact_phone or '',
            'contact_wechat': opp.contact_wechat or '',
        })


# ==================== OPP-009: Smart Recommended ====================


class OpportunityRecommendedView(APIView):
    """GET /opp/opportunity/recommended - Smart recommended opportunities."""

    permission_classes = [AllowAny]
    PAGE_SIZE = 4

    # Recommendation factor weights
    WEIGHT_VIEW_COUNT = 0.25
    WEIGHT_CONTACT_COUNT = 0.30
    WEIGHT_RECENCY = 0.25
    WEIGHT_INDUSTRY_MATCH = 0.20

    def get(self, request):
        """Return up to 4 recommended opportunities based on user context."""
        queryset = Opportunity.objects.filter(
            status=Opportunity.OppStatus.ACTIVE,
        )

        # Exclude own enterprise's opportunities if logged in + has enterprise
        user_enterprise = self._get_requester_enterprise(request)
        if user_enterprise:
            queryset = queryset.exclude(enterprise_id=user_enterprise.id)

        # If not enough data, just return empty
        if not queryset.exists():
            return _success_response({'items': []})

        # Annotate with contact_count (via ContactLog)
        contact_count_sq = ContactLog.objects.filter(
            opportunity=OuterRef('pk'),
        ).values('opportunity').annotate(cnt=Count('id')).values('cnt')
        queryset = queryset.annotate(
            contact_count=Subquery(contact_count_sq, output_field=None),
        )

        # Calculate user context for recommendation strategy
        user_industry_id = None
        if user_enterprise:
            user_industry_id = user_enterprise.industry_id

        # Compute scores and select
        scored = list(queryset)
        for opp in scored:
            opp._rec_score = self._compute_score(
                opp, user_industry_id,
            )

        # Sort by score descending
        scored.sort(key=lambda o: o._rec_score, reverse=True)

        # Take top items
        items = scored[:self.PAGE_SIZE]

        serializer = OpportunityListSerializer(items, many=True)
        return _success_response({'items': serializer.data})

    def _get_requester_enterprise(self, request):
        """Return the user's verified enterprise, or None."""
        if not request.user or not request.user.is_authenticated:
            return None
        return _get_user_enterprise(request.user)

    def _compute_score(self, opp, user_industry_id):
        """Compute a weighted recommendation score for an opportunity."""
        # Normalize view_count (cap at 100)
        view_score = min(opp.view_count or 0, 100) / 100.0

        # Normalize contact_count (cap at 50)
        contact_score = min(opp.contact_count or 0, 50) / 50.0

        # Recency score: highest for 7 days, decays after
        days_since = (timezone.now() - opp.created_at).days
        if days_since <= 7:
            recency_score = 1.0
        elif days_since <= 30:
            recency_score = 0.5
        elif days_since <= 90:
            recency_score = 0.2
        else:
            recency_score = 0.1

        # Industry match: only if user has enterprise
        if user_industry_id:
            industry_score = 1.0 if opp.industry_id == user_industry_id else 0.0
        else:
            industry_score = 0.0

        score = (
            self.WEIGHT_VIEW_COUNT * view_score
            + self.WEIGHT_CONTACT_COUNT * contact_score
            + self.WEIGHT_RECENCY * recency_score
            + self.WEIGHT_INDUSTRY_MATCH * industry_score
        )
        return score
