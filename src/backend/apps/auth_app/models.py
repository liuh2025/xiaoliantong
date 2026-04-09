from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """用户企业扩展表"""
    ROLE_CHOICES = (
        ('super_admin', '超级管理员'),
        ('platform_operator', '平台运营'),
        ('enterprise_admin', '企业管理员'),
        ('employee', '企业员工'),
        ('guest', '游客'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ent_user_profile', verbose_name='关联用户')
    role_code = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest', verbose_name='业务角色码')
    real_name = models.CharField(max_length=50, blank=True, default='', verbose_name='真实姓名')
    position = models.CharField(max_length=50, blank=True, null=True, verbose_name='职位/职级')
    contact_phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='联系电话')
    contact_wechat = models.CharField(max_length=50, blank=True, null=True, verbose_name='微信')
    enterprise_id = models.IntegerField(null=True, blank=True, verbose_name='关联企业ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ent_user_profile'
        verbose_name = '用户企业扩展'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username}'s profile"


class AuthSmsCode(models.Model):
    """短信验证码表"""
    TYPE_CHOICES = (
        ('login', '登录'),
        ('register', '注册'),
        ('password_reset', '密码重置'),
    )

    phone = models.CharField(max_length=11, verbose_name='手机号')
    code = models.CharField(max_length=6, verbose_name='验证码')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='业务类型')
    expire_at = models.DateTimeField(verbose_name='过期时间')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'auth_sms_code'
        verbose_name = '短信验证码'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['phone', 'type'], name='idx_phone_type'),
            models.Index(fields=['expire_at'], name='idx_expire_at'),
        ]

    def __str__(self):
        return f"{self.phone} - {self.type} - {self.code}"
