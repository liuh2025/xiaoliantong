---
name: git-baseline-commit
description: 提交阶段基线，统一处理工作区检查、提交、推送。由各 m*-exit 调用。
user-invocable: false
argument-hint: "<阶段> [M1|M2|M3|M4|M5|M6]"
context: fork
agent: general-purpose
allowed-tools: Bash, Read
---

## 前置检查

```bash
git status --porcelain 2>/dev/null || echo "[非 git 仓库]"
git branch --show-current 2>/dev/null || echo "[未知]"
```

## 按阶段执行

### M1 基线

```bash
git add docs/PRD-*.md
git diff --cached --quiet || git commit -m "baseline(M1): 需求文档已批准"
```

### M2 基线

```bash
git add docs/PRD-*.md docs/DESN-*.md docs/QA-test-plan-*.md docs/CHK-*.md
git diff --cached --quiet || git commit -m "baseline(M1+M2): 需求、设计已批准"
```

### M3 基线

```bash
git add src/ tests/unit/ docs/plans/DEV-plan-*.md
git diff --cached --quiet || git commit -m "baseline(M3): 开发完成，单元测试通过"
```

### M4 基线

```bash
git add docs/TEST-REPORT-*.md tests/e2e/screenshots/
git diff --cached --quiet || git commit -m "baseline(M4): 测试完成"
```

### M5 基线

```bash
git add docs/DEPLOY-TEST-*.md tests/screenshots/smoke/
git diff --cached --quiet || git commit -m "baseline(M5): 部署完成，冒烟测试通过"
```

### M6 基线

```bash
git add docs/CHANGELOG-*.md docs/rules/
git diff --cached --quiet || git commit -m "baseline(M6): 项目验收通过，归档"
```

## 推送

```bash
REMOTE=$(git remote | head -1)
[ -n "$REMOTE" ] && git push "$REMOTE" $(git branch --show-current)
```

## M6 打标签

```bash
if [ "$ARG1" = "M6" ]; then
    VERSION=$(grep "当前版本" CLAUDE.md | grep -oP '(?<=v)[0-9.]+' | head -1)
    if [ -n "$VERSION" ]; then
        git tag -a "v${VERSION}" -m "Release v${VERSION}"
        REMOTE=$(git remote | head -1)
        [ -n "$REMOTE" ] && git push "$REMOTE" "v${VERSION}"
    fi
fi
```

## 完成标志

```
✅ 基线提交完成
   - 阶段: {阶段}
   - 提交: {commit-sha}
```
