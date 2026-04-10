"""
ENT-007: Enterprise Update API unit tests.
Tests cover: successful update, permission (only admin), locked fields,
unauthenticated access, field validation.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile


def _create_admin_with_enterprise(username='admin_user'):
    """Helper to create a user who is the admin of an enterprise."""
    user = User.objects.create_user(
        username=username, password='testpass123',
    )
    ent = Enterprise(
        name='Test Enterprise',
        credit_code=f'91{username[:4]:0<6}1X',
        legal_representative='Zhang San',
        business_license='https://example.com/license.jpg',
        industry_id=1,
        sub_industry_id=101,
        category_id=5,
        province_id=110000,
        region_id=110100,
        tags=['old_tag'],
        description='Old description',
        auth_status=Enterprise.AuthStatus.PENDING,
        admin_user=user,
    )
    ent.save()
    profile = user.ent_user_profile
    profile.enterprise_id = ent.id
    profile.role_code = 'enterprise_admin'
    profile.save()
    return user, ent


@pytest.mark.django_db
class TestEnterpriseUpdateAPI:
    """ENT-007: Enterprise Update API tests."""

    def setup_method(self):
        self.client = APIClient()

    def _update_url(self, pk):
        return reverse('enterprise:enterprise-detail', kwargs={'pk': pk})

    # ==================== Successful update tests ====================

    def test_update_success(self):
        """PUT /ent/enterprise/{id} successfully updates allowed fields."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.put(self._update_url(ent.id), {
            'category_id': 10,
            'province_id': 310000,
            'region_id': 310100,
            'description': 'Updated description',
            'tags': ['new_tag'],
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200

    def test_update_persists_changes(self):
        """Updated fields are persisted in the database."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        self.client.put(self._update_url(ent.id), {
            'category_id': 10,
            'description': 'New description',
            'tags': ['updated'],
        }, format='json')

        ent.refresh_from_db()
        assert ent.category_id == 10
        assert ent.description == 'New description'
        assert ent.tags == ['updated']

    def test_update_response_contains_full_data(self):
        """Update response includes updated enterprise info."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.put(self._update_url(ent.id), {
            'description': 'Updated desc',
        }, format='json')
        data = response.data['data']
        assert data['id'] == ent.id
        assert data['description'] == 'Updated desc'

    # ==================== Updatable fields tests ====================

    def test_update_category_id(self):
        """Can update category_id."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)
        response = self.client.put(self._update_url(ent.id), {'category_id': 99}, format='json')
        assert response.data['code'] == 200

    def test_update_province_id(self):
        """Can update province_id."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)
        response = self.client.put(self._update_url(ent.id), {'province_id': 440000}, format='json')
        assert response.data['code'] == 200

    def test_update_region_id(self):
        """Can update region_id."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)
        response = self.client.put(self._update_url(ent.id), {'region_id': 440100}, format='json')
        assert response.data['code'] == 200

    def test_update_description(self):
        """Can update description."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)
        response = self.client.put(self._update_url(ent.id), {'description': 'New desc'}, format='json')
        assert response.data['code'] == 200

    def test_update_logo_url(self):
        """Can update logo_url."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)
        response = self.client.put(self._update_url(ent.id), {'logo_url': 'https://new.logo/logo.png'}, format='json')
        assert response.data['code'] == 200

    def test_update_tags(self):
        """Can update tags."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)
        response = self.client.put(self._update_url(ent.id), {'tags': ['tag1', 'tag2']}, format='json')
        assert response.data['code'] == 200

    # ==================== Locked fields tests ====================

    def test_cannot_update_name(self):
        """name is a locked field and cannot be updated."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        self.client.put(self._update_url(ent.id), {'name': 'New Name'}, format='json')
        ent.refresh_from_db()
        assert ent.name == 'Test Enterprise'  # unchanged

    def test_cannot_update_credit_code(self):
        """credit_code is a locked field and cannot be updated."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        self.client.put(self._update_url(ent.id), {'credit_code': 'NEW_CODE'}, format='json')
        ent.refresh_from_db()
        assert ent.credit_code != 'NEW_CODE'

    def test_cannot_update_legal_representative(self):
        """legal_representative is a locked field and cannot be updated."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        self.client.put(self._update_url(ent.id), {'legal_representative': 'New Name'}, format='json')
        ent.refresh_from_db()
        assert ent.legal_representative == 'Zhang San'

    def test_cannot_update_business_license(self):
        """business_license is a locked field and cannot be updated."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        self.client.put(self._update_url(ent.id), {'business_license': 'https://new.license'}, format='json')
        ent.refresh_from_db()
        assert ent.business_license == 'https://example.com/license.jpg'

    def test_cannot_update_industry_id(self):
        """industry_id is a locked field and cannot be updated."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        self.client.put(self._update_url(ent.id), {'industry_id': 999}, format='json')
        ent.refresh_from_db()
        assert ent.industry_id == 1

    def test_cannot_update_sub_industry_id(self):
        """sub_industry_id is a locked field and cannot be updated."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        self.client.put(self._update_url(ent.id), {'sub_industry_id': 999}, format='json')
        ent.refresh_from_db()
        assert ent.sub_industry_id == 101

    def test_cannot_update_auth_status(self):
        """auth_status is a locked field and cannot be updated."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        self.client.put(self._update_url(ent.id), {'auth_status': Enterprise.AuthStatus.VERIFIED}, format='json')
        ent.refresh_from_db()
        assert ent.auth_status == Enterprise.AuthStatus.PENDING

    # ==================== Permission tests ====================

    def test_update_requires_authentication(self):
        """PUT /ent/enterprise/{id} requires authentication."""
        _, ent = _create_admin_with_enterprise('owner')
        response = self.client.put(self._update_url(ent.id), {'description': 'hacked'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_only_admin_can_update(self):
        """Only the enterprise admin_user can update the enterprise."""
        admin, ent = _create_admin_with_enterprise('admin')
        other_user = User.objects.create_user(username='other', password='testpass123')
        self.client.force_authenticate(user=other_user)

        response = self.client.put(self._update_url(ent.id), {'description': 'hacked'}, format='json')
        assert response.data['code'] in (403, 404)

    def test_update_non_existent_enterprise(self):
        """Updating non-existent enterprise returns 404."""
        user = User.objects.create_user(username='nobody', password='testpass123')
        self.client.force_authenticate(user=user)

        response = self.client.put(self._update_url(99999), {'description': 'test'}, format='json')
        assert response.data['code'] == 404

    # ==================== Response format tests ====================

    def test_update_response_format(self):
        """Response follows unified format {code, message, data}."""
        user, ent = _create_admin_with_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.put(self._update_url(ent.id), {'description': 'Updated'}, format='json')
        assert response.data['code'] == 200
        assert 'message' in response.data
        assert 'data' in response.data
