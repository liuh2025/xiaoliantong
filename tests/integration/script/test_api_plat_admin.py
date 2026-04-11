"""
L1 API 集成测试 - plat_admin 模块
用例编号: TC-API-platadmin-001 ~ 015
测试: 数据大盘、企业审核、租户管理、内容管理、基础数据字典
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise, MasterData, AuditRecord
from apps.opportunity.models import Opportunity
from apps.feed.models import Feed
from apps.auth_app.models import UserProfile


def _create_plat_admin():
    """创建平台管理员(superuser)"""
    user = User.objects.create_superuser(
        username='plat_admin_test',
        password='TestPass123!',
        email='admin@test.com',
    )
    profile = user.ent_user_profile
    profile.role_code = 'super_admin'
    profile.save()
    return user


def _create_verified_ent_with_admin(username='ent_for_audit'):
    """创建待审核企业+管理员"""
    user = User.objects.create_user(
        username=username, password='TestPass123!'
    )
    profile = user.ent_user_profile
    profile.role_code = 'enterprise_admin'
    profile.save()

    ent = Enterprise.objects.create(
        name=f'审核测试企业_{username}',
        credit_code=f'91MA00{username[:4]:0<6}X',
        legal_representative='法人代表',
        business_license='https://example.com/license.jpg',
        industry_id=1,
        sub_industry_id=101,
        province_id=110000,
        region_id=110100,
        auth_status=Enterprise.AuthStatus.PENDING,
        admin_user=user,
    )
    profile.enterprise_id = ent.id
    profile.save()

    # Create audit record
    audit = AuditRecord.objects.create(
        enterprise=ent,
        status=AuditRecord.AuditStatus.PENDING,
    )
    return user, ent, audit


@pytest.mark.django_db
class TestDashboardAPI:
    """TC-API-platadmin-001 ~ 002: 数据大盘"""

    def setup_method(self):
        admin = _create_plat_admin()
        self.client = APIClient()
        self.client.force_authenticate(user=admin)

    # TC-API-platadmin-001: 获取统计数据
    def test_api_platadmin_001_dashboard_stats(self):
        """
        TC-API-platadmin-001: 获取统计数据
        预期: HTTP 200, 含统计字段
        """
        url = '/api/v1/plat-admin/dashboard/stats'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-002: 获取趋势数据
    def test_api_platadmin_002_dashboard_trend(self):
        """
        TC-API-platadmin-002: 获取趋势数据
        预期: HTTP 200
        """
        url = '/api/v1/plat-admin/dashboard/trend'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)


@pytest.mark.django_db
class TestAuditAPI:
    """TC-API-platadmin-003 ~ 006: 企业审核"""

    def setup_method(self):
        self.admin = _create_plat_admin()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    # TC-API-platadmin-003: 获取审核列表
    def test_api_platadmin_003_audit_list(self):
        """
        TC-API-platadmin-003: 获取审核列表
        预期: HTTP 200
        """
        _create_verified_ent_with_admin('audit_ent_list')
        url = '/api/v1/plat-admin/audit/enterprise'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-004: 审核列表筛选
    def test_api_platadmin_004_audit_list_filter(self):
        """
        TC-API-platadmin-004: 审核列表按状态筛选
        预期: HTTP 200
        """
        url = '/api/v1/plat-admin/audit/enterprise'
        response = self.client.get(url, {'status': 'PENDING'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-005: 审核驳回
    def test_api_platadmin_005_audit_reject(self):
        """
        TC-API-platadmin-005: 审核驳回企业
        预期: HTTP 200, 企业状态变为REJECTED
        """
        _, ent, audit = _create_verified_ent_with_admin('reject_ent')
        url = f'/api/v1/plat-admin/audit/enterprise/{audit.id}/reject'
        response = self.client.post(url, {'reason': '材料不完整'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)
        ent.refresh_from_db()
        assert ent.auth_status == Enterprise.AuthStatus.REJECTED

    # TC-API-platadmin-006: 审核通过
    def test_api_platadmin_006_audit_approve(self):
        """
        TC-API-platadmin-006: 审核通过企业
        预期: HTTP 200, 企业状态变为VERIFIED
        """
        _, ent, audit = _create_verified_ent_with_admin('approve_ent')
        url = f'/api/v1/plat-admin/audit/enterprise/{audit.id}/approve'
        response = self.client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)
        ent.refresh_from_db()
        assert ent.auth_status == Enterprise.AuthStatus.VERIFIED


@pytest.mark.django_db
class TestTenantAPI:
    """TC-API-platadmin-007 ~ 009: 租户管理"""

    def setup_method(self):
        self.admin = _create_plat_admin()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    # TC-API-platadmin-007: 获取租户列表
    def test_api_platadmin_007_tenant_list(self):
        """
        TC-API-platadmin-007: 获取租户(企业)列表
        预期: HTTP 200
        """
        _create_verified_ent_with_admin('tenant_ent')
        url = '/api/v1/plat-admin/tenant/enterprise'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-008: 获取租户详情
    def test_api_platadmin_008_tenant_detail(self):
        """
        TC-API-platadmin-008: 获取租户详情
        预期: HTTP 200
        """
        _, ent, _ = _create_verified_ent_with_admin('tenant_detail')
        url = f'/api/v1/plat-admin/tenant/enterprise/{ent.id}'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-009: 租户启停
    def test_api_platadmin_009_tenant_toggle_status(self):
        """
        TC-API-platadmin-009: 租户启停切换
        预期: HTTP 200
        """
        _, ent, _ = _create_verified_ent_with_admin('tenant_toggle')
        url = f'/api/v1/plat-admin/tenant/enterprise/{ent.id}/toggle-status'
        response = self.client.put(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)


@pytest.mark.django_db
class TestContentAPI:
    """TC-API-platadmin-010 ~ 013: 内容管理"""

    def setup_method(self):
        self.admin = _create_plat_admin()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        # 创建测试数据
        user, ent, _ = _create_verified_ent_with_admin('content_ent')
        ent.auth_status = Enterprise.AuthStatus.VERIFIED
        ent.save()
        self.opp = Opportunity.objects.create(
            title='内容管理测试商机',
            type='BUY',
            detail='测试商机描述，至少需要20个字符才能通过验证。',
            enterprise=ent,
            publisher=user,
            status='ACTIVE',
            contact_name='张经理',
            contact_phone='13800138000',
            industry_id=1,
            sub_industry_id=101,
            category_id=1,
            province_id=110000,
            region_id=110100,
        )
        self.feed = Feed.objects.create(
            publisher=user,
            enterprise=ent,
            content='内容管理测试动态，这是一条测试动态。',
            status='ACTIVE',
        )

    # TC-API-platadmin-010: 商机内容列表
    def test_api_platadmin_010_content_opportunity_list(self):
        """
        TC-API-platadmin-010: 商机内容列表
        预期: HTTP 200
        """
        url = '/api/v1/plat-admin/content/opportunity'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-011: 商机强制下架
    def test_api_platadmin_011_content_opportunity_offline(self):
        """
        TC-API-platadmin-011: 商机强制下架
        预期: HTTP 200
        """
        url = f'/api/v1/plat-admin/content/opportunity/{self.opp.id}/offline'
        response = self.client.put(url, {'reason': '违规内容'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-012: 动态内容列表
    def test_api_platadmin_012_content_feed_list(self):
        """
        TC-API-platadmin-012: 动态内容列表
        预期: HTTP 200
        """
        url = '/api/v1/plat-admin/content/feed'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-013: 动态强制下架
    def test_api_platadmin_013_content_feed_offline(self):
        """
        TC-API-platadmin-013: 动态强制下架
        预期: HTTP 200
        """
        url = f'/api/v1/plat-admin/content/feed/{self.feed.id}/offline'
        response = self.client.put(url, {'reason': '不合规内容'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)


@pytest.mark.django_db
class TestMasterDataAPI:
    """TC-API-platadmin-014 ~ 015: 基础数据字典"""

    def setup_method(self):
        self.admin = _create_plat_admin()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    # TC-API-platadmin-014: 获取基础数据列表
    def test_api_platadmin_014_master_data_list(self):
        """
        TC-API-platadmin-014: 获取基础数据列表
        预期: HTTP 200
        """
        MasterData.objects.create(
            category='industry', name='测试行业', code='IND-PLAT', parent_id=0
        )
        url = '/api/v1/plat-admin/master-data'
        response = self.client.get(url, {'category': 'industry'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-platadmin-015: 创建基础数据
    def test_api_platadmin_015_master_data_create(self):
        """
        TC-API-platadmin-015: 创建基础数据
        预期: HTTP 200
        """
        url = '/api/v1/plat-admin/master-data'
        payload = {
            'category': 'industry',
            'name': '新建行业',
            'code': 'IND-NEW',
            'parent_id': 0,
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)
        assert MasterData.objects.filter(code='IND-NEW').exists()

    # TC-API-platadmin-016: 非管理员访问被拒
    def test_api_platadmin_016_non_admin_rejected(self):
        """
        TC-API-platadmin-016: 非管理员访问被拒
        预期: HTTP 403
        """
        guest = User.objects.create_user(
            username='guest_plat', password='TestPass123!'
        )
        client = APIClient()
        client.force_authenticate(user=guest)
        url = '/api/v1/plat-admin/dashboard/stats'
        response = client.get(url)
        # 非管理员应被拒绝(403或401)
        assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED)
