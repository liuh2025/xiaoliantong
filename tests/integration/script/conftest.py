"""
L1 API Integration Test - Shared fixtures and configuration.
"""
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from apps.enterprise.models import Enterprise, MasterData
from apps.auth_app.models import UserProfile, AuthSmsCode
from apps.opportunity.models import Opportunity


# ============================================================
# API Client fixtures
# ============================================================

@pytest.fixture
def anon_client():
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user_password():
    return 'TestPass123!'


@pytest.fixture
def normal_user(user_password):
    """Create a normal registered user."""
    user = User.objects.create_user(
        username='testuser', password=user_password, email='test@example.com'
    )
    # Signal auto-creates UserProfile; update it
    profile = user.ent_user_profile
    profile.contact_phone = '13800001111'
    profile.save()
    return user


@pytest.fixture
def auth_client(normal_user):
    """Authenticated API client for normal user."""
    client = APIClient()
    client.force_authenticate(user=normal_user)
    return client


@pytest.fixture
def admin_user(user_password):
    """Platform super admin."""
    user = User.objects.create_superuser(
        username='platadmin', password=user_password, email='admin@example.com'
    )
    profile = user.ent_user_profile
    profile.role_code = 'plat_admin'
    profile.contact_phone = '13800000001'
    profile.save()
    return user


@pytest.fixture
def admin_client(admin_user):
    """Authenticated API client for platform admin."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def ent_admin_user(user_password):
    """Enterprise admin user with a verified enterprise."""
    user = User.objects.create_user(
        username='entadmin', password=user_password, email='ent@example.com'
    )
    profile = user.ent_user_profile
    profile.role_code = 'enterprise_admin'
    profile.contact_phone = '13900000001'
    profile.save()

    ent = Enterprise.objects.create(
        name='测试企业有限公司',
        credit_code='91MA0000001234X',
        legal_representative='张三',
        business_license='https://example.com/license.jpg',
        industry_id=1,
        sub_industry_id=101,
        province_id=110000,
        region_id=110100,
        auth_status=Enterprise.AuthStatus.VERIFIED,
        admin_user=user,
    )
    profile.enterprise_id = ent.id
    profile.save()
    return user, ent


@pytest.fixture
def ent_admin_client(ent_admin_user):
    """Authenticated API client for enterprise admin."""
    client = APIClient()
    client.force_authenticate(user=ent_admin_user[0])
    return client


# ============================================================
# Helper fixtures
# ============================================================

@pytest.fixture
def verified_enterprise(ent_admin_user):
    """A verified enterprise."""
    return ent_admin_user[1]


@pytest.fixture
def sample_opportunity(verified_enterprise, ent_admin_user):
    """Create a sample opportunity."""
    return Opportunity.objects.create(
        title='测试采购商机',
        type=Opportunity.OppType.BUY,
        detail='这是一个测试商机描述，至少需要20个字符才能通过验证。',
        enterprise=verified_enterprise,
        publisher=ent_admin_user[0],
        status=Opportunity.OppStatus.ACTIVE,
        contact_name='李经理',
        contact_phone='13800138000',
        industry_id=1,
        sub_industry_id=101,
        category_id=1,
        province_id=110000,
        region_id=110100,
    )


@pytest.fixture
def master_data_industry():
    """Create industry master data."""
    items = []
    parent = MasterData.objects.create(
        category='industry', name='智能网联', code='IND-01', parent_id=0
    )
    items.append(parent)
    child = MasterData.objects.create(
        category='industry', name='自动驾驶', code='IND-01-01', parent_id=parent.id
    )
    items.append(child)
    return items


@pytest.fixture
def master_data_region():
    """Create region master data."""
    items = []
    parent = MasterData.objects.create(
        category='region', name='上海市', code='310000', parent_id=0
    )
    items.append(parent)
    child = MasterData.objects.create(
        category='region', name='浦东新区', code='310115', parent_id=parent.id
    )
    items.append(child)
    return items


@pytest.fixture
def master_data_category():
    """Create category master data."""
    return MasterData.objects.create(
        category='category', name='自动驾驶算法', code='CAT-01', parent_id=0
    )


@pytest.fixture
def sms_code_record(normal_user):
    """Create a valid SMS code record."""
    profile = UserProfile.objects.get(user=normal_user)
    phone = profile.contact_phone or normal_user.username
    code = AuthSmsCode.objects.create(
        phone=phone,
        code='123456',
        type='login',
        expire_at=timezone.now() + timedelta(minutes=5),
    )
    return code
