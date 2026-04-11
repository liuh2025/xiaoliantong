import logging

from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile
from apps.opportunity.models import Opportunity
from apps.ent_admin.serializers import (
    EmployeeListSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    EntAdminOpportunityListSerializer,
    EntAdminOpportunityUpdateSerializer,
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


def _get_admin_enterprise(user):
    """Return the VERIFIED Enterprise for the enterprise_admin user, or None."""
    try:
        profile = user.ent_user_profile
    except Exception:
        return None
    if profile.role_code != 'enterprise_admin':
        return None
    if not profile.enterprise_id:
        return None
    try:
        return Enterprise.objects.get(
            id=profile.enterprise_id,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
    except Enterprise.DoesNotExist:
        return None


def _get_user_enterprise(user):
    """Return the VERIFIED Enterprise bound to user (admin or employee), or None."""
    try:
        profile = user.ent_user_profile
    except Exception:
        return None
    if not profile.enterprise_id:
        return None
    try:
        return Enterprise.objects.get(
            id=profile.enterprise_id,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
    except Enterprise.DoesNotExist:
        return None


# ==================== ADM-001/002: Employee List / Create ====================


class EmployeeListView(APIView):
    """GET/POST /api/v1/ent-admin/employees - List or create employees."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ADM-001: List employees of the current admin's enterprise."""
        enterprise = _get_admin_enterprise(request.user)
        if not enterprise:
            return _error_response('无权操作，需要企业管理员权限', 403)

        profiles = UserProfile.objects.filter(
            enterprise_id=enterprise.id,
        ).select_related('user')

        # Keyword search on real_name or phone (user.username)
        keyword = request.query_params.get('keyword', '').strip()
        if keyword:
            profiles = profiles.filter(
                Q(real_name__icontains=keyword)
                | Q(user__username__icontains=keyword),
            )

        serializer = EmployeeListSerializer(profiles, many=True)
        return _success_response({'items': serializer.data})

    def post(self, request):
        """ADM-002: Create/bind an employee to the current enterprise."""
        enterprise = _get_admin_enterprise(request.user)
        if not enterprise:
            return _error_response('无权操作，需要企业管理员权限', 403)

        serializer = EmployeeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        phone = serializer.validated_data['phone']
        real_name = serializer.validated_data['real_name']
        position = serializer.validated_data.get('position')
        role_code = serializer.validated_data['role_code']

        # Find user by phone (username)
        from django.contrib.auth.models import User
        try:
            target_user = User.objects.get(username=phone)
        except User.DoesNotExist:
            return _error_response('用户未注册', 400)

        # Check if user already bound to another enterprise
        try:
            target_profile = target_user.ent_user_profile
            if target_profile.enterprise_id and target_profile.enterprise_id != enterprise.id:
                return _error_response('用户已绑定其他企业', 400)
        except Exception:
            # No profile yet - create one
            target_profile = UserProfile.objects.create(
                user=target_user,
                role_code='guest',
            )

        # Bind user to current enterprise
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


# ==================== ADM-003: Employee Update ====================


class EmployeeDetailView(APIView):
    """PUT /api/v1/ent-admin/employees/{id} - Update employee."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """ADM-003: Update employee info."""
        enterprise = _get_admin_enterprise(request.user)
        if not enterprise:
            return _error_response('无权操作，需要企业管理员权限', 403)

        # Get target user
        from django.contrib.auth.models import User
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return _error_response('用户不存在', 404)

        # Check target belongs to same enterprise
        try:
            target_profile = target_user.ent_user_profile
        except Exception:
            return _error_response('用户不存在企业信息', 404)

        if target_profile.enterprise_id != enterprise.id:
            return _error_response('该用户不属于当前企业', 403)

        serializer = EmployeeUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        validated = serializer.validated_data

        # Cannot downgrade own role
        if 'role_code' in validated and target_user == request.user:
            if validated['role_code'] != 'enterprise_admin':
                return _error_response('不能修改自己的角色', 400)

        # Cannot downgrade the last admin
        if 'role_code' in validated and validated['role_code'] != 'enterprise_admin':
            if target_profile.role_code == 'enterprise_admin':
                admin_count = UserProfile.objects.filter(
                    enterprise_id=enterprise.id,
                    role_code='enterprise_admin',
                ).count()
                if admin_count <= 1:
                    return _error_response('至少保留一个企业管理员', 400)

        # Apply updates
        if 'real_name' in validated:
            target_profile.real_name = validated['real_name']
        if 'position' in validated:
            target_profile.position = validated['position'] or ''
        if 'role_code' in validated:
            target_profile.role_code = validated['role_code']
        if 'is_active' in validated:
            target_user.is_active = validated['is_active']
            target_user.save(update_fields=['is_active'])

        target_profile.save(update_fields=['real_name', 'position', 'role_code', 'updated_at'])

        return _success_response({'message': '更新成功'})


# ==================== ADM-004: Reset Password ====================


class EmployeeResetPasswordView(APIView):
    """POST /api/v1/ent-admin/employees/{id}/reset-password - Reset employee password."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """ADM-004: Reset employee password to last 6 digits of phone."""
        enterprise = _get_admin_enterprise(request.user)
        if not enterprise:
            return _error_response('无权操作，需要企业管理员权限', 403)

        from django.contrib.auth.models import User
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return _error_response('用户不存在', 404)

        # Check target belongs to same enterprise
        try:
            target_profile = target_user.ent_user_profile
        except Exception:
            return _error_response('用户不存在企业信息', 404)

        if target_profile.enterprise_id != enterprise.id:
            return _error_response('该用户不属于当前企业', 403)

        # New password = last 6 digits of phone (username)
        phone = target_user.username
        new_password = phone[-6:]
        target_user.set_password(new_password)
        target_user.save(update_fields=['password'])

        return _success_response({'message': '密码重置成功'})


# ==================== ADM-005: Disable/Enable Employee ====================


class EmployeeDisableView(APIView):
    """PUT /api/v1/ent-admin/employees/{id}/disable - Toggle employee active status."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """ADM-005: Toggle employee is_active status."""
        enterprise = _get_admin_enterprise(request.user)
        if not enterprise:
            return _error_response('无权操作，需要企业管理员权限', 403)

        from django.contrib.auth.models import User
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return _error_response('用户不存在', 404)

        # Check target belongs to same enterprise
        try:
            target_profile = target_user.ent_user_profile
        except Exception:
            return _error_response('用户不存在企业信息', 404)

        if target_profile.enterprise_id != enterprise.id:
            return _error_response('该用户不属于当前企业', 403)

        # Toggle is_active
        target_user.is_active = not target_user.is_active
        target_user.save(update_fields=['is_active'])

        return _success_response({
            'id': target_user.id,
            'is_active': target_user.is_active,
        })


# ==================== ADM-006: Unbind Employee ====================


class EmployeeUnbindView(APIView):
    """POST /api/v1/ent-admin/employees/{id}/unbind - Unbind employee from enterprise."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """ADM-006: Unbind employee from enterprise."""
        enterprise = _get_admin_enterprise(request.user)
        if not enterprise:
            return _error_response('无权操作，需要企业管理员权限', 403)

        from django.contrib.auth.models import User
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return _error_response('用户不存在', 404)

        # Check target belongs to same enterprise
        try:
            target_profile = target_user.ent_user_profile
        except Exception:
            return _error_response('用户不存在企业信息', 404)

        if target_profile.enterprise_id != enterprise.id:
            return _error_response('该用户不属于当前企业', 403)

        # Unbind: clear enterprise association
        target_profile.enterprise_id = None
        target_profile.role_code = 'guest'

        # If disabled, re-enable
        if not target_user.is_active:
            target_user.is_active = True
            target_user.save(update_fields=['is_active'])

        target_profile.save(update_fields=['enterprise_id', 'role_code', 'updated_at'])

        return _success_response({'message': '解绑成功'})


# ==================== ADM-007: My Opportunity List ====================


class OpportunityListView(APIView):
    """GET /api/v1/ent-admin/my-opportunities - List current enterprise's opportunities."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ADM-007: List opportunities for the current user's enterprise."""
        enterprise = _get_user_enterprise(request.user)
        if not enterprise:
            return _error_response('用户未绑定已认证企业', 403)

        queryset = Opportunity.objects.filter(
            enterprise_id=enterprise.id,
        ).select_related('enterprise', 'publisher')

        # Filter by type
        opp_type = request.query_params.get('type')
        if opp_type:
            queryset = queryset.filter(type=opp_type)

        # Filter by status
        opp_status = request.query_params.get('status')
        if opp_status:
            queryset = queryset.filter(status=opp_status)

        # Keyword search on title
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

        serializer = EntAdminOpportunityListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })


# ==================== ADM-008: Update Opportunity ====================


class OpportunityDetailView(APIView):
    """PUT /api/v1/ent-admin/my-opportunities/{id} - Update opportunity."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """ADM-008: Update opportunity (enterprise admin or publisher)."""
        enterprise = _get_user_enterprise(request.user)
        if not enterprise:
            return _error_response('用户未绑定已认证企业', 403)

        try:
            opp = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        # Check the opportunity belongs to the enterprise
        if opp.enterprise_id != enterprise.id:
            return _error_response('无权操作', 403)

        # Permission: enterprise admin or publisher
        profile = getattr(request.user, 'ent_user_profile', None)
        is_admin = profile and profile.role_code == 'enterprise_admin'
        is_publisher = opp.publisher == request.user
        if not is_admin and not is_publisher:
            return _error_response('无权操作', 403)

        serializer = EntAdminOpportunityUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response('请求参数错误', 400)

        validated = serializer.validated_data
        updatable_fields = [
            'title', 'industry_id', 'sub_industry_id', 'category_id',
            'province_id', 'region_id', 'detail', 'tags',
            'contact_name', 'contact_phone', 'contact_wechat',
        ]
        update_fields = ['updated_at']
        for field in updatable_fields:
            if field in validated:
                setattr(opp, field, validated[field])
                update_fields.append(field)

        opp.save(update_fields=update_fields)
        return _success_response({'message': '更新成功'})


# ==================== ADM-009: Republish Opportunity ====================


class OpportunityRepublishView(APIView):
    """PUT /api/v1/ent-admin/my-opportunities/{id}/republish - Republish opportunity."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """ADM-009: Republish OFFLINE opportunity to ACTIVE."""
        enterprise = _get_user_enterprise(request.user)
        if not enterprise:
            return _error_response('用户未绑定已认证企业', 403)

        try:
            opp = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        if opp.enterprise_id != enterprise.id:
            return _error_response('无权操作', 403)

        # Permission: enterprise admin or publisher
        profile = getattr(request.user, 'ent_user_profile', None)
        is_admin = profile and profile.role_code == 'enterprise_admin'
        is_publisher = opp.publisher == request.user
        if not is_admin and not is_publisher:
            return _error_response('无权操作', 403)

        if opp.status != Opportunity.OppStatus.OFFLINE:
            return _error_response('只有已下架的商机可以重新发布', 400)

        opp.status = Opportunity.OppStatus.ACTIVE
        opp.save(update_fields=['status', 'updated_at'])
        return _success_response({'message': '重新发布成功'})


# ==================== ADM-010: Offline Opportunity ====================


class OpportunityOfflineView(APIView):
    """PUT /api/v1/ent-admin/my-opportunities/{id}/offline - Offline opportunity."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """ADM-010: Offline ACTIVE opportunity."""
        enterprise = _get_user_enterprise(request.user)
        if not enterprise:
            return _error_response('用户未绑定已认证企业', 403)

        try:
            opp = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return _error_response('商机不存在', 404)

        if opp.enterprise_id != enterprise.id:
            return _error_response('无权操作', 403)

        # Permission: enterprise admin only for offline
        profile = getattr(request.user, 'ent_user_profile', None)
        is_admin = profile and profile.role_code == 'enterprise_admin'
        if not is_admin:
            return _error_response('无权操作，需要企业管理员权限', 403)

        if opp.status != Opportunity.OppStatus.ACTIVE:
            return _error_response('只有在线的商机可以下架', 400)

        opp.status = Opportunity.OppStatus.OFFLINE
        opp.save(update_fields=['status', 'updated_at'])
        return _success_response({'message': '下架成功'})
