---
name: m2-exit
description: M2 准出检查，确认所有文档已批准后更新阶段。由 write-chk 完成后自动触发。
user-invocable: false
---

你现在作为 Orchestrator 角色工作。

## Step 1: QA 准出检查

```
/qa-milestone-check --stage M2
```

**检查结果处理：**
- ✅ 通过 → 继续 Step 2
- ❌ 不通过 → 停止，返回问题清单

---

## Step 2: 提交基线

```
/git-baseline-commit M2
```

---

## Step 3: 创建 Worktree

```
/create-worktrees
```

---

## Step 4: 更新阶段

```bash
# 更新质量门禁
sed -i "s/- \[ \] M2 设计阶段准出/- [x] M2 设计阶段准出/" CLAUDE.md

# 更新当前阶段
sed -i "s/- \*\*当前阶段\*\*: M2/- **当前阶段**: M3/" CLAUDE.md
```

---

## Step 5: 触发下一步

```
M2 准出完成，进入 M3 开发阶段：
/m3-write-dev-plan
```

---

## 流程图

```
m2-exit
    │
    ├── Step 1: /qa-milestone-check --stage M2
    │       │
    │       ├── ✅ 通过 ──► Step 2
    │       └── ❌ 不通过 ──► 停止
    │
    ├── Step 2: /git-baseline-commit M2
    │
    ├── Step 3: /create-worktrees (创建 worktree)
    │
    ├── Step 4: 更新 CLAUDE.md（质量门禁 + 阶段）
    │
    └── Step 5: 触发 /m3-write-dev-plan
```

---

## 关联 Skills

**调用：**
- `/qa-milestone-check` - QA 准出检查
- `/git-baseline-commit` - 提交基线
- `/create-worktrees` - 创建 worktree

**后续：**
- `/m3-write-dev-plan` - 进入 M3 开发阶段
