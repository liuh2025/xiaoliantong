"""PLAT-007: Master data CRUD tests."""
import pytest
from django.urls import reverse
from apps.enterprise.models import MasterData


@pytest.mark.django_db
class TestMasterDataList:
    """Tests for GET /api/v1/plat-admin/master-data."""

    def setup_method(self):
        self.url = reverse('plat_admin:master-data-list')

    def test_list_master_data(self, api_client, platform_admin):
        MasterData.objects.create(
            category='industry', name='IT', code='IT001',
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.data['data']['total'] >= 1

    def test_list_filter_by_category(self, api_client, platform_admin):
        MasterData.objects.create(category='industry', name='IT', code='IT001')
        MasterData.objects.create(category='region', name='Beijing', code='BJ001')
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'category': 'industry'})
        items = response.data['data']['items']
        for item in items:
            assert item['category'] == 'industry'

    def test_list_pagination(self, api_client, platform_admin):
        for i in range(3):
            MasterData.objects.create(
                category=f'cat_{i}', name=f'Name {i}', code=f'CODE_{i}',
            )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'page': 1, 'page_size': 2})
        assert len(response.data['data']['items']) == 2


@pytest.mark.django_db
class TestMasterDataCreate:
    """Tests for POST /api/v1/plat-admin/master-data."""

    def setup_method(self):
        self.url = reverse('plat_admin:master-data-list')

    def test_create_master_data(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(self.url, {
            'category': 'industry',
            'name': 'Manufacturing',
            'code': 'MFG001',
            'sort_order': 10,
        })
        assert response.data['code'] == 200
        assert MasterData.objects.filter(code='MFG001').exists()

    def test_create_with_parent(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(self.url, {
            'category': 'industry',
            'name': 'Sub Industry',
            'code': 'SUB001',
            'parent_id': 1,
        })
        assert response.data['code'] == 200

    def test_create_invalid_data(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(self.url, {})
        assert response.data['code'] == 400


@pytest.mark.django_db
class TestMasterDataUpdate:
    """Tests for PUT /api/v1/plat-admin/master-data/{id}."""

    def test_update_master_data(self, api_client, platform_admin):
        md = MasterData.objects.create(
            category='industry', name='Old Name', code='OLD001',
        )
        url = reverse('plat_admin:master-data-detail', kwargs={'pk': md.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'name': 'New Name'})
        assert response.data['code'] == 200

        md.refresh_from_db()
        assert md.name == 'New Name'

    def test_update_not_found(self, api_client, platform_admin):
        url = reverse('plat_admin:master-data-detail', kwargs={'pk': 99999})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'name': 'Test'})
        assert response.data['code'] == 404


@pytest.mark.django_db
class TestMasterDataToggleStatus:
    """Tests for PUT /api/v1/plat-admin/master-data/{id}/toggle-status."""

    def test_toggle_status(self, api_client, platform_admin):
        md = MasterData.objects.create(
            category='industry', name='Test', code='TST001', is_active=True,
        )
        url = reverse(
            'plat_admin:master-data-toggle-status',
            kwargs={'pk': md.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url)
        assert response.data['data']['is_active'] is False

        md.refresh_from_db()
        assert md.is_active is False
