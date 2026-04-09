"""
OPP-003: Opportunity Detail API unit tests.
Tests cover: normal detail, view_count increment, phone masking, auth-gated contact fields.
"""
import itertools

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile
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


def _create_user_with_profile(**overrides):
    user = _build_user(**overrides)
    # Signal auto-creates UserProfile, just update it
    profile = user.ent_user_profile
    profile.role_code = 'enterprise_admin'
    profile.save(update_fields=['role_code'])
    return user


def _create_opportunity(**overrides):
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
        'contact_name': 'Li Si',
        'contact_phone': '13800138000',
        'contact_wechat': 'test_wechat',
    }
    defaults.update(overrides)
    opp = Opportunity(**defaults)
    opp.save()
    return opp


@pytest.mark.django_db
class TestOpportunityDetailAPI:
    """OPP-003: Opportunity Detail API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.user = _create_user_with_profile()
        self.client.force_authenticate(user=self.user)

    def _url(self, pk):
        return reverse('opportunity:opp-detail', kwargs={'pk': pk})

    # ==================== Basic detail tests ====================

    def test_detail_returns_200(self):
        opp = _create_opportunity()
        response = self.client.get(self._url(opp.id))
        assert response.status_code == status.HTTP_200_OK

    def test_detail_response_format(self):
        opp = _create_opportunity()
        response = self.client.get(self._url(opp.id))
        data = response.data
        assert data['code'] == 200
        assert data['message'] == 'success'
        assert 'data' in data

    def test_detail_fields(self):
        opp = _create_opportunity(
            type=Opportunity.OppType.BUY,
            title='Buy Equipment',
            detail='Need equipment',
            contact_name='Wang Wu',
            contact_phone='13812345678',
            contact_wechat='wx_test',
        )
        response = self.client.get(self._url(opp.id))
        item = response.data['data']
        assert item['id'] == opp.id
        assert item['type'] == 'BUY'
        assert item['title'] == 'Buy Equipment'
        assert item['detail'] == 'Need equipment'
        assert item['enterprise_id'] == opp.enterprise_id
        assert item['enterprise_name'] == opp.enterprise.name
        assert item['publisher_id'] == opp.publisher_id
        assert 'industry_id' in item
        assert 'sub_industry_id' in item
        assert 'category_id' in item
        assert 'province_id' in item
        assert 'region_id' in item
        assert 'tags' in item
        assert item['status'] == 'ACTIVE'
        assert 'view_count' in item
        assert 'contact_name' in item
        assert 'contact_phone' in item
        assert 'contact_wechat' in item
        assert 'created_at' in item
        assert 'updated_at' in item

    def test_detail_not_found(self):
        response = self.client.get(self._url(99999))
        data = response.data
        assert data['code'] == 404
        assert '不存在' in data['message']

    # ==================== View count tests ====================

    def test_view_count_increments(self):
        opp = _create_opportunity(view_count=0)
        self.client.get(self._url(opp.id))
        opp.refresh_from_db()
        assert opp.view_count == 1

    def test_view_count_increments_multiple(self):
        opp = _create_opportunity(view_count=0)
        self.client.get(self._url(opp.id))
        self.client.get(self._url(opp.id))
        self.client.get(self._url(opp.id))
        opp.refresh_from_db()
        assert opp.view_count == 3

    def test_view_count_returned_in_response(self):
        opp = _create_opportunity(view_count=0)
        response = self.client.get(self._url(opp.id))
        assert response.data['data']['view_count'] == 1

    # ==================== Phone masking tests ====================

    def test_contact_phone_masked(self):
        opp = _create_opportunity(contact_phone='13800138000')
        response = self.client.get(self._url(opp.id))
        assert response.data['data']['contact_phone'] == '138****8000'

    def test_contact_phone_short_not_masked(self):
        opp = _create_opportunity(contact_phone='1234567')
        response = self.client.get(self._url(opp.id))
        assert response.data['data']['contact_phone'] == '1234567'

    def test_contact_phone_empty(self):
        opp = _create_opportunity(contact_phone='')
        response = self.client.get(self._url(opp.id))
        assert response.data['data']['contact_phone'] is None

    # ==================== Auth-gated contact fields ====================

    def test_contact_fields_visible_to_authenticated_user(self):
        opp = _create_opportunity(
            contact_name='Test Contact',
            contact_phone='13800138000',
            contact_wechat='test_wx',
        )
        response = self.client.get(self._url(opp.id))
        data = response.data['data']
        assert data['contact_name'] == 'Test Contact'
        assert data['contact_phone'] == '138****8000'
        assert data['contact_wechat'] == 'test_wx'

    def test_contact_fields_null_for_unauthenticated_user(self):
        opp = _create_opportunity(
            contact_name='Test Contact',
            contact_phone='13800138000',
            contact_wechat='test_wx',
        )
        client = APIClient()  # unauthenticated client
        response = client.get(self._url(opp.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== Auth required ====================

    def test_auth_required(self):
        client = APIClient()
        opp = _create_opportunity()
        response = client.get(self._url(opp.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== Publisher name ====================

    def test_publisher_name_returns_username(self):
        publisher = _build_user(username='publisher1')
        opp = _create_opportunity(publisher=publisher)
        response = self.client.get(self._url(opp.id))
        assert response.data['data']['publisher_name'] == 'publisher1'
