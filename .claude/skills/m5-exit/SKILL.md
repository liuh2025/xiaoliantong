---
name: m5-exit
description: M5 准出检查，提交部署基线。由 QA 审查通过后自动触发。
user-invocable: false
---

你现在作为 Orchestrator 角色工作。

## Step 1: QA 准出检查

```
/qa-milestone-check --stage M5
```

**检查结果处理：**
- ✅ 通过 → 继续 Step 2
- ❌ 不通过 → 停止，返回问题清单

---

## Step 2: 提交基线

```
/git-baseline-commit M5
```

---

## Step 3: 更新阶段

```bash
# 更新质量门禁
sed -i "s/- \[ \] M5 部署阶段准出/- [x] M5 部署阶段准出/" CLAUDE.md

# 更新当前阶段
sed -i "s/- \*\*当前阶段\*\*: M5/- **当前阶段**: M6/" CLAUDE.md
```

---

## Step 4: 触发下一步

```
M5 准出完成，进入 M6 验收阶段：
/m6-acceptance
```

---

## 流程图

```
m5-exit
    │
    ├── Step 1: /qa-milestone-check --stage M5
    │       │
    │       ├── ✅ 通过 ──► Step 2
    │       └── ❌ 不通过 ──► 停止
    │
    ├── Step 2: /git-baseline-commit M5
    │
    ├── Step 3: 更新 CLAUDE.md（质量门禁 + 阶段）
    │
    └── Step 4: 触发 /m6-acceptance
```

---

## 关联 Skills

**调用：**
- `/qa-milestone-check` - QA 准出检查
- `/git-baseline-commit` - 提交基线

**后续：**
- `/m6-acceptance` - 进入 M6 验收阶段
