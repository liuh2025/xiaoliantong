---
name: m4-test-api
description: 执行 L1 API 测试，覆盖所有接口（RPC/RESTful/MQ）的正例、反例、边界值、业务规则。由 m4-test-kickoff 自动触发。
user-invocable: false
allowed-tools: Read, Write, Bash(pytest *)
agent: general-purpose
---

你现在作为 Tester 角色工作，执行 L1 API 测试。

主要步骤如下：
Step1： 前置检查
确认 QA-test-plan 中存在 API 测试用例定义，如无用例则停止测试工作。

Step2：读取 API 测试用例（分批次读取，直至所有API测试用例全部读完）
!`ABBR=$(grep "项目简称" CLAUDE.md | grep -oP '(?<=: ).*' | tr -d '[:space:]'); grep -A 20 "API 测试" docs/QA-test-plan-${ABBR}-*.md 2>/dev/null | head -100`

Step3：生成测试脚本
根据读取到的API 测试用例，生成测试脚本：

1. **脚本位置**：`tests/integration/script/test_api_{模块名}.py`
2. **共享配置**：`tests/integration/script/conftest.py`
3. **命名规范**：`test_api_{模块}_{功能}_{场景}`

### 脚本模板

```python
# tests/integration/script/test_api_user.py
import pytest

class TestUserAPI:
    """用户模块 API 测试"""

    def test_api_user_create_success(self):
        """
        TC-API-001: 创建用户 - 正例
        预期：返回 201，用户创建成功
        """
        # 测试实现
        pass

    def test_api_user_create_duplicate(self):
        """
        TC-API-002: 创建用户 - 用户名重复
        预期：返回 400，提示用户名已存在
        """
        # 测试实现
        pass

    def test_api_user_create_empty_username(self):
        """
        TC-API-003: 创建用户 - 用户名为空
        预期：返回 400，提示用户名不能为空
        """
        # 测试实现
        pass
```

Step4：执行测试

```bash
# 生成时间戳目录
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
mkdir -p tests/integration/log/$TIMESTAMP

# 执行测试并记录日志
python -m pytest tests/integration/script/ -v \
  --tb=short \
  --log-file=tests/integration/log/$TIMESTAMP/api-test.log \
  --log-file-level=INFO \
  2>&1 | tee tests/integration/log/$TIMESTAMP/summary.log
```

执行完成后，先检查测试脚本是否编写有误，排除测试脚本问题后再重新执行。

Step5：记录结果

在 TEST-REPORT 中更新以下章节：

### 1.2 测试结果汇总

| 层级 | 设计用例数 | 执行用例数 | 通过 | 失败 | 阻塞 | 通过率 |
|------|-----------|-----------|------|------|------|--------|
| L1-API | X | X | X | X | X | XX% |

### 2.1 API 测试结果

按表格逐条填写每条用例 ID 的执行结果：

| 用例 ID | 用例描述 | 执行结果 | 备注 |
|---------|---------|---------|------|
| TC-API-001 | 创建用户-正例 | 通过 | - |
| TC-API-002 | 创建用户-重复 | 通过 | - |

### 3.2 缺陷详情

如有失败用例，则按照3.2 缺陷详情格式要求，填写缺陷详情


## 完成标志

- **若无问题**（全部通过）→ 自动触发 `/m4-test-e2e`
- **若有问题**（有失败用例）→ 自动触发 `/m3-subagent-development --mode fix`

