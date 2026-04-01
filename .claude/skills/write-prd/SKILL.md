---
name: write-prd
description: 编写 PRD 需求文档。需求澄清完成后，调用此 Skill 生成正式PRD。
user-invocable: false
---

## 加载模板
- !`cat docs/templates/PRD-template.md 2>/dev/null && echo "[已加载 PRD 模板]" || echo "[PRD 模板未找到]"`

## 执行步骤
1. 以 PRD 模板为框架，按各章节要求，将用户已澄清的需求填入对应章节，生成 `docs/PRD-{项目简称}-{最新版本号}.md`，初始状态为"草稿"
2. 逐节向用户展示 PRD 内容，每节确认后再继续下一节
3. 全部章节确认后，将状态更新为"待审批"

## 完成标志
用户明确说"PRD 批准"后，将 PRD 状态更新为"已批准"，自动触发 `/m1-exit`
