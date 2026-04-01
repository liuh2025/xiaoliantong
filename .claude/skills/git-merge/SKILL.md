---
name: git-merge
description: 安全的分支合并，带冲突检测和自动 rebase。由 m3-exit、m4-exit 调用。
user-invocable: false
argument-hint: "<源分支> <目标分支> [--rebase]"
context: fork
agent: general-purpose
allowed-tools: Bash
---

## 前置检查

```bash
git branch -a | grep -E "$ARG1|$ARG2" || echo "[分支不存在]"
git status --porcelain 2>/dev/null || echo "[非 git 仓库]"
```

## 获取最新代码

```bash
git fetch origin 2>/dev/null || true
git checkout "$ARG2"
git pull origin "$ARG2" 2>/dev/null || true
```

## 冲突检测

```bash
git merge --no-commit --no-ff "$ARG1" 2>/dev/null
if [ $? -ne 0 ]; then
    git merge --abort 2>/dev/null || git reset --hard HEAD
    CONFLICT_DETECTED=true
    echo "⚠️ 检测到冲突"
    git diff --name-only "$ARG2" "$ARG1"
else
    git merge --abort 2>/dev/null || git reset --hard HEAD
    CONFLICT_DETECTED=false
fi
```

## 执行合并

### 无冲突 - 直接合并

```bash
if [ "$CONFLICT_DETECTED" = false ]; then
    git checkout "$ARG2"
    git merge "$ARG1" --no-edit
fi
```

### 有冲突 + --rebase 模式

```bash
if [ "$CONFLICT_DETECTED" = true ] && [ "$ARG3" = "--rebase" ]; then
    git checkout "$ARG1"
    git rebase "$ARG2"

    if [ $? -ne 0 ]; then
        echo "❌ rebase 冲突，解决步骤："
        echo "1. git status 查看冲突文件"
        echo "2. 编辑冲突文件"
        echo "3. git add <file>"
        echo "4. git rebase --continue"
        exit 1
    fi

    git checkout "$ARG2"
    git merge "$ARG1" --no-edit
fi
```

### 有冲突 + 普通模式

```bash
if [ "$CONFLICT_DETECTED" = true ] && [ "$ARG3" != "--rebase" ]; then
    echo "❌ 检测到冲突，请手动解决或使用 --rebase"
    exit 1
fi
```

## 推送

```bash
REMOTE=$(git remote | head -1)
[ -n "$REMOTE" ] && git push "$REMOTE" "$ARG2"
```

## 完成标志

```
✅ 合并完成
   - 源: $ARG1 → 目标: $ARG2
   - 模式: {直接合并/rebase}
```
