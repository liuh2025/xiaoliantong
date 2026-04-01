---
name: git-cleanup
description: 清理已合并的分支和 worktree。由 m4-exit、m6-exit 调用。
user-invocable: true
argument-hint: "[--all | --merged | --worktrees]"
context: fork
agent: general-purpose
allowed-tools: Bash
---

## 参数

- `--all`: 清理所有 feature 分支和 worktree（默认）
- `--merged`: 只清理已合并的分支
- `--worktrees`: 只清理 worktree

## 当前状态

```bash
git worktree list 2>/dev/null || echo "[无 worktree]"
git branch -a 2>/dev/null || echo "[无分支]"
```

## 清理 worktree

```bash
WORKTREES=$(git worktree list | tail -n +2 | awk '{print $1}')
for wt in $WORKTREES; do
    git worktree remove "$wt" --force 2>/dev/null || rm -rf "$wt"
done
git worktree prune
```

## 清理分支

### --merged: 已合并的 feature 分支

```bash
if [ "$ARG1" = "--merged" ] || [ "$ARG1" = "--all" ] || [ -z "$ARG1" ]; then
    for branch in $(git branch --merged develop 2>/dev/null | grep "feature/" | sed 's/^[ *]*//'); do
        git branch -d "$branch" 2>/dev/null || true
    done
fi
```

### --all: 所有 feature 分支

```bash
if [ "$ARG1" = "--all" ]; then
    for branch in $(git branch | grep "feature/" | sed 's/^[ *]*//'); do
        git branch -D "$branch" 2>/dev/null || true
    done
fi
```

## 完成标志

```bash
git worktree list
git branch -a | grep -v "remotes/origin/HEAD"
```

```
✅ 清理完成
   - 剩余分支: main, develop
```
