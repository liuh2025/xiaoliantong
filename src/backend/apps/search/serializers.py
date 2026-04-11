from rest_framework import serializers
from apps.enterprise.models import MasterData


def _get_master_data_name(data_id, category):
    """Look up a MasterData name by id and category."""
    if not data_id:
        return ''
    md = MasterData.objects.filter(
        id=data_id, category=category, is_active=True,
    ).first()
    return md.name if md else ''


class SearchOpportunitySerializer(serializers.Serializer):
    """Serializer for search results from the opportunity domain."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    type = serializers.CharField()
    enterprise_id = serializers.IntegerField()
    enterprise_name = serializers.SerializerMethodField()
    industry_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    tags = serializers.JSONField()
    view_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()

    def get_enterprise_name(self, obj):
        return obj.enterprise.name if obj.enterprise else ''

    def get_industry_name(self, obj):
        return _get_master_data_name(obj.industry_id, 'industry')

    def get_category_name(self, obj):
        return _get_master_data_name(obj.category_id, 'category')

    def get_province_name(self, obj):
        return _get_master_data_name(obj.province_id, 'region')


class SearchEnterpriseSerializer(serializers.Serializer):
    """Serializer for search results from the enterprise domain."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    logo_url = serializers.CharField(allow_null=True)
    industry_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    tags = serializers.JSONField(allow_null=True)
    auth_status = serializers.CharField()

    def get_industry_name(self, obj):
        return _get_master_data_name(obj.industry_id, 'industry')

    def get_category_name(self, obj):
        return _get_master_data_name(obj.category_id, 'category')

    def get_province_name(self, obj):
        return _get_master_data_name(obj.province_id, 'region')


class SearchFeedSerializer(serializers.Serializer):
    """Serializer for search results from the feed domain."""

    id = serializers.IntegerField()
    content = serializers.CharField()
    images = serializers.JSONField()
    publisher_id = serializers.IntegerField()
    publisher_name = serializers.SerializerMethodField()
    enterprise_id = serializers.IntegerField()
    enterprise_name = serializers.SerializerMethodField()
    enterprise_logo = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_publisher_name(self, obj):
        user = obj.publisher
        if not user:
            return ''
        parts = [user.first_name, user.last_name]
        full_name = ' '.join(p for p in parts if p)
        return full_name if full_name else user.username

    def get_enterprise_name(self, obj):
        return obj.enterprise.name if obj.enterprise else ''

    def get_enterprise_logo(self, obj):
        logo = getattr(obj.enterprise, 'logo_url', None)
        return logo or ''
