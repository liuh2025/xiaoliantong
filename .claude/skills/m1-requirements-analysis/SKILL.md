---
name: m1-requirements-analysis
description: 进入 M1 需求澄清阶段，加载 BA 角色定义和业务规约。当用户说"开始需求分析"、"进入M1"、"需求澄清"时自动触发。
---

## 加载规则
- !`cat docs/rules/prompts/ba-prompt.md 2>/dev/null || echo "[ba-prompt.md 未找到，请先初始化项目规约]"`
- !`cat docs/rules/BR-business-rules.md 2>/dev/null || echo "[BR-business-rules.md 未找到]"`

## 完成标志
当你与用户就需求达成共识后，提示用户：
"需求已澄清，可以使用 `/write-prd` 编写正式 PRD 文档"
