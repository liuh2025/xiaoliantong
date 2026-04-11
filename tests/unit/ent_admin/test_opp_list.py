"""
ADM-007: Enterprise Opportunity List API unit tests.
Tests cover: normal listing, filtering, keyword search, pagination, permission checks.
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

_counter = itertools.count(7000)


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
class TestOpportunityListAPI:
    """ADM-007: Enterprise Opportunity List API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('ent_admin:opp-list')

    def test_list_returns_enterprise_opportunities(self):
        """Admin can list own enterprise's opportunities."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        _build_opportunity(ent, admin, title='Opp 1')
        _build_opportunity(ent, admin, title='Opp 2')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        assert response.data['code'] == 200
        items = response.data['data']['items']
        assert len(items) == 2

    def test_list_response_format(self):
        """Response follows standard pagination format."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        _build_opportunity(ent, admin)

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        data = response.data['data']
        assert 'total' in data
        assert 'page' in data
        assert 'page_size' in data
        assert 'items' in data

    def test_list_includes_publisher_name(self):
        """Opportunity list includes publisher_name field."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        _build_opportunity(ent, admin)

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1
        assert 'publisher_name' in items[0]
        assert 'publisher_id' in items[0]

    def test_list_includes_status(self):
        """Opportunity list includes status field (ACTIVE and OFFLINE)."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        _build_opportunity(ent, admin, status=Opportunity.OppStatus.ACTIVE, title='Active')
        _build_opportunity(ent, admin, status=Opportunity.OppStatus.OFFLINE, title='Offline')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 2
        statuses = {i['status'] for i in items}
        assert 'ACTIVE' in statuses
        assert 'OFFLINE' in statuses

    def test_data_isolation(self):
        """Only see own enterprise's opportunities."""
        ent1 = _build_enterprise()
        ent2 = _build_enterprise()
        admin1 = _build_admin(ent1)
        admin2 = _build_admin(ent2)
        _build_opportunity(ent1, admin1, title='Ent1 Opp')
        _build_opportunity(ent2, admin2, title='Ent2 Opp')

        self.client.force_authenticate(user=admin1)
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['title'] == 'Ent1 Opp'

    def test_filter_by_type(self):
        """Filter opportunities by type."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        _build_opportunity(ent, admin, type=Opportunity.OppType.BUY, title='Buy')
        _build_opportunity(ent, admin, type=Opportunity.OppType.SUPPLY, title='Supply')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url, {'type': 'BUY'})
        assert response.data['data']['total'] == 1
        assert response.data['data']['items'][0]['title'] == 'Buy'

    def test_filter_by_status(self):
        """Filter opportunities by status."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        _build_opportunity(ent, admin, status=Opportunity.OppStatus.ACTIVE, title='Active')
        _build_opportunity(ent, admin, status=Opportunity.OppStatus.OFFLINE, title='Offline')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url, {'status': 'OFFLINE'})
        assert response.data['data']['total'] == 1
        assert response.data['data']['items'][0]['title'] == 'Offline'

    def test_keyword_search(self):
        """Keyword search on title and detail."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        _build_opportunity(ent, admin, title='Cloud Computing', detail='detail1')
        _build_opportunity(ent, admin, title='Hardware', detail='AI hardware detail')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url, {'keyword': 'Cloud'})
        assert response.data['data']['total'] == 1

    def test_pagination(self):
        """Pagination works correctly."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        for i in range(25):
            _build_opportunity(ent, admin, title=f'Opp {i:03d}')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url, {'page': 1, 'page_size': 10})
        data = response.data['data']
        assert data['total'] == 25
        assert len(data['items']) == 10
        assert data['page'] == 1

    def test_pagination_page_2(self):
        """Page 2 returns correct subset."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        for i in range(15):
            _build_opportunity(ent, admin, title=f'Opp {i:03d}')

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url, {'page': 2, 'page_size': 10})
        data = response.data['data']
        assert len(data['items']) == 5

    def test_empty_list(self):
        """Enterprise with no opportunities returns empty."""
        ent = _build_enterprise()
        admin = _build_admin(ent)

        self.client.force_authenticate(user=admin)
        response = self.client.get(self.url)
        assert response.data['data']['total'] == 0
        assert response.data['data']['items'] == []

    def test_employee_can_list(self):
        """Employee can also list enterprise opportunities."""
        ent = _build_enterprise()
        admin = _build_admin(ent)
        emp = _build_employee_user(ent)
        _build_opportunity(ent, admin)

        self.client.force_authenticate(user=emp)
        response = self.client.get(self.url)
        assert response.data['code'] == 200
        assert response.data['data']['total'] == 1

    # ==================== Permission tests ====================

    def test_unauthenticated_denied(self):
        """Unauthenticated request returns 401."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_no_enterprise_denied(self):
        """User without enterprise binding cannot access."""
        user = _build_user()
        _setup_profile(user, role_code='guest')

        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        assert response.data['code'] == 403
