"""Unit tests for FEED-002: Feed list API.

GET /api/v1/feed/feed
- Public access (AllowAny)
- Returns ACTIVE feeds, ordered by created_at desc
- Supports keyword search and pagination
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.enterprise.models import Enterprise
from apps.feed.models import Feed


class FeedListTests(TestCase):
    """Tests for FEED-002: Feed list."""

    def setUp(self):
        """Create shared test fixtures."""
        self.client = APIClient()
        self.url = '/api/v1/feed/feed'

        # Create user and verified enterprise
        self.user = User.objects.create_user(
            username='feeduser', password='pass1234',
        )
        self.enterprise = Enterprise.objects.create(
            name='Feed Corp',
            credit_code='111122223333444455',
            legal_representative='Alice',
            business_license='http://example.com/license.png',
            industry_id=1,
            sub_industry_id=2,
            category_id=3,
            province_id=4,
            region_id=5,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )

        # Create some ACTIVE feeds
        self.feed1 = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='First feed post about Python',
        )
        self.feed2 = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Second feed post about Django',
        )

    def test_list_feeds_returns_200(self):
        """Public user can list feeds."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 200)

    def test_list_feeds_returns_active_only(self):
        """Only ACTIVE feeds should be returned."""
        offline_feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Offline feed',
            status=Feed.FeedStatus.OFFLINE,
        )
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        for item in items:
            self.assertNotEqual(item['id'], offline_feed.id)

    def test_list_feeds_ordered_by_created_at_desc(self):
        """Feeds should be ordered by created_at descending."""
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 2)
        # feed2 was created after feed1, so it comes first
        self.assertEqual(items[0]['id'], self.feed2.id)
        self.assertEqual(items[1]['id'], self.feed1.id)

    def test_list_feeds_pagination(self):
        """Pagination should work with page and page_size params."""
        # Create more feeds to test pagination
        for i in range(5):
            Feed.objects.create(
                publisher=self.user,
                enterprise=self.enterprise,
                content=f'Extra feed {i}',
            )
        response = self.client.get(self.url, {'page': 1, 'page_size': 3})
        data = response.json()
        self.assertEqual(data['data']['page'], 1)
        self.assertEqual(data['data']['page_size'], 3)
        self.assertEqual(len(data['data']['items']), 3)
        self.assertEqual(data['data']['total'], 7)  # 2 + 5

    def test_list_feeds_default_pagination(self):
        """Default pagination is page=1, page_size=20."""
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['data']['page'], 1)
        self.assertEqual(data['data']['page_size'], 20)

    def test_list_feeds_keyword_search(self):
        """Keyword search should filter by content."""
        response = self.client.get(self.url, {'keyword': 'Python'})
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['id'], self.feed1.id)

    def test_list_feeds_keyword_no_match(self):
        """Keyword search with no match returns empty items."""
        response = self.client.get(self.url, {'keyword': 'nonexistent'})
        data = response.json()
        items = data['data']['items']
        self.assertEqual(len(items), 0)

    def test_list_feeds_response_fields(self):
        """Response items should have expected fields."""
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        expected_fields = [
            'id', 'content', 'images',
            'publisher_id', 'publisher_name', 'publisher_role',
            'enterprise_id', 'enterprise_name', 'enterprise_logo',
            'created_at',
        ]
        for field in expected_fields:
            self.assertIn(field, item)

    def test_list_feeds_enterprise_name(self):
        """enterprise_name should come from enterprise.name."""
        response = self.client.get(self.url)
        data = response.json()
        item = data['data']['items'][0]
        self.assertEqual(item['enterprise_name'], 'Feed Corp')

    def test_list_feeds_pagination_page_2(self):
        """Page 2 should work correctly."""
        for i in range(5):
            Feed.objects.create(
                publisher=self.user,
                enterprise=self.enterprise,
                content=f'Extra feed {i}',
            )
        response = self.client.get(self.url, {'page': 2, 'page_size': 3})
        data = response.json()
        self.assertEqual(data['data']['page'], 2)
        self.assertEqual(len(data['data']['items']), 3)
