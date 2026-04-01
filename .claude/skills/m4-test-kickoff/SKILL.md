---
name: m4-test-kickoff
description: 进入 M4 测试阶段，Tester 读取测试计划并启动分层测试。当用户说"开始测试"、"进入M4"时自动触发。
---

你现在作为 Tester 角色工作。

## 前置检查

!`grep "当前阶段:" CLAUDE.md 2>/dev/null | head -1 || echo "未找到 CLAUDE.md"`

若当前阶段不是 M4，停止并提示用户先完成 M3。

## 加载规则

!`cat docs/rules/prompts/tester-prompt.md 2>/dev/null || echo "[tester-prompt.md 未找到]"`
!`cat docs/rules/TR-test-rules.md 2>/dev/null || echo "[TR-test-rules.md 未找到]"`
!`ABBR=$(grep "项目简称" CLAUDE.md | grep -oP '(?<=: ).*' | tr -d '[:space:]'); cat docs/QA-test-plan-${ABBR}-*.md 2>/dev/null || echo "[QA-test-plan-${ABBR}-*.md 未找到]"`

## 测试分层说明

M4 测试分为两层：

| 层级 | 名称 | 覆盖范围 | 执行方式 |
|------|------|---------|---------|
| L1 | API 测试 | 所有接口（RPC/RESTful/MQ）正例、反例、边界值、业务规则 | Subagent 自动生成脚本并执行 |
| L2 | E2E 测试 | 用户操作流程，主流程/核心功能 100%，含异常测试 | Subagent 自动生成脚本并执行 |

## 目录结构

```
tests/
├── unit/                        # 单元测试（M3 已完成）
├── integration/                 # L1 API 测试
│   ├── script/                  # 测试脚本
│   └── log/                     # 执行日志（按时间分目录）
├── e2e/                         # L2 E2E 测试
│   ├── script/                  # 测试脚本（Page Object 模式）
│   ├── screenshots/             # 测试截图（按时间分目录）
│   └── log/                     # 执行日志（按时间分目录）
└── test-data/                   # 测试数据
```

## 执行流程

```
m4-test-kickoff
    │
    ▼
m4-test-api（L1 API 测试）
    │
    ├── 全部通过 ──► m4-test-e2e（L2 E2E 测试）
    │                    │
    │                    ├── 全部通过 ──► m4-exit
    │                    └── 有问题 ──► m3-tl-bug-fix --all
    │
    └── 有问题 ──► m3-tl-bug-fix --all
```

## 人工检查说明

人工检查发现的问题**不在自动化流程内**，直接作为缺陷登记在 TEST-REPORT 中。

## 完成标志

自动触发 `/m4-test-api` 启动 L1 API 测试。
