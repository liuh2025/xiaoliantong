"""
ADM-002: Employee Create (Bind) API unit tests.
Tests cover: normal bind, user not registered, user already bound, permission checks.
"""
import itertools

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile

_counter = itertools.count(2000)


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
    defaults = {'username': f'1{n:010d}', 'password': 'testpass123'}
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


@pytest.mark.django_db
class TestEmployeeCreateAPI:
    """ADM-002: Employee Create (Bind) API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('ent_admin:employee-list')

    def test_bind_registered_user_success(self):
        """Bind a registered user to enterprise."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        target = _build_user()
        # Profile is auto-created by signal; set as guest
        _setup_profile(target, role_code='guest')

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.url, {
            'phone': target.username,
            'real_name': 'New Employee',
            'role_code': 'employee',
        })
        assert response.data['code'] == 200
        assert response.data['data']['id'] == target.id

        target_profile = target.ent_user_profile
        target_profile.refresh_from_db()
        assert target_profile.enterprise_id == enterprise.id
        assert target_profile.role_code == 'employee'
        assert target_profile.real_name == 'New Employee'

    def test_bind_with_position(self):
        """Bind user with position specified."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        target = _build_user()
        _setup_profile(target, role_code='guest')

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.url, {
            'phone': target.username,
            'real_name': 'Eng',
            'position': 'Senior Engineer',
            'role_code': 'employee',
        })
        assert response.data['code'] == 200
        target.ent_user_profile.refresh_from_db()
        assert target.ent_user_profile.position == 'Senior Engineer'

    def test_bind_user_not_registered(self):
        """Cannot bind user that is not registered."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.url, {
            'phone': '99999999999',
            'real_name': 'No One',
            'role_code': 'employee',
        })
        assert response.data['code'] == 400
        assert '未注册' in response.data['message']

    def test_bind_user_already_bound_other_enterprise(self):
        """Cannot bind user already bound to another enterprise."""
        ent1 = _build_enterprise()
        ent2 = _build_enterprise()
        admin = _build_admin(ent1)
        target = _build_user()
        _setup_profile(
            target, role_code='employee',
            enterprise_id=ent2.id,
        )

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.url, {
            'phone': target.username,
            'real_name': 'Bound',
            'role_code': 'employee',
        })
        assert response.data['code'] == 400
        assert '已绑定其他企业' in response.data['message']

    def test_bind_user_with_default_profile(self):
        """User with auto-created default profile can be bound."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        target = _build_user()
        # Profile is auto-created by signal with defaults (guest, no enterprise)

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.url, {
            'phone': target.username,
            'real_name': 'Default Profile',
            'role_code': 'employee',
        })
        assert response.data['code'] == 200
        target.ent_user_profile.refresh_from_db()
        assert target.ent_user_profile.enterprise_id == enterprise.id

    def test_bind_user_already_in_same_enterprise(self):
        """User already in same enterprise can be re-bound (updated)."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        target = _build_user()
        _setup_profile(
            target, role_code='employee',
            enterprise_id=enterprise.id, real_name='Old Name',
        )

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.url, {
            'phone': target.username,
            'real_name': 'New Name',
            'role_code': 'enterprise_admin',
        })
        assert response.data['code'] == 200
        target_profile = target.ent_user_profile
        target_profile.refresh_from_db()
        assert target_profile.real_name == 'New Name'
        assert target_profile.role_code == 'enterprise_admin'

    def test_bind_missing_required_fields(self):
        """Missing required fields returns error."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)

        self.client.force_authenticate(user=admin)
        response = self.client.post(self.url, {
            'phone': '12345678901',
        })
        assert response.data['code'] == 400

    # ==================== Permission tests ====================

    def test_unauthenticated_denied(self):
        """Unauthenticated request returns 401."""
        response = self.client.post(self.url, {
            'phone': '12345678901',
            'real_name': 'Test',
            'role_code': 'employee',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_denied(self):
        """Employee (non-admin) cannot bind users."""
        enterprise = _build_enterprise()
        _build_admin(enterprise)
        emp = _build_user()
        _setup_profile(emp, role_code='employee', enterprise_id=enterprise.id)
        target = _build_user()

        self.client.force_authenticate(user=emp)
        response = self.client.post(self.url, {
            'phone': target.username,
            'real_name': 'Test',
            'role_code': 'employee',
        })
        assert response.data['code'] == 403
