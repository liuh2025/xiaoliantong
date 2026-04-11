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

| 用例ID            | 用例名称            | 测试场景     | 测试数据                                                                   | 操作步骤                                        | 预期结果                                            | 验证步骤                                                                                                                                                                                        |
| --------------- | --------------- | -------- | ---------------------------------------------------------------------- | ------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TC-API-auth-001 | 发送登录验证码-成功      | 正例-有效手机号 | phone: `${valid_phone}`<br>type: `login`                               | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 0                             | **API断言**:<br>- data.send_status = true<br>**DB校验**:<br>- sms_codes表: phone=`${valid_phone}`<br>- type=`login`<br>- used=false<br>- code=6位数字<br>- expires_at > now+4min<br>**清理**: 删除验证码记录 |
| TC-API-auth-002 | 发送登录验证码-超过每日限制  | 反例-10次限制 | phone: `${phone_daily_limit}`<br>type: `login`<br>**Mock**: 注入limit=10 | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 10001<br>message: "当日发送次数已用尽" | **Mock验证**:<br>- 检查daily_limit[phone] >= 10<br>**DB校验**:<br>- sms_send_log表当日count=10                                                                                                       |
| TC-API-auth-003 | 发送注册验证码-成功      | 正例-新手机号  | phone: `${new_phone}`<br>type: `register`                              | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 0                             | **API断言**:<br>- data.send_status = true<br>**DB校验**:<br>- sms_codes表记录存在<br>- type=`register`                                                                                               |
| TC-API-auth-004 | 发送注册验证码-手机号已注册  | 反例-手机号重复 | phone: `${registered_phone}`<br>type: `register`                       | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 10002<br>message: "手机号已注册"    | **API断言**:<br>- data.exists = true<br>**DB校验**:<br>- users表有记录                                                                                                                              |
| TC-API-auth-005 | 发送密码重置验证码-成功    | 正例-已注册手机 | phone: `${valid_phone}`<br>type: `password_reset`                      | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 0                             | **API断言**:<br>- data.send_status = true<br>**DB校验**:<br>- sms_codes.type=`password_reset`                                                                                                   |
| TC-API-auth-006 | 发送密码重置验证码-未注册手机 | 反例-手机不存在 | phone: `${nonexistent_phone}`<br>type: `password_reset`                | POST /api/v1/auth/sms/send<br>{phone, type} | HTTP 200<br>code: 10003<br>message: "手机号未注册"    | **API断言**:<br>- data.exists = false                                                                                                                                                         |

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

| 阶段           | 用例              | 操作                                    | 预期结果         | DB验证                            |
| ------------ | --------------- | ------------------------------------- | ------------ | ------------------------------- |
| 1.登录         | TC-API-auth-007 | POST /auth/login/sms                  | 成功，返回tokens  | auth_tokens.expires_at = now+2h |
| 2.刷新Token    | TC-API-auth-015 | POST /auth/token/refresh              | 成功，返回新tokens | 原refresh_token.revoked=true     |
| 3.使用旧refresh | TC-API-auth-016 | POST /auth/token/refresh<br>(用旧token) | 失败，Token无效   | token_blacklist有记录              |
| 4.使用新refresh | TC-API-auth-015 | POST /auth/token/refresh<br>(用新token) | 成功           | —                               |

---

## 8. 测试用例（L2 E2E）

> **详细用例文档**: [E2E 测试用例详细设计](floating-dazzling-feigenbaum.md)

### 8.0 测试前置条件检查（必读）

> **WARNING**: 执行任何 E2E 测试用例前，必须逐项确认以下条件已满足。如有不满足项，须先准备测试数据，否则用例将因数据缺失而失败。

#### 8.0.1 环境就绪检查

| 序号 | 检查项 | 检查方法 | 不满足时的处理 |
|:----:|--------|----------|--------------|
| 1 | 后端服务已启动 | `curl http://localhost:8000/api/v1/public/stats` 返回 200 | `cd src/backend && python manage.py runserver 0.0.0.0:8000` |
| 2 | 前端服务已启动 | `curl http://localhost:3000` 返回 200 | `cd frontend && npm run dev` |
| 3 | 数据库 migration 已执行 | `python manage.py showmigrations` 无 `[X]` 待执行项 | `python manage.py migrate` |
| 4 | 基础数据字典已加载 | 行业/品类/标签/地区表有数据 | 执行 fixtures 或通过管理后台录入 |

#### 8.0.2 测试账号准备

| 账号类型 | 手机号 | 密码 | 角色 | 用途 | 准备方式 |
|----------|--------|------|------|------|----------|
| 平台超级管理员 | 13800000001 | Admin123! | `SUPER_ADMIN` | 第12~19章测试 | 执行 `python manage.py createsuperuser` 或 fixtures |
| 平台运营 | 13800000002 | Admin123! | `PLATFORM_OPERATOR` | 第13~16章审核测试 | 通过超管后台创建 |
| 企业管理员（已认证） | 13900000001 | Ent123! | `ENT_ADMIN` | 第9~11章企业管理测试 | 注册 → 创建企业 → 超管审核通过 |
| 企业普通员工 | 13900000002 | Ent123! | `EMPLOYEE` | 员工相关测试 | 企业管理员添加 |
| 未绑定企业用户 | 13700000001 | User123! | `GUEST` | 第20章权限测试 | 注册即可 |
| 无企业用户（用于第2章注册测试） | — | — | — | 新注册测试 | 无需预创建 |

#### 8.0.3 业务数据准备

| 数据项 | 要求 | 影响章节 | 准备方式 |
|--------|------|----------|----------|
| 已认证企业 ≥1 家 | auth_status=VERIFIED, 企业管理员已绑定 | 第3~7章, 第9~11章 | 注册企业管理员 → 创建企业 → 超管审核通过 |
| 未认证企业 ≥1 家 | auth_status=UNVERIFIED | 第13章审核测试 | 创建企业后不审核 |
| 生效中的商机 ≥5 条 | status=PUBLISHED，类型包含"我要买"和"我能供" | 第3~4章商机列表, 第7章搜索 | 企业管理员发布 |
| 已发布动态 ≥3 条 | status=NORMAL | 第3章校友动态, 第6章校友圈 | 已登录用户发布 |
| 未读通知 ≥3 条 | is_read=false | 第3.10节, 第8章通知页 | 触发审核/商机查看等业务动作 |
| 基础数据字典 | 行业≥3个一级+二级，地区≥3省+市，品类≥3个，标签≥5个 | 第4~5章筛选, 第17章字典 | fixtures 或管理后台录入 |

#### 8.0.4 检查脚本（建议在测试前执行）

```bash
# 1. 检查后端
curl -s http://localhost:8000/api/v1/public/stats | python -m json.tool

# 2. 检查前端
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

# 3. 检查数据库 migration
cd src/backend && python manage.py showmigrations --plan 2>&1 | grep "\[ \]" && echo "存在未执行迁移!" || echo "迁移全部完成"

# 4. 检查测试账号可登录
curl -s -X POST http://localhost:8000/api/v1/auth/login/password \
  -H "Content-Type: application/json" \
  -d '{"phone":"13900000001","password":"Ent123!"}' | python -m json.tool
```

---

### 8.1 用例总览（20章 × 全页面覆盖）

> 以下为用例摘要，**完整步骤与预期结果**见 [floating-dazzling-feigenbaum.md](floating-dazzling-feigenbaum.md)。

| 章节 | 模块 | 页面原型 | 前提条件 | 关键测试点 |
|------|------|----------|----------|-----------|
| 第1章 | 登录 | login.html | 用户未登录 | 短信登录、密码登录、忘记密码、Tab切换、弹窗关闭 |
| 第2章 | 注册 | register.html | 用户未登录 | 页面展示、表单校验（5项）、注册成功跳转 |
| 第3章 | 首页 | index.html | 已登录 | Header结构、Hero区、统计卡片、推荐列表、发布商机弹窗、获取联系方式、企业Drawer、通知面板、用户菜单、搜索跳转 |
| 第4章 | 商机广场 | opportunity.html | 已登录 | 页面结构、筛选侧边栏（类型/行业级联/品类/地区级联）、已选摘要、重置、商机卡片、分页、发布弹窗、获取联系方式 |
| 第5章 | 企业名录 | enterprise.html | 已登录 | 页面结构、筛选（行业/品类/地区/热门标签）、企业卡片、分页、认领弹窗（两步式）、创建弹窗、企业详情Drawer |
| 第6章 | 校友圈 | feeds.html | 已登录 | 页面展示、动态卡片、发布动态 |
| 第7章 | 搜索 | search.html | — | 搜索页面、三Tab切换、重新搜索 |
| 第8章 | 通知消息 | notification.html | 已登录 | 页面展示、通知列表、未读/已读、全部已读 |
| 第9章 | 企业信息维护 | enterprise-admin/enterprise-info.html | 企业管理员登录 | Admin侧边栏、只读/可编辑字段、保存/取消 |
| 第10章 | 员工管理 | enterprise-admin/employee.html | 企业管理员登录 | 员工列表、新增弹窗、编辑弹窗、重置密码、解绑 |
| 第11章 | 商机管理 | enterprise-admin/my-opportunity.html | 企业管理员登录 | 列表筛选、编辑弹窗、下架/重新发布 |
| 第12章 | 数据大盘 | platform-admin/dashboard.html | 平台管理员登录 | 侧边栏4分组、统计卡片4项、趋势图 |
| 第13章 | 企业审核 | platform-admin/audit.html | 平台管理员登录 | 审核列表Tab切换、审核弹窗（通过/驳回） |
| 第14章 | 租户管理 | platform-admin/tenant.html | 平台管理员登录 | 租户列表、成员管理弹窗、新增成员、禁用/启用 |
| 第15章 | 商机内容管理 | platform-admin/opportunity-manage.html | 平台管理员登录 | 列表筛选、查看详情弹窗、强制下架 |
| 第16章 | 动态内容管理 | platform-admin/feeds-manage.html | 平台管理员登录 | 列表筛选、查看/下架 |
| 第17章 | 基础数据字典 | platform-admin/master-data.html | 平台管理员登录 | 4个Tab（行业/品类/标签/区划）、树形CRUD |
| 第18章 | 权限管理 | platform-admin/rbac.html | 超级管理员登录 | 5个角色卡片、权限矩阵（3系统Tab） |
| 第19章 | 系统设置 | platform-admin/settings.html | 超级管理员登录 | 基础设置、安全策略（Phase 2禁用）、保存/重置 |
| 第20章 | 全局交互 | — | 多种角色 | 导航一致性、通知一致性、菜单一致性、弹窗遮罩、登出、未登录保护、权限不足 |

### 8.2 用例格式说明

每个用例采用 `前提/步骤/预期` 格式（参考 EACheck 项目测试用例规范）：

```markdown
**前提：** [前置条件]

- 步骤：[具体操作]
- 预期：[验证点1]
- 预期：[验证点2]
- 预期：[验证点3]
```

特点：
- 每个步骤可列出多个预期结果，确保全面验证
- 前提条件与 8.0 节的前置条件检查对应
- 操作步骤细化到具体元素（按钮、输入框、Tab、级联选择器等）
- 预期结果覆盖页面展示、交互行为、API调用、状态变化

### 8.3 各章节测试用例

> 完整内容见 [floating-dazzling-feigenbaum.md](floating-dazzling-feigenbaum.md)，以下为各章摘要。

#### 第1章 登录模块（login.html）

**前提：** 用户未登录

| 用例 | 测试点 |
|------|--------|
| 1.1 短信验证码登录 | 页面渲染（蓝色渐变+卡片+Tab+表单）、空手机号校验、不足11位校验、正确手机号输入、获取验证码（60s倒计时+disabled）、输入验证码、7天免登录、登录成功弹窗 |
| 1.2 密码登录 | Tab切换、表单切换、密码明文/密文切换、登录成功 |
| 1.3 忘记密码 | 两步式弹窗（验证码→重置密码）、密码长度校验、两次不一致校验、重置成功弹窗 |
| 1.4 Tab切换数据独立 | 两个表单数据互不影响 |
| 1.5 弹窗关闭 | ✕按钮关闭、遮罩层关闭 |

#### 第2章 注册模块（register.html）

**前提：** 用户未登录

| 用例 | 测试点 |
|------|--------|
| 2.1 页面展示 | 卡片（480px）、4个必填字段、协议复选框（蓝色链接）、"立即登录"链接 |
| 2.2 校验 | 空表单、缺验证码、密码<8位、两次不一致、未勾协议（5项校验） |
| 2.3 注册成功 | 提示成功、1.5秒跳转login.html |

#### 第3章 首页模块（index.html）

**前提：** 已登录，需已认证企业+商机+动态+通知数据

| 用例 | 测试点 |
|------|--------|
| 3.1 Header结构 | Logo、导航4项（首页active）、搜索框、铃铛+徽标3、用户头像 |
| 3.2 Hero区域 | 大标题、副标题、两个发布按钮、热门检索标签5个 |
| 3.3 统计卡片 | 4项统计（企业/商机/撮合/用户） |
| 3.4 智能匹配推荐 | 标题+链接、2列商机卡片（类型标签+标题+标签组+企业+地区） |
| 3.5 侧边栏-新入驻企业 | 标题+链接、企业列表 |
| 3.6 侧边栏-校友动态 | 标题+链接、动态条目 |
| 3.7 发布商机弹窗 | 弹窗表单完整字段、类型radio切换、填写提交 |
| 3.8 获取联系方式 | 确认弹窗、结果弹窗（联系人+手机+微信+复制） |
| 3.9 企业详情Drawer | 550px Drawer、基础信息、简介、商机列表 |
| 3.10 通知下拉面板 | 360px面板、通知列表、全部已读、查看全部链接 |
| 3.11 用户菜单 | 下拉菜单3项、外部关闭 |
| 3.12 搜索跳转 | 输入搜索→跳转、热门标签点击→跳转 |

#### 第4章 商机广场模块（opportunity.html）

**前提：** 已登录，需基础数据字典+商机数据

| 用例 | 测试点 |
|------|--------|
| 4.1 页面结构 | Header active、标题副标题、两个发布按钮、筛选栏+列表 |
| 4.2 筛选-商机类型 | 全部/我要买/我能供、多选逻辑 |
| 4.3 筛选-行业级联 | 一级+二级联动、勾选/取消、标签显示/移除 |
| 4.4 筛选-业务品类 | 多选、摘要更新 |
| 4.5 筛选-地区级联 | 省份+城市联动 |
| 4.6 已选条件摘要 | 所有标签带✕、单项移除 |
| 4.7 重置筛选 | 全部清空 |
| 4.8 商机卡片 | 类型徽章+内容+按钮 |
| 4.9 分页 | 页码组件 |
| 4.10 发布弹窗 | 完整表单、类型默认、提交成功 |
| 4.11 获取联系方式 | 确认→成功 |

#### 第5章 企业名录模块（enterprise.html）

**前提：** 已登录，需基础数据字典+企业数据+未认领企业

| 用例 | 测试点 |
|------|--------|
| 5.1 页面结构 | 标题副标题、认领+创建按钮、2列grid |
| 5.2~5.5 筛选 | 行业级联、品类多选、地区级联、热门标签（14个） |
| 5.6 摘要与重置 | 已选标签、重置按钮 |
| 5.7 企业卡片 | 2列grid、Logo+名称+✓+标签+查看详情 |
| 5.8 分页 | 页码组件 |
| 5.9 认领企业 | 两步式弹窗（选企业→填资料）、返回选择、提交申请 |
| 5.10 创建企业 | 分区表单（企业信息+申请人信息）、联动下拉 |
| 5.11 企业详情Drawer | Logo+认证徽章+基础信息+简介+商机列表 |

#### 第6~8章 校友圈/搜索/通知

| 章节 | 关键测试点 |
|------|-----------|
| 第6章 | 动态卡片结构、发布动态（输入+提交+列表更新） |
| 第7章 | 搜索框预填、三Tab切换（商机/企业/动态+数量角标）、重新搜索 |
| 第8章 | 通知列表（4种图标类型）、未读背景、全部已读 |

#### 第9~11章 企业管理

| 章节 | 关键测试点 |
|------|-----------|
| 第9章 | Admin侧边栏、只读/可编辑字段、Logo上传、标签添加、保存/取消 |
| 第10章 | 员工表格、新增弹窗（4字段+单选角色）、编辑弹窗（手机号disabled）、重置密码、解绑 |
| 第11章 | 筛选（类型+状态+搜索）、编辑弹窗、下架、重新发布 |

#### 第12~16章 平台管理

| 章节 | 关键测试点 |
|------|-----------|
| 第12章 | 侧边栏4分组、4统计卡片（↑↓趋势）、趋势图 |
| 第13章 | 3 Tab（待审核/已通过/已驳回）、审核弹窗（企业信息+申请人+附件+驳回原因）、通过/驳回 |
| 第14章 | 租户列表、成员管理弹窗（统计+表格+新增）、禁用/启用切换 |
| 第15章 | 筛选、查看详情弹窗、强制下架（原因必填） |
| 第16章 | 筛选、查看弹窗、下架（原因必填） |

#### 第17~19章 系统管理

| 章节 | 关键测试点 |
|------|-----------|
| 第17章 | 4 Tab（行业树形/品类列表/标签Chip/区划树形）、CRUD、启用/禁用 |
| 第18章 | 5角色卡片、权限矩阵（3系统Tab）、✓/○/[超管]标记 |
| 第19章 | 平台名称+客服热线、敏感词/先审后发toggle（禁用态）、保存/重置 |

#### 第20章 全局公共交互

| 用例 | 关键测试点 |
|------|-----------|
| 20.1 Header导航一致性 | 4页面切换时active状态 |
| 20.2 通知铃铛一致性 | 所有页面面板内容一致 |
| 20.3 用户菜单一致性 | 所有页面菜单选项一致 |
| 20.4 弹窗遮罩关闭 | 任意弹窗/Drawer遮罩关闭 |
| 20.5 登出 | 菜单退出→跳转登录页→localStorage清空 |
| 20.6 未登录保护 | 直接访问/ent-admin/*→跳转/login |
| 20.7 权限不足 | 企业用户访问/plat-admin/*→拦截 |

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
