"""
ENT-005: Enterprise Create API unit tests.
Tests cover: successful creation, credit_code uniqueness, required fields,
unauthenticated access, and UserProfile updates.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise, AuditRecord
from apps.auth_app.models import UserProfile


def _create_user(username='testuser'):
    """Helper to create a user (signal auto-creates UserProfile)."""
    return User.objects.create_user(
        username=username, password='testpass123',
    )


def _valid_create_payload(**overrides):
    """Helper to build a valid create request payload."""
    defaults = {
        'name': 'New Enterprise Co., Ltd.',
        'credit_code': '91MA01ABCD1234X',
        'legal_representative': 'Zhang San',
        'business_license': 'https://example.com/license.jpg',
        'industry_id': 1,
        'sub_industry_id': 101,
        'province_id': 110000,
        'region_id': 110100,
    }
    defaults.update(overrides)
    return defaults


@pytest.mark.django_db
class TestEnterpriseCreateAPI:
    """ENT-005: Enterprise Create API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('enterprise:enterprise-create')

    # ==================== Successful creation tests ====================

    def test_create_success(self):
        """POST /ent/enterprise/create successfully creates a new enterprise."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload()
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['id'] is not None
        assert response.data['data']['name'] == payload['name']

    def test_create_sets_auth_status_pending(self):
        """Created enterprise has auth_status=PENDING."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        self.client.post(self.url, _valid_create_payload(), format='json')

        ent = Enterprise.objects.first()
        assert ent.auth_status == Enterprise.AuthStatus.PENDING

    def test_create_sets_admin_user(self):
        """Created enterprise has admin_user set to the current user."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        self.client.post(self.url, _valid_create_payload(), format='json')

        ent = Enterprise.objects.first()
        assert ent.admin_user == user

    def test_create_creates_audit_record(self):
        """Creating an enterprise creates an AuditRecord with status PENDING."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        self.client.post(self.url, _valid_create_payload(), format='json')

        ent = Enterprise.objects.first()
        audit = AuditRecord.objects.filter(enterprise=ent).first()
        assert audit is not None
        assert audit.status == AuditRecord.AuditStatus.PENDING

    def test_create_updates_user_profile(self):
        """Creating updates UserProfile.enterprise_id and role_code."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        self.client.post(self.url, _valid_create_payload(), format='json')

        ent = Enterprise.objects.first()
        profile = UserProfile.objects.get(user=user)
        assert profile.enterprise_id == ent.id
        assert profile.role_code == 'enterprise_admin'

    def test_create_response_format(self):
        """Create response follows unified format {code, message, data}."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, _valid_create_payload(), format='json')
        assert response.data['code'] == 200
        assert 'message' in response.data
        assert 'data' in response.data
        data = response.data['data']
        assert 'id' in data
        assert 'name' in data
        assert 'credit_code' in data
        assert 'auth_status' in data

    def test_create_with_optional_fields(self):
        """Creating with optional fields (category_id, tags, description) works."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload(
            category_id=5,
            tags=['cloud', 'AI'],
            description='A great company',
        )
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 200

        ent = Enterprise.objects.first()
        assert ent.category_id == 5
        assert ent.tags == ['cloud', 'AI']
        assert ent.description == 'A great company'

    # ==================== credit_code uniqueness tests ====================

    def test_create_duplicate_credit_code(self):
        """Cannot create enterprise with duplicate credit_code."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload(credit_code='DUPLICATE001')
        response1 = self.client.post(self.url, payload, format='json')
        assert response1.data['code'] == 200

        # Try to create again with same credit_code
        response2 = self.client.post(self.url, payload, format='json')
        assert response2.data['code'] == 400

    def test_create_duplicate_credit_code_existing_enterprise(self):
        """Cannot create enterprise with credit_code that already exists in database."""
        user1 = _create_user('user1')
        user2 = _create_user('user2')
        self.client.force_authenticate(user=user1)
        self.client.post(self.url, _valid_create_payload(credit_code='EXISTING001'), format='json')

        self.client.force_authenticate(user=user2)
        response = self.client.post(self.url, _valid_create_payload(credit_code='EXISTING001'), format='json')
        assert response.data['code'] == 400

    # ==================== Required field validation tests (BR-ENT-05) ====================

    def test_create_missing_name(self):
        """BR-ENT-05: name is required."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload()
        del payload['name']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_create_missing_credit_code(self):
        """BR-ENT-05: credit_code is required."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload()
        del payload['credit_code']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_create_missing_legal_representative(self):
        """BR-ENT-05: legal_representative is required."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload()
        del payload['legal_representative']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_create_missing_business_license(self):
        """BR-ENT-05: business_license is required."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload()
        del payload['business_license']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_create_missing_industry_id(self):
        """BR-ENT-05: industry_id is required."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload()
        del payload['industry_id']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    def test_create_missing_province_id(self):
        """BR-ENT-05: province_id is required."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload()
        del payload['province_id']
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 400

    # ==================== Authentication tests ====================

    def test_create_requires_authentication(self):
        """POST /ent/enterprise/create requires authentication."""
        response = self.client.post(self.url, _valid_create_payload(), format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== Optional fields omitted tests ====================

    def test_create_without_optional_fields(self):
        """Creating without optional fields (category_id, tags, description) works."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        payload = _valid_create_payload()
        response = self.client.post(self.url, payload, format='json')
        assert response.data['code'] == 200

        ent = Enterprise.objects.first()
        assert ent.category_id is None
        assert ent.tags is None
        assert ent.description == ''
