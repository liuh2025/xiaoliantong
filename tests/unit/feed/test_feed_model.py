"""Unit tests for FEED-001: Feed model.

Verify Feed model creation, fields, choices, and Meta options.
"""
from django.test import TestCase
from django.contrib.auth.models import User

from apps.auth_app.models import UserProfile
from apps.enterprise.models import Enterprise
from apps.feed.models import Feed


class FeedModelTests(TestCase):
    """Tests for FEED-001: Feed model."""

    def setUp(self):
        """Create shared test fixtures."""
        self.user = User.objects.create_user(
            username='testuser', password='pass1234',
        )
        self.enterprise = Enterprise.objects.create(
            name='Test Corp',
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

    def test_create_feed_with_required_fields(self):
        """Feed can be created with required fields only."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Hello world!',
        )
        self.assertEqual(feed.content, 'Hello world!')
        self.assertEqual(feed.publisher, self.user)
        self.assertEqual(feed.enterprise, self.enterprise)

    def test_default_status_is_active(self):
        """New feed should have ACTIVE status by default."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Test',
        )
        self.assertEqual(feed.status, Feed.FeedStatus.ACTIVE)

    def test_default_images_is_empty_list(self):
        """New feed should have empty list for images by default."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Test',
        )
        self.assertEqual(feed.images, [])

    def test_images_can_store_url_list(self):
        """Feed images field can store a list of URLs."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='With images',
            images=['http://img1.jpg', 'http://img2.jpg'],
        )
        feed.refresh_from_db()
        self.assertEqual(len(feed.images), 2)
        self.assertEqual(feed.images[0], 'http://img1.jpg')

    def test_status_choices(self):
        """FeedStatus should have ACTIVE and OFFLINE choices."""
        self.assertEqual(Feed.FeedStatus.ACTIVE, 'ACTIVE')
        self.assertEqual(Feed.FeedStatus.OFFLINE, 'OFFLINE')

    def test_db_table_name(self):
        """Feed model should use feed_feed as db_table."""
        self.assertEqual(Feed._meta.db_table, 'feed_feed')

    def test_ordering(self):
        """Feed model should order by -created_at."""
        self.assertEqual(Feed._meta.ordering, ['-created_at'])

    def test_auto_timestamps(self):
        """created_at and updated_at should be auto-populated."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Timestamped',
        )
        self.assertIsNotNone(feed.created_at)
        self.assertIsNotNone(feed.updated_at)

    def test_str_representation(self):
        """Feed __str__ should return expected format."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Test',
        )
        self.assertIn('testuser', str(feed))

    def test_cascade_protect_on_publisher_delete(self):
        """Deleting publisher should be PROTECTed (raises error)."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Protected',
        )
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.user.delete()

    def test_cascade_protect_on_enterprise_delete(self):
        """Deleting enterprise should be PROTECTed (raises error)."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Protected',
        )
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.enterprise.delete()

    def test_feed_can_be_set_offline(self):
        """Feed status can be changed to OFFLINE."""
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Going offline',
        )
        feed.status = Feed.FeedStatus.OFFLINE
        feed.save(update_fields=['status', 'updated_at'])
        feed.refresh_from_db()
        self.assertEqual(feed.status, Feed.FeedStatus.OFFLINE)

    def test_images_max_9_in_application(self):
        """While DB doesn't enforce max 9, the view layer validates this."""
        # Create a feed with 10 images directly (bypassing view validation)
        images = [f'http://img{i}.jpg' for i in range(10)]
        feed = Feed.objects.create(
            publisher=self.user,
            enterprise=self.enterprise,
            content='Many images',
            images=images,
        )
        # The model accepts it; validation is at the view level
        self.assertEqual(len(feed.images), 10)
