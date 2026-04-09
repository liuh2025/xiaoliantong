"""Unit tests for FEED-004: Create feed API.

POST /api/v1/feed/feed
- Requires IsAuthenticated + verified enterprise binding
- content required, max 1000 chars
- images optional, max 9 URLs
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.enterprise.models import Enterprise
from apps.feed.models import Feed


class FeedCreateTests(TestCase):
    """Tests for FEED-004: Create feed."""

    def setUp(self):
        """Create shared test fixtures."""
        self.client = APIClient()
        self.url = '/api/v1/feed/feed'

        # Publisher user + verified enterprise
        self.user = User.objects.create_user(
            username='creator', password='pass1234',
        )
        self.enterprise = Enterprise.objects.create(
            name='Create Corp',
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
        self.user.ent_user_profile.role_code = 'employee'
        self.user.ent_user_profile.enterprise_id = self.enterprise.id
        self.user.ent_user_profile.save()

    def test_create_feed_success(self):
        """Authenticated user with verified enterprise can create feed."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {'content': 'Hello from create test!'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertIn('id', data['data'])
        self.assertEqual(data['data']['status'], 'ACTIVE')

    def test_create_feed_with_images(self):
        """Feed can be created with image URL list."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {
                'content': 'With images',
                'images': ['http://img1.jpg', 'http://img2.jpg'],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        feed = Feed.objects.first()
        self.assertEqual(len(feed.images), 2)

    def test_create_feed_max_9_images(self):
        """Creating feed with more than 9 images should fail."""
        self.client.force_authenticate(user=self.user)
        images = [f'http://img{i}.jpg' for i in range(10)]
        response = self.client.post(
            self.url,
            {'content': 'Too many images', 'images': images},
            format='json',
        )
        data = response.json()
        self.assertEqual(data['code'], 400)

    def test_create_feed_exactly_9_images_ok(self):
        """Creating feed with exactly 9 images should succeed."""
        self.client.force_authenticate(user=self.user)
        images = [f'http://img{i}.jpg' for i in range(9)]
        response = self.client.post(
            self.url,
            {'content': 'Nine images', 'images': images},
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    def test_create_feed_without_images(self):
        """Feed can be created without images (default empty list)."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {'content': 'No images'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        feed = Feed.objects.first()
        self.assertEqual(feed.images, [])

    def test_create_feed_auto_sets_publisher_and_enterprise(self):
        """Publisher and enterprise should be set from request.user."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {'content': 'Auto fields'},
            format='json',
        )
        feed = Feed.objects.first()
        self.assertEqual(feed.publisher, self.user)
        self.assertEqual(feed.enterprise, self.enterprise)

    def test_create_feed_unauthenticated(self):
        """Unauthenticated user cannot create feed."""
        response = self.client.post(
            self.url,
            {'content': 'No auth'},
            format='json',
        )
        self.assertIn(response.status_code, [401, 403])

    def test_create_feed_no_enterprise_binding(self):
        """User without enterprise binding cannot create feed."""
        user_no_ent = User.objects.create_user(
            username='noent', password='pass1234',
        )
        self.client.force_authenticate(user=user_no_ent)
        response = self.client.post(
            self.url,
            {'content': 'No enterprise'},
            format='json',
        )
        data = response.json()
        self.assertEqual(data['code'], 403)

    def test_create_feed_unverified_enterprise(self):
        """User with unverified enterprise cannot create feed."""
        unverified_ent = Enterprise.objects.create(
            name='Unverified Corp',
            credit_code='987654321098765432',
            legal_representative='Charlie',
            business_license='http://example.com/license.png',
            industry_id=1,
            sub_industry_id=2,
            category_id=3,
            province_id=4,
            region_id=5,
            auth_status=Enterprise.AuthStatus.PENDING,
        )
        user_unv = User.objects.create_user(
            username='unvuser', password='pass1234',
        )
        user_unv.ent_user_profile.enterprise_id = unverified_ent.id
        user_unv.ent_user_profile.save()

        self.client.force_authenticate(user=user_unv)
        response = self.client.post(
            self.url,
            {'content': 'Unverified ent'},
            format='json',
        )
        data = response.json()
        self.assertEqual(data['code'], 403)

    def test_create_feed_missing_content(self):
        """Creating feed without content should fail."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {},
            format='json',
        )
        data = response.json()
        self.assertEqual(data['code'], 400)

    def test_create_feed_content_max_1000(self):
        """Content exceeding 1000 chars should fail."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {'content': 'x' * 1001},
            format='json',
        )
        data = response.json()
        self.assertEqual(data['code'], 400)

    def test_create_feed_content_exactly_1000_ok(self):
        """Content of exactly 1000 chars should succeed."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {'content': 'x' * 1000},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
