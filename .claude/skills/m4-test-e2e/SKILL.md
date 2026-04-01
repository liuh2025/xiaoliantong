---
name: m4-test-e2e
description: 执行 L2 E2E 测试，覆盖用户操作流程，主流程/核心功能100%，含异常测试。由 m4-test-api 完成后自动触发。
user-invocable: false
allowed-tools: Read, Write, Bash(pytest *), Bash(playwright *)
agent: general-purpose
---

你现在作为 Tester 角色工作，执行 L2 E2E 测试。

主要步骤如下：
Step1：前置检查
确认：
1. QA-test-plan 中存在 E2E 测试用例定义
2. 应用已启动并可访问

Step2：读取 E2E 测试用例（分批次读取，直至所有E2E测试用例全部读完）
!`ABBR=$(grep "项目简称" CLAUDE.md | grep -oP '(?<=: ).*' | tr -d '[:space:]'); grep -A 20 "E2E 测试" docs/QA-test-plan-${ABBR}-*.md 2>/dev/null | head -100`

Step3：生成测试脚本
根据读取到的 E2E 测试用例，使用 **Page Object 模式** 生成测试脚本。

### 目录结构

```
tests/e2e/
├── script/
│   ├── pages/                   # Page Object 定义
│   │   ├── __init__.py
│   │   ├── base_page.py         # 基础页面类
│   │   ├── login_page.py        # 登录页面
│   │   └── dashboard_page.py    # 仪表盘页面
│   ├── conftest.py              # 共享配置和 fixtures
│   ├── test_e2e_auth.py         # 认证流程测试
│   └── test_e2e_user.py         # 用户管理测试
├── screenshots/
│   └── {YYYY-MM-DD_HHMMSS}/     # 按执行时间分目录
│       ├── TC-E2E-001-成功.png
│       └── TC-E2E-001-失败-密码错误.png
└── log/
    └── {YYYY-MM-DD_HHMMSS}/     # 按执行时间分目录
        └── e2e-test.log
```

### Page Object 模板

```python
# tests/e2e/script/pages/base_page.py
from playwright.sync_api import Page, Locator
from pathlib import Path
from datetime import datetime


class BasePage:
    """基础页面类"""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        """导航到指定 URL"""
        self.page.goto(url)

    def take_screenshot(self, test_id: str, result: str, detail: str = None):
        """
        功能响应后截图

        Args:
            test_id: 测试用例 ID（如 TC-E2E-001）
            result: 结果（成功/失败）
            detail: 失败详情（如 密码错误）
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        screenshot_dir = Path(f"tests/e2e/screenshots/{timestamp}")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        if detail:
            filename = f"{test_id}-{result}-{detail}.png"
        else:
            filename = f"{test_id}-{result}.png"

        self.page.screenshot(path=str(screenshot_dir / filename))
```

```python
# tests/e2e/script/pages/login_page.py
from playwright.sync_api import Page, expect
from .base_page import BasePage


class LoginPage(BasePage):
    """登录页面 Page Object"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("button[type='submit']")
        self.error_message = page.locator(".error-message")

    def navigate_to_login(self, base_url: str):
        """导航到登录页面"""
        self.navigate(f"{base_url}/login")

    def login(self, username: str, password: str):
        """执行登录操作"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def should_login_success(self):
        """验证登录成功 - 跳转到仪表盘"""
        expect(self.page).to_have_url("/dashboard")

    def should_show_error(self, message: str):
        """验证错误消息"""
        expect(self.error_message).to_contain_text(message)
```

### 测试脚本模板

```python
# tests/e2e/script/test_e2e_auth.py
import pytest
from pages.login_page import LoginPage


class TestE2EAuth:
    """用户认证 E2E 测试"""

    def test_e2e_login_success(self, page, base_url):
        """
        TC-E2E-001: 用户登录成功

        前置条件：用户已注册
        操作步骤：
        1. 打开登录页面
        2. 输入正确的用户名和密码
        3. 点击登录按钮
        预期结果：跳转到系统主界面

        截图：登录成功后截取主界面
        """
        login_page = LoginPage(page)
        login_page.navigate_to_login(base_url)
        login_page.login("testuser", "password123")
        login_page.should_login_success()
        login_page.take_screenshot("TC-E2E-001", "成功")

    def test_e2e_login_wrong_password(self, page, base_url):
        """
        TC-E2E-002: 密码错误登录失败

        前置条件：用户已注册
        操作步骤：
        1. 打开登录页面
        2. 输入正确的用户名和错误的密码
        3. 点击登录按钮
        预期结果：显示错误提示"密码错误"

        截图：截取错误提示界面
        """
        login_page = LoginPage(page)
        login_page.navigate_to_login(base_url)
        login_page.login("testuser", "wrongpassword")
        login_page.should_show_error("密码错误")
        login_page.take_screenshot("TC-E2E-002", "失败", "密码错误")
```

Step4：执行测试

```bash
# 生成时间戳目录
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
mkdir -p tests/e2e/screenshots/$TIMESTAMP
mkdir -p tests/e2e/log/$TIMESTAMP

# 执行 E2E 测试
python -m pytest tests/e2e/script/ -v \
  --headed \
  --tb=short \
  --log-file=tests/e2e/log/$TIMESTAMP/e2e-test.log \
  --log-file-level=INFO \
  2>&1 | tee tests/e2e/log/$TIMESTAMP/summary.log
```

## 截图规则

### 截图时机

**在功能响应后截图**：

| 场景 | 截图内容 | 文件命名示例 |
|------|---------|-------------|
| 操作成功 | 功能成功后的界面 | `TC-E2E-001-成功.png` |
| 操作失败 | 错误提示界面 | `TC-E2E-001-失败-密码错误.png` |
| 校验不通过 | 校验错误提示 | `TC-E2E-002-失败-用户名不能为空.png` |

### 截图示例

```
登录成功 → 截取跳转后的系统主界面
登录失败 → 截取显示"密码错误"的提示界面
新增校验失败 → 截取显示"XXX不能为空"的提示界面
```

执行完成后，先对执行结果进行检查，检查测试脚本是否编写有误、截屏是否符合要求，排除测试问题后再重新执行。

Step5：记录结果

在 TEST-REPORT 中更新以下章节：

### 1.2 测试结果汇总

| 层级 | 设计用例数 | 执行用例数 | 通过 | 失败 | 阻塞 | 通过率 |
|------|-----------|-----------|------|------|------|--------|
| L2-E2E | X | X | X | X | X | XX% |

### 2.2 E2E 测试结果

按表格逐条填写每条用例 ID 的执行结果：

| 用例 ID | 用例描述 | 执行结果 | 截图 | 备注 |
|---------|---------|---------|------|------|
| TC-E2E-001 | 用户登录成功 | 通过 | TC-E2E-001-成功.png | - |
| TC-E2E-002 | 密码错误登录失败 | 通过 | TC-E2E-002-失败-密码错误.png | - |

### 3.2 缺陷详情

如有失败用例，则按照3.2 缺陷详情格式要求，填写缺陷详情

## 截图完整性检查

所有用例执行完成后，检查：

```bash
# 统计截图数量
ls tests/e2e/screenshots/$TIMESTAMP/ | wc -l
```

确认截图数量与执行的 E2E 用例数量一致；若不一致，补充执行。

## 完成标志

- **若无问题**（全部通过）→ 自动触发 `/m4-exit`
- **若有问题**（有失败用例）→ 自动触发 `/m3-subagent-development --mode fix`

## 人工检查说明

人工检查发现的问题**不在自动化流程内**，直接作为缺陷登记在 TEST-REPORT 中。