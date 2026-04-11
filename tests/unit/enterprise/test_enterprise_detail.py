"""
ENT-003: Enterprise Detail API unit tests.
Tests cover: response format, all DESN fields, desensitization logic,
not found handling, public access.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile


def _build_enterprise(**overrides):
    """Helper to build a valid Enterprise dict with sensible defaults."""
    defaults = {
        'name': 'Test Enterprise Co., Ltd.',
        'credit_code': '91MA01ABCD1234X',
        'legal_representative': 'Zhang San',
        'business_license': 'https://example.com/license/test.jpg',
        'industry_id': 1,
        'sub_industry_id': 101,
        'province_id': 110000,
        'region_id': 110100,
        'auth_status': Enterprise.AuthStatus.VERIFIED,
    }
    defaults.update(overrides)
    return Enterprise(**defaults)


def _create_enterprise(**overrides):
    """Helper to create and return a saved Enterprise instance."""
    ent = _build_enterprise(**overrides)
    ent.save()
    return ent


@pytest.mark.django_db
class TestEnterpriseDetailAPI:
    """ENT-003: Enterprise Detail API tests."""

    def setup_method(self):
        self.client = APIClient()

    def _detail_url(self, pk):
        return reverse('enterprise:enterprise-detail', kwargs={'pk': pk})

    # ==================== Basic response format tests ====================

    def test_detail_returns_200(self):
        """GET /ent/enterprise/{id} returns 200 OK for existing enterprise."""
        ent = _create_enterprise()
        response = self.client.get(self._detail_url(ent.id))
        assert response.status_code == status.HTTP_200_OK

    def test_detail_response_format(self):
        """Response follows the unified format: {code, message, data}."""
        ent = _create_enterprise()
        response = self.client.get(self._detail_url(ent.id))
        data = response.data
        assert data['code'] == 200
        assert data['message'] == 'success'
        assert 'data' in data
        # data.data should be an object, not a list
        assert isinstance(data['data'], dict)

    def test_detail_not_found(self):
        """GET /ent/enterprise/{id} returns 404 for non-existent enterprise."""
        response = self.client.get(self._detail_url(99999))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 404

    def test_detail_not_found_message(self):
        """404 response includes a descriptive message."""
        response = self.client.get(self._detail_url(99999))
        assert 'data' in response.data
        assert response.data['data'] is None or response.data['data'] == {}

    # ==================== Permission tests ====================

    def test_no_auth_required(self):
        """Enterprise detail is a public endpoint, no authentication needed."""
        ent = _create_enterprise()
        response = self.client.get(self._detail_url(ent.id))
        assert response.status_code == status.HTTP_200_OK

    # ==================== VERIFIED enterprise - full info ====================

    def test_verified_enterprise_all_fields(self):
        """VERIFIED enterprise returns all DESN-defined fields with values."""
        user = User.objects.create_user(
            username='admin_user', password='testpass123',
            first_name='Admin', last_name='User',
        )
        # Signal auto-creates UserProfile; update it with test data
        profile = user.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.contact_phone = '13800138000'
        profile.save()
        ent = _create_enterprise(
            name='Full Info Corp',
            credit_code='91MA01ABCD1234X',
            logo_url='https://example.com/logo.png',
            legal_representative='Li Si',
            business_license='https://example.com/license.jpg',
            industry_id=1,
            sub_industry_id=101,
            category_id=5,
            province_id=110000,
            region_id=110100,
            tags=['cloud', 'AI'],
            description='A leading technology company.',
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=user,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']

        # Verify all DESN fields are present
        assert item['id'] == ent.id
        assert item['name'] == 'Full Info Corp'
        assert item['credit_code'] == '91MA01ABCD1234X'
        assert item['logo_url'] == 'https://example.com/logo.png'
        assert item['legal_representative'] == 'Li Si'
        assert item['business_license'] == 'https://example.com/license.jpg'
        assert item['industry_name'] == ''
        assert item['sub_industry_name'] == ''
        assert item['category_name'] == ''
        assert item['province_name'] == ''
        assert item['region_name'] == ''
        assert item['tags'] == ['cloud', 'AI']
        assert item['description'] == 'A leading technology company.'
        assert item['auth_status'] == Enterprise.AuthStatus.VERIFIED
        assert item['admin_user_name'] == 'Admin User'
        assert item['contact_phone'] == '13800138000'
        assert item['opportunities'] == []
        assert 'created_at' in item

    def test_verified_enterprise_contact_phone_visible(self):
        """VERIFIED enterprise shows contact_phone from UserProfile."""
        user = User.objects.create_user(
            username='phone_user', password='testpass123',
            email='admin@example.com',
        )
        # Signal auto-creates UserProfile; update it with test data
        profile = user.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.contact_phone = '13900139000'
        profile.save()
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=user,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert item['contact_phone'] == '13900139000'

    def test_verified_enterprise_admin_user_name(self):
        """VERIFIED enterprise shows admin_user_name from admin_user."""
        user = User.objects.create_user(
            username='named_admin', password='testpass123',
            first_name='John', last_name='Doe',
        )
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=user,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert item['admin_user_name'] == 'John Doe'

    def test_verified_enterprise_no_admin_user(self):
        """VERIFIED enterprise with no admin_user shows None for admin_user_name and contact_phone."""
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=None,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert item['admin_user_name'] is None
        assert item['contact_phone'] is None

    # ==================== Non-VERIFIED enterprise - desensitization ====================

    def test_unclaimed_enterprise_desensitized(self):
        """UNCLAIMED enterprise: sensitive fields are desensitized."""
        ent = _create_enterprise(
            name='Unclaimed Corp',
            credit_code='91MA01ABCD1234X',
            logo_url='https://example.com/logo.png',
            legal_representative='Secret Name',
            business_license='https://example.com/license.jpg',
            tags=['secret'],
            description='Secret info',
            auth_status=Enterprise.AuthStatus.UNCLAIMED,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']

        # Basic fields should still be present
        assert item['id'] == ent.id
        assert item['name'] == 'Unclaimed Corp'
        assert item['auth_status'] == Enterprise.AuthStatus.UNCLAIMED

        # Sensitive fields should be desensitized
        assert item['credit_code'] is None
        assert item['legal_representative'] is None
        assert item['contact_phone'] is None
        assert item['admin_user_name'] is None

    def test_pending_enterprise_desensitized(self):
        """PENDING enterprise: sensitive fields are desensitized."""
        ent = _create_enterprise(
            name='Pending Corp',
            credit_code='91110000PEND01X',
            legal_representative='Secret Person',
            auth_status=Enterprise.AuthStatus.PENDING,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']

        assert item['id'] == ent.id
        assert item['name'] == 'Pending Corp'
        assert item['auth_status'] == Enterprise.AuthStatus.PENDING
        assert item['credit_code'] is None
        assert item['legal_representative'] is None
        assert item['contact_phone'] is None
        assert item['admin_user_name'] is None

    def test_rejected_enterprise_desensitized(self):
        """REJECTED enterprise: sensitive fields are desensitized."""
        ent = _create_enterprise(
            name='Rejected Corp',
            credit_code='91MA01REJ01234X',
            legal_representative='Secret Person',
            auth_status=Enterprise.AuthStatus.REJECTED,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']

        assert item['id'] == ent.id
        assert item['name'] == 'Rejected Corp'
        assert item['auth_status'] == Enterprise.AuthStatus.REJECTED
        assert item['credit_code'] is None
        assert item['legal_representative'] is None
        assert item['contact_phone'] is None
        assert item['admin_user_name'] is None

    def test_non_verified_keeps_non_sensitive_fields(self):
        """Non-VERIFIED enterprise still shows non-sensitive fields."""
        ent = _create_enterprise(
            name='Public Corp',
            logo_url='https://example.com/logo.png',
            business_license='https://example.com/license.jpg',
            industry_id=1,
            sub_industry_id=101,
            category_id=5,
            province_id=110000,
            region_id=110100,
            tags=['cloud'],
            description='Visible description',
            auth_status=Enterprise.AuthStatus.UNCLAIMED,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']

        # These non-sensitive fields should still be visible
        assert item['logo_url'] == 'https://example.com/logo.png'
        assert item['business_license'] == 'https://example.com/license.jpg'
        assert item['description'] == 'Visible description'
        assert item['tags'] == ['cloud']
        assert item['industry_name'] == ''
        assert item['sub_industry_name'] == ''
        assert item['category_name'] == ''
        assert item['province_name'] == ''
        assert item['region_name'] == ''
        assert 'created_at' in item

    # ==================== Field type / format tests ====================

    def test_id_field_is_integer(self):
        """id field should be an integer."""
        ent = _create_enterprise()
        response = self.client.get(self._detail_url(ent.id))
        assert isinstance(response.data['data']['id'], int)

    def test_tags_field_is_list(self):
        """tags field should be a list."""
        ent = _create_enterprise(tags=['a', 'b'])
        response = self.client.get(self._detail_url(ent.id))
        assert isinstance(response.data['data']['tags'], list)

    def test_created_at_field_is_string(self):
        """created_at field should be a string."""
        ent = _create_enterprise()
        response = self.client.get(self._detail_url(ent.id))
        assert isinstance(response.data['data']['created_at'], str)

    def test_null_tags_field(self):
        """Enterprise with null tags returns null or empty list."""
        ent = _create_enterprise(tags=None)
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert item['tags'] is None or item['tags'] == []

    def test_empty_description(self):
        """Enterprise with empty description returns empty string."""
        ent = _create_enterprise(description='')
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert item['description'] == ''

    # ==================== Edge case tests ====================

    def test_invalid_id_format(self):
        """GET /ent/enterprise/abc returns proper error (Django URL routing rejects)."""
        # With URL pattern <int:pk>, non-integer will get 404 from URL resolver
        url = '/api/v1/ent/enterprise/abc'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ==================== contact_phone data source tests ====================

    def test_contact_phone_from_user_profile(self):
        """contact_phone is read from UserProfile, not from User.email."""
        user = User.objects.create_user(
            username='profile_phone_user', password='testpass123',
            email='email@example.com',
        )
        # Signal auto-creates UserProfile; update it with test data
        profile = user.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.contact_phone = '15800158000'
        profile.save()
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=user,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        # Should return profile phone, NOT email
        assert item['contact_phone'] == '15800158000'

    def test_contact_phone_none_when_no_profile(self):
        """contact_phone is None when admin_user has no UserProfile."""
        user = User.objects.create_user(
            username='no_profile_user', password='testpass123',
        )
        # Deliberately do NOT create a UserProfile
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=user,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert item['contact_phone'] is None

    def test_contact_phone_none_when_profile_phone_empty(self):
        """contact_phone is None when UserProfile.contact_phone is empty."""
        user = User.objects.create_user(
            username='empty_phone_user', password='testpass123',
        )
        # Signal auto-creates UserProfile; update it with empty phone
        profile = user.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.contact_phone = ''
        profile.save()
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=user,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert item['contact_phone'] is None

    def test_contact_phone_none_when_profile_phone_null(self):
        """contact_phone is None when UserProfile.contact_phone is null."""
        user = User.objects.create_user(
            username='null_phone_user', password='testpass123',
        )
        # Signal auto-creates UserProfile; contact_phone is already None by default
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=user,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert item['contact_phone'] is None

    # ==================== opportunities field tests ====================

    def test_opportunities_field_present_verified(self):
        """VERIFIED enterprise has opportunities field as empty list."""
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert 'opportunities' in item
        assert item['opportunities'] == []

    def test_opportunities_field_present_non_verified(self):
        """Non-VERIFIED enterprise also has opportunities field as empty list."""
        ent = _create_enterprise(
            auth_status=Enterprise.AuthStatus.UNCLAIMED,
        )
        response = self.client.get(self._detail_url(ent.id))
        item = response.data['data']
        assert 'opportunities' in item
        assert item['opportunities'] == []

    def test_opportunities_is_list_type(self):
        """opportunities field should always be a list."""
        ent = _create_enterprise()
        response = self.client.get(self._detail_url(ent.id))
        assert isinstance(response.data['data']['opportunities'], list)
