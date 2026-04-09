from rest_framework import serializers
from apps.enterprise.models import Enterprise, AuditRecord, MasterData
from apps.opportunity.models import Opportunity
from apps.feed.models import Feed
from apps.auth_app.models import UserProfile


def _get_master_data_name(data_id, category):
    """Look up a MasterData name by id and category."""
    if not data_id:
        return ''
    md = MasterData.objects.filter(
        id=data_id, category=category, is_active=True,
    ).first()
    return md.name if md else ''


def _get_user_display_name(user):
    """Get display name for a user from profile.real_name or username."""
    if not user:
        return ''
    profile = getattr(user, 'ent_user_profile', None)
    if profile and profile.real_name:
        return profile.real_name
    return user.username


# ==================== PLAT-001: Profile ====================


class PlatformProfileSerializer(serializers.Serializer):
    """Serializer for platform admin profile."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    role_code = serializers.CharField()
    role_name = serializers.CharField()


# ==================== PLAT-002: Dashboard ====================


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard stats."""

    enterprise_count = serializers.IntegerField()
    opportunity_count = serializers.IntegerField()
    deal_count = serializers.IntegerField()
    active_user_count = serializers.IntegerField()
    pending_audit_count = serializers.IntegerField()
    enterprise_trend = serializers.FloatField()
    opportunity_trend = serializers.FloatField()
    deal_trend = serializers.FloatField()


class DashboardTrendItemSerializer(serializers.Serializer):
    """Serializer for a single trend data point."""

    date = serializers.DateField()
    count = serializers.IntegerField()


# ==================== PLAT-003: Audit ====================


class AuditEnterpriseListSerializer(serializers.ModelSerializer):
    """Serializer for enterprise audit list."""

    enterprise_id = serializers.IntegerField(source='enterprise.id')
    enterprise_name = serializers.CharField(source='enterprise.name')
    credit_code = serializers.CharField(source='enterprise.credit_code')
    industry_name = serializers.SerializerMethodField()
    sub_industry_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()
    applicant_name = serializers.SerializerMethodField()
    applicant_position = serializers.SerializerMethodField()
    contact_phone = serializers.SerializerMethodField()
    legal_representative = serializers.CharField(
        source='enterprise.legal_representative',
    )
    business_license_url = serializers.CharField(
        source='enterprise.business_license',
    )

    class Meta:
        model = AuditRecord
        fields = [
            'id', 'enterprise_id', 'enterprise_name', 'credit_code',
            'industry_name', 'sub_industry_name',
            'province_name', 'region_name',
            'applicant_name', 'applicant_position', 'contact_phone',
            'legal_representative', 'business_license_url',
            'status', 'created_at',
        ]

    def get_industry_name(self, obj):
        return _get_master_data_name(obj.enterprise.industry_id, 'industry')

    def get_sub_industry_name(self, obj):
        return _get_master_data_name(obj.enterprise.sub_industry_id, 'industry')

    def get_province_name(self, obj):
        return _get_master_data_name(obj.enterprise.province_id, 'region')

    def get_region_name(self, obj):
        return _get_master_data_name(obj.enterprise.region_id, 'region')

    def get_applicant_name(self, obj):
        admin_user = obj.enterprise.admin_user
        if admin_user:
            return _get_user_display_name(admin_user)
        return ''

    def get_applicant_position(self, obj):
        admin_user = obj.enterprise.admin_user
        if admin_user:
            profile = getattr(admin_user, 'ent_user_profile', None)
            if profile:
                return profile.position or ''
        return ''

    def get_contact_phone(self, obj):
        admin_user = obj.enterprise.admin_user
        if admin_user:
            profile = getattr(admin_user, 'ent_user_profile', None)
            if profile and profile.contact_phone:
                return profile.contact_phone
            return admin_user.username
        return ''


class AuditRejectSerializer(serializers.Serializer):
    """Serializer for audit reject request."""

    reason = serializers.CharField(max_length=500)


# ==================== PLAT-004: Tenant ====================


class TenantEnterpriseListSerializer(serializers.ModelSerializer):
    """Serializer for tenant enterprise list."""

    industry_name = serializers.SerializerMethodField()
    admin_name = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Enterprise
        fields = [
            'id', 'name', 'logo_url', 'industry_name',
            'auth_status', 'admin_name', 'member_count',
            'created_at', 'is_active',
        ]

    def get_industry_name(self, obj):
        return _get_master_data_name(obj.industry_id, 'industry')

    def get_admin_name(self, obj):
        if obj.admin_user:
            return _get_user_display_name(obj.admin_user)
        return ''

    def get_member_count(self, obj):
        return UserProfile.objects.filter(enterprise_id=obj.id).count()


class TenantEnterpriseDetailSerializer(TenantEnterpriseListSerializer):
    """Serializer for tenant enterprise detail, includes member list."""

    members = serializers.SerializerMethodField()

    class Meta(TenantEnterpriseListSerializer.Meta):
        fields = TenantEnterpriseListSerializer.Meta.fields + ['members']

    def get_members(self, obj):
        profiles = UserProfile.objects.filter(
            enterprise_id=obj.id,
        ).select_related('user')
        return TenantMemberListSerializer(profiles, many=True).data


class TenantMemberListSerializer(serializers.Serializer):
    """Serializer for tenant member list."""

    id = serializers.IntegerField(source='user.id')
    real_name = serializers.CharField()
    position = serializers.CharField(allow_null=True)
    phone = serializers.CharField(source='user.username')
    role_code = serializers.CharField()
    is_active = serializers.BooleanField(source='user.is_active')
    created_at = serializers.DateTimeField()


class TenantMemberCreateSerializer(serializers.Serializer):
    """Serializer for creating a tenant member."""

    phone = serializers.CharField(max_length=11)
    real_name = serializers.CharField(max_length=50)
    position = serializers.CharField(
        max_length=50, required=False, allow_null=True, allow_blank=True,
    )
    role_code = serializers.ChoiceField(
        choices=['enterprise_admin', 'employee'],
    )


class TenantMemberUpdateSerializer(serializers.Serializer):
    """Serializer for updating a tenant member."""

    real_name = serializers.CharField(
        max_length=50, required=False, allow_blank=True,
    )
    position = serializers.CharField(
        max_length=50, required=False, allow_null=True, allow_blank=True,
    )
    role_code = serializers.ChoiceField(
        choices=['enterprise_admin', 'employee'], required=False,
    )
    is_active = serializers.BooleanField(required=False)


# ==================== PLAT-005: Opportunity Content ====================


class PlatOpportunityListSerializer(serializers.ModelSerializer):
    """Serializer for platform admin opportunity list."""

    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )
    industry_name = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id', 'type', 'title', 'enterprise_name',
            'industry_name', 'status', 'view_count', 'created_at',
        ]

    def get_industry_name(self, obj):
        return _get_master_data_name(obj.industry_id, 'industry')


class PlatOpportunityDetailSerializer(serializers.ModelSerializer):
    """Serializer for platform admin opportunity detail."""

    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )
    publisher_name = serializers.SerializerMethodField()
    industry_name = serializers.SerializerMethodField()
    sub_industry_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id', 'type', 'title',
            'enterprise_id', 'enterprise_name',
            'publisher_id', 'publisher_name',
            'industry_id', 'industry_name',
            'sub_industry_id', 'sub_industry_name',
            'category_id', 'category_name',
            'province_id', 'province_name',
            'region_id', 'region_name',
            'tags', 'detail', 'status',
            'view_count', 'contact_name',
            'contact_phone', 'contact_wechat',
            'created_at', 'updated_at',
        ]

    def get_publisher_name(self, obj):
        return _get_user_display_name(obj.publisher)

    def get_industry_name(self, obj):
        return _get_master_data_name(obj.industry_id, 'industry')

    def get_sub_industry_name(self, obj):
        return _get_master_data_name(obj.sub_industry_id, 'industry')

    def get_category_name(self, obj):
        return _get_master_data_name(obj.category_id, 'category')

    def get_province_name(self, obj):
        return _get_master_data_name(obj.province_id, 'region')

    def get_region_name(self, obj):
        return _get_master_data_name(obj.region_id, 'region')


class ContentOfflineSerializer(serializers.Serializer):
    """Serializer for offline reason."""

    reason = serializers.CharField(max_length=500)


# ==================== PLAT-006: Feed Content ====================


class PlatFeedListSerializer(serializers.ModelSerializer):
    """Serializer for platform admin feed list."""

    publisher_name = serializers.SerializerMethodField()
    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )

    class Meta:
        model = Feed
        fields = [
            'id', 'content', 'publisher_name', 'enterprise_name',
            'status', 'created_at',
        ]

    def get_publisher_name(self, obj):
        return _get_user_display_name(obj.publisher)


class PlatFeedDetailSerializer(serializers.ModelSerializer):
    """Serializer for platform admin feed detail."""

    publisher_name = serializers.SerializerMethodField()
    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )

    class Meta:
        model = Feed
        fields = [
            'id', 'content', 'images',
            'publisher_id', 'publisher_name',
            'enterprise_id', 'enterprise_name',
            'status', 'created_at', 'updated_at',
        ]

    def get_publisher_name(self, obj):
        return _get_user_display_name(obj.publisher)


# ==================== PLAT-007: Master Data ====================


class MasterDataListSerializer(serializers.ModelSerializer):
    """Serializer for master data list."""

    class Meta:
        model = MasterData
        fields = [
            'id', 'category', 'name', 'code',
            'parent_id', 'sort_order', 'is_active',
            'created_at', 'updated_at',
        ]


class MasterDataCreateSerializer(serializers.Serializer):
    """Serializer for creating master data."""

    category = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=50)
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    sort_order = serializers.IntegerField(default=0)


class MasterDataUpdateSerializer(serializers.Serializer):
    """Serializer for updating master data."""

    name = serializers.CharField(max_length=200, required=False)
    code = serializers.CharField(max_length=50, required=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    sort_order = serializers.IntegerField(required=False)


# ==================== PLAT-008: RBAC ====================


class RoleSerializer(serializers.Serializer):
    """Serializer for fixed role list."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    description = serializers.CharField()


class RolePermissionSerializer(serializers.Serializer):
    """Serializer for role permissions detail."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    description = serializers.CharField()
    permissions = serializers.ListField()


class RolePermissionUpdateSerializer(serializers.Serializer):
    """Serializer for updating role permissions."""

    permissions = serializers.ListField()


# ==================== PLAT-009: Settings ====================


class SettingsSerializer(serializers.Serializer):
    """Serializer for system settings."""

    key = serializers.CharField(max_length=100)
    value = serializers.CharField(allow_blank=True)
