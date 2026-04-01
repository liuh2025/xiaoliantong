---
name: write-design
description: 编写DESN详细设计文档。方案选定后，调用此 Skill 生成正式DESN。
user-invocable: false
---

## 加载模板
- !`cat docs/templates/DESN-template.md 2>/dev/null && echo "[已加载 DESN 模板]" || echo "[DESN 模板未找到]"`

## 执行步骤
1. 以 DESN 模板为框架，按各章节要求，将用户已澄清的设计填入对应章节，生成 `docs/DESN-{项目简称}-{最新版本号}.md`，初始状态为"草稿"
2.逐节向用户展示 DESN 内容，每节确认后再继续下一节
3. 全部章节确认后，将状态更新为"待审批"

## 完成标志
用户明确说"DESN 批准"后：
1. 将 DESN 状态更新为"已批准"
2. 将确定的技术栈写回 CLAUDE.md：
!`sed -i "s/- \*\*技术栈\*\*:.*$/- **技术栈**: ${TECH_STACK}/" CLAUDE.md`
（执行前将 `${TECH_STACK}` 替换为实际技术栈字符串，如 `Django + DRF + Vue3 + Element Plus`）
3. 自动触发 `/write-test-plan`

