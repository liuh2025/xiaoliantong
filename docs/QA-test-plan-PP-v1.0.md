---
status: 已批准
---

# 测试计划

## XiaoLianTong (校链通)

| 文档信息  | 内容                                                             |
| ----- | -------------------------------------------------------------- |
| 项目名称  | XiaoLianTong (校链通)                                             |
| 文档版本  | v2.0                                                           |
| 创建日期  | 2026-04-07                                                     |
| 关联PRD | [PRD-XiaoLianTong-v1.0.md](PRD-XiaoLianTong-v1.0.md)           |
| 关联设计  | [DESN-PP-v1.0.md](DESN-PP-v1.0.md)                             |
| 关联CHK | [CHK-PP-v1.0.md](CHK-PP-v1.0.md)                               |
| 测试环境  | Windows 10, Python 3.11+, Django 4.2+, MySQL 8.0+, Node.js 18+ |
| 文档状态  | 已批准                                                           |

---

## 1. 测试概述

### 1.1 测试范围

本测试计划覆盖 XiaoLianTong 项目的以下功能模块：

| 模块标识 | 模块名称 | API数量 | 说明 |
|----------|---------|:------:|------|
| auth | 认证模块 | 8 | 登录/注册/登出/Token刷新/密码重置 |
| public | 公共接口 | 1 | 公开统计数据 |
| ent | 企业名录 | 9 | 企业列表/详情/认领/创建/认证 |
| opp | 商机广场 | 7 | 商机列表/详情/发布/联系/推荐 |
| feed | 校友圈 | 6 | 动态列表/详情/发布/最新动态 |
| ent-admin | 企业工作台 | 10 | 企业信息/员工/商机/动态/联系记录 |
| plat-admin | 平台管理 | 48 | 数据大盘/审核/租户/内容/字典/权限/设置 |
| search | 搜索 | 1 | 全局搜索 |
| msg | 消息通知 | 3 | 消息列表/已读/全部已读 |
| **合计** | — | **93** | |

### 1.2 测试层级

| 层次 | 范围 | 工具 | 执行者 | 覆盖目标 |
|------|------|------|--------|---------|
| L1 API 测试 | 所有接口（RPC/RESTful/MQ）正例、反例、边界值、业务规则 | pytest + requests | Tester | API 接口覆盖率 100% |
| L2 E2E 测试 | 完整用户操作流程，主流程/核心功能 100%，含异常测试 | Playwright | Tester | 核心用户场景覆盖率 100% |

---

## 2. 测试用例模板

### 2.1 L1 API 测试用例结构

每个 L1 API 测试用例包含以下结构：

```yaml
用例ID: TC-API-{模块}-{序号}
用例名称: {描述}
接口类型: RESTful / RPC / MQ
模块: {模块名}

# 测试数据（支持参数化）
test_data:
  request: {}        # 请求参数
  dependencies: []   # 依赖的外部数据

# 前置条件
preconditions:
  - 已登录用户 / 已发送验证码 / 已创建企业 / ...

# 操作步骤（详细）
steps:
  - step: 1
    action: POST /api/v1/auth/sms/send
    params:
      phone: "${valid_phone}"
      type: "login"

# 预期结果（HTTP层面）
expected_http:
  status_code: 200
  code: 0
  message: "success"

# 验证步骤（多维验证）
validators:
  # API响应断言
  api:
    - field: data.send_status
      operator: equals
      value: true
  # 数据库校验
  db:
    - table: sms_codes
      conditions:
        phone: "${valid_phone}"
        type: "login"
        used: false
      fields:
        code: "^\\d{6}$"                    # 正则：6位数字
        expires_at: "_ > now + 4min"        # 脚本运行时计算，不写死
        created_at: "_ <= now"
  # 缓存/日志校验
  cache:
    - key: "sms:send:count:${valid_phone}"
      operator: equals
      value: 1

# 后置动作（数据清理）
teardown:
  - DELETE FROM sms_codes WHERE phone="${valid_phone}"

# 依赖用例（参数来源）
depends_on: []

# 参数提取（供后续用例使用）
extractors:
  - from: response.body.data.code_id
    to: "${sms_code_id}"
```

### 2.2 用例模板说明

| 字段 | 说明 | 必填 |
|------|------|------|
| `test_data` | 测试数据，支持变量引用 `${var}` | 是 |
| `steps` | 详细操作步骤，包含完整请求信息 | 是 |
| `expected_http` | HTTP响应预期（状态码、业务码） | 是 |
| `validators` | 多维验证：api/db/cache | 是 |
| `validators.db` | 数据库校验，包含表名、条件、字段断言 | 涉及数据持久化的接口必填 |
| `teardown` | 数据清理，保证用例可重复执行 | 建议填写 |
| `extractors` | 从响应提取参数，供后续用例使用 | 涉及链路测试时填写 |

---

## 3. 测试数据设计

### 3.1 数据驱动架构

```
tests/integration/
├── script/
│   ├── conftest.py              # pytest配置、fixtures、mock
│   ├── test_data/               # 参数化测试数据
│   │   ├── auth/
│   │   │   ├── sms_send.yml    # 发送验证码测试数据
│   │   │   ├── login.yml       # 登录测试数据
│   │   │   └── register.yml    # 注册测试数据
│   │   ├── ent/
│   │   │   ├── list.yml        # 企业列表测试数据
│   │   │   └── create.yml      # 企业创建测试数据
│   │   └── ...
│   ├── api/                     # API测试脚本
│   ├── db/                      # 数据库校验辅助
│   │   ├── queries.py           # 封装常用查询
│   │   └── validators.py        # 自定义断言
│   └── utils/
│       ├── data_loader.py        # YAML数据加载
│       └── parameter_linker.py   # 参数关联
└── fixtures/                    # Django fixtures
    ├── auth/
    └── ent/
```

### 3.2 测试数据类型

| 类型 | 存储方式 | 示例 | 用途 |
|------|---------|------|------|
| 基础数据 | Django Fixtures | `users.json`, `enterprises.json` | 预置用户、企业、字典等基础数据 |
| 业务数据 | YAML + Python | `sms_send.yml`, `login.yml` | 参数化请求数据、预期结果 |
| 边界数据 | YAML | `boundary.yml` | 分页边界、超长字符串、特殊字符 |
| 异常数据 | SQL 脚本 | `sms_expired.sql` | 构造过期验证码、黑名单Token |

### 3.3 变量引用规则

| 语法 | 说明 | 示例 |
|------|------|------|
| `${var}` | 引用预定义变量 | `${valid_phone}` |
| `${PREV_xxx}` | 引用上一个用例提取的参数 | `${PREV_sms_code}` |
| `${now}` | 当前时间（运行时刻） | `${now} + 5min` |
| `${today}` | 当前日期 | `${today}` |
| `${uuid}` | 随机UUID | `${uuid}` |

---

## 4. Mock 策略

### 4.1 Mock 层级

| 层级    | Mock对象     | 实现方式                  | 使用场景       |
| ----- | ---------- | --------------------- | ---------- |
| L1/L2 | 短信服务 (SMS) | `unittest.mock.patch` | 默认所有短信相关测试 |


### 4.2 短信服务 Mock 方案

```python
# conftest.py
import pytest
from unittest.mock import patch, MagicMock
import re
from datetime import datetime, timedelta

# 预定义验证码存储（用于验证场景）
SMS_CODE_STORE = {}

def generate_sms_code():
    """生成6位数字验证码"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

@pytest.fixture(autouse=True)
def mock_sms_service(monkeypatch):
    """Mock短信服务"""
    def fake_send_sms(phone: str, template: str, **kwargs):
        code = generate_sms_code()
        expires_at = datetime.now() + timedelta(minutes=5)

        # 存储验证码用于后续验证
        SMS_CODE_STORE[phone] = {
            'code': code,
            'expires_at': expires_at,
            'used': False,
            'type': template
        }

        # 记录发送次数
        send_count_key = f"sms:send:count:{phone}"
        # ... 记录发送次数逻辑

        return {
            'code': code,
            'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S'),
            'send_status': True
        }

    monkeypatch.setattr("app.services.sms.SMSService.send", fake_send_sms)
    return SMS_CODE_STORE

@pytest.fixture
def mock_sms_with_limit(monkeypatch):
    """Mock短信服务 - 带每日次数限制"""
    daily_limit = {}

    def fake_send_sms(phone: str, template: str, **kwargs):
        today = datetime.now().strftime('%Y-%m-%d')

        # 检查当日发送次数
        key = f"{phone}:{today}"
        count = daily_limit.get(key, 0)

        if count >= 10:
            raise SMSLimitExceededException(f"每日发送次数已用尽: {count}/10")

        count += 1
        daily_limit[key] = count

        # 调用真实的发送逻辑或mock
        return {'code': '123456', 'send_status': True}

    monkeypatch.setattr("app.services.sms.SMSService.send", fake_send_sms)
    return daily_limit

@pytest.fixture
def mock_sms_expired(monkeypatch):
    """Mock短信服务 - 构造过期验证码"""
    def fake_send_sms(phone: str, template: str, **kwargs):
        # 创建已过期的验证码记录
        expired_time = datetime.now() - timedelta(minutes=10)

        with get_db_connection() as conn:
            cursor.execute("""
                INSERT INTO sms_codes (phone, code, type, used, created_at, expires_at)
                VALUES (%s, '888888', %s, 0, %s, %s)
            """, [phone, template, expired_time, expired_time + timedelta(minutes=5)])

        return {'send_status': True, 'code': '888888'}

    monkeypatch.setattr("app.services.sms.SMSService.send", fake_send_sms)
```

### 4.3 验证码超时时间计算

验证码超时时间**不写死**，按脚本运行时间动态计算：

```python
# validators/db_validators.py
def assert_sms_code_valid(db_record, expected_type):
    """验证短信验证码记录"""
    now = datetime.now()

    # 超时时间 = 创建时间 + 5分钟，不写死
    expected_expires = db_record['created_at'] + timedelta(minutes=5)

    assert db_record['code'].match(r'^\d{6}$'), "验证码应为6位数字"
    assert db_record['used'] == False, "验证码不应已被使用"
    assert db_record['expires_at'] > now, "验证码不应已过期"
    assert db_record['expires_at'] <= expected_expires + timedelta(seconds=1), "超时时间应为5分钟"
    assert db_record['type'] == expected_type, f"验证码类型应为{expected_type}"
```

---

## 5. 数据库校验规范

### 5.1 数据库校验时机

| 场景 | 必须进行数据库校验 |
|------|------------------|
| 发送验证码 | ✅ 验证码写入、次数记录 |
| 登录 | ✅ Token写入、用户状态 |
| 注册 | ✅ 用户创建 |
| 创建企业 | ✅ 企业记录、关联关系 |
| 发布商机 | ✅ 商机记录、状态变更 |
| 审核操作 | ✅ 多表状态联动 |
| 权限变更 | ✅ 角色表、关联表 |

### 5.2 常用数据库校验SQL

```sql
-- 校验1: 验证码记录存在且有效
SELECT id, phone, code, type, used, created_at, expires_at
FROM sms_codes
WHERE phone = '${phone}' AND type = '${type}' AND used = 0
ORDER BY created_at DESC LIMIT 1;

-- 校验2: 验证码已过期（用于异常测试）
SELECT id, phone, code, expires_at
FROM sms_codes
WHERE phone = '${phone}' AND expires_at < NOW() AND used = 0;

-- 校验3: 用户Token记录
SELECT id, user_id, access_token, refresh_token, expires_at
FROM auth_tokens
WHERE user_id = '${user_id}' AND revoked = 0;

-- 校验4: 企业状态流转
SELECT e.id, e.name, e.auth_status, e.audit_status,
       u.id as user_id, u.role as user_role
FROM enterprises e
JOIN users u ON e.create_user_id = u.id
WHERE e.id = '${ent_id}';

-- 校验5: 商机联系记录（防重复获取）
SELECT id, opp_id, user_id, contact_phone, created_at
FROM opp_contacts
WHERE opp_id = '${opp_id}' AND user_id = '${user_id}';

-- 校验6: 每日短信发送次数
SELECT COUNT(*) as send_count
FROM sms_send_log
WHERE phone = '${phone}' AND DATE(created_at) = CURDATE();
```

### 5.3 数据库校验辅助类

```python
# tests/integration/db/queries.py
class SmsCodeQueries:
    """短信验证码相关查询"""

    @staticmethod
    def find_valid_code(phone: str, code_type: str) -> dict:
        """查找有效验证码"""
        return db.query_one("""
            SELECT * FROM sms_codes
            WHERE phone = %s AND type = %s AND used = 0 AND expires_at > NOW()
            ORDER BY created_at DESC LIMIT 1
        """, [phone, code_type])

    @staticmethod
    def assert_code_valid(phone: str, code_type: str, expected_code: str = None):
        """断言验证码有效"""
        record = SmsCodeQueries.find_valid_code(phone, code_type)
        assert record is not None, f"找不到有效验证码: {phone}/{code_type}"

        if expected_code:
            assert record['code'] == expected_code, f"验证码不匹配"

        # 动态计算超时时间
        expires_at = record['expires_at']
        created_at = record['created_at']
        diff_minutes = (expires_at - created_at).total_seconds() / 60

        assert 4.9 <= diff_minutes <= 5.1, f"超时时间应为5分钟，实际: {diff_minutes}分钟"
        return record

    @staticmethod
    def find_expired_code(phone: str) -> dict:
        """查找过期验证码"""
        return db.query_one("""
            SELECT * FROM sms_codes
            WHERE phone = %s AND expires_at < NOW() AND used = 0
            ORDER BY created_at DESC LIMIT 1
        """, [phone])


class EnterpriseQueries:
    """企业相关查询"""

    @staticmethod
    def get_enterprise_with_user(ent_id: int) -> dict:
        """获取企业及关联用户信息"""
        return db.query_one("""
            SELECT e.*, u.id as user_id, u.role as user_role,
                   u.real_name as user_real_name
            FROM enterprises e
            JOIN users u ON e.create_user_id = u.id
            WHERE e.id = %s
        """, [ent_id])

    @staticmethod
    def assert_enterprise_status(ent_id: int, expected_auth_status: str,
                                 expected_audit_status: str, expected_user_role: str):
        """断言企业状态"""
        record = EnterpriseQueries.get_enterprise_with_user(ent_id)

        assert record['auth_status'] == expected_auth_status, \
            f"企业认证状态应为{expected_auth_status}，实际: {record['auth_status']}"
        assert record['audit_status'] == expected_audit_status, \
            f"企业审核状态应为{expected_audit_status}，实际: {record['audit_status']}"
        assert record['user_role'] == expected_user_role, \
            f"用户角色应为{expected_user_role}，实际: {record['user_role']}"
```

---

## 6. 参数关联设计

### 6.1 参数生命周期

```
用例A执行 → 提取参数 → 存储到context → 用例B引用 → 用例C引用 → ...
    ↓
  cleanup → 清除context
```

### 6.2 参数提取与传递

```python
# tests/integration/utils/parameter_linker.py
class ParameterLinker:
    """参数关联管理器"""

    def __init__(self):
        self._context = {}

    def extract(self, case_id: str, response: dict, extractors: list):
        """从响应中提取参数"""
        for ext in extractors:
            value = self._get_nested(response, ext['from'])
            self._context[ext['to']] = value
            self._context[f"{case_id}:{ext['to']}"] = value  # 带用例前缀

    def get(self, key: str, case_id: str = None) -> any:
        """获取参数值"""
        # 优先尝试: case_id:key
        if case_id:
            prefixed = f"{case_id}:{key}"
            if prefixed in self._context:
                return self._context[prefixed]

        # 其次尝试: key
        if key in self._context:
            return self._context[key]

        # 最后尝试: PREV_xxx (上一个用例的值)
        prev_key = f"PREV_{key}"
        if prev_key in self._context:
            return self._context[prev_key]

        raise KeyError(f"参数未找到: {key}")

    def set(self, key: str, value: any):
        """设置参数值"""
        self._context[key] = value

    def clear(self):
        """清空context"""
        self._context.clear()

# 全局实例
linker = ParameterLinker()
```

### 6.3 参数关联使用示例

```yaml
# 链路测试: TC-API-Chain-001 (完整企业入驻流程)
test_data:
  case_001_register:
    phone: "${test_phone_001}"
    steps:
      - action: POST /api/v1/auth/sms/send
        params: {phone: "${test_phone_001}", type: "register"}
      - action: POST /api/v1/auth/register
        params:
          phone: "${test_phone_001}"
          code: "${PREV_sms_code}"          # 引用上一步提取的验证码
          password: "Test123456"
          username: "测试用户"
    extractors:
      - from: response.body.data.user_id
        to: "${user_id}"
      - from: response.body.data.access_token
        to: "${guest_token}"

  case_002_create_enterprise:
    depends_on: [case_001_register]
    steps:
      - action: POST /api/v1/ent/create
        headers: {Authorization: "Bearer ${guest_token}"}
        params:
          name: "测试企业有限公司"
          credit_code: "${credit_code_unique}"
    validators:
      db:
        - table: enterprises
          conditions:
            create_user_id: "${user_id}"
          fields:
            audit_status: "PENDING"
            auth_status: "UNVERIFIED"
    extractors:
      - from: response.body.data.enterprise_id
        to: "${ent_id}"

  case_003_audit_approve:
    depends_on: [case_002_create_enterprise]
    steps:
      - action: POST /api/v1/auth/login/password
        params: {username: "${plat_admin_username}", password: "${plat_admin_password}"}
      - action: POST /api/v1/plat-admin/audit/${ent_id}/approve
        headers: {Authorization: "Bearer ${plat_admin_token}"}
    validators:
      db:
        - table: enterprises
          conditions: {id: "${ent_id}"}
          fields:
            audit_status: "APPROVED"
            auth_status: "VERIFIED"
        - table: users
          conditions: {id: "${user_id}"}
          fields:
            role: "ENT_ADMIN"
```

---

## 7. 测试用例（L1 API）

### 7.1 认证模块（auth）

#### 7.1.1 发送短信验证码

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-auth-001 | 发送登录验证码-成功 | 正例-有效手机号 | phone: `${valid_phone}`<br>type: `login` | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 0 | **API断言**:<br>- data.send_status = true<br>**DB校验**:<br>- sms_codes表: phone=`${valid_phone}`<br>- type=`login`<br>- used=false<br>- code=6位数字<br>- expires_at > now+4min<br>**清理**: 删除验证码记录 |
| TC-API-auth-002 | 发送登录验证码-超过每日限制 | 反例-10次限制 | phone: `${phone_daily_limit}`<br>type: `login`<br>**Mock**: 注入limit=10 | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 10001<br>message: "当日发送次数已用尽" | **Mock验证**:<br>- 检查daily_limit[phone] >= 10<br>**DB校验**:<br>- sms_send_log表当日count=10 |
| TC-API-auth-003 | 发送注册验证码-成功 | 正例-新手机号 | phone: `${new_phone}`<br>type: `register` | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 0 | **API断言**:<br>- data.send_status = true<br>**DB校验**:<br>- sms_codes表记录存在<br>- type=`register` |
| TC-API-auth-004 | 发送注册验证码-手机号已注册 | 反例-手机号重复 | phone: `${registered_phone}`<br>type: `register` | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 10002<br>message: "手机号已注册" | **API断言**:<br>- data.exists = true<br>**DB校验**:<br>- users表有记录 |
| TC-API-auth-005 | 发送密码重置验证码-成功 | 正例-已注册手机 | phone: `${valid_phone}`<br>type: `password_reset` | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 0 | **API断言**:<br>- data.send_status = true<br>**DB校验**:<br>- sms_codes.type=`password_reset` |
| TC-API-auth-006 | 发送密码重置验证码-未注册手机 | 反例-手机不存在 | phone: `${nonexistent_phone}`<br>type: `password_reset` | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 10003<br>message: "手机号未注册" | **API断言**:<br>- data.exists = false |

#### 7.1.2 短信验证码登录

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-auth-007 | 短信验证码登录-成功 | 正例-有效验证码 | phone: `${valid_phone}`<br>code: `${sms_code}` | POST /api/v1/auth/login/sms<br>{phone, code} | HTTP 200<br>code: 0<br>含access_token | **API断言**:<br>- data.access_token != null<br>- data.refresh_token != null<br>- data.expires_in = 7200<br>**DB校验**:<br>- sms_codes.used=true<br>- auth_tokens记录存在<br>**参数提取**:<br>- access_token → `${login_token}`<br>- user_id → `${login_user_id}` |
| TC-API-auth-008 | 短信验证码登录-验证码错误 | 反例-错误验证码 | phone: `${valid_phone}`<br>code: `000000` | POST /api/v1/auth/login/sms<br>{phone, code} | HTTP 200<br>code: 10004<br>message: "验证码无效" | **API断言**:<br>- data.access_token = null<br>**DB校验**:<br>- sms_codes.used保持false |
| TC-API-auth-009 | 短信验证码登录-验证码过期 | 异常-验证码超时 | phone: `${valid_phone}`<br>code: `${expired_code}`<br>**前置**: 创建过期验证码 | POST /api/v1/auth/login/sms<br>{phone, code} | HTTP 200<br>code: 10005<br>message: "验证码已过期" | **DB校验**:<br>- sms_codes.expires_at < now<br>- sms_codes.used保持false |
| TC-API-auth-010 | 短信验证码登录-验证码已使用 | 异常-重复使用 | phone: `${valid_phone}`<br>code: `${used_code}`<br>**前置**: 验证码已使用 | POST /api/v1/auth/login/sms<br>{phone, code} | HTTP 200<br>code: 10006<br>message: "验证码已使用" | **DB校验**:<br>- sms_codes.used=true |
| TC-API-auth-011 | 短信验证码登录-手机号未注册 | 反例-用户不存在 | phone: `${nonexistent_phone}`<br>code: `123456` | POST /api/v1/auth/login/sms<br>{phone, code} | HTTP 200<br>code: 10007<br>message: "用户不存在" | |

#### 7.1.3 账号密码登录

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-auth-012 | 账号密码登录-成功 | 正例-正确密码 | username: `${valid_username}`<br>password: `${valid_password}` | POST /api/v1/auth/login/password<br>{username, password} | HTTP 200<br>code: 0<br>含JWT Token | **API断言**:<br>- data.access_token != null<br>- data.user_id != null<br>**DB校验**:<br>- auth_tokens记录存在 |
| TC-API-auth-013 | 账号密码登录-密码错误 | 反例-密码错误 | username: `${valid_username}`<br>password: `WrongPass123` | POST /api/v1/auth/login/password<br>{username, password} | HTTP 200<br>code: 10008<br>message: "密码错误" | **API断言**:<br>- data.access_token = null<br>**DB校验**:<br>- auth_tokens无新记录 |
| TC-API-auth-014 | 账号密码登录-用户不存在 | 反例-用户不存在 | username: `nonexistent_user`<br>password: `AnyPass123` | POST /api/v1/auth/login/password<br>{username, password} | HTTP 200<br>code: 10007<br>message: "用户不存在" | |

#### 7.1.4 Token刷新

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-auth-015 | Token刷新-成功 | 正例-有效refresh_token | refresh_token: `${valid_refresh_token}` | POST /api/v1/auth/token/refresh<br>{refresh_token} | HTTP 200<br>code: 0<br>含新access_token | **API断言**:<br>- data.access_token != 原token<br>- data.refresh_token != 原refresh_token<br>**DB校验**:<br>- 原refresh_token.revoked=true<br>- 新tokens记录存在 |
| TC-API-auth-016 | Token刷新-token已加入黑名单 | 反例-旧token复用 | refresh_token: `${blacklisted_token}` | POST /api/v1/auth/token/refresh<br>{refresh_token} | HTTP 200<br>code: 10009<br>message: "Token无效" | **DB校验**:<br>- token_blacklist表有记录 |
| TC-API-auth-017 | Token刷新-token过期 | 反例-超长未刷新 | refresh_token: `${expired_refresh_token}` | POST /api/v1/auth/token/refresh<br>{refresh_token} | HTTP 200<br>code: 10010<br>message: "Token已过期" | **DB校验**:<br>- auth_tokens.expires_at < now |

#### 7.1.5 注册与密码重置

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-auth-018 | 注册账号-成功 | 正例-完整信息 | phone: `${new_phone}`<br>code: `${sms_code}`<br>password: `Test123456`<br>username: `newuser` | POST /api/v1/auth/register<br>{phone, code, password, username} | HTTP 200<br>code: 0<br>含JWT Token | **API断言**:<br>- data.user_id != null<br>- data.access_token != null<br>**DB校验**:<br>- users表: phone=`${new_phone}`<br>- users.role=`GUEST`<br>- sms_codes.used=true<br>**提取**:<br>- user_id → `${new_user_id}` |
| TC-API-auth-019 | 注册账号-验证码错误 | 反例-验证码错误 | phone: `${new_phone}`<br>code: `000000`<br>password: `Test123456`<br>username: `newuser` | POST /api/v1/auth/register<br>{phone, code, ...} | HTTP 200<br>code: 10004 | **DB校验**:<br>- users表无新记录 |
| TC-API-auth-020 | 注册账号-手机号已注册 | 反例-手机号重复 | phone: `${registered_phone}`<br>code: `123456`<br>password: `Test123456`<br>username: `newuser` | POST /api/v1/auth/register<br>{phone, code, ...} | HTTP 200<br>code: 10002 | **DB校验**:<br>- users表无新记录 |
| TC-API-auth-021 | 修改密码-成功 | 正例-有效验证码 | phone: `${valid_phone}`<br>code: `${sms_code}`<br>new_password: `NewPass123` | POST /api/v1/auth/password/reset<br>{phone, code, new_password} | HTTP 200<br>code: 0 | **DB校验**:<br>- users.password已更新<br>- sms_codes.used=true |
| TC-API-auth-022 | 修改密码-未认证 | 反例-无认证 | phone: `${valid_phone}`<br>code: `123456`<br>new_password: `NewPass123`<br>**前置**: 无效用户 | POST /api/v1/auth/password/reset<br>{phone, code, new_password} | HTTP 200<br>code: 10003 | |

#### 7.1.6 登出与用户信息

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-auth-023 | 登出-成功 | 正例-有效token | Authorization: `Bearer ${valid_token}` | POST /api/v1/auth/logout | HTTP 200<br>code: 0 | **DB校验**:<br>- auth_tokens.revoked=true<br>- refresh_token在黑名单 |
| TC-API-auth-024 | 登出-无效token | 反例-token无效 | Authorization: `Bearer invalid_token` | POST /api/v1/auth/logout | HTTP 401 | |
| TC-API-auth-025 | 获取当前用户信息-已登录 | 正例-有效token | Authorization: `Bearer ${valid_token}` | GET /api/v1/auth/me | HTTP 200<br>code: 0<br>含用户信息 | **API断言**:<br>- data.user_id != null<br>- data.phone != null<br>- data.role != null |
| TC-API-auth-026 | 获取当前用户信息-未登录 | 反例-无token | 无 | GET /api/v1/auth/me | HTTP 401 | |

---

### 7.2 企业名录（ent）- L1 API 测试

#### 7.2.1 企业列表

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-ent-001 | 获取企业列表-成功 | 正例-公开浏览 | page: 1<br>page_size: 10 | GET /api/v1/ent/list | HTTP 200<br>含企业列表 | **API断言**:<br>- data.items[].name != null<br>- data.total > 0 |
| TC-API-ent-002 | 获取企业列表-按行业筛选 | 正例-筛选条件 | industry_id: 1<br>sub_industry_id: 2 | GET /api/v1/ent/list<br>?industry_id=1&sub_industry_id=2 | HTTP 200<br>仅返回该行业企业 | **API断言**:<br>- 所有items.industry_id=1<br>- 所有items.sub_industry_id=2 |
| TC-API-ent-003 | 获取企业列表-按认证状态筛选 | 正例-认证企业 | auth_status: VERIFIED | GET /api/v1/ent/list<br>?auth_status=VERIFIED | HTTP 200<br>仅已认证企业 | **API断言**:<br>- 所有items.auth_status=VERIFIED |
| TC-API-ent-004 | 获取企业列表-关键词搜索 | 正例-搜索 | keyword: "科技" | GET /api/v1/ent/list<br>?keyword=科技 | HTTP 200<br>返回匹配企业 | **API断言**:<br>- items[].name含"科技"<br>  或description含"科技" |
| TC-API-ent-005 | 获取企业列表-分页 | 边界值-分页 | page: 1<br>page_size: 10 | GET /api/v1/ent/list<br>?page=1&page_size=10 | HTTP 200<br>返回10条 | **API断言**:<br>- len(items) = 10<br>- data.has_more = true |
| TC-API-ent-006 | 获取企业列表-空结果 | 正例-无匹配 | auth_status: NONEXISTENT | GET /api/v1/ent/list<br>?auth_status=NONEXISTENT | HTTP 200<br>items=[] | **API断言**:<br>- data.items = []<br>- data.total = 0 |

#### 7.2.2 企业详情

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-ent-007 | 获取企业详情-已认证企业 | 正例-完整信息 | ent_id: `${verified_ent_id}` | GET /api/v1/ent/{id} | HTTP 200<br>含商机列表 | **API断言**:<br>- data.contact_phone != null<br>- data.opportunities[]存在<br>**DB校验**:<br>- enterprises.auth_status=VERIFIED |
| TC-API-ent-008 | 获取企业详情-未认证企业 | 正例-脱敏信息 | ent_id: `${unverified_ent_id}` | GET /api/v1/ent/{id} | HTTP 200<br>联系方式为空 | **API断言**:<br>- data.contact_phone = null<br>- data.opportunities = [] |
| TC-API-ent-009 | 获取企业详情-企业不存在 | 反例-ID无效 | ent_id: 999999 | GET /api/v1/ent/999999 | HTTP 404<br>code: 20001 | |

#### 7.2.3 企业认领与创建

| 用例ID | 用例名称 | 测试场景 | 测试数据 | 操作步骤 | 预期结果 | 验证步骤 |
|--------|----------|----------|----------|----------|----------|----------|
| TC-API-ent-010 | 认领企业-成功 | 正例-未认领企业 | credit_code: `${unclaimed_code}`<br>Authorization: `Bearer ${user_token}` | POST /api/v1/ent/claim<br>{credit_code, ...} | HTTP 200<br>code: 0<br>audit_status=PENDING | **API断言**:<br>- data.ent_id != null<br>- data.audit_status=PENDING<br>**DB校验**:<br>- enterprises.audit_status=PENDING<br>- enterprises.create_user_id=当前用户 |
| TC-API-ent-011 | 认领企业-已认领 | 反例-重复认领 | credit_code: `${claimed_code}` | POST /api/v1/ent/claim<br>{credit_code, ...} | HTTP 200<br>code: 20002<br>message: "企业已被认领" | **DB校验**:<br>- enterprises.create_user_id != 当前用户 |
| TC-API-ent-012 | 创建企业-成功 | 正例-新企业 | name: "新企业"<br>credit_code: `${unique_code}`<br>Authorization: `Bearer ${user_token}` | POST /api/v1/ent/create<br>{name, credit_code, ...} | HTTP 200<br>code: 0<br>待审核 | **API断言**:<br>- data.ent_id != null<br>**DB校验**:<br>- enterprises.name="新企业"<br>- enterprises.audit_status=PENDING |
| TC-API-ent-013 | 创建企业-信用代码重复 | 反例-代码已存在 | credit_code: `${existing_code}` | POST /api/v1/ent/create<br>{credit_code: existing_code} | HTTP 200<br>code: 20003<br>message: "统一社会信用代码已存在" | **DB校验**:<br>- 仅1条enterprise记录 |

---

### 7.3 复杂链路测试

#### TC-API-Chain-001: 完整企业入驻流程

| 阶段 | 用例 | 操作 | 预期结果 | DB验证 |
|------|------|------|----------|--------|
| 1.注册 | TC-API-auth-018 | POST /auth/register | 成功，返回user_id, token | users.role=GUEST |
| 2.创建企业 | TC-API-ent-012 | POST /ent/create<br>Header: Bearer ${token} | 成功，返回ent_id, audit_status=PENDING | enterprises.audit_status=PENDING<br>enterprises.auth_status=UNVERIFIED |
| 3.平台登录 | TC-API-auth-012 | POST /auth/login/password<br>(plat_admin) | 成功，返回admin_token | — |
| 4.审核通过 | TC-API-platadmin-006 | POST /plat-admin/audit/{ent_id}/approve<br>Header: Bearer ${admin_token} | 成功 | enterprises.audit_status=APPROVED<br>enterprises.auth_status=VERIFIED |
| 5.用户角色变更 | — | 审核通过后自动触发 | — | users.role=ENT_ADMIN |
| 6.发布商机 | TC-API-opp-009 | POST /opp/publish<br>Header: Bearer ${user_token} | 成功 | opportunities.status=PUBLISHED |

**验证点**:
- 步骤4后: `EnterpriseQueries.assert_enterprise_status(ent_id, 'VERIFIED', 'APPROVED', 'ENT_ADMIN')`
- 步骤6前: 用户已具备企业管理员权限，可正常发布商机

#### TC-API-Chain-002: Token刷新链路

| 阶段 | 用例 | 操作 | 预期结果 | DB验证 |
|------|------|------|----------|--------|
| 1.登录 | TC-API-auth-007 | POST /auth/login/sms | 成功，返回tokens | auth_tokens.expires_at = now+2h |
| 2.刷新Token | TC-API-auth-015 | POST /auth/token/refresh | 成功，返回新tokens | 原refresh_token.revoked=true |
| 3.使用旧refresh | TC-API-auth-016 | POST /auth/token/refresh<br>(用旧token) | 失败，Token无效 | token_blacklist有记录 |
| 4.使用新refresh | TC-API-auth-015 | POST /auth/token/refresh<br>(用新token) | 成功 | — |

---

## 8. 测试用例（L2 E2E）

### 8.1 E2E 用例模板

```yaml
用例ID: TC-E2E-{序号}
用例名称: {描述}
前置条件:
  - 已登录 / 已认证用户 / 已创建企业 / ...
操作步骤:
  - step: 1
    action: 点击元素 / 输入文本 / API调用
    selector: "#login-phone" / "登录按钮"
    value: "${phone}"
  - step: 2
    action: API调用
    method: POST
    url: /api/v1/auth/sms/send
    body: {phone: "${phone}"}
预期结果:
  - 页面跳转到首页
  - 显示用户头像
截图:
  - TC-E2E-xxx-步骤1-登录成功.png
  - TC-E2E-xxx-步骤2-进入首页.png
```

### 8.2 冒烟测试用例

| 用例ID | 用例名称 | 冒烟 | 操作步骤 | 预期结果 | 截图 |
|--------|----------|:----:|----------|----------|------|
| TC-E2E-001 | 短信验证码登录 | ✅ | 1. 打开登录页<br>2. 输入手机号<br>3. 点击获取验证码<br>4. 输入验证码(123456)<br>5. 点击登录 | 登录成功，跳转首页，显示用户信息 | ✅ |
| TC-E2E-002 | 账号密码登录 | ✅ | 1. 打开登录页<br>2. 输入用户名/密码<br>3. 点击登录 | 登录成功，跳转首页 | ✅ |
| TC-E2E-003 | 注册新账号 | ✅ | 1. 打开注册页<br>2. 输入手机号/验证码/密码/用户名<br>3. 点击注册 | 注册成功，自动登录 | ✅ |
| TC-E2E-004 | 浏览企业名录 | ✅ | 1. 首页点击"企业名录"<br>2. 筛选行业/省份<br>3. 点击企业查看详情 | 显示企业列表和详情 | ✅ |
| TC-E2E-005 | 认领企业 | ✅ | 1. 搜索未认领企业<br>2. 点击"认领"<br>3. 填写认证信息<br>4. 提交认证 | 提交成功，等待审核 | ✅ |
| TC-E2E-006 | 发布商机 | ✅ | 1. 进入企业工作台<br>2. 点击"商机管理"<br>3. 点击"发布商机"<br>4. 填写商机信息<br>5. 提交发布 | 商机发布成功 | ✅ |
| TC-E2E-007 | 获取商机联系方式 | ✅ | 1. 商机广场浏览商机<br>2. 点击"查看详情"<br>3. 点击"获取联系方式" | 显示联系方式 | ✅ |
| TC-E2E-008 | 发布动态 | ✅ | 1. 进入校友圈<br>2. 点击"发布动态"<br>3. 填写内容并上传图片<br>4. 提交发布 | 动态发布成功 | ✅ |
| TC-E2E-009 | 企业管理员添加员工 | ✅ | 1. 进入企业工作台<br>2. 点击"员工管理"<br>3. 点击"添加员工"<br>4. 填写员工信息<br>5. 提交添加 | 员工添加成功 | ✅ |
| TC-E2E-010 | 企业管理员编辑企业信息 | ✅ | 1. 进入企业工作台<br>2. 点击"企业信息"<br>3. 编辑企业简介<br>4. 保存修改 | 信息更新成功 | ✅ |
| TC-E2E-011 | 平台运营审核企业 | ✅ | 1. 进入管理后台<br>2. 点击"企业审核"<br>3. 查看待审核企业<br>4. 点击"通过" | 企业审核通过 | ✅ |
| TC-E2E-013 | 全局搜索功能 | ✅ | 1. 首页搜索框输入关键词<br>2. 点击搜索 | 显示搜索结果 | ✅ |
| TC-E2E-015 | 登出功能 | ✅ | 1. 点击用户头像<br>2. 点击"退出登录" | 退出登录，跳转登录页 | ✅ |

### 8.3 核心功能测试用例

| 用例ID | 用例名称 | 操作步骤 | 预期结果 | 截图 |
|--------|----------|----------|----------|------|
| TC-E2E-012 | 平台运营下架商机 | 1. 进入管理后台<br>2. 点击"商机内容管理"<br>3. 选择商机并下架 | 商机已下架 | ✅ |
| TC-E2E-014 | 消息通知查看 | 1. 点击顶部铃铛图标<br>2. 查看最近通知<br>3. 点击单条查看详情<br>4. 点击"全部已读" | 通知显示并标记已读 | ✅ |
| TC-E2E-016 | Token自动刷新 | 1. 登录系统<br>2. 等待access_token即将过期<br>3. 继续操作 | 操作不中断，Token自动刷新 | ✅ |
| TC-E2E-017 | 登录失败-验证码错误 | 1. 打开登录页<br>2. 输入手机号<br>3. 获取验证码<br>4. 输入错误验证码<br>5. 点击登录 | 提示"验证码错误" | ✅ |
| TC-E2E-018 | 登录失败-密码错误 | 1. 打开登录页<br>2. 输入错误密码<br>3. 点击登录 | 提示"密码错误" | ✅ |
| TC-E2E-019 | 发布商机-未绑定企业 | 1. 未认领企业<br>2. 进入企业工作台<br>3. 点击"发布商机" | 提示"请先认领或创建企业" | ✅ |
| TC-E2E-020 | 访问管理后台-无权限 | 1. 已登录企业用户<br>2. 尝试访问管理后台URL | 提示"权限不足" | ✅ |

---

## 9. 测试用例统计

| 模块 | L1 API | L2 E2E | 合计 |
|------|--------|--------|------|
| 认证模块（auth） | 26 | 5 | 31 |
| 公共接口（public） | 1 | 0 | 1 |
| 企业名录（ent） | 13 | 2 | 15 |
| 商机广场（opp） | 16 | 2 | 18 |
| 校友圈（feed） | 10 | 1 | 11 |
| 企业工作台（ent-admin） | 23 | 3 | 26 |
| 平台管理（plat-admin） | 28 | 3 | 31 |
| 搜索（search） | 3 | 1 | 4 |
| 消息通知（msg） | 7 | 1 | 8 |
| 复杂链路 | 2 | 0 | 2 |
| **合计** | **129** | **18** | **147** |

---

## 10. 测试环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10 Pro |
| Python | 3.11+ |
| Node.js | 18+ |
| Django | 4.2+ |
| MySQL | 8.0+ |
| 数据库 | 独立测试库 `xlt_test`，禁止使用生产库（RL-DV-0005） |
| 测试数据 | 独立测试数据集，通过 fixtures 预置 |
| 前端 | Vue3 + Element Plus 开发服务器 |
| 浏览器 | Chrome/Edge（E2E 测试） |

---

## 11. 测试执行计划

### 11.1 M4 测试阶段执行顺序

1. **测试环境部署**（M4 进入时）
   - 部署独立测试数据库 `xlt_test`
   - 执行 Django migrations
   - 加载 fixtures 基础数据

2. **L1 API 测试**（优先执行）
   - 按模块执行：认证 → 企业 → 商机 → 校友圈 → 企业工作台 → 平台管理 → 搜索 → 消息
   - 链路测试单独执行（TC-API-Chain-001, TC-API-Chain-002）
   - 发现 bug 则记录并继续执行后续测试

3. **L2 E2E 测试**（L1 API 全部通过后执行）
   - 冒烟测试用例优先执行
   - 核心流程全部通过后执行剩余用例

### 11.2 Bug 修复流程

- E2E 测试发现 bug 时，触发 `/m3-subagent-development` 进行修复
- 修复完成后重新执行相关测试用例

---

## 12. 准出条件

| 检查项 | 要求 |
|--------|------|
| L1 API 测试用例执行率 | 100% |
| L1 API 测试用例通过率 | 100% |
| L2 E2E 测试用例执行率 | 100% |
| L2 E2E 测试用例通过率 | 100% |
| 数据库校验覆盖率 | 100%（涉及数据持久化的接口） |
| Mock使用覆盖率 | 100%（外部服务调用） |
| 测试报告 | 包含实际执行结果、截图、数据库验证结果 |
| QA 签署 | 报告末尾有 QA 审查结论 |

---

*文档结束*
