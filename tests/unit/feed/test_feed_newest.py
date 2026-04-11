"""Unit tests for FEED-007: Newest feeds API.

GET /api/v1/feed/feed/newest
- Public access (AllowAny)
- Returns max 2 newest ACTIVE feeds from verified enterprises
- Content truncated to 100 chars + '...'
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.enterprise.models import Enterprise
from apps.feed.models import Feed


class FeedNewestTests(TestCase):
    """Tests for FEED-007: Newest feeds."""

    def setUp(self):
        """Create shared test fixtures."""
        self.client = APIClient()
        self.url = '/api/v1/feed/feed/newest'

        # Create user and verified enterprise
        self.user = User.objects.create_user(
            username='newestuser', password='pass1234',
        )
        self.verified_ent = Enterprise.objects.create(
            name='Verified Corp',
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

        # Unverified enterprise
        self.unverified_ent = Enterprise.objects.create(
            name='Unverified Corp',
            credit_code='987654321098765432',
            legal_representative='Bob',
            business_license='http://example.com/license2.png',
            industry_id=1,
            sub_industry_id=2,
            category_id=3,
            province_id=4,
            region_id=5,
            auth_status=Enterprise.AuthStatus.PENDING,
        )

    def test_newest_returns_max_2_feeds(self):
        """Should return at most 2 feeds."""
        for i in range(5):
            Feed.objects.create(
                publisher=self.user,
                enterprise=self.verified_ent,
                content=f'Feed {i}',
            )
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(len(data['data']['items']), 2)

    def test_newest_returns_active_only(self):
        """Only ACTIVE feeds should be returned."""
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.verified_ent,
            content='Active feed',
        )
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.verified_ent,
            content='Offline feed',
            status=Feed.FeedStatus.OFFLINE,
        )
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['content'], 'Active feed')

    def test_newest_returns_verified_enterprise_only(self):
        """Only feeds from verified enterprises should be returned."""
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.unverified_ent,
            content='Unverified enterprise feed',
        )
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 0)

    def test_newest_ordered_by_created_at_desc(self):
        """Newest feeds should be ordered by created_at descending."""
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.verified_ent,
            content='First feed',
        )
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.verified_ent,
            content='Second feed',
        )
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertEqual(items[0]['content'], 'Second feed')
        self.assertEqual(items[1]['content'], 'First feed')

    def test_newest_content_truncation(self):
        """Content longer than 100 chars should be truncated with '...'."""
        long_content = 'x' * 150
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.verified_ent,
            content=long_content,
        )
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        self.assertEqual(len(item['content']), 103)  # 100 + '...'
        self.assertTrue(item['content'].endswith('...'))

    def test_newest_content_no_truncation_for_short(self):
        """Content <= 100 chars should not be truncated."""
        short_content = 'Short content'
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.verified_ent,
            content=short_content,
        )
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        self.assertEqual(item['content'], short_content)

    def test_newest_response_fields(self):
        """Response items should have expected fields."""
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.verified_ent,
            content='Test',
        )
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        expected_fields = [
            'id', 'content', 'publisher_name', 'enterprise_name', 'created_at',
        ]
        for field in expected_fields:
            self.assertIn(field, item)

    def test_newest_public_access(self):
        """Unauthenticated users can access newest feeds."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_newest_empty_when_no_feeds(self):
        """Should return empty items when no feeds exist."""
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['items'], [])

    def test_newest_content_exactly_100_chars(self):
        """Content of exactly 100 chars should NOT be truncated."""
        content_100 = 'x' * 100
        Feed.objects.create(
            publisher=self.user,
            enterprise=self.verified_ent,
            content=content_100,
        )
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        self.assertEqual(item['content'], content_100)
        self.assertFalse(item['content'].endswith('...'))
