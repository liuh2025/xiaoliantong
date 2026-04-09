"""PLAT-003: Enterprise audit tests."""
import itertools

import pytest
from django.urls import reverse
from apps.enterprise.models import Enterprise, AuditRecord
from apps.auth_app.models import UserProfile
from apps.msg.models import Message

_counter = itertools.count(200300)


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
        'auth_status': Enterprise.AuthStatus.PENDING,
    }
    defaults.update(overrides)
    ent = Enterprise(**defaults)
    ent.save()
    return ent


def build_user(**overrides):
    n = _unique_int()
    from django.contrib.auth.models import User
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
class TestAuditEnterpriseList:
    """Tests for GET /api/v1/plat-admin/audit/enterprise."""

    def setup_method(self):
        self.url = reverse('plat_admin:audit-enterprise-list')

    def test_list_audit_records(self, api_client, platform_admin):
        ent = build_enterprise(auth_status=Enterprise.AuthStatus.PENDING)
        AuditRecord.objects.create(
            enterprise=ent, status=AuditRecord.AuditStatus.PENDING,
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data['data']['total'] >= 1

    def test_list_filter_by_status(self, api_client, platform_admin):
        ent1 = build_enterprise(auth_status=Enterprise.AuthStatus.PENDING)
        ent2 = build_enterprise(auth_status=Enterprise.AuthStatus.VERIFIED)
        AuditRecord.objects.create(
            enterprise=ent1, status=AuditRecord.AuditStatus.PENDING,
        )
        AuditRecord.objects.create(
            enterprise=ent2, status=AuditRecord.AuditStatus.APPROVED,
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'status': 'PENDING'})
        items = response.data['data']['items']
        for item in items:
            assert item['status'] == 'PENDING'

    def test_list_filter_by_keyword(self, api_client, platform_admin):
        ent = build_enterprise(name='UniqueName Corp')
        AuditRecord.objects.create(
            enterprise=ent, status=AuditRecord.AuditStatus.PENDING,
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'keyword': 'UniqueName'})
        assert response.data['data']['total'] >= 1

    def test_list_pagination(self, api_client, platform_admin):
        for i in range(3):
            ent = build_enterprise()
            AuditRecord.objects.create(
                enterprise=ent, status=AuditRecord.AuditStatus.PENDING,
            )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'page': 1, 'page_size': 2})
        assert response.data['data']['page_size'] == 2
        assert len(response.data['data']['items']) == 2


@pytest.mark.django_db
class TestAuditEnterpriseApprove:
    """Tests for POST /api/v1/plat-admin/audit/enterprise/{id}/approve."""

    def test_approve_audit(self, api_client, platform_admin):
        ent = build_enterprise(auth_status=Enterprise.AuthStatus.PENDING)
        admin_user = build_user()
        setup_profile(admin_user, role_code='employee', enterprise_id=ent.id)
        ent.admin_user = admin_user
        ent.save()

        audit = AuditRecord.objects.create(
            enterprise=ent, status=AuditRecord.AuditStatus.PENDING,
        )

        url = reverse('plat_admin:audit-enterprise-approve', kwargs={'pk': audit.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url)

        assert response.data['code'] == 200

        # Verify status changes
        audit.refresh_from_db()
        assert audit.status == AuditRecord.AuditStatus.APPROVED

        ent.refresh_from_db()
        assert ent.auth_status == Enterprise.AuthStatus.VERIFIED

        # Verify role updated
        profile = UserProfile.objects.get(user=admin_user)
        assert profile.role_code == 'enterprise_admin'

        # Verify notification sent
        assert Message.objects.filter(
            receiver=admin_user, type='AUDIT_APPROVED',
        ).exists()

    def test_approve_non_pending_returns_error(self, api_client, platform_admin):
        ent = build_enterprise()
        audit = AuditRecord.objects.create(
            enterprise=ent, status=AuditRecord.AuditStatus.APPROVED,
        )

        url = reverse('plat_admin:audit-enterprise-approve', kwargs={'pk': audit.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url)
        assert response.data['code'] == 400

    def test_approve_nonexistent_returns_404(self, api_client, platform_admin):
        url = reverse('plat_admin:audit-enterprise-approve', kwargs={'pk': 99999})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url)
        assert response.data['code'] == 404


@pytest.mark.django_db
class TestAuditEnterpriseReject:
    """Tests for POST /api/v1/plat-admin/audit/enterprise/{id}/reject."""

    def test_reject_audit(self, api_client, platform_admin):
        ent = build_enterprise(auth_status=Enterprise.AuthStatus.PENDING)
        admin_user = build_user()
        setup_profile(admin_user, enterprise_id=ent.id)
        ent.admin_user = admin_user
        ent.save()

        audit = AuditRecord.objects.create(
            enterprise=ent, status=AuditRecord.AuditStatus.PENDING,
        )

        url = reverse('plat_admin:audit-enterprise-reject', kwargs={'pk': audit.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url, {'reason': 'Incomplete documents'})

        assert response.data['code'] == 200

        audit.refresh_from_db()
        assert audit.status == AuditRecord.AuditStatus.REJECTED
        assert audit.audit_reason == 'Incomplete documents'

        ent.refresh_from_db()
        assert ent.auth_status == Enterprise.AuthStatus.REJECTED

        # Verify notification sent
        assert Message.objects.filter(
            receiver=admin_user, type='AUDIT_REJECTED',
        ).exists()

    def test_reject_without_reason_returns_error(self, api_client, platform_admin):
        ent = build_enterprise()
        audit = AuditRecord.objects.create(
            enterprise=ent, status=AuditRecord.AuditStatus.PENDING,
        )

        url = reverse('plat_admin:audit-enterprise-reject', kwargs={'pk': audit.id})
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url, {})
        assert response.data['code'] == 400
