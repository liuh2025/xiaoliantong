"""
ENT-004: Enterprise Claim API unit tests.
Tests cover: successful claim, already claimed, enterprise not found,
unauthenticated access, and UserProfile updates.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise, AuditRecord
from apps.auth_app.models import UserProfile


def _create_unclaimed_enterprise(**overrides):
    """Helper to create and return an UNCLAIMED Enterprise."""
    defaults = {
        'name': 'Unclaimed Corp',
        'credit_code': '91MA01ABCD1234X',
        'legal_representative': 'Zhang San',
        'business_license': 'https://example.com/license.jpg',
        'industry_id': 1,
        'sub_industry_id': 101,
        'province_id': 110000,
        'region_id': 110100,
        'auth_status': Enterprise.AuthStatus.UNCLAIMED,
    }
    defaults.update(overrides)
    ent = Enterprise(**defaults)
    ent.save()
    return ent


def _create_user(username='testuser'):
    """Helper to create a user (signal auto-creates UserProfile)."""
    return User.objects.create_user(
        username=username, password='testpass123',
    )


@pytest.mark.django_db
class TestEnterpriseClaimAPI:
    """ENT-004: Enterprise Claim API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('enterprise:enterprise-claim')

    # ==================== Successful claim tests ====================

    def test_claim_success(self):
        """POST /ent/enterprise/claim successfully claims an UNCLAIMED enterprise."""
        user = _create_user()
        ent = _create_unclaimed_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {'credit_code': ent.credit_code}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['enterprise_id'] == ent.id
        assert response.data['data']['auth_status'] == Enterprise.AuthStatus.PENDING

    def test_claim_updates_enterprise_status(self):
        """Claiming an enterprise sets auth_status to PENDING and admin_user to current user."""
        user = _create_user()
        ent = _create_unclaimed_enterprise()
        self.client.force_authenticate(user=user)

        self.client.post(self.url, {'credit_code': ent.credit_code}, format='json')

        ent.refresh_from_db()
        assert ent.auth_status == Enterprise.AuthStatus.PENDING
        assert ent.admin_user == user

    def test_claim_creates_audit_record(self):
        """Claiming an enterprise creates an AuditRecord with status PENDING."""
        user = _create_user()
        ent = _create_unclaimed_enterprise()
        self.client.force_authenticate(user=user)

        self.client.post(self.url, {'credit_code': ent.credit_code})

        audit = AuditRecord.objects.filter(enterprise=ent).first()
        assert audit is not None
        assert audit.status == AuditRecord.AuditStatus.PENDING

    def test_claim_updates_user_profile(self):
        """Claiming updates UserProfile.enterprise_id and role_code."""
        user = _create_user()
        ent = _create_unclaimed_enterprise()
        self.client.force_authenticate(user=user)

        self.client.post(self.url, {'credit_code': ent.credit_code})

        profile = UserProfile.objects.get(user=user)
        assert profile.enterprise_id == ent.id
        assert profile.role_code == 'enterprise_admin'

    def test_claim_response_format(self):
        """Claim response follows unified format {code, message, data}."""
        user = _create_user()
        ent = _create_unclaimed_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {'credit_code': ent.credit_code})
        assert response.data['code'] == 200
        assert 'message' in response.data
        assert 'data' in response.data
        assert 'enterprise_id' in response.data['data']
        assert 'auth_status' in response.data['data']

    # ==================== Enterprise not found tests ====================

    def test_claim_nonexistent_enterprise(self):
        """Claiming with a non-existent credit_code returns error."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {'credit_code': 'NONEXISTENT_CODE'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 404

    def test_claim_wrong_credit_code(self):
        """Claiming with wrong credit_code for existing enterprise returns error."""
        user = _create_user()
        _create_unclaimed_enterprise()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {'credit_code': 'WRONG_CODE'})
        assert response.data['code'] == 404

    # ==================== Already claimed tests (BR-ENT-02) ====================

    def test_claim_already_claimed_pending(self):
        """BR-ENT-02: Cannot claim an enterprise already in PENDING status."""
        user1 = _create_user('user1')
        user2 = _create_user('user2')
        ent = _create_unclaimed_enterprise()
        self.client.force_authenticate(user=user1)
        self.client.post(self.url, {'credit_code': ent.credit_code})

        # Second user tries to claim
        self.client.force_authenticate(user=user2)
        response = self.client.post(self.url, {'credit_code': ent.credit_code})
        assert response.data['code'] in (400, 409)

    def test_claim_already_verified(self):
        """Cannot claim an already VERIFIED enterprise."""
        user = _create_user()
        ent = _create_unclaimed_enterprise(auth_status=Enterprise.AuthStatus.VERIFIED)
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {'credit_code': ent.credit_code})
        assert response.data['code'] in (400, 409)

    def test_claim_already_rejected(self):
        """Cannot claim a REJECTED enterprise (already claimed by someone)."""
        user = _create_user()
        ent = _create_unclaimed_enterprise(auth_status=Enterprise.AuthStatus.REJECTED)
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {'credit_code': ent.credit_code})
        assert response.data['code'] in (400, 409)

    # ==================== Authentication tests ====================

    def test_claim_requires_authentication(self):
        """POST /ent/enterprise/claim requires authentication."""
        ent = _create_unclaimed_enterprise()
        response = self.client.post(self.url, {'credit_code': ent.credit_code})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== Validation tests ====================

    def test_claim_missing_credit_code(self):
        """Claim without credit_code returns error."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {})
        assert response.data['code'] == 400

    def test_claim_empty_credit_code(self):
        """Claim with empty credit_code returns error."""
        user = _create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {'credit_code': ''})
        assert response.data['code'] == 400

    # ==================== Edge case tests ====================

    def test_claim_user_already_has_enterprise(self):
        """User who already has an enterprise can still claim another (no restriction in spec)."""
        user = _create_user()
        ent1 = _create_unclaimed_enterprise(credit_code='CODE000000000001')
        ent2 = _create_unclaimed_enterprise(credit_code='CODE000000000002')
        self.client.force_authenticate(user=user)

        # Claim first enterprise
        response1 = self.client.post(self.url, {'credit_code': ent1.credit_code})
        assert response1.data['code'] == 200

        # Claim second enterprise
        response2 = self.client.post(self.url, {'credit_code': ent2.credit_code})
        assert response2.data['code'] == 200

    def test_claim_is_idempotent_for_same_user(self):
        """Same user claiming same enterprise twice: second call should fail (not UNCLAIMED)."""
        user = _create_user()
        ent = _create_unclaimed_enterprise()
        self.client.force_authenticate(user=user)

        response1 = self.client.post(self.url, {'credit_code': ent.credit_code})
        assert response1.data['code'] == 200

        response2 = self.client.post(self.url, {'credit_code': ent.credit_code})
        assert response2.data['code'] in (400, 409)
