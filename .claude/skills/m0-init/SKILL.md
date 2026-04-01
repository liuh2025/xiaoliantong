---
name: m0-init
description: M0 项目初始化，创建项目目录结构、配置文件、复制规约和模板。当用户说"初始化项目"、"开始新项目"时自动触发。
user-invocable: true
---

你现在作为 Orchestrator 角色工作，执行 M0 项目初始化。

## 1. 收集项目信息

请用户提供以下信息：
- **项目名称**：如 "MyAwesomeProject"
- **项目简称**：如 "MAP"（2-4 字母，用于文档命名）
- **项目描述**：一句话描述项目目标

## 2. 创建目录结构

```bash
# 创建核心目录
mkdir -p docs/templates
mkdir -p docs/rules/prompts
mkdir -p docs/plans
mkdir -p src
mkdir -p tests/unit
mkdir -p tests/integration/script
mkdir -p tests/integration/log
mkdir -p tests/e2e/script
mkdir -p tests/e2e/screenshots
mkdir -p tests/e2e/log
mkdir -p tests/screenshots/smoke
mkdir -p tests/test-data
mkdir -p .claude/skills
```

## 3. 初始化 Git

### 3.1 检查是否已初始化

```bash
if [ -d .git ]; then
    echo "✅ Git 仓库已存在"
else
    git init
    echo "✅ Git 仓库已初始化"
fi
```

### 3.2 检查远程同步（如项目已存在）

如果项目目录已存在前期开发内容：

```bash
# 检查是否有远程仓库
REMOTE=$(git remote | head -1)

if [ -n "$REMOTE" ]; then
    # 获取远程最新状态
    git fetch "$REMOTE" 2>/dev/null || true

    # 检查本地 main 与远程 main 是否有差异
    if git rev-parse HEAD &>/dev/null && git rev-parse "$REMOTE/main" &>/dev/null; then
        LOCAL_HEAD=$(git rev-parse HEAD)
        REMOTE_HEAD=$(git rev-parse "$REMOTE/main")

        if [ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]; then
            echo "⚠️ 检测到本地与远程 main 分支有差异："
            echo "   本地: $LOCAL_HEAD"
            echo "   远程: $REMOTE_HEAD"
            echo ""
            echo "请先同步后再初始化："
            echo "   git pull $REMOTE main"
            echo "   或"
            echo "   git push $REMOTE main"
            exit 1
        fi
    fi
fi
```

## 4. 创建配置文件

### 4.1 创建 .gitignore
!`cat docs/templates/.gitignore-template 2>/dev/null || echo "[.gitignore 模板未找到]"`

### 4.2 创建 requirements.txt
!`cat docs/templates/requirements-template.txt 2>/dev/null || echo "[requirements 模板未找到]"`

### 4.3 创建 README.md
使用以下模板，替换占位符：
- `{项目名称}` → 用户提供的项目名称
- `{项目描述}` → 用户提供的项目描述

```markdown
# {项目名称}

> {项目描述}

## 快速开始

### 环境准备

\`\`\`bash
pip install -r requirements.txt
playwright install
\`\`\`

### 开始需求分析

\`\`\`
/m1-requirements-analysis
\`\`\`

## 里程碑流程

M1 需求 → M2 设计 → M3 开发 → M4 测试 → M5 部署 → M6 验收

## 许可证

MIT License
```

## 5. 复制规约和模板

### 5.1 复制规约库
从 ProjectPower 复制以下文件到 `docs/rules/`：
- `BR-business-rules.md`
- `DR-design-rules.md`
- `TR-test-rules.md`
- `SR-security-rules.md`
- `RL-redlines.md`
- `GIT-rules.md`
- `EXCEPTION-rules.md`
- `DEV-plan-writing-rules.md`
- `prompts/orchestrator-prompt.md`
- `prompts/ba-prompt.md`
- `prompts/arch-prompt.md`
- `prompts/tl-prompt.md`
- `prompts/tester-prompt.md`
- `prompts/qa-prompt.md`

### 5.2 复制文档模板
从 ProjectPower 复制 `docs/templates/` 目录下所有模板文件。

### 5.3 复制 Skills
从 ProjectPower 复制 `.claude/skills/` 目录下所有 skill 目录。

## 6. 创建 CLAUDE.md

!`cat docs/templates/CLAUDE-template.md 2>/dev/null || echo "[CLAUDE 模板未找到]"`

使用以下内容创建 `CLAUDE.md`，替换占位符：
- `{项目名称}` → 用户提供的项目名称
- `{项目简称}` → 用户提供的项目简称
- `{实际技术栈}` → 待 M2 确定后填写，初始为空

## 7. 创建初始文档

### 7.1 创建 CHANGELOG
基于 `docs/templates/CHANGELOG-template.md` 创建 `docs/CHANGELOG-{项目简称}.md`

### 7.2 创建环境配置
基于 `docs/templates/env-config-template.md` 创建 `docs/env-config-{项目简称}.md`

提示用户填写：
- 测试环境服务器地址
- 生产环境服务器地址
- 数据库连接信息

### 7.3 初始提交

```bash
git add .
git commit -m "init: 项目初始化"
```

## 完成报告

```
## M0 初始化完成

### 项目信息
- 项目名称：{项目名称}
- 项目简称：{项目简称}
- 项目描述：{项目描述}

### 创建的目录
- docs/templates/（文档模板）
- docs/rules/（规约库）
- docs/plans/（开发计划）
- src/（源代码）
- tests/（测试代码）
- .claude/skills/（Skills）

### 创建的配置文件
- .gitignore
- requirements.txt
- README.md
- CLAUDE.md
- docs/env-config-{项目简称}.md（环境配置）

### 环境信息
请在 docs/env-config-{项目简称}.md 中填写：
- 测试环境部署地址
- 生产环境部署地址
- 数据库连接信息

### 下一步
执行以下命令开始需求分析：

/m1-requirements-analysis
```

## 注意事项

- 本 Skill 仅在创建新项目时使用
- 已存在的项目不应重复执行
- 技术栈在 M2 设计阶段确定后回填到 CLAUDE.md
