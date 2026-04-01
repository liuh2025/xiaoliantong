---
name: create-worktrees
description: M2 准出确认通过后，创建所有模块的 worktree 并写入配置。由 m2-exit 自动触发。
user-invocable: false
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Grep
---

## Step 1: 前置检查

### 1.1 检查 git 状态

```bash
git status --porcelain 2>/dev/null || echo "[非 git 仓库]"
```

如有未提交变更，提示处理后再继续。

---

## Step 2: 创建所有模块的 Worktree

### 2.1 从 DESN 提取模块清单

!`grep -A 20 "### 2.1 模块清单" docs/DESN-*.md 2>/dev/null | grep "^|" | grep -v "模块标识\|^|---" || echo "[未找到模块清单]"`

### 2.2 确认 .gitignore

```bash
git check-ignore -q .worktrees 2>/dev/null || echo ".worktrees/" >> .gitignore
```

### 2.3 批量创建 Worktree

```bash
WORKTREE_DIR=".worktrees"

for MODULE_ID in $(grep -A 20 "### 2.1 模块清单" docs/DESN-*.md | grep "^|" | grep -v "模块标识\|^|---" | sort -t'|' -k4 -n | awk -F'|' '{print $2}' | tr -d ' '); do
    if [ -d "$WORKTREE_DIR/$MODULE_ID" ]; then
        echo "⏭️ 已存在: $MODULE_ID"
    else
        git worktree add "$WORKTREE_DIR/$MODULE_ID" -b "feature/$MODULE_ID"
        echo "✅ 创建: $MODULE_ID"
    fi
done
```

---

## Step 3: Worktree 配置写入 CLAUDE.md

```bash
cat >> CLAUDE.md << 'EOF'

## Worktree 配置

> 由 create-worktrees 自动生成

| 模块标识 | 迭代顺序 | Worktree 路径 | 分支名称 |
|----------|----------|---------------|----------|
EOF

grep -A 20 "### 2.1 模块清单" docs/DESN-*.md | grep "^|" | grep -v "模块标识\|^|---" | while read line; do
    module_id=$(echo "$line" | awk -F'|' '{print $2}' | tr -d ' ')
    order=$(echo "$line" | awk -F'|' '{print $4}' | tr -d ' ')
    echo "| $module_id | $order | .worktrees/$module_id | feature/$module_id |" >> CLAUDE.md
done
```

---

## 完成报告

```
✅ Worktree 创建完成

| 模块 | 迭代顺序 | Worktree | 分支 |
|------|----------|----------|------|
| {modules} |
