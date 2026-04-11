from rest_framework import serializers
from .models import Feed


def _get_publisher_name(user):
    """Get display name for a user: first_name + last_name, or username."""
    if not user:
        return ''
    parts = [user.first_name, user.last_name]
    full_name = ' '.join(p for p in parts if p)
    return full_name if full_name else user.username


def _get_publisher_role(user):
    """Get role_code from UserProfile, or empty string."""
    try:
        return user.ent_user_profile.role_code
    except Exception:
        return ''


class FeedListSerializer(serializers.ModelSerializer):
    """Serializer for feed list view (public, ACTIVE only)."""

    publisher_name = serializers.SerializerMethodField()
    publisher_role = serializers.SerializerMethodField()
    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )
    enterprise_logo = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = [
            'id', 'content', 'images',
            'publisher_id', 'publisher_name', 'publisher_role',
            'enterprise_id', 'enterprise_name', 'enterprise_logo',
            'created_at',
        ]

    def get_publisher_name(self, obj):
        return _get_publisher_name(obj.publisher)

    def get_publisher_role(self, obj):
        return _get_publisher_role(obj.publisher)

    def get_enterprise_logo(self, obj):
        logo = getattr(obj.enterprise, 'logo_url', None)
        return logo or ''


class FeedDetailSerializer(serializers.ModelSerializer):
    """Serializer for feed detail view (authenticated)."""

    publisher_name = serializers.SerializerMethodField()
    publisher_role = serializers.SerializerMethodField()
    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )
    enterprise_logo = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = [
            'id', 'content', 'images',
            'publisher_id', 'publisher_name', 'publisher_role',
            'enterprise_id', 'enterprise_name', 'enterprise_logo',
            'status', 'created_at', 'updated_at',
        ]

    def get_publisher_name(self, obj):
        return _get_publisher_name(obj.publisher)

    def get_publisher_role(self, obj):
        return _get_publisher_role(obj.publisher)

    def get_enterprise_logo(self, obj):
        logo = getattr(obj.enterprise, 'logo_url', None)
        return logo or ''


class FeedCreateSerializer(serializers.Serializer):
    """Serializer for creating a new feed post."""

    content = serializers.CharField(max_length=1000)
    images = serializers.JSONField(required=False, default=list)


class FeedNewestSerializer(serializers.Serializer):
    """Serializer for newest feeds (limited fields, truncated content)."""

    id = serializers.IntegerField()
    content = serializers.SerializerMethodField()
    publisher_name = serializers.SerializerMethodField()
    enterprise_name = serializers.CharField(
        source='enterprise.name', read_only=True,
    )
    created_at = serializers.DateTimeField()

    def get_content(self, obj):
        text = obj.content or ''
        if len(text) > 100:
            return text[:100] + '...'
        return text

    def get_publisher_name(self, obj):
        return _get_publisher_name(obj.publisher)
