import logging
from datetime import timedelta

from django.db.models import Q, Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission

from apps.enterprise.models import Enterprise, AuditRecord, MasterData
from apps.auth_app.models import UserProfile
from apps.opportunity.models import Opportunity, ContactLog
from apps.feed.models import Feed
from apps.msg.views import create_notification
from .serializers import (
    PlatformProfileSerializer,
    AuditEnterpriseListSerializer,
    AuditRejectSerializer,
    TenantEnterpriseListSerializer,
    TenantEnterpriseDetailSerializer,
    TenantMemberCreateSerializer,
    TenantMemberUpdateSerializer,
    PlatOpportunityListSerializer,
    PlatOpportunityDetailSerializer,
    ContentOfflineSerializer,
    PlatFeedListSerializer,
    PlatFeedDetailSerializer,
    MasterDataListSerializer,
    MasterDataCreateSerializer,
    MasterDataUpdateSerializer,
    RoleSerializer,
    RolePermissionSerializer,
    RolePermissionUpdateSerializer,
    SettingsSerializer,
)

logger = logging.getLogger(__name__)


# ==================== Helpers ====================


def _success_response(data=None):
    """Build a standard success response."""
    return Response(
        {'code': 200, 'message': 'success', 'data': data},
        status=http_status.HTTP_200_OK,
    )


def _error_response(message, code=400):
    """Build a standard error response."""
    return Response(
        {'code': code, 'message': message, 'data': None},
        status=http_status.HTTP_200_OK,
    )


def _is_platform_admin(user):
    """Check if user has platform admin role."""
    if not user or not user.is_authenticated:
        return False
    try:
        return user.ent_user_profile.role_code in (
            'super_admin', 'platform_operator',
        )
    except Exception:
        return False


class PlatformAdminPermission(BasePermission):
    """Permission class for platform admin endpoints."""

    def has_permission(self, request, view):
        return _is_platform_admin(request.user)


ROLE_DISPLAY = {
    'super_admin': '超级管理员',
    'platform_operator': '平台运营',
    'enterprise_admin': '企业管理员',
    'employee': '企业员工',
    'guest': '游客',
}


def _paginate(queryset, request):
    """Apply manual pagination to a queryset."""
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    total = queryset.count()
    offset = (page - 1) * page_size
    items = queryset[offset:offset + page_size]
    return items, total, page, page_size


FIXED_ROLES = [
    {
        'id': 1,
        'name': '超级管理员',
        'code': 'super_admin',
        'description': '拥有系统所有权限，可管理平台配置、用户、角色等',
    },
    {
        'id': 2,
        'name': '平台运营',
        'code': 'platform_operator',
        'description': '负责企业审核、内容管理、数据查看等运营工作',
    },
    {
        'id': 3,
        'name': '企业管理员',
        'code': 'enterprise_admin',
        'description': '管理本企业信息、员工、商机等',
    },
    {
        'id': 4,
        'name': '企业员工',
        'code': 'employee',
        'description': '查看和使用企业资源，发布商机和动态',
    },
    {
        'id': 5,
        'name': '游客',
        'code': 'guest',
        'description': '仅可浏览公开信息',
    },
]

FIXED_PERMISSIONS = {
    1: ['dashboard', 'audit', 'tenant', 'content', 'master_data', 'role', 'settings'],
    2: ['dashboard', 'audit', 'tenant', 'content', 'master_data'],
    3: ['enterprise', 'opportunity', 'feed', 'member'],
    4: ['enterprise', 'opportunity', 'feed'],
    5: ['public'],
}


# ==================== PLAT-001: Profile & Notification ====================


class PlatformProfileView(APIView):
    """GET /api/v1/plat-admin/profile - Get platform admin profile."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        profile = request.user.ent_user_profile
        data = {
            'id': request.user.id,
            'name': profile.real_name or request.user.username,
            'role_code': profile.role_code,
            'role_name': ROLE_DISPLAY.get(profile.role_code, ''),
        }
        serializer = PlatformProfileSerializer(data)
        return _success_response(serializer.data)


class PlatformNotificationListView(APIView):
    """GET /api/v1/plat-admin/notification - List notifications for platform admin."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        from apps.msg.models import Message

        queryset = Message.objects.filter(
            receiver=request.user,
        ).select_related('sender').order_by('-created_at')

        # Filter by is_read
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() in ('true', '1', 'yes'):
                queryset = queryset.filter(is_read=True)
            elif is_read.lower() in ('false', '0', 'no'):
                queryset = queryset.filter(is_read=False)

        items, total, page, page_size = _paginate(queryset, request)

        from apps.msg.serializers import MessageListSerializer
        serializer = MessageListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })


class PlatformNotificationReadAllView(APIView):
    """POST /api/v1/plat-admin/notification/read-all - Mark all notifications read."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def post(self, request):
        from apps.msg.models import Message

        updated = Message.objects.filter(
            receiver=request.user, is_read=False,
        ).update(is_read=True)
        return _success_response({'updated_count': updated})


# ==================== PLAT-002: Dashboard ====================


class DashboardStatsView(APIView):
    """GET /api/v1/plat-admin/dashboard/stats - Dashboard statistics."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        now = timezone.now()
        last_month = now - timedelta(days=30)

        # Current counts
        enterprise_count = Enterprise.objects.count()
        opportunity_count = Opportunity.objects.count()
        deal_count = ContactLog.objects.filter(
            status=ContactLog.ContactStatus.COMPLETED,
        ).count()
        active_user_count = UserProfile.objects.filter(
            user__is_active=True,
        ).count()
        pending_audit_count = AuditRecord.objects.filter(
            status=AuditRecord.AuditStatus.PENDING,
        ).count()

        # Previous period counts for trend calculation
        prev_enterprise = Enterprise.objects.filter(created_at__lt=last_month).count()
        prev_opportunity = Opportunity.objects.filter(created_at__lt=last_month).count()
        prev_deal = ContactLog.objects.filter(
            status=ContactLog.ContactStatus.COMPLETED,
            created_at__lt=last_month,
        ).count()

        def _calc_trend(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return round((current - previous) / previous * 100, 1)

        data = {
            'enterprise_count': enterprise_count,
            'opportunity_count': opportunity_count,
            'deal_count': deal_count,
            'active_user_count': active_user_count,
            'pending_audit_count': pending_audit_count,
            'enterprise_trend': _calc_trend(enterprise_count, prev_enterprise),
            'opportunity_trend': _calc_trend(opportunity_count, prev_opportunity),
            'deal_trend': _calc_trend(deal_count, prev_deal),
        }
        return _success_response(data)


class DashboardTrendView(APIView):
    """GET /api/v1/plat-admin/dashboard/trend - Dashboard trend data."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        period = int(request.query_params.get('period', 30))
        if period < 1:
            period = 30
        since = timezone.now() - timedelta(days=period)

        trend_type = request.query_params.get('type', 'opportunity')

        data = {}
        if trend_type in ('opportunity', None):
            qs = Opportunity.objects.filter(created_at__gte=since).annotate(
                date=TruncDay('created_at'),
            ).values('date').annotate(count=Count('id')).order_by('date')
            data['opportunity_trend'] = [
                {'date': item['date'], 'count': item['count']} for item in qs
            ]

        if trend_type in ('enterprise', None):
            qs = Enterprise.objects.filter(created_at__gte=since).annotate(
                date=TruncDay('created_at'),
            ).values('date').annotate(count=Count('id')).order_by('date')
            data['enterprise_trend'] = [
                {'date': item['date'], 'count': item['count']} for item in qs
            ]

        if trend_type in ('deal', None):
            qs = ContactLog.objects.filter(
                status=ContactLog.ContactStatus.COMPLETED,
                created_at__gte=since,
            ).annotate(
                date=TruncDay('created_at'),
            ).values('date').annotate(count=Count('id')).order_by('date')
            data['deal_trend'] = [
                {'date': item['date'], 'count': item['count']} for item in qs
            ]

        return _success_response(data)


# ==================== PLAT-003: Enterprise Audit ====================


class AuditEnterpriseListView(APIView):
    """GET /api/v1/plat-admin/audit/enterprise - List enterprise audit records."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        queryset = AuditRecord.objects.select_related(
            'enterprise', 'enterprise__admin_user',
        )

        # Filter by status
        audit_status = request.query_params.get('status', '').strip()
        if audit_status:
            queryset = queryset.filter(status=audit_status)

        # Keyword search on enterprise name or credit_code
        keyword = request.query_params.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(enterprise__name__icontains=keyword)
                | Q(enterprise__credit_code__icontains=keyword),
            )

        queryset = queryset.order_by('-created_at')
        items, total, page, page_size = _paginate(queryset, request)

        serializer = AuditEnterpriseListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })


class AuditEnterpriseApproveView(APIView):
    """POST /api/v1/plat-admin/audit/enterprise/{id}/approve - Approve enterprise."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def post(self, request, pk):
        try:
            audit_record = AuditRecord.objects.select_related(
                'enterprise', 'enterprise__admin_user',
            ).get(pk=pk)
        except AuditRecord.DoesNotExist:
            return _error_response('审核记录不存在', 404)

        if audit_record.status != AuditRecord.AuditStatus.PENDING:
            return _error_response('该记录不是待审核状态', 400)

        enterprise = audit_record.enterprise

        # Update audit record
        audit_record.status = AuditRecord.AuditStatus.APPROVED
        audit_record.auditor = request.user
        audit_record.save(update_fields=['status', 'auditor'])

        # Update enterprise auth status
        enterprise.auth_status = Enterprise.AuthStatus.VERIFIED
        enterprise.save(update_fields=['auth_status', 'updated_at'])

        # Update applicant role to enterprise_admin
        if enterprise.admin_user:
            try:
                profile = enterprise.admin_user.ent_user_profile
                profile.role_code = 'enterprise_admin'
                profile.save(update_fields=['role_code', 'updated_at'])
            except Exception:
                pass

            # Send notification
            create_notification(
                receiver=enterprise.admin_user,
                type='AUDIT_APPROVED',
                title='企业认证审核通过',
                content=f'您的企业「{enterprise.name}」已通过认证审核。',
                related_type='enterprise',
                related_id=enterprise.id,
            )

        return _success_response({'message': '审核通过'})


class AuditEnterpriseRejectView(APIView):
    """POST /api/v1/plat-admin/audit/enterprise/{id}/reject - Reject enterprise."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def post(self, request, pk):
        try:
            audit_record = AuditRecord.objects.select_related(
                'enterprise', 'enterprise__admin_user',
            ).get(pk=pk)
        except AuditRecord.DoesNotExist:
            return _error_response('审核记录不存在', 404)

        if audit_record.status != AuditRecord.AuditStatus.PENDING:
            return _error_response('该记录不是待审核状态', 400)

        serializer = AuditRejectSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请提供驳回原因', 400)

        reason = serializer.validated_data['reason']
        enterprise = audit_record.enterprise

        # Update audit record
        audit_record.status = AuditRecord.AuditStatus.REJECTED
        audit_record.auditor = request.user
        audit_record.audit_reason = reason
        audit_record.save(update_fields=['status', 'auditor', 'audit_reason'])

        # Update enterprise auth status
        enterprise.auth_status = Enterprise.AuthStatus.REJECTED
        enterprise.save(update_fields=['auth_status', 'updated_at'])

        # Send notification
        if enterprise.admin_user:
            create_notification(
                receiver=enterprise.admin_user,
                type='AUDIT_REJECTED',
                title='企业认证审核驳回',
                content=f'您的企业「{enterprise.name}」认证审核被驳回。原因：{reason}',
                related_type='enterprise',
                related_id=enterprise.id,
            )

        return _success_response({'message': '审核驳回'})


# ==================== PLAT-004: Tenant Management ====================


class TenantEnterpriseListView(APIView):
    """GET /api/v1/plat-admin/tenant/enterprise - List enterprises for tenant mgmt."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        queryset = Enterprise.objects.all()

        # Filter by keyword
        keyword = request.query_params.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(credit_code__icontains=keyword),
            )

        # Filter by status
        ent_status = request.query_params.get('status', '').strip()
        if ent_status:
            queryset = queryset.filter(auth_status=ent_status)

        # Filter by is_active
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ('true', '1', 'yes'):
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ('false', '0', 'no'):
                queryset = queryset.filter(is_active=False)

        queryset = queryset.order_by('-created_at')
        items, total, page, page_size = _paginate(queryset, request)

        serializer = TenantEnterpriseListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })


class TenantEnterpriseDetailView(APIView):
    """GET /api/v1/plat-admin/tenant/enterprise/{id} - Enterprise detail with members."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request, pk):
        try:
            enterprise = Enterprise.objects.get(pk=pk)
        except Enterprise.DoesNotExist:
            return _error_response('企业不存在', 404)

        serializer = TenantEnterpriseDetailSerializer(enterprise)
        return _success_response(serializer.data)


class TenantEnterpriseToggleStatusView(APIView):
    """PUT /api/v1/plat-admin/tenant/enterprise/{id}/toggle-status - Toggle is_active."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def put(self, request, pk):
        try:
            enterprise = Enterprise.objects.get(pk=pk)
        except Enterprise.DoesNotExist:
            return _error_response('企业不存在', 404)

        was_active = enterprise.is_active
        enterprise.is_active = not enterprise.is_active
        enterprise.save(update_fields=['is_active', 'updated_at'])

        if was_active and not enterprise.is_active:
            # Disable cascade: disable all members + offline all opportunities
            from django.contrib.auth.models import User
            member_ids = UserProfile.objects.filter(
                enterprise_id=enterprise.id,
            ).values_list('user_id', flat=True)
            User.objects.filter(id__in=member_ids).update(is_active=False)

            from apps.opportunity.models import Opportunity
            Opportunity.objects.filter(
                enterprise_id=enterprise.id,
                status=Opportunity.OppStatus.ACTIVE,
            ).update(status=Opportunity.OppStatus.OFFLINE)
        elif not was_active and enterprise.is_active:
            # Re-enable: re-activate all members
            from django.contrib.auth.models import User
            member_ids = UserProfile.objects.filter(
                enterprise_id=enterprise.id,
            ).values_list('user_id', flat=True)
            User.objects.filter(id__in=member_ids).update(is_active=True)

        return _success_response({
            'id': enterprise.id,
            'is_active': enterprise.is_active,
        })


class TenantMemberListView(APIView):
    """GET/POST /api/v1/plat-admin/tenant/enterprise/{id}/member - List or add members."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request, pk):
        try:
            enterprise = Enterprise.objects.get(pk=pk)
        except Enterprise.DoesNotExist:
            return _error_response('企业不存在', 404)

        profiles = UserProfile.objects.filter(
            enterprise_id=enterprise.id,
        ).select_related('user').order_by('-created_at')

        from .serializers import TenantMemberListSerializer
        serializer = TenantMemberListSerializer(profiles, many=True)
        return _success_response({'items': serializer.data})

    def post(self, request, pk):
        try:
            enterprise = Enterprise.objects.get(pk=pk)
        except Enterprise.DoesNotExist:
            return _error_response('企业不存在', 404)

        serializer = TenantMemberCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        phone = serializer.validated_data['phone']
        real_name = serializer.validated_data['real_name']
        position = serializer.validated_data.get('position')
        role_code = serializer.validated_data['role_code']

        from django.contrib.auth.models import User
        try:
            target_user = User.objects.get(username=phone)
        except User.DoesNotExist:
            return _error_response('用户未注册', 400)

        try:
            target_profile = target_user.ent_user_profile
            if target_profile.enterprise_id and target_profile.enterprise_id != enterprise.id:
                return _error_response('用户已绑定其他企业', 400)
        except Exception:
            target_profile = UserProfile.objects.create(
                user=target_user,
                role_code='guest',
            )

        target_profile.enterprise_id = enterprise.id
        target_profile.role_code = role_code
        target_profile.real_name = real_name
        if position:
            target_profile.position = position
        target_profile.save()

        return _success_response({
            'id': target_user.id,
            'message': '员工添加成功',
        })


class TenantMemberDetailView(APIView):
    """PUT /api/v1/plat-admin/tenant/member/{id} - Update member."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def put(self, request, pk):
        from django.contrib.auth.models import User

        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return _error_response('用户不存在', 404)

        try:
            target_profile = target_user.ent_user_profile
        except Exception:
            return _error_response('用户不存在企业信息', 404)

        serializer = TenantMemberUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        validated = serializer.validated_data

        if 'real_name' in validated:
            target_profile.real_name = validated['real_name']
        if 'position' in validated:
            target_profile.position = validated['position'] or ''
        if 'role_code' in validated:
            target_profile.role_code = validated['role_code']
        if 'is_active' in validated:
            target_user.is_active = validated['is_active']
            target_user.save(update_fields=['is_active'])

        target_profile.save(
            update_fields=['real_name', 'position', 'role_code', 'updated_at'],
        )

        return _success_response({'message': '更新成功'})


class TenantMemberResetPasswordView(APIView):
    """POST /api/v1/plat-admin/tenant/member/{id}/reset-password - Reset password."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def post(self, request, pk):
        from django.contrib.auth.models import User

        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return _error_response('用户不存在', 404)

        phone = target_user.username
        new_password = phone[-6:]
        target_user.set_password(new_password)
        target_user.save(update_fields=['password'])

        return _success_response({'message': '密码重置成功'})


class TenantMemberUnbindView(APIView):
    """POST /api/v1/plat-admin/tenant/member/{id}/unbind - Unbind member."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def post(self, request, pk):
        from django.contrib.auth.models import User

        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return _error_response('用户不存在', 404)

        try:
            target_profile = target_user.ent_user_profile
        except Exception:
            return _error_response('用户不存在企业信息', 404)

        target_profile.enterprise_id = None
        target_profile.role_code = 'guest'

        if not target_user.is_active:
            target_user.is_active = True
            target_user.save(update_fields=['is_active'])

        target_profile.save(
            update_fields=['enterprise_id', 'role_code', 'updated_at'],
        )

        return _success_response({'message': '解绑成功'})


# ==================== PLAT-005: Opportunity Content ====================


class ContentOpportunityListView(APIView):
    """GET /api/v1/plat-admin/content/opportunity - List all opportunities."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        queryset = Opportunity.objects.select_related('enterprise')

        # Filter by keyword
        keyword = request.query_params.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(detail__icontains=keyword),
            )

        # Filter by type
        opp_type = request.query_params.get('type', '').strip()
        if opp_type:
            queryset = queryset.filter(type=opp_type)

        # Filter by status
        opp_status = request.query_params.get('status', '').strip()
        if opp_status:
            queryset = queryset.filter(status=opp_status)

        queryset = queryset.order_by('-created_at')
        items, total, page, page_size = _paginate(queryset, request)

        serializer = PlatOpportunityListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })


class ContentOpportunityDetailView(APIView):
    """GET /api/v1/plat-admin/content/opportunity/{id} - Opportunity detail."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request, pk):
        try:
            opp = Opportunity.objects.select_related(
                'enterprise', 'publisher',
            ).get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        serializer = PlatOpportunityDetailSerializer(opp)
        return _success_response(serializer.data)


class ContentOpportunityOfflineView(APIView):
    """PUT /api/v1/plat-admin/content/opportunity/{id}/offline - Force offline."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def put(self, request, pk):
        try:
            opp = Opportunity.objects.select_related('publisher').get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        if opp.status != Opportunity.OppStatus.ACTIVE:
            return _error_response('只有在线的商机可以下架', 400)

        serializer = ContentOfflineSerializer(data=request.data)
        reason = ''
        if serializer.is_valid():
            reason = serializer.validated_data.get('reason', '')

        opp.status = Opportunity.OppStatus.OFFLINE
        opp.save(update_fields=['status', 'updated_at'])

        # Notify publisher
        create_notification(
            receiver=opp.publisher,
            type='SYSTEM',
            title='商机被强制下架',
            content=f'您的商机「{opp.title}」已被平台管理员强制下架。'
                    + (f'原因：{reason}' if reason else ''),
            related_type='opportunity',
            related_id=opp.id,
        )

        return _success_response({'message': '下架成功'})


# ==================== PLAT-006: Feed Content ====================


class ContentFeedListView(APIView):
    """GET /api/v1/plat-admin/content/feed - List all feeds."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        queryset = Feed.objects.select_related('publisher', 'enterprise')

        # Filter by keyword
        keyword = request.query_params.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(content__icontains=keyword)

        # Filter by status
        feed_status = request.query_params.get('status', '').strip()
        if feed_status:
            queryset = queryset.filter(status=feed_status)

        queryset = queryset.order_by('-created_at')
        items, total, page, page_size = _paginate(queryset, request)

        serializer = PlatFeedListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })


class ContentFeedDetailView(APIView):
    """GET /api/v1/plat-admin/content/feed/{id} - Feed detail."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request, pk):
        try:
            feed = Feed.objects.select_related(
                'publisher', 'enterprise',
            ).get(pk=pk)
        except Feed.DoesNotExist:
            return _error_response('动态不存在', 404)

        serializer = PlatFeedDetailSerializer(feed)
        return _success_response(serializer.data)


class ContentFeedOfflineView(APIView):
    """PUT /api/v1/plat-admin/content/feed/{id}/offline - Force offline feed."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def put(self, request, pk):
        try:
            feed = Feed.objects.select_related('publisher').get(pk=pk)
        except Feed.DoesNotExist:
            return _error_response('动态不存在', 404)

        if feed.status != Feed.FeedStatus.ACTIVE:
            return _error_response('只有在线的动态可以下架', 400)

        serializer = ContentOfflineSerializer(data=request.data)
        reason = ''
        if serializer.is_valid():
            reason = serializer.validated_data.get('reason', '')

        feed.status = Feed.FeedStatus.OFFLINE
        feed.save(update_fields=['status', 'updated_at'])

        # Notify publisher
        create_notification(
            receiver=feed.publisher,
            type='SYSTEM',
            title='动态被强制下架',
            content='您的动态已被平台管理员强制下架。'
                    + (f'原因：{reason}' if reason else ''),
            related_type='feed',
            related_id=feed.id,
        )

        return _success_response({'message': '下架成功'})


# ==================== PLAT-007: Master Data CRUD ====================


class MasterDataListView(APIView):
    """GET/POST /api/v1/plat-admin/master-data - List or create master data."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        queryset = MasterData.objects.all()

        # Filter by category
        category = request.query_params.get('category', '').strip()
        if category:
            queryset = queryset.filter(category=category)

        queryset = queryset.order_by('sort_order', '-created_at')
        items, total, page, page_size = _paginate(queryset, request)

        serializer = MasterDataListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })

    def post(self, request):
        """POST /api/v1/plat-admin/master-data - Create master data entry."""
        serializer = MasterDataCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        md = MasterData.objects.create(**serializer.validated_data)
        return _success_response({
            'id': md.id,
            'message': '创建成功',
        })


class MasterDataDetailView(APIView):
    """PUT /api/v1/plat-admin/master-data/{id} - Update master data."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def put(self, request, pk):
        try:
            md = MasterData.objects.get(pk=pk)
        except MasterData.DoesNotExist:
            return _error_response('数据不存在', 404)

        serializer = MasterDataUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        validated = serializer.validated_data
        update_fields = ['updated_at']
        for field in ('name', 'code', 'parent_id', 'sort_order'):
            if field in validated:
                setattr(md, field, validated[field])
                update_fields.append(field)

        md.save(update_fields=update_fields)
        return _success_response({'message': '更新成功'})


class MasterDataToggleStatusView(APIView):
    """PUT /api/v1/plat-admin/master-data/{id}/toggle-status - Toggle is_active."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def put(self, request, pk):
        try:
            md = MasterData.objects.get(pk=pk)
        except MasterData.DoesNotExist:
            return _error_response('数据不存在', 404)

        md.is_active = not md.is_active
        md.save(update_fields=['is_active', 'updated_at'])

        return _success_response({
            'id': md.id,
            'is_active': md.is_active,
        })


# ==================== PLAT-008: RBAC ====================


class RoleListView(APIView):
    """GET /api/v1/plat-admin/role - List fixed roles."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        serializer = RoleSerializer(FIXED_ROLES, many=True)
        return _success_response({'items': serializer.data})


class RoleDetailView(APIView):
    """GET /api/v1/plat-admin/role/{id} - Role permission detail."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request, pk):
        role = None
        for r in FIXED_ROLES:
            if r['id'] == pk:
                role = r
                break

        if not role:
            return _error_response('角色不存在', 404)

        data = {
            'id': role['id'],
            'name': role['name'],
            'code': role['code'],
            'description': role['description'],
            'permissions': FIXED_PERMISSIONS.get(role['id'], []),
        }
        serializer = RolePermissionSerializer(data)
        return _success_response(serializer.data)


class RolePermissionUpdateView(APIView):
    """PUT /api/v1/plat-admin/role/{id}/permissions - Update role permissions."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def put(self, request, pk):
        role = None
        for r in FIXED_ROLES:
            if r['id'] == pk:
                role = r
                break

        if not role:
            return _error_response('角色不存在', 404)

        serializer = RolePermissionUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        FIXED_PERMISSIONS[role['id']] = serializer.validated_data['permissions']
        return _success_response({'message': '权限更新成功'})


# ==================== PLAT-009: Settings ====================

SETTINGS_CACHE_KEY = 'plat_admin_settings'


class SettingsGetView(APIView):
    """GET /api/v1/plat-admin/settings - Get system settings."""

    permission_classes = [IsAuthenticated, PlatformAdminPermission]

    def get(self, request):
        key = request.query_params.get('key', '').strip()
        all_settings = cache.get(SETTINGS_CACHE_KEY, {})

        if key:
            value = all_settings.get(key, '')
            return _success_response({'key': key, 'value': value})

        return _success_response({'items': all_settings})

    def put(self, request):
        """PUT /api/v1/plat-admin/settings - Update system settings."""
        serializer = SettingsSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        key = serializer.validated_data['key']
        value = serializer.validated_data['value']

        all_settings = cache.get(SETTINGS_CACHE_KEY, {})
        all_settings[key] = value
        cache.set(SETTINGS_CACHE_KEY, all_settings, timeout=None)

        return _success_response({'key': key, 'value': value})
