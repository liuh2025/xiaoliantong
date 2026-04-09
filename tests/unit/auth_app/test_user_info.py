import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.auth_app.models import UserProfile


@pytest.mark.django_db
class TestCurrentUserInfoAPI:
    """AUTH-008: GET /auth/me 当前用户信息接口测试"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('current-user-info')

    def _create_user(self, phone='13800138000', password='TestPass123!',
                     real_name='', position=None, role_code='guest',
                     enterprise_id=None):
        """辅助方法：创建测试用户并返回 user 对象"""
        user = User.objects.create_user(username=phone, password=password)
        profile = user.ent_user_profile
        profile.real_name = real_name
        profile.position = position
        profile.role_code = role_code
        profile.enterprise_id = enterprise_id
        profile.save()
        return user

    def _authenticate(self, user):
        """辅助方法：为用户生成 JWT 并设置认证头"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
        )

    # ==================== 正例测试 ====================

    def test_authenticated_user_with_enterprise(self):
        """已认证用户（已绑定企业）- 返回完整用户信息"""
        user = self._create_user(
            phone='13800138000',
            real_name='张三',
            position='总经理',
            role_code='enterprise_admin',
            enterprise_id=1,
        )
        self._authenticate(user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 0
        assert data['message'] == 'success'
        user_data = data['data']
        assert user_data['id'] == user.id
        assert user_data['phone'] == '13800138000'
        assert user_data['real_name'] == '张三'
        assert user_data['position'] == '总经理'
        assert user_data['role_code'] == 'enterprise_admin'
        assert user_data['enterprise_id'] == 1
        # ent 模块未开发，enterprise_name 和 enterprise_status 暂时返回 None
        assert user_data['enterprise_name'] is None
        assert user_data['enterprise_status'] is None

    def test_authenticated_user_without_enterprise(self):
        """已认证用户（未绑定企业）- enterprise 相关字段为 null"""
        user = self._create_user(
            phone='13900139000',
            real_name='李四',
            position='开发工程师',
            role_code='employee',
            enterprise_id=None,
        )
        self._authenticate(user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 0
        user_data = data['data']
        assert user_data['id'] == user.id
        assert user_data['phone'] == '13900139000'
        assert user_data['real_name'] == '李四'
        assert user_data['position'] == '开发工程师'
        assert user_data['role_code'] == 'employee'
        assert user_data['enterprise_id'] is None
        assert user_data['enterprise_name'] is None
        assert user_data['enterprise_status'] is None

    def test_user_with_default_values(self):
        """用户使用默认值（空 real_name、无 position、guest 角色）"""
        user = self._create_user(phone='13700137000')
        self._authenticate(user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        user_data = response.data['data']
        assert user_data['id'] == user.id
        assert user_data['phone'] == '13700137000'
        assert user_data['real_name'] == ''
        assert user_data['position'] is None
        assert user_data['role_code'] == 'guest'
        assert user_data['enterprise_id'] is None
        assert user_data['enterprise_name'] is None
        assert user_data['enterprise_status'] is None

    # ==================== 反例测试 ====================

    def test_unauthenticated_request(self):
        """未认证请求 - 返回 401"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self):
        """无效 token - 返回 401"""
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer invalid_token_value'
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_authorization_header(self):
        """缺少 Authorization 头 - 返回 401"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== 边界值测试 ====================

    def test_response_contains_all_required_fields(self):
        """验证响应包含所有必需字段"""
        user = self._create_user(
            phone='13800138001',
            real_name='王五',
            position='产品经理',
            role_code='enterprise_admin',
            enterprise_id=5,
        )
        self._authenticate(user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        user_data = response.data['data']
        required_fields = [
            'id', 'phone', 'real_name', 'position',
            'role_code', 'enterprise_id', 'enterprise_name',
            'enterprise_status',
        ]
        for field in required_fields:
            assert field in user_data, f"Missing required field: {field}"

    def test_guest_role_user(self):
        """guest 角色用户也能正常获取信息"""
        user = self._create_user(
            phone='13600136000',
            role_code='guest',
        )
        self._authenticate(user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['role_code'] == 'guest'

    def test_platform_operator_role(self):
        """platform_operator 角色用户"""
        user = self._create_user(
            phone='13500135000',
            real_name='平台运营',
            role_code='platform_operator',
        )
        self._authenticate(user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['role_code'] == 'platform_operator'
        assert response.data['data']['real_name'] == '平台运营'

    def test_super_admin_role(self):
        """super_admin 角色用户"""
        user = self._create_user(
            phone='13400134000',
            real_name='超级管理员',
            role_code='super_admin',
        )
        self._authenticate(user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['role_code'] == 'super_admin'

    def test_enterprise_id_various_values(self):
        """enterprise_id 可以是各种整数值"""
        user = self._create_user(
            phone='13300133000',
            enterprise_id=999,
        )
        self._authenticate(user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['enterprise_id'] == 999

    def test_get_method_only(self):
        """POST 方法不被允许"""
        user = self._create_user()
        self._authenticate(user)

        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
