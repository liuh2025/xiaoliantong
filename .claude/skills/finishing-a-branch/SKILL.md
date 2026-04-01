---
name: finishing-a-branch
description: 分支完成处理，提供合并/PR/保留/丢弃等选项。手动调用工具，实际里程碑流程中未使用（各阶段已通过 git-* skills 自动处理）。
user-invocable: true
disable-model-invocation: true
argument-hint: "[目标分支] [选项]"
---

你现在作为 Orchestrator 角色工作，处理分支完成后的统一操作。

## 核心原则

**先验证再合并，确保代码质量。**

## 上下文获取

- **当前分支**：自动检测
- **目标分支**：$ARGUMENTS 第一个参数（如 main、develop）
- **选项**：$ARGUMENTS 第二个参数（可选： merge/pr/keep/discard）
- **来源**：调用方传递（m3-exit / m4-exit / m5-exit / 手动调用）

## 分支完成选项

向用户展示以下选项：

```
## 分支完成处理

**当前分支**: {BRANCH}
**目标分支**: {TARGET_BRANCH}

### 1. 合并到目标分支（推荐）
- **用途**：将当前分支合并到目标分支
- **操作**：
  ```bash
  git checkout {TARGET_BRANCH}
  git pull origin {TARGET_BRANCH}
  git merge {BRANCH}
  git push origin {TARGET_BRANCH}
  ```
- **Worktree**：自动清理

### 2. 创建 Pull Request
- **用途**：创建 PR，供代码审查
- **操作**：
  ```bash
  git push -u origin {BRANCH}
  gh pr create --title "{title}" --body "{body}"
  ```
- **Worktree**：保留

### 3. 保持分支不变
- **用途**：暂不处理，稍后决定
- **说明**：分支和 worktree 保持当前状态
- **Worktree**：保留

### 4. 丢弃此工作（危险）
- **用途**：放弃当前分支的所有工作
- **确认**：
  ```
  这将永久删除：
  - 分支：{BRANCH}
  - 提交：{COMMITS}
  - Worktree：{WORKTREE_PATH}

  输入 'discard' 确认删除：
  ```
- **操作**（确认后）

请选择 (1/2/3/4)：
```

## 处理用户选择

### 选项 1：合并到目标分支

```bash
# 获取信息
BRANCH=$(git branch --show-current)
TARGET_BRANCH="{用户指定的目标分支}"
WORKTREE_PATH=$(pwd)

# 切换到目标分支
git checkout "$TARGET_BRANCH"
git pull origin "$TARGET_BRANCH"

# 合并
git merge "$BRANCH"

# 推送
git push origin "$TARGET_BRANCH"

# 清理 worktree（如果在 worktree 中）
if git worktree list | grep -q "$WORKTREE_PATH"; then
    git worktree remove "$WORKTREE_PATH"
fi
```

**完成报告：**
```
✅ 已合并到 {TARGET_BRANCH}
   - 分支：{BRANCH} → {TARGET_BRANCH}
   - Worktree：已清理
```

### 选项 2：创建 Pull Request

```bash
BRANCH=$(git branch --show-current)

# 推送分支
git push -u origin "$BRANCH"

# 创建 PR
gh pr create --title "{title}" --body "$(cat <<'EOF'
## Summary
{summary}

## Test Plan
{test_plan}

## Checklist
{checklist}
EOF
)"
```

**完成报告：**
```
✅ PR 已创建
   - PR URL: {pr-url}
   - Worktree：保留
```

### 选项 3：保持不变

```
✅ 分支保持不变
   - 当前分支：{BRANCH}
   - Worktree：保留
   - 稍后可手动处理
```

### 选项 4：丢弃（需确认）

等待用户输入 'discard' 确认后执行删除操作。

**确认后执行：**
```bash
BRANCH=$(git branch --show-current)
BASE_BRANCH=$(git worktree list | grep "$(pwd)" | head -1 | awk '{print $1}')
WORKTREE_PATH=$(pwd)
COMMITS=$(git log --oneline "$BASE_BRANCH"..HEAD | wc -l)

# 切换到基础分支
git checkout "$BASE_BRANCH"

# 删除分支
git branch -D "$BRANCH"

# 清理 worktree
git worktree remove "$WORKTREE_PATH"
```

**完成报告：**
```
⚠️ 工作已丢弃
   - 已删除分支：{BRANCH}
   - 已删除提交：{COMMITS} 个
   - 已清理 worktree：{WORKTREE_PATH}
```

## 自动模式

如果 `$ARGUMENTS` 包含选项参数，则自动执行对应操作，无需用户确认：

```bash
# 示例：自动合并到 main
/finishing-a-branch main merge

# 示例：自动创建 PR
/finishing-a-branch main pr
```

## 调用示例

### M4 测试完成后合并到 main

```
/finishing-a-branch main
```

### M5 部署完成后合并到 main

```
/finishing-a-branch main merge
```

### 手动调用（需要确认丢弃）

```
/finishing-a-branch main discard
```

## 完成标志

返回处理结果：
- 选择的选项
- 操作结果
- Worktree 状态

## 关联 Skills

**说明：**
- 本 skill 为手动工具，里程碑流程中各阶段已通过 git-* skills 自动处理分支操作
- 适用于需要手动干预或特殊处理的场景

**参考：**
- `/git-merge` - 自动化分支合并
- `/git-cleanup` - 自动化分支清理
