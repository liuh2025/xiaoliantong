"""
ADM-006: Employee Unbind API unit tests.
Tests cover: normal unbind, re-enable disabled user, user not in enterprise, permission checks.
"""
import itertools

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile

_counter = itertools.count(6000)


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


def _build_employee(enterprise, **overrides):
    user = _build_user()
    profile_defaults = {
        'role_code': 'employee',
        'real_name': 'Employee User',
        'enterprise_id': enterprise.id,
    }
    profile_defaults.update(overrides)
    _setup_profile(user, **profile_defaults)
    return user


@pytest.mark.django_db
class TestEmployeeUnbindAPI:
    """ADM-006: Employee Unbind API tests."""

    def setup_method(self):
        self.client = APIClient()

    def _get_url(self, pk):
        return reverse('ent_admin:employee-unbind', kwargs={'pk': pk})

    def test_unbind_employee_success(self):
        """Admin can unbind employee from enterprise."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        emp = _build_employee(enterprise)

        self.client.force_authenticate(user=admin)
        response = self.client.post(self._get_url(emp.id))
        assert response.data['code'] == 200
        assert '解绑成功' in response.data['data']['message']

        emp.ent_user_profile.refresh_from_db()
        assert emp.ent_user_profile.enterprise_id is None
        assert emp.ent_user_profile.role_code == 'guest'

    def test_unbind_re_enables_disabled_user(self):
        """Unbinding a disabled user re-enables them."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        emp = _build_employee(enterprise)
        emp.is_active = False
        emp.save()

        self.client.force_authenticate(user=admin)
        response = self.client.post(self._get_url(emp.id))
        assert response.data['code'] == 200

        emp.refresh_from_db()
        assert emp.is_active is True

    def test_unbind_nonexistent_user(self):
        """Unbind non-existent user returns 404."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)

        self.client.force_authenticate(user=admin)
        response = self.client.post(self._get_url(99999))
        assert response.data['code'] == 404

    def test_unbind_user_not_in_enterprise(self):
        """Cannot unbind user from another enterprise."""
        ent1 = _build_enterprise()
        ent2 = _build_enterprise()
        admin = _build_admin(ent1)
        other_emp = _build_employee(ent2)

        self.client.force_authenticate(user=admin)
        response = self.client.post(self._get_url(other_emp.id))
        assert response.data['code'] == 403

    def test_unbind_user_no_enterprise_binding(self):
        """Unbind user with default profile (no enterprise) returns 403."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        user_no_enterprise = _build_user()
        # Profile is auto-created but has no enterprise_id

        self.client.force_authenticate(user=admin)
        response = self.client.post(self._get_url(user_no_enterprise.id))
        assert response.data['code'] == 403

    def test_unbind_active_user_stays_active(self):
        """Unbinding an active user keeps them active."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        emp = _build_employee(enterprise)

        self.client.force_authenticate(user=admin)
        self.client.post(self._get_url(emp.id))

        emp.refresh_from_db()
        assert emp.is_active is True

    # ==================== Permission tests ====================

    def test_unauthenticated_denied(self):
        """Unauthenticated request returns 401."""
        response = self.client.post(self._get_url(1))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_denied(self):
        """Employee cannot unbind users."""
        enterprise = _build_enterprise()
        _build_admin(enterprise)
        emp = _build_employee(enterprise)

        self.client.force_authenticate(user=emp)
        response = self.client.post(self._get_url(emp.id))
        assert response.data['code'] == 403
