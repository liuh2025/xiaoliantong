# 环境配置模板

## {项目名称}

| 文档信息 | 内容 |
|---------|------|
| 项目名称 | {项目名称} |
| 文档版本 | {版本号} |
| 创建日期 | {日期} |
| 文档状态 | 草稿 |

---

## 1. 环境总览

| 环境 | 用途 | 部署方式 | 访问地址 |
|------|------|----------|----------|
| 开发环境 | 开发调试 | 本地 Docker | http://localhost:8000 |
| 测试环境 | M4 测试验证 | 测试服务器 | http://test.{项目简称}.com |
| 生产环境 | M5 正式部署 | 生产服务器 | https://{项目简称}.com |

---

## 2. 开发环境

### 2.1 本地服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:3000 | Vue Dev Server |
| 后端 API | http://localhost:8000 | Django Runserver |
| API 文档 | http://localhost:8000/swagger/ | Swagger UI |
| 数据库 | localhost:5432 | PostgreSQL |
| Redis | localhost:6379 | 缓存服务 |

### 2.2 环境变量（.env.development）

```bash
# 应用配置
APP_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# 数据库
DB_HOST=localhost
DB_PORT=5432
DB_NAME={项目简称}_dev
DB_USER=dev_user
DB_PASSWORD=dev_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# 前端
VITE_API_BASE_URL=http://localhost:8000
```

### 2.3 启动命令

```bash
# 启动数据库
docker compose up -d db redis

# 启动后端
cd backend
python manage.py runserver 0.0.0.0:8000

# 启动前端
cd frontend
npm run dev
```

---

## 3. 测试环境

### 3.1 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://test.{项目简称}.com | 测试环境入口 |
| 后端 API | http://api.test.{项目简称}.com | 测试 API |
| API 文档 | http://api.test.{项目简称}.com/swagger/ | Swagger UI |
| 数据库 | test-db.internal:5432 | 测试数据库（RL-DV-0005：与生产分离）|

### 3.2 环境变量（.env.test）

```bash
# 应用配置
APP_ENV=test
DEBUG=False
SECRET_KEY=${TEST_SECRET_KEY}

# 数据库
DB_HOST=test-db.internal
DB_PORT=5432
DB_NAME={项目简称}_test
DB_USER=test_user
DB_PASSWORD=${TEST_DB_PASSWORD}

# Redis
REDIS_HOST=test-redis.internal
REDIS_PORT=6379

# 前端
VITE_API_BASE_URL=http://api.test.{项目简称}.com
```

### 3.3 部署方式

```bash
# 从 develop 分支部署
git checkout develop
git pull origin develop

# 构建并启动
docker compose -f docker/docker-compose.test.yml up -d --build

# 执行数据库迁移
docker compose exec backend python manage.py migrate
```

---

## 4. 生产环境

### 4.1 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | https://{项目简称}.com | 生产环境入口 |
| 后端 API | https://api.{项目简称}.com | 生产 API |
| API 文档 | https://api.{项目简称}.com/swagger/ | Swagger UI（内部访问）|
| 数据库 | prod-db.internal:5432 | 生产数据库 |

### 4.2 环境变量（.env.production）

```bash
# 应用配置
APP_ENV=production
DEBUG=False
SECRET_KEY=${PROD_SECRET_KEY}
ALLOWED_HOSTS={项目简称}.com,api.{项目简称}.com

# 数据库
DB_HOST=prod-db.internal
DB_PORT=5432
DB_NAME={项目简称}_prod
DB_USER=prod_user
DB_PASSWORD=${PROD_DB_PASSWORD}

# Redis
REDIS_HOST=prod-redis.internal
REDIS_PORT=6379

# 前端
VITE_API_BASE_URL=https://api.{项目简称}.com

# HTTPS
SSL_CERTIFICATE=/etc/ssl/certs/{项目简称}.crt
SSL_CERTIFICATE_KEY=/etc/ssl/private/{项目简称}.key
```

### 4.3 部署方式

```bash
# 从 main 分支部署（M4 测试通过后）
git checkout main
git pull origin main

# 构建并启动
docker compose -f docker/docker-compose.prod.yml up -d --build

# 执行数据库迁移
docker compose exec backend python manage.py migrate

# 健康检查
curl -f https://{项目简称}.com/health
```

---

## 5. CI/CD 配置

### 5.1 分支与环境对应

| 分支 | 部署环境 | 触发条件 |
|------|----------|----------|
| feature/* | 不部署 | 本地开发 |
| develop | 测试环境 | M3 准出后自动部署 |
| main | 生产环境 | M4 准出后手动触发 |

### 5.2 部署检查清单

**测试环境部署前：**
- [ ] develop 分支代码已推送
- [ ] 单元测试 100% 通过
- [ ] 静态代码扫描无阻断问题

**生产环境部署前：**
- [ ] main 分支代码已合并
- [ ] L1/L2 测试 100% 通过
- [ ] QA 已签署审查意见
- [ ] 用户已批准部署

---

## 6. 网络配置

### 6.1 端口分配

| 服务 | 开发环境 | 测试环境 | 生产环境 |
|------|----------|----------|----------|
| Nginx | 80 | 80 | 80, 443 |
| 后端 API | 8000 | 8000 | 8000 |
| 数据库 | 5432 | 5432 | 5432 |
| Redis | 6379 | 6379 | 6379 |

### 6.2 防火墙规则

**生产环境：**
- 仅开放 80/443 端口给外部
- 数据库/Redis 仅允许内网访问
- SSH 仅允许特定 IP

---

## 7. 监控与日志

### 7.1 日志位置

| 环境 | 日志目录 |
|------|----------|
| 开发环境 | `logs/` |
| 测试环境 | `/var/log/{项目简称}/test/` |
| 生产环境 | `/var/log/{项目简称}/prod/` |

### 7.2 监控指标

| 指标 | 告警阈值 |
|------|----------|
| CPU 使用率 | > 80% |
| 内存使用率 | > 85% |
| 响应时间 | > 2s |
| 错误率 | > 1% |

---

## 8. 变更记录

| 日期 | 变更内容 | 变更人 |
|------|----------|--------|
| {日期} | 初始版本 | - |

---

*文档结束*
