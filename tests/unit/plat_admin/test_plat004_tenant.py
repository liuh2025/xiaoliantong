"""PLAT-004: Tenant management tests."""
import itertools

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise
from apps.auth_app.models import UserProfile

_counter = itertools.count(200400)


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
class TestTenantEnterpriseList:
    """Tests for GET /api/v1/plat-admin/tenant/enterprise."""

    def setup_method(self):
        self.url = reverse('plat_admin:tenant-enterprise-list')

    def test_list_enterprises(self, api_client, platform_admin):
        build_enterprise()
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data['data']['total'] >= 1

    def test_list_filter_by_keyword(self, api_client, platform_admin):
        build_enterprise(name='KeywordSearch Corp')
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'keyword': 'KeywordSearch'})
        assert response.data['data']['total'] >= 1

    def test_list_filter_by_status(self, api_client, platform_admin):
        build_enterprise(auth_status=Enterprise.AuthStatus.VERIFIED)
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'status': 'VERIFIED'})
        items = response.data['data']['items']
        for item in items:
            assert item['auth_status'] == 'VERIFIED'

    def test_list_filter_by_is_active(self, api_client, platform_admin):
        build_enterprise(is_active=True)
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'is_active': 'true'})
        items = response.data['data']['items']
        for item in items:
            assert item['is_active'] is True

    def test_list_pagination(self, api_client, platform_admin):
        for i in range(3):
            build_enterprise()
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'page': 1, 'page_size': 2})
        assert len(response.data['data']['items']) == 2

    def test_list_fields(self, api_client, platform_admin):
        build_enterprise()
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        item = response.data['data']['items'][0]
        expected_fields = [
            'id', 'name', 'logo_url', 'industry_name',
            'auth_status', 'admin_name', 'member_count',
            'created_at', 'is_active',
        ]
        for field in expected_fields:
            assert field in item


@pytest.mark.django_db
class TestTenantEnterpriseDetail:
    """Tests for GET /api/v1/plat-admin/tenant/enterprise/{id}."""

    def test_detail_with_members(self, api_client, platform_admin):
        ent = build_enterprise()
        user1 = build_user()
        setup_profile(user1, role_code='employee', enterprise_id=ent.id)
        user2 = build_user()
        setup_profile(user2, role_code='employee', enterprise_id=ent.id)

        url = reverse('plat_admin:tenant-enterprise-detail', kwargs={'pk': ent.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 200
        assert 'members' in response.data['data']
        assert len(response.data['data']['members']) == 2

    def test_detail_not_found(self, api_client, platform_admin):
        url = reverse('plat_admin:tenant-enterprise-detail', kwargs={'pk': 99999})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 404


@pytest.mark.django_db
class TestTenantEnterpriseToggleStatus:
    """Tests for PUT /api/v1/plat-admin/tenant/enterprise/{id}/toggle-status."""

    def test_toggle_status(self, api_client, platform_admin):
        ent = build_enterprise(is_active=True)

        url = reverse(
            'plat_admin:tenant-enterprise-toggle-status',
            kwargs={'pk': ent.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url)
        assert response.data['code'] == 200
        assert response.data['data']['is_active'] is False

        # Toggle back
        response = api_client.put(url)
        assert response.data['data']['is_active'] is True


@pytest.mark.django_db
class TestTenantMemberList:
    """Tests for GET/POST /api/v1/plat-admin/tenant/enterprise/{id}/member."""

    def test_get_members(self, api_client, platform_admin):
        ent = build_enterprise()
        user1 = build_user()
        setup_profile(user1, role_code='employee', enterprise_id=ent.id, real_name='Emp1')

        url = reverse('plat_admin:tenant-member-list', kwargs={'pk': ent.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(url)
        assert response.data['code'] == 200
        assert len(response.data['data']['items']) == 1

    def test_add_member(self, api_client, platform_admin):
        ent = build_enterprise()
        n = _unique_int()
        phone = f'138{n:07d}'
        target_user = build_user(username=phone)

        url = reverse('plat_admin:tenant-member-list', kwargs={'pk': ent.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url, {
            'phone': phone,
            'real_name': 'New Member',
            'role_code': 'employee',
        })
        assert response.data['code'] == 200

        profile = UserProfile.objects.get(user=target_user)
        assert profile.enterprise_id == ent.id
        assert profile.role_code == 'employee'

    def test_add_member_user_not_registered(self, api_client, platform_admin):
        ent = build_enterprise()

        url = reverse('plat_admin:tenant-member-list', kwargs={'pk': ent.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url, {
            'phone': '99999999999',
            'real_name': 'Test',
            'role_code': 'employee',
        })
        assert response.data['code'] == 400


@pytest.mark.django_db
class TestTenantMemberUpdate:
    """Tests for PUT /api/v1/plat-admin/tenant/member/{id}."""

    def test_update_member(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, role_code='employee', enterprise_id=ent.id, real_name='Old')

        url = reverse('plat_admin:tenant-member-detail', kwargs={'pk': user.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {
            'real_name': 'New Name',
            'position': 'Engineer',
        })
        assert response.data['code'] == 200

        profile = UserProfile.objects.get(user=user)
        assert profile.real_name == 'New Name'

    def test_update_member_not_found(self, api_client, platform_admin):
        url = reverse('plat_admin:tenant-member-detail', kwargs={'pk': 99999})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.put(url, {'real_name': 'Test'})
        assert response.data['code'] == 404


@pytest.mark.django_db
class TestTenantMemberResetPassword:
    """Tests for POST /api/v1/plat-admin/tenant/member/{id}/reset-password."""

    def test_reset_password(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user(username='13800001234')
        setup_profile(user, enterprise_id=ent.id)

        url = reverse(
            'plat_admin:tenant-member-reset-password',
            kwargs={'pk': user.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url)
        assert response.data['code'] == 200

        # Verify password changed
        user.refresh_from_db()
        assert user.check_password('001234')


@pytest.mark.django_db
class TestTenantMemberUnbind:
    """Tests for POST /api/v1/plat-admin/tenant/member/{id}/unbind."""

    def test_unbind_member(self, api_client, platform_admin):
        ent = build_enterprise()
        user = build_user()
        setup_profile(user, role_code='employee', enterprise_id=ent.id)

        url = reverse(
            'plat_admin:tenant-member-unbind',
            kwargs={'pk': user.id},
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url)
        assert response.data['code'] == 200

        profile = UserProfile.objects.get(user=user)
        assert profile.enterprise_id is None
        assert profile.role_code == 'guest'
