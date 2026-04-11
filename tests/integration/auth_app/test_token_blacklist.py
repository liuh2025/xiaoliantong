import pytest
from django.contrib.auth import get_user_model
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# We need to configure simple urls for the test client
urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    user = User.objects.create_user(username='blacklist_user', password='password123')
    return user

@pytest.mark.django_db
@pytest.mark.urls(__name__)
class TestTokenBlacklistIntegration:
    def test_token_rotation_and_blacklist(self, api_client, test_user):
        """测试 Token 刷新时旧 Token 是否被加入黑名单"""
        # 生成初始的 refresh token
        refresh = RefreshToken.for_user(test_user)
        refresh_token = str(refresh)
        
        # 使用旧的 refresh token 发起刷新请求
        response = api_client.post('/api/token/refresh/', {'refresh': refresh_token})
        
        # 断言刷新成功
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        
        new_refresh_token = response.data['refresh']
        assert new_refresh_token != refresh_token
        
        # 尝试再次使用旧的 refresh token 应该失败，因为它已被加入黑名单
        response_reused = api_client.post('/api/token/refresh/', {'refresh': refresh_token})
        
        # 应该返回 401 Unauthorized
        assert response_reused.status_code == 401
        assert response_reused.data['code'] == 'token_not_valid'
