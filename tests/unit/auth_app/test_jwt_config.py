import pytest
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from apps.auth_app.serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()

@pytest.mark.django_db
class TestJWTConfig:
    def test_jwt_settings(self):
        """测试 JWT 的配置项是否符合要求"""
        assert getattr(settings, 'SIMPLE_JWT', None) is not None
        
        jwt_settings = settings.SIMPLE_JWT
        assert jwt_settings.get('ACCESS_TOKEN_LIFETIME') == timedelta(hours=2)
        assert jwt_settings.get('REFRESH_TOKEN_LIFETIME') == timedelta(days=7)
        assert jwt_settings.get('ROTATE_REFRESH_TOKENS') is True
        assert jwt_settings.get('BLACKLIST_AFTER_ROTATION') is True

    def test_drf_authentication_classes(self):
        """测试 DRF 的默认认证类配置"""
        assert getattr(settings, 'REST_FRAMEWORK', None) is not None
        
        drf_settings = settings.REST_FRAMEWORK
        auth_classes = drf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        assert 'rest_framework_simplejwt.authentication.JWTAuthentication' in auth_classes

@pytest.mark.django_db
class TestCustomTokenObtainPairSerializer:
    def test_get_token_includes_custom_claims(self):
        """测试自定义的 Serializer 能否正确获取 token 并包含 role_code 和 permissions"""
        # 创建一个普通的测试用户
        user = User.objects.create_user(username='testuser', password='password123')

        # 使用自动创建的 ent_user_profile 进行修改
        profile = user.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.save()

        # 给用户对象添加 mock 属性，模拟扩展的权限
        user.permissions = ['read', 'write']

        # 获取 token
        token = CustomTokenObtainPairSerializer.get_token(user)

        # 验证自定义字段
        assert 'role_code' in token
        assert token['role_code'] == 'enterprise_admin'

        assert 'permissions' in token
        assert token['permissions'] == ['read', 'write']
