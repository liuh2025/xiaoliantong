"""PLAT-002: Dashboard stats and trend tests."""
import pytest
from django.urls import reverse
from apps.enterprise.models import Enterprise
from apps.opportunity.models import Opportunity, ContactLog


@pytest.mark.django_db
class TestDashboardStats:
    """Tests for GET /api/v1/plat-admin/dashboard/stats."""

    def setup_method(self):
        self.url = reverse('plat_admin:dashboard-stats')

    def test_stats_returns_counts(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.status_code == 200
        data = response.data['data']
        assert 'enterprise_count' in data
        assert 'opportunity_count' in data
        assert 'deal_count' in data
        assert 'active_user_count' in data
        assert 'pending_audit_count' in data
        assert 'enterprise_trend' in data
        assert 'opportunity_trend' in data
        assert 'deal_trend' in data

    def test_stats_reflects_enterprise_count(self, api_client, platform_admin):
        for i in range(2):
            Enterprise.objects.create(
                name=f'Stats Ent {i}',
                credit_code=f'99{i:014d}X',
                legal_representative='Test',
                business_license='https://example.com/license.jpg',
                industry_id=1,
                sub_industry_id=2,
                province_id=110000,
                region_id=110100,
            )

        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.data['data']['enterprise_count'] >= 2

    def test_stats_unauthenticated_denied(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_stats_non_admin_denied(self, api_client, guest_user):
        api_client.force_authenticate(user=guest_user)
        response = api_client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestDashboardTrend:
    """Tests for GET /api/v1/plat-admin/dashboard/trend."""

    def setup_method(self):
        self.url = reverse('plat_admin:dashboard-trend')

    def test_trend_returns_data(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'type': 'opportunity', 'period': 30})
        assert response.status_code == 200
        data = response.data['data']
        assert 'opportunity_trend' in data

    def test_trend_enterprise_type(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'type': 'enterprise'})
        assert response.status_code == 200
        assert 'enterprise_trend' in response.data['data']

    def test_trend_deal_type(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'type': 'deal'})
        assert response.status_code == 200
        assert 'deal_trend' in response.data['data']
