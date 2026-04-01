# Git 规范（GIT-rules.md）

## 分支规范

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 功能开发 | feature/{模块}-{描述} | feature/user-crud |
| 缺陷修复 | fix/{模块}-{描述} | fix/order-status-bug |
| 紧急修复 | hotfix/{描述} | hotfix/login-crash |
| 发布分支 | release/{版本} | release/1.2.0 |

---

## 提交消息规范（Conventional Commits）

格式：`<type>(<scope>): <description>`

| type | 含义 |
|------|------|
| feat | 新功能 |
| fix | 缺陷修复 |
| test | 测试相关 |
| docs | 文档变更 |
| refactor | 重构（不含功能变更） |
| chore | 构建/工具链变更 |

示例：
- feat(user): add user CRUD API
- fix(order): fix status transition bug
- test(user): add boundary test for login

---

## 合并策略

- feature/* → develop：Squash Merge，保持主线整洁
- develop → main：Merge Commit，保留完整历史
- hotfix/* → main：Cherry-pick + 同步到 develop

---

## Git 红线

参照以下规约文件执行检查：

**代码管理类红线（RL-redlines.md）：**
- RL-DV-0001: 禁止在 main/master 分支直接提交（阻断）
- RL-DV-0002: 代码修改完成必须提交，不允许长期未提交（警告）
- RL-DV-0003: 单元测试未全部通过禁止提交（阻断）

**安全规约（SR-security-rules.md）：**
- SR-0003: 敏感文件（.env/.pem/.key）禁止提交（阻断）
