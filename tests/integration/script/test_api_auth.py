"""
L1 API 集成测试 - auth 模块
用例编号: TC-API-auth-001 ~ TC-API-auth-026
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.auth_app.models import UserProfile, AuthSmsCode
from django.utils import timezone
from datetime import timedelta
from django.core.signing import TimestampSigner


@pytest.mark.django_db
class TestSmsSend:
    """TC-API-auth-001 ~ 006: 发送验证码"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('sms-send')

    # TC-API-auth-001: 发送登录验证码-成功
    def test_api_auth_001_sms_send_login_success(self):
        """
        TC-API-auth-001: 发送登录验证码-成功
        预期: HTTP 200, code: 0
        DB校验: sms_codes表有记录
        """
        response = self.client.post(self.url, {
            'phone': '13800001111',
            'type': 'login',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        assert AuthSmsCode.objects.filter(
            phone='13800001111', type='login'
        ).exists()

    # TC-API-auth-002: 发送登录验证码-超过每日限制
    def test_api_auth_002_sms_send_daily_limit(self):
        """
        TC-API-auth-002: 发送登录验证码-超过每日限制
        预期: HTTP 400, code: 400, 超出每日发送次数限制
        """
        now = timezone.now()
        for i in range(10):
            AuthSmsCode.objects.create(
                phone='13800002222',
                code='123456',
                type='login',
                expire_at=now + timedelta(minutes=5),
            )
        response = self.client.post(self.url, {
            'phone': '13800002222',
            'type': 'login',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '超出每日发送次数' in response.data['message']

    # TC-API-auth-003: 发送注册验证码-成功
    def test_api_auth_003_sms_send_register_success(self):
        """
        TC-API-auth-003: 发送注册验证码-成功
        预期: HTTP 200, code: 0, type=register
        """
        response = self.client.post(self.url, {
            'phone': '13900009999',
            'type': 'register',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        assert AuthSmsCode.objects.filter(
            phone='13900009999', type='register'
        ).exists()

    # TC-API-auth-004: 发送注册验证码-手机号已注册 (注册场景后端不校验)
    def test_api_auth_004_sms_send_register_existing_phone(self):
        """
        TC-API-auth-004: 发送注册验证码-手机号已注册
        预期: 后端不校验手机号是否已注册，直接发送成功
        实际行为: code: 0 (当前实现不区分注册/登录的手机号校验)
        """
        User.objects.create_user(username='13900008888', password='Test1234')
        response = self.client.post(self.url, {
            'phone': '13900008888',
            'type': 'register',
        }, format='json')
        # 后端当前不校验手机号是否已注册，直接发送
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0

    # TC-API-auth-005: 发送密码重置验证码-成功
    def test_api_auth_005_sms_send_password_reset_success(self):
        """
        TC-API-auth-005: 发送密码重置验证码-成功
        预期: HTTP 200, code: 0
        """
        response = self.client.post(self.url, {
            'phone': '13800001111',
            'type': 'password_reset',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0

    # TC-API-auth-006: 发送密码重置验证码-未注册手机 (发送时不校验)
    def test_api_auth_006_sms_send_password_reset_unregistered(self):
        """
        TC-API-auth-006: 发送密码重置验证码-未注册手机
        预期: 后端发送验证码时不校验手机号是否注册，直接发送
        实际行为: code: 0 (注册校验在后续步骤做)
        """
        response = self.client.post(self.url, {
            'phone': '13000000000',
            'type': 'password_reset',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0


@pytest.mark.django_db
class TestSmsLogin:
    """TC-API-auth-007 ~ 011: 短信验证码登录"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('sms-login')

    def _create_sms_code(self, phone='13800001111', code='123456', sms_type='login',
                          expired=False, used=False):
        now = timezone.now()
        expire_at = now - timedelta(minutes=1) if expired else now + timedelta(minutes=5)
        sms = AuthSmsCode.objects.create(
            phone=phone,
            code=code,
            type=sms_type,
            expire_at=expire_at,
            used_at=now if used else None,
        )
        return sms

    # TC-API-auth-007: 短信验证码登录-成功
    def test_api_auth_007_sms_login_success(self):
        """
        TC-API-auth-007: 短信验证码登录-成功
        预期: HTTP 200, code: 0, 含access_token和refresh_token
        DB校验: sms_codes.used_at != null
        """
        phone = '13800001111'
        sms = self._create_sms_code(phone=phone, code='654321')

        response = self.client.post(self.url, {
            'phone': phone,
            'code': '654321',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        data = response.data['data']
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['access_token'] != ''
        assert data['user_id'] is not None

        # DB校验: 验证码已标记为使用
        sms.refresh_from_db()
        assert sms.used_at is not None

    # TC-API-auth-008: 短信验证码登录-验证码错误
    def test_api_auth_008_sms_login_wrong_code(self):
        """
        TC-API-auth-008: 短信验证码登录-验证码错误
        预期: HTTP 400, 验证码错误
        """
        self._create_sms_code(code='654321')
        response = self.client.post(self.url, {
            'phone': '13800001111',
            'code': '000000',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '验证码错误' in response.data['message']

    # TC-API-auth-009: 短信验证码登录-验证码过期
    def test_api_auth_009_sms_login_expired_code(self):
        """
        TC-API-auth-009: 短信验证码登录-验证码过期
        预期: HTTP 400, 验证码无效或已过期
        """
        self._create_sms_code(expired=True)
        response = self.client.post(self.url, {
            'phone': '13800001111',
            'code': '123456',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '验证码无效或已过期' in response.data['message']

    # TC-API-auth-010: 短信验证码登录-验证码已使用
    def test_api_auth_010_sms_login_used_code(self):
        """
        TC-API-auth-010: 短信验证码登录-验证码已使用
        预期: HTTP 400, 验证码无效或已过期
        """
        self._create_sms_code(used=True)
        response = self.client.post(self.url, {
            'phone': '13800001111',
            'code': '123456',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '验证码无效或已过期' in response.data['message']

    # TC-API-auth-011: 短信验证码登录-手机号未注册(自动注册)
    def test_api_auth_011_sms_login_auto_register(self):
        """
        TC-API-auth-011: 短信验证码登录-手机号未注册
        预期: 短信登录会自动创建用户(get_or_create)
        实际行为: HTTP 200, code: 0, 自动注册新用户
        """
        phone = '13900009999'
        self._create_sms_code(phone=phone, code='888888')
        assert not User.objects.filter(username=phone).exists()

        response = self.client.post(self.url, {
            'phone': phone,
            'code': '888888',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        # 验证用户已自动创建
        assert User.objects.filter(username=phone).exists()


@pytest.mark.django_db
class TestPasswordLogin:
    """TC-API-auth-012 ~ 014: 账号密码登录"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('password-login')

    # TC-API-auth-012: 账号密码登录-成功
    def test_api_auth_012_password_login_success(self):
        """
        TC-API-auth-012: 账号密码登录-成功
        预期: HTTP 200, code: 0, 含JWT Token
        """
        User.objects.create_user(
            username='13800001111', password='TestPass123'
        )
        response = self.client.post(self.url, {
            'phone': '13800001111',
            'password': 'TestPass123',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        data = response.data['data']
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user_id'] is not None

    # TC-API-auth-013: 账号密码登录-密码错误
    def test_api_auth_013_password_login_wrong_password(self):
        """
        TC-API-auth-013: 账号密码登录-密码错误
        预期: HTTP 401, 手机号或密码错误
        """
        User.objects.create_user(
            username='13800001111', password='TestPass123'
        )
        response = self.client.post(self.url, {
            'phone': '13800001111',
            'password': 'WrongPass123',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert '手机号或密码错误' in response.data['message']

    # TC-API-auth-014: 账号密码登录-用户不存在
    def test_api_auth_014_password_login_user_not_exist(self):
        """
        TC-API-auth-014: 账号密码登录-用户不存在
        预期: HTTP 401, 手机号或密码错误
        """
        response = self.client.post(self.url, {
            'phone': '13000000000',
            'password': 'AnyPass123',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """TC-API-auth-015 ~ 017: Token刷新"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('token-refresh')

    # TC-API-auth-015: Token刷新-成功
    def test_api_auth_015_token_refresh_success(self):
        """
        TC-API-auth-015: Token刷新-成功
        预期: HTTP 200, code: 0, 含新access_token
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        user = User.objects.create_user(username='testuser', password='testpass')
        refresh = RefreshToken.for_user(user)
        response = self.client.post(self.url, {
            'refresh_token': str(refresh),
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        assert 'access_token' in response.data['data']
        assert response.data['data']['access_token'] != ''

    # TC-API-auth-016: Token刷新-token已加入黑名单
    def test_api_auth_016_token_refresh_blacklisted(self):
        """
        TC-API-auth-016: Token刷新-token已加入黑名单
        预期: HTTP 401, Token无效
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        user = User.objects.create_user(username='testuser2', password='testpass')
        refresh = RefreshToken.for_user(user)
        refresh.blacklist()

        response = self.client.post(self.url, {
            'refresh_token': str(refresh),
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # TC-API-auth-017: Token刷新-token过期
    def test_api_auth_017_token_refresh_invalid_token(self):
        """
        TC-API-auth-017: Token刷新-token无效
        预期: HTTP 401, Token无效
        """
        response = self.client.post(self.url, {
            'refresh_token': 'invalid.token.string',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPasswordReset:
    """TC-API-auth-021 ~ 022: 修改密码"""

    def setup_method(self):
        self.client = APIClient()

    # TC-API-auth-021: 修改密码-成功
    def test_api_auth_021_password_reset_success(self):
        """
        TC-API-auth-021: 修改密码-成功
        步骤1: 发送验证码 → Step1验证 → Step2重置密码
        预期: HTTP 200, 密码重置成功
        """
        phone = '13800001111'
        User.objects.create_user(username=phone, password='OldPass123')

        # Step1: 发送密码重置验证码
        now = timezone.now()
        AuthSmsCode.objects.create(
            phone=phone, code='123456', type='password_reset',
            expire_at=now + timedelta(minutes=5),
        )

        # Step1: 验证手机号+验证码
        verify_url = reverse('password-reset-verify')
        verify_resp = self.client.post(verify_url, {
            'phone': phone,
            'code': '123456',
        }, format='json')
        assert verify_resp.status_code == status.HTTP_200_OK
        assert verify_resp.data['code'] == 0
        verify_token = verify_resp.data['data']['verify_token']

        # Step2: 重置密码
        reset_url = reverse('password-reset')
        reset_resp = self.client.post(reset_url, {
            'phone': phone,
            'verify_token': verify_token,
            'password': 'NewPass456',
        }, format='json')
        assert reset_resp.status_code == status.HTTP_200_OK
        assert reset_resp.data['code'] == 0
        assert '密码重置成功' in reset_resp.data['message']

        # 验证新密码可以登录
        user = User.objects.get(username=phone)
        assert user.check_password('NewPass456')

    # TC-API-auth-022: 修改密码-验证码无效
    def test_api_auth_022_password_reset_invalid_code(self):
        """
        TC-API-auth-022: 修改密码-验证码无效
        预期: HTTP 400, 验证码无效或已过期
        """
        phone = '13800001111'
        User.objects.create_user(username=phone, password='OldPass123')
        verify_url = reverse('password-reset-verify')
        resp = self.client.post(verify_url, {
            'phone': phone,
            'code': '000000',
        }, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogout:
    """TC-API-auth-023 ~ 024: 登出"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('logout')

    # TC-API-auth-023: 登出-成功
    def test_api_auth_023_logout_success(self):
        """
        TC-API-auth-023: 登出-成功
        预期: HTTP 200, code: 0, 登出成功
        """
        user = User.objects.create_user(username='testuser', password='testpass')
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, {
            'refresh_token': str(refresh),
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        assert '登出成功' in response.data['message']

    # TC-API-auth-024: 登出-无效token
    def test_api_auth_024_logout_no_auth(self):
        """
        TC-API-auth-024: 登出-未认证
        预期: HTTP 401
        """
        response = self.client.post(self.url, {
            'refresh_token': 'some_token',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCurrentUserInfo:
    """TC-API-auth-025 ~ 026: 获取当前用户信息"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('current-user-info')

    # TC-API-auth-025: 获取当前用户信息-已登录
    def test_api_auth_025_me_authenticated(self):
        """
        TC-API-auth-025: 获取当前用户信息-已登录
        预期: HTTP 200, code: 0, 含用户信息
        """
        user = User.objects.create_user(
            username='13800001111', password='TestPass123'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        data = response.data['data']
        assert data['phone'] == '13800001111'
        assert data['id'] == user.id
        assert 'role_code' in data

    # TC-API-auth-026: 获取当前用户信息-未登录
    def test_api_auth_026_me_unauthenticated(self):
        """
        TC-API-auth-026: 获取当前用户信息-未登录
        预期: HTTP 401
        """
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
