from rest_framework import serializers
from .models import Message


def _get_sender_name(user):
    """Get display name for a user: first_name + last_name, or username."""
    if not user:
        return ''
    parts = [user.first_name, user.last_name]
    full_name = ' '.join(p for p in parts if p)
    return full_name if full_name else user.username


class MessageListSerializer(serializers.ModelSerializer):
    """Serializer for message list view."""

    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender_id', 'sender_name', 'type',
            'title', 'content', 'is_read',
            'related_type', 'related_id', 'created_at',
        ]

    def get_sender_name(self, obj):
        return _get_sender_name(obj.sender)


class MessageRecentSerializer(serializers.ModelSerializer):
    """Serializer for recent notification view."""

    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender_id', 'sender_name', 'type',
            'title', 'content', 'is_read',
            'related_type', 'related_id', 'created_at',
        ]

    def get_sender_name(self, obj):
        return _get_sender_name(obj.sender)
