# XiaoLianTong - Claude Code 工程实践配置

> 本文件为 Claude Code 项目级配置文件，定义项目规范、当前阶段、全局规约加载。

---

## 项目信息

- **项目名称**: XiaoLianTong
- **项目简称**: XLT
- **当前阶段**: M0（初始化）
- **当前版本**: v0.1.0
- **技术栈**:  {实际技术栈}
- **开发模式**: TDD + 六阶段里程碑管理

---

## 里程碑流程

```
M0 初始化  →  M1 需求  →  M2 设计  →  M3 开发  →  M4 测试  →  M5 部署  →  M6 验收
```

### M0 初始化阶段
- **触发条件**: 用户说"初始化项目"、"开始新项目"
- **执行 Skill**: `/m0-init`
- **产出物**: 目录结构、配置文件、规约库、文档模板
- **准出条件**: 项目初始化完成，CLAUDE.md 配置完成

### 当前阶段状态
- **当前阶段**: M0
- **当前阶段状态**: 草稿
- **准出条件**: 项目初始化完成，CLAUDE.md 配置完成

**文档状态标记说明**：所有阶段产出文档（PRD、DESN、CHK、QA-test-plan 等）必须在文件开头使用 YAML frontmatter 标记状态：
```yaml
---
status: 草稿 | 待审批 | 已批准 | 已归档
---
```
### 文档状态流转

| 状态  | 含义            | 转入条件    | 转出条件    |
| --- | ------------- | ------- | ------- |
| 草稿  | 文档正在编写中       | 文档创建时   | 作者完成初稿  |
| 待审批 | 已提交，等待用户批准    | 作者声明完成  | 用户批准或退回 |
| 已批准 | 用户已批准，可作为准出依据 | 用户明确批准  | 发起变更流程  |
| 已归档 | 项目结束后归档       | M6 验收通过 | —       |

---

## 全局规约加载

以下规约文件在所有阶段、所有角色中强制加载：

### Orchestrator 角色
@docs/rules/prompts/orchestrator-prompt.md

### 安全规约（阻断级别）
@docs/rules/SR-security-rules.md

### 红线清单（阻断级别）
@docs/rules/RL-redlines.md

### Git 规范
@docs/rules/GIT-rules.md

### 异常处理规范
@docs/rules/EXCEPTION-rules.md

---

## 角色体系

本项目采用标准角色体系，各角色定义见 `docs/rules/prompts/` 目录：

| 角色                   | 职责                     | 提示文件                           |
| -------------------- | ---------------------- | ------------------------------ |
| Orchestrator         | 里程碑管理、阶段推进、subAgent 调度 | orchestrator-prompt.md         |
| BA                   | 需求分析、PRD 编写            | ba-prompt.md                   |
| ARCH                 | 系统设计、数据库设计、接口设计        | arch-prompt.md                 |
| TL                   | 任务拆分、流水线管理、全量代码审查      | tl-prompt.md                   |
| Tester               | 测试计划、用例执行、测试报告         | tester-prompt.md               |
| QA                   | 质量保障、流程合规、红线检查         | qa-prompt.md                   |

**M3 开发角色（集成在 m3-subagent-development skill 中）：**
- DEV-Implementer：TDD 实现、自审查
- DEV-Spec-Reviewer：规格合规审查
- DEV-Quality-Reviewer：代码质量审查

这些角色的 prompt 模板位于 `.claude/skills/m3-subagent-development/` 目录。


---

## 质量门禁

### M1 需求阶段准出（write-prd）
- [ ] PRD 状态 = 已批准
- [ ] PRD基线已提交
### M2 设计阶段准出（commit-baseline）
- [ ] DESN 状态 = 已批准
- [ ] CHK 状态 = 已批准
- [ ] QA-test-plan 状态 = 已批准
- [ ] 开发 worktree 创建完毕（由 commit-baseline 自动创建）

### M3 开发阶段准出（m3-exit）
- [ ] 所有 task 状态 = 已完成（由 m3-subagent-development 管理）
- [ ] 静态代码扫描无阻断问题（flake8 / bandit）
- [ ] 单元测试 100% 通过
- [ ] TL 全量代码审查通过（集成在 m3-subagent-development 中）

### M4 测试阶段准出（m4-exit）
- [ ] TEST-REPORT 无待执行项
- [ ] TEST-REPORT 无待修复项
- [ ] L1 API 测试 100% 通过
- [ ] L2 E2E 截图完整（tests/e2e/screenshots/）
- [ ] L2 E2E 测试 100% 通过
- [ ] QA 已签署审查意见

### M5 部署阶段准出（m5-exit）
- [ ] 健康检查通过
- [ ] 冒烟测试全部通过
- [ ] 冒烟截图完整（tests/screenshots/smoke/）
- [ ] QA 已签署审查意见

### M6 验收阶段准出（m6-exit）
- [ ] 用户验收通过（m6-acceptance 确认）
- [ ] 回顾会议完成（m6-retrospective）
- [ ] CHANGELOG 归档完成
- [ ] 所有交付物文档状态 = 已归档

---

## 目录结构

```
XiaoLianTong/
├── CLAUDE.md                    # 本文件
├── docs/
│   ├── rules/                   # 规约库
│   │   ├── BR-business-rules.md
│   │   ├── DR-design-rules.md
│   │   ├── TR-test-rules.md
│   │   ├── SR-security-rules.md
│   │   ├── RL-redlines.md
│   │   ├── GIT-rules.md
│   │   ├── EXCEPTION-rules.md
│   │   ├── DEV-plan-writing-rules.md
│   │   └── prompts/             # 角色定义
│   │       ├── orchestrator-prompt.md
│   │       ├── ba-prompt.md
│   │       ├── arch-prompt.md
│   │       ├── tl-prompt.md
│   │       ├── tester-prompt.md
│   │       └── qa-prompt.md
│   ├── plans/                   # 开发计划
│   │   └── DEV-plan-PP-v1.0.md  # M3 开发计划
│   ├── templates/               # 文档模板（M0 初始化）
│   │   ├── PRD-template.md
│   │   ├── DESN-template.md
│   │   ├── CHK-template.md
│   │   ├── QA-test-plan-template.md
│   │   ├── TEST-REPORT-template.md
│   │   ├── DEPLOY-TEST-template.md
│   │   ├── DEV-plan-template.md
│   │   └── CHANGELOG-template.md
│   ├── PRD-PP-v1.0.md           # 需求文档（M1 产出）
│   ├── DESN-PP-v1.0.md          # 设计文档（M2 产出）
│   ├── CHK-PP-v1.0.md           # 一致性检查（M2 产出）
│   ├── QA-test-plan-PP-v1.0.md  # 测试计划（M2 产出）
│   ├── TEST-REPORT-PP-v1.0.md   # 测试报告（M4 产出）
│   ├── DEPLOY-TEST-PP-v1.0.md   # 部署测试报告（M5 产出）
│   └── CHANGELOG-PP.md          # 变更日志
├── src/                         # 源代码
├── tests/
│   ├── unit/                    # L1 单元测试（M3 开发阶段）
│   │   └── {module}/            # 按模块组织
│   │       └── test_*.py        # 开发人员 TDD 编写
│   │
│   ├── integration/             # L1 API 测试（M4 测试阶段）
│   │   ├── script/              # 测试脚本
│   │   │   ├── conftest.py
│   │   │   └── test_api_*.py
│   │   └── log/                 # 执行日志（按时间分目录）
│   │       └── {YYYY-MM-DD_HHMMSS}/
│   │
│   ├── e2e/                     # L2 E2E 测试（M4 测试阶段）
│   │   ├── script/              # 测试脚本（Page Object 模式）
│   │   │   ├── pages/           # Page Object 定义
│   │   │   ├── conftest.py
│   │   │   └── test_e2e_*.py
│   │   ├── screenshots/         # 测试截图（按时间分目录）
│   │   │   └── {YYYY-MM-DD_HHMMSS}/
│   │   │       ├── TC-E2E-001-成功.png
│   │   │       └── TC-E2E-001-失败-{原因}.png
│   │   └── log/                 # 执行日志（按时间分目录）
│   │       └── {YYYY-MM-DD_HHMMSS}/
│   │
│   ├── screenshots/             # 冒烟测试截图（M5）
│   │   └── smoke/
│   └── test-data/               # 测试数据
└── .claude/
    └── skills/                  # Skills 目录
        ├── m0-init/             # M0 项目初始化
        ├── m1-requirements-analysis/
        ├── m2-design-proposal/
        ├── m3-write-dev-plan/
        ├── m3-subagent-development/  # M3 主 skill（含 prompt 模板）
        │   ├── SKILL.md
        │   ├── implementer-prompt.md
        │   ├── spec-reviewer-prompt.md
        │   └── quality-reviewer-prompt.md
        ├── m3-exit/
        ├── m4-test-kickoff/     # M4 测试启动
        ├── m4-test-api/         # L1 API 测试
        ├── m4-test-e2e/         # L2 E2E 测试
        ├── m4-qa-review/        # QA 审查
        ├── m4-exit/             # M4 准出
        ├── m5-deploy/
        ├── m6-acceptance/
        └── check/               # 检查工具
            └── check-skills-integrity.sh
```

---

## Skills 加载时机与规约引用

> 本章节说明各 skill 在项目各阶段的作用、触发时机、加载的规约文件，供 Claude 在回答问题时查找相关规约。

### M0 初始化阶段

| Skill | 触发时机 | 作用 | 加载规约 |
|-------|---------|------|---------|
| `/m0-init` | 用户说"初始化项目"、"开始新项目" | 创建目录结构、配置文件、规约库、文档模板 | 无（创建规约文件） |

### M1 需求阶段

| Skill                       | 触发时机               | 作用              | 加载规约                                                                   |
| --------------------------- | ------------------ | --------------- | ---------------------------------------------------------------------- |
| `/m1-requirements-analysis` | 用户说"开始需求分析"、"进入M1" | 加载 BA 角色，进行需求澄清 | `docs/rules/prompts/ba-prompt.md`<br>`docs/rules/BR-business-rules.md` |
| `/write-prd`                | 需求澄清完成后            | 生成正式 PRD 文档     | `docs/templates/PRD-template.md`                                       |
| `/m1-exit`                  | PRD 已批准后           | 准出检查，更新阶段到 M2   | 无                                                                      |

### M2 设计阶段

| Skill | 触发时机 | 作用 | 加载规约 |
|-------|---------|------|---------|
| `/m2-design-proposal` | 用户说"开始设计"、"进入M2" | ARCH 提出 2-3 个设计方案 | `docs/rules/prompts/arch-prompt.md`<br>`docs/rules/DR-design-rules.md` |
| `/write-design` | 方案选定后 | 生成正式 DESN 文档 | `docs/templates/DESN-template.md` |
| `/write-test-plan` | 设计文档完成后 | 生成正式 QA-test-plan 文档 | `docs/templates/QA-test-plan-template.md`<br>`docs/rules/TR-test-rules.md` |
| `/write-chk` | 测试计划完成后 | 生成一致性检查报告 | `docs/templates/CHK-template.md` |
| `/m2-exit` | 所有文档已批准后 | 准出检查，创建 worktree，更新阶段到 M3 | 无 |
| `/create-worktrees` | m2-exit 自动触发 | 创建所有模块的 worktree | 无 |

### M3 开发阶段

| Skill                      | 触发时机                | 作用                                | 加载规约                                                                                                                                                                                                                                   |
| -------------------------- | ------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/m3-write-dev-plan`       | 用户说"开始开发"、"进入M3"    | TL 拆分详细实施计划                       | `docs/rules/prompts/tl-prompt.md`<br>`docs/rules/DEV-plan-writing-rules.md`                                                                                                                                                            |
| `/m3-subagent-development` | 开发计划完成后             | 使用 Task 工具派发 implementer/reviewer | `.claude/skills/m3-subagent-development/implementer-prompt.md`<br>`.claude/skills/m3-subagent-development/spec-reviewer-prompt.md`<br>`.claude/skills/m3-subagent-development/quality-reviewer-prompt.md`<br>`docs/rules/TDD-rules.md` |
| `/m3-exit`                 | TL final review 通过后 | 准出检查，合并到 develop，更新阶段到 M4         | 无                                                                                                                                                                                                                                      |
| `/git-merge`               | m3-exit 自动触发        | 安全合并分支（冲突检测 + rebase）             | 无                                                                                                                                                                                                                                      |

### M4 测试阶段

| Skill | 触发时机 | 作用 | 加载规约 |
|-------|---------|------|---------|
| `/m4-test-kickoff` | 用户说"开始测试"、"进入M4" | Tester 读取测试计划，启动分层测试 | `docs/rules/prompts/tester-prompt.md`<br>`docs/rules/TR-test-rules.md` |
| `/m4-test-api` | m4-test-kickoff 自动触发 | 执行 L1 API 测试 | `docs/QA-test-plan-PP-v1.0.md` |
| `/m4-test-e2e` | m4-test-api 完成后 | 执行 L2 E2E 测试 | `docs/QA-test-plan-PP-v1.0.md` |
| `/m3-subagent-development` | E2E 发现 bug 时 | Bug 修复（rebase + TDD） | 同 M3 |
| `/m4-exit` | QA 审查通过后 | 准出检查，合并到 main，更新阶段到 M5 | 无 |
| `/git-merge` | m4-exit 自动触发 | 合并 develop → main | 无 |
| `/git-cleanup` | m4-exit 自动触发 | 清理 feature 分支和 worktree | 无 |

### M5 部署阶段

| Skill | 触发时机 | 作用 | 加载规约 |
|-------|---------|------|---------|
| `/m5-deploy` | 用户说"开始部署"、"进入M5" | ARCH 执行 docker compose 部署 | `docs/rules/prompts/arch-prompt.md` |
| `/m5-exit` | QA 审查通过后 | 准出检查，更新阶段到 M6 | 无 |

### M6 验收阶段

| Skill | 触发时机 | 作用 | 加载规约 |
|-------|---------|------|---------|
| `/m6-acceptance` | 用户说"开始验收"、"进入M6" | 等待用户验收确认 | 无 |
| `/m6-retrospective` | 验收通过后 | BA+ARCH+TL 联合复盘 | `docs/CHANGELOG-PP.md` |
| `/m6-merge-rules` | 复盘完成后 | 合并新增规则到规约文件 | `docs/rules/*.md` |
| `/m6-exit` | 规则合并完成后 | 归档，提交最终基线 | 无 |
| `/git-cleanup` | m6-exit 自动触发 | 清理 develop 分支 | 无 |

### 通用工具 Skills

| Skill                   | 触发时机           | 作用          | 加载规约                              |
| ----------------------- | -------------- | ----------- | --------------------------------- |
| `/qa-milestone-check`   | 每个 m*-exit 开始时 | QA 独立审查准出条件 | `docs/rules/prompts/qa-prompt.md` |
| `/systematic-debugging` | 遇到 bug、测试失败时   | 系统性调试，找根因   | `docs/rules/EXCEPTION-rules.md`   |
| `/git-baseline-commit`  | 各 m*-exit 调用   | 提交阶段基线      | `docs/rules/GIT-rules.md`         |

当遇到用户问题，或自动进入到相应阶段，应严格按照以下步骤执行：
步骤 1: 识别问题涉及哪个 skill
  - 问题：在 m3-write-dev-plan 中...
  - Skill: /m3-write-dev-plan

  步骤 2: 查看 CLAUDE.md 找到该 skill 加载的规约
  - 查看 "Skills 加载时机与规约引用" 章节
  - 找到：docs/rules/DEV-plan-writing-rules.md

  步骤 3: 读取规约文件
  - 使用 Read 工具读取 docs/rules/DEV-plan-writing-rules.md

  步骤 4: 基于规约内容回答
  - 根据规约中的 "Task 结构（必须）" 章节回答

---

## 工具与检查

### 完整性检查
```bash
bash .claude/skills/check/check-skills-integrity.sh
```

> 静态代码扫描命令已包含在 `docs/rules/prompts/qa-prompt.md` 的 M3 检查脚本中。

---

## 使用说明

### Orchestrator 启动
Orchestrator 负责里程碑管理和阶段推进。在任何阶段遇到流程问题时，直接告知 Claude "作为 Orchestrator 处理"即可激活该角色。

### CHANGELOG 初始化
项目初始化（M0）时创建 `docs/CHANGELOG-XLT.md`，格式：
```markdown
# 变更日志

| 日期 | 变更描述 | 影响范围 | 发起人 |
|------|---------|---------|--------|
| — | — | — | — |
```


---

**最后更新**: 2026-02-28
**维护者**: Orchestrator

