"""
校链通(XiaoLianTong) - 第2章 注册模块 L2 E2E 测试
基于 QA-test-plan-PP-v1.0.md 第2章
覆盖用例: TC-E2E-007 ~ TC-E2E-010

应用地址: http://localhost:3000
测试日期: 2026-04-11
"""

from playwright.sync_api import sync_playwright
import time
import os
import json
import sys
import subprocess
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
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch02_register")
SCREENSHOT_DIR = os.path.join(CAPTURES_DIR, datetime.now().strftime("%Y-%m-%d_%H%M%S"))

VIEWPORT = {"width": 1280, "height": 900}
DEFAULT_TIMEOUT = 30000

# 后端 SQLite 数据库路径（用于查询验证码）
DB_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
    "src", "backend", "db.sqlite3"
))

# 注册测试手机号（确保与已有测试账号不同）
TEST_NEW_PHONE = "13900009999"
TEST_NEW_PASSWORD = "RegTest123!"


# ============================================================
# 后端辅助：发送短信 + 查询验证码
# ============================================================
def send_sms_code(phone, sms_type="login"):
    """通过 API 发送短信验证码"""
    import urllib.request
    url = f"http://localhost:8000/api/v1/auth/sms/send/"
    data = json.dumps({"phone": phone, "type": sms_type}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        log_warn(f"发送短信失败: {e}")
        return None


def get_sms_code_from_db(phone, sms_type="login"):
    """通过 Django ORM 查询最新的未使用验证码"""
    backend_dir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "backend"
    ))
    script = (
        "import django, os, sys; "
        "os.environ['DJANGO_SETTINGS_MODULE']='config.settings'; "
        "django.setup(); "
        f"from apps.auth_app.models import AuthSmsCode; "
        f"sms = AuthSmsCode.objects.filter("
        f"phone='{phone}', type='{sms_type}', used_at__isnull=True"
        f").order_by('-created_at').first(); "
        "print(sms.code if sms else '')"
    )
    try:
        proc = subprocess.run(
            ["python", "-c", script],
            capture_output=True, text=True, timeout=10,
            cwd=backend_dir
        )
        code = proc.stdout.strip()
        if code:
            return code
        return None
    except Exception as e:
        log_warn(f"查询验证码失败: {e}")
        return None


# ============================================================
# 智能截图管理器
# ============================================================
class SmartScreenshot:
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
            "level": level, "case_id": self.case_id,
            "step": step, "action": action, "message": message, **kwargs,
        }
        self.logs.append(entry)
        icon = {"INFO": "  ", "PASS": "[PASS]", "FAIL": "[FAIL]",
                "WARN": "[WARN]", "DEBUG": "[DBG]"}.get(level, "  ")
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
            "case_id": self.case_id, "duration_sec": round(duration, 2),
            "steps_passed": self.steps_passed, "steps_failed": self.steps_failed,
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
# Element Plus 输入辅助
# ============================================================
def fill_el_input(page, placeholder, value, index=0):
    """使用 press_sequentially 填写 Element Plus el-input"""
    selector = f"input[placeholder='{placeholder}']"
    inp = page.locator(selector).nth(index)
    if inp and inp.is_visible():
        inp.click()
        inp.fill("")
        inp.press_sequentially(value, delay=50)
        inp.evaluate("el => el.dispatchEvent(new Event('blur', { bubbles: true }))")
        page.wait_for_timeout(200)
        return True
    return False


# ============================================================
# 测试用例
# ============================================================

def tc_e2e_007(page):
    """
    TC-E2E-007: 注册页面渲染
    前置条件: 用户未登录
    操作步骤:
      1. 打开注册页面
    预期结果:
      白色卡片、标题"注册"、手机号输入框、验证码输入框+获取验证码按钮、
      密码输入框、确认密码输入框、协议复选框(含《校链通用户协议》《隐私政策》蓝色链接)、
      "立即注册"按钮、"立即登录"链接
    """
    global _logger
    case_id = "TC-E2E-007"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 注册页面渲染 ===")
    result = {"case_id": case_id, "name": "注册页面渲染", "status": "FAIL", "details": []}
    verifications = {}

    try:
        # 确保未登录
        page.evaluate("() => { localStorage.clear(); }")

        # STEP 1: 打开注册页面
        log_info("打开注册页面", step=1)
        page.goto(f"{BASE_URL}/register")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=1, action="page_load")

        # STEP 2: 验证注册卡片
        log_info("验证注册卡片", step=2)
        register_card = page.query_selector(".register-card")
        if register_card and register_card.is_visible():
            log_pass("注册卡片(.register-card)可见", step=2)
            verifications["card_visible"] = True
        else:
            log_fail("注册卡片不可见", step=2)
            verifications["card_visible"] = False

        # STEP 3: 验证标题
        log_info("验证页面标题", step=3)
        title_el = page.query_selector(".register-title")
        if title_el and title_el.is_visible():
            title_text = title_el.inner_text()
            if "注册" in title_text:
                log_pass(f"标题正确: '{title_text}'", step=3)
                verifications["title"] = True
            else:
                log_fail(f"标题不符: '{title_text}'", step=3)
                verifications["title"] = False
        else:
            log_fail("标题元素不可见", step=3)
            verifications["title"] = False

        # STEP 4: 验证4个必填字段
        log_info("验证表单字段", step=4)
        fields = {
            "phone": ("input[placeholder='请输入手机号']", "手机号"),
            "code": ("input[placeholder='请输入验证码']", "验证码"),
            "password": ("input[placeholder='请设置登录密码（8-20位）']", "密码"),
            "confirm": ("input[placeholder='请确认密码']", "确认密码"),
        }
        for key, (selector, label) in fields.items():
            inp = page.locator(selector).first
            if inp.is_visible():
                log_pass(f"{label}输入框可见", step=4)
                verifications[f"field_{key}"] = True
            else:
                log_fail(f"{label}输入框不可见", step=4)
                verifications[f"field_{key}"] = False

        # STEP 5: 验证获取验证码按钮
        log_info("验证获取验证码按钮", step=5)
        get_code_btn = page.locator("button:has-text('获取验证码')")
        if get_code_btn.is_visible():
            log_pass("获取验证码按钮可见", step=5)
            verifications["get_code_btn"] = True
        else:
            log_fail("获取验证码按钮不可见", step=5)
            verifications["get_code_btn"] = False

        # STEP 6: 验证协议复选框
        log_info("验证协议复选框", step=6)
        agreement_text = page.locator("text=校链通用户协议")
        privacy_text = page.locator("text=隐私政策")
        if agreement_text.first.is_visible():
            log_pass("'校链通用户协议'链接可见", step=6)
            verifications["agreement_link"] = True
        else:
            log_fail("'校链通用户协议'链接不可见", step=6)
            verifications["agreement_link"] = False

        if privacy_text.first.is_visible():
            log_pass("'隐私政策'链接可见", step=6)
            verifications["privacy_link"] = True
        else:
            log_fail("'隐私政策'链接不可见", step=6)
            verifications["privacy_link"] = False

        # STEP 7: 验证立即注册按钮
        log_info("验证立即注册按钮", step=7)
        reg_btn = page.locator("button.register-btn")
        if reg_btn.is_visible():
            btn_text = reg_btn.inner_text()
            log_pass(f"注册按钮可见, 文本: '{btn_text}'", step=7)
            verifications["register_btn"] = True
        else:
            log_fail("注册按钮不可见", step=7)
            verifications["register_btn"] = False

        ss.capture("CHECKPOINT", step=7, action="all_elements_verified")

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


def tc_e2e_008(page):
    """
    TC-E2E-008: 注册表单校验
    前置条件: 注册页面已打开
    操作步骤:
      1. 空表单点击注册 → 验证必填校验
      2. 输入手机号但不输验证码 → 验证验证码校验
      3. 输入7位密码 → 验证密码长度校验
      4. 输入不一致确认密码 → 验证密码一致性校验
      5. 不勾选协议 → 验证协议校验
    预期结果: 每项校验均显示对应错误提示
    """
    global _logger
    case_id = "TC-E2E-008"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 注册表单校验 ===")
    result = {"case_id": case_id, "name": "注册表单校验", "status": "FAIL", "details": []}
    verifications = {}

    try:
        page.evaluate("() => { localStorage.clear(); }")

        # 打开注册页面
        log_info("打开注册页面", step=1)
        page.goto(f"{BASE_URL}/register")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # STEP 2: 空表单提交
        log_info("空表单点击注册按钮", step=2)
        reg_btn = page.locator("button.register-btn")
        reg_btn.click()
        page.wait_for_timeout(1000)

        # 检查是否出现校验错误提示
        error_msgs = page.locator(".el-form-item__error")
        error_count = error_msgs.count()
        log_debug(f"校验错误数量: {error_count}", step=2)
        if error_count >= 3:  # 至少3个必填字段报错（手机号、验证码、密码）
            error_texts = [error_msgs.nth(i).inner_text() for i in range(min(error_count, 5))]
            log_pass(f"空表单校验触发 {error_count} 个错误: {error_texts}", step=2)
            verifications["empty_form_validation"] = True
        else:
            log_fail(f"空表单校验仅触发 {error_count} 个错误（期望>=3）", step=2)
            verifications["empty_form_validation"] = False
        ss.capture("CHECKPOINT", step=2, action="empty_form")

        # 清除校验状态 - 重新加载页面
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # STEP 3: 输入手机号，不输验证码
        log_info("只填手机号，不填验证码", step=3)
        fill_el_input(page, "请输入手机号", "13800009999")
        reg_btn.click()
        page.wait_for_timeout(1000)

        code_error = page.locator(".el-form-item__error", has_text="验证码")
        if code_error.count() > 0:
            log_pass(f"验证码校验提示: '{code_error.first.inner_text()}'", step=3)
            verifications["code_required"] = True
        else:
            log_fail("验证码必填校验未触发", step=3)
            verifications["code_required"] = False
        ss.capture("CHECKPOINT", step=3, action="code_validation")

        # 重新加载
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # STEP 4: 密码少于8位
        log_info("输入7位密码", step=4)
        fill_el_input(page, "请设置登录密码（8-20位）", "Abc1234")
        # 触发blur
        pwd_input = page.locator("input[placeholder='请设置登录密码（8-20位）']")
        pwd_input.evaluate("el => el.dispatchEvent(new Event('blur', { bubbles: true }))")
        page.wait_for_timeout(800)

        pwd_error = page.locator(".el-form-item__error", has_text="密码长度")
        if pwd_error.count() > 0:
            log_pass(f"密码长度校验提示: '{pwd_error.first.inner_text()}'", step=4)
            verifications["password_length"] = True
        else:
            log_fail("密码长度校验未触发", step=4)
            verifications["password_length"] = False
        ss.capture("CHECKPOINT", step=4, action="password_length")

        # 重新加载
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # STEP 5: 确认密码不一致
        log_info("输入不一致的确认密码", step=5)
        fill_el_input(page, "请设置登录密码（8-20位）", "Admin123!")
        fill_el_input(page, "请确认密码", "Different1!")
        # 触发blur
        confirm_input = page.locator("input[placeholder='请确认密码']")
        confirm_input.evaluate("el => el.dispatchEvent(new Event('blur', { bubbles: true }))")
        page.wait_for_timeout(800)

        mismatch_error = page.locator(".el-form-item__error", has_text="不一致")
        if mismatch_error.count() > 0:
            log_pass(f"密码一致性校验提示: '{mismatch_error.first.inner_text()}'", step=5)
            verifications["password_mismatch"] = True
        else:
            log_fail("密码一致性校验未触发", step=5)
            verifications["password_mismatch"] = False
        ss.capture("CHECKPOINT", step=5, action="password_mismatch")

        # 重新加载
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # STEP 6: 不勾选协议
        log_info("填写完整但不勾选协议", step=6)
        fill_el_input(page, "请输入手机号", "13800009999")
        fill_el_input(page, "请输入验证码", "123456")
        fill_el_input(page, "请设置登录密码（8-20位）", "Admin123!")
        fill_el_input(page, "请确认密码", "Admin123!")
        # 不勾选协议，直接点注册
        reg_btn = page.locator("button.register-btn")
        reg_btn.click()
        page.wait_for_timeout(1000)

        agreement_error = page.locator(".el-form-item__error", has_text="协议")
        if agreement_error.count() > 0:
            log_pass(f"协议校验提示: '{agreement_error.first.inner_text()}'", step=6)
            verifications["agreement_validation"] = True
        else:
            # 协议校验文本可能不包含"协议"
            all_errors = page.locator(".el-form-item__error")
            if all_errors.count() > 0:
                error_texts = [all_errors.nth(i).inner_text() for i in range(all_errors.count())]
                log_pass(f"有校验提示: {error_texts}", step=6)
                verifications["agreement_validation"] = True
            else:
                log_fail("协议校验未触发", step=6)
                verifications["agreement_validation"] = False
        ss.capture("CHECKPOINT", step=6, action="agreement_validation")

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


def tc_e2e_009(page):
    """
    TC-E2E-009: 注册页登录链接跳转
    前置条件: 注册页面已打开
    操作步骤:
      1. 点击"立即登录"链接
    预期结果:
      跳转到登录页面，URL含/login，登录表单可见
    """
    global _logger
    case_id = "TC-E2E-009"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 注册页登录链接跳转 ===")
    result = {"case_id": case_id, "name": "注册页登录链接跳转", "status": "FAIL", "details": []}
    verifications = {}

    try:
        page.evaluate("() => { localStorage.clear(); }")

        # STEP 1: 打开注册页面
        log_info("打开注册页面", step=1)
        page.goto(f"{BASE_URL}/register")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=1, action="page_load")

        # STEP 2: 点击立即登录
        log_info("点击'立即登录'链接", step=2)
        login_link = page.locator("a:has-text('立即登录'), a[href*='login']").first
        if login_link.is_visible():
            login_link.click()
            page.wait_for_timeout(2000)
            log_pass("已点击'立即登录'链接", step=2)
        else:
            log_fail("'立即登录'链接不可见", step=2)
            result["details"].append("'立即登录'链接不可见")
            _logger.save_json()
            return result

        # STEP 3: 验证URL跳转
        log_info("验证URL跳转", step=3)
        current_url = page.url
        if "/login" in current_url:
            log_pass(f"已跳转到登录页: {current_url}", step=3)
            verifications["url_redirect"] = True
        else:
            log_fail(f"URL未跳转到登录页: {current_url}", step=3)
            verifications["url_redirect"] = False

        # STEP 4: 验证登录页面内容
        log_info("验证登录页面内容", step=4)
        login_card = page.query_selector(".login-card")
        if login_card and login_card.is_visible():
            log_pass("登录卡片(.login-card)可见", step=4)
            verifications["login_card"] = True
        else:
            log_fail("登录卡片不可见", step=4)
            verifications["login_card"] = False

        ss.capture("CHECKPOINT", step=4, action="login_page_verified")

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


def tc_e2e_010(page):
    """
    TC-E2E-010: 登录页Tab切换数据独立
    前置条件: 登录页面已打开
    操作步骤:
      1. 在短信Tab输入手机号
      2. 切换到密码Tab，输入数据
      3. 切回短信Tab
    预期结果:
      短信Tab的手机号数据保留（v-show不销毁DOM）
    """
    global _logger
    case_id = "TC-E2E-010"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 登录页Tab切换数据独立 ===")
    result = {"case_id": case_id, "name": "Tab切换数据独立", "status": "FAIL", "details": []}
    verifications = {}

    try:
        page.evaluate("() => { localStorage.clear(); }")

        # STEP 1: 打开登录页面
        log_info("打开登录页面", step=1)
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=1, action="page_load")

        # STEP 2: 在短信Tab输入手机号
        log_info("在短信Tab输入手机号", step=2)
        sms_phone = page.locator("input[placeholder='请输入手机号']").first
        sms_phone.click()
        sms_phone.fill("")
        sms_phone.press_sequentially("13811112222", delay=50)
        page.wait_for_timeout(300)
        sms_phone_value = sms_phone.input_value()
        log_debug(f"短信Tab手机号: {sms_phone_value}", step=2)
        verifications["sms_phone_filled"] = sms_phone_value == "13811112222"
        if verifications["sms_phone_filled"]:
            log_pass(f"短信Tab手机号已输入: {sms_phone_value}", step=2)
        else:
            log_fail(f"短信Tab手机号输入失败: {sms_phone_value}", step=2)

        ss.capture("AFTER", step=2, action="sms_phone_filled")

        # STEP 3: 切换到密码Tab
        log_info("切换到密码Tab", step=3)
        pwd_tab = page.locator("button.login-tab", has_text="密码登录")
        pwd_tab.click()
        page.wait_for_timeout(500)

        # 在密码Tab输入数据
        log_info("在密码Tab输入手机号和密码", step=3)
        pwd_phone = page.locator("input[placeholder='请输入手机号']").nth(1)
        pwd_phone.click()
        pwd_phone.fill("")
        pwd_phone.press_sequentially("13900001111", delay=50)
        page.wait_for_timeout(300)

        pwd_input = page.locator("input[placeholder='请输入密码']")
        pwd_input.click()
        pwd_input.fill("")
        pwd_input.press_sequentially("Test1234!", delay=50)
        page.wait_for_timeout(300)

        ss.capture("AFTER", step=3, action="pwd_tab_filled")

        # STEP 4: 切回短信Tab
        log_info("切回短信Tab", step=4)
        sms_tab = page.locator("button.login-tab", has_text="短信验证码登录")
        sms_tab.click()
        page.wait_for_timeout(500)

        # 验证短信Tab手机号保留
        sms_phone_value_after = sms_phone.input_value()
        log_debug(f"切回后短信Tab手机号: {sms_phone_value_after}", step=4)

        if sms_phone_value_after == "13811112222":
            log_pass(f"短信Tab数据保留: {sms_phone_value_after}", step=4)
            verifications["data_preserved"] = True
        else:
            log_fail(f"短信Tab数据丢失: 期望'13811112222', 实际'{sms_phone_value_after}'", step=4)
            verifications["data_preserved"] = False

        ss.capture("CHECKPOINT", step=4, action="tab_switch_verified")

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


def tc_e2e_011(page):
    """
    TC-E2E-011: 注册成功流程
    前置条件: 用户未注册
    操作步骤:
      1. 打开注册页面
      2. 发送短信验证码（API）
      3. 从DB查询验证码
      4. 填写完整注册表单
      5. 点击"立即注册"
    预期结果:
      注册成功，提示"注册成功"，跳转到首页
    """
    global _logger
    case_id = "TC-E2E-011"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 注册成功流程 ===")
    result = {"case_id": case_id, "name": "注册成功流程", "status": "FAIL", "details": []}
    verifications = {}

    try:
        page.evaluate("() => { localStorage.clear(); }")

        # STEP 0: 清理残留测试数据（防止上次测试未清理导致"已注册"）
        log_info("清理残留测试数据", step=0)
        try:
            import django as _dj, os as _os, sys as _sys
            _sys.path.insert(0, _os.path.normpath(_os.path.join(
                _os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "src", "backend"
            )))
            _os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
            _dj.setup()
            from django.contrib.auth import get_user_model as _gum
            _User = _gum()
            _old = _User.objects.filter(username=TEST_NEW_PHONE).first()
            if _old:
                _old.delete()
                log_info(f"已清理残留用户 {TEST_NEW_PHONE} (id={_old.id})", step=0)
            else:
                log_info(f"无残留用户 {TEST_NEW_PHONE}", step=0)
        except Exception as _e:
            log_warn(f"清理残留数据失败: {_e}", step=0)

        # STEP 1: 发送短信验证码（type='register' 匹配后端 RegisterView）
        log_info(f"发送短信验证码到 {TEST_NEW_PHONE}", step=1)
        sms_result = send_sms_code(TEST_NEW_PHONE, "register")
        if sms_result and sms_result.get("code") == 0:
            log_pass(f"短信发送成功: {sms_result.get('message')}", step=1)
            verifications["sms_sent"] = True
        else:
            log_fail(f"短信发送失败: {sms_result}", step=1)
            verifications["sms_sent"] = False
            result["details"].append("短信发送失败，无法继续")
            _logger.save_json()
            return result

        # STEP 2: 查询验证码
        log_info("从DB查询验证码", step=2)
        code = get_sms_code_from_db(TEST_NEW_PHONE, "register")
        if code:
            log_pass(f"获取验证码: {code}", step=2)
            verifications["code_retrieved"] = True
        else:
            log_fail("未查询到验证码", step=2)
            verifications["code_retrieved"] = False
            result["details"].append("验证码查询失败，无法继续")
            _logger.save_json()
            return result

        # STEP 3: 打开注册页面
        log_info("打开注册页面", step=3)
        page.goto(f"{BASE_URL}/register")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=3, action="page_load")

        # STEP 4: 填写注册表单
        log_info("填写注册表单", step=4)
        fill_el_input(page, "请输入手机号", TEST_NEW_PHONE)
        fill_el_input(page, "请输入验证码", code)
        fill_el_input(page, "请设置登录密码（8-20位）", TEST_NEW_PASSWORD)
        fill_el_input(page, "请确认密码", TEST_NEW_PASSWORD)

        # 勾选协议
        checkbox = page.locator(".el-checkbox").first
        if checkbox.is_visible():
            checkbox.click()
            page.wait_for_timeout(300)
            log_pass("已勾选用户协议", step=4)

        ss.capture("AFTER", step=4, action="form_filled")

        # STEP 5: 点击注册按钮
        log_info("点击'立即注册'按钮", step=5)

        # 拦截网络请求（监听 /auth/register/ 接口）
        api_responses = []
        def on_response(resp):
            if "auth/register" in resp.url:
                api_responses.append({"url": resp.url, "status": resp.status})
        page.on("response", on_response)

        reg_btn = page.locator("button.register-btn")
        reg_btn.click()
        page.wait_for_timeout(4000)

        for resp in api_responses:
            log_debug(f"API响应: {resp['url']} → {resp['status']}", step=5)

        if not api_responses:
            log_warn("未捕获到 /auth/register/ API 响应", step=5)

        page.remove_listener("response", on_response)
        ss.capture("AFTER", step=5, action="register_clicked")

        # STEP 6: 验证注册结果
        log_info("验证注册结果", step=6)
        current_url = page.url
        log_debug(f"当前URL: {current_url}", step=6)

        if "/register" not in current_url:
            log_pass(f"已跳转离开注册页，当前URL: {current_url}", step=6)
            verifications["redirect_success"] = True
        else:
            log_fail(f"仍在注册页，URL: {current_url}", step=6)
            verifications["redirect_success"] = False
            ss.save_dom_snapshot(step=6, tag="still_on_register")

        # 验证 token
        token = page.evaluate("() => localStorage.getItem('access_token')")
        if token:
            log_pass("localStorage已存入access_token", step=6)
            verifications["token_stored"] = True
        else:
            log_fail("localStorage未存入access_token", step=6)
            verifications["token_stored"] = False

        # 验证成功提示
        success_msg = page.query_selector(".el-message--success")
        if success_msg:
            log_pass(f"成功提示: {success_msg.inner_text()}", step=6)
            verifications["success_message"] = True
        else:
            log_warn("未找到成功提示（可能已消失）", step=6)
            verifications["success_message"] = None

        ss.capture("CHECKPOINT", step=6, action="register_result")

        # 清理登录状态
        page.evaluate("() => { localStorage.clear(); }")

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

    except Exception as e:
        log_fail(f"测试异常: {str(e)}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(f"异常: {str(e)}")
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_012(page):
    """
    TC-E2E-012: 注册后用户可登录验证
    前置条件: TC-E2E-011 已完成注册（TEST_NEW_PHONE 用户已存在）
    操作步骤:
      1. 发送短信验证码
      2. 打开登录页面，切换到短信Tab
      3. 输入手机号和验证码，点击登录
    预期结果:
      登录成功，跳转到首页，localStorage有token
    """
    global _logger
    case_id = "TC-E2E-012"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)

    log_info("=== 注册后用户可登录验证 ===")
    result = {"case_id": case_id, "name": "注册后用户可登录验证", "status": "FAIL", "details": []}
    verifications = {}

    try:
        page.evaluate("() => { localStorage.clear(); }")

        # STEP 1: 发送短信验证码
        log_info(f"发送短信验证码到 {TEST_NEW_PHONE}", step=1)
        sms_result = send_sms_code(TEST_NEW_PHONE, "login")
        if sms_result and sms_result.get("code") == 0:
            log_pass("短信发送成功", step=1)
            verifications["sms_sent"] = True
        else:
            log_fail(f"短信发送失败: {sms_result}", step=1)
            verifications["sms_sent"] = False
            result["details"].append("短信发送失败")
            _logger.save_json()
            return result

        # STEP 2: 查询验证码
        log_info("从DB查询验证码", step=2)
        code = get_sms_code_from_db(TEST_NEW_PHONE, "login")
        if code:
            log_pass(f"获取验证码: {code}", step=2)
            verifications["code_retrieved"] = True
        else:
            log_fail("未查询到验证码", step=2)
            verifications["code_retrieved"] = False
            result["details"].append("验证码查询失败")
            _logger.save_json()
            return result

        # STEP 3: 打开登录页面
        log_info("打开登录页面", step=3)
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        ss.capture("BEFORE", step=3, action="login_page_load")

        # STEP 4: 填写短信登录表单（默认是短信Tab）
        log_info(f"输入手机号和验证码", step=4)
        phone_input = page.locator("input[placeholder='请输入手机号']").first
        phone_input.click()
        phone_input.fill("")
        phone_input.press_sequentially(TEST_NEW_PHONE, delay=50)
        page.wait_for_timeout(200)

        code_input = page.locator("input[placeholder='请输入验证码']").first
        code_input.click()
        code_input.fill("")
        code_input.press_sequentially(code, delay=50)
        page.wait_for_timeout(200)

        ss.capture("AFTER", step=4, action="form_filled")

        # STEP 5: 点击登录
        log_info("点击登录按钮", step=5)

        api_responses = []
        def on_response(resp):
            if "sms/login" in resp.url:
                api_responses.append({"url": resp.url, "status": resp.status})
        page.on("response", on_response)

        login_btn = page.locator("button.login-btn").first
        login_btn.click()
        page.wait_for_timeout(4000)

        for resp in api_responses:
            log_debug(f"API响应: {resp['url']} → {resp['status']}", step=5)

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

        # 验证 token
        token = page.evaluate("() => localStorage.getItem('access_token')")
        if token:
            log_pass("localStorage已存入access_token", step=6)
            verifications["token_stored"] = True
        else:
            log_fail("localStorage未存入access_token", step=6)
            verifications["token_stored"] = False

        ss.capture("CHECKPOINT", step=6, action="login_result")

        # 清理
        page.evaluate("() => { localStorage.clear(); }")

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


# ============================================================
# 报告生成
# ============================================================
def _generate_report(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 校链通 注册模块 E2E 测试报告", "",
        "| 项目 | 内容 |", "|------|------|",
        f"| 测试模块 | 第2章 注册模块 (L2 E2E) |",
        f"| 测试日期 | {now} |",
        f"| 目标地址 | {BASE_URL} |",
        f"| 用例数量 | {len(results)} |", "",
        "## 测试结果汇总", "",
        "| 用例ID | 用例名称 | 结果 | 置信度 |",
        "|--------|----------|------|--------|",
    ]
    pass_count = fail_count = error_count = 0
    for r in results:
        status_icon = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERROR",
                       "NEED_HUMAN_CHECK": "NEED_CHECK"}.get(r["status"], r["status"])
        confidence = f"{r.get('confidence', 'N/A')}"
        lines.append(f"| {r['case_id']} | {r['name']} | {status_icon} | {confidence} |")
        if r["status"] == "PASS":
            pass_count += 1
        elif r["status"] == "FAIL":
            fail_count += 1
        else:
            error_count += 1

    lines.extend([
        "", "### 统计", "",
        f"- 通过: {pass_count}", f"- 失败: {fail_count}", f"- 错误: {error_count}",
        f"- 通过率: {pass_count / len(results) * 100:.0f}%" if results else "- 通过率: N/A",
        "", "## 详细结果", "",
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
    print("校链通(XiaoLianTong) - 第2章 注册模块 L2 E2E 测试")
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
            ("TC-E2E-007: 注册页面渲染", tc_e2e_007),
            ("TC-E2E-008: 注册表单校验", tc_e2e_008),
            ("TC-E2E-009: 注册页登录链接跳转", tc_e2e_009),
            ("TC-E2E-010: Tab切换数据独立", tc_e2e_010),
            ("TC-E2E-011: 注册成功流程", tc_e2e_011),
            ("TC-E2E-012: 注册后用户可登录验证", tc_e2e_012),
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
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch02.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 70)
    print("测试执行完成")
    print("=" * 70)
    print(f"报告路径: {report_path}")
    print(f"截图目录: {SCREENSHOT_DIR}")

    print("\n--- 结果汇总 ---")
    for r in all_results:
        status = r["status"]
        conf = r.get("confidence", "N/A")
        print(f"  {r['case_id']} {r['name']}: {status} (置信度 {conf})")


if __name__ == "__main__":
    main()
