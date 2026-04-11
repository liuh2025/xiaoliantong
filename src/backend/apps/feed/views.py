import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.enterprise.models import Enterprise
from apps.feed.models import Feed
from apps.feed.serializers import (
    FeedListSerializer,
    FeedDetailSerializer,
    FeedCreateSerializer,
    FeedNewestSerializer,
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


def _can_manage(user, feed_obj):
    """Check whether *user* can manage (edit/delete/offline) *feed_obj*."""
    # Publisher can always manage
    if feed_obj.publisher == user:
        return True
    # Enterprise admin of the same enterprise can manage
    profile = _get_user_profile(user)
    if (
        profile
        and profile.enterprise_id == feed_obj.enterprise_id
        and profile.role_code == 'enterprise_admin'
    ):
        return True
    return False


# ==================== FEED-002: Feed List + FEED-004: Create ====================


class FeedListView(APIView):
    """GET/POST /feed/feed - List feeds (GET) or create (POST)."""

    def get_permissions(self):
        """GET (list) is public; POST (create) requires authentication."""
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def get(self, request):
        """List ACTIVE feeds with keyword search and pagination."""
        queryset = Feed.objects.filter(
            status=Feed.FeedStatus.ACTIVE,
        ).select_related('publisher', 'enterprise')

        # Keyword search on content
        keyword = request.query_params.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(content__icontains=keyword)

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

        serializer = FeedListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })

    def post(self, request):
        """Create a feed post for the user's verified enterprise."""
        enterprise = _get_user_enterprise(request.user)
        if not enterprise:
            return _error_response('用户未绑定已认证企业', 403)

        serializer = FeedCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        images = serializer.validated_data.get('images', [])
        if images and len(images) > 9:
            return _error_response('图片数量不能超过9张', 400)

        try:
            feed = Feed(
                publisher=request.user,
                enterprise=enterprise,
                content=serializer.validated_data['content'],
                images=images,
            )
            feed.save()
        except Exception as exc:
            logger.error(f"Failed to create feed: {exc}")
            return _error_response('创建失败，请稍后重试', 500)

        return _success_response({'id': feed.id, 'status': feed.status})


# ==================== FEED-003: Detail + FEED-005: Delete ====================


class FeedDetailView(APIView):
    """GET/DELETE /feed/feed/{id} - Detail or delete."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Return feed detail."""
        try:
            feed = Feed.objects.select_related(
                'publisher', 'enterprise',
            ).get(pk=pk)
        except Feed.DoesNotExist:
            return _error_response('动态不存在', 404)

        # OFFLINE feeds are only visible to publisher and enterprise admin
        if feed.status == Feed.FeedStatus.OFFLINE:
            if not _can_manage(request.user, feed):
                return _error_response('动态不存在', 404)

        serializer = FeedDetailSerializer(feed, context={'request': request})
        return _success_response(serializer.data)

    def delete(self, request, pk):
        """Delete feed (publisher or enterprise admin only)."""
        try:
            feed = Feed.objects.get(pk=pk)
        except Feed.DoesNotExist:
            return _error_response('动态不存在', 404)

        if not _can_manage(request.user, feed):
            return _error_response('无权操作', 403)

        feed.delete()
        return _success_response({'message': '删除成功'})


# ==================== FEED-006: Offline ====================


class FeedOfflineView(APIView):
    """PUT /feed/feed/{id}/offline - Set feed status to OFFLINE."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """Set ACTIVE feed to OFFLINE."""
        try:
            feed = Feed.objects.get(pk=pk)
        except Feed.DoesNotExist:
            return _error_response('动态不存在', 404)

        if not _can_manage(request.user, feed):
            return _error_response('无权操作', 403)

        if feed.status != Feed.FeedStatus.ACTIVE:
            return _error_response('动态已下架', 400)

        feed.status = Feed.FeedStatus.OFFLINE
        feed.save(update_fields=['status', 'updated_at'])
        return _success_response({'id': feed.id, 'status': feed.status})


# ==================== FEED-007: Newest ====================


class FeedNewestView(APIView):
    """GET /feed/feed/newest - Return the 2 newest ACTIVE feeds."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return the 2 newest ACTIVE feeds from verified enterprises."""
        queryset = Feed.objects.filter(
            status=Feed.FeedStatus.ACTIVE,
            enterprise__auth_status=Enterprise.AuthStatus.VERIFIED,
        ).select_related('publisher', 'enterprise').order_by('-created_at')[:2]

        serializer = FeedNewestSerializer(list(queryset), many=True)
        return _success_response({'items': serializer.data})
