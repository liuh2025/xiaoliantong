import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuthSmsCode, UserProfile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 尝试获取用户的额外属性，如果使用内置 User 可以通过 profile 获取
        # 为了兼容不同的实现方式，这里做一定的容错
        try:
            profile = getattr(user, 'ent_user_profile', None)
            if profile:
                token['role_code'] = getattr(profile, 'role_code', 'guest')
                # 权限字段先尝试从 profile 获取，如果没有再从 user 获取
                token['permissions'] = getattr(
                    profile, 'permissions', getattr(user, 'permissions', [])
                )
            else:
                # 假设 user 模型本身有这些字段（如果扩展了 AbstractUser）
                token['role_code'] = getattr(user, 'role_code', 'guest')
                token['permissions'] = getattr(user, 'permissions', [])
        except Exception:
            token['role_code'] = 'guest'
            token['permissions'] = []

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # 将额外的信息也加入到响应体中（如果需要）
        # data['role_code'] = self.user.profile.role_code

        return data


class SmsSendSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    type = serializers.ChoiceField(choices=AuthSmsCode.TYPE_CHOICES)

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value


class SmsLoginSerializer(serializers.Serializer):
    """短信验证码登录请求的序列化器"""
    phone = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6, min_length=6)
    remember_me = serializers.BooleanField(required=False, default=False)

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value

    def validate_code(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("验证码必须为6位数字")
        return value


class RegisterSerializer(serializers.Serializer):
    """用户注册请求的序列化器"""
    phone = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6, min_length=6)
    password = serializers.CharField(min_length=8, max_length=20)

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value

    def validate_code(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("验证码必须为6位数字")
        return value


class PasswordLoginSerializer(serializers.Serializer):
    """密码登录请求的序列化器"""
    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(min_length=1)
    remember_me = serializers.BooleanField(required=False, default=False)

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value


class PasswordResetVerifySerializer(serializers.Serializer):
    """忘记密码 Step1: 验证手机号+验证码"""
    phone = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value

    def validate_code(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("验证码必须为6位数字")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """忘记密码 Step2: 重置密码"""
    phone = serializers.CharField(max_length=11)
    verify_token = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=20)

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value


class LogoutSerializer(serializers.Serializer):
    """登出请求的序列化器"""
    refresh_token = serializers.CharField()


class CustomTokenRefreshSerializer(serializers.Serializer):
    """自定义 Token 刷新序列化器，使用 refresh_token 替代 SimpleJWT 默认的 refresh 字段"""
    refresh_token = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    default_error_messages = {
        'no_active_account': 'No active account found for the given token.'
    }

    def validate(self, attrs):
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.settings import api_settings
        from rest_framework.exceptions import AuthenticationFailed

        refresh = self.token_class(attrs['refresh_token'])

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)
        if user_id and (
            user := get_user_model().objects.get(
                **{api_settings.USER_ID_FIELD: user_id}
            )
        ):
            if not api_settings.USER_AUTHENTICATION_RULE(user):
                raise AuthenticationFailed(
                    self.error_messages['no_active_account'],
                    'no_active_account',
                )

        data = {'access': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()

            data['refresh'] = str(refresh)

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """用户信息序列化器 - 用于 /auth/me 接口"""

    class Meta:
        model = UserProfile
        fields = ['real_name', 'position', 'role_code', 'enterprise_id']


class CurrentUserInfoSerializer(serializers.Serializer):
    """当前用户信息序列化器"""

    id = serializers.IntegerField(source='pk')
    phone = serializers.CharField(source='username')
    real_name = serializers.CharField(
        source='ent_user_profile.real_name', default=''
    )
    position = serializers.CharField(
        source='ent_user_profile.position', allow_null=True, default=None
    )
    role_code = serializers.CharField(
        source='ent_user_profile.role_code', default='guest'
    )
    enterprise_id = serializers.IntegerField(
        source='ent_user_profile.enterprise_id', allow_null=True, default=None
    )
    enterprise_name = serializers.SerializerMethodField()
    enterprise_status = serializers.SerializerMethodField()

    def get_enterprise_name(self, obj):
        """获取企业名称 - ent 模块未开发，返回 None"""
        profile = getattr(obj, 'ent_user_profile', None)
        if profile and profile.enterprise_id:
            # TODO: ent 模块开发后，通过 enterprise_id 查询企业名称
            return None
        return None

    def get_enterprise_status(self, obj):
        """获取企业认证状态 - ent 模块未开发，返回 None"""
        profile = getattr(obj, 'ent_user_profile', None)
        if profile and profile.enterprise_id:
            # TODO: ent 模块开发后，通过 enterprise_id 查询企业状态
            return None
        return None
