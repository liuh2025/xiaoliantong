"""
ADM-008: Enterprise Opportunity Update API unit tests.
Tests cover: normal update, type immutable, permission checks.
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

_counter = itertools.count(8000)


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
class TestOpportunityUpdateAPI:
    """ADM-008: Enterprise Opportunity Update API tests."""

    def setup_method(self):
        self.client = APIClient()

    def _get_url(self, pk):
        return reverse('ent_admin:opp-detail', kwargs={'pk': pk})

    def test_admin_update_title(self):
        """Admin can update opportunity title."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(opp.id), {
            'title': 'Updated Title',
        })
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.title == 'Updated Title'

    def test_admin_update_detail(self):
        """Admin can update opportunity detail."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        emp = _build_employee_user(ent)
        opp = _build_opportunity(ent, emp)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(opp.id), {
            'detail': 'Updated detail',
        })
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.detail == 'Updated detail'

    def test_publisher_update_title(self):
        """Publisher (employee) can update their own opportunity."""
        ent = _build_enterprise()
        _build_admin(ent)
        emp = _build_employee_user(ent)
        opp = _build_opportunity(ent, emp)

        self.client.force_authenticate(user=emp)
        response = self.client.put(self._get_url(opp.id), {
            'title': 'Publisher Updated',
        })
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.title == 'Publisher Updated'

    def test_non_publisher_non_admin_denied(self):
        """Employee who is not publisher and not admin cannot update."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        emp1 = _build_employee_user(ent)
        emp2 = _build_employee_user(ent)
        opp = _build_opportunity(ent, emp1)

        self.client.force_authenticate(user=emp2)
        response = self.client.put(self._get_url(opp.id), {
            'title': 'Hacked',
        })
        assert response.data['code'] == 403

    def test_update_other_enterprise_denied(self):
        """Cannot update opportunity from another enterprise."""
        ent1 = _build_enterprise()
        ent2 = _build_enterprise()
        admin1 = _build_admin(ent1)
        admin2 = _build_admin(ent2)
        opp = _build_opportunity(ent2, admin2)

        self.client.force_authenticate(user=admin1)
        response = self.client.put(self._get_url(opp.id), {
            'title': 'Hacked',
        })
        assert response.data['code'] == 403

    def test_update_nonexistent_opportunity(self):
        """Update non-existent opportunity returns 404."""
        ent = _build_enterprise()
        admin = _build_admin(ent)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(99999), {
            'title': 'No Op',
        })
        assert response.data['code'] == 404

    def test_update_multiple_fields(self):
        """Update multiple fields at once."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin)

        self.client.force_authenticate(user=admin)
        response = self.client.put(self._get_url(opp.id), {
            'title': 'Multi Update',
            'detail': 'New Detail',
            'contact_name': 'New Contact',
        })
        assert response.data['code'] == 200
        opp.refresh_from_db()
        assert opp.title == 'Multi Update'
        assert opp.detail == 'New Detail'
        assert opp.contact_name == 'New Contact'

    # ==================== Permission tests ====================

    def test_unauthenticated_denied(self):
        """Unauthenticated request returns 401."""
        response = self.client.put(self._get_url(1), {'title': 'Test'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_no_enterprise_denied(self):
        """User without enterprise binding cannot update."""
        user = _build_user()
        _setup_profile(user, role_code='guest')
        ent = _build_enterprise()
        admin = _build_admin(ent)
        opp = _build_opportunity(ent, admin)

        self.client.force_authenticate(user=user)
        response = self.client.put(self._get_url(opp.id), {
            'title': 'Hacked',
        })
        assert response.data['code'] == 403
