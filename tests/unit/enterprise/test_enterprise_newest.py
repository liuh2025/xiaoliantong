"""
ENT-009: Newest Enterprises API unit tests.
Tests cover: response format, only VERIFIED, ordering, limit 3, public access.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise


def _create_enterprise(**overrides):
    """Helper to create and return a saved Enterprise instance."""
    defaults = {
        'name': 'Test Enterprise',
        'credit_code': '91110000MA01ABCD1X',
        'legal_representative': 'Zhang San',
        'business_license': 'https://example.com/license.jpg',
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


@pytest.mark.django_db
class TestNewestEnterpriseAPI:
    """ENT-009: Newest Enterprises API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('enterprise:enterprise-newest')

    # ==================== Basic response tests ====================

    def test_newest_returns_200(self):
        """GET /ent/enterprise/newest returns 200 OK."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_newest_response_format(self):
        """Response follows unified format {code, data}."""
        _create_enterprise()
        response = self.client.get(self.url)
        assert response.data['code'] == 200
        assert 'data' in response.data
        assert 'items' in response.data['data']

    # ==================== Only VERIFIED enterprises ====================

    def test_newest_only_verified(self):
        """Only returns VERIFIED enterprises."""
        _create_enterprise(
            credit_code='V001', name='Verified', auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='U001', name='Unclaimed', auth_status=Enterprise.AuthStatus.UNCLAIMED,
        )
        _create_enterprise(
            credit_code='P001', name='Pending', auth_status=Enterprise.AuthStatus.PENDING,
        )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['name'] == 'Verified'

    def test_newest_excludes_non_verified(self):
        """Non-VERIFIED enterprises are excluded from newest list."""
        _create_enterprise(
            credit_code='R001', auth_status=Enterprise.AuthStatus.REJECTED,
        )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 0

    # ==================== Limit to 3 results ====================

    def test_newest_limit_3(self):
        """Returns at most 3 enterprises."""
        for i in range(5):
            _create_enterprise(
                credit_code=f'NL{i:03d}', name=f'Enterprise {i}',
                auth_status=Enterprise.AuthStatus.VERIFIED,
            )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 3

    def test_newest_less_than_3(self):
        """Returns fewer than 3 if not enough VERIFIED enterprises exist."""
        _create_enterprise(
            credit_code='N1', auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1

    def test_newest_empty(self):
        """Returns empty items when no VERIFIED enterprises exist."""
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 0

    # ==================== Ordering tests ====================

    def test_newest_ordering_by_created_at_desc(self):
        """Returns enterprises ordered by created_at descending."""
        import time
        ent1 = _create_enterprise(
            credit_code='O01', name='First',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        time.sleep(0.01)
        ent2 = _create_enterprise(
            credit_code='O02', name='Second',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        time.sleep(0.01)
        ent3 = _create_enterprise(
            credit_code='O03', name='Third',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert items[0]['name'] == 'Third'
        assert items[1]['name'] == 'Second'
        assert items[2]['name'] == 'First'

    # ==================== Response fields tests ====================

    def test_newest_fields(self):
        """Response items contain required fields: id, name, logo_url, industry_name,
        sub_industry_name, auth_status."""
        _create_enterprise(
            credit_code='F01', name='Fields Corp',
            logo_url='https://example.com/logo.png',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url)
        item = response.data['data']['items'][0]
        assert 'id' in item
        assert 'name' in item
        assert 'logo_url' in item
        assert 'industry_name' in item
        assert 'sub_industry_name' in item
        assert 'auth_status' in item

    # ==================== Public access tests ====================

    def test_newest_public_access(self):
        """Newest enterprises endpoint is public (no auth required)."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
