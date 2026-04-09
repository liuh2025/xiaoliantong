from rest_framework import serializers
from apps.enterprise.models import MasterData
from apps.opportunity.models import Opportunity


def _get_master_data_name(data_id, category):
    """Look up a MasterData name by id and category."""
    if not data_id:
        return ''
    md = MasterData.objects.filter(
        id=data_id, category=category, is_active=True,
    ).first()
    return md.name if md else ''


class EmployeeListSerializer(serializers.Serializer):
    """Serializer for employee list in ent-admin."""

    id = serializers.IntegerField(source='user.id')
    real_name = serializers.CharField()
    position = serializers.CharField(allow_null=True)
    phone = serializers.CharField(source='user.username')
    role_code = serializers.CharField()
    is_active = serializers.BooleanField(source='user.is_active')
    created_at = serializers.DateTimeField()


class EmployeeCreateSerializer(serializers.Serializer):
    """Serializer for creating/binding an employee."""

    phone = serializers.CharField(max_length=11)
    real_name = serializers.CharField(max_length=50)
    position = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    role_code = serializers.ChoiceField(choices=['enterprise_admin', 'employee'])


class EmployeeUpdateSerializer(serializers.Serializer):
    """Serializer for updating an employee."""

    real_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    position = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    role_code = serializers.ChoiceField(choices=['enterprise_admin', 'employee'], required=False)
    is_active = serializers.BooleanField(required=False)


class EntAdminOpportunityListSerializer(serializers.ModelSerializer):
    """Serializer for opportunity list in ent-admin (enterprise's own opportunities)."""

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
            'id', 'type', 'title', 'enterprise_id', 'enterprise_name',
            'publisher_id', 'publisher_name',
            'industry_id', 'industry_name',
            'sub_industry_id', 'sub_industry_name',
            'category_id', 'category_name',
            'province_id', 'province_name',
            'region_id', 'region_name',
            'tags', 'status', 'view_count', 'created_at',
        ]

    def get_publisher_name(self, obj):
        if obj.publisher:
            profile = getattr(obj.publisher, 'ent_user_profile', None)
            if profile and profile.real_name:
                return profile.real_name
            return obj.publisher.username
        return None

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


class EntAdminOpportunityUpdateSerializer(serializers.Serializer):
    """Serializer for updating an opportunity in ent-admin. type is not modifiable."""

    title = serializers.CharField(max_length=200, required=False)
    industry_id = serializers.IntegerField(required=False)
    sub_industry_id = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField(required=False)
    province_id = serializers.IntegerField(required=False)
    region_id = serializers.IntegerField(required=False)
    detail = serializers.CharField(required=False)
    tags = serializers.JSONField(required=False)
    contact_name = serializers.CharField(max_length=50, required=False)
    contact_phone = serializers.CharField(max_length=11, required=False)
    contact_wechat = serializers.CharField(
        max_length=50, required=False, allow_blank=True,
    )
