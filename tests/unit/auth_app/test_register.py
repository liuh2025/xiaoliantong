import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.auth_app.models import AuthSmsCode


@pytest.mark.django_db
class TestRegisterAPI:
    """注册接口测试"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('register')
        self.phone = '13900001111'
        self.now = timezone.now()

    def test_register_success(self):
        """注册成功 - 创建用户 + 设置密码 + 返回token"""
        AuthSmsCode.objects.create(
            phone=self.phone, code='123456', type='register',
            expire_at=self.now + timedelta(minutes=5),
        )
        response = self.client.post(self.url, {
            'phone': self.phone, 'code': '123456', 'password': 'Test1234',
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 0
        # 验证用户已创建且有密码
        user = User.objects.get(username=self.phone)
        assert user.check_password('Test1234')
        # 验证返回 token
        assert 'access_token' in response.data['data']
        assert 'refresh_token' in response.data['data']

    def test_register_phone_already_exists(self):
        """手机号已注册 - 返回400"""
        User.objects.create_user(username=self.phone, password='OldPass123')
        AuthSmsCode.objects.create(
            phone=self.phone, code='123456', type='register',
            expire_at=self.now + timedelta(minutes=5),
        )
        response = self.client.post(self.url, {
            'phone': self.phone, 'code': '123456', 'password': 'Test1234',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '已注册' in response.data['message']

    def test_register_invalid_code(self):
        """验证码错误"""
        AuthSmsCode.objects.create(
            phone=self.phone, code='123456', type='register',
            expire_at=self.now + timedelta(minutes=5),
        )
        response = self.client.post(self.url, {
            'phone': self.phone, 'code': '999999', 'password': 'Test1234',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_expired_code(self):
        """验证码过期"""
        AuthSmsCode.objects.create(
            phone=self.phone, code='123456', type='register',
            expire_at=self.now - timedelta(minutes=1),
        )
        response = self.client.post(self.url, {
            'phone': self.phone, 'code': '123456', 'password': 'Test1234',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_too_short(self):
        """密码少于8位"""
        AuthSmsCode.objects.create(
            phone=self.phone, code='123456', type='register',
            expire_at=self.now + timedelta(minutes=5),
        )
        response = self.client.post(self.url, {
            'phone': self.phone, 'code': '123456', 'password': '1234567',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_password(self):
        """缺少密码"""
        AuthSmsCode.objects.create(
            phone=self.phone, code='123456', type='register',
            expire_at=self.now + timedelta(minutes=5),
        )
        response = self.client.post(self.url, {
            'phone': self.phone, 'code': '123456',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_sms_code_marked_used(self):
        """注册成功后验证码标记为已使用"""
        AuthSmsCode.objects.create(
            phone=self.phone, code='123456', type='register',
            expire_at=self.now + timedelta(minutes=5),
        )
        self.client.post(self.url, {
            'phone': self.phone, 'code': '123456', 'password': 'Test1234',
        })
        sms = AuthSmsCode.objects.filter(phone=self.phone, code='123456', type='register').first()
        assert sms.used_at is not None

    def test_register_wrong_sms_type(self):
        """使用 login 类型的验证码注册 - 应失败"""
        AuthSmsCode.objects.create(
            phone=self.phone, code='123456', type='login',
            expire_at=self.now + timedelta(minutes=5),
        )
        response = self.client.post(self.url, {
            'phone': self.phone, 'code': '123456', 'password': 'Test1234',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
