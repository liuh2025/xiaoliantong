---
status: 已批准
---

# 技术设计文档

## XiaoLianTong (校链通)

| 文档信息  | 内容                                                   |
| ----- | ---------------------------------------------------- |
| 项目名称  | XiaoLianTong (校链通)                                   |
| 文档版本  | v1.23                                                |
| 创建日期  | 2026-04-02                                           |
| 关联PRD | [PRD-XiaoLianTong-v1.0.md](PRD-XiaoLianTong-v1.0.md) |
| 文档状态  | 已批准                                                  |
| 方案选择  | 方案一（单体架构）+ Django + DRF + MySQL                      |

---

## 修订历史

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| v1.0 | 2026-04-02 | ARCH | 初始版本 |
| v1.1 | 2026-04-03 | ARCH | 对齐 PRD v1.1：新增宣传页、更新企业认证必填字段 |
| v1.2 | 2026-04-05 | ARCH | 完善RBAC设计：统一auth.Group体系、两层权限体系（导航块可见性+功能权限矩阵）、简化usePermission、DRF Permission Class、数据隔离固化、新增POST /role API |
| v1.3 | 2026-04-05 | ARCH | 完善认证体系：拆分sms/send接口、新增token/verify、更新auth_sms_code表结构（增加type字段）、补充ROTATE_REFRESH_TOKENS机制与logout黑名单说明、更新前端Axios拦截器示例、新增首页推荐/企业/动态接口 |
| v1.4 | 2026-04-05 | ARCH | 完善接口清单：新增登录注册密码API列表（3.2节前）、新增首页API列表（3.4节前）、补充纯JS密码显示交互说明 |
| v1.5 | 2026-04-05 | ARCH | 完善各页面API对照表：企业名录API列表（3.5前）、商机广场API列表（3.6前）、校友圈API列表（3.7前）、企业工作台API列表（3.8前）、管理后台API列表（3.9前）、搜索页API列表（3.10前）、消息通知API列表（3.11前） |
| v1.6 | 2026-04-05 | ARCH | 新增消息接口：GET /msg/notifications/recent（铃铛下拉）、PUT /msg/notifications/{id}/read（单条已读）；登录页remember_me参数；更新首页数据加载流程 |
| v1.7 | 2026-04-05 | ARCH | 更新企业名录API对照表：按前端函数格式重写，含筛选搜索、认领创建、企业详情抽屉、联系企业等完整流程 |
| v1.8 | 2026-04-05 | ARCH | 更新商机广场API对照表：侧边栏改用级联选择器（行业分类、省份城市）+ 多选筛选 + 防抖实时搜索（300ms）+ 已选条件摘要 |
| v1.9 | 2026-04-05 | ARCH | 更新校友圈API对照表：按前端函数格式重写，含动态列表、发布动态、上传图片等完整流程；移除点赞评论分享 |
| v1.10 | 2026-04-06 | ARCH | 更新企业工作台API对照表：按前端函数格式重写，含企业信息维护、员工管理（增删改、密码重置）、商机管理（下架/重新发布）等完整流程 |
| v1.11 | 2026-04-06 | ARCH | 新增企业数据权限过滤逻辑说明：JWT认证流程、自动关联企业、数据隔离保证 |
| v1.12 | 2026-04-06 | ARCH | 修复员工管理API：新增移除员工操作、补全新增员工前提说明、修正重置密码响应说明（短信通知） |
| v1.13 | 2026-04-06 | ARCH | 新增员工账号状态（is_active）校验说明：停用状态需校验的接口清单 |
| v1.14 | 2026-04-06 | ARCH | 拆分停用/解绑功能：停用(is_active)禁止登录，解绑(unbind)恢复游客身份；原DELETE接口改为POST /unbind |
| v1.15 | 2026-04-06 | ARCH | 新增编辑商机功能：内嵌编辑表单，PUT接口，type类型不可修改；补全下架/重新发布API文档 |
| v1.16 | 2026-04-06 | ARCH | 重写企业名录API列表：按前端函数格式对齐原型，含二级行业联动、筛选防抖、认领/创建/详情抽屉等完整流程 |
| v1.17 | 2026-04-06 | ARCH | 更新企业名录API列表结构：Header区域、侧边栏筛选（含级联选择器+多选+防抖）、企业列表+分页、详情悬浮窗、通用组件 |
| v1.18 | 2026-04-06 | ARCH | 企业列表API新增credit_code字段（认领时展示确认）；补全认领/创建企业的提交后落库逻辑及审核通过/驳回的后续操作 |
| v1.19 | 2026-04-06 | ARCH | 创建企业弹窗API补全：加载行业（联动二级+品类）、省份（联动城市）、标签推荐；原型同步更新 |
| v1.20 | 2026-04-06 | ARCH | 更新管理后台API列表：按前端函数格式重写，含Header导航栏、数据大盘、企业审核（含Tab切换）、企业租户管理（含成员管理）、商机内容管理（含type筛选）、动态内容管理、基础数据字典（含树形结构）、账号权限（新增角色暂不支持）、系统设置；移除重复的3.9详细定义章节 |
| v1.21 | 2026-04-06 | ARCH | 恢复管理后台3.9详细接口定义；3.8.x改为摘要表格（含#、页面功能、前端函数、API、方法、请求参数、说明），与其他章节格式对齐 |
| v1.22 | 2026-04-06 | ARCH | 管理后台Header导航栏通知功能对齐首页：使用相同的通知API（/msg/notifications/recent、/msg/notifications/read-all、/msg/notifications）；原型dashboard.html添加通知下拉组件 |
| v1.23 | 2026-04-06 | ARCH | 完善DESN与原型对齐：企业租户管理新增启用/禁用+成员管理API、商机/动态列表响应字段详细定义、字典项parent_id判断逻辑、账号权限功能权限矩阵、API汇总更新(93个)、4.4权限控制设计更新、5.5功能页面设计改为原型引用 |

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
| industry_id | BIGINT | Y | 一级行业ID |
| sub_industry_id | BIGINT | Y | 二级行业ID（末级） |
| category_id | BIGINT | N | 主营业务品类 |
| province_id | BIGINT | Y | 省份ID |
| region_id | BIGINT | Y | 市ID |
| tags | JSON | N | 业务标签 |
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
| position       | VARCHAR(50)        | N   | 职位/职级（如 CEO、总监、员工），用于动态展示              |
| contact_phone  | VARCHAR(11)        | N   | 联系电话                                   |
| contact_wechat | VARCHAR(50)        | N   | 微信                                     |
| created_at     | DATETIME           | Y   | 创建时间                                   |
| updated_at     | DATETIME           | Y   | 更新时间                                   |

#### opp_opportunity（商机表）

| 字段              | 类型                 | 必填  | 说明             |
| --------------- | ------------------ | --- | -------------- |
| id              | BIGINT             | Y   | 主键             |
| type            | VARCHAR(10)        | Y   | BUY/SUPPLY     |
| title           | VARCHAR(200)       | Y   | 商机标题           |
| enterprise      | FK(ent_enterprise) | Y   | 发布企业           |
| publisher       | FK(auth.User)      | Y   | 发布人            |
| industry_id     | BIGINT             | Y   | 一级行业ID         |
| sub_industry_id | BIGINT             | Y   | 二级行业ID（末级）     |
| category_id     | BIGINT             | Y   | 业务品类           |
| province_id     | BIGINT             | Y   | 省份ID           |
| region_id       | BIGINT             | Y   | 市ID            |
| tags            | JSON               | N   | 业务标签           |
| detail          | TEXT               | Y   | 详细描述           |
| status          | VARCHAR(20)        | Y   | ACTIVE/OFFLINE |
| view_count      | INT                | Y   | 浏览量            |
| contact_name    | VARCHAR(50)        | N   | 联系人            |
| contact_phone   | VARCHAR(11)        | N   | 联系电话           |
| contact_wechat  | VARCHAR(50)        | N   | 微信             |
| created_at      | DATETIME           | Y   | 创建时间           |
| updated_at      | DATETIME           | Y   | 更新时间           |

#### opp_contact_log（商机撮合日志表）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGINT | Y | 主键 |
| opportunity | FK(opp_opportunity) | Y | 涉及的商机 |
| getter_user | FK(auth.User) | Y | 获取方用户 |
| getter_enterprise | FK(ent_enterprise) | Y | 获取方企业 |
| status | VARCHAR(20) | Y | 状态：INITIATED/CONFIRMED/COMPLETED/CANCELLED，默认 COMPLETED |
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

| 字段                   | 类型                 | 必填  | 说明                        |
| -------------------- | ------------------ | --- | ------------------------- |
| id                   | BIGINT             | Y   | 主键                        |
| enterprise           | FK(ent_enterprise) | Y   | 申请企业                      |
| applicant            | FK(auth.User)      | Y   | 申请人                       |
| auditor              | FK(auth.User)      | N   | 审批人                       |
| status               | VARCHAR(20)        | Y   | PENDING/VERIFIED/REJECTED |
| applicant_position   | VARCHAR(50)        | Y   | 申请人职务                     |
| legal_representative | VARCHAR(100)       | Y   | 法人姓名                      |
| business_license     | VARCHAR(500)       | Y   | 营业执照URL                   |
| audit_reason         | TEXT               | N   | 驳回原因                      |
| created_at           | DATETIME           | Y   | 操作时间                      |

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

| 字段         | 类型          | 必填  | 说明                                                  |
| ---------- | ----------- | --- | --------------------------------------------------- |
| id         | BIGINT      | Y   | 主键                                                  |
| phone      | VARCHAR(11) | Y   | 手机号，索引                                              |
| code       | VARCHAR(6)  | Y   | 6位验证码                                               |
| type       | VARCHAR(20) | Y   | 验证码类型：login（登录）/ register（注册）/ password_reset（密码重置） |
| expire_at  | DATETIME    | Y   | 过期时间（创建时间+5分钟）                                      |
| used_at    | DATETIME    | N   | 使用时间，NULL表示未使用                                      |
| created_at | DATETIME    | Y   | 创建时间                                                |

**索引**：
- `idx_phone_type`：(phone, type) 联合索引
- `idx_expire_at`：过期时间索引（用于定时清理）

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

### 登录页面 API 列表

**页面**：登录页（login.html）

| #   | 页面功能    | 前端函数                      | API                           |  方法  | 请求参数                               | 说明                                  |
| --- | ------- | ------------------------- | ----------------------------- | :--: | ---------------------------------- | ----------------------------------- |
| 1   | 切换登录方式  | `switchTab(tab)`          | —                             |  —   | —                                  | 纯前端交互，切换sms/password两个tab           |
| 2   | 发送登录验证码 | `sendSms()`               | `/auth/sms/send`              | POST | `phone`, `type='login'`            | 需校验手机号11位                           |
| 3   | 验证码登录   | `handleLogin()`           | `/auth/sms/login`             | POST | `phone`, `code`, `remember_me`     | 校验6位验证码，`remember_me`读取"7天内免登录"勾选状态 |
| 4   | 密码登录    | `handleLogin()`           | `/auth/login/password`        | POST | `phone`, `password`, `remember_me` | `remember_me`读取"7天内免登录"勾选状态         |
| 5   | 显示/隐藏密码 | `togglePassword(inputId)` | —                             |  —   | —                                  | 纯JS，切换input type                    |
| 6   | 发送重置验证码 | `sendForgotSms()`         | `/auth/sms/send`              | POST | `phone`, `type='password_reset'`   | 需校验手机号11位                           |
| 7   | 验证重置验证码 | `verifyForgotCode()`      | `/auth/password/reset/verify` | POST | `phone`, `code`                    | Step1→Step2跳转条件                     |
| 8   | 重置密码    | `resetPassword()`         | `/auth/password/reset`        | POST | `phone`, `code`, `password`        | 需校验两次密码一致                           |
| 9   | 忘记密码弹窗  | `showForgotModal()`       | —                             |  —   | —                                  | 纯前端，重置step状态                        |
| 10  | 关闭弹窗    | `closeModal(id)`          | —                             |  —   | —                                  | 纯前端，点击遮罩或X按钮                        |
| 11  | 登录成功弹窗  | `handleLogin()`           | —                             |  —   | —                                  | mock阶段显示，成功后应跳转                     |
| 12  | 免登录记住   | `handleLogin()`             | —                             |  —   | —                                  | 勾选"7天内免登录"checkbox，handleLogin读取其状态传给API，`localStorage.setItem('refresh_token', token)`统一存储 |

**登录流程**：
```
用户 → 输入手机号 → sendSms() → POST /auth/sms/send(type=login)
                         → 输入验证码 → 勾选"7天内免登录"(可选)
                         → handleLogin() → POST /auth/sms/login(phone, code, remember_me)
                                                      → localStorage.setItem('refresh_token', token)
                                                      → GET /auth/me 获取用户信息
                                                      → 跳转首页

或：用户 → 输入手机号+密码 → 勾选"7天内免登录"(可选)
                         → handleLogin() → POST /auth/login/password(phone, password, remember_me)
                                            → localStorage.setItem('refresh_token', token)
                                            → GET /auth/me 获取用户信息
                                            → 跳转首页
```

**忘记密码流程**：
```
用户点击"忘记密码" → showForgotModal()显示弹窗
                  → 输入手机号+验证码 → sendForgotSms() → POST /auth/sms/send(type=password_reset)
                  → verifyForgotCode() → POST /auth/password/reset/verify 验证通过
                  → 输入新密码+确认密码 → resetPassword() → POST /auth/password/reset
                  → 关闭弹窗，显示重置成功弹窗 → 跳转登录页
```

**前端Token处理（需实现）**：
- access_token：存于memory（Pinia），请求头 `Authorization: Bearer {access_token}` 携带
- refresh_token：统一存于localStorage，由后端根据remember_me参数控制过期时间
  - `remember_me=true`：后端设置refresh_token有效期7天，localStorage持久化
  - `remember_me=false`：后端设置refresh_token为session过期，localStorage存储但浏览器关闭后后端验证失败
- Axios拦截器：401响应时自动用localStorage中的refresh_token刷新，旋转机制由后端SimpleJWT控制
- refresh失败（如token已失效）：清除localStorage，跳转登录页

**remember_me逻辑**：
```
登录请求 → POST /auth/sms/login 或 /auth/login/password
         → 携带 remember_me 参数（true/false）
         ↓
后端处理：根據 remember_me 设置 refresh_token 过期时间
         - remember_me=true：7天有效期
         - remember_me=false：session过期（浏览器关闭后后端拒绝刷新）
         ↓
前端存储：统一存于 localStorage.setItem('refresh_token', token)
         （不区分remember_me，因为token本身已携带有效期信息）
         ↓
后续刷新：Axios拦截器统一从localStorage取refresh_token
         → 后端验证token是否过期/有效
         → 过期则返回401，前端跳转登录页
```

---

### 注册页面 API 列表

**页面**：注册页（register.html）

| #   | 页面功能    | 前端函数                      | API              |  方法  | 请求参数                        | 说明                    |
| --- | ------- | ------------------------- | ---------------- | :--: | --------------------------- | --------------------- |
| 1   | 发送注册验证码 | `sendSms(btn)`            | `/auth/sms/send` | POST | `phone`, `type='register'`  | 需校验手机号11位，启动倒计时       |
| 2   | 用户注册    | `handleRegister(e)`       | `/auth/register` | POST | `phone`, `code`, `password` | 校验密码8-20位、确认密码一致、协议勾选 |
| 3   | 显示/隐藏密码 | `togglePassword(inputId)` | —                |  —   | —                           | 纯JS，切换input type      |
| 4   | 协议链接    | —                         | —                |  —   | —                           | 纯前端跳转                 |
| 5   | 跳转登录    | —                         | —                |  —   | —                           | 纯前端跳转login.html       |

**注册流程**：
```
用户 → 输入手机号 → sendSms() → POST /auth/sms/send(type=register)
                         → 输入验证码+密码+确认密码+协议 → handleRegister()
                         → POST /auth/register
                         → 自动登录（返回token）
                         → 跳转login.html
```

---

### 登出与Token管理

| #   | 功能      | API                  |  方法  | 请求参数            | 说明                                               |
| --- | ------- | -------------------- | :--: | --------------- | ------------------------------------------------ |
| 1   | 登出      | `/auth/logout`       | POST | `refresh_token` | 将refresh_token加入黑名单                              |
| 2   | 刷新Token | `/auth/refresh`      | POST | `refresh_token` | 旋转机制，ROTATE_REFRESH_TOKENS=True，新refresh_token返回 |
| 3   | 验证Token | `/auth/token/verify` | POST | `token`         | 验证access_token有效性                                |
| 4   | 当前用户信息  | `/auth/me`           | GET  | —               | 登录成功后获取用户信息                                      |

**Token旋转机制说明**：
- 用户登录成功，后端返回 access_token（2h） + refresh_token（7d）
- Axios拦截器自动监测401，在后台用refresh_token换取新access_token
- ROTATE_REFRESH_TOKENS=True 时，每次refresh会颁发新的refresh_token（旧的自动作废）
- logout时将当前refresh_token提交至黑名单，后续refresh无效

---

### 3.2 前端交互说明

#### 密码可见切换

**功能**：密码输入框旁提供切换按钮，点击可显示/隐藏密码。

**实现方式**：纯前端 JS 实现，无需 API。

**代码示例**：
```javascript
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    input.type = input.type === 'password' ? 'text' : 'password';
}
```

**UI 示例**：
```html
<div style="position:relative;">
    <input type="password" class="form-input" placeholder="请输入密码" id="password">
    <span class="password-toggle" onclick="togglePassword('password')">👁️</span>
</div>
```

**应用场景**：
- 登录页-密码登录
- 忘记密码弹窗-Step2 设置新密码
- 注册页-设置密码/确认密码

---

### 3.3 认证接口

#### POST /api/v1/auth/sms/send（发送验证码）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| type | string | Y | 验证码类型：login（登录）/ register（注册）/ password_reset（密码重置） |

**业务规则**：
- 同一手机号每天（自然日）最多发送次数：
  - login：10次
  - register：10次
  - password_reset：5次
- 验证码有效期 **5分钟**
- 验证码格式：6位数字
- 同一手机号5分钟内若有未使用验证码，自动作废后重新生成
- 不同 type 的验证码独立计数和校验

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 发送成功提示 |
| expires_in | int | 有效期（秒），固定300 |

**错误码**：
| code | 说明 |
|------|------|
| 400 | 手机号格式错误或 type 非法 |
| 429 | 发送次数超限 |

---

#### POST /api/v1/auth/sms/login（验证码登录）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| code | string | Y | 6位验证码 |
| remember_me | bool | N | 是否7天内免登录，true时refresh_token有效期7天，默认false（浏览器关闭过期） |

**响应字段**: 同密码登录（含 role_code 和 permissions）

---

#### POST /api/v1/auth/login/password（密码登录）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| password | string | Y | 密码 |
| remember_me | bool | N | 是否7天内免登录，true时refresh_token有效期7天，默认false（浏览器关闭过期） |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | JWT访问令牌 |
| refresh_token | string | JWT刷新令牌 |
| user_id | int | 用户ID |
| role_code | string | 角色码（super_admin/platform_operator/enterprise_admin/employee/guest） |
| permissions | array | 权限码列表（由后端根据 auth.Group 动态返回） | |

---

#### POST /api/v1/auth/register（用户注册）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| code | string | Y | 6位验证码 |
| password | string | Y | 密码，8-20位 |

**响应字段**: 同密码登录

---

#### POST /api/v1/auth/password/reset/send（发送密码重置验证码）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |

**业务规则**：
- 同一手机号每天（自然日）最多发送 **5次**
- 验证码有效期 **5分钟**
- 验证码格式：6位数字
- 仅对已注册用户有效，若手机号未注册返回成功（防恶意探测）

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 发送成功提示 |
| expires_in | int | 有效期（秒），固定300 |

**错误码**：
| code | 说明 |
|------|------|
| 400 | 手机号格式错误 |
| 429 | 发送次数超限 |

---

#### POST /api/v1/auth/password/reset/verify（验证重置验证码）
**权限**: 公开

**说明**：验证验证码是否有效（正确 + 未使用 + 未过期），不执行重置操作。用于忘记密码流程的"下一步"按钮。

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| code | string | Y | 6位验证码 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| valid | bool | 验证码是否有效 |

**错误响应**:
| code | 说明 |
|------|------|
| 400 | 验证码错误或已过期 |

---

#### POST /api/v1/auth/password/reset（重置密码）
**权限**: 公开

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号，11位 |
| code | string | Y | 6位验证码 |
| password | string | Y | 新密码，8-20位 |

**业务规则**：
- 验证码必须匹配且未使用、未过期
- 验证码使用后立即作废
- 密码不能与原密码相同

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 重置成功提示 |

**错误码**：
| code | 说明 |
|------|------|
| 400 | 验证码错误或已过期 |

---

#### POST /api/v1/auth/logout（登出）
**权限**: 已认证

**说明**：
- 前端：同时删除 access_token 和 refresh_token
- 后端：将当前 refresh_token 加入黑名单（SimpleJWT 黑名单机制），使其立即失效

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | Y | 当前刷新令牌（用于加入黑名单） |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 成功消息 |

---

#### POST /api/v1/auth/refresh（刷新Token）
**权限**: 公开（接受 refresh_token）

**说明**：
- SimpleJWT 内置接口
- 验证 refresh_token 有效性
- 采用 ROTATE_REFRESH_TOKENS 机制：每次刷新时生成新的 access_token 和新的 refresh_token，旧的 refresh_token 自动加入黑名单

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | Y | 刷新令牌 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | 新JWT访问令牌 |
| refresh_token | string | 新JWT刷新令牌（替换旧的） |

---

#### POST /api/v1/auth/token/verify（验证Token）
**权限**: 公开

**说明**：SimpleJWT 内置接口，验证 access_token 有效性（用于前端检查 token 是否过期）

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token | string | Y | access_token |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，200表示有效 |

**错误响应**:
| code | 说明 |
|------|------|
| 401 | token 无效或已过期 |

---

#### GET /api/v1/auth/me（获取当前用户信息）
**权限**: 已认证

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| phone | string | 手机号 |
| real_name | string | 真实姓名 |
| position | string | 职位/职级（无则null） |
| role_code | string | 角色码 |
| enterprise_id | int | 企业ID（无则null） |
| enterprise_name | string | 企业名称（无则null） |
| enterprise_status | string | 企业认证状态（无则null） |

---

### 首页 API 列表

**页面**：首页（index.html）

| #              | 页面功能      | 前端函数                                            | API                             |  方法  | 请求参数                                                                                                                                                              | 说明                                                                                                                  |
| -------------- | --------- | ----------------------------------------------- | ------------------------------- | :--: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Header 导航栏** |           |                                                 |                                 |      |                                                                                                                                                                   |                                                                                                                     |
| 1              | 搜索框       | `goToSearch()`                                  | —                               |  —   | —                                                                                                                                                                 | 纯前端跳转 `search.html?keyword=xxx`                                                                                     |
| 2              | 通知下拉（加载）  | `toggleNotificationDropdown()`                  | `/msg/notifications/recent`     | GET  | `limit`（默认3）                                                                                                                                                      | 需已认证；首次加载获取 `unread_count`（badge）+ `items`（下拉渲染）；点击铃铛直接渲染 `items`，无需再次请求                                            |
| 3              | 全部已读      | `markAllRead()`                                 | `/msg/notifications/read-all`   | PUT  | —                                                                                                                                                                 | 需已认证                                                                                                                |
| 4              | 查看通知详情    | `goToNotify(id)`                                | `/msg/notifications`            | GET  | `page`, `page_size`                                                                                                                                               | 跳转 `notification.html`分页展示所有通知                                                                                      |
| 6              | 用户菜单      | `toggleUserMenu()`                              | —                               |  —   | —                                                                                                                                                                 | 纯前端，显示/隐藏菜单                                                                                                         |
| 7              | 头像菜单项     | —                                               | —                               |  —   | —                                                                                                                                                                 | 企业工作台/管理后台/退出登录，纯前端跳转                                                                                               |
| 8              | 导航栏链接     | —                                               | —                               |  —   | —                                                                                                                                                                 | 首页/商机广场/企业名录/校友圈，纯前端跳转                                                                                              |
| **Hero 区域**    |           |                                                 |                                 |      |                                                                                                                                                                   |                                                                                                                     |
| 9              | 发布商机按钮    | `showPublishModal(type)`                        | —                               |  —   | —                                                                                                                                                                 | 点击触发显示发布商机弹窗（#21-22），type=buy/supply区分采购/供应；未登录跳转登录页                                                                |
| 10             | 热门检索标签    | —                                               | —                               |  —   | —                                                                                                                                                                 | 点击跳转 `search.html?keyword=标签名`，纯前端                                                                                  |
| **统计数据**       |           |                                                 |                                 |      |                                                                                                                                                                   |                                                                                                                     |
| 11             | 平台统计数字    | —                                               | `/public/stats`                 | GET  | —                                                                                                                                                                 | 公开，展示入驻企业数/商机数/撮合数/活跃用户数                                                                                            |
| **智能匹配推荐**     |           |                                                 |                                 |      |                                                                                                                                                                   |                                                                                                                     |
| 12             | 推荐商机列表    | —                                               | `/opp/opportunity/recommended`  | GET  | —                                                                                                                                                                 | 公开，固定返回4条                                                                                                           |
| 13             | 获取联系方式弹窗  | `showContactModal()`                            | —                               |  —   | —                                                                                                                                                                 | 纯前端弹窗，点击商机卡片触发                                                                                                      |
| 14             | 获取联系方式    | `handleGetContact()`                            | `/opp/opportunity/{id}/contact` | POST | —                                                                                                                                                                 | 需已认证+绑定认证企业；成功后显示contactResultModal                                                                                 |
| 15             | 联系方式结果弹窗  | `showContactResultModal()`                      | —                               |  —   | —                                                                                                                                                                 | 纯前端弹窗，显示联系人姓名+手机号+微信（接口返回数据）；可一键复制                                                                                  |
| **侧边栏**        |           |                                                 |                                 |      |                                                                                                                                                                   |                                                                                                                     |
| 16             | 企业详情抽屉    | `showEnterpriseDrawer(enterpriseId)`            | `/ent/enterprise/{id}`          | GET  | —                                                                                                                                                                 | 点击企业卡片时调用；返回企业详情+商机列表，填充抽屉内容                                                                                        |
| 17             | 新入驻企业     | —                                               | `/ent/enterprise/newest`        | GET  | —                                                                                                                                                                 | 公开，固定返回3条                                                                                                           |
| 18             | 校友动态      | —                                               | `/feed/feed/newest`             | GET  | —                                                                                                                                                                 | 公开，固定返回2条                                                                                                           |
| **登录弹窗**       |           |                                                 |                                 |      |                                                                                                                                                                   |                                                                                                                     |
| 19             | 跳转登录页     | `showLoginModal()`                              | —                               |  —   | —                                                                                                                                                                 | Header未登录状态点击"登录/注册"按钮、点击发布商机按钮（未登录）时调用；跳转login.html，登录逻辑见登录页API列表                                                  |
| **发布商机弹窗**     |           |                                                 |                                 |      |                                                                                                                                                                   |                                                                                                                     |
| —              | 显示弹窗+加载字典 | `showPublishModal(type)`                        | —                               |  —   | —                                                                                                                                                                 | 触发后依次加载：GET /ent/industry、GET /ent/category、GET /ent/region、GET /plat-admin/master-data?category=tag；可复用（首页/商机广场共用） |
| 20             | 行业分类下拉    | —                                               | `/ent/industry`                 | GET  | `parent_id`                                                                                                                                                       | 公开；一级parent_id=0，二级传一级ID；填充行业选择下拉                                                                                   |
| 21             | 业务品类下拉    | —                                               | `/ent/category`                 | GET  | `industry_id`                                                                                                                                                     | 公开；按行业筛选；填充业务品类选择下拉                                                                                                 |
| 22             | 行政区划下拉    | —                                               | `/ent/region`                   | GET  | `parent_id`                                                                                                                                                       | 公开；一级parent_id=0获取省，二级传省ID获取市；填充省市区选择下拉                                                                             |
| 23             | 业务标签下拉    | —                                               | `/plat-admin/master-data`       | GET  | `category='tag'`                                                                                                                                                  | 公开；获取全部业务标签，前端随机展示5个作为推荐标签                                                                                          |
| 24             | 标签选择/添加   | `pickTagIdx()`, `removeTagIdx()`, `addTagIdx()` | —                               |  —   | —                                                                                                                                                                 | 纯前端Tag组件；从23获取的标签中随机展示5个作为推荐，用户可取消选择或手动输入添加                                                                         |
| 25             | 发布商机      | `handlePublish()`                               | `/opp/opportunity`              | POST | `type`, `title`, `industry_id`, `sub_industry_id`, `category_id`, `province_id`, `region_id`, `detail`, `tags`, `contact_name`, `contact_phone`, `contact_wechat` | 需已认证+绑定认证企业                                                                                                         |
| **通用组件**       |           |                                                 |                                 |      |                                                                                                                                                                   |                                                                                                                     |
| 26             | 关闭弹窗      | `closeModal(id)`                                | —                               |  —   | —                                                                                                                                                                 | 纯前端，点击遮罩或X按钮                                                                                                        |
| 27             | 关闭抽屉      | `closeDrawer(id)`                               | —                               |  —   | —                                                                                                                                                                 | 纯前端                                                                                                                 |
| 28             | Toast提示   | `showToast(message, type)`                      | —                               |  —   | —                                                                                                                                                                 | 纯前端，3秒自动消失                                                                                                          |

**交互说明**：
- 通知铃铛：登录用户可见，未登录用户不显示
- 发布商机按钮：登录用户可见，未登录用户跳转登录页
- 企业工作台/管理后台入口：根据用户角色显示（详见权限设计）
- Header搜索框：回车或点击图标跳转 search.html
- 热门检索标签：点击直接跳转 search.html

**首页数据加载流程**：
```
页面加载 → GET /public/stats（统计数据）
         → GET /opp/opportunity/recommended（4条推荐商机）
         → GET /ent/enterprise/newest（3条新入驻企业）
         → GET /feed/feed/newest（2条校友动态）
         ↓
已登录用户 → GET /msg/notifications/recent?limit=3（通知未读数+最新3条）
           → 显示通知铃铛badge（unread_count）
           → 点击铃铛 → 前端直接渲染 items 数组到下拉框
```

**发布商机流程**：
```
点击"发布商机" → showPublishModal()显示弹窗
              → 选择类型(buy/supply)、填写信息、选择标签
              → handlePublish() → POST /opp/opportunity
              → 成功后关闭弹窗，显示Toast
```

---

### 3.4 宣传页接口

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

### 企业名录 API 列表

**页面**：企业名录（enterprise.html）

**Header 导航栏**：见首页 API 列表

---

#### Header 企业名录区域

| #   | 页面功能   | 前端函数                | API                   | 方法  | 请求参数                    | 说明                      |
| --- | ------ | ------------------- | --------------------- | :-: | ----------------------- | ----------------------- |
| 1   | 认领已有企业 | `showClaimModal()`  | `GET /ent/enterprise` | GET | `auth_status=UNCLAIMED` | 获取未认领企业列表（需已认证，未认证跳转登录） |
| 2   | 创建新企业  | `showCreateModal()` | `GET /ent/industry`   | GET | `parent_id=0`           | 加载一级行业字典（创建/认领共用）       |

---

#### 侧边栏筛选（级联选择器 + 多选 + 防抖实时搜索）

| #   | 页面功能   | 前端函数                                          | API                   | 方法  | 请求参数                                                                           | 说明                                             |
| --- | ------ | --------------------------------------------- | --------------------- | :-: | ------------------------------------------------------------------------------ | ---------------------------------------------- |
| 3   | 行业级联选择 | `toggleCascader()` → 展开面板                     | —                     |  —  | —                                                                              | 点击输入框展开两级级联面板；一级行业复选框多选；hover时右侧显示二级列表；二级复选框多选 |
| 4   | 一级行业勾选 | `toggleIndustry1(id)`                         | —                     |  —  | —                                                                              | 勾选时添加该行业旗下全部二级到已选；取消时移除；更新industryTags标签       |
| 5   | 二级行业勾选 | `toggleIndustry2(id)`                         | —                     |  —  | —                                                                              | 勾选/取消单个二级行业；更新industryTags标签；触发防抖搜索            |
| 6   | 行业标签移除 | `removeIndustry1(id)` / `removeIndustry2(id)` | —                     |  —  | —                                                                              | 点击标签×移除单个条件；联动更新二级选项；触发防抖搜索                    |
| 7   | 行业数据加载 | `initIndustryCascader()`                      | `GET /ent/industry`   | GET | `parent_id`                                                                    | 页面初始化时加载一级行业字典；id动态渲染                          |
| 8   | 业务品类多选 | `toggleMultiFilter()`                         | —                     |  —  | —                                                                              | 纯前端多选：全部/具体品类；选中触发防抖搜索                         |
| 9   | 地区级联选择 | `toggleCascader()` → 展开面板                     | —                     |  —  | —                                                                              | 点击输入框展开两级级联面板；省份复选框多选；hover时右侧显示城市列表；城市复选框多选   |
| 10  | 省份勾选   | `toggleProvince(id)`                          | —                     |  —  | —                                                                              | 勾选时添加该省份旗下全部城市到已选；取消时移除；更新regionTags标签         |
| 11  | 城市勾选   | `toggleCity(id)`                              | —                     |  —  | —                                                                              | 勾选/取消单个城市；更新regionTags标签；触发防抖搜索                |
| 12  | 地区标签移除 | `removeProvince(id)` / `removeCity(id)`       | —                     |  —  | —                                                                              | 点击标签×移除单个条件；联动更新城市选项；触发防抖搜索                    |
| 13  | 地区数据加载 | `initRegionCascader()`                        | `GET /ent/region`     | GET | `parent_id`                                                                    | 页面初始化时加载省份字典；id动态渲染                            |
| 14  | 热门标签多选 | `toggleHotTag(tag, element)`                  | —                     |  —  | —                                                                              | 点击切换标签选中状态；触发防抖搜索                              |
| 15  | 已选条件摘要 | `updateFilterSummary()`                       | —                     |  —  | —                                                                              | 纯前端渲染：显示所有已选条件的标签列表；点击×调用对应remove函数            |
| 16  | 防抖搜索触发 | `debounceSearch()` → `triggerSearch()`        | `GET /ent/enterprise` | GET | `industry1`, `industry2`, `category`, `province`, `city`, `hotTags`, `keyword` | 300ms防抖；合并所有筛选参数；联动商机列表刷新                      |
| 17  | 重置筛选   | `resetAllFilters()`                           | —                     |  —  | —                                                                              | 清空filterState；重置所有UI状态；重新触发搜索                  |

**筛选参数说明**：
- `industry1`：一级行业ID数组，如 `industry1=ind-1,ind-2`
- `industry2`：二级行业ID数组，如 `industry2=ind-1-1,ind-1-2`
- `category`：业务品类ID数组，如 `category=cat-1,cat-2`
- `province`：省份ID数组，如 `province=prov-1,prov-2`
- `city`：城市ID数组，如 `city=prov-1-1,prov-1-2`
- `hotTags`：标签数组，如 `tags=专精特新,高新技术企业`
- `keyword`：关键词搜索

**侧边栏筛选交互说明**：
1. **级联选择器**：行业分类和所在地区使用级联面板，一级勾选后hover右侧显示二级列表
2. **多选支持**：一级行业、二级行业，省份、城市均支持多选
3. **联动关系**：一级行业联动二级行业列表；省份联动城市列表
4. **实时搜索**：所有筛选操作触发300ms防抖后调用 `GET /ent/enterprise`
5. **已选摘要**：下方显示所有已选条件标签，点击×可单独移除
6. **空状态处理**：二级行业/城市无数据时显示"暂无数据"提示

---

#### 企业列表 + 分页

| #   | 页面功能   | 前端函数             | API                   | 方法  | 请求参数                | 说明                  |
| --- | ------ | ---------------- | --------------------- | :-: | ------------------- | ------------------- |
| 14  | 企业列表加载 | —                | `GET /ent/enterprise` | GET | `page`, `page_size` | 公开；携带当前筛选条件，含分页     |
| 15  | 分页     | `goToPage(page)` | `GET /ent/enterprise` | GET | `page`              | 点击分页按钮，携带当前筛选条件刷新列表 |

---

#### 企业详情侧边悬浮窗

| #   | 页面功能    | 前端函数                                 | API                                 |  方法  | 请求参数 | 说明                  |
| --- | ------- | ------------------------------------ | ----------------------------------- | :--: | ---- | ------------------- |
| 16  | 打开企业详情  | `showEnterpriseDrawer(enterpriseId)` | `GET /ent/enterprise/{id}`          | GET  | —    | 返回企业详情，含发布的商机列表     |
| 17  | 获取联系方式  | `handleGetContact()`                 | `POST /ent/enterprise/{id}/contact` | POST | —    | 确认后获取企业联系信息（需已认证用户） |
| 18  | 关闭详情悬浮窗 | `closeDrawer('enterpriseDrawer')`    | —                                   |  —   | —    | 纯前端，点击X或遮罩关闭        |

---

#### 通用组件

| #   | 页面功能    | 前端函数                                        | API                           |  方法  | 请求参数                                                                                                                                                                              | 说明                              |
| --- | ------- | ------------------------------------------- | ----------------------------- | :--: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| 19  | 打开认领弹窗  | `showClaimModal()`                          | `GET /ent/enterprise`         | GET  | `auth_status=UNCLAIMED`                                                                                                                                                           | 获取未认领企业列表                       |
| 20  | 选择认领企业  | `selectClaimEnterprise(name, id, industry)` | —                             |  —   | —                                                                                                                                                                                 | 纯前端：切换到填写表单                     |
| 21  | 返回认领选择  | `backToClaimSelect()`                       | —                             |  —   | —                                                                                                                                                                                 | 纯前端：返回企业列表                      |
| 22  | 提交认领申请  | `handleClaim()`                             | `POST /ent/enterprise/claim`  | POST | `enterprise_id`, `applicant_position`, `legal_representative`, `business_license`                                                                                                 | 需已认证用户；图片为multipart             |
| 23  | 打开创建弹窗  | `showCreateModal()`                         | `GET /ent/industry`           | GET  | `parent_id=0`                                                                                                                                                                     | 加载一级行业字典（创建/认领共用）；同时加载省份字典、标签字典 |
| 24  | 切换一级行业  | `onCreateIndustry1Change()`                 | `GET /ent/industry`           | GET  | `parent_id`                                                                                                                                                                       | 联动加载二级行业下拉                      |
| 25  | 切换二级行业  | —                                           | `GET /ent/category`           | GET  | `industry_id`                                                                                                                                                                     | 联动加载业务品类下拉（按行业筛选）               |
| 26  | 切换省份    | `onCreateProvinceChange()`                  | `GET /ent/region`             | GET  | `parent_id`                                                                                                                                                                       | 联动加载城市下拉                        |
| 27  | 标签推荐展示  | —                                           | `GET /plat-admin/master-data` | GET  | `category='tag'`                                                                                                                                                                  | 获取全部标签，前端随机展示5个作为推荐标签           |
| 28  | 添加创建标签  | `pickTag(tag)` / `addTag(input)`            | —                             |  —   | —                                                                                                                                                                                 | 纯前端：从推荐标签选择或自定义输入               |
| 29  | 移除创建标签  | `removeTagCreate(tag)`                      | —                             |  —   | —                                                                                                                                                                                 | 纯前端：从已添加标签中移除                   |
| 30  | 提交创建企业  | `handleCreate()`                            | `POST /ent/enterprise/create` | POST | `name`, `credit_code`, `industry_id`, `sub_industry_id`, `category_id`, `province_id`, `region_id`, `tags[]`, `description`, `logo_url`, `business_license`, `applicant_position` | 需已认证用户；图片为multipart             |
| 27  | Toast提示 | `showToast(message, type)`                  | —                             |  —   | —                                                                                                                                                                                 | 纯前端，3秒自动消失                      |
| 28  | 关闭弹窗    | `closeModal(id)`                            | —                             |  —   | —                                                                                                                                                                                 | 纯前端，点击遮罩或X按钮                    |

---

**交互说明**：
- **认领企业**：用户认领平台上的未认证企业（auth_status=UNCLAIMED），提交证明材料后待平台审核
- **创建企业**：用户在平台上创建新企业档案，提交后待平台审核
- **企业详情**：已认证企业可见完整联系方式；未认证用户仅可见基本信息，联系方式需点击"获取"
- **筛选联动**：
  - 行业筛选：一级行业单选 + 二级行业多选联动（选中一级后展开二级）
  - 地区筛选：省份单选 + 城市多选联动（选中省份后展开城市）
  - 业务品类：多选（可勾选"全部品类"或具体品类）
  - 热门标签：多选（从全部标签中随机展示5个，前端控制）
- **防抖搜索**：所有筛选条件变更后，300ms防抖触发搜索
- **已选条件摘要**：显示所有已选筛选项，支持单独移除

---

### 3.5 企业相关接口

#### GET /api/v1/ent/enterprise（企业列表）
**权限**: 公开

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码，默认1 |
| page_size | int | N | 每页条数，默认20 |
| industry_id | int | N | 一级行业ID |
| sub_industry_id | int | N | 二级行业ID |
| category_id | int | N | 业务品类ID |
| province_id | int | N | 省份ID |
| region_id | int | N | 市ID |
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
| credit_code | string | 统一社会信用代码（认领时展示确认） |
| logo_url | string | Logo URL |
| industry_name | string | 一级行业名称 |
| sub_industry_name | string | 二级行业名称 |
| category_name | string | 主营业务品类名称 |
| province_name | string | 所属省份名称 |
| region_name | string | 市名称 |
| tags | array | 标签列表 |
| auth_status | string | 认证状态 |

---

#### GET /api/v1/ent/enterprise/newest（最新入驻企业）
**权限**: 公开

**功能说明**：首页侧边栏"新入驻企业"模块，展示最近注册的已认证企业。

**业务规则**：
- 每页返回 **3条** 企业
- 仅返回已认证企业（auth_status = 'VERIFIED'）
- 按注册时间倒序（最新在前）
- 排除条件：本企业已入驻的企业（去重）

**查询参数**: 无

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 企业列表（固定3条） |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 企业ID |
| name | string | 企业名称 |
| logo_url | string | Logo URL |
| industry_name | string | 一级行业名称 |
| sub_industry_name | string | 二级行业名称 |
| auth_status | string | 认证状态（固定为 VERIFIED） |

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
| industry_id | int | 一级行业ID |
| industry_name | string | 一级行业名称 |
| sub_industry_id | int | 二级行业ID |
| sub_industry_name | string | 二级行业名称 |
| category_id | int | 品类ID |
| category_name | string | 品类名称 |
| region_id | int | 市ID |
| province_id | int | 省份ID |
| province_name | string | 所属省份名称 |
| region_name | string | 市名称 |
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

**提交后落库逻辑**：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 新增 `plat_audit_record` 记录 | 关联企业+申请人，status=PENDING，附件存储business_license |
| 2 | 更新 `ent_enterprise` 记录 | auth_status → PENDING，锁定 name 和 credit_code（不可再修改） |
| 3 | 记录 `ent_user_profile` 关联 | 临时记录申请人信息，待审核通过后生效 |
| 4 | 发送系统通知 | 通知平台运营有新的认领待审核 |

---

#### POST /api/v1/ent/enterprise/create（创建企业）
**权限**: 已认证

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | Y | 企业全称 |
| credit_code | string | Y | 统一社会信用代码，18位 |
| legal_representative | string | Y | 法人姓名 |
| industry_id | int | Y | 一级行业ID |
| sub_industry_id | int | Y | 二级行业ID |
| category_id | int | N | 主营业务品类ID |
| province_id | int | Y | 省份ID |
| region_id | int | Y | 市ID |
| tags | array | N | 业务标签，如 ["专精特新", "高新技术企业"] |
| description | string | N | 企业简介，≥50字 |
| logo_url | file | N | Logo图片 |
| business_license | file | Y | 营业执照图片 |
| applicant_position | string | Y | 申请人职务（申请信息，非企业字段） |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| enterprise_id | int | 企业ID |
| audit_id | int | 审核记录ID |
| status | string | PENDING |
| message | string | 提示信息 |

**提交后落库逻辑**：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 新增 `ent_enterprise` 记录 | auth_status=PENDING，name和credit_code待审核 |
| 2 | 新增 `plat_audit_record` 记录 | 关联新创建企业+申请人，status=PENDING，附件存储logo和business_license |
| 3 | 临时记录 `ent_user_profile` | 申请人user_id和职务待审核通过后生效 |
| 4 | 发送系统通知 | 通知平台运营有新的创建待审核 |


---

#### GET /api/v1/ent/enterprise/my（我的企业）
**权限**: 已认证

**业务说明**: 返回当前用户所属企业的完整信息，用于企业端管理中心的"维护信息"页面。返回空（code=200, data=null）表示用户未绑定任何企业。

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 企业ID |
| name | string | 企业全称 |
| credit_code | string | 统一社会信用代码（认证用户可见） |
| logo_url | string | Logo URL |
| industry_id | int | 一级行业ID |
| industry_name | string | 一级行业名称 |
| sub_industry_id | int | 二级行业ID |
| sub_industry_name | string | 二级行业名称 |
| category_id | int | 品类ID |
| category_name | string | 品类名称 |
| region_id | int | 市ID |
| province_id | int | 省份ID |
| province_name | string | 所属省份名称 |
| region_name | string | 市名称 |
| tags | array | 标签列表 |
| description | string | 企业简介 |
| auth_status | string | UNCLAIMED/PENDING/VERIFIED/REJECTED |
| role_code | string | 当前用户在企业的角色（ADMIN/MEMBER） |
| admin_user_id | int | 管理员用户ID |
| created_at | datetime | 创建时间 |

---

#### PUT /api/v1/ent/enterprise/{id}（更新企业信息）
**权限**: 企业管理员

**请求字段**（仅可修改以下字段）:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| logo_url | file | N | Logo图片 |
| category_id | int | N | 主营业务品类 |
| province_id | int | N | 省份ID |
| region_id | int | N | 市ID |
| tags | array | N | 标签 |
| description | string | N | 企业简介 |

**不可修改字段**: name, credit_code, legal_representative, industry_id（需联系平台运营）

---

#### GET /api/v1/ent/industry（行业分类列表）
**权限**: 公开
**数据来源**: plat_master_data，category='industry'（支持二级：父级ID为空为一级，父级ID不为空为二级子行业）
**层级说明**: 一级（如"智能网联"）、二级（如"智能网联>自动驾驶"）

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parent_id | int | N | 父级行业ID，传0或空获取一级，传一级ID获取二级 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 行业ID |
| name | string | 行业名称 |
| parent_id | int | 父级ID（一级为0） |
| sort_order | int | 排序 |

---

#### GET /api/v1/ent/category（业务品类列表）
**权限**: 公开
**数据来源**: plat_master_data，category='category'（一级平铺，不分层级）
**层级说明**: 一级平铺结构，业务品类按行业归类但无父子层级关系

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
**数据来源**: plat_master_data，category='region'（二级：省→市）
**层级说明**: 一级为省/直辖市，二级为市/区

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parent_id | int | N | 父级ID，传0或空获取一级（省），传一级ID获取二级（市） |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 地区ID |
| name | string | 地区名称 |
| parent_id | int | 父级ID（一级为0） |

---

### 商机广场 API 列表

**页面**：商机广场（opportunity.html）

**Header 导航栏**：见首页 API 列表

| #                              | 页面功能    | 前端函数                                          | API                    | 方法  | 请求参数                                                                                              | 说明                                                          |
| ------------------------------ | ------- | --------------------------------------------- | ---------------------- | :-: | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Header 商机广场区域**              |         |                                               |                        |     |                                                                                                   |                                                             |
| 1                              | 发布采购需求  | `showPublishModal('buy')`                     | —                      |  —  | —                                                                                                 | 点击显示发布商机弹窗；未登录跳转登录页；可复用（首页/商机广场共用）                          |
| 2                              | 发布供应能力  | `showPublishModal('supply')`                  | —                      |  —  | —                                                                                                 | 同上，type='supply'                                            |
| **侧边栏筛选（级联选择器 + 多选 + 防抖实时搜索）** |         |                                               |                        |     |                                                                                                   |                                                             |
| 3                              | 商机类型多选  | `toggleMultiFilter()`                         | —                      |  —  | —                                                                                                 | 纯前端多选：全部/我要买/我能供；选中触发防抖搜索（300ms）                            |
| 4                              | 行业级联选择  | `toggleCascader()` → 展开面板                     | —                      |  —  | —                                                                                                 | 点击输入框展开两级级联面板；一级行业复选框多选；hover时右侧显示二级列表；二级复选框多选              |
| 5                              | 一级行业勾选  | `toggleIndustry1(id)`                         | —                      |  —  | —                                                                                                 | 勾选时添加该行业旗下全部二级到已选；取消时移除；更新industryTags标签                    |
| 6                              | 二级行业勾选  | `toggleIndustry2(id)`                         | —                      |  —  | —                                                                                                 | 勾选/取消单个二级行业；更新industryTags标签；触发防抖搜索                         |
| 7                              | 行业标签移除  | `removeIndustry1(id)` / `removeIndustry2(id)` | —                      |  —  | —                                                                                                 | 点击标签×移除单个条件；联动更新二级选项；触发防抖搜索                                 |
| 8                              | 行业数据加载  | `initIndustryCascader()`                      | `GET /ent/industry`    | GET | `parent_id`                                                                                       | 页面初始化时加载一级行业字典；id动态渲染                                       |
| 9                              | 业务品类多选  | `toggleMultiFilter()`                         | —                      |  —  | —                                                                                                 | 纯前端多选：全部/自动驾驶算法/车规级芯片/动力电池；选中触发防抖搜索                         |
| 10                             | 地区级联选择  | `toggleCascader()` → 展开面板                     | —                      |  —  | —                                                                                                 | 点击输入框展开两级级联面板；省份复选框多选；hover时右侧显示城市列表；城市复选框多选                |
| 11                             | 省份勾选    | `toggleProvince(id)`                          | —                      |  —  | —                                                                                                 | 勾选时添加该省份旗下全部城市到已选；取消时移除；更新regionTags标签                      |
| 12                             | 城市勾选    | `toggleCity(id)`                              | —                      |  —  | —                                                                                                 | 勾选/取消单个城市；更新regionTags标签；触发防抖搜索                             |
| 13                             | 地区标签移除  | `removeProvince(id)` / `removeCity(id)`       | —                      |  —  | —                                                                                                 | 点击标签×移除单个条件；联动更新城市选项；触发防抖搜索                                 |
| 14                             | 地区数据加载  | `initProvinceCascader()`                      | `GET /ent/region`      | GET | `parent_id`                                                                                       | 页面初始化时加载省份字典；id动态渲染                                         |
| 15                             | 已选条件摘要  | `updateFilterSummary()`                       | —                      |  —  | —                                                                                                 | 纯前端渲染：显示所有已选条件的标签列表；点击×调用对应remove函数                         |
| 16                             | 防抖搜索触发  | `debounceSearch()` → `triggerSearch()`        | `GET /opp/opportunity` | GET | `type`, `industry1`, `industry2`, `category`, `province`, `city`                                  | 300ms防抖；合并所有筛选参数；联动商机列表刷新                                   |
| 17                             | 重置筛选    | `resetAllFilters()`                           | —                      |  —  | —                                                                                                 | 清空filterState；重置所有UI状态；重新触发搜索                               |
| **商机列表+分页**                    |         |                                               |                        |     |                                                                                                   |                                                             |
| 18                             | 商机列表加载  | —                                             | `GET /opp/opportunity` | GET | `page`, `page_size`, `type[]`, `industry1[]`, `industry2[]`, `category[]`, `province[]`, `city[]` | 公开；筛选参数支持多值逗号分隔；如 `industry1=ind-1,ind-2&industry2=ind-1-1` |
| 19                             | 商机分页    | `goToPage(page)`                              | `GET /opp/opportunity` | GET | `page`                                                                                            | 点击分页按钮刷新列表；保持当前筛选条件                                         |
| 20                             | 商机卡片点击  | `showContactModal()`                          | 见首页 API 列表             |  —  | —                                                                                                 | 纯前端，显示联系方式确认弹窗；联系弹窗可复用（首页/商机广场共用）                           |
| 21                             | 获取联系方式  | `handleGetContact()`                          | 见首页 API 列表             |  —  | —                                                                                                 | 需已认证+绑定认证企业                                                 |
| **发布商机弹窗**                     |         |                                               |                        |     |                                                                                                   |                                                             |
| —                              | 发布商机弹窗  | `showPublishModal(type)`                      | 见首页 API 列表             |  —  | —                                                                                                 | 可复用（首页/商机广场共用）；字典加载逻辑见首页                                    |
| **通用组件**                       |         |                                               |                        |     |                                                                                                   |                                                             |
| 22                             | 关闭弹窗    | `closeModal(id)`                              | —                      |  —  | —                                                                                                 | 纯前端，点击遮罩或X按钮                                                |
| 23                             | Toast提示 | `showToast(message, type)`                    | —                      |  —  | —                                                                                                 | 纯前端，3秒自动消失                                                  |

**侧边栏筛选交互说明**：

1. **级联选择器**：行业分类和所在地区使用级联面板，一级勾选后hover右侧显示二级列表
2. **多选支持**：商机类型、业务品类、一级行业、二级行业、省份、城市均支持多选
3. **联动关系**：一级行业联动二级行业列表；省份联动城市列表
4. **实时搜索**：所有筛选操作触发300ms防抖后调用 `GET /opp/opportunity`
5. **已选摘要**：下方显示所有已选条件标签，点击×可单独移除
6. **空状态处理**：二级行业/城市无数据时显示"暂无数据"提示

**交互说明**：
- 商机列表：筛选条件变更时自动联动刷新列表
- 一级行业变更时：清空二级行业选择，重新加载二级行业下拉
- 省份变更时：清空城市选择，重新加载城市下拉
- 发布商机：仅限已绑定认证企业的用户，需填写完整联系方式
- 获取联系方式：用户点击"获取联系方式"后，后台记录一次联系请求

**商机列表加载流程**：
```
页面加载 → GET /opp/opportunity（默认全量列表）
         ↓
筛选条件变更 → GET /opp/opportunity（携带筛选参数）
分页点击 → GET /opp/opportunity（携带page参数）
```

---

### 3.6 商机相关接口

#### GET /api/v1/opp/opportunity（商机列表）
**权限**: 公开

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码，默认1 |
| page_size | int | N | 每页条数，默认20 |
| type | string | N | BUY/SUPPLY/空（全部） |
| industry_id | int | N | 一级行业ID |
| sub_industry_id | int | N | 二级行业ID |
| category_id | int | N | 品类ID |
| province_id | int | N | 省份ID |
| region_id | int | N | 市ID |
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
| industry_name | string | 一级行业名称 |
| sub_industry_name | string | 二级行业名称 |
| category_name | string | 品类名称 |
| province_name | string | 所属省份名称 |
| region_name | string | 市名称 |
| tags | array | 标签列表 |
| view_count | int | 浏览量 |
| created_at | datetime | 发布时间 |

---

#### GET /api/v1/opp/opportunity/recommended（智能推荐商机）
**权限**: 公开

**功能说明**：首页智能推荐模块，根据用户登录状态和企业绑定情况，采用不同的推荐策略。

**智能推荐算法逻辑**：

| 用户状态 | 推荐策略 | 说明 |
|---------|---------|------|
| **已登录+有企业** | 协同过滤 + 内容匹配 | 基于用户企业行业标签，匹配同行业/相关行业的商机 |
| **已登录+无企业** | 热门优先 + 多样性 | 同游客，按浏览量/联系量排序，确保行业多样性 |
| **未登录/游客** | 热门优先 + 多样性 | 按浏览量/联系量排序，确保行业多样性展示 |

**推荐因子权重**（综合得分 = Σ 因子 × 权重）：

| 因子 | 权重 | 说明 |
|------|:----:|------|
| 浏览量（view_count） | 0.25 | 历史数据标准化 |
| 联系量（contact_count） | 0.30 | 表明有实际需求 |
| 发布时间（recency） | 0.25 | 新发布优先（7天内最高权重） |
| 行业匹配（industry_match） | 0.20 | 与用户/企业行业匹配（仅已登录+有企业用户有效） |

**业务规则**：
- 每页返回 **4条** 商机
- 商机类型分布：优先 BUY 类型（60%）+ SUPPLY 类型（40%），不足时按实际比例
- 排除条件：已下架（OFFLINE）、本企业已发布的商机（去重）
- 同一商机不重复出现（按商机ID去重）

**查询参数**: 无

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 推荐商机列表（固定4条） |

**items元素**: 同商机列表（id, type, title, enterprise_id, enterprise_name, industry_name, sub_industry_name, category_name, province_name, region_name, tags, view_count, created_at）

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
| industry_id | int | 一级行业ID |
| industry_name | string | 一级行业名称 |
| sub_industry_id | int | 二级行业ID |
| sub_industry_name | string | 二级行业名称 |
| category_id | int | 品类ID |
| category_name | string | 品类名称 |
| region_id | int | 市ID |
| province_id | int | 省份ID |
| province_name | string | 所属省份名称 |
| region_name | string | 市名称 |
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
| industry_id | int | Y | 一级行业ID |
| sub_industry_id | int | Y | 二级行业ID |
| category_id | int | Y | 品类ID |
| province_id | int | Y | 省份ID |
| region_id | int | Y | 市ID |
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

### 校友圈 API 列表

**页面**：校友圈（feeds.html）

**Header 导航栏**：见首页 API 列表

| #        | 页面功能    | 前端函数                       |        API        | 方法   | 请求参数                             | 说明                                                    |
| -------- | ------- | -------------------------- | :---------------: | ---- | -------------------------------- | ----------------------------------------------------- |
| **动态列表** |         |                            |                   |      |                                  |                                                       |
| 1        | 页面加载    | —                          | `GET /feed/feed`  | GET  | `page`, `page_size`              | 公开；按发布时间倒序；响应返回`total`(总数)、`page`、`page_size`、`items` |
| 2        | 加载更多    | `loadMoreFeeds()`          | `GET /feed/feed`  | GET  | `page`, `page_size`              | 公开；前端`currentPage++`请求下一页；响应同页面加载；无更多数据时隐藏按钮          |
| **发布动态** |         |                            |                   |      |                                  |                                                       |
| 3        | 发布动态按钮  | `showPublishModal()`       |         —         | —    | —                                | 纯前端显示发布弹窗；feeds.html内嵌发布弹窗                            |
| 4        | 发布动态    | `handlePublish()`          | `POST /feed/feed` | POST | `content`, `images[]`（multipart） | 需已认证+绑定认证企业；images最多9张，作为multipart/form-data一起上传      |
| **通用组件** |         |                            |                   |      |                                  |                                                       |
| 5        | 关闭弹窗    | `closeModal(id)`           |         —         | —    | —                                | 纯前端，点击遮罩或X按钮                                          |
| 6        | Toast提示 | `showToast(message, type)` |         —         | —    | —                                | 纯前端，3秒自动消失                                            |

**交互说明**：
- 动态列表：公开显示，仅展示已认证企业发布的动态
- 点赞/评论/分享：需登录，未登录点击跳转登录页
- 发布动态：仅限已绑定认证企业的用户，支持图文内容（最多9张）
- 删除/下线：企业管理员可下线本企业发布的动态，发布者可删除自己的动态

**Header 导航栏**：见首页 API 列表

---

### 3.7 动态相关接口

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
| publisher_role | string | 发布人职级（如 CEO、员工） |
| enterprise_id | int | 企业ID |
| enterprise_name | string | 企业名称 |
| enterprise_logo | string | 企业Logo URL |
| created_at | datetime | 发布时间 |

---

#### GET /api/v1/feed/feed/newest（最新校友动态）
**权限**: 公开

**功能说明**：首页侧边栏"校友动态"模块，展示最近发布的动态。

**业务规则**：
- 每页返回 **2条** 动态
- 按发布时间倒序（最新在前）
- 仅返回已认证企业发布的动态（过滤 UNCLAIMED/PENDING 企业）

**查询参数**: 无

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 动态列表（固定2条） |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 动态ID |
| content | string | 动态内容（截取前100字+省略号） |
| publisher_name | string | 发布人姓名 |
| enterprise_name | string | 企业名称 |
| created_at | datetime | 发布时间（相对时间展示，如"1小时前"由前端处理） |

---

#### GET /api/v1/feed/feed/{id}（动态详情）
**权限**: 已认证

**响应字段**: 同动态列表元素，增加 updated_at

---

#### POST /api/v1/feed/feed（发布动态）
**权限**: 已认证（需绑定认证企业）

**Content-Type**: `multipart/form-data`

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | Y | 动态内容，≤1000字 |
| images | file[] | N | 图片文件列表，最多9张；支持jpg/png；前端直接上传文件，后端存储并返回URL |

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

### 企业工作台 API 列表

**页面**：企业信息（enterprise-admin/enterprise-info.html）、员工管理（enterprise-admin/employee.html）、商机管理（enterprise-admin/my-opportunity.html）

**Header 导航栏**：见首页 API 列表

---

#### enterprise-info.html（企业信息维护）

| #        | 页面功能    | 前端函数                       | API                        | 方法  | 请求参数                                                                      | 说明                       |
| -------- | ------- | -------------------------- | -------------------------- | :-: | ------------------------------------------------------------------------- | ------------------------ |
| 1        | 页面加载    | —                          | `GET /ent/enterprise/my`   | GET | —                                                                         | 需已认证，返回当前用户所属企业信息        |
| 2        | 保存修改    | `handleSave()`             | `PUT /ent/enterprise/{id}` | PUT | `category_id`, `province_id`, `region_id`, `detail`, `logo_url`, `tags[]` | 需企业管理员；支持multipart更新Logo |
| **通用组件** |         |                            |                            |     |                                                                           |                          |
| 3        | Toast提示 | `showToast(message, type)` | —                          |  —  | —                                                                         | 纯前端，3秒自动消失               |

---

#### employee.html（员工管理）

| #        | 页面功能    | 前端函数                        | API                                             |  方法  | 请求参数                                              | 说明                                          |
| -------- | ------- | --------------------------- | ----------------------------------------------- | :--: | ------------------------------------------------- | ------------------------------------------- |
| 1        | 页面加载    | —                           | `GET /ent-admin/employees`                      | GET  | `keyword`（可选）                                     | 需企业管理员；后端根据认证用户自动关联企业，无需传参；keyword可搜索姓名或手机号 |
| 2        | 添加员工弹窗  | `showAddModal()`            | —                                               |  —   | —                                                 | 纯前端显示新增弹窗                                   |
| 3        | 添加员工    | `handleAdd()`               | `POST /ent-admin/employees`                     | POST | `phone`, `real_name`, `position`, `role_code`     | 需企业管理员；手机号需已注册用户（非企业员工）                     |
| 4        | 编辑员工弹窗  | `showEditModal(employeeId)` | —                                               |  —   | —                                                 | 纯前端显示编辑弹窗；可修改姓名、职位、角色、账号状态（启用/停用）           |
| 5        | 编辑员工    | `handleEdit()`              | `PUT /ent-admin/employees/{id}`                 | PUT  | `real_name`, `position`, `role_code`, `is_active` | 需企业管理员；`is_active=false`为停用账号，`true`为启用     |
| 6        | 重置密码    | `resetPassword(employeeId)` | `POST /ent-admin/employees/{id}/reset-password` | POST | —                                                 | 需企业管理员；系统发送新密码至员工手机                         |
| 7        | 解绑员工    | `handleUnbind(employeeId)`  | `POST /ent-admin/employees/{id}/unbind`         | POST | —                                                 | 需企业管理员；解除员工与企业绑定，恢复为游客身份；若原为停用状态则自动启用       |
| **通用组件** |         |                             |                                                 |      |                                                   |                                             |
| 8        | 关闭弹窗    | `closeModal(id)`            | —                                               |  —   | —                                                 | 纯前端，点击遮罩或X按钮                                |
| 9        | Toast提示 | `showToast(message, type)`  | —                                               |  —   | —                                                 | 纯前端，3秒自动消失                                  |

---

#### my-opportunity.html（商机管理）

| #        | 页面功能    | 前端函数                             | API                                              | 方法  | 请求参数                                                                                                        | 说明                            |
| -------- | ------- | -------------------------------- | ------------------------------------------------ | :-: | ----------------------------------------------------------------------------------------------------------- | ----------------------------- |
| 1        | 页面加载    | —                                | `GET /ent-admin/my-opportunities`                | GET | `page`, `page_size`, `type`, `status`, `keyword`                                                            | 需已认证；后端根据认证用户自动关联企业；展示本企业所有商机 |
| 2        | 筛选      | `handleFilter()`                 | `GET /ent-admin/my-opportunities`                | GET | `type`, `status`, `keyword`                                                                                 | 按类型/状态/关键词筛选                  |
| 3        | 分页      | `goToPage(page)`                 | `GET /ent-admin/my-opportunities`                | GET | `page`                                                                                                      | 点击分页按钮刷新列表                    |
| 4        | 编辑商机    | `showEditModal(opportunityId)`   | `PUT /ent-admin/my-opportunities/{id}`           | PUT | `title`, `industry1_id`, `industry2_id`, `category_id`, `province_id`, `region_id`, `tags[]`, `description` | 需企业管理员或发布人；type（类型）发布后不可修改    |
| 5        | 下架商机    | `handleOffline(opportunityId)`   | `PUT /ent-admin/my-opportunities/{id}/offline`   | PUT | —                                                                                                           | 需企业管理员或商机发布人                  |
| 6        | 重新发布    | `handleRepublish(opportunityId)` | `PUT /ent-admin/my-opportunities/{id}/republish` | PUT | —                                                                                                           | 需企业管理员或商机发布人                  |
| **通用组件** |         |                                  |                                                  |     |                                                                                                             |                               |
| 7        | Toast提示 | `showToast(message, type)`       | —                                                |  —  | —                                                                                                           | 纯前端，3秒自动消失                    |

**交互说明**：
- 企业信息维护：基本认证信息（名称、信用代码、行业）不可修改；公开展示信息（品类、地区、Logo、标签、简介）可由企业管理员修改
- 员工管理：企业管理员可添加/编辑/停用/解绑员工，设置角色；普通员工仅可编辑自己的职位
  - **添加员工前提**：该手机号需已在平台注册（通过校友圈注册流程），但尚未加入任何企业
  - **停用账号**：`is_active=false`，该用户无法登录；通过编辑弹窗中的账号状态下拉框操作
  - **解绑员工**：解除员工与企业绑定，角色变更为`guest`（游客），可重新加入本企业或其他企业；若原为停用状态，自动恢复为启用
- 密码重置：系统自动将密码重置为手机号后6位，由管理员线下通知用户
- 商机管理：展示本企业所有员工发布的商机；企业管理员或发布人可下架/重新发布

---

### 3.8 企业端管理接口

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
| position | string | 职位/职级 |
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
| position | string | N | 职位/职级（如 CEO、总监、员工） |
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
| position | string | N | 职位/职级 |
| role_code | string | N | enterprise_admin/employee |
| is_active | bool | N | 是否启用（设为 false 则停用账号） |

**停用账号说明**：
- `is_active = false`：账号停用，该用户无法登录
- `is_active = true`：账号启用，恢复正常使用
- 停用后，用户当前会话立即失效

---

#### POST /api/v1/ent-admin/employees/{id}/unbind（解绑员工）
**权限**: 企业管理员

**功能说明**：将员工从本企业解绑，解除其与企业的绑定关系。

**解绑效果**：
| 字段 | 变化 |
|------|------|
| enterprise_id | 置为 null |
| role_code | 更新为 `guest`（游客） |
| is_active | 若原为停用，自动恢复为 true |
| 账号状态 | 恢复为"游客"，可重新加入其他企业 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 解绑成功 |

**使用场景**：
- 员工离职，需解除其与企业绑定但保留账号
- 解绑后该账号可重新被本企业或其他企业添加

---

#### POST /api/v1/ent-admin/employees/{id}/reset-password（重置密码）
**权限**: 企业管理员

**功能说明**：将员工密码重置为手机号后6位，由管理员线下通知用户。

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 操作结果提示 |

---

#### 员工账号状态校验说明

**停用（is_active = false）校验**：

| 接口 | 校验方式 | 停用后行为 |
|------|----------|------------|
| `POST /api/v1/auth/login` | 登录时校验 | 禁止登录，提示"账号已停用" |
| `GET /api/v1/ent-admin/employees` | 列表查询时校验 | 管理员可通过筛选查看已停用员工 |
| `POST /api/v1/ent-admin/employees` | 添加时校验 | 禁止添加已停用的手机号（需先启用） |
| `GET /api/v1/ent-admin/my-opportunities` | 查询时校验 | 停用员工不能查看/操作本企业商机 |
| `POST /api/v1/opportunity/opportunities` | 发布时校验 | 停用员工不能发布商机，提示"账号已停用" |
| `POST /api/v1/feed/feed` | 发布时校验 | 停用员工不能发布动态，提示"账号已停用" |
| `POST .../reset-password` | 操作时校验 | 仍可重置（便于管理员恢复账号） |

**解绑后账号状态**：
- 恢复为"游客"身份，enterprise_id = null
- 若原为停用状态，自动恢复为启用
- 解绑后该账号可被重新添加至本企业或加入其他企业

---

#### GET /api/v1/ent-admin/my-opportunities（本企业商机列表）
**权限**: 企业管理员/员工
**说明**: 返回当前用户所属企业的商机列表，enterprise_id 从登录用户信息自动获取

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | N | BUY/SUPPLY/空（全部） |
| status | string | N | ACTIVE/OFFLINE/PENDING/空（全部） |
| keyword | string | N | 商机标题关键词搜索 |
| page | int | N | 页码，默认1 |
| page_size | int | N | 每页条数，默认20 |

**响应字段**: 同商机列表

---

#### PUT /api/v1/ent-admin/my-opportunities/{id}（编辑商机）
**权限**: 企业管理员或发布人

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | Y | 商机标题 |
| industry1_id | int | Y | 一级行业ID |
| industry2_id | int | Y | 二级行业ID |
| category_id | int | Y | 业务品类ID |
| province_id | int | Y | 省份ID |
| region_id | int | Y | 城市/地区ID |
| tags | array | N | 业务标签数组 |
| description | string | Y | 详细描述 |

**不可修改字段**：
| 字段 | 说明 |
|------|------|
| type | 商机类型（我要买/我能供）发布后不可修改 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 保存成功 |

---

#### PUT /api/v1/ent-admin/my-opportunities/{id}/offline（下架商机）
**权限**: 企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 下架成功 |

---

#### PUT /api/v1/ent-admin/my-opportunities/{id}/republish（重新发布）
**权限**: 企业管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 重新发布成功 |

---

### 管理后台 API 列表

**页面**：数据大盘（platform-admin/dashboard.html）、企业入驻审核（platform-admin/audit.html）、企业租户管理（platform-admin/tenant.html）、商机内容管理（platform-admin/opportunity-manage.html）、动态内容管理（platform-admin/feeds-manage.html）、基础数据字典（platform-admin/master-data.html）、账号与角色权限（platform-admin/rbac.html）、系统设置（platform-admin/settings.html）

---

#### 3.8.1 Header 导航栏

| #   | 页面功能     | 前端函数                           | API                               | 方法  | 请求参数                | 说明                                                                |
| --- | -------- | ------------------------------ | --------------------------------- | :-: | ------------------- | ----------------------------------------------------------------- |
| 1   | 管理员信息    | —                              | `GET /plat-admin/profile`         | GET | —                   | 获取当前管理员基本信息                                                       |
| 2   | 通知下拉（加载） | `toggleNotificationDropdown()` | `GET /msg/notifications/recent`   | GET | `limit`（默认3）        | 需已认证；首次加载获取 `unread_count`（badge）+ `items`（下拉渲染）；点击铃铛直接渲染 `items` |
| 3   | 全部已读     | `markAllRead()`                | `PUT /msg/notifications/read-all` | PUT | —                   | 需已认证；badge隐藏，`unread_count`归零                                     |
| 4   | 查看通知详情   | `goToNotify(id)`               | `GET /msg/notifications`          | GET | `page`, `page_size` | 跳转 `notification.html`分页展示所有通知                                    |

---

#### 3.8.2 数据大盘（dashboard.html）

| #   | 页面功能  | 前端函数 | API                               | 方法  | 请求参数                                                     | 说明                        |
| --- | ----- | ---- | --------------------------------- | :-: | -------------------------------------------------------- | ------------------------- |
| 5   | 统计指标卡 | —    | `GET /plat-admin/dashboard/stats` | GET | —                                                        | 获取入驻企业数、累计商机数、成功撮合数、活跃用户数 |
| 6   | 趋势数据  | —    | `GET /plat-admin/dashboard/trend` | GET | `type` (opportunity/enterprise/deal), `period` (天数，默认30) | 获取近30天趋势数据                |

---

#### 3.8.3 企业入驻审核（audit.html）

| #   | 页面功能   | 前端函数                       | API                                              |  方法  | 请求参数                                              | 说明           |
| --- | ------ | -------------------------- | ------------------------------------------------ | :--: | ------------------------------------------------- | ------------ |
| 7   | 待审核Tab | —                          | `GET /plat-admin/audit/enterprise`               | GET  | `page`, `page_size`, `status=PENDING`, `keyword`  | 获取待审核企业列表    |
| 8   | 已通过Tab | —                          | `GET /plat-admin/audit/enterprise`               | GET  | `page`, `page_size`, `status=VERIFIED`, `keyword` | 获取已通过审核企业列表  |
| 9   | 已驳回Tab | —                          | `GET /plat-admin/audit/enterprise`               | GET  | `page`, `page_size`, `status=REJECTED`, `keyword` | 获取已驳回企业列表    |
| 10  | 打开审核弹窗 | `showAuditModal()`         | —                                                |  —   | —                                                 | 纯前端：加载审核弹窗   |
| 11  | 审核通过   | `handleApprove()`          | `POST /plat-admin/audit/enterprise/{id}/approve` | POST | —                                                 | 审核通过，发送站内通知  |
| 12  | 审核驳回   | `handleReject()`           | `POST /plat-admin/audit/enterprise/{id}/reject`  | POST | `reason`                                          | 审核驳回，发送站内通知  |
| 13  | 关闭弹窗   | `closeModal('auditModal')` | —                                                |  —   | —                                                 | 纯前端：点击X或遮罩关闭 |

---

#### 3.8.4 企业租户管理（tenant.html）

| #   | 页面功能    | 前端函数                        | API                                                    |  方法  | 请求参数                                          | 说明                |
| --- | ------- | --------------------------- | ------------------------------------------------------ | :--: | --------------------------------------------- | ----------------- |
| 14  | 企业列表    | —                           | `GET /plat-admin/tenant/enterprise`                    | GET  | `page`, `page_size`, `keyword`, `status`      | 获取企业列表，支持关键词和状态筛选 |
| 15  | 启用/禁用企业 | `handleToggleStatus()`      | `PUT /plat-admin/tenant/enterprise/{id}/toggle-status` | PUT  | —                                             | 启用或禁用企业账号         |
| 16  | 打开成员弹窗  | `showMemberModal()`         | —                                                      |  —   | —                                             | 纯前端：加载成员管理弹窗      |
| 17  | 成员列表    | —                           | `GET /plat-admin/tenant/enterprise/{id}/member`        | GET  | `page`, `page_size`                           | 获取企业成员列表          |
| 18  | 新增成员    | `handleAddMember()`         | `POST /plat-admin/tenant/enterprise/{id}/member`       | POST | `phone`, `real_name`, `position`, `role_code` | 添加企业成员，需已注册用户     |
| 19  | 编辑成员    | `handleEditMember()`        | `PUT /plat-admin/tenant/member/{id}`                   | PUT  | `name`, `position`, `role_code`, `is_active`  | 编辑成员信息            |
| 20  | 重置密码    | `handleResetPassword()`     | `POST /plat-admin/tenant/member/{id}/reset-password`   | POST | —                                             | 重置密码为手机号后6位，线下通知  |
| 21  | 解绑成员    | `handleUnbind()`            | `POST /plat-admin/tenant/member/{id}/unbind`           | POST | —                                             | 解绑后恢复游客身份(guest)  |
| 22  | 关闭弹窗    | `closeModal('memberModal')` | —                                                      |  —   | —                                             | 纯前端：点击X或遮罩关闭      |

---

#### 3.8.5 商机内容管理（opportunity-manage.html）

| #   | 页面功能   | 前端函数                | API                                                | 方法  | 请求参数                                             | 说明              |
| --- | ------ | ------------------- | -------------------------------------------------- | :-: | ------------------------------------------------ | --------------- |
| 22  | 商机列表   | —                   | `GET /plat-admin/content/opportunity`              | GET | `page`, `page_size`, `keyword`, `type`, `status` | 获取商机列表，含类型和状态筛选 |
| 23  | 打开查看弹窗 | `handleView(id)`    | `GET /plat-admin/content/opportunity/{id}`         | GET | —                                                | 获取商机详情          |
| 24  | 打开下架弹窗 | `handleOffline(id)` | —                                                  |  —  | —                                                | 纯前端：加载下架原因填写弹窗  |
| 25  | 确认下架   | `confirmOffline()`  | `PUT /plat-admin/content/opportunity/{id}/offline` | PUT | `reason`                                         | 填写下架原因，发送站内通知   |
| 26  | 关闭弹窗   | `closeModal(id)`    | —                                                  |  —  | —                                                | 纯前端：点击X或遮罩关闭    |

---

#### 3.8.6 动态内容管理（feeds-manage.html）

| #   | 页面功能    | 前端函数                  | API                                  | 方法  | 请求参数                            | 说明              |
| --- | ------- | --------------------- | ------------------------------------ | :--: | --------------------------------- | --------------- |
| 27  | 动态列表    | —                       | `GET /plat-admin/content/feed`        | GET  | `page`, `page_size`, `keyword`, `status` | 获取动态列表，含状态筛选 |
| 28  | 打开查看弹窗  | `handleView(id)`       | `GET /plat-admin/content/feed/{id}`   | GET  | —                                  | 获取动态详情           |
| 29  | 打开下架弹窗  | `handleOffline(id)`    | —                                    |  —   | —                                  | 纯前端：加载下架原因填写弹窗   |
| 30  | 确认下架    | `confirmOffline()`     | `PUT /plat-admin/content/feed/{id}/offline` | PUT  | `reason`                            | 填写下架原因，发送站内通知    |
| 31  | 关闭弹窗    | `closeModal(id)`       | —                                    |  —   | —                                  | 纯前端：点击X或遮罩关闭      |

---

#### 3.8.7 基础数据字典（master-data.html）

| #   | 页面功能     | 前端函数                        | API                                              |  方法  | 请求参数                                                  | 说明                         |
| --- | -------- | --------------------------- | ------------------------------------------------ | :--: | ----------------------------------------------------- | -------------------------- |
| 32  | Tab切换    | `switchTab(tab)`            | —                                                |  —   | —                                                     | 纯前端：切换行业/品类/标签/行政区划Tab     |
| 33  | 字典列表     | —                           | `GET /plat-admin/master-data`                    | GET  | `category`, `page`, `page_size`                       | 获取字典列表                     |
| 34  | 打开新增弹窗   | `openAddModal()`            | —                                                |  —   | —                                                     | 纯前端：加载新增弹窗                 |
| 35  | 打开新增子项弹窗 | `openAddSubModal(parentId)` | —                                                |  —   | —                                                     | 纯前端：加载新增子项弹窗（树形结构）         |
| 36  | 确认新增     | `confirmAdd()`              | `POST /plat-admin/master-data`                   | POST | `category`, `name`, `code`, `parent_id`, `sort_order` | 新增字典项                      |
| 37  | 打开编辑弹窗   | `openEditModal(id)`         | —                                                |  —   | —                                                     | 纯前端：加载编辑弹窗                 |
| 38  | 确认编辑     | `confirmEdit()`             | `PUT /plat-admin/master-data/{id}`               | PUT  | `name`, `code`, `parent_id`, `sort_order`             | 更新字典项，parent_id=0为顶级，>0为子项 |
| 39  | 启用/禁用    | `toggleStatus(id)`          | `PUT /plat-admin/master-data/{id}/toggle-status` | PUT  | —                                                     | 切换启用/禁用状态（不支持物理删除）         |
| 40  | 关闭弹窗     | `closeModal(id)`            | —                                                |  —   | —                                                     | 纯前端：点击X或遮罩关闭               |

---

#### 3.8.8 账号与角色权限（rbac.html）

| #   | 页面功能   | 前端函数                      | API                                     | 方法  | 请求参数          | 说明                 |
| --- | ------ | ------------------------- | --------------------------------------- | :-: | ------------- | ------------------ |
| 41  | 角色列表   | —                         | `GET /plat-admin/role`                  | GET | —             | 获取角色列表             |
| 42  | 选择角色   | `selectRole(roleId)`      | `GET /plat-admin/role/{id}`             | GET | —             | 获取角色权限详情           |
| 43  | 渲染权限面板 | `renderPermissionPanel()` | —                                       |  —  | —             | 纯前端：根据选中角色渲染权限矩阵展示 |
| 44  | 保存权限配置 | —                         | `PUT /plat-admin/role/{id}/permissions` | PUT | `permissions` | 保存角色权限配置           |
| 45  | 新增角色   | —                         | —                                       |  —  | —             | **暂不支持**，预留        |

---

#### 3.8.9 系统设置（settings.html）

| #   | 页面功能    | 前端函数            | API                        | 方法  | 请求参数            | 说明              |
| --- | ------- | ---------------- | -------------------------- | :--: | --------------- | --------------- |
| 46  | 获取设置    | —                  | `GET /plat-admin/settings` | GET  | `key` (可选)       | 获取平台设置          |
| 47  | 保存设置    | `saveSettings()` | `PUT /plat-admin/settings` | PUT  | `key`, `value`    | 更新平台设置          |
| 48  | 重置     | —                  | —                          |  —   | —               | 纯前端：重置表单到初始值    |

---

### 3.9 平台端管理接口

#### GET /api/v1/plat-admin/profile（管理员信息）
**权限**: 平台运营/超级管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 管理员ID |
| name | string | 姓名 |
| role_code | string | 角色码 |
| role_name | string | 角色名称 |

---

#### GET /api/v1/plat-admin/notification（通知列表）
**权限**: 平台运营/超级管理员

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码 |
| page_size | int | N | 每页条数 |
| is_read | bool | N | 已读状态筛选 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总数 |
| items | array | 通知列表 |

---

#### POST /api/v1/plat-admin/notification/read-all（全部已读）
**权限**: 平台运营/超级管理员

**响应字段**: 无

---

#### GET /api/v1/plat-admin/dashboard/stats（统计指标）
**权限**: 平台运营/超级管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| enterprise_count | int | 入驻企业数 |
| opportunity_count | int | 累计商机数 |
| deal_count | int | 成功撮合数 |
| active_user_count | int | 活跃校友数 |
| pending_audit_count | int | 待审核数 |
| enterprise_trend | string | 入驻企业较上月趋势，如 "+12%" |
| opportunity_trend | string | 累计商机较上月趋势，如 "+8%" |
| deal_trend | string | 成功撮合较上月趋势，如 "+23%" |
| active_user_trend | string | 活跃用户较上月趋势，如 "-3%" |

---

#### GET /api/v1/plat-admin/dashboard/trend（趋势数据）
**权限**: 平台运营/超级管理员

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | N | opportunity/enterprise/deal，默认全部 |
| period | int | N | 天数，默认30 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| opportunity_trend | array | 每日商机数量 `[{date, count}]` |
| enterprise_trend | array | 每日企业入驻数量 |
| deal_trend | array | 每日撮合数量 |

---

#### GET /api/v1/plat-admin/audit/enterprise（企业审核列表）
**权限**: 平台运营

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码 |
| status | string | N | PENDING/VERIFIED/REJECTED |
| keyword | string | N | 关键词 |

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
| industry_name | string | 一级行业名称 |
| sub_industry_name | string | 二级行业名称 |
| province_name | string | 省份名称 |
| region_name | string | 城市名称 |
| applicant_name | string | 申请人姓名 |
| applicant_position | string | 申请人职务 |
| contact_phone | string | 联系方式 |
| legal_representative | string | 法人姓名 |
| business_license_url | string | 营业执照URL |
| attachment_urls | array | 附件URL列表 |
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
**权限**: 平台运营/超级管理员

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码 |
| keyword | string | N | 企业名称关键词 |
| status | string | N | is_active状态 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总数 |
| items | array | 企业列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 企业ID |
| name | string | 企业名称 |
| logo_url | string | Logo URL |
| industry_name | string | 一级行业名称 |
| sub_industry_name | string | 二级行业名称 |
| province_name | string | 省份名称 |
| region_name | string | 城市名称 |
| auth_status | string | 认证状态 |
| admin_name | string | 企业管理员姓名 |
| member_count | int | 成员数量 |
| created_at | datetime | 入驻时间 |
| is_active | bool | 账号状态 |

---

#### PUT /api/v1/plat-admin/tenant/enterprise/{id}/toggle-status（启用/停用企业）
**权限**: 平台运营/超级管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 企业ID |
| is_active | bool | 当前状态 |

---

#### GET /api/v1/plat-admin/tenant/enterprise/{id}/member（企业成员列表）
**权限**: 平台运营/超级管理员

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码 |
| page_size | int | N | 每页条数 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总数 |
| items | array | 成员列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| real_name | string | 真实姓名 |
| phone | string | 手机号 |
| position | string | 职位/职级 |
| role_code | string | guest/employee/admin |
| is_active | bool | 是否启用 |
| created_at | datetime | 加入时间 |

---

#### POST /api/v1/plat-admin/tenant/enterprise/{id}/member（新增成员）
**权限**: 平台运营/超级管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | Y | 手机号（需已注册用户） |
| real_name | string | Y | 真实姓名 |
| position | string | N | 职位/职级 |
| role_code | string | N | guest/employee/admin，默认employee |

**响应字段**: 新增的成员信息

**说明**: 平台管理员可为企业新增成员，手机号需已注册平台账号。

---

#### PUT /api/v1/plat-admin/tenant/member/{id}（编辑成员）
**权限**: 平台运营/超级管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | N | 姓名 |
| position | string | N | 职位 |
| role_code | string | N | guest/employee/admin |
| is_active | bool | N | 是否启用 |

**响应字段**: 更新后的成员信息

---

#### POST /api/v1/plat-admin/tenant/member/{id}/reset-password（重置密码）
**权限**: 平台运营/超级管理员

**说明**: 重置为手机号后6位，由管理员线下通知用户。

**响应字段**: 无

---

#### POST /api/v1/plat-admin/tenant/member/{id}/unbind（解绑成员）
**权限**: 平台运营/超级管理员

**说明**: 解绑后该成员恢复为游客身份（role_code=guest），如账号原为停用则恢复为正常。

**响应字段**: 无

---

#### GET /api/v1/plat-admin/content/opportunity（商机列表）
**权限**: 平台运营

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码 |
| page_size | int | N | 每页条数 |
| keyword | string | N | 关键词 |
| type | string | N | buy/supply |
| status | string | N | ACTIVE/OFFLINE |

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
| industry_name | string | 一级行业名称 |
| sub_industry_name | string | 二级行业名称 |
| category_name | string | 品类名称 |
| province_name | string | 所属省份名称 |
| region_name | string | 市名称 |
| tags | array | 标签列表 |
| status | string | ACTIVE/OFFLINE |
| view_count | int | 浏览量 |
| created_at | datetime | 发布时间 |

---

#### GET /api/v1/plat-admin/content/opportunity/{id}（商机详情）
**权限**: 平台运营

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
| industry_id | int | 一级行业ID |
| industry_name | string | 一级行业名称 |
| sub_industry_id | int | 二级行业ID |
| sub_industry_name | string | 二级行业名称 |
| category_id | int | 品类ID |
| category_name | string | 品类名称 |
| region_id | int | 市ID |
| province_id | int | 省份ID |
| province_name | string | 所属省份名称 |
| region_name | string | 市名称 |
| tags | array | 标签列表 |
| status | string | ACTIVE/OFFLINE |
| view_count | int | 浏览量 |
| contact_name | string | 联系人 |
| contact_phone | string | 联系电话 |
| contact_wechat | string | 微信 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

---

#### PUT /api/v1/plat-admin/content/opportunity/{id}/offline（强制下架）
**权限**: 平台运营

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | Y | 下架原因 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 商机ID |
| status | string | OFFLINE |

---

#### GET /api/v1/plat-admin/content/feed（动态列表）
**权限**: 平台运营

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码 |
| page_size | int | N | 每页条数 |
| keyword | string | N | 关键词 |
| status | string | N | ACTIVE/OFFLINE |

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
| publisher_role | string | 发布人职级 |
| enterprise_id | int | 企业ID |
| enterprise_name | string | 企业名称 |
| enterprise_logo | string | 企业Logo URL |
| status | string | ACTIVE/OFFLINE |
| view_count | int | 浏览量 |
| created_at | datetime | 发布时间 |

---

#### GET /api/v1/plat-admin/content/feed/{id}（动态详情）
**权限**: 平台运营

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 动态ID |
| content | string | 动态内容 |
| images | array | 图片URL列表 |
| publisher_id | int | 发布人ID |
| publisher_name | string | 发布人姓名 |
| publisher_role | string | 发布人职级 |
| enterprise_id | int | 企业ID |
| enterprise_name | string | 企业名称 |
| enterprise_logo | string | 企业Logo URL |
| status | string | ACTIVE/OFFLINE |
| view_count | int | 浏览量 |
| created_at | datetime | 发布时间 |
| updated_at | datetime | 更新时间 |

---

#### PUT /api/v1/plat-admin/content/feed/{id}/offline（强制下架）
**权限**: 平台运营

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | Y | 下架原因 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 动态ID |
| status | string | OFFLINE |

---

#### GET /api/v1/plat-admin/master-data（字典列表）
**权限**: 平台运营/超级管理员

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
| parent_id | int | N | 父级ID（0或空=顶级，>0=子项） |
| sort_order | int | N | 排序，默认0 |

**判断逻辑**：
- `parent_id = 0` 或不传 → 新增顶级分类（如"智能网联"）
- `parent_id > 0` → 新增子项（如"自动驾驶算法"），parent_id指向父级ID

**说明**：
- `category` 可选值：`industry`（行业分类）、`category`（业务品类）、`tag`（业务标签）、`region`（行政区划）
- 仅行业分类、行政区划支持层级结构
- 业务品类、业务标签为扁平结构，parent_id传0或不传

**响应字段**: 新增的字典项

---

#### PUT /api/v1/plat-admin/master-data/{id}（更新字典项）
**权限**: 超级管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | N | 名称 |
| code | string | N | 编码 |
| parent_id | int | N | 父级ID（0或空=顶级，>0=子项） |
| sort_order | int | N | 排序 |

**判断逻辑**：
- `parent_id = 0` 或不传 → 更新顶级分类（如"智能网联"）
- `parent_id > 0` → 更新子项（如"自动驾驶算法"），parent_id指向父级ID

**说明**：
- 仅行业分类、行政区划支持层级结构（parent_id有效）
- 业务品类、业务标签为扁平结构，parent_id传0或不传
- 支持通过传入不同的parent_id实现跨父级移动（如将某城市从A省移至B省）

---

#### PUT /api/v1/plat-admin/master-data/{id}/toggle-status（启用/禁用）
**权限**: 超级管理员

**说明**: 字典项被业务数据（企业/商机）引用后，**不支持物理删除**，仅可禁用（is_active=false）。

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
| role_code | string | 角色码 |
| description | string | 描述 |

---

#### GET /api/v1/plat-admin/role/{id}（角色权限详情）
**权限**: 超级管理员

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 角色ID |
| name | string | 角色名称 |
| role_code | string | 角色码 |
| permissions | array | 权限码列表 |

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

#### GET /api/v1/plat-admin/settings（获取设置）
**权限**: 超级管理员

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | N | 设置键，不传则返回全部 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| platform_name | string | 平台名称 |
| customer_service_phone | string | 客服热线 |

---

#### PUT /api/v1/plat-admin/settings（更新设置）
**权限**: 超级管理员

**请求字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | Y | 设置键 |
| value | string | Y | 设置值 |

**数据存储**:
- 表名：`platform_settings`
- 结构：`id`, `key`, `value`, `updated_at`
- 支持的 key：`platform_name`, `customer_service_phone`

**响应字段**: 更新后的设置

### 搜索页 API 列表

**页面**：搜索结果（search.html）

| # | 功能 | API | 方法 | 请求参数 | 说明 |
|---|------|-----|:----:|---------|------|
| 1 | 统一搜索 | `/search/all` | GET | `keyword`, `type` (opportunity/enterprise/feed/空), `page`, `page_size` | 需已认证，返回商机/企业/动态三类搜索结果 |

**交互说明**：
- type为空时返回全部三类结果，支持按类型筛选
- 每个类型返回 `total` 总数和 `items` 结果列表
- 商机/企业/动态各自独立分页

---

### 3.10 搜索接口

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

### 消息通知 API 列表

**页面**：通知消息（notification.html），同时作为 Header 组件全局可见

| # | 页面功能 | 前端函数 | API | 方法 | 请求参数 | 说明 |
|---|---------|---------|-----|:----:|---------|------|
| **Header 铃铛组件** | | | | | | |
| 1 | 页面加载获取未读数+最新消息 | `toggleNotificationDropdown()` | `/msg/notifications/recent` | GET | `limit`（默认3） | 需已认证；返回 `unread_count`（badge数字）+ `items`（最新未读列表）；点击铃铛时前端直接渲染 `items` 展示下拉 |
| 2 | 点击单条已读 | — | `/msg/notifications/{id}/read` | PUT | — | 需已认证；点击某条消息后该条变已读，`unread_count` 减1 |
| 3 | 全部已读 | `markAllRead()` | `/msg/notifications/read-all` | PUT | — | 需已认证；点击后 `unread_count` 归零，badge隐藏 |
| **通知消息页** | | | | | | |
| 4 | 通知列表（分页） | — | `/msg/notifications` | GET | `page`, `page_size` | 需已认证，返回所有通知列表 |
| 5 | 查看通知详情 | — | — | — | — | 纯前端跳转，通知消息页展示详情 |

**交互说明**：
- 铃铛badge数字：登录成功后前端调用 `/msg/notifications/recent?limit=3`，取响应中 `unread_count` 显示badge
- 铃铛下拉：前端直接渲染 `items` 数组，无需额外接口调用
- 点击单条消息：前端将该条从"未读"状态变更为"已读"，同时 `unread_count` 减1，并调用 `PUT /msg/notifications/{id}/read` 同步后端
- 点击"全部已读"：badge隐藏，`unread_count` 归零，调用 `PUT /msg/notifications/read-all`
- 点击"查看全部通知"：跳转 `notification.html`，调用 `GET /msg/notifications?page=1&page_size=20`
- 通知类型包括：企业审核结果、商机查看请求、系统通知等

**铃铛数据加载流程**：
```
页面加载（已登录） → GET /msg/notifications/recent?limit=3
                  → 渲染 badge 数字（unread_count）
                  → 用户点击铃铛 → 直接渲染 items 数组到下拉框
                  
用户点击单条 → PUT /msg/notifications/{id}/read
            → 更新本地 unread_count--
            → 更新下拉框该条为已读样式

用户点击"全部已读" → PUT /msg/notifications/read-all
                  → unread_count 归零 → badge隐藏
```

---

### 3.11 消息接口

#### GET /api/v1/msg/notifications/recent（铃铛下拉 - 最新未读消息）
**权限**: 已认证

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | N | 返回条数，默认3条 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| unread_count | int | 未读总数（供铃铛badge使用，页面加载时调用此字段） |
| items | array | 最新未读消息列表（最多limit条，按创建时间倒序） |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 消息ID |
| type | string | AUDIT_APPROVED/AUDIT_REJECTED/CONTACT_RECEIVED/SYSTEM |
| title | string | 标题 |
| content | string | 内容（摘要，前端截断显示） |
| is_read | bool | 是否已读（此接口仅返回未读，固定为false） |
| related_type | string | 关联对象类型 |
| related_id | int | 关联对象ID |
| created_at | datetime | 创建时间 |

**使用场景**：
- 页面加载时调用，获取 `unread_count` 显示铃铛badge，同时获取最新 `items` 渲染下拉框
- 无需分两次调用，下拉框展示由前端纯JS渲染 `items` 数组

---

#### GET /api/v1/msg/notifications（通知列表）
**权限**: 已认证

**查询参数**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | N | 页码 |
| page_size | int | N | 每页条数，默认20 |

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总数 |
| unread_count | int | 未读数 |
| items | array | 通知列表 |

**items元素**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 消息ID |
| type | string | AUDIT_APPROVED/AUDIT_REJECTED/CONTACT_RECEIVED/SYSTEM |
| title | string | 标题 |
| content | string | 内容 |
| is_read | bool | 是否已读 |
| related_type | string | 关联对象类型 |
| related_id | int | 关联对象ID |
| created_at | datetime | 创建时间 |

---

#### PUT /api/v1/msg/notifications/{id}/read（标记已读）
**权限**: 已认证

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 消息ID |
| is_read | bool | 已读 |

---

#### PUT /api/v1/msg/notifications/read-all（全部已读）
**权限**: 已认证

**响应字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| unread_count | int | 剩余未读数 |

---

### 3.12 API 汇总

| 模块标识       |  接口数   | 路径前缀                | 说明                           |
| ---------- | :----: | ------------------- | ---------------------------- |
| auth       |   8    | /api/v1/auth/       | 认证相关（登录/注册/登出/刷新/密码）         |
| public     |   1    | /api/v1/public/     | 公开统计                         |
| ent        |   9    | /api/v1/ent/        | 企业名录（列表/详情/认领/入驻/认证）         |
| opp        |   7    | /api/v1/opp/        | 商机广场（列表/详情/发布/联系/推荐）         |
| feed       |   6    | /api/v1/feed/       | 校友圈（列表/详情/发布/最新动态）           |
| ent-admin  |   10   | /api/v1/ent-admin/  | 企业工作台（企业信息/员工/商机/动态/联系记录）    |
| plat-admin |   48   | /api/v1/plat-admin/ | 管理后台（数据中心/审核/租户/内容/字典/权限/设置） |
| search     |   1    | /api/v1/search/     | 全局搜索                         |
| msg        |   3    | /api/v1/msg/        | 消息通知                         |
| **合计**     | **93** | -                   |                              |

---

## 4. 核心功能设计

### 4.1 认证流程设计

**短信验证码登录流程：**
```
用户输入手机号，点击"获取验证码"
         │
         ▼
  后端校验：同一手机号每天最多生成10次（登录）/ 5次（重置密码）
         │
         ▼
  生成6位数字验证码，写入 auth_sms_code 表（有效期5分钟）
         │
         ▼
  调用短信服务商 API 发送验证码
         │
         ▼
  用户输入验证码，前端提交登录请求
         │
         ▼
  后端验证：code匹配 + 未使用 + 未过期 + type匹配
         │
         ▼
  标记验证码已使用（used_at = now）
         │
         ▼
  查询/创建 Django User（username = 手机号），返回 JWT Token
```

**Token 机制（SimpleJWT）：**
- access_token 有效期：**2小时**
- refresh_token 有效期：**7天**
- **ROTATE_REFRESH_TOKENS = True**：每次刷新时生成新的 access_token 和 refresh_token，旧的 refresh_token 自动加入黑名单
- 前端自动在 access_token 过期前（提前5分钟）调用刷新接口

**登出流程：**
```
用户点击"退出登录"
         │
         ▼
  前端：删除 localStorage 中的 access_token 和 refresh_token
         │
         ▼
  后端：将当前 refresh_token 加入黑名单
         │
         ▼
  返回成功，用户跳转登录页
```

**前端 Token 自动刷新（Axios 拦截器）：**
```javascript
// 请求拦截器：携带 token
config.headers.Authorization = `Bearer ${localStorage.access_token}`

// 响应拦截器：401 时自动刷新
if (error.response?.status === 401) {
    try {
        await userStore.refreshToken()  // 自动用 refresh_token 换新 token
        return request(error.config)    // 重试刚才的请求
    } catch {
        userStore.logout()              // refresh_token 也失效了，跳转登录
        router.push('/login')
    }
}
```

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
 ent_user_profile.position = plat_audit_record.applicant_position（职务同步）
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

**两层权限体系：**

- **第一层**：导航块可见性（前端控制）
- **第二层**：功能操作权限（API拦截）

---

#### 第一层：导航块可见性

| 导航块                   | 可见角色                          | 说明    |
| --------------------- | ----------------------------- | ----- |
| 第一块（首页/商机广场/企业名录/校友圈） | 所有人（游客 + 已登录用户）               | 公开内容  |
| 第二块（企业工作台）            | enterprise_admin、employee     | 需绑定企业 |
| 第三块（管理后台）             | platform_operator、super_admin | 平台侧   |

**前端导航控制示例：**

```vue
<!-- 公共导航：始终显示 -->
<el-menu>
  <el-menu-item index="/">首页</el-menu-item>
  <el-menu-item index="/opportunity">商机广场</el-menu-item>
  <el-menu-item index="/enterprise">企业名录</el-menu-item>
  <el-menu-item index="/feed">校友圈</el-menu-item>
</el-menu>

<!-- 企业工作台入口：仅企业用户可见 -->
<el-sub-menu v-if="isEnterpriseUser" index="enterprise">
  <template #title>企业工作台</template>
  <el-menu-item index="/enterprise-admin/info">企业信息</el-menu-item>
  <el-menu-item index="/enterprise-admin/opportunity">商机管理</el-menu-item>
  <el-menu-item index="/enterprise-admin/employee">员工管理</el-menu-item>
</el-sub-menu>

<!-- 管理后台入口：仅平台用户可见 -->
<el-sub-menu v-if="isPlatformUser" index="platform">
  <template #title>管理后台</template>
  <el-menu-item index="/platform-admin/dashboard">数据大盘</el-menu-item>
  <el-menu-item index="/platform-admin/audit">企业审核</el-menu-item>
  <el-menu-item index="/platform-admin/tenant">企业(租户)管理</el-menu-item>
  <el-menu-item index="/platform-admin/opportunity-manage">商机内容管理</el-menu-item>
  <el-menu-item index="/platform-admin/feeds-manage">动态内容管理</el-menu-item>
  <el-menu-item index="/platform-admin/master-data">基础数据字典</el-menu-item>
  <el-menu-item index="/platform-admin/rbac">账号与角色权限</el-menu-item>
  <el-menu-item index="/platform-admin/settings">系统设置</el-menu-item>
</el-sub-menu>
```

---

#### 第二层：功能权限矩阵

**详细权限配置见 3.8.8 账号与角色权限页面。**

权限配置数据通过 `PUT /api/v1/plat-admin/role/{id}/permissions` 保存至数据库，通过 `GET /api/v1/plat-admin/role/{id}` 获取。

**权限码说明**：

| 权限码 | 说明 | 归属模块 |
|--------|------|---------|
| `xlt.*` | 校链通系统公开模块权限 | 校链通 |
| `ent.*` | 企业工作台模块权限 | 企业工作台 |
| `admin.*` | 管理后台模块权限 | 管理后台 |
| `super_admin` | 超级管理员专属 | 系统级 |
| `platform_operator` | 平台运营角色 | 系统级 |

**数据库存储**：

| 表名 | 说明 |
|------|------|
| `auth_group` | 角色组（对应5种业务角色） |
| `auth_permission` | Django权限表（存储权限码如 `xlt.opportunity.list`） |
| `auth_group_permissions` | 角色-权限多对多关联 |
| `user_user_permissions` | 用户-权限多对多关联（备用） |

**权限码格式**：`{子系统}.{模块}.{操作}`

示例：
- `xlt.opportunity.list` - 商机列表查看
- `xlt.opportunity.publish` - 发布商机
- `ent.employee.manage` - 员工管理
- `admin.audit.view` - 审核查看
- `admin.rbac.manage` - 账号权限管理（仅超管）

**前端权限校验**：

```javascript
// usePermission.ts
export function usePermission() {
  const roleCode = userStore.roleCode
  const permissions = userStore.permissions // 后端返回的权限码数组

  const can = (perm) => permissions.includes(perm)

  return {
    can,
    isSuperAdmin: roleCode === 'super_admin',
    isPlatformOperator: roleCode === 'platform_operator',
    canPublish: can('xlt.opportunity.publish'),
    // ...
  }
}
```

**后端API拦截示例**：

```python
# DRF Permission Class
class HasPermission(BasePermission):
    def has_permission(self, request, view):
        required_perm = view.required_permission  # 如 'admin.rbac.manage'
        if request.user.role_code == 'super_admin':
            return True
        return request.user.has_perm(required_perm)
```

---

#### API拦截校验

**校验原则**：页面上所有功能按钮都展示，点击时后端API校验权限，无权限则返回错误，前端提示用户。

```python
# 发布商机 API 校验示例
class OpportunityPublishView(APIView):
    def post(self, request):
        # 1. 登录校验
        if not request.user.is_authenticated:
            return Response({'error': '请先登录'}, status=401)

        # 2. 角色校验（enterprise_admin 或 employee）
        profile = request.user.ent_user_profile
        if not profile or not profile.enterprise_id:
            return Response({'error': '请先认领或创建企业，或联系企业管理员'}, status=403)
        if request.user.groups.filter(name='guest').exists():
            return Response({'error': '您暂无权限执行此操作'}, status=403)

        # 3. 企业认证状态校验
        enterprise = Enterprise.objects.get(pk=profile.enterprise_id)
        if enterprise.auth_status != 'VERIFIED':
            return Response({'error': '企业尚未认证通过'}, status=403)

        # 4. 业务逻辑...
```

---

#### 数据权限（QuerySet固化）

企业用户只能操作自己企业的数据，在数据库查询层固化：

```python
class OpportunityQuerySet(models.QuerySet):
    def for_enterprise(self, user):
        """仅返回用户所属企业的商机"""
        profile = user.ent_user_profile
        if not profile or not profile.enterprise_id:
            return self.none()
        return self.filter(enterprise_id=profile.enterprise_id)
```

> **说明**：employee 被赋予企业工作台功能后，可管理本企业下所有商机和动态（非仅自己创建）。

#### 企业数据权限过滤逻辑（JWT认证流程）

企业工作台API（如 `GET /ent-admin/employees`、`GET /ent-admin/my-opportunities`）无需前端传递 `enterprise_id` 参数，后端通过JWT Token自动关联企业：

**认证流程：**

```
1. 用户登录
   前端: POST /api/v1/auth/login { phone, password }
   后端: 验证手机号+密码 → 查询用户表获取 user_id → 返回 JWT Token（包含 user_id）

2. 前端请求企业数据
   Header: Authorization: Bearer <access_token>

3. 后端自动关联企业
   解析 Token 获取 user_id
        ↓
   查询 ent_user_profile 表获取该用户的 enterprise_id
        ↓
   自动过滤：仅返回该 enterprise_id 下的数据
```

**代码示例：**

```python
# GET /ent-admin/employees（员工管理）
class EmployeeListView(APIView):
    def get(self, request):
        # 1. 登录校验（DRF 自动解析 JWT）
        if not request.user.is_authenticated:
            return Response({'error': '请先登录'}, status=401)

        # 2. 自动获取当前用户的企业ID（无需前端传参）
        profile = request.user.ent_user_profile
        if not profile or not profile.enterprise_id:
            return Response({'error': '您暂未绑定企业'}, status=403)

        # 3. 查询该企业下的所有员工（自动过滤）
        employees = EntEmployee.objects.filter(
            enterprise_id=profile.enterprise_id
        ).order_by('-created_at')

        # 4. 返回数据
        serializer = EmployeeSerializer(employees, many=True)
        return Response({
            'total': employees.count(),
            'items': serializer.data
        })
```

**前端调用示例：**

```typescript
// 员工管理 - 页面加载时调用
const loadEmployees = async () => {
  const res = await axios.get('/api/v1/ent-admin/employees', {
    // 无需传 enterprise_id，后端自动关联
    headers: { Authorization: `Bearer ${token}` }
  })
  employeeList.value = res.data.items
}

// 商机管理 - 页面加载时调用
const loadMyOpportunities = async () => {
  const res = await axios.get('/api/v1/ent-admin/my-opportunities', {
    params: { page: 1, page_size: 10 },
    headers: { Authorization: `Bearer ${token}` }
  })
  opportunityList.value = res.data.items
}
```

**数据隔离保证：**

| 步骤 | 说明 |
|------|------|
| Token 解析 | 后端解析 JWT 获取 user_id（SR-0004: Token必须设置过期时间） |
| 企业关联 | 通过 user_id 查询 ent_user_profile 表获取 enterprise_id |
| 数据过滤 | 所有企业数据查询强制附加 `enterprise_id` 过滤条件 |
| 权限校验 | API 层校验用户是否属于该企业（防止横向越权） |

---

#### DRF Permission Class

```python
class IsPlatformUser(BasePermission):
    """平台用户：platform_operator 或 super_admin"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(
            name__in=['platform_operator', 'super_admin']
        ).exists()

class IsEnterpriseUser(BasePermission):
    """企业用户：enterprise_admin 或 employee"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(
            name__in=['enterprise_admin', 'employee']
        ).exists()

class IsSuperAdmin(BasePermission):
    """超级管理员"""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
```

---

#### usePermission（简化版）

```typescript
export function usePermission() {
  const userStore = useUserStore()

  const isAuthenticated = computed(() => !!userStore.token)
  const roleCode = computed(() => userStore.roleCode)

  // 是否平台用户（可见管理后台）
  const isPlatformUser = computed(() =>
    ['super_admin', 'platform_operator'].includes(roleCode.value)
  )

  // 是否企业用户（可见企业工作台）
  const isEnterpriseUser = computed(() =>
    ['enterprise_admin', 'employee'].includes(roleCode.value)
  )

  // 是否已认证企业（可发布商机）
  const canPublish = computed(() => {
    if (!userStore.profile?.enterprise_id) return false
    return userStore.profile?.enterprise?.auth_status === 'VERIFIED'
  })

  return { isAuthenticated, roleCode, isPlatformUser, isEnterpriseUser, canPublish }
}
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

  // 平台角色（对应 auth.Group）
  const isPlatformRole = computed(() =>
    ['super_admin', 'platform_operator'].includes(userStore.roleCode)
  )

  // 企业角色（对应 auth.Group）
  const isEnterpriseRole = computed(() =>
    ['enterprise_admin', 'employee', 'guest'].includes(userStore.roleCode)
  )

  // 超级管理员
  const isSuperAdmin = computed(() => userStore.roleCode === 'super_admin')

  // 企业管理员
  const isEnterpriseAdmin = computed(() => userStore.roleCode === 'enterprise_admin')

  // 普通员工
  const isEmployee = computed(() => userStore.roleCode === 'employee')

  // 来宾
  const isGuest = computed(() => userStore.roleCode === 'guest')

  // 可发布（需已认证企业）
  const canPublish = computed(() => {
    if (!userStore.profile?.enterprise_id) return false
    return userStore.profile?.enterprise?.auth_status === 'VERIFIED'
  })

  // 角色码校验
  const hasRole = (roleCodes: string[]) => {
    return roleCodes.includes(userStore.roleCode)
  }

  // 细粒度权限码校验（需后端返回用户权限码列表）
  const hasPermission = (permissionCode: string) => {
    return userStore.permissions?.includes(permissionCode) ?? false
  }

  return {
    isAuthenticated,
    isPlatformRole,
    isEnterpriseRole,
    isSuperAdmin,
    isEnterpriseAdmin,
    isEmployee,
    isGuest,
    canPublish,
    hasRole,
    hasPermission
  }
}
```

**Vue Router 路由级权限配置示例：**

```typescript
// 平台管理员路由
{
  path: '/platform-admin',
  component: () => import('@/views/PlatformAdmin/index.vue'),
  meta: { requiresAuth: true, platformRequired: true },
  children: [
    {
      path: 'dashboard',
      component: () => import('@/views/PlatformAdmin/dashboard.vue'),
      meta: { requiresAuth: true, platformRequired: true, permission: 'dashboard_view' }
    },
    {
      path: 'audit',
      component: () => import('@/views/PlatformAdmin/audit.vue'),
      meta: { requiresAuth: true, platformRequired: true, permission: 'enterprise_audit_view' }
    },
    // ...
  ]
}

// 企业管理员/员工路由
{
  path: '/enterprise-admin',
  component: () => import('@/views/EnterpriseAdmin/index.vue'),
  meta: { requiresAuth: true, enterpriseRequired: true },
  children: [
    {
      path: 'opportunity',
      component: () => import('@/views/EnterpriseAdmin/my-opportunity.vue'),
      meta: {
        requiresAuth: true,
        enterpriseRequired: true,
        permission: 'opportunity_view',
        enterpriseAdminOnly: false  // 员工也可访问
      }
    },
  ]
}
```

**路由守卫中的权限校验逻辑：**

```typescript
// router.beforeEach
router.beforeEach((to, from, next) => {
  const { isAuthenticated, hasPermission } = usePermission()
  const userStore = useUserStore()

  // 必须登录
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return next('/login')
  }

  // 平台页面校验
  if (to.meta.platformRequired) {
    if (!['super_admin', 'platform_operator'].includes(userStore.roleCode)) {
      return next('/unauthorized')
    }
    if (to.meta.permission && !hasPermission(to.meta.permission)) {
      return next('/unauthorized')
    }
  }

  // 企业页面校验
  if (to.meta.enterpriseRequired) {
    if (!['enterprise_admin', 'employee', 'guest'].includes(userStore.roleCode)) {
      return next('/unauthorized')
    }
    if (to.meta.permission && !hasPermission(to.meta.permission)) {
      return next('/unauthorized')
    }
  }

  next()
})
```

### 5.5 功能页面设计

**说明**：详细页面设计见 `docs/prototype/` 目录下的 HTML 原型。前端开发须严格按照原型实现页面布局、交互逻辑和 API 调用。

#### 5.5.1 前台页面原型

| 页面 | 原型文件 | 说明 |
|------|---------|------|
| 首页 | `prototype/index.html` | 全局导航、数据展示、智能推荐、企业动态 |
| 登录页 | `prototype/login.html` | 短信登录、密码登录 |
| 注册页 | `prototype/register.html` | 用户注册流程 |
| 宣传页 | `prototype/index.html` | 品牌展示、统计数据、二维码入口 |
| 企业名录 | `prototype/enterprise.html` | 企业列表、筛选、详情抽屉 |
| 商机广场 | `prototype/opportunity.html` | 商机列表、筛选、发布、联系方式 |
| 校友圈 | `prototype/feeds.html` | 动态列表、发布动态 |
| 通知消息 | `prototype/notification.html` | 消息列表、已读/全部已读 |
| 搜索结果 | `prototype/search.html` | 全局搜索结果 |

#### 5.5.2 企业工作台原型

| 页面 | 原型文件 | 说明 |
|------|---------|------|
| 企业信息 | `enterprise-admin/info.html` | 企业信息查看/编辑 |
| 员工管理 | `enterprise-admin/employee.html` | 员工列表、新增、编辑、停用、重置密码、解绑 |
| 商机管理 | `enterprise-admin/opportunity.html` | 本企业商机列表、编辑、删除 |
| 动态管理 | `enterprise-admin/feeds.html` | 本企业动态列表、编辑、删除 |
| 联系记录 | `enterprise-admin/contact-records.html` | 联系记录列表 |

#### 5.5.3 管理后台原型

| 页面 | 原型文件 | 说明 |
|------|---------|------|
| 数据大盘 | `platform-admin/dashboard.html` | 统计卡片、趋势图表、通知下拉 |
| 企业审核 | `platform-admin/audit.html` | 待审核列表、审核详情、Tab切换（全部/待审核/已通过/已驳回） |
| 企业租户管理 | `platform-admin/tenant.html` | 企业列表、启用/禁用、成员管理、新增/编辑/解绑 |
| 商机内容管理 | `platform-admin/opportunity-manage.html` | 商机列表、类型/状态筛选、查看详情、强制下架 |
| 动态内容管理 | `platform-admin/feeds-manage.html` | 动态列表、状态筛选、查看详情、下架 |
| 基础数据字典 | `platform-admin/master-data.html` | Tab切换（行业/品类/标签/地区）、树形结构、新增/编辑/启用禁用 |
| 账号与角色权限 | `platform-admin/rbac.html` | 角色列表、权限矩阵、API级别配置 |
| 系统设置 | `platform-admin/settings.html` | 平台名称、客服热线 |

#### 5.5.4 前端开发规范

1. **页面实现**：严格按原型 HTML 实现，不得随意修改布局和样式
2. **交互逻辑**：按原型中定义的 JS 函数实现，包括弹窗、表单提交、状态切换等
3. **API 调用**：按 3.8.x 页面功能-API对照表调用，对应原型中的 API 注释
4. **响应处理**：参考原型中 `showToast()` 等提示函数处理接口返回
5. **数据模拟**：原型中已有 mock 数据，前端开发阶段可参考数据格式

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
