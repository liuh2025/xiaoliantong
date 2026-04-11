"""Unit tests for OPP-008: Get contact info API.

POST /api/v1/opp/opportunity/{id}/contact
- Requires authenticated user with verified enterprise binding
- Returns full (non-masked) contact info
- Creates a ContactLog record
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.auth_app.models import UserProfile
from apps.enterprise.models import Enterprise, MasterData
from apps.opportunity.models import Opportunity, ContactLog


class OPP008ContactTests(TestCase):
    """Tests for OPP-008: Get contact info."""

    def setUp(self):
        """Create shared test fixtures."""
        self.client = APIClient()

        # Create master data entries for lookups
        self.industry = MasterData.objects.create(
            category='industry', name='IT', code='IT', is_active=True,
        )
        self.sub_industry = MasterData.objects.create(
            category='industry', name='Software', code='SW',
            parent_id=self.industry.id, is_active=True,
        )
        self.category = MasterData.objects.create(
            category='category', name='Dev Services', code='DS', is_active=True,
        )
        self.province = MasterData.objects.create(
            category='region', name='Beijing', code='BJ', is_active=True,
        )
        self.region = MasterData.objects.create(
            category='region', name='Haidian', code='HD',
            parent_id=self.province.id, is_active=True,
        )

        # Publisher user + verified enterprise
        self.publisher = User.objects.create_user(
            username='publisher', password='pass1234',
        )
        self.publisher_enterprise = Enterprise.objects.create(
            name='Publisher Corp',
            credit_code='123456789012345678',
            legal_representative='Alice',
            business_license='http://example.com/license.png',
            industry_id=self.industry.id,
            sub_industry_id=self.sub_industry.id,
            category_id=self.category.id,
            province_id=self.province.id,
            region_id=self.region.id,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )

        # Create an ACTIVE opportunity with contact info
        self.opp = Opportunity.objects.create(
            type=Opportunity.OppType.BUY,
            title='Test Opportunity',
            enterprise=self.publisher_enterprise,
            publisher=self.publisher,
            industry_id=self.industry.id,
            sub_industry_id=self.sub_industry.id,
            category_id=self.category.id,
            province_id=self.province.id,
            region_id=self.region.id,
            detail='Test detail',
            contact_name='Bob',
            contact_phone='13800138000',
            contact_wechat='bob_wx',
            status=Opportunity.OppStatus.ACTIVE,
        )

        # Requester user with verified enterprise
        # UserProfile is auto-created by signal; update it
        self.requester = User.objects.create_user(
            username='requester', password='pass1234',
        )
        self.requester_enterprise = Enterprise.objects.create(
            name='Requester Corp',
            credit_code='987654321098765432',
            legal_representative='Charlie',
            business_license='http://example.com/license2.png',
            industry_id=self.industry.id,
            sub_industry_id=self.sub_industry.id,
            category_id=self.category.id,
            province_id=self.province.id,
            region_id=self.region.id,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        self.requester.ent_user_profile.role_code = 'enterprise_admin'
        self.requester.ent_user_profile.enterprise_id = self.requester_enterprise.id
        self.requester.ent_user_profile.save()

    def _get_url(self, pk):
        return f'/api/v1/opp/opportunity/{pk}/contact'

    # ===== Positive cases =====

    def test_authenticated_with_verified_enterprise_can_get_contact(self):
        """Authenticated user with verified enterprise can get contact info."""
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self._get_url(self.opp.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 200)
        contact_data = data['data']
        self.assertEqual(contact_data['contact_name'], 'Bob')
        self.assertEqual(contact_data['contact_phone'], '13800138000')
        self.assertEqual(contact_data['contact_wechat'], 'bob_wx')

    def test_returns_full_contact_not_masked(self):
        """Contact phone should be returned in full (not masked)."""
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self._get_url(self.opp.id))
        data = response.json()
        # Full 11-digit phone, not masked like 138****8000
        self.assertEqual(data['data']['contact_phone'], '13800138000')
        self.assertNotIn('****', data['data']['contact_phone'])

    def test_creates_contact_log_record(self):
        """Getting contact info should create a ContactLog record."""
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self._get_url(self.opp.id))
        self.assertEqual(response.status_code, 200)

        # Verify ContactLog was created
        logs = ContactLog.objects.filter(
            opportunity=self.opp,
            getter_user=self.requester,
            getter_enterprise=self.requester_enterprise,
        )
        self.assertEqual(logs.count(), 1)
        log = logs.first()
        self.assertEqual(log.status, ContactLog.ContactStatus.COMPLETED)

    # ===== Negative cases =====

    def test_unauthenticated_user_cannot_get_contact(self):
        """Unauthenticated user should be denied."""
        response = self.client.post(self._get_url(self.opp.id))
        # DRF returns 401 for unauthenticated with JWT auth
        self.assertIn(response.status_code, [401, 403])

    def test_user_without_enterprise_cannot_get_contact(self):
        """Authenticated user without enterprise binding should be denied."""
        user_no_ent = User.objects.create_user(
            username='noent', password='pass1234',
        )
        # UserProfile auto-created by signal, defaults: role_code='guest', enterprise_id=None
        self.client.force_authenticate(user=user_no_ent)
        response = self.client.post(self._get_url(self.opp.id))
        data = response.json()
        self.assertEqual(data['code'], 403)

    def test_user_with_unverified_enterprise_cannot_get_contact(self):
        """User whose enterprise is not verified should be denied."""
        unverified_ent = Enterprise.objects.create(
            name='Unverified Corp',
            credit_code='111122223333444455',
            legal_representative='Dave',
            business_license='http://example.com/license3.png',
            industry_id=self.industry.id,
            sub_industry_id=self.sub_industry.id,
            category_id=self.category.id,
            province_id=self.province.id,
            region_id=self.region.id,
            auth_status=Enterprise.AuthStatus.PENDING,
        )
        user_unverified = User.objects.create_user(
            username='unverified', password='pass1234',
        )
        user_unverified.ent_user_profile.role_code = 'enterprise_admin'
        user_unverified.ent_user_profile.enterprise_id = unverified_ent.id
        user_unverified.ent_user_profile.save()

        self.client.force_authenticate(user=user_unverified)
        response = self.client.post(self._get_url(self.opp.id))
        data = response.json()
        self.assertEqual(data['code'], 403)

    def test_offline_opportunity_cannot_get_contact(self):
        """Cannot get contact info for an OFFLINE opportunity."""
        self.opp.status = Opportunity.OppStatus.OFFLINE
        self.opp.save(update_fields=['status', 'updated_at'])

        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self._get_url(self.opp.id))
        data = response.json()
        self.assertEqual(data['code'], 400)

    def test_nonexistent_opportunity_returns_404(self):
        """Request for non-existent opportunity should return 404."""
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(self._get_url(99999))
        data = response.json()
        self.assertEqual(data['code'], 404)
