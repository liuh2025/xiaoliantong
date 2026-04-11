"""Unit tests for FEED-006: Offline feed API.

PUT /api/v1/feed/feed/{id}/offline
- Requires IsAuthenticated
- Only publisher or enterprise admin can set offline
- Changes status from ACTIVE to OFFLINE
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.enterprise.models import Enterprise
from apps.feed.models import Feed


class FeedOfflineTests(TestCase):
    """Tests for FEED-006: Offline feed."""

    def setUp(self):
        """Create shared test fixtures."""
        self.client = APIClient()

        # Publisher user + verified enterprise
        self.publisher = User.objects.create_user(
            username='publisher', password='pass1234',
        )
        self.enterprise = Enterprise.objects.create(
            name='Offline Corp',
            credit_code='123456789012345678',
            legal_representative='Alice',
            business_license='http://example.com/license.png',
            industry_id=1,
            sub_industry_id=2,
            category_id=3,
            province_id=4,
            region_id=5,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )

        self.active_feed = Feed.objects.create(
            publisher=self.publisher,
            enterprise=self.enterprise,
            content='Active feed to offline',
        )
        self.offline_feed = Feed.objects.create(
            publisher=self.publisher,
            enterprise=self.enterprise,
            content='Already offline',
            status=Feed.FeedStatus.OFFLINE,
        )

        # Enterprise admin
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
        return f'/api/v1/feed/feed/{pk}/offline'

    def test_publisher_can_offline_feed(self):
        """Publisher can set their feed to OFFLINE."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.put(self._get_url(self.active_feed.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['id'], self.active_feed.id)
        self.assertEqual(data['data']['status'], 'OFFLINE')

    def test_enterprise_admin_can_offline_feed(self):
        """Enterprise admin can set feeds to OFFLINE."""
        self.client.force_authenticate(user=self.ent_admin)
        response = self.client.put(self._get_url(self.active_feed.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['status'], 'OFFLINE')

    def test_other_user_cannot_offline(self):
        """Unrelated user cannot set feed offline."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(self._get_url(self.active_feed.id))
        data = response.json()
        self.assertEqual(data['code'], 403)

    def test_unauthenticated_cannot_offline(self):
        """Unauthenticated user cannot set feed offline."""
        response = self.client.put(self._get_url(self.active_feed.id))
        self.assertIn(response.status_code, [401, 403])

    def test_offline_already_offline_feed(self):
        """Setting OFFLINE on already OFFLINE feed should fail."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.put(self._get_url(self.offline_feed.id))
        data = response.json()
        self.assertEqual(data['code'], 400)

    def test_offline_nonexistent_feed(self):
        """Setting non-existent feed offline returns 404."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.put(self._get_url(99999))
        data = response.json()
        self.assertEqual(data['code'], 404)

    def test_offline_persists_in_db(self):
        """Offline status should persist in database."""
        self.client.force_authenticate(user=self.publisher)
        self.client.put(self._get_url(self.active_feed.id))
        self.active_feed.refresh_from_db()
        self.assertEqual(self.active_feed.status, Feed.FeedStatus.OFFLINE)
