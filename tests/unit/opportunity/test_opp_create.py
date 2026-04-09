"""
OPP-004: Opportunity Create API unit tests.
Tests cover: successful creation, auth checks, enterprise verification, validation.
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


def _create_user_with_enterprise(enterprise=None, role_code='enterprise_admin'):
    """Create user with profile bound to a verified enterprise."""
    user = _build_user()
    if enterprise is None:
        enterprise = _build_enterprise()
    # Signal auto-creates UserProfile, just update it
    profile = user.ent_user_profile
    profile.role_code = role_code
    profile.enterprise_id = enterprise.id
    profile.save(update_fields=['role_code', 'enterprise_id'])
    return user, enterprise


@pytest.mark.django_db
class TestOpportunityCreateAPI:
    """OPP-004: Opportunity Create API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.user, self.enterprise = _create_user_with_enterprise()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('opportunity:opp-list')

    def _valid_payload(self, **overrides):
        defaults = {
            'type': 'BUY',
            'title': 'Test Buy Opportunity',
            'industry_id': 1,
            'sub_industry_id': 101,
            'category_id': 5,
            'province_id': 110000,
            'region_id': 110100,
            'detail': 'Need to buy some equipment.',
            'contact_name': 'Li Si',
            'contact_phone': '13800138000',
        }
        defaults.update(overrides)
        return defaults

    # ==================== Success tests ====================

    def test_create_returns_200(self):
        response = self.client.post(
            self.url, self._valid_payload(), format='json',
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_success_response(self):
        response = self.client.post(
            self.url, self._valid_payload(), format='json',
        )
        data = response.data
        assert data['code'] == 200
        assert data['message'] == 'success'
        assert data['data']['id'] is not None
        assert data['data']['status'] == 'ACTIVE'

    def test_create_saves_to_db(self):
        self.client.post(self.url, self._valid_payload(), format='json')
        assert Opportunity.objects.count() == 1
        opp = Opportunity.objects.first()
        assert opp.type == 'BUY'
        assert opp.title == 'Test Buy Opportunity'
        assert opp.enterprise == self.enterprise
        assert opp.publisher == self.user
        assert opp.status == Opportunity.OppStatus.ACTIVE

    def test_create_with_optional_fields(self):
        payload = self._valid_payload(
            tags=['cloud', 'AI'],
            contact_wechat='wx_test',
        )
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 200
        opp = Opportunity.objects.first()
        assert opp.tags == ['cloud', 'AI']
        assert opp.contact_wechat == 'wx_test'

    def test_create_supply_type(self):
        payload = self._valid_payload(type='SUPPLY')
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 200
        opp = Opportunity.objects.first()
        assert opp.type == 'SUPPLY'

    # ==================== Auth tests ====================

    def test_auth_required(self):
        client = APIClient()
        response = client.post(
            self.url, self._valid_payload(), format='json',
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_without_enterprise_rejected(self):
        user = _build_user()
        # Signal auto-creates profile; just set role_code
        profile = user.ent_user_profile
        profile.role_code = 'guest'
        profile.save(update_fields=['role_code'])
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url, self._valid_payload(), format='json',
        )
        assert response.data['code'] == 403

    def test_user_with_unverified_enterprise_rejected(self):
        ent = _build_enterprise(auth_status=Enterprise.AuthStatus.PENDING)
        user = _build_user()
        profile = user.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.enterprise_id = ent.id
        profile.save(update_fields=['role_code', 'enterprise_id'])
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url, self._valid_payload(), format='json',
        )
        assert response.data['code'] == 403

    def test_user_without_profile_rejected(self):
        user = _build_user()
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self.url, self._valid_payload(), format='json',
        )
        assert response.data['code'] == 403

    # ==================== Validation tests ====================

    def test_missing_required_field_type(self):
        payload = self._valid_payload()
        del payload['type']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_missing_required_field_title(self):
        payload = self._valid_payload()
        del payload['title']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_missing_required_field_detail(self):
        payload = self._valid_payload()
        del payload['detail']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_missing_required_field_contact_name(self):
        payload = self._valid_payload()
        del payload['contact_name']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_missing_required_field_contact_phone(self):
        payload = self._valid_payload()
        del payload['contact_phone']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_invalid_type_value(self):
        payload = self._valid_payload(type='INVALID')
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_title_max_length(self):
        payload = self._valid_payload(title='A' * 201)
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    # ==================== Auto-assignment tests ====================

    def test_enterprise_auto_assigned(self):
        self.client.post(self.url, self._valid_payload(), format='json')
        opp = Opportunity.objects.first()
        assert opp.enterprise == self.enterprise

    def test_publisher_auto_assigned(self):
        self.client.post(self.url, self._valid_payload(), format='json')
        opp = Opportunity.objects.first()
        assert opp.publisher == self.user
