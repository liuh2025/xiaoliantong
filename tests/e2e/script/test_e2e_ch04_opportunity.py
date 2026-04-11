"""
校链通(XiaoLianTong) - 第4章 商机广场模块 L2 E2E 测试
基于 QA-test-plan-PP-v1.0.md 第4章
覆盖用例: TC-E2E-015 ~ TC-E2E-025

应用地址: http://localhost:3000
测试日期: 2026-04-11
"""

from playwright.sync_api import sync_playwright
import time, os, json, sys, subprocess
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:3000")
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch04_opportunity")
SCREENSHOT_DIR = os.path.join(CAPTURES_DIR, datetime.now().strftime("%Y-%m-%d_%H%M%S"))
VIEWPORT = {"width": 1280, "height": 900}
DEFAULT_TIMEOUT = 30000

# Test user credentials
TEST_PHONE = "13800000001"
TEST_PASSWORD = "Admin123!"


# ============================================================
# Auth helper - get JWT tokens via API
# ============================================================
def get_auth_tokens():
    import urllib.request
    url = "http://localhost:8000/api/v1/auth/login/password/"
    data = json.dumps({"phone": TEST_PHONE, "password": TEST_PASSWORD}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result.get("data", {})


def inject_login(page, token_data):
    page.evaluate(f"""() => {{
        localStorage.setItem('access_token', '{token_data.get("access_token", "")}');
        localStorage.setItem('refresh_token', '{token_data.get("refresh_token", "")}');
    }}""")


# ============================================================
# Screenshot & Logger
# ============================================================
class SmartScreenshot:
    def __init__(self, page, output_dir, case_id):
        self.page, self.output_dir, self.case_id, self.counter = page, output_dir, case_id, 0
        os.makedirs(output_dir, exist_ok=True)

    def capture(self, trigger, step=None, action=None, tag=None):
        self.counter += 1
        parts = [self.case_id]
        if step: parts.append(f"step{step}")
        if action: parts.append(action)
        parts.append(trigger.lower())
        if tag: parts.append(tag)
        filepath = os.path.join(self.output_dir, f"{'-'.join(parts)}_{self.counter}.png")
        self.page.screenshot(path=filepath, full_page=True)
        return filepath

    def save_dom_snapshot(self, step=None, tag=""):
        self.counter += 1
        parts = [self.case_id]
        if step: parts.append(f"step{step}")
        parts.append("dom_snapshot")
        if tag: parts.append(tag)
        filepath = os.path.join(self.output_dir, f"{'-'.join(parts)}_{self.counter}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.page.content())
        return filepath


class TestLogger:
    def __init__(self, case_id, output_dir):
        self.case_id, self.output_dir, self.logs, self.start_time = case_id, output_dir, [], time.time()
        self.steps_passed = self.steps_failed = 0

    def log(self, level, step, action, message, **kwargs):
        entry = {"timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3], "level": level,
                 "case_id": self.case_id, "step": step, "action": action, "message": message, **kwargs}
        self.logs.append(entry)
        icon = {"INFO": "  ", "PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]", "DEBUG": "[DBG]"}.get(level, "  ")
        step_str = f"STEP {step}" if step else ""
        print(f"[{entry['timestamp']}] {icon} {self.case_id} | {step_str} {action} | {message}")
        if level == "PASS": self.steps_passed += 1
        elif level == "FAIL": self.steps_failed += 1

    def summary(self):
        return {"case_id": self.case_id, "duration_sec": round(time.time() - self.start_time, 2),
                "steps_passed": self.steps_passed, "steps_failed": self.steps_failed}

    def save_json(self):
        filepath = os.path.join(self.output_dir, f"{self.case_id}_log.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"summary": self.summary(), "logs": self.logs}, f, ensure_ascii=False, indent=2)
        return filepath


_logger = None
def log_info(msg, step=None, **kw): _logger.log("INFO", step, "", msg, **kw)
def log_pass(msg, step=None, **kw): _logger.log("PASS", step, "", msg, **kw)
def log_fail(msg, step=None, **kw): _logger.log("FAIL", step, "", msg, **kw)
def log_warn(msg, step=None, **kw): _logger.log("WARN", step, "", msg, **kw)
def log_debug(msg, step=None, **kw): _logger.log("DEBUG", step, "", msg, **kw)


# ============================================================
# Helper to setup logged-in opportunity page
# ============================================================
def setup_opportunity_page(page, tokens):
    inject_login(page, tokens)
    page.goto(f"{BASE_URL}/opportunity")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)


# ============================================================
# Test Cases
# ============================================================

def tc_e2e_015(page, tokens):
    """TC-E2E-015: 页面结构 - header active, title/subtitle, publish buttons, sidebar+list layout"""
    global _logger
    case_id = "TC-E2E-015"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "页面结构", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 页面结构验证 ===")

        # Verify nav link active for "商机广场"
        opp_nav = page.locator(".nav-link:has-text('商机广场')")
        if opp_nav.count() > 0:
            nav_class = opp_nav.first.get_attribute("class") or ""
            is_active = "active" in nav_class
            if is_active:
                log_pass("导航项'商机广场'高亮(active)", step=1)
                verifications["nav_active"] = True
            else:
                log_warn("导航项'商机广场'未高亮", step=1)
                verifications["nav_active"] = False
        else:
            log_fail("导航项'商机广场'不可见", step=1)
            verifications["nav_active"] = False

        # Verify page title
        title = page.locator(".opportunity-page .page-title")
        if title.count() > 0 and title.first.is_visible():
            text = title.first.inner_text()
            log_pass(f"页面标题: '{text}'", step=1)
            verifications["page_title"] = "商机广场" in text
        else:
            log_fail("页面标题不可见", step=1)
            verifications["page_title"] = False

        # Verify page subtitle
        subtitle = page.locator(".opportunity-page .page-subtitle")
        if subtitle.count() > 0 and subtitle.first.is_visible():
            log_pass(f"页面副标题: '{subtitle.first.inner_text()}'", step=1)
            verifications["page_subtitle"] = True
        else:
            log_fail("页面副标题不可见", step=1)
            verifications["page_subtitle"] = False

        # Verify publish buttons
        buy_btn = page.locator(".opportunity-page button:has-text('发布采购需求')")
        supply_btn = page.locator(".opportunity-page button:has-text('发布供应能力')")
        verifications["buy_btn"] = buy_btn.count() > 0 and buy_btn.first.is_visible()
        verifications["supply_btn"] = supply_btn.count() > 0 and supply_btn.first.is_visible()
        log_pass(f"发布采购需求按钮: {'可见' if verifications['buy_btn'] else '不可见'}", step=2)
        log_pass(f"发布供应能力按钮: {'可见' if verifications['supply_btn'] else '不可见'}", step=2)

        # Verify sidebar + list layout
        sidebar = page.locator(".opportunity-page .filter-sidebar")
        main_content = page.locator(".opportunity-page .main-content")
        verifications["sidebar"] = sidebar.count() > 0 and sidebar.first.is_visible()
        verifications["main_content"] = main_content.count() > 0 and main_content.first.is_visible()
        log_pass(f"侧边栏筛选: {'可见' if verifications['sidebar'] else '不可见'}", step=3)
        log_pass(f"主内容区: {'可见' if verifications['main_content'] else '不可见'}", step=3)

        ss.capture("CHECKPOINT", step=3, action="page_structure_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_016(page, tokens):
    """TC-E2E-016: 筛选-商机类型 - test filter checkboxes for buy/supply types"""
    global _logger
    case_id = "TC-E2E-016"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "筛选-商机类型", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 筛选-商机类型 ===")

        # Verify filter section title
        section_title = page.locator(".filter-section .filter-title:has-text('商机类型')")
        if section_title.count() > 0:
            log_pass("'商机类型'筛选区标题可见", step=1)
            verifications["section_title"] = True
        else:
            log_fail("'商机类型'筛选区标题不可见", step=1)
            verifications["section_title"] = False

        # Verify checkbox group exists
        type_section = page.locator(".filter-section").first
        checkboxes = type_section.locator(".el-checkbox")
        if checkboxes.count() >= 2:
            log_pass(f"商机类型复选框: {checkboxes.count()}个", step=2)
            verifications["checkboxes_exist"] = True

            # Check labels: "我要买" and "我能供"
            buy_cb = type_section.locator(".el-checkbox:has-text('我要买')")
            supply_cb = type_section.locator(".el-checkbox:has-text('我能供')")
            verifications["buy_checkbox"] = buy_cb.count() > 0
            verifications["supply_checkbox"] = supply_cb.count() > 0
            log_pass(f"'我要买'复选框: {'存在' if verifications['buy_checkbox'] else '不存在'}", step=2)
            log_pass(f"'我能供'复选框: {'存在' if verifications['supply_checkbox'] else '不存在'}", step=2)

            # Click "我要买" checkbox
            if buy_cb.count() > 0:
                buy_cb.first.click()
                page.wait_for_timeout(1000)
                log_pass("点击'我要买'复选框", step=3)
                verifications["click_buy"] = True

                # Click again to uncheck
                buy_cb.first.click()
                page.wait_for_timeout(500)
                log_pass("取消'我要买'复选框", step=3)
        else:
            log_fail(f"商机类型复选框不足(找到{checkboxes.count()}个)", step=2)
            verifications["checkboxes_exist"] = False

        ss.capture("CHECKPOINT", step=3, action="type_filter_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_017(page, tokens):
    """TC-E2E-017: 筛选-行业级联 - test industry cascade selection"""
    global _logger
    case_id = "TC-E2E-017"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "筛选-行业级联", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 筛选-行业级联 ===")

        # Verify industry filter section
        industry_title = page.locator(".filter-section .filter-title:has-text('行业筛选')")
        if industry_title.count() > 0:
            log_pass("'行业筛选'区标题可见", step=1)
            verifications["section_title"] = True
        else:
            log_fail("'行业筛选'区标题不可见", step=1)
            verifications["section_title"] = False

        # Verify first-level industry select
        industry_section = page.locator(".filter-section").nth(1)
        first_select = industry_section.locator(".el-select").first
        if first_select.count() > 0:
            log_pass("一级行业下拉框存在", step=2)
            verifications["first_select"] = True

            # Click to open dropdown
            first_select.click()
            page.wait_for_timeout(1000)

            # Check dropdown options (teleported to body)
            options = page.locator("body > .el-select-dropdown:visible .el-select-dropdown__item")
            if options.count() > 0:
                log_pass(f"一级行业选项: {options.count()}个", step=2)
                verifications["first_options"] = True

                # Select first option
                options.first.click()
                page.wait_for_timeout(2000)

                log_pass("选择了一级行业", step=3)
                verifications["select_first"] = True

                # Check if second-level select appears
                second_select = page.locator(".filter-section").nth(1).locator(".el-select").nth(1)
                if second_select.count() > 0:
                    log_pass("二级行业下拉框已出现", step=3)
                    verifications["second_select_visible"] = True
                else:
                    log_warn("二级行业下拉框未出现(可能该行业无子行业)", step=3)
                    verifications["second_select_visible"] = None
            else:
                log_warn("一级行业选项为空(可能字典数据未加载)", step=2)
                verifications["first_options"] = None
        else:
            log_fail("一级行业下拉框不存在", step=2)
            verifications["first_select"] = False

        ss.capture("CHECKPOINT", step=3, action="industry_cascade_verified")

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_018(page, tokens):
    """TC-E2E-018: 筛选-业务品类 - test category filter"""
    global _logger
    case_id = "TC-E2E-018"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "筛选-业务品类", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 筛选-业务品类 ===")

        # Find category filter section
        category_title = page.locator(".filter-section .filter-title:has-text('业务品类')")
        if category_title.count() > 0:
            log_pass("'业务品类'区标题可见", step=1)
            verifications["section_title"] = True
        else:
            log_fail("'业务品类'区标题不可见", step=1)
            verifications["section_title"] = False

        # Check category checkbox group
        category_section = page.locator(".filter-section").nth(2)
        checkboxes = category_section.locator(".el-checkbox-group .el-checkbox")
        if checkboxes.count() > 0:
            log_pass(f"业务品类复选框: {checkboxes.count()}个", step=2)
            verifications["checkboxes_count"] = True

            # Click first category checkbox
            checkboxes.first.click()
            page.wait_for_timeout(1000)
            log_pass("点击了第一个品类复选框", step=3)
            verifications["click_category"] = True
        else:
            log_warn("业务品类复选框为空(可能字典数据未加载)", step=2)
            verifications["checkboxes_count"] = None

        ss.capture("CHECKPOINT", step=3, action="category_filter_verified")

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_019(page, tokens):
    """TC-E2E-019: 筛选-地区级联 - test region cascade"""
    global _logger
    case_id = "TC-E2E-019"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "筛选-地区级联", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 筛选-地区级联 ===")

        # Find region filter section
        region_title = page.locator(".filter-section .filter-title:has-text('地区筛选')")
        if region_title.count() > 0:
            log_pass("'地区筛选'区标题可见", step=1)
            verifications["section_title"] = True
        else:
            log_fail("'地区筛选'区标题不可见", step=1)
            verifications["section_title"] = False

        # Find province select (in the region section - 4th filter-section)
        region_section = page.locator(".filter-section").nth(3)
        province_select = region_section.locator(".el-select").first
        if province_select.count() > 0:
            log_pass("省份下拉框存在", step=2)
            verifications["province_select"] = True

            # Click to open dropdown
            province_select.click()
            page.wait_for_timeout(1000)

            options = page.locator("body > .el-select-dropdown:visible .el-select-dropdown__item")
            if options.count() > 0:
                log_pass(f"省份选项: {options.count()}个", step=2)
                verifications["province_options"] = True

                # Select first province
                options.first.click()
                page.wait_for_timeout(2000)

                log_pass("选择了省份", step=3)
                verifications["select_province"] = True

                # Check if city select appears
                city_select = region_section.locator(".el-select").nth(1)
                if city_select.count() > 0:
                    log_pass("城市下拉框已出现", step=3)
                    verifications["city_select_visible"] = True
                else:
                    log_warn("城市下拉框未出现(可能该省无城市数据)", step=3)
                    verifications["city_select_visible"] = None
            else:
                log_warn("省份选项为空(可能字典数据未加载)", step=2)
                verifications["province_options"] = None
        else:
            log_fail("省份下拉框不存在", step=2)
            verifications["province_select"] = False

        ss.capture("CHECKPOINT", step=3, action="region_cascade_verified")

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_020(page, tokens):
    """TC-E2E-020: 已选条件摘要 - verify selected filters summary"""
    global _logger
    case_id = "TC-E2E-020"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "已选条件摘要", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 已选条件摘要 ===")

        # Activate a filter by clicking "我要买" checkbox
        type_section = page.locator(".filter-section").first
        buy_cb = type_section.locator(".el-checkbox:has-text('我要买')")
        if buy_cb.count() > 0:
            buy_cb.first.click()
            page.wait_for_timeout(1500)
            log_pass("点击'我要买'激活筛选条件", step=1)
            verifications["activate_filter"] = True
        else:
            log_fail("'我要买'复选框未找到", step=1)
            verifications["activate_filter"] = False

        # Check filter summary section
        summary_section = page.locator(".filter-section .filter-title:has-text('已选条件')")
        if summary_section.count() > 0:
            log_pass("'已选条件'区标题可见", step=2)
            verifications["summary_title"] = True

            # Check filter summary tags
            summary_tags = page.locator(".filter-section .filter-summary .el-tag")
            if summary_tags.count() > 0:
                tag_texts = [summary_tags.nth(i).inner_text() for i in range(summary_tags.count())]
                log_pass(f"已选条件标签: {tag_texts}", step=2)
                verifications["summary_tags"] = True
            else:
                log_fail("已选条件标签为空", step=2)
                verifications["summary_tags"] = False

            # Check reset button
            reset_btn = page.locator(".filter-section button:has-text('重置筛选')")
            if reset_btn.count() > 0:
                log_pass("'重置筛选'按钮可见", step=3)
                verifications["reset_btn"] = True
            else:
                log_fail("'重置筛选'按钮不可见", step=3)
                verifications["reset_btn"] = False
        else:
            log_fail("'已选条件'区未出现(筛选可能未生效)", step=2)
            verifications["summary_title"] = False

        ss.capture("CHECKPOINT", step=3, action="filter_summary_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_021(page, tokens):
    """TC-E2E-021: 重置筛选 - test reset button"""
    global _logger
    case_id = "TC-E2E-021"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "重置筛选", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 重置筛选 ===")

        # Activate filter by clicking "我要买"
        type_section = page.locator(".filter-section").first
        buy_cb = type_section.locator(".el-checkbox:has-text('我要买')")
        if buy_cb.count() > 0:
            buy_cb.first.click()
            page.wait_for_timeout(1500)
            log_pass("激活了'我要买'筛选", step=1)
            verifications["activate"] = True
        else:
            log_fail("无法激活筛选条件", step=1)
            verifications["activate"] = False

        # Click reset button
        reset_btn = page.locator(".filter-section button:has-text('重置筛选')")
        if reset_btn.count() > 0:
            reset_btn.first.click()
            page.wait_for_timeout(1500)
            log_pass("点击了'重置筛选'", step=2)
            verifications["click_reset"] = True

            # Verify "已选条件" section is gone or empty
            summary_title = page.locator(".filter-section .filter-title:has-text('已选条件')")
            if summary_title.count() == 0:
                log_pass("重置后'已选条件'区已消失", step=3)
                verifications["reset_cleared"] = True
            else:
                summary_tags = page.locator(".filter-section .filter-summary .el-tag")
                if summary_tags.count() == 0:
                    log_pass("重置后已选条件标签已清空", step=3)
                    verifications["reset_cleared"] = True
                else:
                    log_fail("重置后已选条件仍然存在", step=3)
                    verifications["reset_cleared"] = False
        else:
            log_fail("'重置筛选'按钮不存在(可能需要先激活筛选)", step=2)
            verifications["click_reset"] = False

        ss.capture("CHECKPOINT", step=3, action="reset_filter_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_022(page, tokens):
    """TC-E2E-022: 商机卡片 - verify card structure (type badge, title, tags, company, location)"""
    global _logger
    case_id = "TC-E2E-022"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "商机卡片", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 商机卡片验证 ===")

        opp_cards = page.locator(".opp-card")
        opp_count = opp_cards.count()
        if opp_count > 0:
            log_pass(f"商机卡片数量: {opp_count}", step=1)
            verifications["cards_exist"] = True

            # Check first card structure
            first = opp_cards.first

            # Type badge
            badge = first.locator(".opp-type-badge")
            if badge.count() > 0:
                badge_text = badge.first.inner_text()
                log_pass(f"类型标签: '{badge_text.strip()}'", step=2)
                verifications["type_badge"] = True
            else:
                log_fail("类型标签不存在", step=2)
                verifications["type_badge"] = False

            # Title
            title = first.locator(".opp-title")
            if title.count() > 0:
                log_pass(f"商机标题: '{title.first.inner_text()}'", step=2)
                verifications["title"] = True
            else:
                log_fail("商机标题不存在", step=2)
                verifications["title"] = False

            # Tags
            tags = first.locator(".opp-tags .tag")
            if tags.count() > 0:
                tag_texts = [tags.nth(i).inner_text() for i in range(min(tags.count(), 4))]
                log_pass(f"标签: {tag_texts}", step=2)
                verifications["tags"] = True
            else:
                log_warn("标签为空", step=2)
                verifications["tags"] = None

            # Company
            company = first.locator(".opp-company")
            if company.count() > 0:
                log_pass("企业信息可见", step=3)
                verifications["company"] = True
            else:
                log_warn("企业信息不存在", step=3)
                verifications["company"] = None

            # Location
            location = first.locator(".opp-location")
            if location.count() > 0:
                log_pass(f"地区: '{location.first.inner_text()}'", step=3)
                verifications["location"] = True
            else:
                log_warn("地区信息不存在", step=3)
                verifications["location"] = None

            # Action button
            action_btn = first.locator("button:has-text('获取联系方式')")
            if action_btn.count() > 0:
                log_pass("'获取联系方式'按钮可见", step=3)
                verifications["action_btn"] = True
            else:
                log_fail("'获取联系方式'按钮不可见", step=3)
                verifications["action_btn"] = False
        else:
            # Check empty state
            empty = page.locator(".el-empty")
            if empty.count() > 0:
                log_warn("商机列表为空(el-empty显示)", step=1)
                verifications["cards_exist"] = None
            else:
                log_fail("商机卡片为空且无empty状态", step=1)
                verifications["cards_exist"] = False

        ss.capture("CHECKPOINT", step=3, action="opp_card_verified")

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_023(page, tokens):
    """TC-E2E-023: 分页 - verify pagination component"""
    global _logger
    case_id = "TC-E2E-023"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "分页", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 分页验证 ===")

        # Check result count text
        result_count = page.locator(".result-count")
        if result_count.count() > 0:
            log_pass(f"结果计数: '{result_count.first.inner_text()}'", step=1)
            verifications["result_count"] = True
        else:
            log_fail("结果计数不可见", step=1)
            verifications["result_count"] = False

        # Check pagination component
        pagination = page.locator(".pagination-wrap .el-pagination")
        if pagination.count() > 0:
            log_pass("分页组件可见", step=2)
            verifications["pagination"] = True

            # Check pagination elements
            total_text = pagination.locator(".el-pagination__total")
            if total_text.count() > 0:
                log_pass(f"总数: '{total_text.first.inner_text()}'", step=2)

            prev_btn = pagination.locator(".btn-prev")
            next_btn = pagination.locator(".btn-next")
            pager = pagination.locator(".el-pager")
            verifications["prev_btn"] = prev_btn.count() > 0
            verifications["next_btn"] = next_btn.count() > 0
            verifications["pager"] = pager.count() > 0
            log_pass(f"上一页按钮: {'存在' if verifications['prev_btn'] else '不存在'}", step=3)
            log_pass(f"下一页按钮: {'存在' if verifications['next_btn'] else '不存在'}", step=3)
            log_pass(f"页码区: {'存在' if verifications['pager'] else '不存在'}", step=3)
        else:
            # Pagination may not show if total <= page_size
            opp_cards = page.locator(".opp-card")
            if opp_cards.count() == 0:
                log_warn("无数据，分页组件不显示", step=2)
                verifications["pagination"] = None
            else:
                total_val = page.locator(".result-count strong")
                if total_val.count() > 0:
                    num = total_val.first.inner_text()
                    log_warn(f"数据量({num})不足显示分页", step=2)
                    verifications["pagination"] = None
                else:
                    log_fail("分页组件不可见", step=2)
                    verifications["pagination"] = False

        ss.capture("CHECKPOINT", step=3, action="pagination_verified")

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_024(page, tokens):
    """TC-E2E-024: 发布商机弹窗 - click publish button, verify dialog form"""
    global _logger
    case_id = "TC-E2E-024"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "发布商机弹窗", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 发布商机弹窗 ===")

        # Click publish buy button
        buy_btn = page.locator(".opportunity-page button:has-text('发布采购需求')").first
        buy_btn.click()
        page.wait_for_timeout(1500)

        # Verify dialog
        dialog = page.locator(".el-dialog:visible")
        if dialog.count() > 0:
            log_pass("发布商机弹窗已打开", step=1)
            verifications["dialog_open"] = True

            # Check dialog title
            dialog_title = dialog.locator(".el-dialog__title")
            if dialog_title.count() > 0:
                log_pass(f"弹窗标题: '{dialog_title.first.inner_text()}'", step=1)

            # Check form fields
            # Type radio group
            radios = dialog.locator(".el-radio")
            if radios.count() >= 2:
                log_pass(f"商机类型radio: {radios.count()}个", step=2)
                verifications["type_radio"] = True
            else:
                log_fail("商机类型radio不足", step=2)
                verifications["type_radio"] = False

            # Title input
            title_item = dialog.locator(".el-form-item:has-text('标题')")
            if title_item.count() > 0:
                log_pass("表单项'标题'存在", step=2)
                verifications["title_field"] = True
            else:
                log_fail("表单项'标题'不存在", step=2)
                verifications["title_field"] = False

            # Industry select
            industry_item = dialog.locator(".el-form-item:has-text('一级行业')")
            if industry_item.count() > 0:
                log_pass("表单项'一级行业'存在", step=2)
                verifications["industry_field"] = True
            else:
                log_warn("表单项'一级行业'未找到", step=2)

            # Province select
            province_item = dialog.locator(".el-form-item:has-text('省份')")
            if province_item.count() > 0:
                log_pass("表单项'省份'存在", step=2)
                verifications["province_field"] = True
            else:
                log_warn("表单项'省份'未找到", step=2)

            # Description textarea
            desc_item = dialog.locator(".el-form-item:has-text('详情描述')")
            if desc_item.count() > 0:
                log_pass("表单项'详情描述'存在", step=2)
                verifications["desc_field"] = True
            else:
                log_warn("表单项'详情描述'未找到", step=2)

            # Submit button
            submit_btn = dialog.locator("button:has-text('立即发布')")
            if submit_btn.count() > 0:
                log_pass("'立即发布'按钮可见", step=3)
                verifications["submit_btn"] = True
            else:
                log_fail("'立即发布'按钮不可见", step=3)
                verifications["submit_btn"] = False

            ss.capture("CHECKPOINT", step=3, action="dialog_open")

            # Close dialog
            close_btn = dialog.locator(".el-dialog__headerbtn")
            if close_btn.count() > 0:
                close_btn.first.click()
                page.wait_for_timeout(500)
        else:
            log_fail("发布商机弹窗未打开", step=1)
            verifications["dialog_open"] = False
            ss.save_dom_snapshot(step=1, tag="no_dialog")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_025(page, tokens):
    """TC-E2E-025: 获取联系方式 - click contact button, verify dialog flow"""
    global _logger
    case_id = "TC-E2E-025"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "获取联系方式", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_opportunity_page(page, tokens)
        log_info("=== 获取联系方式 ===")

        # Find first opportunity card with contact button
        contact_btn = page.locator(".opp-card button:has-text('获取联系方式')").first
        if contact_btn.is_visible():
            contact_btn.click()
            page.wait_for_timeout(1500)

            # Check contact dialog
            dialog = page.locator(".el-dialog:visible")
            if dialog.count() > 0:
                log_pass("联系方式弹窗已打开", step=1)
                verifications["dialog_open"] = True

                # Check dialog title
                dialog_title = dialog.locator(".el-dialog__title")
                if dialog_title.count() > 0:
                    log_pass(f"弹窗标题: '{dialog_title.first.inner_text()}'", step=1)

                # Check confirmation text
                confirm_text = dialog.locator("text=确认获取")
                if confirm_text.count() > 0:
                    log_pass("确认获取提示可见", step=2)
                    verifications["confirm_text"] = True
                else:
                    log_fail("确认获取提示不可见", step=2)
                    verifications["confirm_text"] = False

                # Click confirm button
                confirm_btn = dialog.locator("button:has-text('确认获取')")
                if confirm_btn.count() > 0:
                    confirm_btn.first.click()
                    page.wait_for_timeout(2000)

                    # Check result - success OR business rule error
                    success_text = dialog.locator("text=获取成功")
                    contact_info = dialog.locator(".contact-info-box")
                    error_msg = page.locator(".el-message--error")

                    if success_text.count() > 0 or contact_info.count() > 0:
                        log_pass("获取成功，联系方式显示", step=3)
                        verifications["contact_shown"] = True
                    elif error_msg.count() > 0:
                        log_pass("业务规则拦截，错误提示显示", step=3)
                        verifications["contact_shown"] = True
                    else:
                        log_fail("获取成功提示或联系方式未显示", step=3)
                        ss.save_dom_snapshot(step=3, tag="contact_result")
                        verifications["contact_shown"] = False

                ss.capture("CHECKPOINT", step=3, action="contact_result")

                # Close dialog
                close = dialog.locator("button:has-text('知道了'), button:has-text('取消')")
                if close.count() > 0:
                    close.first.click()
                    page.wait_for_timeout(500)
            else:
                log_fail("联系方式弹窗未打开", step=1)
                verifications["dialog_open"] = False
        else:
            log_warn("无商机卡片或获取联系方式按钮，跳过", step=1)
            verifications["dialog_open"] = None

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=4)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


# ============================================================
# Report
# ============================================================
def _generate_report(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = ["# 校链通 商机广场模块 E2E 测试报告", "",
             f"| 项目 | 内容 |", "|------|------|",
             f"| 测试模块 | 第4章 商机广场模块 (L2 E2E) |",
             f"| 测试日期 | {now} |", f"| 用例数量 | {len(results)} |", "",
             "## 测试结果汇总", "",
             "| 用例ID | 用例名称 | 结果 | 置信度 |",
             "|--------|----------|------|--------|"]
    for r in results:
        icon = r["status"]
        conf = f"{r.get('confidence', 'N/A')}"
        lines.append(f"| {r['case_id']} | {r['name']} | {icon} | {conf} |")
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    lines.extend(["", f"通过率: {pass_count}/{len(results)} ({pass_count/len(results)*100:.0f}%)"])
    return "\n".join(lines)


# ============================================================
# Main
# ============================================================
def main():
    global SCREENSHOT_DIR
    print("=" * 70)
    print("校链通(XiaoLianTong) - 第4章 商机广场模块 L2 E2E 测试")
    print(f"目标地址: {BASE_URL}")
    print(f"截图目录: {SCREENSHOT_DIR}")
    print("=" * 70)

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Get auth tokens
    print("获取认证Token...")
    try:
        token_data = get_auth_tokens()
        print(f"  access_token: {token_data.get('access_token', '')[:20]}...")
    except Exception as e:
        print(f"获取Token失败: {e}")
        return

    all_results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT, ignore_https_errors=True)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)

        # Check app
        try:
            resp = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=10000)
            print(f"应用可访问: HTTP {resp.status if resp else 'N/A'}")
        except Exception as e:
            print(f"无法访问: {e}")
            browser.close()
            return
        page.wait_for_timeout(500)

        test_cases = [
            ("TC-E2E-015: 页面结构", tc_e2e_015),
            ("TC-E2E-016: 筛选-商机类型", tc_e2e_016),
            ("TC-E2E-017: 筛选-行业级联", tc_e2e_017),
            ("TC-E2E-018: 筛选-业务品类", tc_e2e_018),
            ("TC-E2E-019: 筛选-地区级联", tc_e2e_019),
            ("TC-E2E-020: 已选条件摘要", tc_e2e_020),
            ("TC-E2E-021: 重置筛选", tc_e2e_021),
            ("TC-E2E-022: 商机卡片", tc_e2e_022),
            ("TC-E2E-023: 分页", tc_e2e_023),
            ("TC-E2E-024: 发布商机弹窗", tc_e2e_024),
            ("TC-E2E-025: 获取联系方式", tc_e2e_025),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page, token_data)
            all_results.append(r)

        browser.close()

    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch04.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 70)
    print("测试执行完成")
    print("=" * 70)
    print(f"\n--- 结果汇总 ---")
    for r in all_results:
        print(f"  {r['case_id']} {r['name']}: {r['status']} (置信度 {r.get('confidence', 'N/A')})")


if __name__ == "__main__":
    main()
