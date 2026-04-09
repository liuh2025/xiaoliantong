"""Unit tests for MSG-002: Notification list API.

GET /api/v1/msg/notifications
- IsAuthenticated required
- Data isolation: only receiver=request.user
- Pagination: page, page_size
- Filter: is_read
- Response fields: total, page, page_size, items
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.msg.models import Message


class NotificationListTests(TestCase):
    """Tests for MSG-002: Notification list."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/msg/notifications'

        self.user = User.objects.create_user(
            username='testuser', password='pass1234',
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='pass1234',
        )

        # Get JWT token for self.user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    def _authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def _create_message(self, receiver, type=Message.MessageType.SYSTEM,
                        title='Test', content='Test content', **kwargs):
        return Message.objects.create(
            receiver=receiver, type=type,
            title=title, content=content, **kwargs,
        )

    def test_list_requires_authentication(self):
        """Unauthenticated request should return 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_list_returns_200(self):
        """Authenticated user can list notifications."""
        self._authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 200)

    def test_list_data_isolation(self):
        """Only messages where receiver=request.user are returned."""
        self._authenticate()
        self._create_message(self.user, title='My message')
        self._create_message(self.other_user, title='Other message')
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'My message')

    def test_list_pagination(self):
        """Pagination should work with page and page_size params."""
        self._authenticate()
        for i in range(5):
            self._create_message(self.user, title=f'Msg {i}')
        response = self.client.get(self.url, {'page': 1, 'page_size': 2})
        data = response.json()
        self.assertEqual(data['data']['page'], 1)
        self.assertEqual(data['data']['page_size'], 2)
        self.assertEqual(len(data['data']['items']), 2)
        self.assertEqual(data['data']['total'], 5)

    def test_list_default_pagination(self):
        """Default pagination is page=1, page_size=20."""
        self._authenticate()
        self._create_message(self.user)
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['page'], 1)
        self.assertEqual(data['data']['page_size'], 20)

    def test_list_page_2(self):
        """Page 2 should return correct items."""
        self._authenticate()
        for i in range(5):
            self._create_message(self.user, title=f'Msg {i}')
        response = self.client.get(self.url, {'page': 2, 'page_size': 2})
        data = response.json()
        self.assertEqual(data['data']['page'], 2)
        self.assertEqual(len(data['data']['items']), 2)

    def test_list_filter_is_read_true(self):
        """Filter by is_read=true should return only read messages."""
        self._authenticate()
        self._create_message(self.user, title='Read msg', is_read=True)
        self._create_message(self.user, title='Unread msg', is_read=False)
        response = self.client.get(self.url, {'is_read': 'true'})
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'Read msg')

    def test_list_filter_is_read_false(self):
        """Filter by is_read=false should return only unread messages."""
        self._authenticate()
        self._create_message(self.user, title='Read msg', is_read=True)
        self._create_message(self.user, title='Unread msg', is_read=False)
        response = self.client.get(self.url, {'is_read': 'false'})
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'Unread msg')

    def test_list_ordered_by_created_at_desc(self):
        """Messages should be ordered by created_at descending."""
        self._authenticate()
        msg1 = self._create_message(self.user, title='First')
        msg2 = self._create_message(self.user, title='Second')
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertEqual(items[0]['id'], msg2.id)
        self.assertEqual(items[1]['id'], msg1.id)

    def test_list_response_fields(self):
        """Response items should have expected fields."""
        self._authenticate()
        sender = User.objects.create_user(username='sender_user', password='pass')
        self._create_message(
            self.user, type=Message.MessageType.AUDIT_APPROVED,
            title='Title', content='Content',
            sender=sender, related_type='enterprise', related_id=1,
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

    def test_list_empty_for_user_with_no_messages(self):
        """User with no messages should get empty items."""
        self._authenticate()
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['total'], 0)
        self.assertEqual(data['data']['items'], [])

    def test_list_sender_name_uses_full_name(self):
        """sender_name should prefer first_name + last_name."""
        self._authenticate()
        sender = User.objects.create_user(
            username='named_sender', password='pass',
            first_name='John', last_name='Doe',
        )
        self._create_message(self.user, title='Named', content='c', sender=sender)
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        self.assertEqual(item['sender_name'], 'John Doe')

    def test_list_sender_name_falls_back_to_username(self):
        """sender_name should fall back to username if no real name."""
        self._authenticate()
        sender = User.objects.create_user(username='nosendername', password='pass')
        self._create_message(self.user, title='NoName', content='c', sender=sender)
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        self.assertEqual(item['sender_name'], 'nosendername')

    def test_list_sender_name_empty_when_no_sender(self):
        """sender_name should be empty when sender is null."""
        self._authenticate()
        self._create_message(self.user, title='System', content='c')
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        self.assertEqual(item['sender_name'], '')
        self.assertIsNone(item['sender_id'])
