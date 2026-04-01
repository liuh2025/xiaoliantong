---
name: m6-acceptance
description: 进入 M6 验收阶段，等待用户验收确认。当用户说"开始验收"、"进入M6"时自动触发。
---

你现在作为 Orchestrator 角色工作。

## 前置检查
!`grep "当前阶段:" CLAUDE.md 2>/dev/null | head -1 || echo "未找到 CLAUDE.md"`
若当前阶段不是 M6，停止并提示用户先完成 M5。

## 验收准备
向用户展示本项目交付物清单：
!`ls docs/PRD-*.md docs/DESN-*.md docs/CHK-*.md docs/QA-test-plan-*.md docs/TEST-REPORT-*.md docs/DEPLOY-TEST-*.md 2>/dev/null`

提示用户：
"请确认以上交付物是否符合预期，确认后请明确说'验收通过'。
若有问题请描述，将派发对应阶段处理：
- 功能问题 → 回 M3 回环
- 测试遗漏 → 回 M4
- 部署问题 → 回 M5"

## 完成标志
用户明确说"验收通过" →
1. 在 CLAUDE.md 中记录验收时间
2. 自动触发 `/m6-retrospective`
