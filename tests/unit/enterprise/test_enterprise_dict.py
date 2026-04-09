"""
ENT-008: Dictionary API unit tests.
Tests cover: industry list, category list, region list,
parent_id filtering, public access.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import MasterData


def _create_master_data(**overrides):
    """Helper to create and return a MasterData instance."""
    defaults = {
        'category': 'industry',
        'name': 'Test Industry',
        'code': 'IND001',
        'parent_id': None,
        'industry_id': None,
        'sort_order': 0,
        'is_active': True,
    }
    defaults.update(overrides)
    md = MasterData(**defaults)
    md.save()
    return md


@pytest.mark.django_db
class TestIndustryAPI:
    """ENT-008: Industry list API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('enterprise:industry-list')

    def test_industry_list_returns_200(self):
        """GET /ent/industry returns 200 OK."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_industry_list_response_format(self):
        """Response follows unified format {code, data}."""
        response = self.client.get(self.url)
        assert response.data['code'] == 200
        assert 'data' in response.data

    def test_industry_list_no_filter_returns_all_industries(self):
        """Without parent_id, returns all industry records."""
        _create_master_data(category='industry', name='Industry A', code='A')
        _create_master_data(category='industry', name='Industry B', code='B')
        response = self.client.get(self.url)
        assert len(response.data['data']) == 2

    def test_industry_list_filter_by_parent_id_0(self):
        """parent_id=0 returns top-level industries (parent_id is None)."""
        _create_master_data(category='industry', name='Top Level', code='TOP', parent_id=None)
        _create_master_data(category='industry', name='Sub Level', code='SUB', parent_id=1)
        response = self.client.get(self.url, {'parent_id': 0})
        items = response.data['data']
        assert len(items) == 1
        assert items[0]['name'] == 'Top Level'

    def test_industry_list_filter_by_parent_id(self):
        """parent_id={id} returns sub-industries under that parent."""
        parent = _create_master_data(category='industry', name='Parent', code='P')
        _create_master_data(category='industry', name='Child 1', code='C1', parent_id=parent.id)
        _create_master_data(category='industry', name='Child 2', code='C2', parent_id=parent.id)
        response = self.client.get(self.url, {'parent_id': parent.id})
        items = response.data['data']
        assert len(items) == 2

    def test_industry_list_only_returns_industry_category(self):
        """Only returns records with category='industry'."""
        _create_master_data(category='industry', name='Industry', code='I1')
        _create_master_data(category='category', name='Category', code='C1')
        response = self.client.get(self.url)
        items = response.data['data']
        assert len(items) == 1
        assert items[0]['name'] == 'Industry'

    def test_industry_list_includes_required_fields(self):
        """Each item includes id, name, code."""
        _create_master_data(category='industry', name='Test Ind', code='TI01')
        response = self.client.get(self.url)
        item = response.data['data'][0]
        assert 'id' in item
        assert 'name' in item
        assert 'code' in item

    def test_industry_list_public_access(self):
        """Industry list is a public endpoint."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_industry_list_excludes_inactive(self):
        """Inactive records are excluded."""
        _create_master_data(category='industry', name='Active', code='A', is_active=True)
        _create_master_data(category='industry', name='Inactive', code='I', is_active=False)
        response = self.client.get(self.url)
        items = response.data['data']
        assert len(items) == 1
        assert items[0]['name'] == 'Active'


@pytest.mark.django_db
class TestCategoryAPI:
    """ENT-008: Category list API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('enterprise:category-list')

    def test_category_list_returns_200(self):
        """GET /ent/category returns 200 OK."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_category_list_filter_by_industry_id(self):
        """GET /ent/category?industry_id={id} returns categories for that industry."""
        _create_master_data(category='category', name='Cat A', code='CA', industry_id=1)
        _create_master_data(category='category', name='Cat B', code='CB', industry_id=2)
        response = self.client.get(self.url, {'industry_id': 1})
        items = response.data['data']
        assert len(items) == 1
        assert items[0]['name'] == 'Cat A'

    def test_category_list_only_returns_category_type(self):
        """Only returns records with category='category'."""
        _create_master_data(category='category', name='Cat', code='C')
        _create_master_data(category='industry', name='Ind', code='I')
        response = self.client.get(self.url)
        items = response.data['data']
        assert len(items) == 1
        assert items[0]['name'] == 'Cat'

    def test_category_list_public_access(self):
        """Category list is a public endpoint."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRegionAPI:
    """ENT-008: Region list API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('enterprise:region-list')

    def test_region_list_returns_200(self):
        """GET /ent/region returns 200 OK."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_region_list_filter_by_parent_id_0(self):
        """parent_id=0 returns provinces (parent_id is None)."""
        _create_master_data(category='region', name='Beijing', code='110000', parent_id=None)
        _create_master_data(category='region', name='Beijing City', code='110100', parent_id=1)
        response = self.client.get(self.url, {'parent_id': 0})
        items = response.data['data']
        assert len(items) == 1
        assert items[0]['name'] == 'Beijing'

    def test_region_list_filter_by_parent_id(self):
        """parent_id={id} returns cities under that province."""
        parent = _create_master_data(category='region', name='Beijing', code='110000')
        _create_master_data(
            category='region', name='Haidian', code='110108', parent_id=parent.id,
        )
        _create_master_data(
            category='region', name='Chaoyang', code='110105', parent_id=parent.id,
        )
        response = self.client.get(self.url, {'parent_id': parent.id})
        items = response.data['data']
        assert len(items) == 2

    def test_region_list_only_returns_region_type(self):
        """Only returns records with category='region'."""
        _create_master_data(category='region', name='Region', code='R')
        _create_master_data(category='industry', name='Industry', code='I')
        response = self.client.get(self.url)
        items = response.data['data']
        assert len(items) == 1
        assert items[0]['name'] == 'Region'

    def test_region_list_public_access(self):
        """Region list is a public endpoint."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
