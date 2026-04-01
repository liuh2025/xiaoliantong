---
name: write-test-plan
description: 编写测试计划。设计文档完成后，调用此 Skill 生成正式QA-test-plan。
user-invocable: false
---

## 前置检查
!`grep "status:" docs/DESN-*.md 2>/dev/null | head -1 || echo "[未找到 DESN]"`
若 DESN 状态不是"已批准"，停止并提示用户先批准 DESN。

# 上下文压缩
执行 `/compact` 命令来压缩当前对话历史。
根据以下指导进行压缩：
-移除冗余的探索性对话
-移除冗余的与用户逐条确认的内容
-移除其他角色定义与规约

## 加载规则
- !`cat docs/rules/prompts/tester-prompt.md 2>/dev/null || echo "[tester-prompt.md 未找到]"`
- !`cat docs/rules/TR-test-rules.md 2>/dev/null || echo "[TR-test-rules.md 未找到]"`
- !`cat docs/PRD-*.md 2>/dev/null || echo "[PRD 未找到]"`
- !`cat docs/DESN-*.md 2>/dev/null || echo "[DESN 未找到]"`

## 加载模板
- !`cat docs/templates/QA-test-plan-template.md 2>/dev/null && echo "[已加载 test-plan 模板]" || echo "[test-plan 模板未找到]"`

## 执行步骤
1. 基于 PRD 和 DESN，编写 `docs/QA-test-plan-{项目简称}-{最新版本号}.md`
2. 包含 L1 API 测试 + L2 E2E 测试用例，标记冒烟测试用例
3. 初始状态为"草稿"
4. 逐节向用户展示测试计划，询问是否需要修改，每节确认后再继续下一节
5. 全部章节确认后，将状态更新为"待审批"

## 完成标志
用户明确说"测试计划批准"后，将状态更新为"已批准"，自动触发 `/write-chk`
