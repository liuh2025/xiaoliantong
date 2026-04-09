"""
OPP-005: Opportunity Update API unit tests.
Tests cover: successful update, permission checks, type immutability.
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
    }
    defaults.update(overrides)
    opp = Opportunity(**defaults)
    opp.save()
    return opp


@pytest.mark.django_db
class TestOpportunityUpdateAPI:
    """OPP-005: Opportunity Update API tests."""

    def setup_method(self):
        self.client = APIClient()

    def _url(self, pk):
        return reverse('opportunity:opp-detail', kwargs={'pk': pk})

    # ==================== Success tests ====================

    def test_publisher_can_update(self):
        publisher = _build_user()
        opp = _create_opportunity(publisher=publisher)
        self.client.force_authenticate(user=publisher)
        response = self.client.put(
            self._url(opp.id),
            {'title': 'Updated Title'},
            format='json',
        )
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.title == 'Updated Title'

    def test_update_response_format(self):
        publisher = _build_user()
        opp = _create_opportunity(publisher=publisher)
        self.client.force_authenticate(user=publisher)
        response = self.client.put(
            self._url(opp.id),
            {'title': 'Updated Title'},
            format='json',
        )
        data = response.data
        assert data['code'] == 200
        assert data['data']['id'] == opp.id
        assert data['data']['status'] == opp.status

    def test_enterprise_admin_can_update(self):
        ent = _build_enterprise()
        publisher = _build_user()
        opp = _create_opportunity(enterprise=ent, publisher=publisher)
        admin = _build_user()
        profile = admin.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.enterprise_id = ent.id
        profile.save(update_fields=['role_code', 'enterprise_id'])
        self.client.force_authenticate(user=admin)
        response = self.client.put(
            self._url(opp.id),
            {'title': 'Admin Updated'},
            format='json',
        )
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.title == 'Admin Updated'

    def test_update_multiple_fields(self):
        publisher = _build_user()
        opp = _create_opportunity(publisher=publisher)
        self.client.force_authenticate(user=publisher)
        response = self.client.put(
            self._url(opp.id),
            {
                'title': 'Updated Title',
                'detail': 'Updated detail',
                'tags': ['new_tag'],
            },
            format='json',
        )
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.title == 'Updated Title'
        assert opp.detail == 'Updated detail'
        assert opp.tags == ['new_tag']

    # ==================== Type immutability ====================

    def test_type_ignored_on_update(self):
        publisher = _build_user()
        opp = _create_opportunity(
            publisher=publisher, type=Opportunity.OppType.BUY,
        )
        self.client.force_authenticate(user=publisher)
        self.client.put(
            self._url(opp.id),
            {'type': 'SUPPLY', 'title': 'Updated'},
            format='json',
        )
        opp.refresh_from_db()
        assert opp.type == Opportunity.OppType.BUY

    # ==================== Permission tests ====================

    def test_non_publisher_non_admin_cannot_update(self):
        publisher = _build_user()
        opp = _create_opportunity(publisher=publisher)
        other_user = _build_user()
        self.client.force_authenticate(user=other_user)
        response = self.client.put(
            self._url(opp.id),
            {'title': 'Hacked'},
            format='json',
        )
        assert response.data['code'] == 403

    def test_auth_required(self):
        opp = _create_opportunity()
        client = APIClient()
        response = client.put(
            self._url(opp.id),
            {'title': 'Updated'},
            format='json',
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== Not found ====================

    def test_update_not_found(self):
        user = _build_user()
        self.client.force_authenticate(user=user)
        response = self.client.put(
            self._url(99999),
            {'title': 'Updated'},
            format='json',
        )
        assert response.data['code'] == 404

    # ==================== Validation ====================

    def test_invalid_title_too_long(self):
        publisher = _build_user()
        opp = _create_opportunity(publisher=publisher)
        self.client.force_authenticate(user=publisher)
        response = self.client.put(
            self._url(opp.id),
            {'title': 'A' * 201},
            format='json',
        )
        assert response.data['code'] == 400
