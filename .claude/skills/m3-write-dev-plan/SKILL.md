---
name: m3-write-dev-plan
description: 进入 M3 开发阶段，TL 读取 PRD、DESN 拆分覆盖所有模块的详细实施计划。
---

# 上下文压缩
执行 `/compact` 命令来压缩当前对话历史。
根据以下指导进行压缩：
-移除冗余的探索性对话
-移除冗余的与用户逐条确认的内容
-移除其他角色定义与规约

## 角色
你现在作为 TL（技术负责人）角色工作，负责编制覆盖所有模块的开发计划。

## 多模块计划说明

本项目的开发计划**覆盖所有模块**，按 DESN 中定义的迭代顺序组织：

```
DESN 2.1 模块清单
    │
    │ 按迭代顺序提取模块
    ▼
DEV-plan 结构
    │
    ├── 模块1（迭代顺序=1）
    │   ├── task-001: xxx
    │   ├── task-002: xxx
    │   └── ...
    │
    ├── 模块2（迭代顺序=2）
    │   ├── task-xxx: xxx
    │   └── ...
    │
    └── 模块N（迭代顺序=N）
        └── ...

执行时：m3-subagent-development 按模块顺序依次在各模块 worktree 中开发
```

## 前置检查
!`grep "当前阶段:" CLAUDE.md 2>/dev/null | head -1 || echo "未找到 CLAUDE.md"`
!`grep -h "status:" docs/PRD-*.md 2>/dev/null | head -1 || echo "未找到 PRD 文档"`
!`grep -h "status:" docs/DESN-*.md 2>/dev/null | head -1 || echo "未找到 DESN 文档"`
若 PRD、DESN 状态不是"已批准"，停止并提示用户先完成 M2。

## 加载规则
### TL角色的具体定义
!`cat docs/rules/prompts/tl-prompt.md 2>/dev/null || echo "[tl-prompt.md 未找到]"`
### 开发计划编写规范
!`cat docs/rules/DEV-plan-writing-rules.md 2>/dev/null || echo "[DEV-plan-writing-rules.md 未找到]"`


## 加载基线文档
!`cat docs/PRD-*.md 2>/dev/null || echo "[PRD 未找到]"`（前端 task 需参考 UI 原型和交互设计，后端task需参考功能业务逻辑）
!`cat docs/DESN-*.md 2>/dev/null || echo "[DESN 未找到]"`（架构、数据库、接口设计）

## 编写开发计划

### 计划文件路径
`docs/plans/DEV-plan-{项目简称}-v1.0.md`

## 计划确认

计划编写完成后，展示给用户：

```
开发计划已保存到 `docs/plans/DEV-plan-{项目简称}-v1.0.md`

共拆分 {N} 个 task，涵盖以下模块：
- [模块1]：task-001 ~ task-003
- [模块2]：task-004 ~ task-006
...

请确认计划是否合理。确认后输入 `/m3-subagent-development` 开始执行。
```

## 完成标志
用户确认计划后，提示输入 `/m3-subagent-development` 开始执行。
