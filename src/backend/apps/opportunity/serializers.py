from rest_framework import serializers
from apps.enterprise.models import MasterData
from .models import Opportunity


def _get_master_data_name(data_id, category):
    """Look up a MasterData name by id and category."""
    if not data_id:
        return ''
    md = MasterData.objects.filter(
        id=data_id, category=category, is_active=True,
    ).first()
    return md.name if md else ''


class OpportunityListSerializer(serializers.ModelSerializer):
    """Serializer for opportunity list view (public, ACTIVE only)."""

    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )
    industry_name = serializers.SerializerMethodField()
    sub_industry_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id', 'type', 'title', 'enterprise_id', 'enterprise_name',
            'industry_name', 'sub_industry_name', 'category_name',
            'province_name', 'region_name', 'tags', 'view_count', 'created_at',
        ]

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


class OpportunityDetailSerializer(serializers.ModelSerializer):
    """Serializer for opportunity detail view (authenticated)."""

    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )
    publisher_name = serializers.SerializerMethodField()
    industry_name = serializers.SerializerMethodField()
    sub_industry_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()
    contact_name = serializers.SerializerMethodField()
    contact_phone = serializers.SerializerMethodField()
    contact_wechat = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id', 'type', 'title', 'detail',
            'enterprise_id', 'enterprise_name',
            'publisher_id', 'publisher_name',
            'industry_id', 'industry_name',
            'sub_industry_id', 'sub_industry_name',
            'category_id', 'category_name',
            'region_id', 'province_id',
            'province_name', 'region_name',
            'tags', 'status', 'view_count',
            'contact_name', 'contact_phone', 'contact_wechat',
            'created_at', 'updated_at',
        ]

    def get_publisher_name(self, obj):
        if obj.publisher:
            parts = [obj.publisher.first_name, obj.publisher.last_name]
            full_name = ' '.join(p for p in parts if p)
            return full_name if full_name else obj.publisher.username
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

    def get_contact_name(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return None
        return obj.contact_name or None

    def get_contact_phone(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return None
        phone = obj.contact_phone
        if phone and len(phone) == 11:
            return phone[:3] + '****' + phone[7:]
        return phone or None

    def get_contact_wechat(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return None
        return obj.contact_wechat or None


class OpportunityCreateSerializer(serializers.Serializer):
    """Serializer for creating a new opportunity."""

    type = serializers.ChoiceField(choices=['BUY', 'SUPPLY'])
    title = serializers.CharField(max_length=200)
    industry_id = serializers.IntegerField()
    sub_industry_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    province_id = serializers.IntegerField()
    region_id = serializers.IntegerField()
    detail = serializers.CharField()
    tags = serializers.JSONField(required=False, default=list)
    contact_name = serializers.CharField(max_length=50)
    contact_phone = serializers.CharField(max_length=11)
    contact_wechat = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default='',
    )


class OpportunityUpdateSerializer(serializers.Serializer):
    """Serializer for updating an opportunity. type is not modifiable."""

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
