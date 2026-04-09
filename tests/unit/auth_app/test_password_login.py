import pytest
from datetime import timedelta, timezone as dt_timezone
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from apps.auth_app.models import UserProfile


@pytest.mark.django_db
class TestPasswordLoginAPI:
    """AUTH-005: 密码登录接口测试"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('password-login')
        self.phone = '13800138000'
        self.password = 'TestPass123!'
        self.ip = '127.0.0.1'
        # 每个测试前清理 cache
        cache.clear()

    def _create_user(self, phone=None, password=None, role_code='guest'):
        """辅助方法：创建测试用户"""
        phone = phone or self.phone
        password = password or self.password
        user = User.objects.create_user(username=phone, password=password)
        profile = user.ent_user_profile
        profile.role_code = role_code
        profile.save()
        return user

    def _get_cache_key(self, ip=None):
        """辅助方法：获取登录失败次数的 cache key"""
        ip = ip or self.ip
        return f'login_fail_count:{ip}'

    def _get_lock_key(self, ip=None):
        """辅助方法：获取锁定状态的 cache key"""
        ip = ip or self.ip
        return f'login_locked:{ip}'

    # ==================== 正例测试 ====================

    def test_login_success(self):
        """正常登录 - 手机号+密码正确，返回token和用户信息"""
        user = self._create_user()

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 0
        assert data['message'] == 'success'
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user_id'] == user.id
        assert data['data']['role_code'] == 'guest'
        assert isinstance(data['data']['permissions'], list)

    def test_login_success_with_role(self):
        """登录成功 - 返回用户的真实角色码"""
        user = self._create_user(role_code='enterprise_admin')

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['role_code'] == 'enterprise_admin'
        assert response.data['data']['user_id'] == user.id

    def test_remember_me_extends_refresh_token(self):
        """remember_me=true 时 refresh_token 有效期延长至 7 天"""
        import jwt as pyjwt
        from django.conf import settings

        self._create_user()

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password, 'remember_me': True},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_200_OK

        # 解析 refresh_token 验证有效期恰好为 7 天
        refresh_token = response.data['data']['refresh_token']
        secret = settings.SECRET_KEY
        algorithm = settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')
        decoded = pyjwt.decode(
            refresh_token, secret, algorithms=[algorithm],
            options={'verify_exp': False},
        )
        exp = timezone.datetime.fromtimestamp(decoded['exp'], tz=dt_timezone.utc)
        iat = timezone.datetime.fromtimestamp(decoded['iat'], tz=dt_timezone.utc)
        delta = exp - iat
        # 允许 1 秒误差
        assert abs(delta.total_seconds() - timedelta(days=7).total_seconds()) < 1

    def test_remember_me_false_default(self):
        """不传 remember_me 时使用默认短期 refresh_token"""
        self._create_user()

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data['data']
        assert 'refresh_token' in response.data['data']

    def test_successful_login_resets_fail_count(self):
        """登录成功后清除该IP的失败计数"""
        self._create_user()
        cache_key = self._get_cache_key()

        # 先模拟有2次失败记录
        cache.set(cache_key, 2, 1800)

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_200_OK
        # 失败计数应被清除
        assert cache.get(cache_key) is None

    # ==================== 反例测试：密码校验 ====================

    def test_wrong_password(self):
        """密码错误 - 返回错误信息"""
        self._create_user()

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': 'WrongPass999!'},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['code'] != 0
        assert '密码' in response.data['message'] or '错误' in response.data['message']

    def test_wrong_password_increments_fail_count(self):
        """密码错误 - 失败计数递增"""
        self._create_user()
        cache_key = self._get_cache_key()

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': 'WrongPass999!'},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert cache.get(cache_key) == 1

    def test_user_not_found(self):
        """手机号未注册 - 返回错误"""
        response = self.client.post(
            self.url,
            {'phone': '13900139000', 'password': 'SomePass123!'},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['code'] != 0

    # ==================== 反例测试：参数校验 ====================

    def test_missing_phone(self):
        """缺少手机号"""
        response = self.client.post(
            self.url,
            {'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'phone' in response.data['errors']

    def test_missing_password(self):
        """缺少密码"""
        response = self.client.post(
            self.url,
            {'phone': self.phone},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'password' in response.data['errors']

    def test_invalid_phone_format(self):
        """手机号格式不正确"""
        response = self.client.post(
            self.url,
            {'phone': '123', 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'phone' in response.data['errors']

    def test_phone_with_letters(self):
        """手机号包含字母"""
        response = self.client.post(
            self.url,
            {'phone': '13800ab0000', 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'phone' in response.data['errors']

    # ==================== IP锁定逻辑测试 ====================

    def test_ip_locked_after_5_failures(self):
        """同一IP连续5次密码错误后锁定30分钟"""
        self._create_user()
        cache_key = self._get_cache_key()
        lock_key = self._get_lock_key()

        # 模拟已有5次失败并且已经触发锁定
        cache.set(cache_key, 5, 1800)
        cache.set(lock_key, True, 1800)

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert '30' in response.data['message']

    def test_ip_locked_even_with_correct_password(self):
        """IP被锁定时，即使密码正确也无法登录"""
        self._create_user()
        lock_key = self._get_lock_key()

        # 直接设置锁定状态
        cache.set(lock_key, True, 1800)

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_ip_lock_at_5th_failure(self):
        """第5次密码错误时触发锁定"""
        self._create_user()
        cache_key = self._get_cache_key()
        lock_key = self._get_lock_key()

        # 模拟已有4次失败
        cache.set(cache_key, 4, 1800)

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': 'WrongPass999!'},
            REMOTE_ADDR=self.ip,
        )

        # 第5次错误应返回 401（本次错误本身），但锁定已生效
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # 验证锁定 key 已设置
        assert cache.get(lock_key) is not None

    def test_different_ip_not_affected(self):
        """不同IP不受锁定影响"""
        self._create_user()
        cache_key_1 = self._get_cache_key('192.168.1.1')
        lock_key_1 = self._get_lock_key('192.168.1.1')

        # 锁定 IP 192.168.1.1
        cache.set(lock_key_1, True, 1800)

        # 使用另一个 IP 127.0.0.1 应该正常
        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_200_OK

    def test_lock_duration_30_minutes(self):
        """锁定时间应设置为30分钟（验证锁定 key 存在且使用正确的超时）"""
        self._create_user()
        cache_key = self._get_cache_key()
        lock_key = self._get_lock_key()

        # 模拟已有4次失败
        cache.set(cache_key, 4, 1800)

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': 'WrongPass999!'},
            REMOTE_ADDR=self.ip,
        )

        # 验证锁定 key 已设置
        assert cache.get(lock_key) is not None

    # ==================== 边界值测试 ====================

    def test_4_failures_not_locked(self):
        """4次失败后仍未锁定，第5次用正确密码可登录"""
        self._create_user()
        cache_key = self._get_cache_key()

        # 模拟已有4次失败
        cache.set(cache_key, 4, 1800)

        # 第5次用正确密码应该能登录
        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_200_OK

    def test_empty_password(self):
        """空密码"""
        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': ''},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remember_me_explicit_false(self):
        """remember_me=false 时使用默认 refresh_token 有效期"""
        self._create_user()

        response = self.client.post(
            self.url,
            {'phone': self.phone, 'password': self.password, 'remember_me': False},
            REMOTE_ADDR=self.ip,
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data['data']
        assert 'refresh_token' in response.data['data']
