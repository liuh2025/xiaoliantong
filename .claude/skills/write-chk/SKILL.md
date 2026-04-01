---
name: write-chk
description: 编写一致性检查报告。测试计划完成后，调用此 Skill 生成正式CHK。
user-invocable: false
---

## 前置检查
!`grep "status:" docs/QA-test-plan-*.md 2>/dev/null | head -1 || echo "[未找到测试计划]"`
若测试计划状态不是"已批准"，停止并提示用户先批准测试计划。

# 上下文压缩
执行 `/compact` 命令来压缩当前对话历史。
根据以下指导进行压缩：
-移除冗余的探索性对话
-移除冗余的与用户逐条确认的内容
-移除其他角色定义与规约

## 加载规则
- !`cat docs/rules/prompts/qa-prompt.md 2>/dev/null || echo "[qa-prompt.md 未找到]"`
- !`cat docs/PRD-*.md 2>/dev/null || echo "[PRD 未找到]"`
- !`cat docs/DESN-*.md 2>/dev/null || echo "[DESN 未找到]"`
- !`cat docs/QA-test-plan-*.md 2>/dev/null || echo "[测试计划未找到]"`

## 检查范围
对照 PRD，检查 DESN 和 test-plan 针对需求范围的一致性：
1. PRD 中每个功能需求是否在 DESN 中有对应设计
2. PRD 中每个功能需求是否在 test-plan 中有对应测试用例
3. DESN 中是否有超出 PRD 范围的设计
4. test-plan 中是否有遗漏的需求覆盖

## 加载模板
- !`cat docs/templates/CHK-template.md 2>/dev/null && echo "[已加载 CHK 模板]" || echo "[CHK 模板未找到]"`

## 执行步骤
1. 编写 `docs/CHK-{项目简称}-v1.0.md`
2. 列出一致性检查结果，标记不一致项
3. 初始状态为"草稿"
4. 向用户展示检查报告，询问是否需要修改
5. 用户确认后，将状态更新为"待审批"

## 完成标志
用户明确说"一致性检查批准"后，将状态更新为"已批准"，自动触发 `/m2-exit`
