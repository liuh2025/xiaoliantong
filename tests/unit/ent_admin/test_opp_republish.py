"""
ADM-009: Enterprise Opportunity Republish API unit tests.
Tests cover: republish offline opportunity, status check, permission checks.
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

_counter = itertools.count(9000)


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


def _setup_profile(user, **kwargs):
    """Update the auto-created UserProfile with given fields."""
    profile = user.ent_user_profile
    for key, value in kwargs.items():
        setattr(profile, key, value)
    profile.save()
    return profile


def _build_admin(enterprise):
    user = _build_user()
    _setup_profile(
        user,
        role_code='enterprise_admin',
        real_name='Admin User',
        enterprise_id=enterprise.id,
    )
    return user


def _build_employee_user(enterprise, **overrides):
    user = _build_user()
    profile_defaults = {
        'role_code': 'employee',
        'real_name': 'Employee User',
        'enterprise_id': enterprise.id,
    }
    profile_defaults.update(overrides)
    _setup_profile(user, **profile_defaults)
    return user


def _build_opportunity(enterprise, publisher, **overrides):
    defaults = {
        'type': Opportunity.OppType.BUY,
        'title': 'Test Opportunity',
        'enterprise': enterprise,
        'publisher': publisher,
        'industry_id': 1,
        'sub_industry_id': 101,
        'category_id': 5,
        'province_id': 110000,
        'region_id': 110100,
        'detail': 'Test detail',
        'status': Opportunity.OppStatus.OFFLINE,
    }
    defaults.update(overrides)
    opp = Opportunity(**defaults)
    opp.save()
    return opp


@pytest.mark.django_db
class TestOpportunityRepublishAPI:
    """ADM-009: Enterprise Opportunity Republish API tests."""

    def setup_method(self):
        self.client = APIClient()

    def _get_url(self, pk):
        return reverse('ent_admin:opp-republish', kwargs={'pk': pk})

    def test_republish_offline_opportunity(self):
        """Admin can republish an offline opportunity."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin, status=Opportunity.OppStatus.OFFLINE)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 200
        assert '重新发布成功' in response.data['data']['message']

        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.ACTIVE

    def test_republish_by_publisher(self):
        """Publisher (employee) can republish their own offline opportunity."""
        ent = _build_enterprise()
        _build_admin(ent)
        emp = _build_employee_user(ent)
        opp = _build_opportunity(ent, emp, status=Opportunity.OppStatus.OFFLINE)

        self.client.force_authenticate(user=emp)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 200

        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.ACTIVE

    def test_republish_active_opportunity_denied(self):
        """Cannot republish an already active opportunity."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin, status=Opportunity.OppStatus.ACTIVE)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 400
        assert '已下架' in response.data['message']

    def test_republish_other_enterprise_denied(self):
        """Cannot republish opportunity from another enterprise."""
        ent1 = _build_enterprise()
        ent2 = _build_enterprise()
        admin1 = _build_admin(ent1)
        admin2 = _build_admin(ent2)
        opp = _build_opportunity(ent2, admin2, status=Opportunity.OppStatus.OFFLINE)

        self.client.force_authenticate(user=admin1)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 403

    def test_republish_nonexistent_opportunity(self):
        """Republish non-existent opportunity returns 404."""
        ent = _build_enterprise()
        admin = _build_admin(ent)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(99999))
        assert response.data['code'] == 404

    def test_republish_non_publisher_non_admin_denied(self):
        """Non-publisher, non-admin employee cannot republish."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        emp1 = _build_employee_user(ent)
        emp2 = _build_employee_user(ent)
        opp = _build_opportunity(ent, emp1, status=Opportunity.OppStatus.OFFLINE)

        self.client.force_authenticate(user=emp2)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 403

    # ==================== Permission tests ====================

    def test_unauthenticated_denied(self):
        """Unauthenticated request returns 401."""
        response = self.client.put(self._get_url(1))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_no_enterprise_denied(self):
        """User without enterprise binding cannot republish."""
        user = _build_user()
        _setup_profile(user, role_code='guest')
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin, status=Opportunity.OppStatus.OFFLINE)

        self.client.force_authenticate(user=user)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 403
