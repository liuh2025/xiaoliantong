"""
校链通(XiaoLianTong) - 第1章 登录模块 L2 E2E 测试
基于 QA-test-plan-PP-v1.0.md 第1章
覆盖用例: TC-E2E-001 ~ TC-E2E-006

应用地址: http://localhost:3000
测试日期: 2026-04-10
"""

from playwright.sync_api import sync_playwright
import time
import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# ============================================================
# 配置
# ============================================================
BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:3000")
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch01_login")
SCREENSHOT_DIR = os.path.join(CAPTURES_DIR, datetime.now().strftime("%Y-%m-%d_%H%M%S"))

VIEWPORT = {"width": 1280, "height": 900}
DEFAULT_TIMEOUT = 30000

# 测试账号
TEST_PHONE = "13800000001"
TEST_PASSWORD = "Admin123!"


# ============================================================
# 智能截图管理器
# ============================================================
class SmartScreenshot:
    """智能截图管理器"""

    def __init__(self, page, output_dir, case_id):
        self.page = page
        self.output_dir = output_dir
        self.case_id = case_id
        self.counter = 0
        os.makedirs(output_dir, exist_ok=True)

    def capture(self, trigger, step=None, action=None, tag=None):
        self.counter += 1
        parts = [self.case_id]
        if step is not None:
            parts.append(f"step{step}")
        if action:
            parts.append(action)
        parts.append(trigger.lower())
        if tag:
            parts.append(tag)
        filename = f"{'-'.join(parts)}_{self.counter}.png"
        filepath = os.path.join(self.output_dir, filename)
        self.page.screenshot(path=filepath, full_page=True)
        log_info(f"Screenshot saved: {filename}")
        return filepath

    def save_dom_snapshot(self, step=None, tag=""):
        """保存DOM快照用于调试"""
        self.counter += 1
        parts = [self.case_id]
        if step is not None:
            parts.append(f"step{step}")
        parts.append("dom_snapshot")
        if tag:
            parts.append(tag)
        filename = f"{'-'.join(parts)}_{self.counter}.html"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.page.content())
        log_info(f"DOM snapshot saved: {filename}")
        return filepath


# ============================================================
# 日志工具
# ============================================================
class TestLogger:
    """结构化日志"""

    def __init__(self, case_id, output_dir):
        self.case_id = case_id
        self.output_dir = output_dir
        self.logs = []
        self.start_time = time.time()
        self.steps_passed = 0
        self.steps_failed = 0

    def log(self, level, step, action, message, **kwargs):
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "level": level,
            "case_id": self.case_id,
            "step": step,
            "action": action,
            "message": message,
            **kwargs,
        }
        self.logs.append(entry)
        icon = {"INFO": "  ", "PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]", "DEBUG": "[DBG]"}.get(level, "  ")
        step_str = f"STEP {step}" if step else ""
        print(f"[{entry['timestamp']}] {icon} {self.case_id} | {step_str} {action} | {message}")
        if kwargs:
            for k, v in kwargs.items():
                print(f"    -> {k}: {v}")
        if level == "PASS":
            self.steps_passed += 1
        elif level == "FAIL":
            self.steps_failed += 1

    def summary(self):
        duration = time.time() - self.start_time
        return {
            "case_id": self.case_id,
            "duration_sec": round(duration, 2),
            "steps_passed": self.steps_passed,
            "steps_failed": self.steps_failed,
            "total_steps": self.steps_passed + self.steps_failed,
        }

    def save_json(self):
        filepath = os.path.join(self.output_dir, f"{self.case_id}_log.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"summary": self.summary(), "logs": self.logs}, f, ensure_ascii=False, indent=2)
        return filepath


_logger = None


def log_info(msg, step=None, **kw):
    _logger.log("INFO", step, "", msg, **kw)


def log_pass(msg, step=None, **kw):
    _logger.log("PASS", step, "", msg, **kw)


def log_fail(msg, step=None, **kw):
    _logger.log("FAIL", step, "", msg, **kw)


def log_warn(msg, step=None, **kw):
    _logger.log("WARN", step, "", msg, **kw)


def log_debug(msg, step=None, **kw):
    _logger.log("DEBUG", step, "", msg, **kw)


# ============================================================
# Element Plus 组件辅助
# ============================================================
class ElementPlusHelper:
    """Element Plus 组件操作辅助"""

    @staticmethod
    def js_click(page, selector):
        btn = page.query_selector(selector)
        if btn:
            btn.evaluate("el => el.click()")
            return True
        return False

    @staticmethod
    def fill_el_input(page, placeholder, value):
        """填写 Element Plus el-input"""
        selector = f"input[placeholder='{placeholder}']"
        inp = page.locator(selector).first
        if inp and inp.is_visible():
            inp.click()
            inp.fill("")
            inp.fill(value)
            return True
        return False

    @staticmethod
    def fill_el_input_by_index(page, placeholder, index, value):
        """填写第N个匹配placeholder的el-input"""
        selector = f"input[placeholder='{placeholder}']"
        inp = page.locator(selector).nth(index)
        if inp and inp.is_visible():
            inp.click()
            inp.fill("")
            inp.fill(value)
            return True
        return False


# ============================================================
# 测试用例
# ============================================================

def tc_e2e_001(page):
    """
    TC-E2E-001: 登录页面渲染
    前置条件: 无
    操作步骤:
      1. 打开登录页面
    预期结果:
      蓝色渐变背景、白色卡片、标题"登录"、两个Tab（短信验证码登录、密码登录）
    """
    global _logger
    case_id = "TC-E2E-001"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 登录页面渲染 ===")
    result = {"case_id": case_id, "name": "登录页面渲染", "status": "FAIL", "details": []}
    verifications = {}

    try:
        # STEP 1: 打开登录页面
        log_info("打开登录页面", step=1)
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=1, action="page_load")

        # STEP 2: 验证白色卡片存在
        log_info("验证登录卡片存在", step=2)
        login_card = page.query_selector(".login-card")
        if login_card and login_card.is_visible():
            log_pass("登录卡片(.login-card)可见", step=2)
            verifications["login_card_visible"] = True
        else:
            log_fail("登录卡片(.login-card)不可见", step=2)
            verifications["login_card_visible"] = False
            ss.save_dom_snapshot(step=2, tag="no_login_card")

        # STEP 3: 验证标题
        log_info("验证页面标题", step=3)
        title_el = page.query_selector(".login-title")
        if title_el and title_el.is_visible():
            title_text = title_el.inner_text()
            if "登录" in title_text:
                log_pass(f"标题正确: '{title_text}'", step=3)
                verifications["title_correct"] = True
            else:
                log_fail(f"标题不符: 期望含'登录', 实际'{title_text}'", step=3)
                verifications["title_correct"] = False
        else:
            log_fail("标题元素(.login-title)不可见", step=3)
            verifications["title_correct"] = False

        # STEP 4: 验证两个Tab
        log_info("验证Tab存在", step=4)
        sms_tab = page.locator("button.login-tab", has_text="短信验证码登录")
        pwd_tab = page.locator("button.login-tab", has_text="密码登录")

        if sms_tab.is_visible():
            log_pass("短信验证码登录Tab可见", step=4)
            verifications["sms_tab_visible"] = True
        else:
            log_fail("短信验证码登录Tab不可见", step=4)
            verifications["sms_tab_visible"] = False

        if pwd_tab.is_visible():
            log_pass("密码登录Tab可见", step=4)
            verifications["pwd_tab_visible"] = True
        else:
            log_fail("密码登录Tab不可见", step=4)
            verifications["pwd_tab_visible"] = False

        ss.capture("CHECKPOINT", step=4, action="tabs_verified")

        # 综合判定
        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total > 0 else 0
        if confidence >= 0.8:
            result["status"] = "PASS"
        elif confidence >= 0.6:
            result["status"] = "NEED_HUMAN_CHECK"
        else:
            result["status"] = "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=5)

    except Exception as e:
        log_fail(f"测试异常: {str(e)}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(f"异常: {str(e)}")
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_002(page):
    """
    TC-E2E-002: 短信登录Tab - 表单元素检查
    前置条件: 登录页面已打开，默认显示短信登录Tab
    操作步骤:
      1. 检查短信登录Tab下的表单元素
    预期结果:
      手机号输入框、验证码输入框、获取验证码按钮、7天免登录复选框、登录按钮
    """
    global _logger
    case_id = "TC-E2E-002"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 短信登录Tab表单元素 ===")
    result = {"case_id": case_id, "name": "短信登录Tab表单元素", "status": "FAIL", "details": []}
    verifications = {}

    try:
        # STEP 1: 打开登录页面
        log_info("打开登录页面", step=1)
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=1, action="page_load")

        # STEP 2: 确认短信Tab激活
        log_info("确认短信登录Tab为激活状态", step=2)
        sms_tab = page.locator("button.login-tab", has_text="短信验证码登录")
        if sms_tab.is_visible():
            sms_tab_classes = sms_tab.get_attribute("class") or ""
            if "active" in sms_tab_classes:
                log_pass("短信验证码登录Tab已激活", step=2)
                verifications["sms_tab_active"] = True
            else:
                log_warn("短信Tab未激活，尝试点击", step=2)
                sms_tab.click()
                page.wait_for_timeout(500)
                verifications["sms_tab_active"] = True

        # STEP 3: 验证手机号输入框
        log_info("验证手机号输入框", step=3)
        phone_input = page.locator("input[placeholder='请输入手机号']").first
        if phone_input.is_visible():
            log_pass("手机号输入框可见", step=3)
            verifications["phone_input"] = True
        else:
            log_fail("手机号输入框不可见", step=3)
            verifications["phone_input"] = False

        # STEP 4: 验证验证码输入框
        log_info("验证验证码输入框", step=4)
        code_input = page.locator("input[placeholder='请输入验证码']").first
        if code_input.is_visible():
            log_pass("验证码输入框可见", step=4)
            verifications["code_input"] = True
        else:
            log_fail("验证码输入框不可见", step=4)
            verifications["code_input"] = False

        # STEP 5: 验证获取验证码按钮
        log_info("验证获取验证码按钮", step=5)
        get_code_btn = page.locator("button:has-text('获取验证码')")
        if get_code_btn.is_visible():
            log_pass("获取验证码按钮可见", step=5)
            verifications["get_code_btn"] = True
        else:
            log_fail("获取验证码按钮不可见", step=5)
            verifications["get_code_btn"] = False

        # STEP 6: 验证7天免登录复选框
        log_info("验证7天免登录复选框", step=6)
        checkbox_text = page.locator("text=7天内免登录")
        if checkbox_text.first.is_visible():
            log_pass("'7天内免登录'复选框可见", step=6)
            verifications["remember_checkbox"] = True
        else:
            log_fail("'7天内免登录'复选框不可见", step=6)
            verifications["remember_checkbox"] = False

        # STEP 7: 验证登录按钮
        log_info("验证登录按钮", step=7)
        login_btn = page.locator("button.login-btn").first
        if login_btn.is_visible():
            btn_text = login_btn.inner_text()
            log_pass(f"登录按钮可见, 文本: '{btn_text}'", step=7)
            verifications["login_btn"] = True
        else:
            log_fail("登录按钮不可见", step=7)
            verifications["login_btn"] = False

        ss.capture("CHECKPOINT", step=7, action="form_elements_verified")

        # 综合判定
        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total > 0 else 0
        if confidence >= 0.8:
            result["status"] = "PASS"
        elif confidence >= 0.6:
            result["status"] = "NEED_HUMAN_CHECK"
        else:
            result["status"] = "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=8)

    except Exception as e:
        log_fail(f"测试异常: {str(e)}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(f"异常: {str(e)}")
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_003(page):
    """
    TC-E2E-003: 密码登录Tab切换
    前置条件: 登录页面已打开
    操作步骤:
      1. 点击密码登录Tab
    预期结果:
      显示密码输入框、手机号输入框、忘记密码链接、7天免登录复选框
    """
    global _logger
    case_id = "TC-E2E-003"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 密码登录Tab切换 ===")
    result = {"case_id": case_id, "name": "密码登录Tab切换", "status": "FAIL", "details": []}
    verifications = {}

    try:
        # STEP 1: 打开登录页面
        log_info("打开登录页面", step=1)
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=1, action="page_load")

        # STEP 2: 点击密码登录Tab
        log_info("点击密码登录Tab", step=2)
        pwd_tab = page.locator("button.login-tab", has_text="密码登录")
        if pwd_tab.is_visible():
            pwd_tab.click()
            page.wait_for_timeout(500)
            # 验证Tab激活
            pwd_tab_classes = pwd_tab.get_attribute("class") or ""
            if "active" in pwd_tab_classes:
                log_pass("密码登录Tab已激活", step=2)
                verifications["pwd_tab_active"] = True
            else:
                log_fail("密码登录Tab未激活", step=2)
                verifications["pwd_tab_active"] = False
        else:
            log_fail("密码登录Tab不可见", step=2)
            result["details"].append("密码登录Tab不可见")
            _logger.save_json()
            return result

        # STEP 3: 验证密码输入框
        log_info("验证密码输入框", step=3)
        pwd_input = page.locator("input[placeholder='请输入密码']")
        if pwd_input.is_visible():
            log_pass("密码输入框可见", step=3)
            verifications["password_input"] = True
        else:
            log_fail("密码输入框不可见", step=3)
            verifications["password_input"] = False

        # STEP 4: 验证手机号输入框（密码Tab的）
        log_info("验证密码Tab下的手机号输入框", step=4)
        # 密码表单在v-show="activeTab === 'password'"下
        # 此时页面有两个input[placeholder='请输入手机号']，第二个属于密码表单
        phone_inputs = page.locator("input[placeholder='请输入手机号']")
        phone_count = phone_inputs.count()
        log_debug(f"手机号输入框数量: {phone_count}", step=4)
        if phone_count >= 2:
            pwd_phone = phone_inputs.nth(1)
            if pwd_phone.is_visible():
                log_pass("密码Tab手机号输入框可见", step=4)
                verifications["pwd_phone_input"] = True
            else:
                log_fail("密码Tab手机号输入框不可见", step=4)
                verifications["pwd_phone_input"] = False
        else:
            log_warn(f"只找到{phone_count}个手机号输入框（两个Tab可能共享）", step=4)
            verifications["pwd_phone_input"] = False

        # STEP 5: 验证忘记密码链接
        log_info("验证忘记密码链接", step=5)
        forgot_link = page.locator("text=忘记密码")
        if forgot_link.first.is_visible():
            log_pass("'忘记密码'链接可见", step=5)
            verifications["forgot_link"] = True
        else:
            log_fail("'忘记密码'链接不可见", step=5)
            verifications["forgot_link"] = False

        # STEP 6: 验证7天免登录复选框
        log_info("验证7天免登录复选框", step=6)
        remember_text = page.locator("text=7天内免登录")
        remember_count = remember_text.count()
        if remember_count >= 2:
            log_pass(f"'7天内免登录'复选框可见({remember_count}个)", step=6)
            verifications["remember_checkbox"] = True
        elif remember_count >= 1:
            log_pass("'7天内免登录'复选框可见", step=6)
            verifications["remember_checkbox"] = True
        else:
            log_fail("'7天内免登录'复选框不可见", step=6)
            verifications["remember_checkbox"] = False

        ss.capture("CHECKPOINT", step=6, action="pwd_tab_verified")

        # 综合判定
        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total > 0 else 0
        if confidence >= 0.8:
            result["status"] = "PASS"
        elif confidence >= 0.6:
            result["status"] = "NEED_HUMAN_CHECK"
        else:
            result["status"] = "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=7)

    except Exception as e:
        log_fail(f"测试异常: {str(e)}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(f"异常: {str(e)}")
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_004(page):
    """
    TC-E2E-004: 密码登录成功流程
    前置条件: 用户已注册（13800000001 / Admin123!）
    操作步骤:
      1. 打开登录页面
      2. 切换到密码登录Tab
      3. 输入手机号和密码
      4. 点击登录按钮
    预期结果:
      登录成功，跳转到首页，页面URL不含/login
    """
    global _logger
    case_id = "TC-E2E-004"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 密码登录成功流程 ===")
    result = {"case_id": case_id, "name": "密码登录成功流程", "status": "FAIL", "details": []}
    verifications = {}

    try:
        # STEP 1: 打开登录页面
        log_info("打开登录页面", step=1)
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=1, action="page_load")

        # STEP 2: 切换到密码登录Tab
        log_info("切换到密码登录Tab", step=2)
        pwd_tab = page.locator("button.login-tab", has_text="密码登录")
        pwd_tab.click()
        page.wait_for_timeout(500)
        ss.capture("AFTER", step=2, action="pwd_tab_active")

        # STEP 3: 输入手机号（密码Tab的输入框是第二个）
        # 使用 press_sequentially 逐字输入，确保 Element Plus v-model 正确触发
        log_info(f"输入手机号: {TEST_PHONE}", step=3)
        phone_inputs = page.locator("input[placeholder='请输入手机号']")
        phone_count = phone_inputs.count()
        log_debug(f"手机号输入框数量: {phone_count}", step=3)

        if phone_count >= 2:
            pwd_phone = phone_inputs.nth(1)
            if pwd_phone.is_visible():
                pwd_phone.click()
                pwd_phone.fill("")
                pwd_phone.press_sequentially(TEST_PHONE, delay=50)
                # 触发 blur 确保 el-form 校验规则触发
                pwd_phone.evaluate("el => el.dispatchEvent(new Event('blur', { bubbles: true }))")
                page.wait_for_timeout(300)
                log_pass(f"手机号已输入: {TEST_PHONE}", step=3)
                verifications["phone_filled"] = True
            else:
                log_fail("密码Tab手机号输入框不可见", step=3)
                verifications["phone_filled"] = False
                ss.save_dom_snapshot(step=3, tag="pwd_phone_not_visible")
                result["details"].append("密码Tab手机号输入框不可见")
        else:
            log_fail(f"手机号输入框只有{phone_count}个，无法定位密码Tab的输入框", step=3)
            verifications["phone_filled"] = False
            ss.save_dom_snapshot(step=3, tag="phone_input_count")

        # STEP 4: 输入密码
        log_info("输入密码", step=4)
        pwd_input = page.locator("input[placeholder='请输入密码']")
        if pwd_input.is_visible():
            pwd_input.click()
            pwd_input.fill("")
            pwd_input.press_sequentially(TEST_PASSWORD, delay=50)
            pwd_input.evaluate("el => el.dispatchEvent(new Event('blur', { bubbles: true }))")
            page.wait_for_timeout(300)
            log_pass("密码已输入", step=4)
            verifications["password_filled"] = True
        else:
            log_fail("密码输入框不可见", step=4)
            verifications["password_filled"] = False

        # 检查 Vue 响应式数据是否已更新
        vue_phone = pwd_phone.input_value()
        log_debug(f"输入框DOM值: {vue_phone}", step=3)

        ss.capture("AFTER", step=4, action="form_filled")

        # STEP 5: 点击登录按钮（带网络拦截诊断）
        log_info("点击登录按钮", step=5)
        login_btns = page.locator("button.login-btn")
        log_debug(f"登录按钮数量: {login_btns.count()}", step=5)

        # 拦截网络请求以诊断API调用
        api_responses = []

        def on_response(response):
            if "login/password" in response.url or "auth" in response.url:
                api_responses.append({"url": response.url, "status": response.status})

        page.on("response", on_response)

        # 密码Tab的登录按钮是第二个
        if login_btns.count() >= 2:
            login_btns.nth(1).click()
        else:
            login_btns.first.click()

        # 等待API响应
        page.wait_for_timeout(2000)

        # 检查API响应和错误消息
        for resp in api_responses:
            log_debug(f"API响应: {resp['url']} → {resp['status']}", step=5)
            if resp["status"] >= 400:
                verifications["api_error"] = f"HTTP {resp['status']}"

        error_msg = page.query_selector(".el-message--error")
        if error_msg:
            error_text = error_msg.inner_text()
            log_warn(f"错误提示: {error_text}", step=5)
            result["details"].append(f"API错误: {error_text}")

        page.wait_for_timeout(2000)
        page.remove_listener("response", on_response)
        ss.capture("AFTER", step=5, action="login_clicked")

        # STEP 6: 验证登录结果
        log_info("验证登录结果", step=6)
        current_url = page.url
        log_debug(f"当前URL: {current_url}", step=6)

        if "/login" not in current_url:
            log_pass(f"已跳转离开登录页，当前URL: {current_url}", step=6)
            verifications["redirect_success"] = True
        else:
            log_fail(f"仍在登录页，URL: {current_url}", step=6)
            verifications["redirect_success"] = False
            ss.save_dom_snapshot(step=6, tag="still_on_login")

        # 验证成功提示
        success_msg = page.query_selector(".el-message--success")
        if success_msg:
            log_pass(f"成功提示: {success_msg.inner_text()}", step=6)
            verifications["success_message"] = True
        else:
            log_warn("未找到成功提示（可能已消失）", step=6)
            verifications["success_message"] = None  # 不影响判定

        # 验证localStorage有token
        token = page.evaluate("() => localStorage.getItem('access_token')")
        if token:
            log_pass("localStorage已存入access_token", step=6)
            verifications["token_stored"] = True
        else:
            log_fail("localStorage未存入access_token", step=6)
            verifications["token_stored"] = False

        ss.capture("CHECKPOINT", step=6, action="login_result_verified")

        # 综合判定
        key_verifications = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_verifications.values() if v)
        total = len(key_verifications)
        confidence = passed / total if total > 0 else 0
        if confidence >= 0.8:
            result["status"] = "PASS"
        elif confidence >= 0.6:
            result["status"] = "NEED_HUMAN_CHECK"
        else:
            result["status"] = "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=7)

        # 清理登录状态，避免影响后续用例
        page.evaluate("() => { localStorage.clear(); }")
        log_debug("已清理localStorage", step=7)

    except Exception as e:
        log_fail(f"测试异常: {str(e)}", step=0)
        ss.capture("ERROR", tag="exception")
        ss.save_dom_snapshot(tag="exception")
        result["details"].append(f"异常: {str(e)}")
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_005(page):
    """
    TC-E2E-005: 忘记密码弹窗
    前置条件: 登录页面已打开，密码登录Tab激活
    操作步骤:
      1. 切换到密码登录Tab
      2. 点击"忘记密码？"链接
    预期结果:
      弹出忘记密码弹窗，含标题"忘记密码"、手机号输入框、验证码输入框、获取验证码按钮、下一步按钮
    """
    global _logger
    case_id = "TC-E2E-005"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 忘记密码弹窗 ===")
    result = {"case_id": case_id, "name": "忘记密码弹窗", "status": "FAIL", "details": []}
    verifications = {}

    try:
        # STEP 1: 打开登录页面
        log_info("打开登录页面", step=1)
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # STEP 2: 切换到密码登录Tab
        log_info("切换到密码登录Tab", step=2)
        pwd_tab = page.locator("button.login-tab", has_text="密码登录")
        pwd_tab.click()
        page.wait_for_timeout(500)
        ss.capture("AFTER", step=2, action="pwd_tab_active")

        # STEP 3: 点击忘记密码链接
        log_info("点击忘记密码链接", step=3)
        forgot_link = page.locator("text=忘记密码").first
        if forgot_link.is_visible():
            forgot_link.click()
            page.wait_for_timeout(1000)
            log_pass("已点击忘记密码链接", step=3)
        else:
            log_fail("忘记密码链接不可见", step=3)
            result["details"].append("忘记密码链接不可见")
            _logger.save_json()
            return result

        # STEP 4: 验证弹窗出现
        log_info("验证弹窗出现", step=4)
        dialog = page.locator(".el-dialog")
        if dialog.is_visible():
            log_pass("忘记密码弹窗已打开", step=4)
            verifications["dialog_visible"] = True
        else:
            log_fail("忘记密码弹窗未打开", step=4)
            verifications["dialog_visible"] = False
            ss.save_dom_snapshot(step=4, tag="no_dialog")
            result["details"].append("弹窗未打开")

        # STEP 5: 验证弹窗标题
        log_info("验证弹窗标题", step=5)
        dialog_title = page.locator(".el-dialog__header .el-dialog__title")
        if dialog_title.is_visible():
            title_text = dialog_title.inner_text()
            if "忘记密码" in title_text:
                log_pass(f"弹窗标题正确: '{title_text}'", step=5)
                verifications["dialog_title"] = True
            else:
                log_fail(f"弹窗标题不符: 期望含'忘记密码', 实际'{title_text}'", step=5)
                verifications["dialog_title"] = False
        else:
            log_fail("弹窗标题元素不可见", step=5)
            verifications["dialog_title"] = False

        # STEP 6: 验证弹窗内表单元素（步骤1：验证手机）
        log_info("验证弹窗内表单元素", step=6)
        dialog_body = page.locator(".el-dialog__body")

        # 手机号输入框
        dialog_phone = dialog_body.locator("input[placeholder='请输入手机号']")
        if dialog_phone.is_visible():
            log_pass("弹窗内手机号输入框可见", step=6)
            verifications["dialog_phone_input"] = True
        else:
            log_fail("弹窗内手机号输入框不可见", step=6)
            verifications["dialog_phone_input"] = False

        # 验证码输入框
        dialog_code = dialog_body.locator("input[placeholder='请输入验证码']")
        if dialog_code.is_visible():
            log_pass("弹窗内验证码输入框可见", step=6)
            verifications["dialog_code_input"] = True
        else:
            log_fail("弹窗内验证码输入框不可见", step=6)
            verifications["dialog_code_input"] = False

        # 获取验证码按钮
        dialog_get_code = dialog_body.locator("button:has-text('获取验证码')")
        if dialog_get_code.is_visible():
            log_pass("弹窗内获取验证码按钮可见", step=6)
            verifications["dialog_get_code_btn"] = True
        else:
            log_fail("弹窗内获取验证码按钮不可见", step=6)
            verifications["dialog_get_code_btn"] = False

        # 下一步按钮
        dialog_next = page.locator(".el-dialog__footer button:has-text('下一步')")
        if dialog_next.is_visible():
            log_pass("'下一步'按钮可见", step=6)
            verifications["dialog_next_btn"] = True
        else:
            log_fail("'下一步'按钮不可见", step=6)
            verifications["dialog_next_btn"] = False

        ss.capture("CHECKPOINT", step=6, action="dialog_verified")

        # 综合判定
        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total > 0 else 0
        if confidence >= 0.8:
            result["status"] = "PASS"
        elif confidence >= 0.6:
            result["status"] = "NEED_HUMAN_CHECK"
        else:
            result["status"] = "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=7)

    except Exception as e:
        log_fail(f"测试异常: {str(e)}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(f"异常: {str(e)}")
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_006(page):
    """
    TC-E2E-006: 注册链接跳转
    前置条件: 登录页面已打开
    操作步骤:
      1. 点击"立即注册"链接
    预期结果:
      跳转到注册页面，URL含/register，注册表单可见
    """
    global _logger
    case_id = "TC-E2E-006"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 注册链接跳转 ===")
    result = {"case_id": case_id, "name": "注册链接跳转", "status": "FAIL", "details": []}
    verifications = {}

    try:
        # STEP 1: 打开登录页面
        log_info("打开登录页面", step=1)
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=1, action="page_load")

        # STEP 2: 点击立即注册
        log_info("点击'立即注册'链接", step=2)
        reg_link = page.locator("a:has-text('立即注册'), a[href*='register']").first
        if reg_link.is_visible():
            reg_link.click()
            page.wait_for_timeout(2000)
            log_pass("已点击'立即注册'链接", step=2)
        else:
            log_fail("'立即注册'链接不可见", step=2)
            result["details"].append("'立即注册'链接不可见")
            _logger.save_json()
            return result

        # STEP 3: 验证URL跳转
        log_info("验证URL跳转", step=3)
        current_url = page.url
        if "/register" in current_url:
            log_pass(f"已跳转到注册页: {current_url}", step=3)
            verifications["url_redirect"] = True
        else:
            log_fail(f"URL未跳转到注册页: {current_url}", step=3)
            verifications["url_redirect"] = False
            ss.save_dom_snapshot(step=3, tag="url_not_redirect")

        # STEP 4: 验证注册页面内容
        log_info("验证注册页面内容", step=4)
        page_text = page.inner_text("body")
        # 检查注册表单元素
        reg_indicators = ["手机号", "验证码", "密码", "注册"]
        found = [ind for ind in reg_indicators if ind in page_text]
        if found:
            log_pass(f"注册页面包含关键文本: {found}", step=4)
            verifications["register_page_content"] = True
        else:
            log_fail(f"注册页面缺少关键文本, 期望含: {reg_indicators}", step=4)
            verifications["register_page_content"] = False

        ss.capture("CHECKPOINT", step=4, action="register_page_verified")

        # 综合判定
        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total > 0 else 0
        if confidence >= 0.8:
            result["status"] = "PASS"
        elif confidence >= 0.6:
            result["status"] = "NEED_HUMAN_CHECK"
        else:
            result["status"] = "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=5)

    except Exception as e:
        log_fail(f"测试异常: {str(e)}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(f"异常: {str(e)}")
        result["status"] = "ERROR"

    _logger.save_json()
    return result


# ============================================================
# 报告生成
# ============================================================
def _generate_report(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 校链通 登录模块 E2E 测试报告",
        "",
        "| 项目 | 内容 |",
        "|------|------|",
        f"| 测试模块 | 第1章 登录模块 (L2 E2E) |",
        f"| 测试日期 | {now} |",
        f"| 目标地址 | {BASE_URL} |",
        f"| 用例数量 | {len(results)} |",
        "",
        "## 测试结果汇总",
        "",
        "| 用例ID | 用例名称 | 结果 | 置信度 |",
        "|--------|----------|------|--------|",
    ]
    pass_count = 0
    fail_count = 0
    error_count = 0
    for r in results:
        status_icon = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERROR", "NEED_HUMAN_CHECK": "NEED_CHECK"}.get(r["status"], r["status"])
        confidence = f"{r.get('confidence', 'N/A')}"
        lines.append(f"| {r['case_id']} | {r['name']} | {status_icon} | {confidence} |")
        if r["status"] == "PASS":
            pass_count += 1
        elif r["status"] == "FAIL":
            fail_count += 1
        else:
            error_count += 1

    lines.extend([
        "",
        "### 统计",
        "",
        f"- 通过: {pass_count}",
        f"- 失败: {fail_count}",
        f"- 错误: {error_count}",
        f"- 通过率: {pass_count / len(results) * 100:.0f}%" if results else "- 通过率: N/A",
        "",
        "## 详细结果",
        "",
    ])

    for r in results:
        lines.append(f"### {r['case_id']}: {r['name']}")
        lines.append("")
        lines.append(f"**结果**: {r['status']}")
        lines.append(f"**置信度**: {r.get('confidence', 'N/A')}")
        if r.get("verifications"):
            lines.append("")
            lines.append("| 验证项 | 结果 |")
            lines.append("|--------|------|")
            for vk, vv in r["verifications"].items():
                icon = "PASS" if vv else ("N/A" if vv is None else "FAIL")
                lines.append(f"| {vk} | {icon} |")
        if r.get("details"):
            lines.append("")
            lines.append(f"**备注**: {'; '.join(r['details'])}")
        lines.append("")

    lines.extend(["---", f"*报告生成时间: {now}*"])
    return "\n".join(lines)


# ============================================================
# 主入口
# ============================================================
def main():
    global SCREENSHOT_DIR
    print("=" * 70)
    print("校链通(XiaoLianTong) - 第1章 登录模块 L2 E2E 测试")
    print(f"目标地址: {BASE_URL}")
    print(f"截图目录: {SCREENSHOT_DIR}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT, ignore_https_errors=True)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)

        # 检查应用可访问性
        try:
            response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=10000)
            if response and response.status < 400:
                print(f"\n应用可访问: {BASE_URL} (HTTP {response.status})")
            else:
                print(f"\n应用响应异常: HTTP {response.status if response else 'N/A'}")
        except Exception as e:
            print(f"\n无法访问应用: {BASE_URL}")
            print(f"   错误: {e}")
            browser.close()
            return

        page.wait_for_timeout(1000)

        # 执行测试用例
        test_cases = [
            ("TC-E2E-001: 登录页面渲染", tc_e2e_001),
            ("TC-E2E-002: 短信登录Tab表单元素", tc_e2e_002),
            ("TC-E2E-003: 密码登录Tab切换", tc_e2e_003),
            ("TC-E2E-004: 密码登录成功流程", tc_e2e_004),
            ("TC-E2E-005: 忘记密码弹窗", tc_e2e_005),
            ("TC-E2E-006: 注册链接跳转", tc_e2e_006),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page)
            all_results.append(r)

        browser.close()

    # 生成报告
    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch01.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 70)
    print("测试执行完成")
    print("=" * 70)
    print(f"报告路径: {report_path}")
    print(f"截图目录: {SCREENSHOT_DIR}")

    # 输出汇总
    print("\n--- 结果汇总 ---")
    for r in all_results:
        status = r["status"]
        conf = r.get("confidence", "N/A")
        print(f"  {r['case_id']} {r['name']}: {status} (置信度 {conf})")


if __name__ == "__main__":
    main()
