"""PLAT-009: System settings tests."""
import pytest
from django.urls import reverse
from django.core.cache import cache


@pytest.mark.django_db
class TestSettingsGet:
    """Tests for GET /api/v1/plat-admin/settings."""

    def setup_method(self):
        self.url = reverse('plat_admin:settings')

    def test_get_settings_empty(self, api_client, platform_admin):
        cache.delete('plat_admin_settings')
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.data['code'] == 200

    def test_get_settings_by_key(self, api_client, platform_admin):
        cache.set('plat_admin_settings', {'site_name': 'XiaoLianTong'}, timeout=None)
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'key': 'site_name'})
        assert response.data['data']['key'] == 'site_name'
        assert response.data['data']['value'] == 'XiaoLianTong'

    def test_get_settings_nonexistent_key(self, api_client, platform_admin):
        cache.set('plat_admin_settings', {}, timeout=None)
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'key': 'nonexistent'})
        assert response.data['data']['value'] == ''

    def test_get_all_settings(self, api_client, platform_admin):
        cache.set('plat_admin_settings', {'k1': 'v1', 'k2': 'v2'}, timeout=None)
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert 'items' in response.data['data']

    def test_unauthenticated_denied(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestSettingsUpdate:
    """Tests for PUT /api/v1/plat-admin/settings."""

    def setup_method(self):
        self.url = reverse('plat_admin:settings')
        cache.delete('plat_admin_settings')

    def test_update_setting(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(self.url, {
            'key': 'site_name',
            'value': 'New Site Name',
        })
        assert response.data['code'] == 200
        assert response.data['data']['key'] == 'site_name'
        assert response.data['data']['value'] == 'New Site Name'

        # Verify persisted in cache
        settings = cache.get('plat_admin_settings')
        assert settings['site_name'] == 'New Site Name'

    def test_update_multiple_settings(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        api_client.put(self.url, {'key': 'k1', 'value': 'v1'})
        api_client.put(self.url, {'key': 'k2', 'value': 'v2'})

        settings = cache.get('plat_admin_settings')
        assert settings['k1'] == 'v1'
        assert settings['k2'] == 'v2'

    def test_update_invalid_data(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(self.url, {})
        assert response.data['code'] == 400
