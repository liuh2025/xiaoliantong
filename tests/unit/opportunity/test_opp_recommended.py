"""Unit tests for OPP-009: Smart recommended opportunities API.

GET /api/v1/opp/opportunity/recommended
- Public access (AllowAny)
- Returns up to 4 recommended opportunities
- Excludes OFFLINE opportunities
- For logged-in users with enterprise, excludes own enterprise's opportunities
- Response format matches opportunity list
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.auth_app.models import UserProfile
from apps.enterprise.models import Enterprise, MasterData
from apps.opportunity.models import Opportunity


class OPP009RecommendedTests(TestCase):
    """Tests for OPP-009: Smart recommended opportunities."""

    def setUp(self):
        """Create shared test fixtures."""
        self.client = APIClient()
        self.url = '/api/v1/opp/opportunity/recommended'

        # Master data
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

        # Enterprise + publisher
        self.publisher = User.objects.create_user(
            username='publisher', password='pass1234',
        )
        self.enterprise = Enterprise.objects.create(
            name='Test Corp',
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

        # Create 4 BUY + 2 SUPPLY ACTIVE opportunities
        for i in range(4):
            Opportunity.objects.create(
                type=Opportunity.OppType.BUY,
                title=f'BUY Opportunity {i}',
                enterprise=self.enterprise,
                publisher=self.publisher,
                industry_id=self.industry.id,
                sub_industry_id=self.sub_industry.id,
                category_id=self.category.id,
                province_id=self.province.id,
                region_id=self.region.id,
                detail=f'Detail {i}',
                view_count=(4 - i) * 10,  # Varying view counts
                status=Opportunity.OppStatus.ACTIVE,
            )
        for i in range(2):
            Opportunity.objects.create(
                type=Opportunity.OppType.SUPPLY,
                title=f'SUPPLY Opportunity {i}',
                enterprise=self.enterprise,
                publisher=self.publisher,
                industry_id=self.industry.id,
                sub_industry_id=self.sub_industry.id,
                category_id=self.category.id,
                province_id=self.province.id,
                region_id=self.region.id,
                detail=f'Supply Detail {i}',
                view_count=(2 - i) * 5,
                status=Opportunity.OppStatus.ACTIVE,
            )

    # ===== Positive cases =====

    def test_guest_can_get_recommended_list(self):
        """Guest (unauthenticated) user can get recommended list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertIn('items', data['data'])
        self.assertIsInstance(data['data']['items'], list)

    def test_returns_up_to_4_items(self):
        """Should return at most 4 items."""
        response = self.client.get(self.url)
        data = response.json()
        self.assertLessEqual(len(data['data']['items']), 4)

    def test_offline_opportunities_excluded(self):
        """OFFLINE opportunities should not appear in recommendations."""
        Opportunity.objects.update(status=Opportunity.OppStatus.OFFLINE)
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(len(data['data']['items']), 0)

    def test_logged_in_with_enterprise_excludes_own(self):
        """Logged-in user with enterprise should not see own enterprise's opps."""
        # Create a second enterprise and user
        other_enterprise = Enterprise.objects.create(
            name='Other Corp',
            credit_code='987654321098765432',
            legal_representative='Other',
            business_license='http://example.com/license2.png',
            industry_id=self.industry.id,
            sub_industry_id=self.sub_industry.id,
            category_id=self.category.id,
            province_id=self.province.id,
            region_id=self.region.id,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        other_user = User.objects.create_user(
            username='other_user', password='pass1234',
        )
        other_user.ent_user_profile.role_code = 'enterprise_admin'
        other_user.ent_user_profile.enterprise_id = other_enterprise.id
        other_user.ent_user_profile.save()

        # All opportunities belong to self.enterprise, not other_enterprise
        # So other_user should see all of them
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        self.assertGreaterEqual(len(items), 1)

        # Now test: user from self.enterprise should see none
        # because all opps are published by self.enterprise
        user_same_ent = User.objects.create_user(
            username='same_ent_user', password='pass1234',
        )
        user_same_ent.ent_user_profile.role_code = 'employee'
        user_same_ent.ent_user_profile.enterprise_id = self.enterprise.id
        user_same_ent.ent_user_profile.save()

        self.client.force_authenticate(user=user_same_ent)
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        # All opps belong to self.enterprise, so user from same enterprise sees 0
        self.assertEqual(len(items), 0)

    def test_response_format_matches_list(self):
        """Response items should contain the same fields as list serializer."""
        response = self.client.get(self.url)
        data = response.json()
        items = data['data']['items']
        if items:
            item = items[0]
            expected_fields = {
                'id', 'type', 'title', 'enterprise_id', 'enterprise_name',
                'industry_name', 'sub_industry_name', 'category_name',
                'province_name', 'region_name', 'tags', 'view_count',
                'created_at',
            }
            self.assertTrue(
                expected_fields.issubset(set(item.keys())),
                f'Missing fields: {expected_fields - set(item.keys())}',
            )

    def test_no_active_opps_returns_empty_list(self):
        """When no active opportunities exist, should return empty list."""
        Opportunity.objects.all().delete()
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['items'], [])
