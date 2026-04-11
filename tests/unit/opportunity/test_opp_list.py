"""
OPP-002: Opportunity List API unit tests.
Tests cover: normal listing, filtering, keyword search, pagination, tags, ordering.
"""
import itertools

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise
from apps.opportunity.models import Opportunity

_counter = itertools.count(1)


def _unique_int():
    return next(_counter)


def _build_enterprise(**overrides):
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


def _build_user(**overrides):
    n = _unique_int()
    defaults = {'username': f'testuser_{n}', 'password': 'testpass123'}
    defaults.update(overrides)
    return User.objects.create_user(**defaults)


def _build_opportunity(**overrides):
    if 'enterprise' not in overrides:
        overrides['enterprise'] = _build_enterprise()
    if 'publisher' not in overrides:
        overrides['publisher'] = _build_user()
    defaults = {
        'type': Opportunity.OppType.BUY,
        'title': 'Test Opportunity',
        'industry_id': 1,
        'sub_industry_id': 101,
        'category_id': 5,
        'province_id': 110000,
        'region_id': 110100,
        'detail': 'This is a test opportunity detail.',
        'status': Opportunity.OppStatus.ACTIVE,
    }
    defaults.update(overrides)
    return Opportunity(**defaults)


def _create_opportunity(**overrides):
    opp = _build_opportunity(**overrides)
    opp.save()
    return opp


def _create_batch(count, **overrides):
    opps = []
    for i in range(count):
        defaults = {'title': f'Opportunity {i:03d}'}
        defaults.update(overrides)
        opps.append(_create_opportunity(**defaults))
    return opps


@pytest.mark.django_db
class TestOpportunityListAPI:
    """OPP-002: Opportunity List API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('opportunity:opp-list')

    # ==================== Basic tests ====================

    def test_list_returns_200(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_response_format(self):
        _create_opportunity()
        response = self.client.get(self.url)
        data = response.data
        assert data['code'] == 200
        assert data['message'] == 'success'
        assert 'data' in data
        assert 'items' in data['data']
        assert 'total' in data['data']
        assert 'page' in data['data']
        assert 'page_size' in data['data']

    def test_list_returns_active_only(self):
        _create_opportunity(status=Opportunity.OppStatus.ACTIVE)
        _create_opportunity(status=Opportunity.OppStatus.OFFLINE)
        response = self.client.get(self.url)
        assert response.data['data']['total'] == 1

    def test_list_fields(self):
        _create_opportunity(
            type=Opportunity.OppType.BUY,
            title='Buy Equipment',
            tags=['cloud', 'AI'],
        )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1
        item = items[0]
        assert 'id' in item
        assert item['type'] == 'BUY'
        assert item['title'] == 'Buy Equipment'
        assert 'enterprise_id' in item
        assert 'enterprise_name' in item
        assert 'industry_name' in item
        assert 'sub_industry_name' in item
        assert 'category_name' in item
        assert 'province_name' in item
        assert 'region_name' in item
        assert item['tags'] == ['cloud', 'AI']
        assert 'view_count' in item
        assert 'created_at' in item

    def test_empty_list(self):
        response = self.client.get(self.url)
        data = response.data['data']
        assert data['total'] == 0
        assert data['items'] == []

    # ==================== Filtering tests ====================

    def test_filter_by_type_buy(self):
        _create_opportunity(type=Opportunity.OppType.BUY)
        _create_opportunity(type=Opportunity.OppType.SUPPLY)
        response = self.client.get(self.url, {'type': 'BUY'})
        assert response.data['data']['total'] == 1

    def test_filter_by_type_supply(self):
        _create_opportunity(type=Opportunity.OppType.BUY)
        _create_opportunity(type=Opportunity.OppType.SUPPLY)
        response = self.client.get(self.url, {'type': 'SUPPLY'})
        assert response.data['data']['total'] == 1

    def test_filter_by_industry_id(self):
        _create_opportunity(industry_id=1)
        _create_opportunity(industry_id=2)
        response = self.client.get(self.url, {'industry_id': 1})
        assert response.data['data']['total'] == 1

    def test_filter_by_sub_industry_id(self):
        _create_opportunity(sub_industry_id=101)
        _create_opportunity(sub_industry_id=202)
        response = self.client.get(self.url, {'sub_industry_id': 101})
        assert response.data['data']['total'] == 1

    def test_filter_by_category_id(self):
        _create_opportunity(category_id=5)
        _create_opportunity(category_id=6)
        response = self.client.get(self.url, {'category_id': 5})
        assert response.data['data']['total'] == 1

    def test_filter_by_province_id(self):
        _create_opportunity(province_id=110000)
        _create_opportunity(province_id=310000)
        response = self.client.get(self.url, {'province_id': 110000})
        assert response.data['data']['total'] == 1

    def test_filter_by_region_id(self):
        _create_opportunity(region_id=110100)
        _create_opportunity(region_id=310100)
        response = self.client.get(self.url, {'region_id': 110100})
        assert response.data['data']['total'] == 1

    def test_multiple_filters_combined(self):
        _create_opportunity(industry_id=1, province_id=110000)
        _create_opportunity(industry_id=2, province_id=110000)
        _create_opportunity(industry_id=1, province_id=310000)
        response = self.client.get(self.url, {
            'industry_id': 1,
            'province_id': 110000,
        })
        assert response.data['data']['total'] == 1

    # ==================== Tags filter tests ====================

    def test_filter_by_single_tag(self):
        _create_opportunity(tags=['cloud', 'AI'])
        _create_opportunity(tags=['hardware', 'IoT'])
        response = self.client.get(self.url, {'tags': 'cloud'})
        assert response.data['data']['total'] == 1

    def test_filter_by_multiple_tags(self):
        _create_opportunity(tags=['AI'])
        _create_opportunity(tags=['IoT'])
        _create_opportunity(tags=['finance'])
        response = self.client.get(self.url, {'tags': 'AI,IoT'})
        assert response.data['data']['total'] == 2

    def test_filter_by_tag_no_match(self):
        _create_opportunity(tags=['cloud'])
        response = self.client.get(self.url, {'tags': 'nonexistent'})
        assert response.data['data']['total'] == 0

    # ==================== Keyword search tests ====================

    def test_keyword_search_by_title(self):
        _create_opportunity(title='Beijing Tech Equipment')
        _create_opportunity(title='Shanghai Data Solutions')
        response = self.client.get(self.url, {'keyword': 'Beijing'})
        assert response.data['data']['total'] == 1

    def test_keyword_search_by_detail(self):
        _create_opportunity(detail='Leading cloud computing provider')
        _create_opportunity(detail='Hardware manufacturing')
        response = self.client.get(self.url, {'keyword': 'cloud'})
        assert response.data['data']['total'] == 1

    def test_keyword_search_case_insensitive(self):
        _create_opportunity(title='UPPERCASE OPPORTUNITY')
        response = self.client.get(self.url, {'keyword': 'uppercase'})
        assert response.data['data']['total'] == 1

    def test_keyword_search_no_match(self):
        _create_opportunity(title='Some Opportunity')
        response = self.client.get(self.url, {'keyword': 'nonexistent'})
        assert response.data['data']['total'] == 0

    # ==================== Pagination tests ====================

    def test_default_page_size(self):
        _create_batch(25)
        response = self.client.get(self.url)
        data = response.data['data']
        assert len(data['items']) == 20
        assert data['total'] == 25
        assert data['page'] == 1
        assert data['page_size'] == 20

    def test_custom_page_size(self):
        _create_batch(10)
        response = self.client.get(self.url, {'page_size': 5})
        data = response.data['data']
        assert len(data['items']) == 5
        assert data['total'] == 10

    def test_page_2(self):
        _create_batch(25)
        response = self.client.get(self.url, {'page': 2, 'page_size': 10})
        data = response.data['data']
        assert len(data['items']) == 10
        assert data['total'] == 25
        assert data['page'] == 2

    def test_page_beyond_range(self):
        _create_batch(5)
        response = self.client.get(self.url, {'page': 999})
        data = response.data['data']
        assert data['items'] == []
        assert data['total'] == 5

    # ==================== Ordering tests ====================

    def test_default_ordering_by_created_at_desc(self):
        import time
        opp1 = _create_opportunity(title='First Created')
        time.sleep(0.01)
        opp2 = _create_opportunity(title='Second Created')
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert items[0]['title'] == 'Second Created'
        assert items[1]['title'] == 'First Created'

    # ==================== Permission tests ====================

    def test_no_auth_required(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
