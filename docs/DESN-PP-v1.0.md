---
status: 草稿
---

# 技术设计文档

## XiaoLianTong (校链通)

| 文档信息 | 内容 |
|----------|------|
| 项目名称 | XiaoLianTong (校链通) |
| 文档版本 | v1.1 |
| 创建日期 | 2026-04-02 |
| 关联PRD | [PRD-XiaoLianTong-v1.0.md](PRD-XiaoLianTong-v1.0.md) |
| 文档状态 | 待审批 |
| 方案选择 | 方案一（单体架构）+ Django + DRF + MySQL |

---

## 修订历史

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| v1.0 | 2026-04-02 | ARCH | 初始版本 |
| v1.1 | 2026-04-03 | ARCH | 对齐 PRD v1.1：新增宣传页、更新企业认证必填字段 |

---

## 1. 技术架构

### 1.1 技术栈选型

| 层级           | 技术选型                  | 版本    | 说明                        |
| ------------ | --------------------- | ----- | ------------------------- |
| **前端框架**     | Vue3                  | 3.4+  | 组合式 API (Composition API) |
| **UI 组件库**   | Element Plus          | 2.5+  | 企业级 UI 组件库                |
| **状态管理**     | Pinia                 | 2.1+  | Vue3 官方推荐状态管理             |
| **HTTP 客户端** | Axios                 | 1.6+  | HTTP 请求库                  |
| **路由**       | Vue Router            | 4.2+  | Vue3 官方路由                 |
| **后端框架**     | Django 4.2+           | 4.2+  | Python Web 框架             |
| **API 框架**   | Django REST Framework | 3.14+ | RESTful API               |
| **数据库**      | MySQL                 | 8.0+  | 关系型数据库                    |
| **认证**       | SimpleJWT             | -     | Token 认证                  |
| **Docker**   | Docker Compose        | 2.20+ | 容器编排                      |

### 1.2 后端核心依赖

```txt
Django==4.2.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.0
django-filter==23.5
mysqlclient==2.2.0
gunicorn==21.2.0
python-dotenv==1.0.0
Pillow==10.1.0
```

### 1.3 前端核心依赖

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "axios": "^1.6.0",
    "@vueuse/core": "^10.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0"
  }
}
```

### 1.4 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端                                │
│                  Vue3 + Element Plus                        │
│              (PC 浏览器 / 移动端 H5)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼─────────────────────────────────────┐
│                      Nginx                                    │
│            静态文件服务 + API 反向代理                        │
└──────┬────────────────────────────┬───────────────────────────┘
       │ /api/*                   │ /*
┌──────▼──────┐           ┌─────────▼─────────┐
│  后端服务    │           │   前端静态文件      │
│  Django+DRF │           │                   │
│  :8000      │           │                   │
└──────┬──────┘           └───────────────────┘
       │
┌──────▼──────┐
│   数据库     │
│   MySQL     │
│   :3306     │
└─────────────┘
```

### 1.5 项目目录结构

```
XiaoLianTong/
├── backend/                     # 后端代码（Django 项目）
│   ├── config/                 # Django 配置
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── auth_app/          # 认证模块
│   │   │   ├── models.py      # User, SMSCode
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   └── urls.py
│   │   ├── enterprise/         # 企业模块
│   │   │   ├── models.py      # Enterprise, UserProfile
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   └── urls.py
│   │   ├── opportunity/        # 商机模块
│   │   │   ├── models.py      # Opportunity, ContactLog
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   └── urls.py
│   │   ├── feed/               # 校友圈模块
│   │   │   ├── models.py      # Feed
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   └── urls.py
│   │   ├── platform_admin/     # 平台管理模块
│   │   │   ├── models.py      # AuditRecord, OperationLog, MasterData
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   └── urls.py
│   │   └── message/            # 消息模块
│   │       ├── models.py      # Message
│   │       ├── views.py
│   │       ├── serializers.py
│   │       └── urls.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── api/                # API 请求封装
│   │   ├── views/              # 页面
│   │   ├── components/         # 公共组件
│   │   ├── composables/        # 组合式函数
│   │   ├── store/             # Pinia 状态
│   │   ├── router/            # 路由配置
│   │   └── styles/            # 全局样式
│   ├── package.json
│   └── vite.config.ts
├── docker/                     # 部署配置
│   ├── docker-compose.yml
│   ├── nginx/
│   │   └── nginx.conf
│   └── Dockerfile
└── tests/                      # 测试代码
```

### 1.6 模块清单

| 模块标识       | 模块名称  | 迭代顺序 | 说明                  |
| ---------- | ----- | ---- | ------------------- |
| auth_app   | 认证模块  | 1    | 登录、注册、Token 管理、短信验证 |
| ent        | 企业名录  | 1    | 企业浏览、认领、创建          |
| opp        | 商机广场  | 1    | 供需发布、检索、撮合          |
| feed       | 校友圈   | 1    | 动态发布、浏览             |
| ent-admin  | 企业端管理 | 1    | 企业信息维护、员工管理、商机管理    |
| plat-admin | 平台端管理 | 1    | 数据大盘、企业审核、基础数据、RBAC |
| msg        | 消息通知  | 2    | 站内消息、撮合通知           |
| search     | 搜索服务  | 2    | 统一搜索                |

---

## 2. 模块与数据库设计

### 2.1 数据库设计原则

| 原则 | 说明 |
|------|------|
| 使用 Django 内置认证 | 用户系统使用 `django.contrib.auth`，不重复造轮子 |
| 业务扩展表 | 仅新建业务相关表（Django 外键关联 auth.User） |
| RBAC | 使用 Django 内置 Group + Permission 体系 |

### 2.2 Django 内置表（复用）

| 表名 | 说明 |
|------|------|
| auth_user | 用户表（username, password, email, is_active, last_login 等） |
| auth_group | 角色组（对应平台角色） |
| auth_permission | 权限表 |
| auth_group_permissions | 组-权限关联 |
| user_user_permissions | 用户-权限关联 |
| django_admin_log | 系统操作日志（Admin 站点） |

### 2.3 业务扩展表（共 8 张）

#### ent_enterprise（企业表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| name | VARCHAR(200) | Y | 企业全称 |
| credit_code | VARCHAR(18) | Y | 统一社会信用代码 |
| legal_representative | VARCHAR(100) | Y | 法人姓名 |
| business_license | VARCHAR(500) | Y | 营业执照URL |
| logo_url | VARCHAR(500) | N | Logo地址 |
| industry_id | BIGINT | Y | 所属行业 |
| category_id | BIGINT | N | 主营业务品类 |
| region_id | BIGINT | Y | 所在地区 |
| tags | JSON | N | 供需标签 |
| description | TEXT | N | 企业简介 |
| admin_user | FK(auth.User) | N | 企业管理员 |
| auth_status | VARCHAR(20) | Y | UNCLAIMED/PENDING/VERIFIED/REJECTED |
| created_at | DATETIME | Y | 创建时间 |
| updated_at | DATETIME | Y | 更新时间 |

#### ent_user_profile（用户企业扩展表）

| 字段             | 类型                 | 必填  | 说明                                     |
| -------------- | ------------------ | --- | -------------------------------------- |
| id             | BIGINT             | Y   | 主键                                     |
| user           | FK(auth.User)      | Y   | 关联用户（一对一）                              |
| enterprise     | FK(ent_enterprise) | N   | 归属企业                                   |
| role_code      | VARCHAR(20)        | Y   | 业务角色码（enterprise_admin/employee/guest） |
| real_name      | VARCHAR(50)        | Y   | 真实姓名                                   |
| contact_phone  | VARCHAR(11)        | N   | 联系电话                                   |
| contact_wechat | VARCHAR(50)        | N   | 微信                                     |
| created_at     | DATETIME           | Y   | 创建时间                                   |
| updated_at     | DATETIME           | Y   | 更新时间                                   |

#### opp_opportunity（商机表）

| 字段             | 类型                 | 必填  | 说明             |
| -------------- | ------------------ | --- | -------------- |
| id             | BIGINT             | Y   | 主键             |
| type           | VARCHAR(10)        | Y   | BUY/SUPPLY     |
| title          | VARCHAR(200)       | Y   | 商机标题           |
| enterprise     | FK(ent_enterprise) | Y   | 发布企业           |
| publisher      | FK(auth.User)      | Y   | 发布人            |
| industry_id    | BIGINT             | Y   | 所属行业           |
| category_id    | BIGINT             | Y   | 业务品类           |
| region_id      | BIGINT             | Y   | 所在地区           |
| tags           | JSON               | N   | 业务标签           |
| detail         | TEXT               | Y   | 详细描述           |
| status         | VARCHAR(20)        | Y   | ACTIVE/OFFLINE |
| view_count     | INT                | Y   | 浏览量            |
| contact_name   | VARCHAR(50)        | N   | 联系人            |
| contact_phone  | VARCHAR(11)        | N   | 联系电话           |
| contact_wechat | VARCHAR(50)        | N   | 微信             |
| created_at     | DATETIME           | Y   | 创建时间           |
| updated_at     | DATETIME           | Y   | 更新时间           |

#### opp_contact_log（商机撮合日志表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| opportunity | FK(opp_opportunity) | Y | 涉及的商机 |
| getter_user | FK(auth.User) | Y | 获取方用户 |
| getter_enterprise | FK(ent_enterprise) | Y | 获取方企业 |
| created_at | DATETIME | Y | 获取时间 |

#### feed_feed（动态表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| publisher | FK(auth.User) | Y | 发布人 |
| enterprise | FK(ent_enterprise) | Y | 发布人所属企业 |
| content | TEXT | Y | 动态内容 |
| images | JSON | N | 图片URL数组（最多9张） |
| status | VARCHAR(20) | Y | ACTIVE/OFFLINE |
| created_at | DATETIME | Y | 创建时间 |
| updated_at | DATETIME | Y | 更新时间 |

#### plat_audit_record（审批记录表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| enterprise | FK(ent_enterprise) | Y | 申请企业 |
| applicant | FK(auth.User) | Y | 申请人 |
| auditor | FK(auth.User) | N | 审批人 |
| status | VARCHAR(20) | Y | PENDING/VERIFIED/REJECTED |
| applicant_position | VARCHAR(50) | Y | 申请人职务 |
| legal_representative | VARCHAR(100) | Y | 法人姓名 |
| business_license | VARCHAR(500) | Y | 营业执照URL |
| audit_reason | TEXT | N | 驳回原因 |
| created_at | DATETIME | Y | 操作时间 |

#### plat_operation_log（操作日志表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| user | FK(auth.User) | Y | 操作人 |
| action | VARCHAR(50) | Y | 操作动作 |
| target_type | VARCHAR(50) | Y | 对象类型 |
| target_id | BIGINT | Y | 对象ID |
| detail | TEXT | N | 变更详情 |
| ip_address | VARCHAR(50) | Y | IP地址 |
| created_at | DATETIME | Y | 操作时间 |

#### plat_master_data（基础数据字典表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| category | VARCHAR(50) | Y | 字典类别（industry/category/tag/region） |
| parent | FK(plat_master_data) | N | 父级ID |
| name | VARCHAR(100) | Y | 名称 |
| code | VARCHAR(50) | N | 编码 |
| sort_order | INT | Y | 排序 |
| is_active | TINYINT(1) | Y | 是否启用 |
| created_at | DATETIME | Y | 创建时间 |

#### msg_message（消息通知表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| receiver | FK(auth.User) | Y | 接收人 |
| sender | FK(auth.User) | N | 发送人（系统消息为NULL） |
| type | VARCHAR(20) | Y | 消息类型 |
| title | VARCHAR(200) | Y | 标题 |
| content | TEXT | Y | 内容 |
| is_read | TINYINT(1) | Y | 是否已读 |
| related_type | VARCHAR(50) | N | 关联对象类型 |
| related_id | BIGINT | N | 关联对象ID |
| created_at | DATETIME | Y | 创建时间 |

#### auth_sms_code（短信验证码表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| phone | VARCHAR(11) | Y | 手机号 |
| code | VARCHAR(6) | Y | 6位验证码 |
| expire_at | DATETIME | Y | 过期时间（创建时间+5分钟） |
| is_used | TINYINT(1) | Y | 是否已使用 |
| created_at | DATETIME | Y | 创建时间 |

### 2.4 ER 图

```
┌─────────────┐       ┌─────────────┐
│  auth_user  │──────▶│ent_user_profile│  (一对一扩展)
└──────┬──────┘       └──────┬──────┘
       │                     │
       │              ┌──────┴──────┐
       │              │             │
       ▼              ▼             │
┌─────────────┐  ┌─────────────┐   │
│auth_group   │  │ent_enterprise│◄──┘
└─────────────┘  └──────┬──────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│opp_opportunity│  │  feed_feed  │  │plat_audit_record│
└──────┬──────┘  └─────────────┘  └─────────────┘
       │
       ▼
┌─────────────┐
│opp_contact_log│
└─────────────┘
       │
       ▼
┌─────────────┐       ┌─────────────┐
│ msg_message │       │plat_operation_log│
└─────────────┘       └─────────────┘
       ▲
       │
┌─────────────┐
│plat_master_data│
└─────────────┘
```

---

## 3. API 设计

### 3.1 API 规范

**Base URL**：`/api/v1/`

**统一响应格式**：
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

**分页响应格式**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": []
  }
}
```

**错误响应格式**：
```json
{
  "code": 400,
  "message": "参数错误",
  "errors": {
    "field_name": ["错误描述"]
  }
}
```

### 3.2 认证接口

#### POST /api/v1/auth/login/sms（短信验证码登录）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| code | string | Y | 6位验证码 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | JWT访问令牌 |
| refresh_token | string | JWT刷新令牌 |
| user_id | int | 用户ID |
| phone | string | 手机号 |

---

#### POST /api/v1/auth/login/password（密码登录）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| password | string | Y | 密码 |

**响应字段**: 同上

---

#### POST /api/v1/auth/register（用户注册）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| code | string | Y | 6位验证码 |
| password | string | Y | 密码，8-20位 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | JWT访问令牌 |
| refresh_token | string | JWT刷新令牌 |
| user_id | int | 用户ID |

---

#### POST /api/v1/auth/logout（登出）
**权限**: 已认证

**请求字段**: 无

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 成功消息 |

---

#### POST /api/v1/auth/refresh（刷新Token）
**权限**: 已认证

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | Y | 刷新令牌 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | 新JWT访问令牌 |
| refresh_token | string | 新JWT刷新令牌 |

---

#### GET /api/v1/auth/me（获取当前用户信息）
**权限**: 已认证

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| phone | string | 手机号 |
| real_name | string | 真实姓名 |
| role_code | string | 角色码 |
| enterprise_id | int | 企业ID（无则null） |
| enterprise_name | string | 企业名称（无则null） |
| enterprise_status | string | 企业认证状态（无则null） |

---

### 3.3 宣传页接口

#### GET /api/v1/public/stats（获取平台统计数据）
**权限**: 公开

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| enterprise_count | int | 入驻企业数 |
| opportunity_count | int | 累计商机数 |
| deal_count | int | 成功撮合数 |
| active_user_count | int | 活跃校友数（近30天有登录的用户数） |

---

### 3.4 企业相关接口

#### GET /api/v1/ent/enterprise（企业列表）
**权限**: 公开

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码，默认1 |
| page_size | int | N | 每页条数，默认20 |
| industry_id | int | N | 行业ID |
| category_id | int | N | 业务品类ID |
| region_id | int | N | 地区ID |
| tags | string | N | 标签，逗号分隔 |
| keyword | string | N | 关键词搜索 |
| auth_status | string | N | 认证状态筛选：UNCLAIMED/PENDING/VERIFIED/REJECTED |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总数 |
| page | int | 当前页 |
| page_size | int | 每页条数 |
| items | array | 企业列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 企业ID |
| name | string | 企业名称 |
| logo_url | string | Logo URL |
| industry | string | 行业名称 |
| category | string | 主营业务品类名称 |
| region | string | 地区名称 |
| tags | array | 标签列表 |
| auth_status | string | 认证状态 |

---

#### GET /api/v1/ent/enterprise/{id}（企业详情）
**权限**: 已认证

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 企业ID |
| name | string | 企业全称 |
| credit_code | string | 统一社会信用代码（已认证用户可见） |
| logo_url | string | Logo URL |
| industry_id | int | 行业ID |
| industry_name | string | 行业名称 |
| category_id | int | 品类ID |
| category_name | string | 品类名称 |
| region_id | int | 地区ID |
| region_name | string | 地区名称 |
| tags | array | 标签列表 |
| description | string | 企业简介 |
| auth_status | string | UNCLAIMED/PENDING/VERIFIED/REJECTED |
| admin_user_id | int | 管理员用户ID |
| created_at | datetime | 创建时间 |
| opportunities | array | 该企业发布的商机列表（最新3条） |

**opportunities 元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 商机ID |
| type | string | BUY/SUPPLY |
| title | string | 商机标题 |
| view_count | int | 浏览量 |
| created_at | datetime | 发布时间 |

---

#### POST /api/v1/ent/enterprise/claim（认领企业）
**权限**: 已认证

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| enterprise_id | int | Y | 企业ID |
| applicant_position | string | Y | 申请人职务 |
| legal_representative | string | Y | 法人姓名 |
| business_license | file | Y | 营业执照图片 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| audit_id | int | 审核记录ID |
| status | string | PENDING |
| message | string | 提示信息 |

---

#### POST /api/v1/ent/enterprise/create（创建企业）
**权限**: 已认证

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | Y | 企业全称 |
| credit_code | string | Y | 统一社会信用代码，18位 |
| legal_representative | string | Y | 法人姓名 |
| industry_id | int | Y | 所属行业ID |
| category_id | int | N | 主营业务品类ID |
| region_id | int | Y | 所在地区ID |
| description | string | Y | 企业简介，≥50字 |
| logo_url | file | N | Logo图片 |
| business_license | file | Y | 营业执照图片 |
| applicant_position | string | Y | 申请人职务 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| enterprise_id | int | 企业ID |
| audit_id | int | 审核记录ID |
| status | string | PENDING |
| message | string | 提示信息 |

---

#### GET /api/v1/ent/enterprise/my（我的企业）
**权限**: 已认证

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 企业ID |
| name | string | 企业名称 |
| auth_status | string | 认证状态 |
| role_code | string | 当前用户在企业的角色 |

---

#### PUT /api/v1/ent/enterprise/{id}（更新企业信息）
**权限**: 企业管理员

**请求字段**（仅可修改以下字段）:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| logo_url | file | N | Logo图片 |
| category_id | int | N | 主营业务品类 |
| region_id | int | N | 所在地区 |
| tags | array | N | 标签 |
| description | string | N | 企业简介 |

**不可修改字段**: name, credit_code, legal_representative, industry_id（需联系平台运营）

---

#### GET /api/v1/ent/industry（行业分类列表）
**权限**: 公开

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 行业ID |
| name | string | 行业名称 |
| sort_order | int | 排序 |

---

#### GET /api/v1/ent/category（业务品类列表）
**权限**: 公开

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| industry_id | int | N | 行业ID（筛选） |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 品类ID |
| name | string | 品类名称 |
| industry_id | int | 所属行业ID |
| sort_order | int | 排序 |

---

#### GET /api/v1/ent/region（行政区划列表）
**权限**: 公开

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parent_id | int | N | 父级ID，省份为0 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 地区ID |
| name | string | 地区名称 |
| parent_id | int | 父级ID |

---

### 3.5 商机相关接口

#### GET /api/v1/opp/opportunity（商机列表）
**权限**: 公开

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码，默认1 |
| page_size | int | N | 每页条数，默认20 |
| type | string | N | BUY/SUPPLY/空（全部） |
| industry_id | int | N | 行业ID |
| category_id | int | N | 品类ID |
| region_id | int | N | 地区ID |
| tags | string | N | 标签 |
| keyword | string | N | 关键词 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总数 |
| items | array | 商机列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 商机ID |
| type | string | BUY/SUPPLY |
| title | string | 商机标题 |
| enterprise_id | int | 企业ID |
| enterprise_name | string | 企业名称 |
| industry_name | string | 行业名称 |
| category_name | string | 品类名称 |
| region_name | string | 地区名称 |
| tags | array | 标签列表 |
| view_count | int | 浏览量 |
| created_at | datetime | 发布时间 |

---

#### GET /api/v1/opp/opportunity/{id}（商机详情）
**权限**: 已认证

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 商机ID |
| type | string | BUY/SUPPLY |
| title | string | 商机标题 |
| detail | string | 详细描述 |
| enterprise_id | int | 企业ID |
| enterprise_name | string | 企业名称 |
| publisher_id | int | 发布人ID |
| publisher_name | string | 发布人姓名 |
| industry_id | int | 行业ID |
| industry_name | string | 行业名称 |
| category_id | int | 品类ID |
| category_name | string | 品类名称 |
| region_id | int | 地区ID |
| region_name | string | 地区名称 |
| tags | array | 标签列表 |
| status | string | ACTIVE/OFFLINE |
| view_count | int | 浏览量 |
| contact_name | string | 联系人（已认证可见） |
| contact_phone | string | 联系电话（已认证可见） |
| contact_wechat | string | 微信（已认证可见） |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

---

#### POST /api/v1/opp/opportunity（发布商机）
**权限**: 已认证（需绑定认证企业）

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | Y | BUY/SUPPLY |
| title | string | Y | 商机标题，≤200字 |
| industry_id | int | Y | 行业ID |
| category_id | int | Y | 品类ID |
| region_id | int | Y | 地区ID |
| detail | string | Y | 详细描述 |
| tags | array | N | 标签 |
| contact_name | string | Y | 联系人 |
| contact_phone | string | Y | 联系电话 |
| contact_wechat | string | N | 微信 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 商机ID |
| status | string | ACTIVE |

---

#### PUT /api/v1/opp/opportunity/{id}（更新商机）
**权限**: 发布人或企业管理员

**请求字段**: 同发布，可选填

**响应字段**: 同上

---

#### DELETE /api/v1/opp/opportunity/{id}（删除商机）
**权限**: 发布人或企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 删除成功 |

---

#### PUT /api/v1/opp/opportunity/{id}/offline（下架商机）
**权限**: 企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 商机ID |
| status | string | OFFLINE |

---

#### POST /api/v1/opp/opportunity/{id}/contact（获取联系方式）
**权限**: 已认证（需绑定认证企业）

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| contact_name | string | 联系人 |
| contact_phone | string | 联系电话 |
| contact_wechat | string | 微信 |

---

### 3.6 动态相关接口

#### GET /api/v1/feed/feed（动态列表）
**权限**: 公开

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码，默认1 |
| page_size | int | N | 每页条数，默认20 |
| keyword | string | N | 关键词 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总数 |
| items | array | 动态列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 动态ID |
| content | string | 动态内容 |
| images | array | 图片URL列表 |
| publisher_id | int | 发布人ID |
| publisher_name | string | 发布人姓名 |
| enterprise_id | int | 企业ID |
| enterprise_name | string | 企业名称 |
| created_at | datetime | 发布时间 |

---

#### GET /api/v1/feed/feed/{id}（动态详情）
**权限**: 已认证

**响应字段**: 同动态列表元素，增加 updated_at

---

#### POST /api/v1/feed/feed（发布动态）
**权限**: 已认证（需绑定认证企业）

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | Y | 动态内容，≤1000字 |
| images | array | N | 图片URL列表，最多9张 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 动态ID |
| status | string | ACTIVE |

---

#### DELETE /api/v1/feed/feed/{id}（删除动态）
**权限**: 发布人或企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 删除成功 |

---

#### PUT /api/v1/feed/feed/{id}/offline（下架动态）
**权限**: 平台管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 动态ID |
| status | string | OFFLINE |

---

### 3.7 企业端管理接口

#### GET /api/v1/ent-admin/employees（员工列表）
**权限**: 企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 员工列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| real_name | string | 真实姓名 |
| phone | string | 手机号 |
| role_code | string | enterprise_admin/employee |
| is_active | bool | 是否启用 |
| created_at | datetime | 加入时间 |

---

#### POST /api/v1/ent-admin/employees（新增员工）
**权限**: 企业管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号 |
| real_name | string | Y | 真实姓名 |
| role_code | string | Y | enterprise_admin/employee |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| message | string | 成功提示 |

---

#### PUT /api/v1/ent-admin/employees/{id}（更新员工）
**权限**: 企业管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| real_name | string | N | 真实姓名 |
| role_code | string | N | enterprise_admin/employee |

---

#### DELETE /api/v1/ent-admin/employees/{id}（移除员工）
**权限**: 企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 移除成功 |

---

#### POST /api/v1/ent-admin/employees/{id}/reset-password（重置密码）
**权限**: 企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| temp_password | string | 临时密码（手机号后6位） |

---

#### POST /api/v1/ent-admin/employees/{id}/toggle-status（启用/停用）
**权限**: 企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| is_active | bool | 当前状态 |

---

#### GET /api/v1/ent-admin/my-opportunities（本企业商机列表）
**权限**: 企业管理员/员工

**响应字段**: 同商机列表

---

### 3.8 平台端管理接口

#### GET /api/v1/plat-admin/dashboard/stats（统计指标）
**权限**: 平台运营

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| enterprise_count | int | 入驻企业数 |
| opportunity_count | int | 累计商机数 |
| deal_count | int | 成功撮合数 |
| active_user_count | int | 活跃校友数 |
| pending_audit_count | int | 待审核数 |

---

#### GET /api/v1/plat-admin/audit/enterprise（企业审核列表）
**权限**: 平台运营

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码 |
| status | string | N | PENDING/VERIFIED/REJECTED |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总数 |
| items | array | 审核列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 审核记录ID |
| enterprise_id | int | 企业ID |
| enterprise_name | string | 企业名称 |
| credit_code | string | 信用代码 |
| applicant_name | string | 申请人姓名 |
| applicant_position | string | 申请人职务 |
| legal_representative | string | 法人姓名 |
| business_license_url | string | 营业执照URL |
| status | string | 审核状态 |
| created_at | datetime | 申请时间 |

---

#### POST /api/v1/plat-admin/audit/enterprise/{id}/approve（审核通过）
**权限**: 平台运营

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 审核记录ID |
| status | string | VERIFIED |
| enterprise_id | int | 企业ID |

---

#### POST /api/v1/plat-admin/audit/enterprise/{id}/reject（审核驳回）
**权限**: 平台运营

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | Y | 驳回原因 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 审核记录ID |
| status | string | REJECTED |

---

#### GET /api/v1/plat-admin/tenant/enterprise（企业列表）
**权限**: 超级管理员

**响应字段**: 同企业列表

---

#### PUT /api/v1/plat-admin/tenant/enterprise/{id}/toggle-status（启用/停用企业）
**权限**: 超级管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 企业ID |
| is_active | bool | 当前状态 |

---

#### GET /api/v1/plat-admin/content/opportunity（商机列表）
**权限**: 平台运营

**响应字段**: 同商机列表

---

#### PUT /api/v1/plat-admin/content/opportunity/{id}/offline（强制下架）
**权限**: 平台运营

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | N | 下架原因 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 商机ID |
| status | string | OFFLINE |

---

#### GET /api/v1/plat-admin/content/feed（动态列表）
**权限**: 平台运营

**响应字段**: 同动态列表

---

#### PUT /api/v1/plat-admin/content/feed/{id}/offline（强制下架）
**权限**: 平台运营

**响应字段**: 同上

---

#### GET /api/v1/plat-admin/master-data（字典列表）
**权限**: 平台运营

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | N | industry/category/tag/region |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 字典项列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 字典ID |
| category | string | 类别 |
| name | string | 名称 |
| code | string | 编码 |
| parent_id | int | 父级ID |
| sort_order | int | 排序 |
| is_active | bool | 是否启用 |

---

#### POST /api/v1/plat-admin/master-data（新增字典项）
**权限**: 超级管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | Y | 类别 |
| name | string | Y | 名称 |
| code | string | N | 编码 |
| parent_id | int | N | 父级ID |
| sort_order | int | N | 排序，默认0 |

**响应字段**: 新增的字典项

---

#### PUT /api/v1/plat-admin/master-data/{id}（更新字典项）
**权限**: 超级管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | N | 名称 |
| code | string | N | 编码 |
| sort_order | int | N | 排序 |

**响应字段**: 更新后的字典项

---

#### PUT /api/v1/plat-admin/master-data/{id}/toggle-status（启用/禁用）
**权限**: 超级管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 字典ID |
| is_active | bool | 当前状态 |

---

#### GET /api/v1/plat-admin/role（角色列表）
**权限**: 超级管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 角色列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 角色ID |
| name | string | 角色名称 |
| permissions | array | 权限列表 |

---

#### PUT /api/v1/plat-admin/role/{id}/permissions（更新角色权限）
**权限**: 超级管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| permissions | array | Y | 权限码列表 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 角色ID |
| permissions | array | 更新后的权限列表 |

---

### 3.9 搜索接口

#### GET /api/v1/search/all（统一搜索）
**权限**: 已认证

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | Y | 关键词 |
| type | string | N | opportunity/enterprise/feed/空（全部） |
| page | int | N | 页码 |
| page_size | int | N | 每页条数 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| opportunity | object | 商机搜索结果 `{ total, items }` |
| enterprise | object | 企业搜索结果 `{ total, items }` |
| feed | object | 动态搜索结果 `{ total, items }` |

---

### 3.10 API 汇总

| 模块标识 | 接口数 | 路径前缀 |
|----------|--------|----------|
| auth_app | 6 | /api/v1/auth/ |
| public | 1 | /api/v1/public/ |
| ent | 9 | /api/v1/ent/ |
| opp | 7 | /api/v1/opp/ |
| feed | 5 | /api/v1/feed/ |
| ent-admin | 7 | /api/v1/ent-admin/ |
| plat-admin | 14 | /api/v1/plat-admin/ |
| search | 1 | /api/v1/search/ |
| **合计** | **50** | - |

---

## 4. 核心功能设计

### 4.1 认证流程设计

**短信验证码登录流程：**
```
1. 用户输入手机号，点击"获取验证码"
2. 后端校验：同一手机号每天最多生成10次
3. 生成6位数字验证码，写入 auth_sms_code 表（TTL: 5分钟）
4. 调用短信服务商 API 发送验证码
5. 用户输入验证码，前端提交登录请求
6. 后端验证：code匹配 + 未使用 + 未过期
7. 查询/创建 Django User，返回 JWT Token
```

**Token 机制（SimpleJWT）：**
- access_token 有效期：2小时
- refresh_token 有效期：7天
- 前端自动在 token 过期前调用刷新接口

### 4.2 企业认领/创建流程

```
用户提交认领/创建申请
         │
         ▼
  创建 plat_audit_record，status=PENDING
  认领：锁定企业信息（name, credit_code）
  创建：写入 ent_enterprise 草稿
         │
         ▼
  平台运营审核
         │
    ┌────┴────┐
    ▼         ▼
  通过       驳回
    │         │
    ▼         ▼
 enterprise.auth_status=VERIFIED  enterprise.auth_status=REJECTED
 admin_user = 申请人
 ent_user_profile.role_code = 'enterprise_admin'
 ent_user_profile.enterprise_id = 企业ID
         │
         ▼
  发送 msg_message 通知申请人
```

### 4.3 联系方式获取流程（商机撮合）

```
意向方点击"获取联系方式"
         │
         ▼
  校验权限：已认证 + 已绑定认证企业
         │
         ▼
  记录 opp_contact_log（撮合日志）
         │
         ▼
  发送 msg_message 通知发布方
  "【XX企业】查看了您的商机《XXX》，请及时关注"
         │
         ▼
  返回发布方联系信息
  （contact_name, contact_phone, contact_wechat）
```

### 4.4 权限控制设计

**混合权限体系：**

| 权限维度 | 实现 | 说明 |
|----------|------|------|
| 平台角色 | auth.Group | super_admin, platform_operator |
| 企业角色 | ent_user_profile.role_code | enterprise_admin, employee, guest |
| 企业归属 | ent_user_profile.enterprise_id | 数据隔离依据 |

**数据隔离（QuerySet 过滤）：**

```python
class OpportunityQuerySet(models.QuerySet):
    def for_enterprise(self, user):
        """仅返回用户所属企业的商机"""
        profile = user.ent_user_profile
        if not profile or not profile.enterprise_id:
            return self.none()
        return self.filter(enterprise_id=profile.enterprise_id)
```

### 4.5 操作日志设计

**业务操作日志（使用 Django Signals）：**

| 操作 | 触发时机 | 记录内容 |
|------|----------|----------|
| 企业审核通过 | audit approve | enterprise_id, auditor_id, status变更 |
| 企业审核驳回 | audit reject | enterprise_id, auditor_id, reason |
| 商机强制下架 | platform offline | opportunity_id, reason, operator_id |
| 动态强制下架 | platform offline | feed_id, reason, operator_id |

### 4.6 统计指标说明

| 指标 | 计算方式 |
|------|----------|
| 累计入驻企业 | `COUNT(ent_enterprise WHERE auth_status='VERIFIED')` |
| 累计发布商机 | `COUNT(opp_opportunity)` |
| 成功撮合对接 | `COUNT(opp_contact_log)` |
| 活跃校友人数 | `COUNT(DISTINCT auth_user WHERE last_login >= N天内)` |

---

## 5. 前端设计

### 5.1 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue3 | 3.4+ | 组合式 API |
| Element Plus | 2.5+ | UI 组件库 |
| Pinia | 2.1+ | 状态管理 |
| Axios | 1.6+ | HTTP 客户端 |
| Vue Router | 4.2+ | 路由管理 |

### 5.2 项目目录结构

```
frontend/
├── src/
│   ├── api/                 # API 请求封装
│   │   ├── request.ts       # Axios 封装
│   │   ├── auth.ts         # 认证接口
│   │   ├── enterprise.ts   # 企业接口
│   │   ├── opportunity.ts  # 商机接口
│   │   ├── feed.ts        # 动态接口
│   │   └── admin.ts       # 管理端接口
│   │
│   ├── views/              # 页面
│   │   ├── Home/           # 前台
│   │   │   ├── index.vue   # 首页
│   │   │   ├── promotion.vue  # 宣传页
│   │   │   ├── enterprise.vue   # 企业名录
│   │   │   ├── opportunity.vue  # 商机广场
│   │   │   ├── feed.vue    # 校友圈
│   │   │   └── search.vue  # 搜索结果
│   │   │
│   │   ├── Auth/          # 认证
│   │   │   ├── login.vue   # 登录页
│   │   │   └── register.vue  # 注册页
│   │   │
│   │   ├── EnterpriseAdmin/ # 企业端
│   │   │   ├── index.vue   # 工作台
│   │   │   ├── enterprise-info.vue  # 企业信息维护
│   │   │   ├── employee.vue        # 员工管理
│   │   │   └── my-opportunity.vue   # 我的商机
│   │   │
│   │   └── PlatformAdmin/  # 平台端
│   │       ├── index.vue   # 工作台
│   │       ├── dashboard.vue   # 数据大盘
│   │       ├── audit.vue   # 企业审核
│   │       ├── tenant.vue  # 企业管理
│   │       ├── opportunity-manage.vue  # 商机管理
│   │       ├── feed-manage.vue      # 动态管理
│   │       ├── master-data.vue      # 基础数据
│   │       ├── rbac.vue   # 权限管理
│   │       └── settings.vue # 系统设置
│   │
│   ├── components/         # 公共组件
│   │   ├── Header.vue     # 顶部导航
│   │   ├── Footer.vue     # 底部
│   │   ├── SearchBar.vue   # 搜索框
│   │   ├── EnterpriseCard.vue  # 企业卡片
│   │   ├── OpportunityCard.vue # 商机卡片
│   │   ├── FeedCard.vue   # 动态卡片
│   │   └── ModalForm.vue  # 弹窗表单
│   │
│   ├── composables/       # 组合式函数
│   │   ├── useAuth.ts    # 认证状态
│   │   ├── useEnterprise.ts  # 企业信息
│   │   └── usePermission.ts   # 权限判断
│   │
│   ├── store/            # Pinia 状态
│   │   ├── user.ts       # 用户状态
│   │   └── app.ts        # 应用状态
│   │
│   ├── router/           # 路由配置
│   │   └── index.ts
│   │
│   ├── styles/           # 全局样式
│   │   ├── variables.scss # 样式变量
│   │   └── common.scss   # 公共样式
│   │
│   ├── App.vue
│   └── main.ts
│
├── package.json
├── vite.config.ts
└── index.html
```

### 5.3 路由设计

```typescript
const routes = [
  // 前台（无需认证）
  { path: '/', component: () => import('@/views/Home/index.vue') },
  { path: '/promotion', component: () => import('@/views/Home/promotion.vue') },
  { path: '/enterprise', component: () => import('@/views/Home/enterprise.vue') },
  { path: '/opportunity', component: () => import('@/views/Home/opportunity.vue') },
  { path: '/feed', component: () => import('@/views/Home/feed.vue') },
  { path: '/search', component: () => import('@/views/Home/search.vue') },

  // 认证
  { path: '/login', component: () => import('@/views/Auth/login.vue') },
  { path: '/register', component: () => import('@/views/Auth/register.vue') },

  // 企业端（需企业角色）
  {
    path: '/enterprise-admin',
    component: () => import('@/views/EnterpriseAdmin/index.vue'),
    meta: { requiresAuth: true, enterpriseRequired: true },
    children: [
      { path: 'info', component: () => import('@/views/EnterpriseAdmin/enterprise-info.vue') },
      { path: 'employee', component: () => import('@/views/EnterpriseAdmin/employee.vue') },
      { path: 'opportunity', component: () => import('@/views/EnterpriseAdmin/my-opportunity.vue') },
    ]
  },

  // 平台端（需平台角色）
  {
    path: '/platform-admin',
    component: () => import('@/views/PlatformAdmin/index.vue'),
    meta: { requiresAuth: true, platformRequired: true },
    children: [
      { path: 'dashboard', component: () => import('@/views/PlatformAdmin/dashboard.vue') },
      { path: 'audit', component: () => import('@/views/PlatformAdmin/audit.vue') },
      { path: 'tenant', component: () => import('@/views/PlatformAdmin/tenant.vue') },
      { path: 'opportunity-manage', component: () => import('@/views/PlatformAdmin/opportunity-manage.vue') },
      { path: 'feed-manage', component: () => import('@/views/PlatformAdmin/feed-manage.vue') },
      { path: 'master-data', component: () => import('@/views/PlatformAdmin/master-data.vue') },
      { path: 'rbac', component: () => import('@/views/PlatformAdmin/rbac.vue') },
      { path: 'settings', component: () => import('@/views/PlatformAdmin/settings.vue') },
    ]
  }
]
```

### 5.4 权限判断 composable

```typescript
// composables/usePermission.ts
export function usePermission() {
  const userStore = useUserStore()

  const isAuthenticated = computed(() => !!userStore.token)

  const isPlatformRole = computed(() =>
    ['super_admin', 'platform_operator'].includes(userStore.roleCode)
  )

  const isEnterpriseRole = computed(() =>
    ['enterprise_admin', 'employee'].includes(userStore.roleCode)
  )

  const canPublish = computed(() => {
    if (!userStore.profile?.enterprise_id) return false
    return userStore.profile?.enterprise?.auth_status === 'VERIFIED'
  })

  const hasRole = (roleCodes: string[]) => {
    return roleCodes.includes(userStore.roleCode)
  }

  return {
    isAuthenticated,
    isPlatformRole,
    isEnterpriseRole,
    canPublish,
    hasRole
  }
}
```

### 5.5 功能页面设计

#### 5.5.1 首页（/）

**页面功能**：全局导航、数据展示、快捷入口、智能推荐

| 功能      | 说明                                        |
| ------- | ----------------------------------------- |
| 热门标签点击  | 点击跳转 `/opportunity?tag=标签名`，商机广场自动应用该标签筛选 |
| 快捷发布按钮  | 未登录→跳转登录页；未绑定企业→提示认领/创建企业；已认证→弹窗发布        |
| 新入驻企业点击 | 跳转企业详情抽屉                                  |
| 最新动态点击  | 跳转校友圈详情                                   |

#### 5.5.2 企业名录页（/enterprise）

**页面功能**：企业列表查询、筛选、企业详情

| 搜索字段 | 类型 |
|----------|------|
| keyword | string |
| industry_id | select |
| category_id | select |
| region_id | cascader |
| tags | checkbox（热门标签筛选） |

**交互**：
- 点击热门标签 → 本页应用该标签筛选
- 点击企业卡片 → 右侧抽屉展示企业详情（含该企业商机 Tab）

#### 5.5.3 商机广场页（/opportunity）

**页面功能**：商机列表查询、筛选、发布、获取联系方式

| 搜索字段 | 类型 |
|----------|------|
| type | radio（全部/我要买/我能供） |
| industry_id | select |
| category_id | select |
| region_id | cascader |
| **tags** | **checkbox** |
| keyword | string |

**交互**：
- 点击"获取联系方式" → 需登录 + 已绑定认证企业
- 点击商机卡片 → 跳转商机详情

#### 5.5.4 校友圈页（/feed）

**页面功能**：动态列表、发布动态

| 搜索字段 | 类型 |
|----------|------|
| keyword | string |

**交互**：
- 点击发布 → 弹窗输入内容+上传图片（最多9张）
- 点击动态卡片 → 展开详情

#### 5.5.5 登录页（/login）

**页面功能**：短信登录、密码登录

| 字段 | 类型 | 说明 |
|------|------|------|
| phone | input | 手机号，11位 |
| code | input | 验证码，6位 + 获取验证码按钮（60秒倒计时） |
| password | input | 密码登录时显示 |

#### 5.5.5b 注册页（/register）

**页面功能**：用户注册（扫码后的落地页）

| 字段 | 类型 | 说明 |
|------|------|------|
| phone | input | 手机号，11位 |
| code | input | 验证码，6位 + 获取验证码按钮（60秒倒计时） |
| password | input | 设置密码，8-20位 |
| confirmPassword | input | 确认密码 |

**交互**：注册成功后跳转首页

#### 5.5.5c 宣传页（/promotion）

**页面功能**：统一宣传页 + 二维码入口

| 元素 | 说明 |
|------|------|
| 品牌展示 | Logo、品牌名称、口号 |
| 平台介绍 | 校友供应链撮合平台定位 |
| 统计数据 | 入驻企业数、累计商机、成功撮合（调用 /api/v1/public/stats） |
| 二维码 | 扫码注册入口，二维码内容为 `/register` 页面 URL |

**交互**：扫码后直接进入注册页面

#### 5.5.6 企业端 - 员工管理页

**页面功能**：员工列表、新增、编辑、停用、重置密码、移除

| 操作 | 说明 |
|------|------|
| 编辑 | 修改员工姓名、角色 |
| 重置密码 | 重置为手机号后6位 |
| 停用/启用 | 切换账号状态 |
| **移除** | 解除员工与企业绑定关系（账号保留） |

#### 5.5.7 平台端 - 企业审核页

**页面功能**：待审核企业列表、审核通过/驳回

| 操作 | 说明 |
|------|------|
| 审核通过 | 更新企业状态为 VERIFIED，升级用户角色 |
| 审核驳回 | 填写驳回原因，更新企业状态为 REJECTED |

**审核弹窗展示**：
- 企业基本信息（名称、信用代码、行业、地区）
- 申请人职务
- 证明材料预览

### 5.6 API 请求封装

```typescript
// api/request.ts
import axios, { AxiosError } from 'axios'
import { useUserStore } from '@/store/user'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
})

request.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.accessToken) {
    config.headers.Authorization = `Bearer ${userStore.accessToken}`
  }
  return config
})

request.interceptors.response.use(
  response => response.data,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      try {
        await userStore.refreshToken()
        return request(error.config!)
      } catch {
        userStore.logout()
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

export default request
```

---

## 6. 部署设计

### 6.1 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                            │
│                                                              │
│  ┌──────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │  nginx  │───▶│    backend    │───▶│     MySQL     │   │
│  │ :80/:443│    │  (Django)     │    │    :3306      │   │
│  └──────────┘    │   :8000       │    └───────────────┘   │
│       │         └───────────────┘                          │
│       │                                                    │
│       │         ┌───────────────┐                         │
│       └────────▶│   frontend    │                         │
│                 │  (Vue3 dist)  │                         │
│                 │    :80        │                         │
│                 └───────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Docker Compose 配置

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: xlt
      MYSQL_USER: xlt_user
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=mysql://xlt_user:${DB_PASSWORD}@db:3306/xlt?charset=utf8mb4
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - DEBUG=${DEBUG:-False}
    depends_on:
      - db
    ports:
      - "8000:8000"
    volumes:
      - ../backend:/app

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    depends_on:
      - backend
    ports:
      - "80:80"

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ../frontend/dist:/usr/share/nginx/html
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  mysql_data:
```

### 6.3 后端 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### 6.4 前端 Dockerfile

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 6.5 Nginx 配置

```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        proxy_pass http://backend;
    }
}
```

### 6.6 环境变量配置

```bash
# .env
SECRET_KEY=your-secret-key-here-must-be-at-least-50-characters
JWT_SECRET=your-jwt-secret-here
DB_PASSWORD=your-db-password-here
DB_ROOT_PASSWORD=your-root-password-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6.7 部署命令

```bash
# 1. 克隆代码
git clone <repository>
cd XiaoLianTong

# 2. 配置环境变量
cp .env.example .env

# 3. 构建并启动
docker compose -f docker/docker-compose.yml up -d --build

# 4. 执行数据库迁移
docker compose exec backend python manage.py migrate

# 5. 创建超级管理员
docker compose exec backend python manage.py createsuperuser

# 6. 健康检查
curl -f http://localhost/health

# 7. 查看日志
docker compose logs -f
```

---

## 7. 附录

### A. 技术选型对比

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| Django + DRF | 功能完善生态好、内置 Admin 站点、用户系统完善 | 重量级、同步框架 | **选用** |
| FastAPI | 高性能、自动文档、轻量 | 无内置用户系统 | 未选用 |

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| Vue2+Element | 稳定 | Options API 已过时 | 未选用 |
| Vue3+Element Plus | 组合式API、性能好 | 需Vue3学习成本 | **选用** |

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| PostgreSQL | 功能丰富 | 需单独安装 | 未选用 |
| MySQL | 轻量、托管方便 | 功能相对较少 | **选用（用户要求）** |

---

*文档结束*
