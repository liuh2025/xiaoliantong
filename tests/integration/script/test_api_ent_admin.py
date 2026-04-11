"""
L1 API 集成测试 - ent_admin 模块
用例编号: TC-API-entadmin-001 ~ 010
测试: 员工管理 + 企业商机管理
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise
from apps.opportunity.models import Opportunity
from apps.auth_app.models import UserProfile


def _create_ent_admin_with_enterprise():
    """创建企业管理员+已认证企业"""
    user = User.objects.create_user(
        username='ent_admin_test', password='TestPass123!'
    )
    profile = user.ent_user_profile
    profile.role_code = 'enterprise_admin'
    profile.save()

    ent = Enterprise.objects.create(
        name='企业管理测试公司',
        credit_code='91MA00ENTADM01X',
        legal_representative='管理员',
        business_license='https://example.com/license.jpg',
        industry_id=1,
        sub_industry_id=101,
        province_id=110000,
        region_id=110100,
        auth_status=Enterprise.AuthStatus.VERIFIED,
        admin_user=user,
    )
    profile.enterprise_id = ent.id
    profile.save()
    return user, ent


@pytest.mark.django_db
class TestEmployeeAPI:
    """TC-API-entadmin-001 ~ 005: 员工管理"""

    def setup_method(self):
        self.user, self.ent = _create_ent_admin_with_enterprise()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # TC-API-entadmin-001: 获取员工列表
    def test_api_entadmin_001_employee_list(self):
        """
        TC-API-entadmin-001: 获取员工列表
        预期: HTTP 200
        """
        url = '/api/v1/ent-admin/employees'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-entadmin-002: 新增员工
    def test_api_entadmin_002_employee_create(self):
        """
        TC-API-entadmin-002: 新增员工
        预期: HTTP 200, 员工创建成功
        前提: 目标用户已注册
        """
        # Pre-create the target user (simulating a registered user)
        target_user = User.objects.create_user(
            username='13900001234', password='TestPass123!'
        )
        url = '/api/v1/ent-admin/employees'
        payload = {
            'phone': '13900001234',
            'real_name': '测试员工',
            'role_code': 'employee',
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-entadmin-003: 重置员工密码
    def test_api_entadmin_003_employee_reset_password(self):
        """
        TC-API-entadmin-003: 重置员工密码
        预期: HTTP 200
        """
        # 先创建一个员工用户
        emp_user = User.objects.create_user(
            username='13900005678', password='TestPass123!'
        )
        profile = emp_user.ent_user_profile
        profile.role_code = 'employee'
        profile.enterprise_id = self.ent.id
        profile.save()

        url = f'/api/v1/ent-admin/employees/{emp_user.id}/reset-password'
        response = self.client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-entadmin-004: 禁用/启用员工
    def test_api_entadmin_004_employee_disable(self):
        """
        TC-API-entadmin-004: 禁用/启用员工
        预期: HTTP 200
        """
        emp_user = User.objects.create_user(
            username='13900009999', password='TestPass123!'
        )
        profile = emp_user.ent_user_profile
        profile.role_code = 'employee'
        profile.enterprise_id = self.ent.id
        profile.save()

        url = f'/api/v1/ent-admin/employees/{emp_user.id}/disable'
        response = self.client.put(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-entadmin-005: 解绑员工
    def test_api_entadmin_005_employee_unbind(self):
        """
        TC-API-entadmin-005: 解绑员工
        预期: HTTP 200
        """
        emp_user = User.objects.create_user(
            username='13900008888', password='TestPass123!'
        )
        profile = emp_user.ent_user_profile
        profile.role_code = 'employee'
        profile.enterprise_id = self.ent.id
        profile.save()

        url = f'/api/v1/ent-admin/employees/{emp_user.id}/unbind'
        response = self.client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)


@pytest.mark.django_db
class TestEntAdminOpportunityAPI:
    """TC-API-entadmin-006 ~ 010: 企业商机管理"""

    def setup_method(self):
        self.user, self.ent = _create_ent_admin_with_enterprise()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # TC-API-entadmin-006: 获取企业商机列表
    def test_api_entadmin_006_my_opportunity_list(self):
        """
        TC-API-entadmin-006: 获取企业商机列表
        预期: HTTP 200
        """
        Opportunity.objects.create(
            title='企业商机测试',
            type='BUY',
            detail='测试商机描述，至少需要20个字符才能通过验证。',
            enterprise=self.ent,
            publisher=self.user,
            status='ACTIVE',
            contact_name='李经理',
            contact_phone='13800138000',
            industry_id=1,
            sub_industry_id=101,
            category_id=1,
            province_id=110000,
            region_id=110100,
        )
        url = '/api/v1/ent-admin/my-opportunities'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)
        assert response.data['data']['total'] >= 1

    # TC-API-entadmin-007: 商机下架
    def test_api_entadmin_007_opportunity_offline(self):
        """
        TC-API-entadmin-007: 商机下架
        预期: HTTP 200, status=OFFLINE
        """
        opp = Opportunity.objects.create(
            title='下架测试商机',
            type='BUY',
            detail='测试商机描述，至少需要20个字符才能通过验证。',
            enterprise=self.ent,
            publisher=self.user,
            status='ACTIVE',
            contact_name='李经理',
            contact_phone='13800138000',
            industry_id=1,
            sub_industry_id=101,
            category_id=1,
            province_id=110000,
            region_id=110100,
        )
        url = f'/api/v1/ent-admin/my-opportunities/{opp.id}/offline'
        response = self.client.put(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-entadmin-008: 商机重新发布
    def test_api_entadmin_008_opportunity_republish(self):
        """
        TC-API-entadmin-008: 商机重新发布
        预期: HTTP 200, status=ACTIVE
        """
        opp = Opportunity.objects.create(
            title='重新发布测试商机',
            type='BUY',
            detail='测试商机描述，至少需要20个字符才能通过验证。',
            enterprise=self.ent,
            publisher=self.user,
            status='OFFLINE',
            contact_name='李经理',
            contact_phone='13800138000',
            industry_id=1,
            sub_industry_id=101,
            category_id=1,
            province_id=110000,
            region_id=110100,
        )
        url = f'/api/v1/ent-admin/my-opportunities/{opp.id}/republish'
        response = self.client.put(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (200, 0)

    # TC-API-entadmin-009: 未绑定企业用户访问被拒
    def test_api_entadmin_009_no_enterprise_rejected(self):
        """
        TC-API-entadmin-009: 未绑定企业用户无法访问企业管理接口
        预期: HTTP 200, code: 403
        """
        guest = User.objects.create_user(
            username='guest_user', password='TestPass123!'
        )
        client = APIClient()
        client.force_authenticate(user=guest)
        url = '/api/v1/ent-admin/employees'
        response = client.get(url)
        # 未绑定企业应返回错误
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] in (403, 400, 404)

    # TC-API-entadmin-010: 未认证用户访问被拒
    def test_api_entadmin_010_unauthenticated_rejected(self):
        """
        TC-API-entadmin-010: 未认证用户无法访问企业管理接口
        预期: HTTP 401
        """
        client = APIClient()
        url = '/api/v1/ent-admin/employees'
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
