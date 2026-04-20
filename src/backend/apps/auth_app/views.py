from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from datetime import timedelta
import secrets
import string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import AuthSmsCode
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from .serializers import (
    SmsSendSerializer, SmsLoginSerializer, PasswordLoginSerializer,
    PasswordResetVerifySerializer, PasswordResetSerializer,
    LogoutSerializer, CustomTokenRefreshSerializer,
    CurrentUserInfoSerializer, RegisterSerializer,
)


def _get_user_permissions(user, profile):
    """获取用户权限列表"""
    try:
        perms = getattr(profile, 'permissions', None)
        if perms:
            return list(perms)
        perm_list = list(
            user.user_permissions.values_list('codename', flat=True)
        )
        return perm_list
    except Exception:
        return []


class SmsSendView(views.APIView):
    # 根据需要，发送验证码可能不需要认证
    permission_classes = []

    def post(self, request):
        serializer = SmsSendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'code': 400, 'message': '参数错误', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data['phone']
        sms_type = serializer.validated_data['type']

        # 每日次数限制
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_count = AuthSmsCode.objects.filter(
            phone=phone,
            type=sms_type,
            created_at__gte=today_start
        ).count()

        limits = {
            'login': 10,
            'register': 10,
            'password_reset': 5
        }
        limit = limits.get(sms_type, 5)

        if daily_count >= limit:
            return Response(
                {'code': 429, 'message': '超出每日发送次数限制'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 5分钟内未使用验证码自动作废重发
        # 我们这里的实现逻辑：直接创建一条新的，新的一旦生成，旧的在后面校验时应该取最新的一条或者把旧的used_at标记
        # 这里把旧的5分钟内未使用的统一作废
        AuthSmsCode.objects.filter(
            phone=phone,
            type=sms_type,
            used_at__isnull=True,
            expire_at__gt=now
        ).update(used_at=now)  # 标记为已使用/作废

        # 生成新验证码
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        expire_at = now + timedelta(minutes=5)

        AuthSmsCode.objects.create(
            phone=phone,
            code=code,
            type=sms_type,
            expire_at=expire_at
        )

        # TODO: 集成真实的短信发送服务
        # 发送成功
        return Response({
            'code': 0,
            'message': '验证码已发送（开发环境mock）',
            'data': {}  # 生产环境不返回code，这里如果为了方便测试可以考虑返回或者不返回，按规范不返回
        }, status=status.HTTP_200_OK)


class SmsLoginView(views.APIView):
    """短信验证码登录/注册接口"""
    permission_classes = []

    def post(self, request):
        serializer = SmsLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'code': 400, 'message': '参数错误', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        remember_me = serializer.validated_data.get('remember_me', False)

        now = timezone.now()

        # 查找该手机号最新的、未使用的、未过期的 login 类型验证码
        sms_record = (
            AuthSmsCode.objects
            .filter(phone=phone, type='login', used_at__isnull=True, expire_at__gt=now)
            .order_by('-created_at')
            .first()
        )

        if sms_record is None:
            return Response(
                {'code': 400, 'message': '验证码无效或已过期'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if sms_record.code != code:
            return Response(
                {'code': 400, 'message': '验证码错误'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 标记验证码为已使用
        sms_record.used_at = now
        sms_record.save()

        # 仅允许已注册用户登录
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            return Response(
                {'code': 400, 'message': '用户未注册'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 获取 UserProfile（由信号自动创建）
        profile = user.ent_user_profile
        role_code = profile.role_code

        # 生成 JWT Token
        refresh = RefreshToken.for_user(user)

        # 将自定义信息写入 token
        refresh['role_code'] = role_code

        # 获取权限列表
        permissions = _get_user_permissions(user, profile)
        refresh['permissions'] = permissions

        # remember_me 为 true 时延长 refresh_token 有效期
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=7))

        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user_id': user.id,
                'role_code': role_code,
                'permissions': permissions,
            },
        }, status=status.HTTP_200_OK)


class RegisterView(views.APIView):
    """用户注册接口 POST /auth/register/"""
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'code': 400, 'message': '参数错误', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        password = serializer.validated_data['password']

        now = timezone.now()

        # 检查用户是否已注册
        if User.objects.filter(username=phone).exists():
            return Response(
                {'code': 400, 'message': '该手机号已注册'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证短信验证码（type='register'）
        sms_record = (
            AuthSmsCode.objects
            .filter(phone=phone, type='register', used_at__isnull=True, expire_at__gt=now)
            .order_by('-created_at')
            .first()
        )

        if sms_record is None:
            return Response(
                {'code': 400, 'message': '验证码无效或已过期'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if sms_record.code != code:
            return Response(
                {'code': 400, 'message': '验证码错误'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 标记验证码为已使用
        sms_record.used_at = now
        sms_record.save()

        # 创建用户（设置密码）
        user = User.objects.create_user(username=phone, password=password)
        # UserProfile 由信号自动创建

        # 生成 JWT Token（注册后自动登录）
        refresh = RefreshToken.for_user(user)
        profile = user.ent_user_profile
        refresh['role_code'] = profile.role_code

        permissions = _get_user_permissions(user, profile)
        refresh['permissions'] = permissions

        return Response({
            'code': 0,
            'message': '注册成功',
            'data': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user_id': user.id,
                'role_code': profile.role_code,
                'permissions': permissions,
            },
        }, status=status.HTTP_201_CREATED)


# ==================== 常量定义 ====================

LOGIN_FAIL_LIMIT = 5
LOGIN_LOCK_DURATION = 1800  # 30 minutes in seconds
LOGIN_FAIL_COUNT_TTL = 1800  # same as lock duration


def _get_client_ip(request):
    """获取客户端真实 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


class PasswordLoginView(views.APIView):
    """密码登录接口"""
    permission_classes = []

    def post(self, request):
        ip = _get_client_ip(request)
        lock_key = f'login_locked:{ip}'
        fail_key = f'login_fail_count:{ip}'

        # 1. 检查 IP 是否被锁定
        if cache.get(lock_key):
            return Response(
                {'code': 429, 'message': '登录失败次数过多，请30分钟后再试'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 2. 参数校验
        serializer = PasswordLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'code': 400, 'message': '参数错误', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        remember_me = serializer.validated_data.get('remember_me', False)

        # 3. 查找用户
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            self._record_failure(fail_key, lock_key)
            return Response(
                {'code': 401, 'message': '手机号或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 4. 验证密码
        if not check_password(password, user.password):
            self._record_failure(fail_key, lock_key)
            return Response(
                {'code': 401, 'message': '手机号或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 5. 登录成功 - 清除失败计数
        cache.delete(fail_key)
        cache.delete(lock_key)

        # 6. 获取用户信息
        profile = user.ent_user_profile
        role_code = profile.role_code

        # 7. 生成 JWT Token
        refresh = RefreshToken.for_user(user)
        refresh['role_code'] = role_code

        permissions = _get_user_permissions(user, profile)
        refresh['permissions'] = permissions

        # remember_me 为 true 时延长 refresh_token 有效期
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=7))

        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user_id': user.id,
                'role_code': role_code,
                'permissions': permissions,
            },
        }, status=status.HTTP_200_OK)

    @staticmethod
    def _record_failure(fail_key, lock_key):
        """记录登录失败次数，达到阈值后锁定IP"""
        fail_count = cache.get(fail_key, 0) + 1
        cache.set(fail_key, fail_count, LOGIN_FAIL_COUNT_TTL)

        if fail_count >= LOGIN_FAIL_LIMIT:
            cache.set(lock_key, True, LOGIN_LOCK_DURATION)


# ==================== 密码重置常量 ====================

VERIFY_TOKEN_MAX_AGE = 600  # verify_token 有效期 10 分钟（秒）


class PasswordResetVerifyView(views.APIView):
    """忘记密码 Step1: 验证手机号+验证码，返回 verify_token"""
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'code': 400, 'message': '参数错误', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        now = timezone.now()

        # 检查用户是否存在
        if not User.objects.filter(username=phone).exists():
            return Response(
                {'code': 400, 'message': '用户未注册'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 查找最新的、未使用的、未过期的 password_reset 类型验证码
        sms_record = (
            AuthSmsCode.objects
            .filter(phone=phone, type='password_reset', used_at__isnull=True, expire_at__gt=now)
            .order_by('-created_at')
            .first()
        )

        if sms_record is None:
            return Response(
                {'code': 400, 'message': '验证码无效或已过期'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if sms_record.code != code:
            return Response(
                {'code': 400, 'message': '验证码错误'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 标记验证码为已使用（作废）
        sms_record.used_at = now
        sms_record.save()

        # 生成临时 verify_token（包含手机号和时间戳签名）
        signer = TimestampSigner()
        verify_token = signer.sign(phone)

        return Response({
            'code': 0,
            'message': '验证通过',
            'data': {
                'verify_token': verify_token,
            },
        }, status=status.HTTP_200_OK)


class PasswordResetView(views.APIView):
    """忘记密码 Step2: 使用 verify_token 重置密码"""
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'code': 400, 'message': '参数错误', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data['phone']
        verify_token = serializer.validated_data['verify_token']
        password = serializer.validated_data['password']

        # 验证 verify_token 有效性
        signer = TimestampSigner()

        # 先检查 token 是否已被使用（防止重放攻击）
        cache_key = f'pw_reset_used:{verify_token}'
        if cache.get(cache_key):
            return Response(
                {'code': 400, 'message': 'verify_token 已使用'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            signed_phone = signer.unsign(verify_token, max_age=VERIFY_TOKEN_MAX_AGE)
        except SignatureExpired:
            return Response(
                {'code': 400, 'message': 'verify_token 已过期'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BadSignature:
            return Response(
                {'code': 400, 'message': 'verify_token 无效'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证 verify_token 与手机号匹配
        if signed_phone != phone:
            return Response(
                {'code': 400, 'message': 'verify_token 与手机号不匹配'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查用户是否存在
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            return Response(
                {'code': 400, 'message': '用户未注册'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 新密码不能与原密码相同
        if user.check_password(password):
            return Response(
                {'code': 400, 'message': '新密码不能与原密码相同'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 重置密码
        user.set_password(password)
        user.save()

        # 使 verify_token 失效 - 标记为已使用，防止重放
        cache.set(cache_key, True, VERIFY_TOKEN_MAX_AGE)

        return Response({
            'code': 0,
            'message': '密码重置成功',
            'data': {},
        }, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    """登出接口：将 refresh_token 加入黑名单"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'code': 400, 'message': '参数错误', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh_token_str = serializer.validated_data['refresh_token']

        try:
            token = RefreshToken(refresh_token_str)
        except (TokenError, InvalidToken):
            return Response(
                {'code': 400, 'message': '无效的refresh_token'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 将 token 加入黑名单
        try:
            token.blacklist()
        except AttributeError:
            # token_blacklist app 未正确安装时回退处理
            return Response(
                {'code': 500, 'message': '登出服务暂不可用'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({
            'code': 0,
            'message': '登出成功',
            'data': {},
        }, status=status.HTTP_200_OK)


class CustomTokenRefreshView(BaseTokenRefreshView):
    """自定义 Token 刷新视图，使用项目统一的响应格式"""
    permission_classes = []
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # 将 DESN 要求的字段名映射到响应中
        validated = serializer.validated_data
        data = {
            'access_token': validated.get('access', ''),
            'refresh_token': validated.get('refresh', ''),
        }

        return Response({
            'code': 0,
            'message': 'success',
            'data': data,
        }, status=status.HTTP_200_OK)


class CurrentUserInfoView(views.APIView):
    """AUTH-008: 当前用户信息接口 GET /auth/me"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CurrentUserInfoSerializer(user)

        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)
