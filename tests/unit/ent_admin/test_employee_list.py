"""
ADM-001: Employee List API unit tests.
Tests cover: normal listing, keyword search, permission checks, empty list.
"""
import itertools

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile

_counter = itertools.count(1000)


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
class TestEmployeeListAPI:
    """ADM-001: Employee List API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('ent_admin:employee-list')

    # ==================== Basic listing tests ====================

    def test_list_returns_employees(self):
        """Admin can list employees of own enterprise."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        _build_employee(enterprise, real_name='Emp One')
        _build_employee(enterprise, real_name='Emp Two')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        items = response.data['data']['items']
        assert len(items) == 3  # admin + 2 employees

    def test_list_fields(self):
        """Employee list returns correct fields."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        emp = _build_employee(enterprise, real_name='John', position='Engineer')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        items = response.data['data']['items']
        emp_item = [i for i in items if i['id'] == emp.id][0]
        assert emp_item['real_name'] == 'John'
        assert emp_item['phone'] == emp.username
        assert emp_item['role_code'] == 'employee'
        assert emp_item['is_active'] is True
        assert 'created_at' in emp_item

    def test_empty_list(self):
        """Admin with no other employees returns own profile."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['id'] == admin.id

    # ==================== Keyword search tests ====================

    def test_keyword_search_by_real_name(self):
        """Keyword search matches real_name."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        _build_employee(enterprise, real_name='Alice Wang')
        _build_employee(enterprise, real_name='Bob Li')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url, {'keyword': 'Alice'})
        items = response.data['data']['items']
        emp_items = [i for i in items if i['id'] != admin.id]
        assert len(emp_items) == 1
        assert 'Alice' in emp_items[0]['real_name']

    def test_keyword_search_by_phone(self):
        """Keyword search matches phone (username)."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        emp = _build_employee(enterprise, real_name='Test')
        phone = emp.username

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url, {'keyword': phone})
        items = response.data['data']['items']
        emp_items = [i for i in items if i['id'] == emp.id]
        assert len(emp_items) == 1

    def test_keyword_search_no_match(self):
        """Keyword with no match returns empty list."""
        enterprise = _build_enterprise()
        admin = _build_admin(enterprise)
        _build_employee(enterprise, real_name='Alice')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url, {'keyword': 'nonexistent'})
        items = response.data['data']['items']
        assert len(items) == 0  # no match for keyword

    # ==================== Data isolation tests ====================

    def test_data_isolation_between_enterprises(self):
        """Admin can only see own enterprise employees."""
        ent1 = _build_enterprise()
        ent2 = _build_enterprise()
        admin1 = _build_admin(ent1)
        _build_admin(ent2)
        _build_employee(ent2, real_name='Other Emp')

        self.client.force_authenticate(user=admin1)
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['id'] == admin1.id

    # ==================== Permission tests ====================

    def test_unauthenticated_denied(self):
        """Unauthenticated request returns 401."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_denied(self):
        """Employee (non-admin) cannot access employee list."""
        enterprise = _build_enterprise()
        emp = _build_employee(enterprise)

        self.client.force_authenticate(user=emp)
        response = self.client.get(self.url)
        assert response.data['code'] == 403

    def test_no_enterprise_denied(self):
        """User without enterprise binding cannot access."""
        user = _build_user()
        _setup_profile(user, role_code='guest')

        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        assert response.data['code'] == 403
