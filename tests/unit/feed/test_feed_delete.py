"""Unit tests for FEED-005: Delete feed API.

DELETE /api/v1/feed/feed/{id}
- Requires IsAuthenticated
- Only publisher or enterprise admin can delete
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.enterprise.models import Enterprise
from apps.feed.models import Feed


class FeedDeleteTests(TestCase):
    """Tests for FEED-005: Delete feed."""

    def setUp(self):
        """Create shared test fixtures."""
        self.client = APIClient()

        # Publisher user + verified enterprise
        self.publisher = User.objects.create_user(
            username='publisher', password='pass1234',
        )
        self.enterprise = Enterprise.objects.create(
            name='Delete Corp',
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

        self.feed = Feed.objects.create(
            publisher=self.publisher,
            enterprise=self.enterprise,
            content='To be deleted',
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
        return f'/api/v1/feed/feed/{pk}'

    def test_publisher_can_delete_own_feed(self):
        """Publisher can delete their own feed."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.delete(self._get_url(self.feed.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['message'], '删除成功')

    def test_enterprise_admin_can_delete(self):
        """Enterprise admin can delete feeds from their enterprise."""
        self.client.force_authenticate(user=self.ent_admin)
        response = self.client.delete(self._get_url(self.feed.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['message'], '删除成功')

    def test_other_user_cannot_delete(self):
        """Unrelated user cannot delete feed."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self._get_url(self.feed.id))
        data = response.json()
        self.assertEqual(data['code'], 403)

    def test_unauthenticated_cannot_delete(self):
        """Unauthenticated user cannot delete feed."""
        response = self.client.delete(self._get_url(self.feed.id))
        self.assertIn(response.status_code, [401, 403])

    def test_delete_nonexistent_feed(self):
        """Deleting non-existent feed returns 404."""
        self.client.force_authenticate(user=self.publisher)
        response = self.client.delete(self._get_url(99999))
        data = response.json()
        self.assertEqual(data['code'], 404)

    def test_delete_actually_removes_feed(self):
        """Feed should be removed from database after delete."""
        feed_id = self.feed.id
        self.client.force_authenticate(user=self.publisher)
        self.client.delete(self._get_url(feed_id))
        self.assertFalse(Feed.objects.filter(id=feed_id).exists())
