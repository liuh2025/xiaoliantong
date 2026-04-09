"""Unit tests for FEED-003: Feed detail API.

GET /api/v1/feed/feed/{id}
- Requires IsAuthenticated
- OFFLINE feeds only visible to publisher and enterprise admin
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.enterprise.models import Enterprise
from apps.feed.models import Feed


class FeedDetailTests(TestCase):
    """Tests for FEED-003: Feed detail."""

    def setUp(self):
        """Create shared test fixtures."""
        self.client = APIClient()

        # Publisher user + verified enterprise
        self.publisher = User.objects.create_user(
            username='publisher', password='pass1234',
        )
        self.enterprise = Enterprise.objects.create(
            name='Detail Corp',
            credit_code='123456789012345678',
            legal_representative='Bob',
            business_license='http://example.com/license.png',
            industry_id=1,
            sub_industry_id=2,
            category_id=3,
            province_id=4,
            region_id=5,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )

        # Active feed
        self.active_feed = Feed.objects.create(
            publisher=self.publisher,
            enterprise=self.enterprise,
            content='Active feed content',
        )

        # Offline feed
        self.offline_feed = Feed.objects.create(
            publisher=self.publisher,
            enterprise=self.enterprise,
            content='Offline feed content',
            status=Feed.FeedStatus.OFFLINE,
        )

        # Another user (enterprise admin of same enterprise)
        self.ent_admin = User.objects.create_user(
            username='entadmin', password='pass1234',
        )
        self.ent_admin.ent_user_profile.role_code = 'enterprise_admin'
        self.ent_admin.ent_user_profile.enterprise_id = self.enterprise.id
        self.ent_admin.ent_user_profile.save()

        # Unrelated user
        self.other_user = User.objects.create_user(
            username='otheruser', password='pass1234',
        )

    def _get_url(self, pk):
        return f'/api/v1/feed/feed/{pk}'

    def test_authenticated_user_can_view_active_feed(self):
        """Authenticated user can view an ACTIVE feed."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self._get_url(self.active_feed.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['id'], self.active_feed.id)
        self.assertEqual(data['data']['content'], 'Active feed content')

    def test_unauthenticated_user_cannot_view_feed(self):
        """Unauthenticated user should be denied."""
        response = self.client.get(self._get_url(self.active_feed.id))
        self.assertIn(response.status_code, [401, 403])

    def test_detail_response_includes_updated_at(self):
        """Detail response should include updated_at field."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.get(self._get_url(self.active_feed.id))
        data = response.json()
        self.assertIn('updated_at', data['data'])

    def test_detail_response_fields(self):
        """Detail response should have all expected fields."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.get(self._get_url(self.active_feed.id))
        data = response.json()
        expected_fields = [
            'id', 'content', 'images',
            'publisher_id', 'publisher_name', 'publisher_role',
            'enterprise_id', 'enterprise_name', 'enterprise_logo',
            'status', 'created_at', 'updated_at',
        ]
        for field in expected_fields:
            self.assertIn(field, data['data'])

    def test_offline_feed_visible_to_publisher(self):
        """Publisher can see their own OFFLINE feed."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.get(self._get_url(self.offline_feed.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['id'], self.offline_feed.id)

    def test_offline_feed_visible_to_enterprise_admin(self):
        """Enterprise admin can see OFFLINE feeds from their enterprise."""
        self.client.force_authenticate(user=self.ent_admin)
        response = self.client.get(self._get_url(self.offline_feed.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['id'], self.offline_feed.id)

    def test_offline_feed_hidden_from_others(self):
        """OFFLINE feed should be hidden from unrelated users."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self._get_url(self.offline_feed.id))
        data = response.json()
        self.assertEqual(data['code'], 404)

    def test_nonexistent_feed_returns_404(self):
        """Request for non-existent feed should return 404."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.get(self._get_url(99999))
        data = response.json()
        self.assertEqual(data['code'], 404)

    def test_detail_includes_status(self):
        """Detail response should include status field."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.get(self._get_url(self.active_feed.id))
        data = response.json()
        self.assertEqual(data['data']['status'], 'ACTIVE')
