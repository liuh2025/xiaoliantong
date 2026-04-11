"""
L1 API Integration Tests - Opportunity & Feed Modules (OPP / FEED)

Tests all endpoints under:
- /api/v1/opp/  (Opportunity: list, recommended, detail, contact, create, offline)
- /api/v1/feed/ (Feed: list, newest)

TC-ID ranges:
  Opportunity: TC-API-opp-001 ~ TC-API-opp-006
  Feed:        TC-API-feed-001 ~ TC-API-feed-002
"""
import pytest
from apps.enterprise.models import Enterprise
from apps.opportunity.models import Opportunity, ContactLog
from apps.feed.models import Feed
from apps.auth_app.models import UserProfile


# ============================================================
# Helper: ensure ent_admin_user profile has enterprise_id set
# ============================================================


@pytest.fixture
def ent_admin_with_profile(ent_admin_user):
    """Ent admin user whose profile is bound to the verified enterprise."""
    user, ent = ent_admin_user
    # conftest already sets enterprise_id and role_code
    return user, ent


@pytest.fixture
def ent_admin_client_bound(ent_admin_with_profile):
    """Authenticated client for ent admin with bound enterprise profile."""
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=ent_admin_with_profile[0])
    return client


# ============================================================
# Opportunity API Tests
# ============================================================


@pytest.mark.django_db
class TestOpportunityAPI:
    """Opportunity module L1 API integration tests."""

    # TC-API-opp-001: List opportunities (public)
    def test_list_opportunities(self, anon_client, sample_opportunity):
        """TC-API-opp-001: GET /api/v1/opp/opportunity returns paginated list."""
        url = '/api/v1/opp/opportunity'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'items' in data['data']
        assert 'total' in data['data']
        assert data['data']['total'] >= 1
        assert len(data['data']['items']) >= 1

    # TC-API-opp-002: Recommended opportunities (public)
    def test_recommended_opportunities(self, anon_client, sample_opportunity):
        """TC-API-opp-002: GET /api/v1/opp/opportunity/recommended returns up to 4."""
        url = '/api/v1/opp/opportunity/recommended'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'items' in data['data']
        assert len(data['data']['items']) <= 4

    # TC-API-opp-003: Opportunity detail (authenticated)
    def test_opportunity_detail(self, auth_client, sample_opportunity):
        """TC-API-opp-003: GET /api/v1/opp/opportunity/<id> returns detail."""
        url = f'/api/v1/opp/opportunity/{sample_opportunity.id}'
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] is not None
        assert data['data']['id'] == sample_opportunity.id
        assert data['data']['title'] == sample_opportunity.title

    # TC-API-opp-004: Get contact info for an opportunity
    def test_opportunity_contact(self, ent_admin_client_bound, ent_admin_with_profile,
                                 sample_opportunity):
        """TC-API-opp-004: POST /api/v1/opp/opportunity/<id>/contact returns contact."""
        user, ent = ent_admin_with_profile

        url = f'/api/v1/opp/opportunity/{sample_opportunity.id}/contact'
        response = ent_admin_client_bound.post(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'contact_name' in data['data']
        assert 'contact_phone' in data['data']
        # Verify ContactLog was created
        assert ContactLog.objects.filter(
            opportunity=sample_opportunity,
            getter_user=user,
        ).exists()

    # TC-API-opp-005: Create an opportunity
    def test_create_opportunity(self, ent_admin_client_bound, ent_admin_with_profile):
        """TC-API-opp-005: POST /api/v1/opp/opportunity creates opportunity."""
        user, ent = ent_admin_with_profile

        payload = {
            'type': 'BUY',
            'title': '新创建的测试商机',
            'industry_id': 1,
            'sub_industry_id': 101,
            'category_id': 1,
            'province_id': 110000,
            'region_id': 110100,
            'detail': '这是一个通过API创建的测试商机，描述至少需要20个字符以上。',
            'tags': ['测试'],
            'contact_name': '张经理',
            'contact_phone': '13900139000',
        }
        url = '/api/v1/opp/opportunity'
        response = ent_admin_client_bound.post(url, payload, format='json')

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['id'] is not None
        assert data['data']['status'] == 'ACTIVE'

        # Verify the opportunity was actually created in the database
        assert Opportunity.objects.filter(
            title='新创建的测试商机',
            publisher=user,
        ).exists()

    # TC-API-opp-006: Take an opportunity offline
    def test_opportunity_offline(self, ent_admin_client_bound, ent_admin_with_profile,
                                 sample_opportunity):
        """TC-API-opp-006: PUT /api/v1/opp/opportunity/<id>/offline toggles status."""
        assert sample_opportunity.status == 'ACTIVE'

        url = f'/api/v1/opp/opportunity/{sample_opportunity.id}/offline'
        response = ent_admin_client_bound.put(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['status'] == 'OFFLINE'

        # Refresh from DB and verify
        sample_opportunity.refresh_from_db()
        assert sample_opportunity.status == 'OFFLINE'


# ============================================================
# Feed API Tests
# ============================================================


@pytest.mark.django_db
class TestFeedAPI:
    """Feed module L1 API integration tests."""

    # TC-API-feed-001: List feeds (public)
    def test_list_feeds(self, anon_client, ent_admin_with_profile):
        """TC-API-feed-001: GET /api/v1/feed/feed returns paginated list."""
        user, ent = ent_admin_with_profile

        # Create sample feed
        Feed.objects.create(
            publisher=user,
            enterprise=ent,
            content='这是一条测试校友圈动态内容，用于测试列表接口。',
            status='ACTIVE',
        )

        url = '/api/v1/feed/feed'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'items' in data['data']
        assert 'total' in data['data']
        assert data['data']['total'] >= 1
        assert len(data['data']['items']) >= 1

    # TC-API-feed-002: Newest feeds (public)
    def test_newest_feeds(self, anon_client, ent_admin_with_profile):
        """TC-API-feed-002: GET /api/v1/feed/feed/newest returns top 2."""
        user, ent = ent_admin_with_profile

        # Enterprise must be VERIFIED (uppercase) for newest to include it
        ent.auth_status = Enterprise.AuthStatus.VERIFIED
        ent.save()

        # Create sample feeds
        Feed.objects.create(
            publisher=user,
            enterprise=ent,
            content='最新动态第一条，用于测试newest接口。',
            status='ACTIVE',
        )
        Feed.objects.create(
            publisher=user,
            enterprise=ent,
            content='最新动态第二条，用于测试newest接口。',
            status='ACTIVE',
        )

        url = '/api/v1/feed/feed/newest'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'items' in data['data']
        assert len(data['data']['items']) <= 2
        if data['data']['items']:
            assert 'id' in data['data']['items'][0]
            assert 'content' in data['data']['items'][0]
