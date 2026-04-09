"""Unit tests for MSG-004: Recent notifications API.

GET /api/v1/msg/notifications/recent
- IsAuthenticated required
- Returns recent 5 unread messages + unread_count
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.msg.models import Message


class NotificationRecentTests(TestCase):
    """Tests for MSG-004: Recent notifications."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/msg/notifications/recent'

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

    def test_recent_requires_authentication(self):
        """Unauthenticated request should return 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_recent_returns_200(self):
        """Authenticated user can get recent notifications."""
        self._authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 200)

    def test_recent_returns_unread_count(self):
        """unread_count should reflect unread messages for the user."""
        self._authenticate()
        self._create_message(self.user, is_read=False, title='Unread1')
        self._create_message(self.user, is_read=False, title='Unread2')
        self._create_message(self.user, is_read=True, title='Read1')
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['unread_count'], 2)

    def test_recent_returns_only_unread_items(self):
        """Items should only contain unread messages."""
        self._authenticate()
        self._create_message(self.user, is_read=True, title='Read')
        self._create_message(self.user, is_read=False, title='Unread')
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'Unread')

    def test_recent_limited_to_5(self):
        """Should return at most 5 unread messages."""
        self._authenticate()
        for i in range(8):
            self._create_message(self.user, is_read=False, title=f'Msg {i}')
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['unread_count'], 8)
        self.assertEqual(len(data['data']['items']), 5)

    def test_recent_data_isolation(self):
        """Should only include messages where receiver=request.user."""
        self._authenticate()
        self._create_message(self.user, is_read=False, title='My msg')
        self._create_message(self.other_user, is_read=False, title='Other msg')
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['unread_count'], 1)
        items = data['data']['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'My msg')

    def test_recent_empty_when_no_messages(self):
        """Should return unread_count=0 and empty items when no messages."""
        self._authenticate()
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['unread_count'], 0)
        self.assertEqual(data['data']['items'], [])

    def test_recent_ordered_by_created_at_desc(self):
        """Items should be ordered by created_at descending."""
        self._authenticate()
        msg1 = self._create_message(self.user, is_read=False, title='First')
        msg2 = self._create_message(self.user, is_read=False, title='Second')
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertEqual(items[0]['id'], msg2.id)
        self.assertEqual(items[1]['id'], msg1.id)

    def test_recent_response_fields(self):
        """Items should have expected fields."""
        self._authenticate()
        sender = User.objects.create_user(username='recent_sender', password='pass')
        self._create_message(
            self.user, is_read=False,
            type=Message.MessageType.CONTACT_RECEIVED,
            title='Title', content='Content',
            sender=sender, related_type='opportunity', related_id=10,
        )
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        expected_fields = [
            'id', 'sender_id', 'sender_name', 'type',
            'title', 'content', 'is_read',
            'related_type', 'related_id', 'created_at',
        ]
        for field in expected_fields:
            self.assertIn(field, item)

    def test_recent_all_read(self):
        """When all messages are read, unread_count should be 0."""
        self._authenticate()
        self._create_message(self.user, is_read=True, title='Read')
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['unread_count'], 0)
        self.assertEqual(data['data']['items'], [])
