"""
ADM-010: Enterprise Opportunity Offline API unit tests.
Tests cover: offline active opportunity, status check, admin-only permission.
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

_counter = itertools.count(10000)


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
        'status': Opportunity.OppStatus.ACTIVE,
    }
    defaults.update(overrides)
    opp = Opportunity(**defaults)
    opp.save()
    return opp


@pytest.mark.django_db
class TestOpportunityOfflineAPI:
    """ADM-010: Enterprise Opportunity Offline API tests."""

    def setup_method(self):
        self.client = APIClient()

    def _get_url(self, pk):
        return reverse('ent_admin:opp-offline', kwargs={'pk': pk})

    def test_offline_active_opportunity(self):
        """Admin can offline an active opportunity."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin, status=Opportunity.OppStatus.ACTIVE)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 200
        assert '下架成功' in response.data['data']['message']

        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.OFFLINE

    def test_offline_already_offline_denied(self):
        """Cannot offline an already offline opportunity."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin, status=Opportunity.OppStatus.OFFLINE)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 400
        assert '在线' in response.data['message']

    def test_offline_other_enterprise_denied(self):
        """Cannot offline opportunity from another enterprise."""
        ent1 = _build_enterprise()
        ent2 = _build_enterprise()
        admin1 = _build_admin(ent1)
        admin2 = _build_admin(ent2)
        opp = _build_opportunity(ent2, admin2, status=Opportunity.OppStatus.ACTIVE)

        self.client.force_authenticate(user=admin1)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 403

    def test_offline_nonexistent_opportunity(self):
        """Offline non-existent opportunity returns 404."""
        ent = _build_enterprise()
        admin = _build_admin(ent)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(99999))
        assert response.data['code'] == 404

    def test_employee_cannot_offline(self):
        """Employee (non-admin) cannot offline opportunities."""
        ent = _build_enterprise()
        _build_admin(ent)
        emp = _build_employee_user(ent)
        opp = _build_opportunity(ent, emp, status=Opportunity.OppStatus.ACTIVE)

        self.client.force_authenticate(user=emp)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 403

    def test_employee_publisher_cannot_offline(self):
        """Even publisher (if employee, not admin) cannot offline."""
        ent = _build_enterprise()
        _build_admin(ent)
        emp = _build_employee_user(ent)
        opp = _build_opportunity(ent, emp, status=Opportunity.OppStatus.ACTIVE)

        self.client.force_authenticate(user=emp)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 403
        assert '企业管理员' in response.data['message']

    # ==================== Permission tests ====================

    def test_unauthenticated_denied(self):
        """Unauthenticated request returns 401."""
        response = self.client.put(self._get_url(1))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_no_enterprise_denied(self):
        """User without enterprise binding cannot offline."""
        user = _build_user()
        _setup_profile(user, role_code='guest')
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin, status=Opportunity.OppStatus.ACTIVE)

        self.client.force_authenticate(user=user)
        response = self.client.put(self._get_url(opp.id))
        assert response.data['code'] == 403
