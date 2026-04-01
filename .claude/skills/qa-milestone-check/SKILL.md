---
name: qa-milestone-check
description: QA 里程碑准出检查，在每个 m*-exit 开始时由 Orchestrator 触发。使用 subagent 执行独立审查。
user-invocable: false
argument-hint: "--stage M1|M2|M3|M4|M5|M6"
context: fork
agent: general-purpose
allowed-tools: Read, Grep, Glob, Bash
---

## 角色定义

加载 QA 角色定义：
!`cat docs/rules/prompts/qa-prompt.md 2>/dev/null || echo "[qa-prompt.md 未找到]"`

## 执行方式

根据 qa-prompt.md 中的角色定义、职责范围、工作原则（分阶段）、红线检查、参考脚本、报告格式执行审查。

## 参数

阶段: {从 $ARGUMENTS 获取，如 M1、M2、M3、M4、M5、M6}

## 完成标志

按 qa-prompt.md 中定义的报告格式返回结果：
- ✅ 全部通过 → 返回 `{ "passed": true, "stage": "{阶段}" }`
- ❌ 有问题 → 返回 `{ "passed": false, "stage": "{阶段}", "issues": [...] }`
