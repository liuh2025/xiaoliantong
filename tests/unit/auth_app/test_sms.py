import pytest
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.auth_app.models import AuthSmsCode

@pytest.mark.django_db
class TestSmsCodeAPI:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('sms-send')
        self.phone = '13800138000'
        
    def test_send_sms_success(self):
        """测试成功发送短信验证码"""
        data = {
            'phone': self.phone,
            'type': 'login'
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 0
        assert '验证码已发送' in response.data['message']
        
        # 验证数据库记录
        sms_record = AuthSmsCode.objects.filter(phone=self.phone, type='login').first()
        assert sms_record is not None
        assert len(sms_record.code) == 6
        assert sms_record.used_at is None
        
    def test_send_sms_invalid_phone(self):
        """测试无效的手机号"""
        data = {
            'phone': '123',
            'type': 'login'
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'phone' in response.data['errors']
        
    def test_send_sms_invalid_type(self):
        """测试无效的类型"""
        data = {
            'phone': self.phone,
            'type': 'invalid_type'
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'type' in response.data['errors']
        
    def test_daily_limit_login(self):
        """测试每日发送次数限制 - login(10次)"""
        # 创建9条当天的记录
        now = timezone.now()
        for i in range(9):
            AuthSmsCode.objects.create(
                phone=self.phone,
                code=f'{100000+i}',
                type='login',
                expire_at=now + timedelta(minutes=5)
            )
            
        # 第10次应该成功
        data = {'phone': self.phone, 'type': 'login'}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        
        # 第11次应该失败
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '超出每日发送次数限制' in response.data['message']
        
    def test_daily_limit_password_reset(self):
        """测试每日发送次数限制 - password_reset(5次)"""
        # 创建4条当天的记录
        now = timezone.now()
        for i in range(4):
            AuthSmsCode.objects.create(
                phone=self.phone,
                code=f'{100000+i}',
                type='password_reset',
                expire_at=now + timedelta(minutes=5)
            )
            
        # 第5次应该成功
        data = {'phone': self.phone, 'type': 'password_reset'}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        
        # 第6次应该失败
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '超出每日发送次数限制' in response.data['message']

    def test_types_have_separate_limits(self):
        """测试不同类型的次数限制是独立的"""
        now = timezone.now()
        # 把 register 的次数用完(10次)
        for i in range(10):
            AuthSmsCode.objects.create(
                phone=self.phone,
                code=f'{100000+i}',
                type='register',
                expire_at=now + timedelta(minutes=5)
            )
            
        # login 的次数应该不受影响
        data = {'phone': self.phone, 'type': 'login'}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        
    def test_unused_code_in_5_minutes_invalidated(self):
        """测试5分钟内有未使用的验证码时，发送新的会导致旧的作废重发"""
        now = timezone.now()
        old_record = AuthSmsCode.objects.create(
            phone=self.phone,
            code='123456',
            type='login',
            expire_at=now + timedelta(minutes=5)
        )
        
        # 立即发送新的
        data = {'phone': self.phone, 'type': 'login'}
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # 验证旧记录被标记为已使用（作废）
        old_record.refresh_from_db()
        assert old_record.used_at is not None
        
        # 验证生成了新记录并且没有被作废
        new_record = AuthSmsCode.objects.filter(phone=self.phone, type='login').order_by('-created_at').first()
        assert new_record.id != old_record.id
        assert new_record.used_at is None
