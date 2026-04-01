---
name: m1-exit
description: M1 准出检查，确认 PRD 已批准后更新阶段。由 write-prd 完成后自动触发。
user-invocable: false
---

你现在作为 Orchestrator 角色工作。

## Step 1: QA 准出检查

```
/qa-milestone-check --stage M1
```

**检查结果处理：**
- ✅ 通过 → 继续 Step 2
- ❌ 不通过 → 停止，返回问题清单

---

## Step 2: 提交基线

```
/git-baseline-commit M1
```

---

## Step 3: 更新阶段

```bash
# 更新质量门禁
sed -i "s/- \[ \] M1 需求阶段准出/- [x] M1 需求阶段准出/" CLAUDE.md

# 更新当前阶段
sed -i "s/- \*\*当前阶段\*\*: M1/- **当前阶段**: M2/" CLAUDE.md
```

---

## Step 4: 触发下一步

```
M1 准出完成，进入 M2 设计阶段：
/m2-design-proposal
```

---

## 流程图

```
m1-exit
    │
    ├── Step 1: /qa-milestone-check --stage M1
    │       │
    │       ├── ✅ 通过 ──► Step 2
    │       └── ❌ 不通过 ──► 停止
    │
    ├── Step 2: /git-baseline-commit M1
    │
    ├── Step 3: 更新 CLAUDE.md（质量门禁 + 阶段）
    │
    └── Step 4: 触发 /m2-design-proposal
```

---

## 关联 Skills

**调用：**
- `/qa-milestone-check` - QA 准出检查
- `/git-baseline-commit` - 提交基线

**后续：**
- `/m2-design-proposal` - 进入 M2 设计阶段
