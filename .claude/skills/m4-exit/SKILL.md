---
name: m4-exit
description: M4 准出检查，提交测试基线并合并到 main 分支。由 QA 审查通过后自动触发。
user-invocable: false
---

你现在作为 Orchestrator 角色工作。

## Step 1: QA 准出检查

```
/qa-milestone-check --stage M4
```

**检查结果处理：**
- ✅ 通过 → 继续 Step 2
- ❌ 不通过 → 停止，返回问题清单

---

## Step 2: 提交基线

```
/git-baseline-commit M4
```

---

## Step 3: 合并到 main

```
/git-merge develop main
```

---

## Step 4: 清理分支

```
/git-cleanup --all
```

---

## Step 5: 更新阶段

```bash
# 更新质量门禁
sed -i "s/- \[ \] M4 测试阶段准出/- [x] M4 测试阶段准出/" CLAUDE.md

# 更新当前阶段
sed -i "s/- \*\*当前阶段\*\*: M4/- **当前阶段**: M5/" CLAUDE.md
```

---

## Step 6: 触发下一步

```
M4 准出完成，进入 M5 部署阶段：
/m5-deploy
```

---

## 流程图

```
m4-exit
    │
    ├── Step 1: /qa-milestone-check --stage M4
    │       │
    │       ├── ✅ 通过 ──► Step 2
    │       └── ❌ 不通过 ──► 停止
    │
    ├── Step 2: /git-baseline-commit M4
    │
    ├── Step 3: /git-merge develop main
    │
    ├── Step 4: /git-cleanup --all
    │
    ├── Step 5: 更新 CLAUDE.md（质量门禁 + 阶段）
    │
    └── Step 6: 触发 /m5-deploy
```

---

## 关联 Skills

**调用：**
- `/qa-milestone-check` - QA 准出检查
- `/git-baseline-commit` - 提交基线
- `/git-merge` - 合并到 main
- `/git-cleanup` - 清理分支

**后续：**
- `/m5-deploy` - 进入 M5 部署阶段
