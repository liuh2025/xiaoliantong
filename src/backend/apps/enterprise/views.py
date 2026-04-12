import logging

from django.db import connection, transaction
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from apps.enterprise.models import Enterprise, AuditRecord, MasterData
from apps.opportunity.models import Opportunity, ContactLog
from apps.auth_app.models import User
from apps.enterprise.serializers import (
    EnterpriseListSerializer,
    EnterpriseDetailSerializer,
    EnterpriseClaimSerializer,
    EnterpriseCreateSerializer,
    EnterpriseUpdateSerializer,
    MasterDataSerializer,
    NewestEnterpriseSerializer,
)

logger = logging.getLogger(__name__)


class EnterpriseListPagination(PageNumberPagination):
    """Pagination configuration for enterprise list."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        """Override to return None instead of raising Http404 for empty pages."""
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        try:
            self.page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            return None
        self.request = request
        return list(self.page)


class EnterpriseListView(APIView):
    """GET /ent/enterprise - Public enterprise list with filtering and desensitization."""

    permission_classes = []
    authentication_classes = []
    pagination_class = EnterpriseListPagination

    def get(self, request):
        """Handle GET request for enterprise list."""
        queryset = Enterprise.objects.all()

        # Default filter: only show VERIFIED enterprises
        auth_status = request.query_params.get('auth_status')
        if auth_status:
            queryset = queryset.filter(auth_status=auth_status)
        else:
            queryset = queryset.filter(
                auth_status=Enterprise.AuthStatus.VERIFIED,
            )

        # Apply filters
        queryset = self._apply_filters(queryset, request.query_params)

        # Apply keyword search
        keyword = request.query_params.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | Q(description__icontains=keyword),
            )

        # Default ordering: newest first
        queryset = queryset.order_by('-created_at')

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        total_count = queryset.count()
        page_number = paginator.page.number if page is not None else int(
            request.query_params.get('page', 1)
        )
        page_size = paginator.page.paginator.per_page if page is not None else paginator.get_page_size(request)

        if page is None:
            # Page out of range: return empty results with total count
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'total': total_count,
                    'page': page_number,
                    'page_size': page_size,
                    'items': [],
                },
            }, status=status.HTTP_200_OK)

        serializer = EnterpriseListSerializer(page, many=True)

        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'total': paginator.page.paginator.count,
                'page': paginator.page.number,
                'page_size': paginator.page.paginator.per_page,
                'items': serializer.data,
            },
        }, status=status.HTTP_200_OK)

    def _apply_filters(self, queryset, params):
        """Apply filtering based on query parameters."""
        filter_mapping = {
            'industry_id': 'industry_id',
            'sub_industry_id': 'sub_industry_id',
            'category_id': 'category_id',
            'province_id': 'province_id',
            'region_id': 'region_id',
        }
        for param_name, field_name in filter_mapping.items():
            value = params.get(param_name)
            if value is not None:
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    continue
                queryset = queryset.filter(**{field_name: value})

        # Tags filter: comma-separated string, match enterprises whose
        # tags JSON array contains any of the specified tag values.
        tags_param = params.get('tags')
        if tags_param:
            tag_list = [t.strip() for t in tags_param.split(',') if t.strip()]
            if tag_list:
                queryset = self._filter_by_tags(queryset, tag_list)

        return queryset

    @staticmethod
    def _filter_by_tags(queryset, tag_list):
        """Filter queryset by tags, compatible with both MySQL and SQLite.

        MySQL supports JSONField ``contains`` lookup natively.
        SQLite does not, so we fall back to Python-level filtering.
        """
        if connection.vendor == 'sqlite':
            # SQLite: JSON contains not supported, use Python filtering
            matching_ids = []
            for ent in queryset.only('id', 'tags'):
                if ent.tags and isinstance(ent.tags, list):
                    if any(tag in ent.tags for tag in tag_list):
                        matching_ids.append(ent.id)
            return queryset.filter(id__in=matching_ids)
        else:
            # MySQL/PostgreSQL: use native JSON contains lookup
            q = Q()
            for tag in tag_list:
                q |= Q(tags__contains=[tag])
            return queryset.filter(q)


class EnterpriseDetailView(APIView):
    """GET /ent/enterprise/{id} - Public enterprise detail with desensitization.

    PUT /ent/enterprise/{id} - Update enterprise info (admin only).

    GET is public (no authentication required).
    PUT requires authentication (IsAuthenticated).
    """

    def get_permissions(self):
        """Return permission classes based on HTTP method."""
        if self.request.method == 'PUT':
            return [IsAuthenticated()]
        return []

    def get_authenticators(self):
        """Return authenticators based on HTTP method.

        GET requests are public and do not require authentication.
        """
        if self.request.method == 'PUT':
            return super().get_authenticators()
        return []

    def get(self, request, pk):
        """Handle GET request for enterprise detail."""
        try:
            enterprise = Enterprise.objects.select_related('admin_user').get(pk=pk)
        except Enterprise.DoesNotExist:
            return Response({
                'code': 404,
                'message': 'Enterprise not found',
                'data': None,
            }, status=status.HTTP_200_OK)

        serializer = EnterpriseDetailSerializer(enterprise)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """Update an enterprise's updatable fields."""
        try:
            enterprise = Enterprise.objects.get(pk=pk)
        except Enterprise.DoesNotExist:
            return Response({
                'code': 404,
                'message': '企业不存在',
                'data': None,
            }, status=status.HTTP_200_OK)

        # Permission check: only admin_user can update
        if enterprise.admin_user != request.user:
            return Response({
                'code': 403,
                'message': '无权操作',
                'data': None,
            }, status=status.HTTP_200_OK)

        serializer = EnterpriseUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '请求参数错误',
                'data': serializer.errors,
            }, status=status.HTTP_200_OK)

        # Only update allowed fields (locked fields are ignored)
        updatable_fields = [
            'category_id', 'province_id', 'region_id',
            'description', 'logo_url', 'tags',
        ]
        validated_data = serializer.validated_data
        update_fields = ['updated_at']
        for field in updatable_fields:
            if field in validated_data:
                setattr(enterprise, field, validated_data[field])
                update_fields.append(field)

        enterprise.save(update_fields=update_fields)

        detail_serializer = EnterpriseDetailSerializer(enterprise)
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': detail_serializer.data,
        }, status=status.HTTP_200_OK)


# ==================== ENT-004: Claim Enterprise ====================


class EnterpriseClaimView(APIView):
    """POST /ent/enterprise/claim - Claim an unclaimed enterprise."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Claim an enterprise by credit_code or enterprise_id.

        Supports Step2 fields: legal_representative, business_license, position.
        """
        serializer = EnterpriseClaimSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '请求参数错误',
                'data': serializer.errors,
            }, status=status.HTTP_200_OK)

        # Find enterprise by credit_code or enterprise_id
        enterprise = None
        credit_code = serializer.validated_data.get('credit_code', '')
        enterprise_id = serializer.validated_data.get('enterprise_id')

        if enterprise_id:
            try:
                enterprise = Enterprise.objects.get(pk=enterprise_id)
            except Enterprise.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '企业不存在',
                    'data': None,
                }, status=status.HTTP_200_OK)
        elif credit_code:
            try:
                enterprise = Enterprise.objects.get(credit_code=credit_code)
            except Enterprise.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': '企业不存在',
                    'data': None,
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'code': 400,
                'message': '请提供credit_code或enterprise_id',
                'data': None,
            }, status=status.HTTP_200_OK)

        # BR-ENT-02: Claim mutual exclusion
        if enterprise.auth_status != Enterprise.AuthStatus.UNCLAIMED:
            return Response({
                'code': 409,
                'message': '该企业已被认领',
                'data': None,
            }, status=status.HTTP_200_OK)

        try:
            with transaction.atomic():
                # Update enterprise
                enterprise.admin_user = request.user
                enterprise.auth_status = Enterprise.AuthStatus.PENDING

                # Update Step2 fields if provided
                legal_rep = serializer.validated_data.get('legal_representative')
                if legal_rep:
                    enterprise.legal_representative = legal_rep
                position = serializer.validated_data.get('position')
                if position:
                    enterprise.position = position

                update_fields = ['admin_user', 'auth_status', 'updated_at']
                if legal_rep:
                    update_fields.append('legal_representative')
                if position:
                    update_fields.append('position')

                enterprise.save(update_fields=update_fields)

                # Create audit record
                AuditRecord.objects.create(
                    enterprise=enterprise,
                    status=AuditRecord.AuditStatus.PENDING,
                )

                # Update UserProfile
                profile = request.user.ent_user_profile
                profile.enterprise_id = enterprise.id
                profile.role_code = 'enterprise_admin'
                profile.save(
                    update_fields=['enterprise_id', 'role_code', 'updated_at'],
                )
        except Exception as e:
            logger.error(
                f"Failed to claim enterprise for user "
                f"{request.user.id}: {e}",
            )
            return Response({
                'code': 500,
                'message': '认领失败，请稍后重试',
                'data': None,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'code': 200,
            'message': '认领成功',
            'data': {
                'enterprise_id': enterprise.id,
                'auth_status': enterprise.auth_status,
            },
        }, status=status.HTTP_200_OK)


# ==================== ENT-005: Create Enterprise ====================


class EnterpriseCreateView(APIView):
    """POST /ent/enterprise/create - Create a new enterprise."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new enterprise."""
        serializer = EnterpriseCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '请求参数错误',
                'data': serializer.errors,
            }, status=status.HTTP_200_OK)

        try:
            with transaction.atomic():
                enterprise = Enterprise(
                    **serializer.validated_data,
                    admin_user=request.user,
                    auth_status=Enterprise.AuthStatus.PENDING,
                )
                enterprise.save()

                # Create audit record
                AuditRecord.objects.create(
                    enterprise=enterprise,
                    status=AuditRecord.AuditStatus.PENDING,
                )

                # Update UserProfile
                profile = request.user.ent_user_profile
                profile.enterprise_id = enterprise.id
                profile.role_code = 'enterprise_admin'
                profile.save(
                    update_fields=['enterprise_id', 'role_code', 'updated_at'],
                )
        except Exception as e:
            logger.error(
                f"Failed to create enterprise for user "
                f"{request.user.id}: {e}",
            )
            return Response({
                'code': 500,
                'message': '创建失败，请稍后重试',
                'data': None,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return full enterprise info
        detail_serializer = EnterpriseDetailSerializer(enterprise)
        return Response({
            'code': 200,
            'message': '创建成功',
            'data': detail_serializer.data,
        }, status=status.HTTP_200_OK)


# ==================== ENT-006: My Enterprise ====================


class MyEnterpriseView(APIView):
    """GET /ent/enterprise/my - Get current user's enterprise."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return current user's enterprise info."""
        try:
            profile = request.user.ent_user_profile
        except Exception:
            return Response({
                'code': 404,
                'message': '未绑定企业',
                'data': None,
            }, status=status.HTTP_200_OK)

        if not profile.enterprise_id:
            return Response({
                'code': 404,
                'message': '未绑定企业',
                'data': None,
            }, status=status.HTTP_200_OK)

        try:
            enterprise = Enterprise.objects.select_related(
                'admin_user',
            ).get(pk=profile.enterprise_id)
        except Enterprise.DoesNotExist:
            return Response({
                'code': 404,
                'message': '未绑定企业',
                'data': None,
            }, status=status.HTTP_200_OK)

        serializer = EnterpriseDetailSerializer(enterprise)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)


# ==================== ENT-008: Dictionary APIs ====================


class IndustryListView(APIView):
    """GET /ent/industry - List industries (public)."""

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        """List industries, optionally filtered by parent_id."""
        queryset = MasterData.objects.filter(
            category='industry', is_active=True,
        )

        parent_id = request.query_params.get('parent_id')
        if parent_id is not None:
            try:
                parent_id = int(parent_id)
            except (ValueError, TypeError):
                parent_id = None
            if parent_id == 0:
                # parent_id=0 means top-level (parent_id IS NULL)
                queryset = queryset.filter(parent_id__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)

        queryset = queryset.order_by('sort_order', 'id')
        serializer = MasterDataSerializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)


class CategoryListView(APIView):
    """GET /ent/category - List categories (public)."""

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        """List categories, optionally filtered by industry_id."""
        queryset = MasterData.objects.filter(
            category='category', is_active=True,
        )

        industry_id = request.query_params.get('industry_id')
        if industry_id is not None:
            try:
                industry_id = int(industry_id)
                queryset = queryset.filter(industry_id=industry_id)
            except (ValueError, TypeError):
                pass

        queryset = queryset.order_by('sort_order', 'id')
        serializer = MasterDataSerializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)


class RegionListView(APIView):
    """GET /ent/region - List regions (public)."""

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        """List regions, optionally filtered by parent_id."""
        queryset = MasterData.objects.filter(
            category='region', is_active=True,
        )

        parent_id = request.query_params.get('parent_id')
        if parent_id is not None:
            try:
                parent_id = int(parent_id)
            except (ValueError, TypeError):
                parent_id = None
            if parent_id == 0:
                queryset = queryset.filter(parent_id__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)

        queryset = queryset.order_by('sort_order', 'id')
        serializer = MasterDataSerializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)


# ==================== ENT-009: Newest Enterprises ====================


class NewestEnterpriseView(APIView):
    """GET /ent/enterprise/newest - Get newest VERIFIED enterprises (public)."""

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        """Return top 3 newest VERIFIED enterprises."""
        enterprises = Enterprise.objects.filter(
            auth_status=Enterprise.AuthStatus.VERIFIED,
        ).order_by('-created_at')[:3]

        serializer = NewestEnterpriseSerializer(enterprises, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'items': serializer.data,
            },
        }, status=status.HTTP_200_OK)


class HomeStatsView(APIView):
    """GET /ent/stats - Public homepage statistics."""

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        """Return homepage statistics."""
        from django.db.models import Count

        total_enterprises = Enterprise.objects.filter(
            auth_status=Enterprise.AuthStatus.VERIFIED,
        ).count()

        total_opportunities = Opportunity.objects.filter(
            status=Opportunity.OppStatus.ACTIVE,
        ).count()

        total_matchmaking = ContactLog.objects.filter(
            status=ContactLog.ContactStatus.COMPLETED,
        ).count()

        total_users = User.objects.filter(is_active=True).count()

        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'total_enterprises': total_enterprises,
                'total_opportunities': total_opportunities,
                'total_matchmaking': total_matchmaking,
                'total_users': total_users,
            },
        }, status=status.HTTP_200_OK)
