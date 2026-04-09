import pytest
from datetime import timedelta, timezone as dt_timezone
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.auth_app.models import AuthSmsCode, UserProfile


@pytest.mark.django_db
class TestSmsLoginAPI:
    """AUTH-004: 短信验证码登录/注册接口测试"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('sms-login')
        self.phone = '13800138000'
        self.now = timezone.now()

    # ==================== 正例测试 ====================

    def test_login_with_existing_user_success(self):
        """已注册用户 - 验证码正确，登录成功，返回token和用户信息"""
        # 创建已有用户（手机号作为username）
        user = User.objects.create_user(username=self.phone, password='')
        profile = user.ent_user_profile
        profile.role_code = 'enterprise_admin'
        profile.save()

        # 创建有效验证码
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='123456',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '123456',
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 0
        assert data['message'] == 'success'
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user_id'] == user.id
        assert data['data']['role_code'] == 'enterprise_admin'
        assert isinstance(data['data']['permissions'], list)

    def test_register_new_user_success(self):
        """新手机号 - 自动注册，创建User和UserProfile(role_code=guest)"""
        # 不创建User，模拟新用户
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='654321',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '654321',
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 0

        # 验证User被创建
        user = User.objects.get(username=self.phone)
        assert user is not None

        # 验证UserProfile被信号自动创建，role_code=guest
        profile = user.ent_user_profile
        assert profile.role_code == 'guest'

        # 验证返回数据
        assert data['data']['user_id'] == user.id
        assert data['data']['role_code'] == 'guest'

    def test_sms_code_marked_as_used_after_login(self):
        """验证码使用后标记 used_at，防止重用"""
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='111111',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '111111',
        })

        assert response.status_code == status.HTTP_200_OK

        # 验证码的used_at应该被标记
        sms_record = AuthSmsCode.objects.filter(
            phone=self.phone, code='111111', type='login'
        ).first()
        assert sms_record.used_at is not None

    def test_remember_me_extends_refresh_token(self):
        """remember_me=true 时 refresh_token 有效期延长至 7 天（DESN 规定）"""
        import jwt as pyjwt
        from django.conf import settings

        AuthSmsCode.objects.create(
            phone=self.phone,
            code='222222',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '222222',
            'remember_me': True,
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data['data']
        assert 'refresh_token' in response.data['data']

        # 解析 refresh_token 验证有效期恰好为 7 天
        refresh_token = response.data['data']['refresh_token']
        secret = settings.SECRET_KEY
        algorithm = settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')
        decoded = pyjwt.decode(refresh_token, secret, algorithms=[algorithm], options={'verify_exp': False})
        exp = timezone.datetime.fromtimestamp(decoded['exp'], tz=dt_timezone.utc)
        iat = timezone.datetime.fromtimestamp(decoded['iat'], tz=dt_timezone.utc)
        delta = exp - iat
        # 允许 1 秒误差
        assert abs(delta.total_seconds() - timedelta(days=7).total_seconds()) < 1

    def test_remember_me_false_default(self):
        """不传 remember_me 时使用默认短期 refresh_token"""
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='333333',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '333333',
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data['data']
        assert 'refresh_token' in response.data['data']

    # ==================== 反例测试：验证码校验 ====================

    def test_wrong_code(self):
        """验证码错误"""
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='123456',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '999999',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] != 0

    def test_expired_code(self):
        """验证码已过期（超过5分钟）"""
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='123456',
            type='login',
            expire_at=self.now - timedelta(minutes=1),  # 已过期
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '123456',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '验证码' in response.data['message'] or '过期' in response.data['message']

    def test_used_code(self):
        """已使用的验证码不能再次使用（used_at不为NULL）"""
        sms = AuthSmsCode.objects.create(
            phone=self.phone,
            code='123456',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )
        sms.used_at = self.now
        sms.save()

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '123456',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '验证码' in response.data['message'] or '无效' in response.data['message']

    def test_code_not_found(self):
        """手机号没有对应的验证码记录"""
        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '123456',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # ==================== 反例测试：参数校验 ====================

    def test_missing_phone(self):
        """缺少手机号"""
        response = self.client.post(self.url, {
            'code': '123456',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'phone' in response.data['errors']

    def test_missing_code(self):
        """缺少验证码"""
        response = self.client.post(self.url, {
            'phone': self.phone,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'code' in response.data['errors']

    def test_invalid_phone_format(self):
        """手机号格式不正确"""
        response = self.client.post(self.url, {
            'phone': '123',
            'code': '123456',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'phone' in response.data['errors']

    def test_code_not_6_digits(self):
        """验证码不是6位数字"""
        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '12345',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'code' in response.data['errors']

    def test_code_with_letters(self):
        """验证码包含字母"""
        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '12ab56',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'code' in response.data['errors']

    # ==================== 边界值测试 ====================

    def test_code_exactly_at_expiry_boundary(self):
        """验证码刚好到达过期时间"""
        # expire_at 设为当前时间（临界状态）
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='123456',
            type='login',
            expire_at=self.now,
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '123456',
        })

        # 刚好过期的验证码应该无效
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_code_one_second_before_expiry(self):
        """验证码在过期前1秒仍然有效"""
        expire_at = self.now + timedelta(seconds=1)
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='123456',
            type='login',
            expire_at=expire_at,
        )

        response = self.client.post(self.url, {
            'phone': self.phone,
            'code': '123456',
        })

        assert response.status_code == status.HTTP_200_OK

    def test_multiple_valid_codes_use_latest(self):
        """同一个手机号有多条有效验证码时，匹配到的是最新一条"""
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='111111',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )
        # 稍后创建第二条
        AuthSmsCode.objects.create(
            phone=self.phone,
            code='222222',
            type='login',
            expire_at=self.now + timedelta(minutes=5),
        )

        # 用旧验证码 - 不应该成功（因为旧的已被作废或不是最新）
        response_old = self.client.post(self.url, {
            'phone': self.phone,
            'code': '111111',
        })
        # 旧的应该无效
        assert response_old.status_code == status.HTTP_400_BAD_REQUEST

        # 用最新验证码 - 应该成功
        response_new = self.client.post(self.url, {
            'phone': self.phone,
            'code': '222222',
        })
        assert response_new.status_code == status.HTTP_200_OK
