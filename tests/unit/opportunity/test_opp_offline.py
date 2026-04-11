"""
OPP-007: Opportunity Offline/Republish API unit tests.
Tests cover: toggle ACTIVE->OFFLINE, OFFLINE->ACTIVE, permission checks.
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
class TestOpportunityOfflineAPI:
    """OPP-007: Opportunity Offline/Republish API tests."""

    def setup_method(self):
        self.client = APIClient()

    def _url(self, pk):
        return reverse('opportunity:opp-offline', kwargs={'pk': pk})

    # ==================== Toggle ACTIVE -> OFFLINE ====================

    def test_publisher_can_offline(self):
        publisher = _build_user()
        opp = _create_opportunity(
            publisher=publisher, status=Opportunity.OppStatus.ACTIVE,
        )
        self.client.force_authenticate(user=publisher)
        response = self.client.put(self._url(opp.id))
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.OFFLINE

    def test_offline_response_format(self):
        publisher = _build_user()
        opp = _create_opportunity(
            publisher=publisher, status=Opportunity.OppStatus.ACTIVE,
        )
        self.client.force_authenticate(user=publisher)
        response = self.client.put(self._url(opp.id))
        data = response.data
        assert data['code'] == 200
        assert data['data']['id'] == opp.id
        assert data['data']['status'] == 'OFFLINE'

    def test_enterprise_admin_can_offline(self):
        ent = _build_enterprise()
        publisher = _build_user()
        opp = _create_opportunity(
            enterprise=ent, publisher=publisher,
            status=Opportunity.OppStatus.ACTIVE,
        )
        admin = _build_user()
        profile = admin.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.enterprise_id = ent.id
        profile.save(update_fields=['role_code', 'enterprise_id'])
        self.client.force_authenticate(user=admin)
        response = self.client.put(self._url(opp.id))
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.OFFLINE

    # ==================== Toggle OFFLINE -> ACTIVE ====================

    def test_publisher_can_republish(self):
        publisher = _build_user()
        opp = _create_opportunity(
            publisher=publisher, status=Opportunity.OppStatus.OFFLINE,
        )
        self.client.force_authenticate(user=publisher)
        response = self.client.put(self._url(opp.id))
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.ACTIVE

    def test_enterprise_admin_can_republish(self):
        ent = _build_enterprise()
        publisher = _build_user()
        opp = _create_opportunity(
            enterprise=ent, publisher=publisher,
            status=Opportunity.OppStatus.OFFLINE,
        )
        admin = _build_user()
        profile = admin.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.enterprise_id = ent.id
        profile.save(update_fields=['role_code', 'enterprise_id'])
        self.client.force_authenticate(user=admin)
        response = self.client.put(self._url(opp.id))
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.ACTIVE

    # ==================== Permission tests ====================

    def test_non_publisher_non_admin_cannot_toggle(self):
        publisher = _build_user()
        opp = _create_opportunity(publisher=publisher)
        other_user = _build_user()
        self.client.force_authenticate(user=other_user)
        response = self.client.put(self._url(opp.id))
        assert response.data['code'] == 403

    def test_auth_required(self):
        opp = _create_opportunity()
        client = APIClient()
        response = client.put(self._url(opp.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== Not found ====================

    def test_offline_not_found(self):
        user = _build_user()
        self.client.force_authenticate(user=user)
        response = self.client.put(self._url(99999))
        assert response.data['code'] == 404

    # ==================== Double toggle ====================

    def test_double_toggle_returns_to_original(self):
        publisher = _build_user()
        opp = _create_opportunity(
            publisher=publisher, status=Opportunity.OppStatus.ACTIVE,
        )
        self.client.force_authenticate(user=publisher)
        # First toggle: ACTIVE -> OFFLINE
        self.client.put(self._url(opp.id))
        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.OFFLINE
        # Second toggle: OFFLINE -> ACTIVE
        self.client.put(self._url(opp.id))
        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.ACTIVE
