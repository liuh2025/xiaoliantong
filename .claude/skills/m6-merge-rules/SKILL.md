---
name: m6-merge-rules
description: 将用户确认的新增规则合并到对应规约文件。由 m6-retrospective 用户确认后自动触发。
user-invocable: false
---

你现在作为 Orchestrator 角色工作。

## 读取新增规则清单
!`cat docs/NEW-RULES-*.md 2>/dev/null || echo "[新增规则清单未找到，请先运行 /m6-retrospective]"`

## 逐条合并
对每条规则，追加到对应规约文件末尾：
- BR-xxx → docs/rules/BR-business-rules.md
- DR-xxx → docs/rules/DR-design-rules.md
- TR-xxx → docs/rules/TR-test-rules.md
- RL-xxx → docs/rules/RL-redlines.md
- SR-xxx → docs/rules/SR-security-rules.md

合并时保持文件原有格式和编号顺序，不得覆盖已有规则。

## 完成后
输出合并摘要：各文件新增了哪些规则编号
自动触发 `/m6-exit`
