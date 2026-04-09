"""PLAT-006: Feed content management tests."""
import itertools

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile
from apps.feed.models import Feed
from apps.msg.models import Message

_counter = itertools.count(200600)


def _unique_int():
    return next(_counter)


def build_enterprise(**overrides):
    n = _unique_int()
    defaults = {
        'name': f'Test Enterprise {n}',
        'credit_code': f'91{n:014d}X',
        'legal_representative': 'Zhang San',
        'business_license': f'https://example.com/license/test{n}.jpg',
        'industry_id': 1,
        'sub_industry_id': 101,
        'province_id': 110000,
        'region_id': 110100,
        'auth_status': Enterprise.AuthStatus.VERIFIED,
    }
    defaults.update(overrides)
    ent = Enterprise(**defaults)
    ent.save()
    return ent


def build_user(**overrides):
    n = _unique_int()
    defaults = {'username': f'testuser_{n}', 'password': 'testpass123'}
    defaults.update(overrides)
    return User.objects.create_user(**defaults)


def setup_profile(user, **kwargs):
    profile = user.ent_user_profile
    for key, value in kwargs.items():
        setattr(profile, key, value)
    profile.save()
    return profile


@pytest.mark.django_db
class TestContentFeedList:
    """Tests for GET /api/v1/plat-admin/content/feed."""

    def setup_method(self):
        self.url = reverse('plat_admin:content-feed-list')

    def test_list_feeds(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        Feed.objects.create(
            publisher=user, enterprise=ent,
            content='Test feed content',
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.data['data']['total'] >= 1

    def test_list_filter_by_keyword(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        Feed.objects.create(
            publisher=user, enterprise=ent,
            content='UniqueKeyword feed',
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'keyword': 'UniqueKeyword'})
        assert response.data['data']['total'] >= 1

    def test_list_filter_by_status(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        Feed.objects.create(
            publisher=user, enterprise=ent,
            content='Active feed',
            status=Feed.FeedStatus.ACTIVE,
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'status': 'ACTIVE'})
        items = response.data['data']['items']
        for item in items:
            assert item['status'] == 'ACTIVE'


@pytest.mark.django_db
class TestContentFeedDetail:
    """Tests for GET /api/v1/plat-admin/content/feed/{id}."""

    def test_detail(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        feed = Feed.objects.create(
            publisher=user, enterprise=ent,
            content='Detail feed',
        )
        url = reverse(
            'plat_admin:content-feed-detail',
            kwargs={'pk': feed.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 200
        assert response.data['data']['content'] == 'Detail feed'

    def test_detail_not_found(self, api_client, platform_admin):
        url = reverse(
            'plat_admin:content-feed-detail',
            kwargs={'pk': 99999},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 404


@pytest.mark.django_db
class TestContentFeedOffline:
    """Tests for PUT /api/v1/plat-admin/content/feed/{id}/offline."""

    def test_offline_feed(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        feed = Feed.objects.create(
            publisher=user, enterprise=ent,
            content='Feed to offline',
            status=Feed.FeedStatus.ACTIVE,
        )
        url = reverse(
            'plat_admin:content-feed-offline',
            kwargs={'pk': feed.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'reason': 'Inappropriate content'})
        assert response.data['code'] == 200

        feed.refresh_from_db()
        assert feed.status == Feed.FeedStatus.OFFLINE

        assert Message.objects.filter(
            receiver=user, type='SYSTEM', title='动态被强制下架',
        ).exists()

    def test_offline_already_offline(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        feed = Feed.objects.create(
            publisher=user, enterprise=ent,
            content='Already offline',
            status=Feed.FeedStatus.OFFLINE,
        )
        url = reverse(
            'plat_admin:content-feed-offline',
            kwargs={'pk': feed.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'reason': 'test'})
        assert response.data['code'] == 400
