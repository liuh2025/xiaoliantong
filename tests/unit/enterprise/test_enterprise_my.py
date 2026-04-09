"""
ENT-006: My Enterprise API unit tests.
Tests cover: user with enterprise, user without enterprise,
unauthenticated access, response fields.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile


def _create_user_with_enterprise(username='testuser'):
    """Helper to create a user and bind to an enterprise."""
    user = User.objects.create_user(
        username=username, password='testpass123',
    )
    ent = Enterprise(
        name='Test Enterprise',
        credit_code=f'91110000MA{username[:5]:0<8}1X',
        legal_representative='Zhang San',
        business_license='https://example.com/license.jpg',
        industry_id=1,
        sub_industry_id=101,
        province_id=110000,
        region_id=110100,
        auth_status=Enterprise.AuthStatus.VERIFIED,
        admin_user=user,
    )
    ent.save()
    profile = user.ent_user_profile
    profile.enterprise_id = ent.id
    profile.role_code = 'enterprise_admin'
    profile.save()
    return user, ent


@pytest.mark.django_db
class TestMyEnterpriseAPI:
    """ENT-006: My Enterprise API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('enterprise:enterprise-my')

    # ==================== Successful retrieval tests ====================

    def test_my_enterprise_success(self):
        """GET /ent/enterprise/my returns current user's enterprise."""
        user, ent = _create_user_with_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['id'] == ent.id
        assert response.data['data']['name'] == ent.name

    def test_my_enterprise_response_format(self):
        """Response follows unified format {code, message, data}."""
        user, ent = _create_user_with_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.url)
        assert response.data['code'] == 200
        assert 'message' in response.data
        assert 'data' in response.data
        assert isinstance(response.data['data'], dict)

    def test_my_enterprise_returns_full_detail(self):
        """Response includes full enterprise detail fields."""
        user, ent = _create_user_with_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.url)
        data = response.data['data']
        # Same fields as enterprise detail
        assert 'id' in data
        assert 'name' in data
        assert 'auth_status' in data
        assert 'credit_code' in data
        assert 'description' in data
        assert 'tags' in data
        assert 'created_at' in data

    # ==================== User without enterprise tests ====================

    def test_my_enterprise_no_enterprise_bound(self):
        """GET /ent/enterprise/my returns 404 when user has no enterprise."""
        user = User.objects.create_user(username='noent', password='testpass123')
        self.client.force_authenticate(user=user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 404

    def test_my_enterprise_no_enterprise_message(self):
        """Returns appropriate message when user has no enterprise."""
        user = User.objects.create_user(username='noent2', password='testpass123')
        self.client.force_authenticate(user=user)

        response = self.client.get(self.url)
        assert response.data['code'] == 404
        assert 'data' in response.data

    def test_my_enterprise_null_enterprise_id(self):
        """User with null enterprise_id in profile gets 404."""
        user = User.objects.create_user(username='null_ent', password='testpass123')
        profile = user.ent_user_profile
        profile.enterprise_id = None
        profile.save()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.url)
        assert response.data['code'] == 404

    # ==================== Authentication tests ====================

    def test_my_enterprise_requires_authentication(self):
        """GET /ent/enterprise/my requires authentication."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== Enterprise deleted edge case ====================

    def test_my_enterprise_enterprise_deleted(self):
        """If the enterprise referenced by profile is deleted, returns 404."""
        user = User.objects.create_user(username='delent', password='testpass123')
        profile = user.ent_user_profile
        profile.enterprise_id = 99999  # Non-existent enterprise
        profile.save()
        self.client.force_authenticate(user=user)

        response = self.client.get(self.url)
        assert response.data['code'] == 404
