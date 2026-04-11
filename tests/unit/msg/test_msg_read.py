"""Unit tests for MSG-003: Notification read APIs.

PUT /api/v1/msg/notifications/{id}/read - Mark single as read
PUT /api/v1/msg/notifications/read-all - Mark all as read
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.msg.models import Message


class NotificationReadTests(TestCase):
    """Tests for MSG-003: Single notification read."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='pass1234',
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='pass1234',
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    def _authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def _create_message(self, receiver, **kwargs):
        defaults = {
            'type': Message.MessageType.SYSTEM,
            'title': 'Test',
            'content': 'Test content',
        }
        defaults.update(kwargs)
        return Message.objects.create(receiver=receiver, **defaults)

    # --- Single read ---

    def test_read_requires_authentication(self):
        """Unauthenticated request to read should return 401."""
        msg = self._create_message(self.user)
        response = self.client.put(f'/api/v1/msg/notifications/{msg.id}/read')
        self.assertEqual(response.status_code, 401)

    def test_read_marks_single_as_read(self):
        """PUT .../read should set is_read=True."""
        self._authenticate()
        msg = self._create_message(self.user, is_read=False)
        response = self.client.put(f'/api/v1/msg/notifications/{msg.id}/read')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertTrue(data['data']['is_read'])
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)

    def test_read_already_read(self):
        """Reading an already-read message should still return success."""
        self._authenticate()
        msg = self._create_message(self.user, is_read=True)
        response = self.client.put(f'/api/v1/msg/notifications/{msg.id}/read')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['data']['is_read'])

    def test_read_other_users_message_returns_404(self):
        """Cannot mark another user's message as read."""
        self._authenticate()
        msg = self._create_message(self.other_user, is_read=False)
        response = self.client.put(f'/api/v1/msg/notifications/{msg.id}/read')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 404)

    def test_read_nonexistent_message_returns_404(self):
        """Reading a non-existent message should return 404."""
        self._authenticate()
        response = self.client.put('/api/v1/msg/notifications/99999/read')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 404)

    def test_read_returns_message_id(self):
        """Response should include the message id."""
        self._authenticate()
        msg = self._create_message(self.user)
        response = self.client.put(f'/api/v1/msg/notifications/{msg.id}/read')
        data = response.json()
        self.assertEqual(data['data']['id'], msg.id)


class NotificationReadAllTests(TestCase):
    """Tests for MSG-003: Read all notifications."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='pass1234',
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='pass1234',
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    def _authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def _create_message(self, receiver, **kwargs):
        defaults = {
            'type': Message.MessageType.SYSTEM,
            'title': 'Test',
            'content': 'Test content',
        }
        defaults.update(kwargs)
        return Message.objects.create(receiver=receiver, **defaults)

    def test_read_all_requires_authentication(self):
        """Unauthenticated request should return 401."""
        response = self.client.put('/api/v1/msg/notifications/read-all')
        self.assertEqual(response.status_code, 401)

    def test_read_all_marks_all_unread_as_read(self):
        """All unread messages for the user should be marked as read."""
        self._authenticate()
        self._create_message(self.user, is_read=False, title='Msg1')
        self._create_message(self.user, is_read=False, title='Msg2')
        response = self.client.put('/api/v1/msg/notifications/read-all')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['updated_count'], 2)
        # Verify in DB
        self.assertEqual(
            Message.objects.filter(receiver=self.user, is_read=False).count(),
            0,
        )

    def test_read_all_does_not_affect_other_users(self):
        """Read-all should not affect other users' messages."""
        self._authenticate()
        self._create_message(self.user, is_read=False, title='My msg')
        self._create_message(self.other_user, is_read=False, title='Other msg')
        response = self.client.put('/api/v1/msg/notifications/read-all')
        data = response.json()
        self.assertEqual(data['data']['updated_count'], 1)
        # Other user's message should still be unread
        self.assertFalse(
            Message.objects.get(receiver=self.other_user).is_read,
        )

    def test_read_all_already_read(self):
        """Read-all when all messages are already read should return 0 updated."""
        self._authenticate()
        self._create_message(self.user, is_read=True, title='Read msg')
        response = self.client.put('/api/v1/msg/notifications/read-all')
        data = response.json()
        self.assertEqual(data['data']['updated_count'], 0)

    def test_read_all_no_messages(self):
        """Read-all when user has no messages should return 0 updated."""
        self._authenticate()
        response = self.client.put('/api/v1/msg/notifications/read-all')
        data = response.json()
        self.assertEqual(data['data']['updated_count'], 0)

    def test_read_all_mixed_read_unread(self):
        """Read-all should only update unread messages."""
        self._authenticate()
        self._create_message(self.user, is_read=True, title='Read')
        self._create_message(self.user, is_read=False, title='Unread1')
        self._create_message(self.user, is_read=False, title='Unread2')
        response = self.client.put('/api/v1/msg/notifications/read-all')
        data = response.json()
        self.assertEqual(data['data']['updated_count'], 2)
