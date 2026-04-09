"""PLAT-008: RBAC role and permission tests."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestRoleList:
    """Tests for GET /api/v1/plat-admin/role."""

    def setup_method(self):
        self.url = reverse('plat_admin:role-list')

    def test_list_roles(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.data['code'] == 200
        items = response.data['data']['items']
        assert len(items) >= 5

    def test_role_fields(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        item = response.data['data']['items'][0]
        assert 'id' in item
        assert 'name' in item
        assert 'code' in item
        assert 'description' in item

    def test_role_unauthenticated_denied(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestRoleDetail:
    """Tests for GET /api/v1/plat-admin/role/{id}."""

    def test_role_detail(self, api_client, platform_admin):
        url = reverse('plat_admin:role-detail', kwargs={'pk': 1})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 200
        data = response.data['data']
        assert data['code'] == 'super_admin'
        assert 'permissions' in data

    def test_role_not_found(self, api_client, platform_admin):
        url = reverse('plat_admin:role-detail', kwargs={'pk': 999})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 404


@pytest.mark.django_db
class TestRolePermissionUpdate:
    """Tests for PUT /api/v1/plat-admin/role/{id}/permissions."""

    def test_update_permissions(self, api_client, platform_admin):
        url = reverse('plat_admin:role-permissions', kwargs={'pk': 2})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'permissions': ['dashboard', 'audit']})
        assert response.data['code'] == 200

    def test_update_nonexistent_role(self, api_client, platform_admin):
        url = reverse('plat_admin:role-permissions', kwargs={'pk': 999})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'permissions': ['test']})
        assert response.data['code'] == 404

    def test_update_invalid_data(self, api_client, platform_admin):
        url = reverse('plat_admin:role-permissions', kwargs={'pk': 1})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {})
        assert response.data['code'] == 400
