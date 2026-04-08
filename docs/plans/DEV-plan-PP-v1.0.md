# M3 开发实施计划

## XiaoLianTong (校链通)

| 文档信息 | 内容 |
|----------|------|
| 项目名称 | XiaoLianTong (校链通) |
| 文档版本 | v1.0 |
| 创建日期 | 2026-04-07 |
| 关联PRD | [PRD-XiaoLianTong-v1.0.md](../PRD-XiaoLianTong-v1.0.md) |
| 关联DESN | [DESN-PP-v1.0.md](../DESN-PP-v1.0.md) |
| 关联QA-test-plan | [QA-test-plan-PP-v1.0.md](../QA-test-plan-PP-v1.0.md) |
| 文档状态 | 待审批 |
| 执行角色 | TL |

---

## 1. 模块开发任务拆分

### 1.1 auth_app - 认证模块

**模块职责**：登录注册、短信验证码、Token管理、用户信息

**API清单**（8个）：
| API | 方法 | 功能 |
|-----|------|------|
| `/auth/sms/send` | POST | 发送短信验证码 |
| `/auth/sms/login` | POST | 短信验证码登录 |
| `/auth/login/password` | POST | 账号密码登录 |
| `/auth/register` | POST | 用户注册 |
| `/auth/password/reset/verify` | POST | 验证重置验证码 |
| `/auth/password/reset` | POST | 重置密码 |
| `/auth/logout` | POST | 登出 |
| `/auth/refresh` | POST | Token刷新 |
| `/auth/me` | GET | 获取当前用户信息 |

**补充模块（public）- 公开数据接口**：

**API清单**（1个）：
| API | 方法 | 功能 |
|-----|------|------|
| `/public/stats` | GET | 获取平台统计数据 |

**开发任务**：

| Task ID  | 任务名称         | 优先级 | 预估工时 | 依赖           | 验收标准                              |
| -------- | ------------ | --- | ---- | ------------ | --------------------------------- |
| AUTH-001 | Django认证体系配置 | P0  | 1d   | -            | SimpleJWT配置完成，Token旋转机制生效         |
| AUTH-002 | User模型扩展     | P0  | 1d   | AUTH-001     | UserProfile一对一关联，Django Group体系就绪 |
| AUTH-003 | 短信验证码发送接口    | P0  | 1d   | AUTH-001     | 每日次数限制5分钟过期，type独立计数              |
| AUTH-004 | 短信验证码登录/注册接口 | P0  | 1d   | AUTH-003     | 验证码校验，Token发放，remember_me支持       |
| AUTH-005 | 密码登录接口       | P0  | 0.5d | AUTH-001     | 密码强度校验，错误次数限制                     |
| AUTH-006 | 忘记密码功能       | P0  | 1d   | AUTH-003     | 验证-重置两阶段流程                        |
| AUTH-007 | Token刷新与登出   | P0  | 0.5d | AUTH-004     | 黑名单机制，ROTATE_REFRESH_TOKENS       |
| AUTH-008 | 当前用户信息接口     | P1  | 0.5d | AUTH-002     | 返回用户+企业+角色完整信息                    |
| AUTH-009 | 单元测试         | P0  | 1d   | AUTH-001~008 | 100%覆盖所有接口正反例                     |

**子任务详情**：

```
AUTH-001: Django认证体系配置
  - 安装 djangorestframework-simplejwt
  - 配置 JWT_ACCESS_TOKEN_LIFETIME = timedelta(hours=2)
  - 配置 JWT_REFRESH_TOKEN_LIFETIME = timedelta(days=7)
  - 配置 ROTATE_REFRESH_TOKENS = True
  - 配置 BLACKLIST_AFTER_ROTATION = True
  - 自定义 TokenObtainPairSerializer 返回 role_code, permissions
  - 配置 DRF AuthenticationClasses

AUTH-002: User模型扩展
  - 创建 ent_user_profile 表（一对一关联auth_user）
  - role_code字段：super_admin/platform_operator/enterprise_admin/employee/guest
  - real_name/position/contact_phone/contact_wechat字段
  - 信号机制：创建用户时自动创建UserProfile

AUTH-003: 短信验证码发送接口
  - auth_sms_code表设计（phone, code, type, expire_at, used_at, created_at）
  - 联合索引 idx_phone_type
  - 过期时间索引 idx_expire_at
  - 每日次数限制：login=10次, register=10次, password_reset=5次
  - 5分钟内未使用验证码自动作废重发
  - Mock短信服务（开发阶段）

AUTH-004: 短信验证码登录/注册接口
  - 验证码6位数字校验
  - 验证码有效期5分钟校验
  - used_at为NULL校验
  - 注册时自动创建UserProfile(role_code=guest)
  - 返回 access_token, refresh_token, user_id, role_code, permissions

AUTH-005: 密码登录接口
  - 手机号+密码校验
  - 错误次数限制（同一IP 5次后锁定30分钟）
  - remember_me控制refresh_token过期时间

AUTH-006: 忘记密码功能
  - Step1: 验证手机号+验证码（不重置）
  - Step2: 输入新密码完成重置
  - 验证码使用后立即作废

AUTH-007: Token刷新与登出
  - POST /auth/logout 将refresh_token加入黑名单
  - POST /auth/refresh 返回新access_token+新refresh_token

AUTH-008: 当前用户信息接口
  - 返回: id, phone, real_name, position, role_code, enterprise_id, enterprise_name, enterprise_status
```

---

### 1.2 ent - 企业名录

**模块职责**：企业浏览、筛选搜索、企业认领、企业创建

**API清单**（10个）：
| API | 方法 | 功能 |
|-----|------|------|
| `/ent/enterprise` | GET | 企业列表（筛选+分页） |
| `/ent/enterprise/{id}` | GET | 企业详情 |
| `/ent/enterprise/my` | GET | 我的企业（当前用户所属企业） |
| `/ent/enterprise/claim` | POST | 认领企业 |
| `/ent/enterprise/create` | POST | 创建企业 |
| `/ent/enterprise/{id}` | PUT | 更新企业信息 |
| `/ent/industry` | GET | 行业字典 |
| `/ent/category` | GET | 业务品类字典 |
| `/ent/region` | GET | 行政区划字典 |
| `/ent/enterprise/newest` | GET | 新入驻企业 |

**开发任务**：

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| ENT-001 | 企业模型设计 | P0 | 1d | AUTH-002 | ent_enterprise表结构符合DESN |
| ENT-002 | 企业列表接口 | P0 | 1.5d | ENT-001 | 多条件筛选、关键词搜索、分页 |
| ENT-003 | 企业详情接口 | P0 | 1d | ENT-001 | 认证状态脱敏、返回商机列表 |
| ENT-004 | 认领企业接口 | P0 | 1d | AUTH-008 | auth_status=PENDING审核流程 |
| ENT-005 | 创建企业接口 | P0 | 1d | AUTH-008 | auth_status=PENDING审核流程 |
| ENT-006 | 我的企业接口 | P0 | 0.5d | AUTH-008 | 返回当前用户所属企业信息 |
| ENT-007 | 更新企业信息接口 | P0 | 1d | AUTH-008 | 企业管理员可更新部分字段 |
| ENT-008 | 字典接口（行业/品类/地区） | P0 | 1d | - | 树形结构，级联筛选支持 |
| ENT-009 | 新入驻企业接口 | P1 | 0.5d | ENT-001 | 固定返回3条认证企业 |
| ENT-010 | 单元测试 | P0 | 1.5d | ENT-001~009 | 100%覆盖 |

**子任务详情**：

```
ENT-001: 企业模型设计
  - ent_enterprise表：name, credit_code, legal_representative, business_license
  - logo_url, industry_id, sub_industry_id, category_id, province_id, region_id
  - tags(JSON), description(TEXT)
  - admin_user(FK auth.User), auth_status, created_at, updated_at
  - auth_status枚举：UNCLAIMED/PENDING/VERIFIED/REJECTED
  - 唯一索引：(credit_code)

ENT-002: 企业列表接口
  - GET /ent/enterprise
  - 筛选条件：industry_id, sub_industry_id, category_id, province_id, region_id, auth_status, keyword
  - 关键词搜索：name, description模糊匹配
  - 分页：page, page_size，默认20条
  - 仅返回认证企业完整信息，未认证企业脱敏

ENT-003: 企业详情接口
  - GET /ent/enterprise/{id}
  - auth_status=VERIFIED：返回完整联系信息+商机列表
  - auth_status!=VERIFIED：contact_phone=null，opportunities=[]
  - 返回字段符合DESN设计

ENT-004: 认领企业接口
  - POST /ent/enterprise/claim
  - credit_code匹配未认领企业
  - 写入audit_record表，status=PENDING
  - 业务规则：BR-ENT-02认领互斥

ENT-005: 创建企业接口
  - POST /ent/enterprise/create
  - credit_code唯一性校验
  - 写入enterprise表+audit_record表
  - 业务规则：BR-ENT-05认证必填字段

ENT-006: 我的企业接口
  - GET /ent/enterprise/my
  - 返回当前用户所属企业信息
  - 仅限已绑定企业的用户

ENT-007: 更新企业信息接口
  - PUT /ent/enterprise/{id}
  - 仅企业管理员可更新
  - 可更新：category_id, province_id, region_id, detail, logo_url, tags
  - 不可更新：name, credit_code等认证字段

ENT-008: 字典接口
  - GET /ent/industry?parent_id=0 获取一级行业
  - GET /ent/industry?parent_id={id} 获取二级行业
  - GET /ent/category?industry_id={id} 按行业筛选品类
  - GET /ent/region?parent_id=0 获取省份
  - GET /ent/region?parent_id={id} 获取城市
  - 使用plat_master_data表

ENT-009: 新入驻企业接口
  - GET /ent/enterprise/newest
  - auth_status=VERIFIED，按created_at倒序，limit=3
```

---

### 1.3 opp - 商机广场

**模块职责**：商机发布、商机浏览、商机筛选、商机联系

**API清单**（8个）：
| API | 方法 | 功能 |
|-----|------|------|
| `/opp/opportunity` | GET | 商机列表 |
| `/opp/opportunity/{id}` | GET | 商机详情 |
| `/opp/opportunity` | POST | 发布商机 |
| `/opp/opportunity/{id}` | PUT | 编辑商机 |
| `/opp/opportunity/{id}` | DELETE | 删除商机 |
| `/opp/opportunity/{id}/offline` | POST | 下架商机 |
| `/opp/opportunity/{id}/contact` | POST | 获取联系方式 |
| `/opp/opportunity/recommended` | GET | 智能推荐 |

**开发任务**：

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| OPP-001 | 商机模型设计 | P0 | 1d | ENT-001 | opp_opportunity表结构 |
| OPP-002 | 商机列表接口 | P0 | 1.5d | OPP-001 | 多条件筛选、分页 |
| OPP-003 | 商机详情接口 | P0 | 1d | OPP-001 | 联系方式脱敏 |
| OPP-004 | 发布商机接口 | P0 | 1d | AUTH-008 | 权限校验，status=ACTIVE |
| OPP-005 | 编辑商机接口 | P0 | 0.5d | OPP-001 | type不可修改 |
| OPP-006 | 删除商机接口 | P0 | 0.5d | OPP-001 | 仅发布人可删除 |
| OPP-007 | 下架/重新发布接口 | P0 | 0.5d | OPP-001 | 状态切换 |
| OPP-008 | 获取联系方式接口 | P0 | 1d | OPP-001 | 消息通知触发 |
| OPP-009 | 智能推荐接口 | P1 | 1d | OPP-001 | 推荐算法实现 |
| OPP-010 | 单元测试 | P0 | 1.5d | OPP-001~009 | 100%覆盖 |

**子任务详情**：

```
OPP-001: 商机模型设计
  - opp_opportunity表：type, title, enterprise(FK), publisher(FK)
  - industry_id, sub_industry_id, category_id, province_id, region_id
  - tags(JSON), detail(TEXT), status
  - view_count, contact_name, contact_phone, contact_wechat
  - created_at, updated_at
  - type枚举：BUY/SUPPLY
  - status枚举：ACTIVE/OFFLINE

OPP-002: 商机列表接口
  - GET /opp/opportunity
  - 筛选：type, industry_id, sub_industry_id, category_id, province_id, region_id, keyword
  - 分页：page, page_size，默认20条
  - 排序：created_at倒序

OPP-003: 商机详情接口
  - GET /opp/opportunity/{id}
  - contact_phone脱敏显示（138****8888）
  - view_count+1

OPP-004: 发布商机接口
  - POST /opp/opportunity
  - 权限：已认证+已绑定认证企业
  - status默认ACTIVE（先发后审）
  - BR-OPP-02发布权限限制

OPP-005: 编辑商机接口
  - PUT /opp/opportunity/{id}
  - 仅发布人或企业管理员可编辑
  - type类型不可修改

OPP-006: 删除商机接口
  - DELETE /opp/opportunity/{id}
  - 仅发布人可删除
  - BR-OPP-01事后巡查机制

OPP-007: 下架/重新发布接口
  - POST /opp/opportunity/{id}/offline
  - 仅发布人或企业管理员可操作
  - BR-OPP-01事后巡查机制

OPP-008: 获取联系方式接口
  - POST /opp/opportunity/{id}/contact
  - 权限：已认证+已绑定认证企业
  - 写入opp_contact_log表
  - 发送msg_message通知发布方
  - BR-OPP-03单向获取

OPP-009: 智能推荐接口
  - GET /opp/opportunity/recommended
  - 固定返回4条
  - 冷启动：最新发布+热门标签
  - 个性化：供需互补+品类重合+地域就近
```

---

### 1.4 feed - 校友圈

**模块职责**：动态发布、动态浏览

**API清单**（6个）：
| API | 方法 | 功能 |
|-----|------|------|
| `/feed/feed` | GET | 动态列表 |
| `/feed/feed/{id}` | GET | 动态详情 |
| `/feed/feed` | POST | 发布动态 |
| `/feed/feed/{id}` | DELETE | 删除动态 |
| `/feed/feed/{id}/offline` | PUT | 下架动态 |
| `/feed/feed/newest` | GET | 最新动态 |

**开发任务**：

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FEED-001 | 动态模型设计 | P0 | 1d | AUTH-002 | feed_feed表结构 |
| FEED-002 | 动态列表接口 | P0 | 1d | FEED-001 | 分页、筛选 |
| FEED-003 | 动态详情接口 | P0 | 0.5d | FEED-001 | 内容展示 |
| FEED-004 | 发布动态接口 | P0 | 1d | AUTH-008 | 图片上传 |
| FEED-005 | 删除动态接口 | P0 | 0.5d | FEED-001 | 权限控制 |
| FEED-006 | 下架动态接口 | P1 | 0.5d | FEED-001 | 权限控制 |
| FEED-007 | 最新动态接口 | P1 | 0.5d | FEED-001 | 固定2条 |
| FEED-008 | 单元测试 | P0 | 1d | FEED-001~007 | 100%覆盖 |

**子任务详情**：

```
FEED-001: 动态模型设计
  - feed_feed表：publisher(FK), enterprise(FK), content(TEXT)
  - images(JSON，最多9张), status, created_at, updated_at
  - status枚举：ACTIVE/OFFLINE
  - 图片存储：本地文件服务器或OSS

FEED-002: 动态列表接口
  - GET /feed/feed
  - 分页：page, page_size，默认20条
  - 排序：created_at倒序
  - 仅返回status=ACTIVE

FEED-003: 动态详情接口
  - GET /feed/feed/{id}
  - status=OFFLINE仅发布人和管理员可见

FEED-004: 发布动态接口
  - POST /feed/feed
  - 权限：已认证+已绑定认证企业
  - BR-FED-01发布权限限制
  - 图片上传：支持最多9张，返回URL数组
  - 业务规则：BR-FED-02事后巡查机制

FEED-005: 删除动态接口
  - DELETE /feed/feed/{id} 仅发布人可删除
  - BR-FED-02事后巡查机制

FEED-006: 下架动态接口
  - PUT /feed/feed/{id}/offline 仅发布人和平台管理员可下架

FEED-007: 最新动态接口
  - GET /feed/feed/newest
  - status=ACTIVE，按created_at倒序，limit=2
```

---

### 1.5 ent-admin - 企业端管理

**模块职责**：企业信息维护、员工管理、本企业商机管理

**API清单**（10个）：
| API | 方法 | 功能 |
|-----|------|------|
| `/ent-admin/employees` | GET | 员工列表 |
| `/ent-admin/employees` | POST | 新增员工 |
| `/ent-admin/employees/{id}` | PUT | 编辑员工 |
| `/ent-admin/employees/{id}/reset-password` | POST | 重置密码 |
| `/ent-admin/employees/{id}/disable` | PUT | 停用/启用账号 |
| `/ent-admin/employees/{id}/unbind` | POST | 解绑员工 |
| `/ent-admin/opportunities` | GET | 本企业商机列表 |
| `/ent-admin/opportunities/{id}` | PUT | 编辑商机 |
| `/ent-admin/opportunities/{id}/republish` | POST | 重新发布 |
| `/ent-admin/opportunities/{id}` | DELETE | 删除商机 |

**说明**：企业信息维护使用 `/ent/enterprise/my` (GET) 和 `/ent/enterprise/{id}` (PUT)，在 ent 模块实现

**开发任务**：

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| ADM-001 | 员工列表接口 | P0 | 1d | AUTH-002 | 本企业数据隔离 |
| ADM-002 | 新增员工接口 | P0 | 1.5d | AUTH-002 | 短信通知 |
| ADM-003 | 编辑员工接口 | P0 | 1d | ADM-001 | 角色变更 |
| ADM-004 | 重置密码接口 | P0 | 0.5d | ADM-001 | 短信通知新密码 |
| ADM-005 | 停用/启用账号接口 | P0 | 0.5d | ADM-001 | 状态变更逻辑 |
| ADM-006 | 解绑员工接口 | P0 | 0.5d | ADM-001 | 解绑企业关系 |
| ADM-007 | 本企业商机列表 | P0 | 1d | OPP-001 | 数据隔离 |
| ADM-008 | 编辑商机接口 | P0 | 1d | OPP-001 | 仅发布人可编辑 |
| ADM-009 | 重新发布接口 | P0 | 0.5d | OPP-001 | 状态切换 |
| ADM-010 | 删除商机接口 | P0 | 0.5d | OPP-001 | 仅发布人可删除 |
| ADM-011 | 单元测试 | P0 | 1.5d | ADM-001~010 | 100%覆盖 |

**子任务详情**：

```
ADM-001: 员工列表接口
  - GET /ent-admin/employees
  - enterprise_id=当前用户所属企业
  - 返回：user_id, real_name, phone, role_code, is_active

ADM-002: 新增员工接口
  - POST /ent-admin/employees
  - 手机号已注册：直接绑定企业，role_code=employee
  - 手机号未注册：创建用户，密码默认手机号后6位，首次登录强制修改
  - 短信通知初始密码

ADM-003: 编辑员工接口
  - PUT /ent-admin/employees/{id}
  - 可修改：real_name, position, role_code(仅在enterprise_admin范围内)
  - 不可将其他enterprise_admin降为employee

ADM-004: 重置密码接口
  - POST /ent-admin/employees/{id}/reset-password
  - 新密码默认手机号后6位
  - 短信通知

ADM-005: 停用/启用账号接口
  - PUT /ent-admin/employees/{id}/disable
  - is_active=false，禁止登录
  - 启用时 is_active=true

ADM-006: 解绑员工接口
  - POST /ent-admin/employees/{id}/unbind
  - 解绑企业关系，恢复游客身份
  - 仅Plat-Admin可操作解绑

ADM-007: 本企业商机列表
  - GET /ent-admin/opportunities
  - enterprise_id=当前用户所属企业
  - 支持筛选：status, type, keyword

ADM-008: 编辑商机接口
  - PUT /ent-admin/opportunities/{id}
  - 仅发布人或企业管理员可编辑
  - type不可修改

ADM-009: 重新发布接口
  - POST /ent-admin/opportunities/{id}/republish
  - 仅限status=OFFLINE的商机
  - 重新发布后status=ACTIVE

ADM-010: 删除商机接口
  - DELETE /ent-admin/opportunities/{id}
  - 仅发布人可删除
```

---

### 1.6 plat-admin - 平台端管理

**模块职责**：数据大盘、企业审核、企业租户管理、商机内容管理、动态内容管理、基础数据字典、账号权限、系统设置

**API清单**（30个）：

| API                                                | 方法   | 功能               |
| -------------------------------------------------- | ---- | ---------------- |
| `/plat-admin/profile`                              | GET  | 管理员信息            |
| `/plat-admin/notification`                         | GET  | 通知列表             |
| `/plat-admin/notification/read-all`                | POST | 全部已读             |
| `/plat-admin/dashboard/stats`                      | GET  | 统计指标             |
| `/plat-admin/dashboard/trend`                      | GET  | 趋势数据             |
| `/plat-admin/audit/enterprise`                     | GET  | 企业审核列表（status筛选） |
| `/plat-admin/audit/enterprise/{id}/approve`        | POST | 审核通过             |
| `/plat-admin/audit/enterprise/{id}/reject`         | POST | 审核驳回             |
| `/plat-admin/tenant/enterprise`                    | GET  | 企业列表             |
| `/plat-admin/tenant/enterprise/{id}`               | GET  | 企业详情             |
| `/plat-admin/tenant/enterprise/{id}/toggle-status` | PUT  | 启用/禁用企业          |
| `/plat-admin/tenant/enterprise/{id}/member`        | GET  | 企业成员列表           |
| `/plat-admin/tenant/enterprise/{id}/member`        | POST | 新增成员             |
| `/plat-admin/tenant/member/{id}`                   | PUT  | 编辑成员             |
| `/plat-admin/tenant/member/{id}/reset-password`    | POST | 重置密码             |
| `/plat-admin/tenant/member/{id}/unbind`            | POST | 解绑成员             |
| `/plat-admin/content/opportunity`                  | GET  | 商机列表             |
| `/plat-admin/content/opportunity/{id}`             | GET  | 商机详情             |
| `/plat-admin/content/opportunity/{id}/offline`     | PUT  | 强制下架             |
| `/plat-admin/content/feed`                         | GET  | 动态列表             |
| `/plat-admin/content/feed/{id}`                    | GET  | 动态详情             |
| `/plat-admin/content/feed/{id}/offline`            | PUT  | 强制下架             |
| `/plat-admin/master-data`                          | GET  | 字典列表             |
| `/plat-admin/master-data`                          | POST | 新增字典项            |
| `/plat-admin/master-data/{id}`                     | PUT  | 更新字典项            |
| `/plat-admin/master-data/{id}/toggle-status`       | PUT  | 启用/禁用字典项         |
| `/plat-admin/role`                                 | GET  | 角色列表             |
| `/plat-admin/role/{id}`                            | GET  | 角色权限详情           |
| `/plat-admin/role/{id}/permissions`                | PUT  | 更新角色权限           |
| `/plat-admin/settings`                             | GET  | 获取设置             |
| `/plat-admin/settings`                             | PUT  | 更新设置             |

**说明**：DESN中 plat-admin 模块API总数为48个，以上列出30个核心接口，其余为前端交互辅助接口（如Tab切换的status参数）

**开发任务**：

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| PLAT-001 | 管理员信息与通知 | P0 | 1d | AUTH-002 | profile+notification |
| PLAT-002 | 数据大盘 | P0 | 1d | OPP-001, FEED-001 | stats+trend |
| PLAT-003 | 企业审核 | P0 | 2d | ENT-005 | 审核流程+通知 |
| PLAT-004 | 企业租户管理 | P0 | 2d | ADM-002 | 成员管理CRUD |
| PLAT-005 | 商机内容管理 | P0 | 1d | OPP-001 | 巡查+下架+详情 |
| PLAT-006 | 动态内容管理 | P0 | 1d | FEED-001 | 巡查+下架+详情 |
| PLAT-007 | 基础数据字典 | P0 | 1.5d | - | 树形结构CRUD+toggle |
| PLAT-008 | 账号权限(RBAC) | P0 | 2d | AUTH-002 | 角色+权限矩阵 |
| PLAT-009 | 系统设置 | P1 | 1d | - | 配置管理 |
| PLAT-010 | 单元测试 | P0 | 2d | PLAT-001~009 | 100%覆盖 |

**子任务详情**：

```
PLAT-001: 管理员信息与通知
  - GET /plat-admin/profile
    返回当前管理员基本信息
  - GET /plat-admin/notification
    返回通知列表，分页
  - POST /plat-admin/notification/read-all
    全部标记为已读

PLAT-002: 数据大盘
  - GET /plat-admin/dashboard/stats
    enterprise_count, opportunity_count, active_user_count, deal_count
  - GET /plat-admin/dashboard/trend
    type (opportunity/enterprise/deal), period (天数，默认30)
    返回近30天趋势数据

PLAT-003: 企业审核
  - GET /plat-admin/audit/enterprise
    status=PENDING/VERIFIED/REJECTED，keyword搜索
  - POST /plat-admin/audit/enterprise/{id}/approve
    auth_status=PENDING→VERIFIED
    admin_user_id绑定
    用户role_code=guest→enterprise_admin
    发送审核通过通知
  - POST /plat-admin/audit/enterprise/{id}/reject
    auth_status=PENDING→REJECTED
    填写audit_reason
    发送审核驳回通知(含原因)
  - BR-ENT-03管理员权限分配

PLAT-004: 企业租户管理
  - GET /plat-admin/tenant/enterprise
    enterprise列表，含关键词和状态筛选
  - GET /plat-admin/tenant/enterprise/{id}
    企业详情，含成员列表
  - PUT /plat-admin/tenant/enterprise/{id}/toggle-status
    启用/禁用企业账号
  - GET /plat-admin/tenant/enterprise/{id}/member
    企业成员列表
  - POST /plat-admin/tenant/enterprise/{id}/member
    新增企业成员
  - PUT /plat-admin/tenant/member/{id}
    编辑成员信息(is_active, role_code等)
  - POST /plat-admin/tenant/member/{id}/reset-password
    重置密码为手机号后6位
  - POST /plat-admin/tenant/member/{id}/unbind
    解绑后恢复游客身份

PLAT-005: 商机内容管理
  - GET /plat-admin/content/opportunity
    type, status, keyword筛选
  - GET /plat-admin/content/opportunity/{id}
    商机详情
  - PUT /plat-admin/content/opportunity/{id}/offline
    强制下架，填写原因，发送通知

PLAT-006: 动态内容管理
  - GET /plat-admin/content/feed
    status, keyword筛选
  - GET /plat-admin/content/feed/{id}
    动态详情
  - PUT /plat-admin/content/feed/{id}/offline
    强制下架，填写原因，发送通知

PLAT-007: 基础数据字典
  - GET /plat-admin/master-data
    category, page, page_size筛选
  - POST /plat-admin/master-data
    新增字典项(category, name, code, parent_id, sort_order)
  - PUT /plat-admin/master-data/{id}
    更新字典项
  - PUT /plat-admin/master-data/{id}/toggle-status
    启用/禁用字典项（禁止物理删除）
  - BR-ADM-02被引用禁止物理删除

PLAT-008: 账号权限(RBAC)
  - GET /plat-admin/role
    角色列表
  - GET /plat-admin/role/{id}
    角色权限详情
  - PUT /plat-admin/role/{id}/permissions
    保存角色权限配置
  - BR-ADM-01平台运营仅可见审核和内容管理

PLAT-009: 系统设置
  - GET /plat-admin/settings
    获取平台设置(key可选)
  - PUT /plat-admin/settings
    更新平台设置(key, value)
```

---

### 1.7 msg - 消息通知

**模块职责**：站内消息、通知推送

**API清单**（3个）：
| API | 方法 | 功能 |
|-----|------|------|
| `/msg/notifications` | GET | 消息列表 |
| `/msg/notifications/{id}/read` | PUT | 单条已读 |
| `/msg/notifications/read-all` | PUT | 全部已读 |
| `/msg/notifications/recent` | GET | 最近通知（铃铛下拉） |

**开发任务**：

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| MSG-001 | 消息模型设计 | P0 | 1d | AUTH-002 | msg_message表结构 |
| MSG-002 | 消息列表接口 | P0 | 0.5d | MSG-001 | 分页+已读未读筛选 |
| MSG-003 | 已读接口 | P0 | 0.5d | MSG-001 | 单条+全部已读 |
| MSG-004 | 最近通知接口 | P0 | 0.5d | MSG-001 | 固定返回5条 |
| MSG-005 | 消息触发机制 | P0 | 1d | OPP-007, PLAT-002 | 审核/联系/系统通知 |
| MSG-006 | 单元测试 | P0 | 1d | MSG-001~005 | 100%覆盖 |

**子任务详情**：

```
MSG-001: 消息模型设计
  - msg_message表：receiver(FK), sender(FK), type, title, content
  - is_read, related_type, related_id, created_at
  - type枚举：AUDIT_APPROVED/AUDIT_REJECTED/CONTACT_RECEIVED/SYSTEM

MSG-002: 消息列表接口
  - GET /msg/notifications
  - 分页：page, page_size，默认20条
  - 筛选：is_read

MSG-003: 已读接口
  - PUT /msg/notifications/{id}/read
    is_read=true
  - PUT /msg/notifications/read-all
    批量更新is_read=true

MSG-004: 最近通知接口
  - GET /msg/notifications/recent?limit=5
  - 返回unread_count+items

MSG-005: 消息触发机制
  - 审核通过：AUDIT_APPROVED类型通知申请人
  - 审核驳回：AUDIT_REJECTED类型通知申请人（含原因）
  - 获取联系方式：CONTACT_RECEIVED类型通知发布方
  - BR-MSG-01 Badge实时更新
  - BR-MSG-02 驳回通知含原因
  - BR-MSG-03 永久存储
```

---

### 1.8 search - 搜索服务

**模块职责**：全局搜索、商机企业动态聚合

**API清单**（1个）：
| API | 方法 | 功能 |
|-----|------|------|
| `/search` | GET | 全局搜索 |

**开发任务**：

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| SCH-001 | 全局搜索接口 | P0 | 2d | OPP-001, ENT-001, FEED-001 | 三域聚合 |
| SCH-002 | 搜索结果分页 | P0 | 1d | SCH-001 | 每域20条 |
| SCH-003 | 单元测试 | P0 | 1d | SCH-001~002 | 100%覆盖 |

**子任务详情**：

```
SCH-001: 全局搜索接口
  - GET /search?keyword=xxx&tab=opp|ent|feed
  - 匹配：opportunities.title, enterprises.name, feeds.content
  - BR-SCH-01 敏感词过滤
  - BR-SCH-02 分页规则：每域20条

SCH-002: 搜索结果分页
  - Tab切换：找商机/找企业/看动态
  - 相关性排序：标题优先>内容匹配
  - 返回结构：{opp: {items: [], total}, ent: {items: [], total}, feed: {items: [], total}}
```

---

## 2. 模块间依赖关系

### 2.1 依赖矩阵

| 模块 | 依赖模块 | 依赖类型 | 说明 |
|------|----------|----------|------|
| public | 无 | - | 公开接口，无需认证 |
| auth_app | 无 | - | 认证模块，无依赖 |
| ent | auth_app | 硬依赖 | User模型关联，JWT认证 |
| opp | auth_app | 硬依赖 | JWT认证，用户信息 |
| opp | ent | 硬依赖 | enterprise_id外键关联 |
| opp | msg | 硬依赖 | 获取联系方式时发送消息 |
| feed | auth_app | 硬依赖 | JWT认证，用户信息 |
| feed | ent | 硬依赖 | enterprise_id外键关联 |
| ent-admin | auth_app | 硬依赖 | JWT认证 |
| ent-admin | ent | 硬依赖 | 企业信息CRUD |
| ent-admin | opp | 硬依赖 | 本企业商机管理 |
| ent-admin | msg | 可选 | 员工密码重置短信通知 |
| plat-admin | auth_app | 硬依赖 | JWT认证，超级管理员权限 |
| plat-admin | ent | 硬依赖 | 企业审核CRUD |
| plat-admin | opp | 硬依赖 | 商机内容管理 |
| plat-admin | feed | 硬依赖 | 动态内容管理 |
| plat-admin | msg | 硬依赖 | 审核结果通知 |
| msg | auth_app | 硬依赖 | JWT认证，receiver关联 |
| search | opp | 硬依赖 | 商机搜索 |
| search | ent | 硬依赖 | 企业搜索 |
| search | feed | 硬依赖 | 动态搜索 |

### 2.2 依赖关系图

```
                    ┌─────────────┐
                    │  auth_app   │
                    │  (认证模块)   │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │    ent      │ │    opp      │ │    feed     │
    │  (企业名录)   │ │  (商机广场)   │ │  (校友圈)    │
    └─────────────┘ └──────┬──────┘ └─────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │    msg      │
                    │ (消息通知)   │
                    └─────────────┘

    ┌─────────────────────────────────────────┐
    │             plat-admin                   │
    │            (平台端管理)                   │
    │  依赖: auth_app, ent, opp, feed, msg    │
    └─────────────────────────────────────────┘

    ┌─────────────────────────────────────────┐
    │             ent-admin                    │
    │            (企业端管理)                   │
    │  依赖: auth_app, ent, opp               │
    └─────────────────────────────────────────┘

                    ┌─────────────┐
                    │   search    │
                    │  (搜索服务)   │
                    │  依赖: opp, ent, feed │
                    └─────────────┘
```

### 2.3 开发顺序

| 阶段 | 模块 | 说明 |
|------|------|------|
| **Phase 1** | auth_app, public | 认证模块（基石）+ 公开接口（独立），可并行 |
| **Phase 2** | ent, feed | 企业名录和校友圈，可并行开发 |
| **Phase 3** | opp, ent-admin | 商机广场 + 企业端管理，opp 依赖 ent |
| **Phase 4** | msg | 消息通知，opp 联系触发 |
| **Phase 5** | plat-admin | 平台管理，依赖所有业务模块 |
| **Phase 6** | search | 搜索服务，依赖 opp/ent/feed |

### 2.4 并行开发分组（8窗口同时开发）

```
【第一组 - 无依赖，可最先开发】
├─ auth_app          ← 其他所有模块的基石
└─ public            ← 公开接口，无依赖

【第二组 - 依赖 auth_app，可并行】
├─ ent               ← 企业模块
├─ feed              ← 动态模块（需 User FK）

【第三组 - 依赖 ent/feed】
├─ opp               ← 商机模块（需 enterprise_id FK）
├─ ent-admin         ← 企业管理（需 ent + opp）

【第四组 - 依赖已完成的业务模块】
├─ msg               ← 消息通知（需 opp 触发）
├─ plat-admin        ← 平台管理（依赖所有业务）
└─ search            ← 搜索（依赖 opp/ent/feed）
```

#### 并行开发窗口分配建议

| 窗口 | 模块 | 依赖注意事项 |
|------|------|-------------|
| 窗口1 | auth_app | 必须先完成，其他所有窗口依赖它 |
| 窗口2 | public | 与 auth_app 并行开发，无依赖 |
| 窗口3 | ent | 完成 auth_app 后开始 |
| 窗口4 | feed | 完成 auth_app 后开始 |
| 窗口5 | opp | 完成 ent 后开始 |
| 窗口6 | ent-admin | 完成 ent + opp 后开始 |
| 窗口7 | msg | 完成 opp 后开始 |
| 窗口8 | plat-admin | 完成 ent + opp + feed + msg 后开始 |
| 窗口9 | search | 完成 opp + ent + feed 后开始 |

#### 关键路径（串行部分）

```
auth_app (+ public) → ent/opp/feed → ent-admin → plat-admin
                              ↓
                            msg
                              ↓
                          search
```

#### Worktree 分支对照

| 窗口 | 模块 | Worktree 分支 | 本地开发目录 |
|------|------|---------------|-------------|
| 窗口1 | auth_app | feature/auth_app | .claude/worktrees/feature-auth_app |
| 窗口2 | public | feature/auth_app | 与 auth_app 同一 worktree |
| 窗口3 | ent | feature/ent | .claude/worktrees/feature-ent |
| 窗口4 | feed | feature/feed | .claude/worktrees/feature-feed |
| 窗口5 | opp | feature/opp | .claude/worktrees/feature-opp |
| 窗口6 | ent-admin | feature/ent-admin | .claude/worktrees/feature-ent-admin |
| 窗口7 | msg | feature/msg | .claude/worktrees/feature-msg |
| 窗口8 | plat-admin | feature/plat-admin | .claude/worktrees/feature-plat-admin |
| 窗口9 | search | feature/search | .claude/worktrees/feature-search |

**说明**：public 模块代码可并入 auth_app worktree 开发，因其独立无依赖

---

## 3. 技术实现要点

### 3.1 Django项目结构

```
backend/
├── config/
│   ├── settings.py          # Django配置
│   ├── urls.py              # 根路由
│   └── wsgi.py
├── apps/
│   ├── auth_app/            # 认证模块
│   │   ├── models.py        # UserProfile, SmsCode
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── enterprise/           # 企业模块
│   │   ├── models.py        # Enterprise
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── opportunity/          # 商机模块
│   │   ├── models.py        # Opportunity, ContactLog
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── feed/                 # 校友圈模块
│   │   ├── models.py        # Feed
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── platform_admin/       # 平台管理模块
│   │   ├── models.py        # AuditRecord, OperationLog, MasterData
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── message/              # 消息模块
│   │   ├── models.py        # Message
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   └── search/               # 搜索模块
│       ├── views.py
│       ├── urls.py
│       └── tests.py
└── requirements.txt
```

### 3.2 API统一响应格式

```python
# 统一响应格式
def api_response(code=200, message='success', data=None):
    return Response({'code': code, 'message': message, 'data': data})

# 分页响应
def paginated_response(queryset, serializer_class, request):
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(page, many=True)
    return paginator.get_paginated_response(serializer.data)
```

### 3.3 权限控制设计

```python
# 权限类
class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsEnterpriseAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        profile = request.user.userprofile
        return profile.enterprise_id and profile.role_code == 'enterprise_admin'

class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        profile = request.user.userprofile
        return profile.role_code in ['super_admin', 'platform_operator']
```

### 3.4 数据隔离设计

```python
# 企业端数据隔离
class EnterpriseQuerySetMixin:
    """企业端只能查询本企业数据"""
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            profile = self.request.user.userprofile
            if profile.enterprise_id:
                queryset = queryset.filter(enterprise_id=profile.enterprise_id)
        return queryset
```

---

## 4. 开发工时估算

| 模块         | Task数  | 预估工时(d)  | 并行开发人数 | 实际工期(d) |
| ---------- | ------ | -------- | ------ | ------- |
| auth_app   | 9      | 7.5      | 2      | 4       |
| public     | 1      | 0.5      | 1      | 0.5     |
| ent        | 10     | 8.5      | 2      | 4       |
| opp        | 10     | 9        | 2      | 5       |
| feed       | 8      | 6        | 2      | 3       |
| ent-admin  | 11     | 9.5      | 2      | 5       |
| plat-admin | 10     | 13       | 2      | 7       |
| msg        | 6      | 4.5      | 2      | 3       |
| search     | 3      | 4        | 2      | 2       |
| **合计**     | **68** | **62.5** | -      | **10**  |

**说明**：
- 并行开发：4组，每组2人
- 关键路径：auth_app → ent/opp/feed → ent-admin/plat-admin → search
- 预计总工期：10个工作日

---

## 5. 测试策略

### 5.1 单元测试覆盖率目标

| 模块 | 覆盖率目标 |
|------|-----------|
| auth_app | 100% |
| enterprise | 100% |
| opportunity | 100% |
| feed | 100% |
| platform_admin | 100% |
| message | 100% |
| search | 100% |

### 5.2 TDD开发流程

```
1. DEV-Implementer 编写失败测试
2. 实现功能代码
3. 测试通过后提交
4. DEV-Spec-Reviewer 审查规格合规
5. DEV-Quality-Reviewer 审查代码质量
6. TL 全量代码审查
```

### 5.3 Mock策略

| 场景 | Mock对象 | 实现方式 |
|------|----------|----------|
| 短信服务 | SMSService.send | unittest.mock.patch |
| 文件上传 | local/OSS | Django test client |

---

## 6. 验收标准

### 6.1 代码质量

- [ ] 静态代码扫描（flake8/bandit）无阻断问题
- [ ] 单元测试 100% 通过
- [ ] API响应格式符合DESN定义
- [ ] 权限控制符合PRD权限矩阵

### 6.2 功能验收

- [ ] auth_app: 登录/注册/登出/Token刷新/密码重置 全流程通
- [ ] ent: 企业列表/筛选/认领/创建/详情 全流程通
- [ ] opp: 商机列表/筛选/发布/联系/推荐 全流程通
- [ ] feed: 动态列表/发布/浏览 全流程通
- [ ] ent-admin: 企业信息维护/员工管理/商机管理 全流程通
- [ ] plat-admin: 审核/租户管理/内容管理/字典管理 全流程通
- [ ] msg: 消息列表/已读/通知触发 全流程通
- [ ] search: 全局搜索/分Tab展示 全流程通

### 6.3 集成验收

- [ ] 企业入驻完整链路：注册→创建企业→审核通过→发布商机
- [ ] 商机联系完整链路：浏览商机→获取联系方式→收到通知
- [ ] 员工管理完整链路：新增员工→重置密码→停用账号

---

---

## 8. 前端开发任务拆分

### 8.1 设计规范

**设计系统**：Trust & Authority
- **主色**：#2563EB (Primary Navy Blue)
- **强调色-我要买**：#F97316 (Orange)
- **强调色-我能供**：#10B981 (Green)
- **背景色**：#F8FAFC
- **认证成功**：#10B981
- **字体**：Plus Jakarta Sans
- **圆角**：6px/8px/12px/16px
- **阴影**：Elevation system (shadow-sm/md/lg/hover)

**UI组件库**：基于原型 common.css 的 CSS Variables 体系

### 8.2 前端页面清单

| 页面编号 | 页面名称 | 原型文件 | 关联后端模块 | 功能描述 |
|----------|----------|----------|--------------|----------|
| P00 | 宣传页 | promotion.html | - | 统一宣传页+二维码入口 |
| P01 | 首页 | index.html | public, opp, ent, feed | 导航、搜索、统计、智能推荐 |
| P02 | 企业名录 | enterprise.html | ent | 筛选条件、企业卡片、认领/创建 |
| P03 | 商机广场 | opportunity.html | opp | 商机列表、筛选、发布、联系 |
| P04 | 校友圈 | feeds.html | feed | 动态列表、发布动态 |
| P05 | 登录页 | login.html | auth_app | 短信/密码登录、忘记密码 |
| P05b | 注册页 | register.html | auth_app | 手机号注册、密码设置 |
| P06 | 搜索结果页 | search.html | search | 三域聚合搜索、Tab切换 |
| P07 | 企业信息维护 | enterprise-admin/enterprise-info.html | ent | 基础信息、Logo、标签 |
| P08 | 员工管理 | enterprise-admin/employee.html | ent-admin | 员工CRUD、密码重置 |
| P09 | 我的商机管理 | enterprise-admin/my-opportunity.html | ent-admin, opp | 本企业商机上下架 |
| P10 | 数据大盘 | platform-admin/dashboard.html | plat-admin | 指标卡片、待办事项 |
| P11 | 企业入驻审核 | platform-admin/audit.html | plat-admin | 审核列表、审核操作 |
| P12 | 企业租户管理 | platform-admin/tenant.html | plat-admin | 企业列表、成员管理 |
| P13 | 商机内容管理 | platform-admin/opportunity-manage.html | plat-admin | 巡查、下架 |
| P14 | 动态内容管理 | platform-admin/feeds-manage.html | plat-admin | 巡查、下架 |
| P15 | 基础数据字典 | platform-admin/master-data.html | plat-admin | 树形CRUD、toggle |
| P16 | 账号与角色权限 | platform-admin/rbac.html | plat-admin | 角色列表、权限配置 |
| P17 | 系统设置 | platform-admin/settings.html | plat-admin | 配置管理 |
| - | 消息通知页 | notification.html | msg | 消息列表、已读 |

### 8.3 前端开发任务拆分

#### 8.3.1 FE-AUTH - 认证模块前端

**页面**：P05 登录页、P05b 注册页
**关联后端**：auth_app

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-AUTH-001 | Vue3项目初始化+路由配置 | P0 | 0.5d | - | 项目结构符合规范 |
| FE-AUTH-002 | 登录页UI实现 | P0 | 1d | FE-AUTH-001 | Tab切换、响应式 |
| FE-AUTH-003 | 短信验证码登录功能 | P0 | 1d | FE-AUTH-002 | 发送验证码、倒计时、登录API对接 |
| FE-AUTH-004 | 密码登录功能 | P0 | 0.5d | FE-AUTH-002 | 密码显示/隐藏、登录API对接 |
| FE-AUTH-005 | 忘记密码功能 | P0 | 1d | FE-AUTH-002 | Step1验证、Step2重置API对接 |
| FE-AUTH-006 | 注册页UI实现 | P0 | 1d | FE-AUTH-001 | 手机号注册、协议勾选 |
| FE-AUTH-007 | 注册功能 | P0 | 1d | FE-AUTH-006 | 发送验证码、注册API对接 |
| FE-AUTH-008 | Token管理+路由守卫 | P0 | 1d | FE-AUTH-003 | JWT存储、自动登录、权限控制 |
| FE-AUTH-009 | 单元测试 | P0 | 0.5d | FE-AUTH-001~008 | 100%覆盖 |

**子任务详情**：
```
FE-AUTH-001: Vue3项目初始化+路由配置
  - 创建 vue3 项目（Vite）
  - 配置路由：/login, /register, /forgot-password
  - 配置 Pinia 状态管理
  - 配置 Axios 实例（baseURL, interceptor）
  - CSS Variables 导入（design system）

FE-AUTH-002: 登录页UI实现
  - 实现 Tab 切换（短信登录/密码登录）
  - 表单验证（手机号11位、验证码6位）
  - 响应式适配
  - 参照原型 login.html

FE-AUTH-003: 短信验证码登录功能
  - POST /auth/sms/send { phone, type: 'login' }
  - POST /auth/sms/login { phone, code, remember_me }
  - 60秒倒计时组件
  - 错误提示 Toast

FE-AUTH-004: 密码登录功能
  - POST /auth/login/password { phone, password, remember_me }
  - 密码显示/隐藏切换
  - 错误次数限制提示

FE-AUTH-005: 忘记密码功能
  - Step1: POST /auth/password/reset/verify { phone, code }
  - Step2: POST /auth/password/reset { phone, code, new_password }
  - 两步式表单交互

FE-AUTH-006: 注册页UI实现
  - 手机号+验证码+密码表单
  - 用户协议勾选
  - 密码强度校验

FE-AUTH-007: 注册功能
  - POST /auth/sms/send { phone, type: 'register' }
  - POST /auth/register { phone, code, password }
  - 注册成功后跳转登录

FE-AUTH-008: Token管理+路由守卫
  - JWT access_token / refresh_token 存储
  - 登录成功及应用初始化时调用 GET /auth/me 获取当前用户信息及权限，并存入 Pinia store
  - Axios 请求拦截器自动携带 Token
  - Token 过期自动刷新
  - 路由守卫：未登录跳转登录页
```

---

#### 8.3.2 FE-PUBLIC - 公共模块前端

**页面**：P00 宣传页、P01 首页
**关联后端**：public, opp, ent, feed

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-PUB-000 | 公共ImageUploader组件 | P0 | 0.5d | FE-AUTH-001 | 统一处理图片压缩、上传和预览逻辑 |
| FE-PUB-001 | 公共Header组件 | P0 | 1d | FE-AUTH-001 | 导航、搜索、通知铃铛、用户菜单 |
| FE-PUB-002 | 首页UI实现 | P0 | 1.5d | FE-PUB-001 | Hero、统计卡片、商机推荐、侧边栏 |
| FE-PUB-003 | 首页API对接 | P0 | 1d | FE-PUB-002 | 统计数据、智能推荐、新企业、校友动态 |
| FE-PUB-004 | 宣传页UI实现 | P1 | 0.5d | FE-PUB-001 | 静态页面 |
| FE-PUB-005 | 单元测试 | P0 | 0.5d | FE-PUB-001~004 | 100%覆盖 |

**子任务详情**：
```
FE-PUB-000: 公共ImageUploader组件
  - 开发公共 ImageUploader 组件
  - 统一处理图片压缩、上传到OSS/本地、并返回URL逻辑
  - 统一处理图片预览功能

FE-PUB-001: 公共Header组件
  - Logo + 导航菜单（首页/商机广场/企业名录/校友圈）
  - 搜索框（跳转搜索页）
  - 通知铃铛（下拉通知列表、全部已读，使用轮询机制定期获取未读数）
  - 用户头像菜单（企业工作台/管理后台/退出）
  - 移动端响应式适配
  - 参照原型 index.html Header 部分

FE-PUB-002: 首页UI实现
  - Hero Section（标题、CTA按钮、热词标签）
  - 统计卡片（企业数/商机数/撮合数/用户数）
  - 智能匹配推荐（4条商机卡片）
  - 侧边栏（新入驻企业+校友动态）
  - 参照原型 index.html
  - 开发公共 ImageUploader 组件，统一处理图片压缩、上传和预览逻辑

FE-PUB-003: 首页API对接
  - GET /public/stats（平台统计）
  - GET /opp/opportunity/recommended（智能推荐）
  - GET /ent/enterprise/newest（新入驻企业）
  - GET /feed/feed/newest（校友动态）

FE-PUB-004: 宣传页UI实现
  - 静态页面
  - 参照原型 promotion.html
```

---

#### 8.3.3 FE-ENT - 企业名录前端

**页面**：P02 企业名录页
**关联后端**：ent

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-ENT-001 | 企业列表页UI | P0 | 1d | FE-PUB-001 | 筛选条件、企业卡片列表 |
| FE-ENT-002 | 企业列表API对接 | P0 | 1d | FE-ENT-001 | GET /ent/enterprise 筛选+分页 |
| FE-ENT-003 | 企业详情Drawer | P0 | 1d | FE-ENT-001 | 企业详情、发布的商机列表 |
| FE-ENT-004 | 认领/创建企业 | P0 | 1.5d | FE-ENT-003 | 认领表单、创建表单、协议确认 |
| FE-ENT-005 | 字典接口对接 | P0 | 0.5d | FE-ENT-001 | 行业/品类/地区级联选择 |
| FE-ENT-006 | 单元测试 | P0 | 0.5d | FE-ENT-001~005 | 100%覆盖 |

**子任务详情**：
```
FE-ENT-001: 企业列表页UI
  - 筛选区域（行业、品类、地区、认证状态、关键词）
  - 企业卡片网格（Logo、名称、行业、标签、认证状态）
  - 分页组件
  - 参照原型 enterprise.html

FE-ENT-002: 企业列表API对接
  - GET /ent/enterprise
    params: industry_id, sub_industry_id, category_id, province_id, region_id, auth_status, keyword, page, page_size
  - 加载更多/分页切换

FE-ENT-003: 企业详情Drawer
  - GET /ent/enterprise/{id}
  - 侧边Drawer展示企业详情
  - auth_status=VERIFIED 显示完整信息
  - auth_status!=VERIFIED 脱敏处理

FE-ENT-004: 认领/创建企业
  - 认领：POST /ent/enterprise/claim { credit_code }
  - 创建：POST /ent/enterprise/create
  - 表单验证、协议确认弹窗

FE-ENT-005: 字典接口对接
  - GET /ent/industry?parent_id=0（一级行业）
  - GET /ent/industry?parent_id={id}（二级行业）
  - GET /ent/category?industry_id={id}（品类）
  - GET /ent/region?parent_id=0（省份）
  - GET /ent/region?parent_id={id}（城市）
  - 级联选择器组件
```

---

#### 8.3.4 FE-OPP - 商机广场前端

**页面**：P03 商机广场页
**关联后端**：opp

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-OPP-001 | 商机列表页UI | P0 | 1d | FE-PUB-001 | 筛选条件、商机卡片 |
| FE-OPP-002 | 商机列表API对接 | P0 | 1d | FE-OPP-001 | GET /opp/opportunity 筛选+分页 |
| FE-OPP-003 | 发布商机弹窗 | P0 | 1.5d | FE-OPP-001 | 多步表单、标签选择、图片上传 |
| FE-OPP-004 | 获取联系方式 | P0 | 1d | FE-OPP-001 | 确认弹窗、结果展示、复制功能 |
| FE-OPP-005 | 商机详情页 | P1 | 1d | FE-OPP-001 | 商机详情、联系方式脱敏 |
| FE-OPP-006 | 单元测试 | P0 | 0.5d | FE-OPP-001~005 | 100%覆盖 |

**子任务详情**：
```
FE-OPP-001: 商机列表页UI
  - 筛选区域（类型、行业的、品类、地区、关键词）
  - 商机卡片网格（类型标签、标题、标签、企业信息）
  - 分页组件
  - 参照原型 opportunity.html

FE-OPP-002: 商机列表API对接
  - GET /opp/opportunity
    params: type, industry_id, sub_industry_id, category_id, province_id, region_id, keyword, page, page_size
  - 排序：created_at 倒序

FE-OPP-003: 发布商机弹窗
  - 多步表单（Step1: 类型+标题, Step2: 行业+品类+地区, Step3: 标签+描述）
  - 标签选择（预设+自定义）
  - 参照原型 index.html publishModal

FE-OPP-004: 获取联系方式
  - POST /opp/opportunity/{id}/contact
  - 确认弹窗 → 结果展示（联系人、手机号、微信）
  - 复制功能
  - 脱敏手机号显示 138****8888

FE-OPP-005: 商机详情页
  - 商机详情展示
  - 联系方式获取
  - 相关推荐
```

---

#### 8.3.5 FE-FEED - 校友圈前端

**页面**：P04 校友圈页
**关联后端**：feed

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-FEED-001 | 动态列表页UI | P0 | 1d | FE-PUB-001 | 动态卡片、图片展示 |
| FE-FEED-002 | 动态列表API对接 | P0 | 0.5d | FE-FEED-001 | GET /feed/feed 分页 |
| FE-FEED-003 | 发布动态 | P0 | 1d | FE-FEED-001 | 文字+图片发布 |
| FE-FEED-004 | 动态详情 | P1 | 0.5d | FE-FEED-001 | 动态详情展示 |
| FE-FEED-005 | 单元测试 | P0 | 0.5d | FE-FEED-001~004 | 100%覆盖 |

**子任务详情**：
```
FE-FEED-001: 动态列表页UI
  - 动态卡片（头像、昵称、企业、内容、图片网格、时间）
  - 无限滚动/分页
  - 参照原型 feeds.html

FE-FEED-002: 动态列表API对接
  - GET /feed/feed
    params: page, page_size
  - 仅显示 status=ACTIVE

FE-FEED-003: 发布动态
  - 文字输入（最多500字）
  - 图片上传（最多9张）
  - POST /feed/feed
  - 预览功能

FE-FEED-004: 动态详情
  - GET /feed/feed/{id}
  - 图片点击放大
  - 当前暂不实现发布人删除动态功能
```

---

#### 8.3.6 FE-SEARCH - 搜索服务前端

**页面**：P06 搜索结果页
**关联后端**：search

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-SCH-001 | 搜索结果页UI | P0 | 1d | FE-PUB-001 | Tab切换、商机/企业/动态列表 |
| FE-SCH-002 | 搜索API对接 | P0 | 1d | FE-SCH-001 | GET /search?keyword&tab |
| FE-SCH-003 | 搜索历史+热词 | P1 | 0.5d | FE-SCH-001 | LocalStorage 存储 |
| FE-SCH-004 | 单元测试 | P0 | 0.5d | FE-SCH-001~003 | 100%覆盖 |

**子任务详情**：
```
FE-SCH-001: 搜索结果页UI
  - 搜索框（header 同步）
  - Tab 切换（找商机/找企业/看动态）
  - 结果列表（商机卡片/企业卡片/动态卡片）
  - 空状态处理
  - 参照原型 search.html

FE-SCH-002: 搜索API对接
  - GET /search?keyword=xxx&tab=opp|ent|feed
  - 数据加载逻辑：首次搜索无 `tab` 参数时，调用接口全量查询三个域的前置数据；切换 Tab 并向下滚动加载更多时，带上具体 `tab` 参数进行针对性的单域分页/无限滚动请求。
  - 分页加载
  - BR-SCH-01 敏感词过滤

FE-SCH-003: 搜索历史+热词
  - LocalStorage 存储最近搜索词（最多10条）
  - 清除历史记录
  - 热门搜索词展示
```

---

#### 8.3.7 FE-ENT-ADMIN - 企业端管理前端

**页面**：P07 企业信息维护、P08 员工管理、P09 我的商机管理
**关联后端**：ent-admin, ent, opp

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-ADM-001 | 企业端Layout | P0 | 0.5d | FE-AUTH-008 | 侧边导航、Header |
| FE-ADM-002 | 企业信息维护页 | P0 | 1d | FE-ADM-001 | 信息展示、编辑表单 |
| FE-ADM-003 | 企业信息API对接 | P0 | 1d | FE-ADM-002 | GET/PUT /ent/enterprise/{id} |
| FE-ADM-004 | 员工管理页 | P0 | 1.5d | FE-ADM-001 | 员工列表、新增/编辑弹窗 |
| FE-ADM-005 | 员工管理API对接 | P0 | 1d | FE-ADM-004 | CRUD /ent-admin/employees |
| FE-ADM-006 | 我的商机管理页 | P0 | 1d | FE-ADM-001 | 商机列表、下架/重新发布操作 |
| FE-ADM-007 | 商机管理API对接 | P0 | 1d | FE-ADM-006 | GET /ent-admin/opportunities, POST offline, PUT republish |
| FE-ADM-008 | 单元测试 | P0 | 0.5d | FE-ADM-001~007 | 100%覆盖 |

**子任务详情**：
```
FE-ADM-001: 企业端Layout
  - 侧边栏（企业工作台、员工管理、我的商机）
  - 深色主题（#0F172A）
  - 参照原型 enterprise-admin/*.html

FE-ADM-002: 企业信息维护页
  - 基础信息展示（名称、信用代码等）
  - 可编辑字段（logo、标签、详细描述）
  - 参照原型 enterprise-info.html

FE-ADM-003: 企业信息API对接
  - GET /ent/enterprise/my
  - PUT /ent/enterprise/{id}
  - 仅企业管理员可编辑部分字段

FE-ADM-004: 员工管理页
  - 员工列表（姓名、手机号、角色、状态）
  - 新增员工弹窗
  - 编辑员工弹窗
  - 重置密码、停用/启用、解绑操作
  - 参照原型 employee.html

FE-ADM-005: 员工管理API对接
  - GET /ent-admin/employees
  - POST /ent-admin/employees
  - PUT /ent-admin/employees/{id}
  - POST /ent-admin/employees/{id}/reset-password
  - PUT /ent-admin/employees/{id}/disable
  - POST /ent-admin/employees/{id}/unbind

FE-ADM-006: 我的商机管理页
  - 商机列表（类型、标题、状态、发布时间）
  - 编辑、下架、重新发布操作
  - 参照原型 my-opportunity.html

FE-ADM-007: 商机管理API对接
  - GET /ent-admin/opportunities
  - PUT /ent-admin/opportunities/{id}
  - POST /opp/opportunity/{id}/offline (下架)
  - PUT /ent-admin/opportunities/{id}/republish (重新发布)
```

---

#### 8.3.8 FE-PLAT-ADMIN - 平台端管理前端

**页面**：P10~P17 全部平台管理页面
**关联后端**：plat-admin

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-PLAT-001 | 平台端Layout | P0 | 0.5d | FE-AUTH-008 | 侧边导航、通知、Header |
| FE-PLAT-002 | 数据大盘页 | P0 | 1.5d | FE-PLAT-001 | 统计卡片、趋势图表 |
| FE-PLAT-003 | 数据大盘API对接 | P0 | 1d | FE-PLAT-002 | GET /plat-admin/dashboard/stats, /trend |
| FE-PLAT-004 | 企业审核页 | P0 | 1.5d | FE-PLAT-001 | 审核列表、审核弹窗 |
| FE-PLAT-005 | 企业审核API对接 | P0 | 1d | FE-PLAT-004 | GET /plat-admin/audit/enterprise, POST approve/reject |
| FE-PLAT-006 | 企业租户管理页 | P0 | 2d | FE-PLAT-001 | 企业列表、成员CRUD |
| FE-PLAT-007 | 租户管理API对接 | P0 | 1.5d | FE-PLAT-006 | CRUD /plat-admin/tenant/enterprise, /member |
| FE-PLAT-008 | 商机内容管理页 | P0 | 1d | FE-PLAT-001 | 商机列表、下架操作 |
| FE-PLAT-009 | 商机内容API对接 | P0 | 0.5d | FE-PLAT-008 | GET /plat-admin/content/opportunity, PUT offline |
| FE-PLAT-010 | 动态内容管理页 | P0 | 1d | FE-PLAT-001 | 动态列表、下架操作 |
| FE-PLAT-011 | 动态内容API对接 | P0 | 0.5d | FE-PLAT-010 | GET /plat-admin/content/feed, PUT offline |
| FE-PLAT-012 | 基础数据字典页 | P0 | 1.5d | FE-PLAT-001 | 树形结构、增删改、toggle |
| FE-PLAT-013 | 字典API对接 | P0 | 1d | FE-PLAT-012 | CRUD /plat-admin/master-data, PUT toggle-status |
| FE-PLAT-014 | 账号与角色权限页 | P0 | 1.5d | FE-PLAT-001 | 角色列表、权限矩阵 |
| FE-PLAT-015 | RBAC API对接 | P0 | 1d | FE-PLAT-014 | GET /plat-admin/role, PUT permissions |
| FE-PLAT-016 | 系统设置页 | P1 | 1d | FE-PLAT-001 | 配置项GET/PUT |
| FE-PLAT-017 | 系统设置API对接 | P1 | 0.5d | FE-PLAT-016 | GET/PUT /plat-admin/settings |
| FE-PLAT-018 | 单元测试 | P0 | 1.5d | FE-PLAT-001~017 | 100%覆盖 |

**子任务详情**：
```
FE-PLAT-001: 平台端Layout
  - 侧边栏（数据中心/企业管理/内容管理/系统管理）
  - 深色主题（#1a1f36）
  - 通知下拉（GET /plat-admin/notification）
  - 参照原型 platform-admin/*.html

FE-PLAT-002: 数据大盘页
  - 4个统计卡片（企业数/商机数/撮合数/活跃用户）
  - 趋势图表（近30天）
  - 待办事项
  - 参照原型 dashboard.html

FE-PLAT-003: 数据大盘API对接
  - GET /plat-admin/dashboard/stats
  - GET /plat-admin/dashboard/trend?type=opportunity&period=30

FE-PLAT-004: 企业审核页
  - 审核列表（状态筛选、关键词搜索）
  - 审核详情弹窗（企业信息、审核操作）
  - 参照原型 audit.html

FE-PLAT-005: 企业审核API对接
  - GET /plat-admin/audit/enterprise?status=PENDING
  - POST /plat-admin/audit/enterprise/{id}/approve
  - POST /plat-admin/audit/enterprise/{id}/reject

FE-PLAT-006: 企业租户管理页
  - 企业列表（搜索、状态筛选）
  - 企业详情（成员列表）
  - 新增成员弹窗
  - 成员编辑弹窗
  - 参照原型 tenant.html

FE-PLAT-007: 租户管理API对接
  - GET /plat-admin/tenant/enterprise
  - GET /plat-admin/tenant/enterprise/{id}
  - PUT /plat-admin/tenant/enterprise/{id}/toggle-status
  - GET /plat-admin/tenant/enterprise/{id}/member
  - POST /plat-admin/tenant/enterprise/{id}/member
  - PUT /plat-admin/tenant/member/{id}
  - POST /plat-admin/tenant/member/{id}/reset-password
  - POST /plat-admin/tenant/member/{id}/unbind

FE-PLAT-008: 商机内容管理页
  - 商机列表（类型/状态筛选、关键词搜索）
  - 强制下架弹窗
  - 参照原型 opportunity-manage.html

FE-PLAT-009: 商机内容API对接
  - GET /plat-admin/content/opportunity
  - GET /plat-admin/content/opportunity/{id}
  - PUT /plat-admin/content/opportunity/{id}/offline

FE-PLAT-010: 动态内容管理页
  - 动态列表（状态筛选、关键词搜索）
  - 强制下架弹窗
  - 参照原型 feeds-manage.html

FE-PLAT-011: 动态内容API对接
  - GET /plat-admin/content/feed
  - GET /plat-admin/content/feed/{id}
  - PUT /plat-admin/content/feed/{id}/offline

FE-PLAT-012: 基础数据字典页
  - 树形结构展示
  - 新增/编辑弹窗
  - 启用/禁用 toggle
  - 参照原型 master-data.html

FE-PLAT-013: 字典API对接
  - GET /plat-admin/master-data
  - POST /plat-admin/master-data
  - PUT /plat-admin/master-data/{id}
  - PUT /plat-admin/master-data/{id}/toggle-status

FE-PLAT-014: 账号与角色权限页
  - 角色列表
  - 角色权限详情
  - 权限配置矩阵
  - 参照原型 rbac.html

FE-PLAT-015: RBAC API对接
  - GET /plat-admin/role
  - GET /plat-admin/role/{id}
  - PUT /plat-admin/role/{id}/permissions

FE-PLAT-016: 系统设置页
  - 配置项展示
  - 配置项编辑
  - 参照原型 settings.html

FE-PLAT-017: 系统设置API对接
  - GET /plat-admin/settings
  - PUT /plat-admin/settings
```

---

#### 8.3.9 FE-MSG - 消息通知前端

**页面**：消息通知页（notification.html）
**关联后端**：msg

| Task ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 验收标准 |
|---------|----------|--------|----------|------|----------|
| FE-MSG-001 | 消息通知页UI | P0 | 1d | FE-PUB-001 | 消息列表、已读/未读筛选 |
| FE-MSG-002 | 消息API对接 | P0 | 1d | FE-MSG-001 | GET /msg/notifications, PUT read, PUT read-all |
| FE-MSG-003 | 单元测试 | P0 | 0.5d | FE-MSG-001~002 | 100%覆盖 |

**子任务详情**：
```
FE-MSG-001: 消息通知页UI
  - 消息列表（类型图标、标题、内容、时间）
  - 已读/未读筛选 Tab
  - 全部已读按钮
  - 参照原型 notification.html

FE-MSG-002: 消息API对接
  - GET /msg/notifications?is_read=false&page=1
  - PUT /msg/notifications/{id}/read
  - PUT /msg/notifications/read-all
  - GET /msg/notifications/recent?limit=5（Header 铃铛用）
  - 前端采用定时轮询机制（或WebSocket/SSE），确保 Header 铃铛的未读消息数字和列表能够实时刷新
```

---

### 8.4 前端技术栈

| 技术 | 用途 | 版本 |
|------|------|------|
| Vue3 | 核心框架 | ^3.4 |
| Vite | 构建工具 | ^5.0 |
| Vue Router | 路由管理 | ^4.2 |
| Pinia | 状态管理 | ^2.1 |
| Axios | HTTP 客户端 | ^1.6 |
| Element Plus | UI 组件库（可选） | ^2.4 |

### 8.5 前端项目结构

```
frontend/
├── src/
│   ├── assets/              # 静态资源
│   │   └── css/
│   │       └── variables.css # CSS Variables（设计系统）
│   ├── components/          # 公共组件
│   │   ├── Header.vue       # 公共Header
│   │   ├── Footer.vue
│   │   ├── Modal.vue
│   │   ├── Drawer.vue
│   │   ├── Toast.vue
│   │   └── Pagination.vue
│   ├── composables/         # 组合式函数
│   │   ├── useAuth.js       # 认证相关
│   │   ├── useApi.js        # API 请求
│   │   └── useDict.js       # 字典级联
│   ├── layouts/
│   │   ├── DefaultLayout.vue   # 前台布局
│   │   ├── AdminLayout.vue     # 管理端布局
│   │   └── AuthLayout.vue      # 认证页布局
│   ├── pages/               # 页面
│   │   ├── auth/
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── public/
│   │   │   ├── Index.vue
│   │   │   ├── Promotion.vue
│   │   │   └── Search.vue
│   │   ├── enterprise/
│   │   │   └── Index.vue
│   │   ├── opportunity/
│   │   │   ├── Index.vue
│   │   │   └── Detail.vue
│   │   ├── feed/
│   │   │   └── Index.vue
│   │   ├── ent-admin/
│   │   │   ├── EnterpriseInfo.vue
│   │   │   ├── Employee.vue
│   │   │   └── MyOpportunity.vue
│   │   ├── plat-admin/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Audit.vue
│   │   │   ├── Tenant.vue
│   │   │   ├── OpportunityManage.vue
│   │   │   ├── FeedManage.vue
│   │   │   ├── MasterData.vue
│   │   │   ├── Rbac.vue
│   │   │   └── Settings.vue
│   │   └── notification/
│   │       └── Index.vue
│   ├── router/
│   │   └── index.js         # 路由配置+守卫
│   ├── stores/
│   │   ├── auth.js          # 认证状态
│   │   └── notification.js  # 通知状态
│   ├── api/                 # API 接口封装
│   │   ├── auth.js
│   │   ├── enterprise.js
│   │   ├── opportunity.js
│   │   ├── feed.js
│   │   ├── message.js
│   │   └── search.js
│   ├── App.vue
│   └── main.js
├── index.html
├── vite.config.js
└── package.json
```

### 8.6 前端开发工时估算

| 模块            | Task数  | 预估工时(d) | 并行开发人数 | 实际工期(d) |
| ------------- | ------ | ------- | ------ | ------- |
| FE-AUTH       | 9      | 8.5     | 2      | 4.5     |
| FE-PUBLIC     | 5      | 5.5     | 2      | 3       |
| FE-ENT        | 6      | 6       | 2      | 3       |
| FE-OPP        | 6      | 6.5     | 2      | 3.5     |
| FE-FEED       | 5      | 4.5     | 1      | 4.5     |
| FE-SEARCH     | 4      | 4       | 1      | 4       |
| FE-ENT-ADMIN  | 8      | 8.5     | 2      | 4.5     |
| FE-PLAT-ADMIN | 18     | 16.5    | 3      | 6       |
| FE-MSG        | 3      | 3       | 1      | 3       |
| **合计**        | **64** | **63**  | -      | **10**  |

**说明**：
- 前端总工期：10个工作日（与后端并行）
- 前端可与后端同步完成
- 关键路径：FE-AUTH → FE-PUBLIC → 业务模块

### 8.7 前端验收标准

- [ ] 所有页面 UI 与原型一致（参照 common.css 设计系统）
- [ ] API 响应正确处理（Loading/Error/Empty 状态）
- [ ] 表单验证完整（手机号、密码强度、必填项）
- [ ] 权限控制（未登录跳转、角色权限校验）
- [ ] 响应式适配（PC/Tablet/Mobile）
- [ ] 单元测试 100% 通过

---

## 9. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 短信服务依赖第三方 | 开发阶段无法真实发送 | Mock短信服务，统一存储验证码 |
| 图片上传存储 | 生产环境需配置OSS | 开发阶段使用本地存储，后续扩展 |
| 搜索性能 | 大数据量下搜索慢 | 使用MySQL全文索引，必要时引入ES |
| 权限变更事务 | 审核通过时用户角色+企业状态需同时更新 | 使用Django事务atomic() |
| 前后端并行开发 | 接口定义可能有偏差 | 每日站会对齐接口，先约定后开发 |

---

*文档结束*
