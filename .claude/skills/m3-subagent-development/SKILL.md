---
name: m3-subagent-development
description: M3 开发阶段执行或 M4 E2E 有 bug 时触发，使用 Task 工具派发 implementer/spec-reviewer/quality-reviewer subagent 循环。
argument-hint: "[--mode full|fix]"
user-invocable: false
---

你现在作为 TL（技术负责人）角色工作，负责管理开发流水线。

## 两个入口

本 skill 支持两种运行模式：

| 模式 | 触发场景 | 数据来源 | 完成后行为 |
|------|---------|---------|-----------|
| **开发模式** (`full`) | M3 开发阶段执行 | 从 DEV-plan 读取开发任务 | TL 全量审查 → 自动触发 `/m3-exit` |
| **Bug 修复模式** (`fix`) | M4 测试发现 bug | 从 TEST-REPORT 读取待修复问题 | TL 全量审查 → 自动触发 `/m3-exit` |

**示例：**
```bash
# 开发模式（M3 阶段）
/m3-subagent-development

# Bug 修复模式（M4 阶段）
/m3-subagent-development --mode fix
```

---

## 加载 TL 角色定义

!`cat docs/rules/prompts/tl-prompt.md 2>/dev/null || echo "[tl-prompt.md 未找到]"`

---

## 开发模式（full）

### 1. 前置检查

#### 1.1 检查开发计划

!`ls docs/plans/DEV-plan-*.md 2>/dev/null | head -1 || echo "[未找到开发计划，请先执行 /m3-write-dev-plan]"`

#### 1.2 检查 worktree 环境

**前置条件：**
1. 所有模块的 worktree 已创建（由 m2-exit 自动创建）
2. CLAUDE.md 中已写入 worktree 配置

**检查命令：**

```bash
# 检查 worktree 是否存在
WORKTREE_COUNT=$(git worktree list | grep ".worktrees" | wc -l)
if [ "$WORKTREE_COUNT" -eq 0 ]; then
    echo "❌ Worktree 未创建，请先执行 m2-exit"
    exit 1
else
    echo "✅ 检测到 $WORKTREE_COUNT 个 worktree"
fi

# 检查 CLAUDE.md 中的配置
if ! grep -q "Worktree 配置" CLAUDE.md; then
    echo "❌ CLAUDE.md 中缺少 worktree 配置"
    exit 1
else
    echo "✅ CLAUDE.md 中已配置 worktree"
fi
```

### 2. 加载开发计划

!`cat docs/plans/DEV-plan-*.md 2>/dev/null || echo "[开发计划未找到]"`

### 3. TaskCreate（从开发计划获取）

使用 Claude Code 内置的 TaskCreate 工具为每个 DEV-plan 中的 task 创建跟踪任务：

```
TaskCreate:
  subject: "[Task ID]: [模块名 - 功能点]"
  description: "[完整 task 描述，包含涉及文件、实现目标、TDD 步骤]"
  activeForm: "执行 [Task ID]"
```

**提前提取原则：** 派发任何 subagent 前，必须先提取所有 task 的完整文本和上下文，不让 subagent 自己读文件。

### 4. 模块状态跟踪

TL 维护当前正在开发的模块状态：

```bash
# 初始化：当前模块为空
CURRENT_MODULE=""
```

在执行每个 task 前，检查 task 所属模块：
- 如果 task 所属模块 != CURRENT_MODULE → 触发模块切换
- 如果 task 所属模块 == CURRENT_MODULE → 继续执行

### 5. Task 执行循环

对每个 task 按模块迭代顺序执行，同一模块内的 task 顺序执行：

#### Step 0: 模块切换（TL 负责）

**TL 在每个模块的第一个 task 开始前自动执行切换：**

```bash
# 从 DEV-plan 中提取当前 task 的模块标识
# 假设 task 格式为：### Task-001: 功能描述\n- 模块标识：user-auth
TASK_MODULE=$(grep -A 10 "^### $CURRENT_TASK_ID" docs/plans/DEV-plan-*.md | grep "模块标识" | awk -F'：' '{print $2}' | tr -d ' ')

# 判断是否需要切换
if [ "$TASK_MODULE" != "$CURRENT_MODULE" ]; then
    echo "📌 检测到模块切换: $CURRENT_MODULE → $TASK_MODULE"

    # 1. 从 CLAUDE.md 读取 worktree 配置
    WORKTREE_PATH=$(grep "| $TASK_MODULE |" CLAUDE.md | awk -F'|' '{print $4}' | tr -d ' ')
    BRANCH_NAME=$(grep "| $TASK_MODULE |" CLAUDE.md | awk -F'|' '{print $5}' | tr -d ' ')

    if [ -z "$WORKTREE_PATH" ] || [ -z "$BRANCH_NAME" ]; then
        echo "❌ 未找到模块 $TASK_MODULE 的 worktree 配置"
        exit 1
    fi

    # 2. 切换到对应模块的 worktree 和分支
    cd "$WORKTREE_PATH" || {
        echo "❌ 切换到 worktree 失败: $WORKTREE_PATH"
        exit 1
    }

    git checkout "$BRANCH_NAME" || {
        echo "❌ 切换到分支失败: $BRANCH_NAME"
        exit 1
    }

    # 3. 确认分支状态
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
        echo "❌ 分支切换失败，当前分支: $CURRENT_BRANCH，期望分支: $BRANCH_NAME"
        exit 1
    fi

    # 确认工作区干净
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️ 工作区有未提交的变更，请先处理"
        git status --short
        exit 1
    fi

    # 4. 更新当前模块状态
    CURRENT_MODULE="$TASK_MODULE"

    echo "✅ 已切换到模块: $TASK_MODULE"
    echo "   - Worktree: $WORKTREE_PATH"
    echo "   - 分支: $BRANCH_NAME"
    echo "   - 当前 task: $CURRENT_TASK_ID"
else
    echo "✅ 当前已在模块 $TASK_MODULE 中，无需切换"
fi
```

#### Step 1: 派发 Implementer

使用 Agent 工具启动 general-purpose agent，**传递完整任务上下文**：

```
Agent:
  subagent_type: "general-purpose"
  description: "实现 [task-id] (模块: {module-id})"
  prompt: |
    {implementer-prompt.md 内容}

    ## 任务定义

    **任务 ID**: {从 DEV-plan 提取 Task ID，如 Task-001}
    **任务标题**: {从 DEV-plan 提取 Task 标题，如"用户管理 - 用户注册接口"}
    **模块标识**: {从 DEV-plan 提取模块标识}

    **涉及文件**:
    {从 DEV-plan 原样复制"涉及文件"部分，包含创建/修改/测试的完整列表}

    **实现目标**:
    {从 DEV-plan 原样复制"实现目标"部分}

    **依赖关系**:
    {从 DEV-plan 原样复制"依赖关系"部分，如无则写"无"}

    ## 模块上下文
    - 模块标识：{module-id}
    - 模块名称：{module-name}
    - 迭代顺序：{iteration-order}
    - Worktree 路径：.worktrees/{module-id}
    - 分支名称：feature/{module-id}

    ## 项目上下文
    - 项目简称：{从 CLAUDE.md 提取}
    - 当前 HEAD：{当前 commit SHA}
    - 技术栈：{从 CLAUDE.md 提取}

    ## 审查意见（如有）
    {如果该 task 有审查意见，列出需要解决的问题}

    **迭代次数**: {当前是第几次迭代，如 1/3}
```

**处理 implementer 返回：**
- 如果 implementer 有疑问 → 回答后重新 dispatch
- 如果 implementer 报告完成 → 继续 Step 2

#### Step 2: 派发 Spec Reviewer

使用 Agent 工具启动 general-purpose agent，**传递模块上下文**：

```
Agent:
  subagent_type: "general-purpose"
  description: "规格审查 [task-id] (模块: {module-id})"
  prompt: |
    {spec-reviewer-prompt.md 内容}

    ## Task 定义
    {从 DEV-plan 提取的完整 task 文本}

    ## 模块上下文
    - 模块标识：{module-id}
    - 模块名称：{module-name}
    - Worktree：.worktrees/{module-id}
    - 分支：feature/{module-id}

    ## Git 上下文
    - BASE_SHA：{implementer 开始前的 commit}
    - HEAD_SHA：{当前 HEAD}
    - 涉及文件：{从 task 提取}
```

**处理 spec reviewer 返回：**
- ✅ 规格合规 → 继续 Step 3
- ❌ 发现问题 → 将问题记录到 task，**迭代计数 +1**
  - 如果迭代次数 < 3 → 回到 Step 1 重新派发 implementer
  - 如果迭代次数 ≥ 3 → 停止，TL 亲自介入分析问题

#### Step 3: 派发 Quality Reviewer

使用 Agent 工具启动 general-purpose agent，**传递模块上下文**：

```
Agent:
  subagent_type: "general-purpose"
  description: "质量审查 [task-id] (模块: {module-id})"
  prompt: |
    {quality-reviewer-prompt.md 内容}

    ## Task 定义
    {从 DEV-plan 提取的完整 task 文本}

    ## 模块上下文
    - 模块标识：{module-id}
    - 模块名称：{module-name}
    - 迭代顺序：{iteration-order}
    - Worktree：.worktrees/{module-id}
    - 分支：feature/{module-id}

    ## Git 上下文
    - BASE_SHA：{implementer 开始前的 commit}
    - HEAD_SHA：{当前 HEAD}
    - 涉及文件：{从 task 提取}
```

**处理 quality reviewer 返回：**
- ✅ 质量通过 → 标记 task 完成，继续下一个 task
- ❌ 发现问题 → 将问题记录到 task，**迭代计数 +1**
  - 如果迭代次数 < 3 → 回到 Step 1 重新派发 implementer
  - 如果迭代次数 ≥ 3 → 停止，TL 亲自介入分析问题

### 6. 循环退出机制

**最大迭代次数：每个 task 最多 3 次审查循环**

当审查发现问题需要退回修复时，必须记录迭代次数：
- 第 1 次迭代：正常修复流程
- 第 2 次迭代：TL 关注，提供更详细指导
- 第 3 次迭代（达到上限）：
  - 停止自动循环
  - TL 必须亲自介入分析根因
  - 考虑拆分 task 或调整需求
  - 记录到 CHANGELOG 并通知 Orchestrator

**迭代计数器示例：**
```
Task: TASK-001 (迭代 1/3)
├── Implementer 执行
├── Spec Review ❌ 发现问题
└── 迭代计数 +1

Task: TASK-001 (迭代 2/3)
├── Implementer 修复
├── Spec Review ✅
├── Quality Review ❌ 发现问题
└── 迭代计数 +1

Task: TASK-001 (迭代 3/3 - 最后机会)
├── Implementer 修复
├── Spec Review ✅
├── Quality Review ✅
└── Task 完成
```

**达到上限时的处理流程：**
1. 停止自动派发
2. TL 执行根因分析（调用 `/systematic-debugging`）
3. 决策：
   - 继续手动修复（TL 亲自指导）
   - 拆分 task 为更小的单元
   - 标记为阻塞，升级到 Orchestrator

### 7. 完成标志

所有 task 完成后：

1. **TL 全量代码审查**（内部执行，非 subagent）
   - 审查范围：`git diff main HEAD -- '*.py' ':!tests/'`
   - 检查模块整体架构与 DESN 一致性
   - 检查跨 task 代码一致性
   - 检查安全隐患（参照 SR-security-rules.md）

2. **自动触发 `/m3-exit`**

### 8. 示例工作流

```
[读取计划文件: docs/plans/DEV-plan-PP-v1.0.md]
[提取所有 5 个 task 的完整文本和上下文]
[创建 TaskCreate 跟踪所有 task]

Task 1: 用户管理 - 用户注册接口

[获取 Task 1 文本和上下文（已预先提取）]
[派发 implementer subagent]

Implementer: "开始前有个问题 - 密码需要加密存储吗？"

TL: "是的，使用 bcrypt，强度 12"

Implementer: "明白了，开始实现..."
[稍后] Implementer:
  - 实现了用户注册接口
  - 测试 5/5 通过
  - 自审查：发现遗漏了密码强度校验，已补充
  - 已提交

[派发 spec reviewer]
Spec reviewer: ✅ 规格合规 - 所有要求已满足，无多余实现

[获取 git SHAs，派发 quality reviewer]
Quality reviewer:
  - 优点：测试覆盖完整，代码整洁
  - 问题：无 Critical/Important 问题
  - 评估：批准

[标记 Task 1 完成]

Task 2: 用户管理 - 用户登录接口

[获取 Task 2 文本和上下文]
[派发 implementer]

Implementer: [无问题，直接开始]
Implementer:
  - 实现了登录接口
  - 测试 8/8 通过
  - 自审查：无问题
  - 已提交

[派发 spec reviewer]
Spec reviewer: ❌ 发现问题:
  - 遗漏需求：缺少登录失败次数限制（src/api/auth.py:45）
  - 多余功能：添加了 remember_me 参数（未在需求中）

[Implementer 修复问题]
Implementer: 移除 remember_me，添加失败次数限制

[Spec reviewer 重新审查]
Spec reviewer: ✅ 规格合规

[派发 quality reviewer]
Quality reviewer:
  - 优点：实现扎实
  - 问题（Important）：失败次数硬编码为 5（应提取为常量）

[Implementer 修复]
Implementer: 提取 MAX_LOGIN_ATTEMPTS 常量

[Quality reviewer 重新审查]
Quality reviewer: ✅ 批准

[标记 Task 2 完成]

...

[所有 task 完成后]
[TL 执行全量代码审查]
[自动触发 /m3-exit]

完成！
```

### 9. 后续流程

自动触发 `/m3-exit` 进入准出检查。

---

## Bug 修复模式（fix）

### 1. 前置检查

#### 1.1 检查 TEST-REPORT 待修复问题

!`grep -A 10 "待修复" docs/TEST-REPORT-*.md 2>/dev/null || echo "未找到待修复 bug"`

**Bug 信息提取：**
| Bug ID | 模块标识 | 模块名称 | 严重程度 | 描述 |
|--------|----------|----------|----------|------|

#### 1.2 检查 worktree 环境

检查所有待修复 bug 对应模块的 worktree 是否存在：

```bash
# 从 TEST-REPORT 提取所有待修复 bug 的模块标识
BUG_MODULES=$(grep -A 10 "待修复" docs/TEST-REPORT-*.md | grep "模块标识" | awk -F'：' '{print $2}' | tr -d ' ' | sort -u)

# 检查每个模块的 worktree
for MODULE in $BUG_MODULES; do
    WORKTREE_PATH=$(grep "| $MODULE |" CLAUDE.md | awk -F'|' '{print $4}' | tr -d ' ')
    if [ ! -d "$WORKTREE_PATH" ]; then
        echo "❌ 模块 $MODULE 的 worktree 不存在: $WORKTREE_PATH"
        exit 1
    fi
done

echo "✅ 所有待修复模块的 worktree 已就绪"
```

### 2. 加载待修复问题清单

从 TEST-REPORT 中提取所有待修复问题的完整详情：

```bash
# 提取所有待修复 bug 详情
grep -A 20 "待修复" docs/TEST-REPORT-*.md > /tmp/bugs-to-fix.txt
```

### 3. TaskCreate（从待修复问题清单获取）

为所有待修复 bug 创建修复任务：

```
TaskCreate:
  subject: "[Bug ID]: [模块名 - Bug 描述]"
  description: "[完整 bug 描述，包含复现步骤、预期结果、实际结果、涉及文件]"
  activeForm: "修复 [Bug ID]"
```

**提前提取原则：** 派发任何 subagent 前，必须先提取所有 bug 的完整文本和上下文，不让 subagent 自己读文件。

### 4. 模块状态跟踪

TL 维护当前正在修复的模块状态：

```bash
# 初始化：当前模块为空
CURRENT_MODULE=""
```

在执行每个 bug 修复 task 前，检查 task 所属模块：
- 如果 task 所属模块 != CURRENT_MODULE → 触发模块切换
- 如果 task 所属模块 == CURRENT_MODULE → 继续执行

### 5. Task 执行循环

对每个 bug 修复 task 按模块分组执行，同一模块内的 task 顺序执行：

#### Step 0: 模块切换（TL 负责）

**TL 在每个模块的第一个 bug 修复 task 开始前自动执行切换：**

```bash
# 从 TEST-REPORT 中提取当前 task 的模块标识
# 假设 bug 格式为：### Bug-001: 问题描述\n- 模块标识：user-auth
TASK_MODULE=$(grep -A 10 "^### $CURRENT_TASK_ID" /tmp/bugs-to-fix.txt | grep "模块标识" | awk -F'：' '{print $2}' | tr -d ' ')

# 判断是否需要切换
if [ "$TASK_MODULE" != "$CURRENT_MODULE" ]; then
    echo "📌 检测到模块切换: $CURRENT_MODULE → $TASK_MODULE"

    # 1. 从 CLAUDE.md 读取 worktree 配置
    WORKTREE_PATH=$(grep "| $TASK_MODULE |" CLAUDE.md | awk -F'|' '{print $4}' | tr -d ' ')
    BRANCH_NAME=$(grep "| $TASK_MODULE |" CLAUDE.md | awk -F'|' '{print $5}' | tr -d ' ')

    if [ -z "$WORKTREE_PATH" ] || [ -z "$BRANCH_NAME" ]; then
        echo "❌ 未找到模块 $TASK_MODULE 的 worktree 配置"
        exit 1
    fi

    # 2. 切换到对应模块的 worktree 和分支
    cd "$WORKTREE_PATH" || {
        echo "❌ 切换到 worktree 失败: $WORKTREE_PATH"
        exit 1
    }

    git checkout "$BRANCH_NAME" || {
        echo "❌ 切换到分支失败: $BRANCH_NAME"
        exit 1
    }

    # 3. 同步 develop 分支最新代码（使用 rebase）
    git fetch origin develop
    git rebase origin/develop || {
        echo "❌ Rebase 冲突，需要手动解决"
        exit 1
    }

    # 4. 确认分支状态
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
        echo "❌ 分支切换失败，当前分支: $CURRENT_BRANCH，期望分支: $BRANCH_NAME"
        exit 1
    fi

    # 确认工作区干净
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️ 工作区有未提交的变更，请先处理"
        git status --short
        exit 1
    fi

    # 5. 更新当前模块状态
    CURRENT_MODULE="$TASK_MODULE"

    echo "✅ 已切换到模块: $TASK_MODULE"
    echo "   - Worktree: $WORKTREE_PATH"
    echo "   - 分支: $BRANCH_NAME"
    echo "   - 当前 task: $CURRENT_TASK_ID"
    echo "   - 已同步 develop 分支最新代码"
else
    echo "✅ 当前已在模块 $TASK_MODULE 中，无需切换"
fi
```

#### Step 1: 派发 Implementer

使用 Agent 工具启动 general-purpose agent，**传递完整任务上下文**：

```
Agent:
  subagent_type: "general-purpose"
  description: "修复 [bug-id] (模块: {module-id})"
  prompt: |
    {implementer-prompt.md 内容}

    ## 任务定义

    **缺陷 ID**: {从 TEST-REPORT 提取 Bug ID，如 BUG-API-001}
    **任务标题**: {从 TEST-REPORT 提取缺陷标题，如"用户管理 - 用户名为空未校验"}
    **模块标识**: {从 TEST-REPORT 提取模块标识}
    **严重级别**: {从 TEST-REPORT 提取严重级别}
    **发现阶段**: {从 TEST-REPORT 提取发现阶段}

    **缺陷描述**:
    {从 TEST-REPORT 原样复制"缺陷描述"部分}

    **复现步骤**:
    {从 TEST-REPORT 原样复制"复现步骤"部分}

    **预期结果**:
    {从 TEST-REPORT 原样复制"预期结果"部分}

    **实际结果**:
    {从 TEST-REPORT 原样复制"实际结果"部分}

    **涉及文件**:
    {从 TEST-REPORT 原样复制"涉及文件"部分}

    **修复要求**:
    1. 使用 TDD 方法修复：先写失败测试（复现 bug），再修复代码，最后验证测试通过
    2. 确保修复不引入新问题
    3. 提交时注明修复的 Bug ID

    ## 模块上下文
    - 模块标识：{module-id}
    - 模块名称：{module-name}
    - Worktree 路径：.worktrees/{module-id}
    - 分支名称：feature/{module-id}

    ## 项目上下文
    - 项目简称：{从 CLAUDE.md 提取}
    - 当前 HEAD：{当前 commit SHA}
    - 技术栈：{从 CLAUDE.md 提取}

    ## 审查意见（如有）
    {如果该 bug 修复有审查意见，列出需要解决的问题}

    **迭代次数**: {当前是第几次迭代，如 1/3}
```

**处理 implementer 返回：**
- 如果 implementer 有疑问 → 回答后重新 dispatch
- 如果 implementer 报告完成 → 继续 Step 2

#### Step 2: 派发 Spec Reviewer

使用 Agent 工具启动 general-purpose agent，**传递模块上下文**：

```
Agent:
  subagent_type: "general-purpose"
  description: "规格审查 [bug-id] (模块: {module-id})"
  prompt: |
    {spec-reviewer-prompt.md 内容}

    ## Bug 定义
    {从 TEST-REPORT 提取的完整 bug 文本}

    ## 模块上下文
    - 模块标识：{module-id}
    - 模块名称：{module-name}
    - Worktree：.worktrees/{module-id}
    - 分支：feature/{module-id}

    ## Git 上下文
    - BASE_SHA：{implementer 开始前的 commit}
    - HEAD_SHA：{当前 HEAD}
    - 涉及文件：{从 bug 提取}
```

**处理 spec reviewer 返回：**
- ✅ 规格合规 → 继续 Step 3
- ❌ 发现问题 → 将问题记录到 task，**迭代计数 +1**
  - 如果迭代次数 < 3 → 回到 Step 1 重新派发 implementer
  - 如果迭代次数 ≥ 3 → 停止，TL 亲自介入分析问题

#### Step 3: 派发 Quality Reviewer

使用 Agent 工具启动 general-purpose agent，**传递模块上下文**：

```
Agent:
  subagent_type: "general-purpose"
  description: "质量审查 [bug-id] (模块: {module-id})"
  prompt: |
    {quality-reviewer-prompt.md 内容}

    ## Bug 定义
    {从 TEST-REPORT 提取的完整 bug 文本}

    ## 模块上下文
    - 模块标识：{module-id}
    - 模块名称：{module-name}
    - Worktree：.worktrees/{module-id}
    - 分支：feature/{module-id}

    ## Git 上下文
    - BASE_SHA：{implementer 开始前的 commit}
    - HEAD_SHA：{当前 HEAD}
    - 涉及文件：{从 bug 提取}
```

**处理 quality reviewer 返回：**
- ✅ 质量通过 → 标记 task 完成，继续下一个 bug 修复 task
- ❌ 发现问题 → 将问题记录到 task，**迭代计数 +1**
  - 如果迭代次数 < 3 → 回到 Step 1 重新派发 implementer
  - 如果迭代次数 ≥ 3 → 停止，TL 亲自介入分析问题

### 6. 循环退出机制

**最大迭代次数：每个 bug 修复 task 最多 3 次审查循环**

当审查发现问题需要退回修复时，必须记录迭代次数：
- 第 1 次迭代：正常修复流程
- 第 2 次迭代：TL 关注，提供更详细指导
- 第 3 次迭代（达到上限）：
  - 停止自动循环
  - TL 必须亲自介入分析根因
  - 考虑调整修复策略或升级问题
  - 记录到 CHANGELOG 并通知 Orchestrator

**迭代计数器示例：**
```
Bug Fix: BUG-001 (迭代 1/3)
├── Implementer 执行
├── Spec Review ❌ 发现问题
└── 迭代计数 +1

Bug Fix: BUG-001 (迭代 2/3)
├── Implementer 修复
├── Spec Review ✅
├── Quality Review ❌ 发现问题
└── 迭代计数 +1

Bug Fix: BUG-001 (迭代 3/3 - 最后机会)
├── Implementer 修复
├── Spec Review ✅
├── Quality Review ✅
└── Bug 修复完成
```

**达到上限时的处理流程：**
1. 停止自动派发
2. TL 执行根因分析（调用 `/systematic-debugging`）
3. 决策：
   - 继续手动修复（TL 亲自指导）
   - 调整修复策略
   - 标记为阻塞，升级到 Orchestrator

### 7. 完成标志

所有 bug 修复 task 完成后：

1. **TL 全量代码审查**（内部执行，非 subagent）
   - 审查范围：`git diff develop HEAD -- '*.py' ':!tests/'`
   - 检查修复是否引入新问题
   - 检查跨 bug 修复的代码一致性
   - 检查安全隐患（参照 SR-security-rules.md）

2. **自动触发 `/m3-exit`**

### 8. 示例工作流

```
[读取 TEST-REPORT: docs/TEST-REPORT-PP-v1.0.md]
[提取所有 3 个待修复 bug 的完整文本和上下文]
[创建 TaskCreate 跟踪所有 bug 修复 task]

Bug 1: 用户登录失败次数限制未生效

[获取 Bug 1 文本和上下文（已预先提取）]
[切换到 user-auth 模块 worktree]
[同步 develop 分支最新代码（rebase）]
[派发 implementer subagent]

Implementer: "开始前有个问题 - 失败次数应该存储在哪里？"

TL: "使用 Redis 缓存，key 格式：login_fail:{user_id}，TTL 30分钟"

Implementer: "明白了，开始修复..."
[稍后] Implementer:
  - 分析根因：失败次数计数器未持久化
  - 修复：添加 Redis 缓存存储失败次数
  - 测试：新增测试用例验证失败次数限制
  - 测试 3/3 通过
  - 已提交

[派发 spec reviewer]
Spec reviewer: ✅ 规格合规 - 修复符合需求

[获取 git SHAs，派发 quality reviewer]
Quality reviewer:
  - 优点：修复扎实，测试覆盖完整
  - 问题：无 Critical/Important 问题
  - 评估：批准

[标记 Bug 1 修复完成]

Bug 2: 用户注册时邮箱格式校验失效

[获取 Bug 2 文本和上下文]
[当前已在 user-auth 模块，无需切换]
[派发 implementer]

Implementer: [无问题，直接开始]
Implementer:
  - 分析根因：正则表达式错误
  - 修复：更正邮箱校验正则
  - 测试：新增边界测试用例
  - 测试 5/5 通过
  - 已提交

[派发 spec reviewer]
Spec reviewer: ✅ 规格合规

[派发 quality reviewer]
Quality reviewer: ✅ 批准

[标记 Bug 2 修复完成]

Bug 3: 订单状态流转异常

[获取 Bug 3 文本和上下文]
[检测到模块切换: user-auth → order-mgmt]
[切换到 order-mgmt 模块 worktree]
[同步 develop 分支最新代码（rebase）]
[派发 implementer]

Implementer:
  - 分析根因：状态机缺少边界条件检查
  - 修复：添加状态流转前置检查
  - 测试：新增状态流转测试用例
  - 测试 4/4 通过
  - 已提交

[派发 spec reviewer]
Spec reviewer: ✅ 规格合规

[派发 quality reviewer]
Quality reviewer: ✅ 批准

[标记 Bug 3 修复完成]

[所有 bug 修复完成后]
[TL 执行全量代码审查]
[自动触发 /m3-exit]

完成！
```

### 9. 后续流程

自动触发 `/m3-exit` 进入准出检查。

---

## 关联 Skills

**前置依赖：**
- `/m3-write-dev-plan` - 创建本 skill 执行的开发计划（开发模式）
- `/create-worktrees` - 已创建开发 worktree（M2 准出时自动创建）
- `/m4-test-api` 或 `/m4-test-e2e` - 生成 TEST-REPORT（Bug 修复模式）

**后续流程：**
- `/m3-exit` - 所有 task 完成后自动触发，执行准出检查

**Subagent 可能使用：**
- `/systematic-debugging` - TL 在迭代次数达到上限时调用
- TDD 原则 - 每个 implementer 遵循 TDD 流程
- 项目规约 - SR-security-rules.md, DR-design-rules.md 等

---

## 关键原则

- **禁止并行派发**：一次只派发一个 implementer，避免冲突（参照 RL-DV-0008）
- **必须顺序审查**：spec review 通过后才能 quality review
- **完整审查循环**：任何审查不通过，必须走完整的三步循环
- **循环次数限制**：每个 task 最多 3 次迭代，超过需 TL 介入（参照 RL-DB-0001）
- **不得手动修复**：发现问题必须派发 implementer 修复，防止 context pollution
- **提前提取上下文**：派发前必须提取完整 task 文本和上下文，不让 subagent 自己读文件

---

## Red Flags（引用红线清单）

### 引用红线规约

**代码管理类（RL-redlines.md）：**
- RL-DV-0001: 不允许在 main/master 分支直接开发（阻断）
- RL-DV-0002: 代码修改完成必须提交 git（警告）
- RL-DV-0003: 单元测试未全部通过不得提交 git（阻断）
- RL-DV-0008: 业务代码开发必须在 worktree 隔离工作区中进行（阻断）

**调试规范类（RL-redlines.md）：**
- RL-DB-0001: 遇到 bug 必须先找根因再修复，禁止猜测性修复；3次修复失败必须停止并向 TL 汇报（阻断）

**验证与声明类（RL-redlines.md）：**
- RL-VF-0001: 声明完成前必须有新鲜的验证证据（阻断）
- RL-VF-0002: 禁止使用"should work"、"probably fixed"等未验证表述（警告）
- RL-VF-0003: 禁止使用"let me try this and see"（猜测性修复）（警告）

**代码审查类（RL-redlines.md）：**
- RL-RV-0001: 禁止表演性同意审查意见（"You're absolutely right!"等），必须验证后再实现（警告）

### 本 Skill 特定禁止项

**流程控制：**
- 跳过任何审查（spec compliance 或 code quality）
- 在 spec compliance 通过前进行 code quality review（顺序错误）
- 在问题未修复时继续下一步
- 在任一审查有未解决问题时进入下一个 task
- 跳过重新审查（有问题 = 修复 = 重新审查）

**Subagent 管理：**
- 并行派发多个 implementer（会产生冲突，参照 RL-DV-0008）
- 让 subagent 自己读取计划文件（必须提供完整文本）
- 跳过上下文说明（subagent 需要理解 task 在整体中的位置）
- 忽略 subagent 的提问（必须在继续前回答）
- 用 implementer 自审查替代正式审查（两者都需要）
- 手动修复问题（必须派发 implementer，防止 context pollution）

**质量标准：**
- 接受"差不多"的规格合规（有问题 = 未完成）

### 应对策略

**如果 subagent 提问：**
- 清晰完整地回答
- 如需要提供额外上下文
- 不要催促他们开始实现

**如果 reviewer 发现问题：**
- 派发 implementer 修复
- Reviewer 重新审查
- 循环直到通过
- 不要跳过重新审查

**如果 subagent 失败：**
- 派发修复 subagent 并提供具体指令
- 不要尝试手动修复（context pollution）
