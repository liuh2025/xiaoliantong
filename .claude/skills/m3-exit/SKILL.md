---
name: m3-exit
description: M3 准出检查，提交开发基线并合并到 develop 分支。由 TL final review 通过后自动触发。
user-invocable: false
---

你现在作为 Orchestrator 角色工作。

## Step 1: QA 准出检查

```
/qa-milestone-check --stage M3
```

**检查结果处理：**
- ✅ 通过 → 继续 Step 2
- ❌ 不通过 → 停止，返回问题清单

---

## Step 2: 提交基线

```
/git-baseline-commit M3
```

---

## Step 3: 合并到 develop

获取所有 feature 分支，依次调用 git-merge：

```bash
# 获取所有 feature 分支
FEATURES=$(git branch | grep "feature/" | sed 's/^[ *]*//')

# 创建 develop 分支（如不存在）
git checkout -b develop 2>/dev/null || git checkout develop

# 依次合并每个 feature 分支
for branch in $FEATURES; do
    /git-merge $branch develop --rebase
done
```

---

## Step 4: 更新阶段

```bash
# 更新质量门禁
sed -i "s/- \[ \] M3 开发阶段准出/- [x] M3 开发阶段准出/" CLAUDE.md

# 更新当前阶段
sed -i "s/- \*\*当前阶段\*\*: M3/- **当前阶段**: M4/" CLAUDE.md
```

---

## Step 5: 触发下一步

```
M3 准出完成，进入 M4 测试阶段：
/m4-test-kickoff
```

---

## 流程图

```
m3-exit
    │
    ├── Step 1: /qa-milestone-check --stage M3
    │       │
    │       ├── ✅ 通过 ──► Step 2
    │       └── ❌ 不通过 ──► 停止
    │
    ├── Step 2: /git-baseline-commit M3
    │
    ├── Step 3: for branch in features:
    │           /git-merge $branch develop --rebase
    │
    ├── Step 4: 更新 CLAUDE.md（质量门禁 + 阶段）
    │
    └── Step 5: 触发 /m4-test-kickoff
```

---

## 关联 Skills

**调用：**
- `/qa-milestone-check` - QA 准出检查
- `/git-baseline-commit` - 提交基线
- `/git-merge` - 合并到 develop

**后续：**
- `/m4-test-kickoff` - 进入 M4 测试阶段
