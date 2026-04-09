"""Shared test fixtures for plat_admin tests."""
import itertools

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.enterprise.models import Enterprise, MasterData, AuditRecord
from apps.auth_app.models import UserProfile

_counter = itertools.count(200000)


def _unique_int():
    return next(_counter)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def platform_admin():
    """Create a platform admin user (super_admin)."""
    n = _unique_int()
    user = User.objects.create_user(
        username=f'platadmin_{n}', password='testpass123',
    )
    profile = UserProfile.objects.get(user=user)
    profile.role_code = 'super_admin'
    profile.real_name = 'Platform Admin'
    profile.save()
    # Reload user to clear cached profile relation
    return User.objects.select_related('ent_user_profile').get(pk=user.pk)


@pytest.fixture
def platform_operator():
    """Create a platform operator user."""
    n = _unique_int()
    user = User.objects.create_user(
        username=f'platop_{n}', password='testpass123',
    )
    profile = UserProfile.objects.get(user=user)
    profile.role_code = 'platform_operator'
    profile.real_name = 'Platform Operator'
    profile.save()
    return User.objects.select_related('ent_user_profile').get(pk=user.pk)


@pytest.fixture
def guest_user():
    """Create a guest user (non-admin)."""
    n = _unique_int()
    user = User.objects.create_user(
        username=f'guest_{n}', password='testpass123',
    )
    return User.objects.select_related('ent_user_profile').get(pk=user.pk)


@pytest.fixture
def enterprise_admin():
    """Create an enterprise admin user."""
    n = _unique_int()
    user = User.objects.create_user(
        username=f'entadmin_{n}', password='testpass123',
    )
    ent = Enterprise.objects.create(
        name=f'Test Enterprise {n}',
        credit_code=f'91{n:014d}X',
        legal_representative='Test Legal',
        business_license='https://example.com/license.jpg',
        industry_id=1,
        sub_industry_id=2,
        province_id=110000,
        region_id=110100,
        auth_status=Enterprise.AuthStatus.VERIFIED,
    )
    ent.admin_user = user
    ent.save()
    profile = UserProfile.objects.get(user=user)
    profile.role_code = 'enterprise_admin'
    profile.enterprise_id = ent.id
    profile.real_name = 'Ent Admin'
    profile.save()
    return User.objects.select_related('ent_user_profile').get(pk=user.pk)


def build_enterprise(**overrides):
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


def build_user(**overrides):
    n = _unique_int()
    defaults = {'username': f'testuser_{n}', 'password': 'testpass123'}
    defaults.update(overrides)
    return User.objects.create_user(**defaults)


def setup_profile(user, **kwargs):
    profile = user.ent_user_profile
    for key, value in kwargs.items():
        setattr(profile, key, value)
    profile.save()
    return profile
