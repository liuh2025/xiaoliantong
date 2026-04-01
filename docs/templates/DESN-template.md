---
status: 草稿
---

# 技术设计文档

## {项目名称}

| 文档信息 | 内容 |
|----------|------|
| 项目名称 | {项目名称} |
| 文档版本 | {版本号} |
| 创建日期 | {日期} |
| 关联PRD | [PRD-{项目简称}-{版本号}.md](PRD-{项目简称}-{版本号}.md) |
| 文档状态 | 草稿 |

---

## 修订历史

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| {版本号} | {日期} | - | 初始版本 |

---

## 1. 技术架构

### 1.1 技术栈选型

| 层级 | 技术选型 | 版本 | 说明 |
|------|----------|------|------|
| **前端框架** | {框架} | {版本} | - |
| **UI 组件库** | {组件库} | {版本} | - |
| **状态管理** | {工具} | {版本} | - |
| **HTTP 客户端** | Axios | 1.x | HTTP 请求库 |
| **后端框架** | {框架} | {版本} | - |
| **API 框架** | {框架} | {版本} | RESTful API |
| **数据库** | {数据库} | {版本} | - |
| **认证** | JWT | - | Token 认证 |

### 1.2 后端核心依赖

```
{requirements.txt 内容}
```

### 1.3 前端核心依赖

```json
{
  "dependencies": {
    "{包名}": "{版本}"
  },
  "devDependencies": {
    "{包名}": "{版本}"
  }
}
```

### 1.4 系统架构图

```
┌─────────────────────────────────────────────┐
│                   客户端                      │
│              Vue3 + Element Plus             │
└─────────────────┬───────────────────────────┘
                  │ HTTPS
┌─────────────────▼───────────────────────────┐
│                 Nginx                        │
│         静态文件服务 + API 反向代理            │
└──────┬──────────────────────┬───────────────┘
       │ /api/*               │ /*
┌──────▼──────┐        ┌──────▼──────┐
│   后端服务   │        │  前端静态文件 │
│  Django+DRF │        │             │
└──────┬──────┘        └─────────────┘
       │
┌──────▼──────┐
│    数据库    │
│   {DB}      │
└─────────────┘
```

### 1.5 项目目录结构

```
{项目名称}/
├── backend/                 # 后端代码
│   ├── apps/                # 业务模块
│   ├── config/              # 配置文件
│   ├── requirements.txt
│   └── manage.py
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── views/           # 页面
│   │   ├── components/      # 公共组件
│   │   ├── store/           # 状态管理
│   │   ├── router/          # 路由
│   │   └── utils/           # 工具函数
│   └── package.json
├── docker/                  # 部署配置
│   ├── docker-compose.prod.yml
│   ├── nginx/
│   └── mysql/
└── docs/                    # 文档
```

### 1.6 模块清单
| 模块标识        | 模块名称    | 迭代顺序 | 说明         |
| ----------- | ------- | ---- | ---------- |
| {module-id} | {模块中文名} | 1    | {模块说明}     |
| sys         | 系统管理    | 2    | 用户、角色、权限管理 |

**模块标识用途：**
- worktree 目录名：`.worktrees/{module-id}`
- git 分支名：`feature/{module-id}`
- 数据库表前缀：`{module-id}_`
- API 路径前缀：`/api/{module-id}/`
---

## 2. 模块与数据库设计

### 2.1 数据库命名规范

| 规范项 | 规则 |
|--------|------|
| 表名 | 小写下划线，含模块前缀 |
| 字段名 | 小写下划线 |
| 主键 | id，BIGINT 自增 |
| 时间字段 | created_at、updated_at，DATETIME |
| 软删除 | 不使用软删除，使用物理删除 |
| 字符集 | utf8mb4 |

### 2.2 表前缀说明

> 前缀与 2.1 模块清单中的"模块标识"对应。

| 前缀 | 模块 |
|------|------|
| {module-id}_ | {模块名} |
| sys_ | 系统管理 |

### 2.3 数据表设计

#### {表名}（{中文名}）

| 字段名 | 类型 | 必填 | 唯一 | 默认值 | 说明 |
|--------|------|------|------|--------|------|
| id | BIGINT | Y | Y | 自增 | 主键 |
| created_at | DATETIME | Y | N | NOW() | 创建时间 |
| updated_at | DATETIME | Y | N | NOW() | 更新时间 |
| created_by | VARCHAR(50) | Y | N | - | 创建人 |
| updated_by | VARCHAR(50) | Y | N | - | 更新人 |

### 2.4 版本历史表设计

使用 `django-simple-history` 自动生成历史表，命名规则：`historical_{原表名}`

| 字段名 | 说明 |
|--------|------|
| history_id | 历史记录主键 |
| history_date | 变更时间 |
| history_type | 变更类型（+新增 / ~修改 / -删除） |
| history_user | 操作人 |

### 2.5 ER 图

```
{ER 图 ASCII}
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
    "count": 100,
    "next": "http://...",
    "previous": null,
    "results": []
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

**HTTP 状态码**：

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

### 3.2 认证接口

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | /api/auth/login/ | 用户登录，返回 JWT Token | 公开 |
| POST | /api/auth/logout/ | 用户登出 | 已认证 |
| POST | /api/auth/refresh/ | 刷新 Token | 已认证 |

**登录请求**：
```json
{
  "username": "admin",
  "password": "{加密后密码}"
}
```

**登录响应**：
```json
{
  "code": 200,
  "data": {
    "access": "{JWT Token}",
    "refresh": "{Refresh Token}",
    "user": { "id": 1, "username": "admin", "role": "admin" }
  }
}
```

### 3.3 {模块名}接口

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /api/{resource}/ | 列表查询（支持分页、过滤） | 全部角色 |
| POST | /api/{resource}/ | 新增 | admin/editor |
| PUT | /api/{resource}/{code}/ | 修改 | admin/editor |
| DELETE | /api/{resource}/{code}/ | 删除 | admin/editor |
| GET | /api/{resource}/{code}/history/ | 历史版本 | 全部角色 |
| POST | /api/{resource}/import/ | Excel 导入 | admin/editor |
| GET | /api/{resource}/export/ | Excel 导出 | 全部角色 |

**查询参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码，默认 1 |
| page_size | int | 每页数量，默认 20 |
| search | string | 模糊搜索关键词 |

### 3.4 API 汇总

> 模块与 1.6 模块清单对应。

| 模块标识 | 接口数 | 路径前缀 |
|----------|--------|----------|
| auth | 3 | /api/auth/ |
| {module-id} | 7 | /api/{module-id}/ |
| sys | 5 | /api/sys/ |
| **合计** | **15** | - |

---

## 4. 核心功能设计

### 4.1 {核心算法/功能1}

{描述核心功能的实现方案}

```python
# 示例代码
def {function_name}(input):
    pass
```

### 4.2 Excel 导入导出设计

**导入流程**：
```
上传文件 → 格式校验 → 逐行数据校验 → 事务批量写入
              ↓               ↓
          格式错误        返回错误行列表（行号 + 错误原因）
```

**导出流程**：
```
接收查询参数 → 查询数据 → 生成 Excel → 返回文件流
```

**Excel 模板规范**：
- 第一行为表头，字段名与数据库字段对应
- 必填字段标红
- 提供下载模板接口

### 4.3 权限控制设计

采用 RBAC（基于角色的访问控制）：

| 角色 | role 值 | 权限范围 |
|------|---------|----------|
| 管理员 | admin | 全部操作 |
| 维护人员 | editor | 增删改查 + 导入导出 |
| 查询人员 | viewer | 只读 + 导出 |

```python
# 权限检查示例
class IsEditorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'editor']
```

### 4.4 操作日志设计

记录所有增删改操作：

| 字段 | 说明 |
|------|------|
| user | 操作人 |
| action | 操作类型（CREATE/UPDATE/DELETE） |
| resource | 资源类型 |
| resource_id | 资源 ID |
| detail | 变更详情（JSON） |
| ip | 客户端 IP |
| created_at | 操作时间 |

### 4.5 密码加密设计

- 前端：使用 RSA 公钥加密后传输（SR-0001）
- 后端：使用 Django 内置 `make_password` 存储（bcrypt）
- 禁止明文传输和存储（SR-0002）

---

## 5. 前端设计

### 5.1 页面结构

```
src/
├── views/
│   ├── login/           # 登录页
│   ├── {module1}/       # 业务模块1
│   └── system/          # 系统管理
│       ├── user/        # 用户管理
│       └── log/         # 操作日志
├── components/
│   ├── Table/           # 通用表格组件
│   ├── Form/            # 表单组件
│   └── Excel/           # 导入导出组件
├── store/
│   └── user.ts          # 用户状态
├── router/
│   └── index.ts         # 路由配置
└── utils/
    └── request.ts       # Axios 封装
```

### 5.2 路由设计

```typescript
const routes = [
  { path: '/login', component: Login },
  {
    path: '/',
    component: Layout,
    children: [
      { path: '{module1}', component: Module1 },
      { path: 'system/user', component: UserManage },
      { path: 'system/log', component: OperationLog },
    ]
  }
]
```

### 5.3 状态管理设计

```typescript
// store/user.ts
export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: { username: '', role: '' }
  }),
  actions: {
    async login(credentials) { ... },
    logout() { ... }
  }
})
```

### 5.4 公共组件设计

| 组件名 | 说明 | Props |
|--------|------|-------|
| ProTable | 通用表格（搜索+分页+操作） | columns, api, actions |
| ModalForm | 弹窗表单（新增/编辑） | fields, onSubmit |
| ExcelImport | Excel 导入组件 | uploadApi, templateApi |
| ExcelExport | Excel 导出组件 | exportApi |
| StatusTag | 状态标签 | status |

### 5.5 功能页面设计

#### {模块1}页面

**页面功能**：列表查询、新增、编辑、删除、导入、导出

**搜索字段**：{字段1}、{字段2}

**表格列**：

| 列名 | 字段 | 宽度 | 说明 |
|------|------|------|------|
| {列名} | {字段} | {宽度} | - |
| 操作 | - | 150px | 编辑、删除 |

### 5.6 API 请求封装

```typescript
// utils/request.ts
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
})

// 请求拦截：注入 Token
request.interceptors.request.use(config => {
  config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：统一错误处理
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) router.push('/login')
    return Promise.reject(error)
  }
)
```

### 5.7 页面设计汇总

| 页面 | 路由 | 组件 | 功能 |
|------|------|------|------|
| 登录 | /login | Login.vue | 登录认证 |
| {模块1} | /{module1} | {Module1}.vue | CRUD + 导入导出 |
| 用户管理 | /system/user | UserManage.vue | 用户 CRUD |
| 操作日志 | /system/log | OperationLog.vue | 日志查询 |

---

## 6. 部署设计（Docker）

### 6.1 部署架构

```
┌─────────────────────────────────────┐
│           Docker Compose            │
│                                     │
│  ┌──────────┐    ┌───────────────┐  │
│  │  nginx   │    │    backend    │  │
│  │ :80/:443 │───▶│    :8000      │  │
│  └──────────┘    └───────┬───────┘  │
│       │                  │          │
│       │          ┌───────▼───────┐  │
│       │          │      db       │  │
│       │          │    :3306      │  │
│       │          └───────────────┘  │
│  前端静态文件                         │
└─────────────────────────────────────┘
```

### 6.2 Docker Compose 配置

```yaml
# docker/docker-compose.prod.yml
version: '3.8'
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql

  backend:
    build: ../backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ../frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend

volumes:
  db_data:
```

### 6.3 后端 Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 6.4 Nginx 配置

```nginx
server {
    listen 80;
    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    # API 反向代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6.5 环境变量配置

```bash
# .env.example
SECRET_KEY=your-secret-key
DB_NAME={项目简称}
DB_USER={项目简称}_user
DB_PASSWORD=your-db-password
DATABASE_URL=mysql://{项目简称}_user:password@db:3306/{项目简称}
DEBUG=False
ALLOWED_HOSTS=localhost,your-domain.com
```

### 6.6 部署命令

```bash
# 构建镜像
docker compose -f docker/docker-compose.prod.yml build

# 启动服务
docker compose -f docker/docker-compose.prod.yml up -d

# 执行数据库迁移
docker compose exec backend python manage.py migrate

# 健康检查
curl -f http://localhost/health
```

---

## 7. 项目配置

### 7.1 代码仓库

| 项目 | 地址 |
|------|------|
| Git 仓库 | {仓库地址} |
| 主分支 | main |
| 开发分支 | develop |

### 7.2 数据库连接（开发环境）

| 项目 | 配置 |
|------|------|
| Host | localhost |
| Port | {端口} |
| Database | {数据库名}_dev |
| User | {用户名} |

---

## 附录

### A. 技术选型对比

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| {方案A} | {优点} | {缺点} | {结论} |
| {方案B} | {优点} | {缺点} | 未选用 |

---

*文档结束*
