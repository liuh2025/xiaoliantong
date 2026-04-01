---
name: m6-retrospective
description: 项目复盘，BA+ARCH+TL 联合回顾 CHANGELOG 进行根因分析。由验收通过后自动触发。
user-invocable: false
---

你现在作为 BA + ARCH + TL 联合角色工作。

## 读取 CHANGELOG
!`cat docs/CHANGELOG-*.md 2>/dev/null || echo "[CHANGELOG 未找到]"`

## 根因分析
对 CHANGELOG 中记录的所有问题进行根因分析，分类为：
- 业务规则类（BR）：需求理解偏差、业务规则遗漏
- 设计规则类（DR）：架构设计缺陷、接口设计不合理
- 测试规则类（TR）：测试覆盖不足、测试策略问题
- 安全规则类（SR）：安全漏洞、权限校验遗漏
- 红线类（RL）：流程违规、质量门禁遗漏

## 生成新增规则清单
输出格式：
```markdown
# 本项目新增规则清单

## 业务规约（BR）
| 编号 | 规约内容 | 来源问题 |
|------|---------|---------|
| BR-xxx | ... | CHANGELOG 第 N 条 |

## 设计规约（DR）
| 编号 | 规约内容 | 来源问题 |
|------|---------|---------|
| DR-xxx | ... | CHANGELOG 第 N 条 |

## 测试规约（TR）
...

## 安全规约（SR）
...

## 红线清单（RL）
...
```

## 完成标志
将新增规则清单输出给用户，用户确认后自动触发 `/m6-merge-rules` 合并到规约文件
