---
name: m5-deploy
description: 进入 M5 部署阶段，ARCH 执行 docker compose 部署并逐步记录。当用户说"开始部署"、"进入M5"时自动触发。
allowed-tools: Read, Bash(docker *), Bash(git *), playwright
---

你现在作为 ARCH 角色工作。

## 前置检查
!`grep "当前阶段:" CLAUDE.md 2>/dev/null | head -1 || echo "未找到 CLAUDE.md"`
若当前阶段不是 M5，停止并提示用户先完成 M4。

## 加载规则
- !`cat docs/rules/prompts/arch-prompt.md 2>/dev/null || echo "[arch-prompt.md 未找到]"`

## 执行步骤
1. 初始化部署报告 `docs/DEPLOY-TEST-{项目名}-v{版本}.md`，边做边追加记录
2. 确认 M4 QA 已签署：!`grep "QA 审查" docs/TEST-REPORT-*.md 2>/dev/null | tail -1`
3. 构建生产镜像：`docker compose -f docker/docker-compose.prod.yml build 2>&1`
4. 启动生产环境：`docker compose -f docker/docker-compose.prod.yml up -d 2>&1`
5. 健康检查：`curl -f http://localhost/health 2>&1`（失败则停止，附 docker logs）
6. 冒烟测试：!`ABBR=$(grep "项目简称" CLAUDE.md | grep -oP '(?<=: ).*' | tr -d '[:space:]'); grep "冒烟" docs/QA-test-plan-${ABBR}-v1.0.md 2>/dev/null`
   使用 Playwright MCP 逐条执行，截图保存到 `tests/screenshots/smoke/`

## 完成标志
✅ 冒烟全部通过 → 部署报告状态=待审批，自动触发 `/m5-exit`

❌ 有失败用例 → 判断问题类型：
- **部署问题**（配置错误/环境问题）→ ARCH 修复配置重新执行
- **代码问题**（功能逻辑错误）→ 触发 `/m3-tl-bug-fix`
