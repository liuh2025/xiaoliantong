"""SCH-001~002: Global search API tests."""
import itertools

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.enterprise.models import Enterprise
from apps.opportunity.models import Opportunity
from apps.feed.models import Feed

_counter = itertools.count(500000)


def _unique_int():
    return next(_counter)


@pytest.fixture
def api_client():
    return APIClient()


def _make_enterprise(**overrides):
    n = _unique_int()
    defaults = {
        'name': f'SearchTest Ent {n}',
        'credit_code': f'55{n:014d}X',
        'legal_representative': 'Test Legal',
        'business_license': 'https://example.com/license.jpg',
        'industry_id': 1,
        'sub_industry_id': 2,
        'province_id': 110000,
        'region_id': 110100,
        'auth_status': Enterprise.AuthStatus.VERIFIED,
    }
    defaults.update(overrides)
    return Enterprise.objects.create(**defaults)


def _make_user(**overrides):
    n = _unique_int()
    defaults = {'username': f'searchuser_{n}', 'password': 'testpass123'}
    defaults.update(overrides)
    return User.objects.create_user(**defaults)


def _make_opportunity(enterprise, user, **overrides):
    n = _unique_int()
    defaults = {
        'type': Opportunity.OppType.BUY,
        'title': f'SearchTest Opp {n}',
        'enterprise': enterprise,
        'publisher': user,
        'industry_id': 1,
        'sub_industry_id': 2,
        'category_id': 3,
        'province_id': 110000,
        'region_id': 110100,
        'detail': 'Test detail',
        'status': Opportunity.OppStatus.ACTIVE,
    }
    defaults.update(overrides)
    return Opportunity.objects.create(**defaults)


def _make_feed(enterprise, user, **overrides):
    n = _unique_int()
    defaults = {
        'publisher': user,
        'enterprise': enterprise,
        'content': f'SearchTest Feed content {n}',
        'status': Feed.FeedStatus.ACTIVE,
    }
    defaults.update(overrides)
    return Feed.objects.create(**defaults)


SEARCH_URL = '/api/v1/search'


@pytest.mark.django_db
class TestSearchKeywordRequired:
    """Empty or missing keyword returns error."""

    def test_empty_keyword_returns_400(self, api_client):
        response = api_client.get(SEARCH_URL, {'keyword': ''})
        assert response.status_code == 400
        assert response.data['code'] == 400

    def test_whitespace_keyword_returns_400(self, api_client):
        response = api_client.get(SEARCH_URL, {'keyword': '   '})
        assert response.status_code == 400

    def test_missing_keyword_returns_400(self, api_client):
        response = api_client.get(SEARCH_URL)
        assert response.status_code == 400


@pytest.mark.django_db
class TestSearchAllDomains:
    """Keyword search returns results from all three domains."""

    def test_returns_three_domains(self, api_client):
        ent = _make_enterprise(name='Alpha Corp')
        user = _make_user()
        _make_opportunity(ent, user, title='Alpha Deal')
        _make_feed(ent, user, content='Alpha post')

        response = api_client.get(SEARCH_URL, {'keyword': 'Alpha'})
        assert response.status_code == 200
        data = response.data['data']
        assert 'opp' in data
        assert 'ent' in data
        assert 'feed' in data
        assert data['opp']['total'] >= 1
        assert data['ent']['total'] >= 1
        assert data['feed']['total'] >= 1

    def test_opp_items_have_expected_fields(self, api_client):
        ent = _make_enterprise(name='Beta Corp')
        user = _make_user()
        _make_opportunity(ent, user, title='Beta Deal')

        response = api_client.get(SEARCH_URL, {'keyword': 'Beta'})
        opp_items = response.data['data']['opp']['items']
        assert len(opp_items) >= 1
        item = opp_items[0]
        assert 'id' in item
        assert 'title' in item
        assert 'enterprise_name' in item

    def test_ent_items_have_expected_fields(self, api_client):
        _make_enterprise(name='Gamma Corp')

        response = api_client.get(SEARCH_URL, {'keyword': 'Gamma'})
        ent_items = response.data['data']['ent']['items']
        assert len(ent_items) >= 1
        item = ent_items[0]
        assert 'id' in item
        assert 'name' in item
        assert 'auth_status' in item

    def test_feed_items_have_expected_fields(self, api_client):
        ent = _make_enterprise(name='Delta Corp')
        user = _make_user()
        _make_feed(ent, user, content='Delta discussion')

        response = api_client.get(SEARCH_URL, {'keyword': 'Delta'})
        feed_items = response.data['data']['feed']['items']
        assert len(feed_items) >= 1
        item = feed_items[0]
        assert 'id' in item
        assert 'content' in item
        assert 'publisher_name' in item


@pytest.mark.django_db
class TestSearchTabFilter:
    """tab parameter filters to a single domain."""

    def test_tab_opp_only(self, api_client):
        ent = _make_enterprise(name='TabOpp Corp')
        user = _make_user()
        _make_opportunity(ent, user, title='TabOpp Deal')
        _make_feed(ent, user, content='TabOpp post')

        response = api_client.get(SEARCH_URL, {'keyword': 'TabOpp', 'tab': 'opp'})
        assert response.status_code == 200
        data = response.data['data']
        assert 'opp' in data
        assert 'ent' not in data
        assert 'feed' not in data
        assert data['opp']['total'] >= 1

    def test_tab_ent_only(self, api_client):
        _make_enterprise(name='TabEnt Corp')

        response = api_client.get(SEARCH_URL, {'keyword': 'TabEnt', 'tab': 'ent'})
        assert response.status_code == 200
        data = response.data['data']
        assert 'ent' in data
        assert 'opp' not in data
        assert 'feed' not in data
        assert data['ent']['total'] >= 1

    def test_tab_feed_only(self, api_client):
        ent = _make_enterprise(name='TabFeed Corp')
        user = _make_user()
        _make_feed(ent, user, content='TabFeed post')

        response = api_client.get(SEARCH_URL, {'keyword': 'TabFeed', 'tab': 'feed'})
        assert response.status_code == 200
        data = response.data['data']
        assert 'feed' in data
        assert 'opp' not in data
        assert 'ent' not in data
        assert data['feed']['total'] >= 1

    def test_invalid_tab_returns_400(self, api_client):
        response = api_client.get(SEARCH_URL, {'keyword': 'test', 'tab': 'invalid'})
        assert response.status_code == 400


@pytest.mark.django_db
class TestSearchNoResults:
    """No matching results returns empty lists."""

    def test_no_match_returns_empty(self, api_client):
        response = api_client.get(SEARCH_URL, {'keyword': 'ZZZ_NO_MATCH_ZZZ'})
        assert response.status_code == 200
        data = response.data['data']
        assert data['opp']['total'] == 0
        assert data['opp']['items'] == []
        assert data['ent']['total'] == 0
        assert data['ent']['items'] == []
        assert data['feed']['total'] == 0
        assert data['feed']['items'] == []


@pytest.mark.django_db
class TestSearchStatusFilter:
    """Only ACTIVE opportunities/feeds and VERIFIED enterprises are returned."""

    def test_inactive_opportunity_excluded(self, api_client):
        ent = _make_enterprise(name='StatusOpp Corp')
        user = _make_user()
        _make_opportunity(
            ent, user, title='StatusOpp Deal',
            status=Opportunity.OppStatus.OFFLINE,
        )

        response = api_client.get(SEARCH_URL, {'keyword': 'StatusOpp'})
        assert response.data['data']['opp']['total'] == 0

    def test_unverified_enterprise_excluded(self, api_client):
        _make_enterprise(
            name='Unverified Corp',
            auth_status=Enterprise.AuthStatus.UNCLAIMED,
        )

        response = api_client.get(SEARCH_URL, {'keyword': 'Unverified'})
        assert response.data['data']['ent']['total'] == 0

    def test_pending_enterprise_excluded(self, api_client):
        _make_enterprise(
            name='Pending Corp',
            auth_status=Enterprise.AuthStatus.PENDING,
        )

        response = api_client.get(SEARCH_URL, {'keyword': 'Pending'})
        assert response.data['data']['ent']['total'] == 0

    def test_rejected_enterprise_excluded(self, api_client):
        _make_enterprise(
            name='Rejected Corp',
            auth_status=Enterprise.AuthStatus.REJECTED,
        )

        response = api_client.get(SEARCH_URL, {'keyword': 'Rejected'})
        assert response.data['data']['ent']['total'] == 0

    def test_offline_feed_excluded(self, api_client):
        ent = _make_enterprise(name='StatusFeed Corp')
        user = _make_user()
        _make_feed(
            ent, user, content='StatusFeed offline post',
            status=Feed.FeedStatus.OFFLINE,
        )

        response = api_client.get(SEARCH_URL, {'keyword': 'StatusFeed'})
        assert response.data['data']['feed']['total'] == 0

    def test_active_opportunity_included(self, api_client):
        ent = _make_enterprise(name='ActiveOpp Corp')
        user = _make_user()
        _make_opportunity(
            ent, user, title='ActiveOpp Deal',
            status=Opportunity.OppStatus.ACTIVE,
        )

        response = api_client.get(SEARCH_URL, {'keyword': 'ActiveOpp'})
        assert response.data['data']['opp']['total'] >= 1

    def test_verified_enterprise_included(self, api_client):
        _make_enterprise(
            name='Verified Corp',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )

        response = api_client.get(SEARCH_URL, {'keyword': 'Verified'})
        assert response.data['data']['ent']['total'] >= 1

    def test_active_feed_included(self, api_client):
        ent = _make_enterprise(name='ActiveFeed Corp')
        user = _make_user()
        _make_feed(
            ent, user, content='ActiveFeed active post',
            status=Feed.FeedStatus.ACTIVE,
        )

        response = api_client.get(SEARCH_URL, {'keyword': 'ActiveFeed'})
        assert response.data['data']['feed']['total'] >= 1


@pytest.mark.django_db
class TestSearchPagination:
    """Pagination works correctly with page and page_size parameters."""

    def test_default_page_size_20(self, api_client):
        ent = _make_enterprise(name='PageTest Corp')
        user = _make_user()
        for i in range(25):
            _make_opportunity(ent, user, title=f'PageTest Deal {i}')

        response = api_client.get(SEARCH_URL, {'keyword': 'PageTest'})
        opp = response.data['data']['opp']
        assert len(opp['items']) == 20
        assert opp['total'] == 25

    def test_page_2_returns_next_batch(self, api_client):
        ent = _make_enterprise(name='PageTwo Corp')
        user = _make_user()
        for i in range(25):
            _make_opportunity(ent, user, title=f'PageTwo Deal {i}')

        response = api_client.get(SEARCH_URL, {'keyword': 'PageTwo', 'page': 2})
        opp = response.data['data']['opp']
        assert len(opp['items']) == 5
        assert opp['total'] == 25

    def test_custom_page_size(self, api_client):
        ent = _make_enterprise(name='PageSize Corp')
        user = _make_user()
        for i in range(15):
            _make_opportunity(ent, user, title=f'PageSize Deal {i}')

        response = api_client.get(
            SEARCH_URL, {'keyword': 'PageSize', 'page_size': 10},
        )
        opp = response.data['data']['opp']
        assert len(opp['items']) == 10
        assert opp['total'] == 15

    def test_page_size_capped_at_20(self, api_client):
        ent = _make_enterprise(name='PageCap Corp')
        user = _make_user()
        for i in range(30):
            _make_opportunity(ent, user, title=f'PageCap Deal {i}')

        response = api_client.get(
            SEARCH_URL, {'keyword': 'PageCap', 'page_size': 50},
        )
        opp = response.data['data']['opp']
        assert len(opp['items']) == 20

    def test_page_beyond_results_returns_empty(self, api_client):
        ent = _make_enterprise(name='PageBeyond Corp')
        user = _make_user()
        _make_opportunity(ent, user, title='PageBeyond Deal')

        response = api_client.get(
            SEARCH_URL, {'keyword': 'PageBeyond', 'page': 99},
        )
        opp = response.data['data']['opp']
        assert opp['total'] >= 1
        assert opp['items'] == []


@pytest.mark.django_db
class TestSearchRelevance:
    """Exact matches sort before partial matches."""

    def test_exact_match_first_in_opportunities(self, api_client):
        ent = _make_enterprise(name='RelevOpp Corp')
        user = _make_user()
        _make_opportunity(ent, user, title='RelevOpp partial match alpha')
        _make_opportunity(ent, user, title='ExactTitle')
        _make_opportunity(ent, user, title='Contains ExactTitle suffix')

        response = api_client.get(SEARCH_URL, {'keyword': 'ExactTitle'})
        items = response.data['data']['opp']['items']
        assert items[0]['title'] == 'ExactTitle'

    def test_exact_match_first_in_enterprises(self, api_client):
        _make_enterprise(name='ExactEntName')
        _make_enterprise(name='Prefix ExactEntName Corp')

        response = api_client.get(SEARCH_URL, {'keyword': 'ExactEntName'})
        items = response.data['data']['ent']['items']
        assert items[0]['name'] == 'ExactEntName'

    def test_exact_match_first_in_feeds(self, api_client):
        ent = _make_enterprise(name='RelevFeed Corp')
        user = _make_user()
        _make_feed(ent, user, content='ExactFeedContent')
        _make_feed(ent, user, content='Some text with ExactFeedContent inside')

        response = api_client.get(SEARCH_URL, {'keyword': 'ExactFeedContent'})
        items = response.data['data']['feed']['items']
        assert items[0]['content'] == 'ExactFeedContent'


@pytest.mark.django_db
class TestSearchPublicAccess:
    """Search API is accessible without authentication."""

    def test_unauthenticated_access_allowed(self, api_client):
        response = api_client.get(SEARCH_URL, {'keyword': 'test'})
        assert response.status_code == 200
