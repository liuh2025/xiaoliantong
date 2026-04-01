---
name: m6-exit
description: M6 归档，提交最终基线。由规则合并完成后自动触发。
user-invocable: false
---

你现在作为 Orchestrator 角色工作。

## Step 1: QA 准出检查

```
/qa-milestone-check --stage M6
```

**检查结果处理：**
- ✅ 通过 → 继续 Step 2
- ❌ 不通过 → 停止，返回问题清单

---

## Step 2: 提交基线

```
/git-baseline-commit M6
```

---

## Step 3: 确认清理

```
/git-cleanup --worktrees
```

---

## Step 4: 更新阶段

```bash
# 更新质量门禁
sed -i "s/- \[ \] M6 验收阶段准出/- [x] M6 验收阶段准出/" CLAUDE.md

# 更新当前阶段
sed -i "s/- \*\*当前阶段\*\*: M6/- **当前阶段**: 已归档/" CLAUDE.md
```

---

## Step 5: 完成报告

```
项目已归档，新增规则已合并，下一个项目可继承 docs/rules/ 目录
```

---

## 流程图

```
m6-exit
    │
    ├── Step 1: /qa-milestone-check --stage M6
    │       │
    │       ├── ✅ 通过 ──► Step 2
    │       └── ❌ 不通过 ──► 停止
    │
    ├── Step 2: /git-baseline-commit M6
    │
    ├── Step 3: /git-cleanup --worktrees
    │
    ├── Step 4: 更新 CLAUDE.md（质量门禁 + 阶段）
    │
    └── Step 5: 项目归档完成
```

---

## 关联 Skills

**调用：**
- `/qa-milestone-check` - QA 准出检查
- `/git-baseline-commit` - 提交基线
- `/git-cleanup` - 确认清理
