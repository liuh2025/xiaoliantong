import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestTokenRefreshAPI:
    """AUTH-007: Token刷新接口测试"""

    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/v1/auth/refresh'
        self.user = User.objects.create_user(
            username='13800138000', password='testpass123'
        )

    def _get_tokens(self):
        """辅助方法：为测试用户生成 token 对"""
        refresh = RefreshToken.for_user(self.user)
        return str(refresh), str(refresh.access_token)

    # ==================== 正例测试 ====================

    def test_refresh_success(self):
        """使用有效 refresh_token 刷新成功，返回新 access_token 和 refresh_token"""
        refresh_token, _ = self._get_tokens()

        response = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 0
        assert data['message'] == 'success'
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        # 新 token 不应为空
        assert data['data']['access_token'] is not None
        assert data['data']['refresh_token'] is not None

    def test_refresh_returns_new_tokens(self):
        """刷新后返回的 token 应与原始 token 不同（ROTATE_REFRESH_TOKENS=True）"""
        refresh_token, old_access = self._get_tokens()

        response = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })

        assert response.status_code == status.HTTP_200_OK
        # 新的 refresh_token 应不同于旧的
        assert response.data['data']['refresh_token'] != refresh_token
        # 新的 access_token 也应不同于旧的
        assert response.data['data']['access_token'] != old_access

    # ==================== 反例测试 ====================

    def test_refresh_with_invalid_token(self):
        """使用无效 token 刷新失败"""
        response = self.client.post(self.url, {
            'refresh_token': 'invalid.token.value',
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_with_missing_field(self):
        """请求体缺少 refresh_token 字段"""
        response = self.client.post(self.url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refresh_with_empty_token(self):
        """使用空字符串 token 刷新"""
        response = self.client.post(self.url, {
            'refresh_token': '',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refresh_with_blacklisted_token(self):
        """使用已黑名单的 refresh_token 刷新失败"""
        refresh_token, _ = self._get_tokens()

        # 将 token 加入黑名单
        token = RefreshToken(refresh_token)
        token.blacklist()

        response = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_old_refresh_token_unusable_after_rotation(self):
        """刷新后旧 refresh_token 不可再次使用（BLACKLIST_AFTER_ROTATION=True）"""
        refresh_token, _ = self._get_tokens()

        # 第一次刷新成功
        response1 = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })
        assert response1.status_code == status.HTTP_200_OK

        # 使用旧 refresh_token 再次刷新应失败
        response2 = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_rejects_old_field_name(self):
        """请求体使用旧字段名 refresh 应失败（DESN 要求使用 refresh_token）"""
        refresh_token, _ = self._get_tokens()

        response = self.client.post(self.url, {
            'refresh': refresh_token,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutAPI:
    """AUTH-007: 登出接口测试"""

    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/v1/auth/logout'
        self.user = User.objects.create_user(
            username='13800138000', password='testpass123'
        )

    def _get_tokens(self):
        """辅助方法：为测试用户生成 token 对"""
        refresh = RefreshToken.for_user(self.user)
        return str(refresh), str(refresh.access_token)

    def _authenticate_client(self):
        """辅助方法：使用 access_token 认证客户端"""
        _, access_token = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # ==================== 正例测试 ====================

    def test_logout_success(self):
        """登出成功，refresh_token 被加入黑名单"""
        refresh_token, access_token = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 0
        assert data['message'] == '登出成功'
        assert data['data'] == {}

    def test_logout_blacklists_token(self):
        """登出后 refresh_token 不可再用于刷新"""
        refresh_token, access_token = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 先登出
        self.client.post(self.url, {
            'refresh_token': refresh_token,
        })

        # 再用同一 refresh_token 尝试刷新，应该失败
        self.client.credentials()  # 清除认证头
        response = self.client.post('/api/v1/auth/refresh', {
            'refresh_token': refresh_token,
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== 反例测试 ====================

    def test_logout_requires_authentication(self):
        """未认证用户登出应返回 401"""
        refresh_token, _ = self._get_tokens()

        response = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_with_invalid_token(self):
        """使用无效 token 登出"""
        self._authenticate_client()

        response = self.client.post(self.url, {
            'refresh_token': 'invalid.token.value',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_with_missing_field(self):
        """请求体缺少 refresh_token 字段"""
        self._authenticate_client()

        response = self.client.post(self.url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_with_empty_token(self):
        """使用空字符串 token 登出"""
        self._authenticate_client()

        response = self.client.post(self.url, {
            'refresh_token': '',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_with_access_token(self):
        """使用 access_token（非 refresh_token）登出应失败"""
        _, access_token = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.post(self.url, {
            'refresh_token': access_token,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_double_logout_same_token(self):
        """重复登出同一 token 应失败（已黑名单）"""
        refresh_token, access_token = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 第一次登出成功
        response1 = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })
        assert response1.status_code == status.HTTP_200_OK

        # 第二次登出应失败
        response2 = self.client.post(self.url, {
            'refresh_token': refresh_token,
        })
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
