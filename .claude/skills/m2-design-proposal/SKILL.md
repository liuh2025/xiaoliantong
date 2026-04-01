---
name: m2-design-proposal
description: 进入 M2 设计阶段，ARCH 提出 2-3 个设计方案供用户选择。当用户说"开始设计"、"进入M2"、"出设计方案"时自动触发。
---

## 前置检查
!`grep -h "status:" docs/PRD-*.md 2>/dev/null | head -1 || echo "未找到 PRD 文档"`
若 PRD 状态不是"已批准"，停止并提示用户先完成 M1 准出（PRD 状态=已批准）。

## 加载规则
- !`cat docs/rules/prompts/arch-prompt.md 2>/dev/null || echo "[arch-prompt.md 未找到]"`
- !`cat docs/rules/DR-design-rules.md 2>/dev/null || echo "[DR-design-rules.md 未找到]"`

## 当前任务
基于已批准的 PRD，提出 2-3 个设计方案，每个方案覆盖架构分层、数据库设计概要、接口设计概要，列出优缺点和推荐理由。

## 完成标志
与用户选定方案后，提示："方案已选定，使用 `/write-design` 展开详细设计文档"
