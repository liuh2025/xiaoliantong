"""
L1 API Integration Tests - Enterprise Module (ENT)

Tests all endpoints under /api/v1/ent/:
- Enterprise CRUD (list, detail, my, create, claim)
- Dictionary APIs (industry, category, region)
- Newest enterprises

TC-ID range: TC-API-ent-001 ~ TC-API-ent-012
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.enterprise.models import Enterprise, MasterData


# ============================================================
# Enterprise API Tests
# ============================================================


@pytest.mark.django_db
class TestEnterpriseAPI:
    """Enterprise module L1 API integration tests."""

    # TC-API-ent-001: List enterprises (public, default verified filter)
    def test_list_enterprises(self, anon_client, verified_enterprise):
        """TC-API-ent-001: GET /api/v1/ent/enterprise returns paginated list."""
        # The conftest fixture creates enterprise with auth_status='verified' (lowercase)
        # but the view filters by Enterprise.AuthStatus.VERIFIED = 'VERIFIED' (uppercase).
        # Update to match the view's expected value.
        verified_enterprise.auth_status = Enterprise.AuthStatus.VERIFIED
        verified_enterprise.save()

        url = '/api/v1/ent/enterprise'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'items' in data['data']
        assert 'total' in data['data']
        assert data['data']['total'] >= 1
        assert len(data['data']['items']) >= 1

    # TC-API-ent-002: List enterprises with pagination params
    def test_list_enterprises_pagination(self, anon_client, verified_enterprise):
        """TC-API-ent-002: GET /api/v1/ent/enterprise with page/page_size params."""
        verified_enterprise.auth_status = Enterprise.AuthStatus.VERIFIED
        verified_enterprise.save()

        url = '/api/v1/ent/enterprise'
        response = anon_client.get(url, {'page': 1, 'page_size': 5})

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['page'] == 1
        assert data['data']['page_size'] == 5
        assert 'total' in data['data']
        assert 'items' in data['data']

    # TC-API-ent-003: Newest enterprises (top 3 verified)
    def test_newest_enterprises(self, anon_client, verified_enterprise):
        """TC-API-ent-003: GET /api/v1/ent/enterprise/newest returns top 3."""
        verified_enterprise.auth_status = Enterprise.AuthStatus.VERIFIED
        verified_enterprise.save()

        url = '/api/v1/ent/enterprise/newest'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'items' in data['data']
        assert len(data['data']['items']) <= 3
        # Each item should have key fields
        if data['data']['items']:
            item = data['data']['items'][0]
            assert 'id' in item
            assert 'name' in item

    # TC-API-ent-004: Enterprise detail for existing enterprise
    def test_enterprise_detail(self, anon_client, verified_enterprise):
        """TC-API-ent-004: GET /api/v1/ent/enterprise/<id> returns detail."""
        url = f'/api/v1/ent/enterprise/{verified_enterprise.id}'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] is not None
        assert data['data']['id'] == verified_enterprise.id
        assert data['data']['name'] == verified_enterprise.name

    # TC-API-ent-005: Enterprise detail for non-existent enterprise
    def test_enterprise_detail_not_found(self, anon_client):
        """TC-API-ent-005: GET /api/v1/ent/enterprise/999999 returns 404."""
        url = '/api/v1/ent/enterprise/999999'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 404
        assert data['data'] is None

    # TC-API-ent-006: My enterprise with authenticated enterprise admin
    def test_my_enterprise(self, ent_admin_client, verified_enterprise):
        """TC-API-ent-006: GET /api/v1/ent/enterprise/my returns bound enterprise."""
        # The my-enterprise view reads enterprise_id from user profile.
        # The conftest creates the user with role='enterprise_admin' but does not
        # set enterprise_id on the profile. Update the profile to bind it.
        from apps.auth_app.models import UserProfile
        profile = UserProfile.objects.get(user=verified_enterprise.admin_user)
        profile.enterprise_id = verified_enterprise.id
        profile.save()

        url = '/api/v1/ent/enterprise/my'
        response = ent_admin_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] is not None
        assert data['data']['id'] == verified_enterprise.id

    # TC-API-ent-007: Create enterprise with valid data
    def test_create_enterprise(self, auth_client, normal_user):
        """TC-API-ent-007: POST /api/v1/ent/enterprise/create creates enterprise."""
        payload = {
            'name': '新建测试企业有限公司',
            'credit_code': '91MA9999888777X',
            'legal_representative': '李四',
            'business_license': 'https://example.com/new_license.jpg',
            'industry_id': 2,
            'sub_industry_id': 201,
            'province_id': 310000,
            'region_id': 310100,
        }
        url = '/api/v1/ent/enterprise/create'
        response = auth_client.post(url, payload, format='json')

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] is not None
        # name is returned in create response
        assert data['data']['name'] == '新建测试企业有限公司'
        # Verify enterprise was created in DB
        assert Enterprise.objects.filter(credit_code='91MA9999888777X').exists()

    # TC-API-ent-008: Create enterprise with duplicate credit_code
    def test_create_enterprise_duplicate_code(self, auth_client, verified_enterprise):
        """TC-API-ent-008: POST /api/v1/ent/enterprise/create with duplicate credit_code fails."""
        payload = {
            'name': '重复企业有限公司',
            'credit_code': verified_enterprise.credit_code,
            'legal_representative': '王五',
            'business_license': 'https://example.com/dup_license.jpg',
            'industry_id': 1,
            'sub_industry_id': 101,
            'province_id': 110000,
            'region_id': 110100,
        }
        url = '/api/v1/ent/enterprise/create'
        response = auth_client.post(url, payload, format='json')

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 400
        assert data['data'] is not None  # validation errors

    # TC-API-ent-009: Claim an unclaimed enterprise
    def test_claim_enterprise(self, auth_client, normal_user):
        """TC-API-ent-009: POST /api/v1/ent/enterprise/claim claims enterprise."""
        from apps.auth_app.models import UserProfile
        # Ensure user has a profile for the claim view to update
        profile, _ = UserProfile.objects.get_or_create(
            user=normal_user,
            defaults={'phone': '13800001111'},
        )

        # Create an unclaimed enterprise
        ent = Enterprise.objects.create(
            name='待认领企业有限公司',
            credit_code='91MACLAIM0001X',
            legal_representative='赵六',
            business_license='https://example.com/claim_license.jpg',
            industry_id=1,
            sub_industry_id=101,
            province_id=110000,
            region_id=110100,
            auth_status=Enterprise.AuthStatus.UNCLAIMED,
        )

        payload = {
            'credit_code': ent.credit_code,
        }
        url = '/api/v1/ent/enterprise/claim'
        response = auth_client.post(url, payload, format='json')

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['enterprise_id'] == ent.id
        assert data['data']['auth_status'] == Enterprise.AuthStatus.PENDING

    # TC-API-ent-010: Get industry dictionary
    def test_get_industry_dict(self, anon_client, master_data_industry):
        """TC-API-ent-010: GET /api/v1/ent/industry returns industry list."""
        url = '/api/v1/ent/industry'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
        assert len(data['data']) >= 2  # parent + child
        # Check that returned items are industry category
        for item in data['data']:
            assert item['category'] == 'industry'

    # TC-API-ent-011: Get region dictionary
    def test_get_region_dict(self, anon_client, master_data_region):
        """TC-API-ent-011: GET /api/v1/ent/region returns region list."""
        url = '/api/v1/ent/region'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
        assert len(data['data']) >= 2  # parent + child
        for item in data['data']:
            assert item['category'] == 'region'

    # TC-API-ent-012: Get category dictionary
    def test_get_category_dict(self, anon_client, master_data_category):
        """TC-API-ent-012: GET /api/v1/ent/category returns category list."""
        url = '/api/v1/ent/category'
        response = anon_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
        assert len(data['data']) >= 1
        assert data['data'][0]['category'] == 'category'
        assert data['data'][0]['name'] == '自动驾驶算法'
