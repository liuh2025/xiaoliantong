import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Message
from .serializers import MessageListSerializer, MessageRecentSerializer

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


# ==================== MSG-002: Notification List ====================


class NotificationListView(APIView):
    """GET /api/v1/msg/notifications - List notifications for current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List notifications for the authenticated user."""
        queryset = Message.objects.filter(
            receiver=request.user,
        ).select_related('sender')

        # Filter by is_read if provided
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() in ('true', '1', 'yes'):
                queryset = queryset.filter(is_read=True)
            elif is_read.lower() in ('false', '0', 'no'):
                queryset = queryset.filter(is_read=False)

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

        serializer = MessageListSerializer(items, many=True)
        return _success_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': serializer.data,
        })


# ==================== MSG-003: Read ====================


class NotificationReadView(APIView):
    """PUT /api/v1/msg/notifications/{id}/read - Mark single notification as read."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """Mark a single notification as read."""
        try:
            msg = Message.objects.get(pk=pk, receiver=request.user)
        except Message.DoesNotExist:
            return _error_response('消息不存在', 404)

        msg.is_read = True
        msg.save(update_fields=['is_read'])
        return _success_response({'id': msg.id, 'is_read': msg.is_read})


class NotificationReadAllView(APIView):
    """PUT /api/v1/msg/notifications/read-all - Mark all notifications as read."""

    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Mark all notifications as read for the current user."""
        updated = Message.objects.filter(
            receiver=request.user, is_read=False,
        ).update(is_read=True)
        return _success_response({'updated_count': updated})


# ==================== MSG-004: Recent ====================


class NotificationRecentView(APIView):
    """GET /api/v1/msg/notifications/recent - Recent 5 unread + unread_count."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return recent 5 unread messages and unread count."""
        unread_count = Message.objects.filter(
            receiver=request.user, is_read=False,
        ).count()

        recent_messages = Message.objects.filter(
            receiver=request.user, is_read=False,
        ).select_related('sender').order_by('-created_at')[:5]

        serializer = MessageRecentSerializer(list(recent_messages), many=True)
        return _success_response({
            'unread_count': unread_count,
            'items': serializer.data,
        })


# ==================== MSG-005: Trigger Helper ====================


def create_notification(receiver, type, title, content,
                        sender=None, related_type='', related_id=None):
    """Create a notification message for use by other modules."""
    return Message.objects.create(
        receiver=receiver,
        sender=sender,
        type=type,
        title=title,
        content=content,
        related_type=related_type,
        related_id=related_id,
    )
