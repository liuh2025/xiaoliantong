import pytest
from django.contrib.auth.models import User
from apps.auth_app.models import UserProfile
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
class TestUserProfileModel:
    def test_create_user_creates_profile(self):
        """测试创建User时是否自动创建UserProfile"""
        user = User.objects.create_user(username='testuser', password='password123')

        # 验证profile被创建
        assert hasattr(user, 'ent_user_profile')
        profile = user.ent_user_profile
        assert profile is not None
        assert profile.user == user
        assert profile.role_code == 'guest'
        assert profile.real_name == ''

    def test_update_user_profile(self):
        """测试更新UserProfile相关字段"""
        user = User.objects.create_user(username='testuser2', password='password123')
        profile = user.ent_user_profile

        profile.real_name = '张三'
        profile.position = '技术总监'
        profile.contact_phone = '13800138000'
        profile.role_code = 'enterprise_admin'
        profile.save()

        # 重新从数据库获取并验证
        user.refresh_from_db()
        updated_profile = user.ent_user_profile
        assert updated_profile.real_name == '张三'
        assert updated_profile.position == '技术总监'
        assert updated_profile.contact_phone == '13800138000'
        assert updated_profile.role_code == 'enterprise_admin'
