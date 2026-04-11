"""PLAT-005: Opportunity content management tests."""
import itertools

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile
from apps.opportunity.models import Opportunity
from apps.msg.models import Message

_counter = itertools.count(200500)


def _unique_int():
    return next(_counter)


def build_enterprise(**overrides):
    n = _unique_int()
    defaults = {
        'name': f'Test Enterprise {n}',
        'credit_code': f'91{n:014d}X',
        'legal_representative': 'Zhang San',
        'business_license': f'https://example.com/license/test{n}.jpg',
        'industry_id': 1,
        'sub_industry_id': 101,
        'province_id': 110000,
        'region_id': 110100,
        'auth_status': Enterprise.AuthStatus.VERIFIED,
    }
    defaults.update(overrides)
    ent = Enterprise(**defaults)
    ent.save()
    return ent


def build_user(**overrides):
    n = _unique_int()
    defaults = {'username': f'testuser_{n}', 'password': 'testpass123'}
    defaults.update(overrides)
    return User.objects.create_user(**defaults)


def setup_profile(user, **kwargs):
    profile = user.ent_user_profile
    for key, value in kwargs.items():
        setattr(profile, key, value)
    profile.save()
    return profile


@pytest.mark.django_db
class TestContentOpportunityList:
    """Tests for GET /api/v1/plat-admin/content/opportunity."""

    def setup_method(self):
        self.url = reverse('plat_admin:content-opportunity-list')

    def test_list_opportunities(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        Opportunity.objects.create(
            type=Opportunity.OppType.BUY,
            title='Test Opportunity',
            enterprise=ent,
            publisher=user,
            industry_id=1,
            sub_industry_id=2,
            category_id=3,
            province_id=4,
            region_id=5,
            detail='Test detail',
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.data['data']['total'] >= 1

    def test_list_filter_by_type(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        Opportunity.objects.create(
            type=Opportunity.OppType.BUY, title='Buy Opp',
            enterprise=ent, publisher=user,
            industry_id=1, sub_industry_id=2, category_id=3,
            province_id=4, region_id=5, detail='d',
        )
        Opportunity.objects.create(
            type=Opportunity.OppType.SUPPLY, title='Supply Opp',
            enterprise=ent, publisher=user,
            industry_id=1, sub_industry_id=2, category_id=3,
            province_id=4, region_id=5, detail='d',
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'type': 'BUY'})
        items = response.data['data']['items']
        for item in items:
            assert item['type'] == 'BUY'

    def test_list_filter_by_status(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        Opportunity.objects.create(
            type=Opportunity.OppType.BUY, title='Active',
            enterprise=ent, publisher=user,
            industry_id=1, sub_industry_id=2, category_id=3,
            province_id=4, region_id=5, detail='d',
            status=Opportunity.OppStatus.ACTIVE,
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'status': 'ACTIVE'})
        items = response.data['data']['items']
        for item in items:
            assert item['status'] == 'ACTIVE'

    def test_list_keyword_search(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        Opportunity.objects.create(
            type=Opportunity.OppType.BUY, title='UniqueKeyword Opp',
            enterprise=ent, publisher=user,
            industry_id=1, sub_industry_id=2, category_id=3,
            province_id=4, region_id=5, detail='d',
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'keyword': 'UniqueKeyword'})
        assert response.data['data']['total'] >= 1


@pytest.mark.django_db
class TestContentOpportunityDetail:
    """Tests for GET /api/v1/plat-admin/content/opportunity/{id}."""

    def test_detail(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        opp = Opportunity.objects.create(
            type=Opportunity.OppType.BUY, title='Detail Opp',
            enterprise=ent, publisher=user,
            industry_id=1, sub_industry_id=2, category_id=3,
            province_id=4, region_id=5, detail='Full detail',
        )
        url = reverse(
            'plat_admin:content-opportunity-detail',
            kwargs={'pk': opp.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 200
        assert response.data['data']['title'] == 'Detail Opp'

    def test_detail_not_found(self, api_client, platform_admin):
        url = reverse(
            'plat_admin:content-opportunity-detail',
            kwargs={'pk': 99999},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 404


@pytest.mark.django_db
class TestContentOpportunityOffline:
    """Tests for PUT /api/v1/plat-admin/content/opportunity/{id}/offline."""

    def test_offline_opportunity(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        opp = Opportunity.objects.create(
            type=Opportunity.OppType.BUY, title='Offline Opp',
            enterprise=ent, publisher=user,
            industry_id=1, sub_industry_id=2, category_id=3,
            province_id=4, region_id=5, detail='d',
            status=Opportunity.OppStatus.ACTIVE,
        )
        url = reverse(
            'plat_admin:content-opportunity-offline',
            kwargs={'pk': opp.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'reason': 'Violation of rules'})
        assert response.data['code'] == 200

        opp.refresh_from_db()
        assert opp.status == Opportunity.OppStatus.OFFLINE

        # Verify notification
        assert Message.objects.filter(
            receiver=user, type='SYSTEM', title='商机被强制下架',
        ).exists()

    def test_offline_already_offline(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, enterprise_id=ent.id)
        opp = Opportunity.objects.create(
            type=Opportunity.OppType.BUY, title='Offline Opp',
            enterprise=ent, publisher=user,
            industry_id=1, sub_industry_id=2, category_id=3,
            province_id=4, region_id=5, detail='d',
            status=Opportunity.OppStatus.OFFLINE,
        )
        url = reverse(
            'plat_admin:content-opportunity-offline',
            kwargs={'pk': opp.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'reason': 'test'})
        assert response.data['code'] == 400
