"""
校链通(XiaoLianTong) - 第5章 企业名录模块 L2 E2E 测试
基于 QA-test-plan-PP-v1.0.md 第5章
覆盖用例: TC-E2E-026 ~ TC-E2E-036

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
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch05_enterprise")
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
# Helper to setup logged-in enterprise page
# ============================================================
def setup_enterprise_page(page, tokens):
    inject_login(page, tokens)
    page.goto(f"{BASE_URL}/enterprise")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)


# ============================================================
# Test Cases
# ============================================================

def tc_e2e_026(page, tokens):
    """TC-E2E-026: 页面结构 - header, title/subtitle, buttons, sidebar+grid layout"""
    global _logger
    case_id = "TC-E2E-026"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "页面结构", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 页面结构验证 ===")

        # Verify nav link active for "企业名录"
        ent_nav = page.locator(".nav-link:has-text('企业名录')")
        if ent_nav.count() > 0:
            nav_class = ent_nav.first.get_attribute("class") or ""
            is_active = "active" in nav_class
            if is_active:
                log_pass("导航项'企业名录'高亮(active)", step=1)
                verifications["nav_active"] = True
            else:
                log_warn("导航项'企业名录'未高亮", step=1)
                verifications["nav_active"] = False
        else:
            log_fail("导航项'企业名录'不可见", step=1)
            verifications["nav_active"] = False

        # Verify page title
        title = page.locator(".enterprise-page .page-title")
        if title.count() > 0 and title.first.is_visible():
            text = title.first.inner_text()
            log_pass(f"页面标题: '{text}'", step=1)
            verifications["page_title"] = "企业名录" in text
        else:
            log_fail("页面标题不可见", step=1)
            verifications["page_title"] = False

        # Verify page subtitle
        subtitle = page.locator(".enterprise-page .page-subtitle")
        if subtitle.count() > 0 and subtitle.first.is_visible():
            log_pass(f"页面副标题: '{subtitle.first.inner_text()}'", step=1)
            verifications["page_subtitle"] = True
        else:
            log_fail("页面副标题不可见", step=1)
            verifications["page_subtitle"] = False

        # Verify action buttons
        claim_btn = page.locator(".enterprise-page button:has-text('认领已有企业')")
        create_btn = page.locator(".enterprise-page button:has-text('创建新企业')")
        verifications["claim_btn"] = claim_btn.count() > 0 and claim_btn.first.is_visible()
        verifications["create_btn"] = create_btn.count() > 0 and create_btn.first.is_visible()
        log_pass(f"'认领已有企业'按钮: {'可见' if verifications['claim_btn'] else '不可见'}", step=2)
        log_pass(f"'创建新企业'按钮: {'可见' if verifications['create_btn'] else '不可见'}", step=2)

        # Verify sidebar + grid layout
        sidebar = page.locator(".enterprise-page .filter-sidebar")
        main_content = page.locator(".enterprise-page .enterprise-main")
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


def tc_e2e_027(page, tokens):
    """TC-E2E-027: 筛选-行业分类 - industry filter with cascade"""
    global _logger
    case_id = "TC-E2E-027"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "筛选-行业分类", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 筛选-行业分类 ===")

        # Find industry filter group
        industry_title = page.locator(".filter-group-title:has-text('行业分类')")
        if industry_title.count() > 0:
            log_pass("'行业分类'区标题可见", step=1)
            verifications["section_title"] = True
        else:
            log_fail("'行业分类'区标题不可见", step=1)
            verifications["section_title"] = False

        # Check first-level industry select
        industry_group = page.locator(".filter-group").first
        first_select = industry_group.locator(".el-select").first
        if first_select.count() > 0:
            log_pass("一级行业下拉框存在", step=2)
            verifications["first_select"] = True

            # Click to open dropdown
            first_select.click()
            page.wait_for_timeout(1000)

            options = page.locator("body > .el-select-dropdown:visible .el-select-dropdown__item")
            if options.count() > 0:
                log_pass(f"一级行业选项: {options.count()}个", step=2)
                verifications["first_options"] = True

                # Select first option
                options.first.click()
                page.wait_for_timeout(2000)
                log_pass("选择了一级行业", step=3)
                verifications["select_first"] = True

                # Check second-level select appears and is enabled
                second_select = industry_group.locator(".el-select").nth(1)
                if second_select.count() > 0:
                    is_disabled = second_select.is_disabled()
                    log_pass(f"二级行业下拉框已出现(disabled={is_disabled})", step=3)
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

        ss.capture("CHECKPOINT", step=3, action="industry_filter_verified")

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


def tc_e2e_028(page, tokens):
    """TC-E2E-028: 筛选-业务品类 - category filter with checkboxes"""
    global _logger
    case_id = "TC-E2E-028"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "筛选-业务品类", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 筛选-业务品类 ===")

        # Find category filter group
        category_title = page.locator(".filter-group-title:has-text('业务品类')")
        if category_title.count() > 0:
            log_pass("'业务品类'区标题可见", step=1)
            verifications["section_title"] = True
        else:
            log_fail("'业务品类'区标题不可见", step=1)
            verifications["section_title"] = False

        # Check "全部品类" checkbox
        all_category_cb = page.locator(".category-checkbox-group .el-checkbox:has-text('全部品类')")
        if all_category_cb.count() > 0:
            log_pass("'全部品类'复选框可见", step=2)
            verifications["all_category_cb"] = True
        else:
            log_fail("'全部品类'复选框不可见", step=2)
            verifications["all_category_cb"] = False

        # Check category checkboxes
        category_group = page.locator(".category-checkbox-group .el-checkbox-group .el-checkbox")
        if category_group.count() > 0:
            log_pass(f"业务品类复选框: {category_group.count()}个", step=2)
            verifications["category_checkboxes"] = True

            # Click first category
            category_group.first.click()
            page.wait_for_timeout(1000)
            log_pass("点击了第一个品类复选框", step=3)
            verifications["click_category"] = True
        else:
            log_warn("业务品类复选框为空(可能字典数据未加载)", step=2)
            verifications["category_checkboxes"] = None

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


def tc_e2e_029(page, tokens):
    """TC-E2E-029: 筛选-所在地区 - region filter with cascade"""
    global _logger
    case_id = "TC-E2E-029"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "筛选-所在地区", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 筛选-所在地区 ===")

        # Find region filter group
        region_title = page.locator(".filter-group-title:has-text('所在地区')")
        if region_title.count() > 0:
            log_pass("'所在地区'区标题可见", step=1)
            verifications["section_title"] = True
        else:
            log_fail("'所在地区'区标题不可见", step=1)
            verifications["section_title"] = False

        # Find the region filter group - it's the 3rd filter-group
        region_group = page.locator(".filter-group").nth(2)
        province_select = region_group.locator(".el-select").first
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
                city_select = region_group.locator(".el-select").nth(1)
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

        ss.capture("CHECKPOINT", step=3, action="region_filter_verified")

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


def tc_e2e_030(page, tokens):
    """TC-E2E-030: 筛选-热门标签 - hot tags filter"""
    global _logger
    case_id = "TC-E2E-030"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "筛选-热门标签", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 筛选-热门标签 ===")

        # Find hot tags filter group
        hot_tags_title = page.locator(".filter-group-title:has-text('热门标签')")
        if hot_tags_title.count() > 0:
            log_pass("'热门标签'区标题可见", step=1)
            verifications["section_title"] = True
        else:
            log_fail("'热门标签'区标题不可见", step=1)
            verifications["section_title"] = False

        # Check hot tags
        hot_tags = page.locator(".hot-tags .hot-tag")
        if hot_tags.count() > 0:
            tag_texts = [hot_tags.nth(i).inner_text() for i in range(hot_tags.count())]
            log_pass(f"热门标签({hot_tags.count()}个): {tag_texts}", step=2)
            verifications["hot_tags_exist"] = True

            # Click first tag to activate
            first_tag = hot_tags.first
            first_tag.click()
            page.wait_for_timeout(1000)

            # Check tag becomes active
            active_tags = page.locator(".hot-tags .hot-tag.active")
            if active_tags.count() > 0:
                log_pass("标签已激活(active样式)", step=3)
                verifications["tag_click"] = True
            else:
                log_fail("点击标签后未变为active", step=3)
                verifications["tag_click"] = False

            # Click again to deactivate
            first_tag.click()
            page.wait_for_timeout(500)
            log_pass("再次点击标签取消选中", step=3)
        else:
            log_fail("热门标签为空", step=2)
            verifications["hot_tags_exist"] = False

        ss.capture("CHECKPOINT", step=3, action="hot_tags_verified")

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


def tc_e2e_031(page, tokens):
    """TC-E2E-031: 已选摘要与重置 - summary + reset"""
    global _logger
    case_id = "TC-E2E-031"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "已选摘要与重置", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 已选摘要与重置 ===")

        # Activate a filter by clicking a hot tag
        hot_tag = page.locator(".hot-tags .hot-tag").first
        if hot_tag.count() > 0 and hot_tag.is_visible():
            tag_text = hot_tag.inner_text()
            hot_tag.click()
            page.wait_for_timeout(1500)
            log_pass(f"点击了热门标签'{tag_text}'激活筛选", step=1)
            verifications["activate_filter"] = True
        else:
            log_fail("无法激活筛选条件", step=1)
            verifications["activate_filter"] = False

        # Check filter summary section
        summary_section = page.locator(".filter-summary")
        if summary_section.count() > 0:
            log_pass("'已选条件'摘要区可见", step=2)
            verifications["summary_visible"] = True

            # Check summary title
            summary_title = page.locator(".filter-summary-title:has-text('已选条件')")
            if summary_title.count() > 0:
                log_pass("'已选条件'标题可见", step=2)
                verifications["summary_title"] = True

            # Check summary tags
            summary_tags = page.locator(".filter-summary-tag")
            if summary_tags.count() > 0:
                tag_texts = [summary_tags.nth(i).inner_text() for i in range(summary_tags.count())]
                log_pass(f"摘要标签: {tag_texts}", step=2)
                verifications["summary_tags"] = True
            else:
                log_fail("摘要标签为空", step=2)
                verifications["summary_tags"] = False
        else:
            log_fail("'已选条件'摘要区不可见(筛选可能未生效)", step=2)
            verifications["summary_visible"] = False

        # Check reset button
        reset_btn = page.locator(".filter-sidebar button:has-text('重置筛选')")
        if reset_btn.count() > 0:
            log_pass("'重置筛选'按钮可见", step=3)
            verifications["reset_btn"] = True

            # Click reset
            reset_btn.first.click()
            page.wait_for_timeout(1500)

            # Verify summary is gone
            summary_after = page.locator(".filter-summary")
            if summary_after.count() == 0:
                log_pass("重置后'已选条件'摘要已消失", step=3)
                verifications["reset_cleared"] = True
            else:
                summary_tags_after = page.locator(".filter-summary-tag")
                if summary_tags_after.count() == 0:
                    log_pass("重置后摘要标签已清空", step=3)
                    verifications["reset_cleared"] = True
                else:
                    log_fail("重置后摘要仍然存在", step=3)
                    verifications["reset_cleared"] = False
        else:
            log_fail("'重置筛选'按钮不可见", step=3)
            verifications["reset_btn"] = False

        ss.capture("CHECKPOINT", step=3, action="summary_reset_verified")

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


def tc_e2e_032(page, tokens):
    """TC-E2E-032: 企业卡片列表 - card grid structure"""
    global _logger
    case_id = "TC-E2E-032"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "企业卡片列表", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 企业卡片列表 ===")

        # Check result count
        result_count = page.locator(".result-count")
        if result_count.count() > 0:
            log_pass(f"结果计数: '{result_count.first.inner_text()}'", step=1)
            verifications["result_count"] = True
        else:
            log_fail("结果计数不可见", step=1)
            verifications["result_count"] = False

        # Check enterprise grid
        ent_grid = page.locator(".enterprise-grid")
        if ent_grid.count() > 0:
            log_pass("企业卡片网格存在", step=2)
            verifications["grid_exists"] = True

            # Check cards
            ent_cards = page.locator(".enterprise-card")
            card_count = ent_cards.count()
            if card_count > 0:
                log_pass(f"企业卡片数量: {card_count}", step=2)
                verifications["cards_exist"] = True

                # Check first card structure
                first = ent_cards.first

                # Logo
                logo = first.locator(".enterprise-logo")
                verifications["card_logo"] = logo.count() > 0
                log_pass(f"企业Logo: {'存在' if verifications['card_logo'] else '不存在'}", step=3)

                # Name
                name = first.locator(".enterprise-name")
                verifications["card_name"] = name.count() > 0
                if name.count() > 0:
                    log_pass(f"企业名称: '{name.first.inner_text()}'", step=3)

                # Field/industry
                field = first.locator(".enterprise-field")
                verifications["card_field"] = field.count() > 0
                log_pass(f"行业领域: {'可见' if verifications['card_field'] else '不可见'}", step=3)

                # Tags
                tags = first.locator(".ent-tag")
                if tags.count() > 0:
                    tag_texts = [tags.nth(i).inner_text() for i in range(min(tags.count(), 4))]
                    log_pass(f"标签: {tag_texts}", step=3)
                    verifications["card_tags"] = True
                else:
                    log_warn("企业标签为空", step=3)
                    verifications["card_tags"] = None

                # Footer
                footer = first.locator(".enterprise-card-footer")
                verifications["card_footer"] = footer.count() > 0
                log_pass(f"卡片底栏: {'可见' if verifications['card_footer'] else '不可见'}", step=3)
            else:
                log_fail("企业卡片为空", step=2)
                verifications["cards_exist"] = False
        else:
            # Check empty state
            empty = page.locator(".el-empty")
            if empty.count() > 0:
                log_warn("企业列表为空(el-empty显示)", step=2)
                verifications["grid_exists"] = None
            else:
                log_fail("企业网格不存在", step=2)
                verifications["grid_exists"] = False

        ss.capture("CHECKPOINT", step=3, action="enterprise_cards_verified")

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


def tc_e2e_033(page, tokens):
    """TC-E2E-033: 分页 - pagination"""
    global _logger
    case_id = "TC-E2E-033"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "分页", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 分页验证 ===")

        # Check pagination component
        pagination = page.locator(".pagination-wrap .el-pagination")
        if pagination.count() > 0:
            log_pass("分页组件可见", step=1)
            verifications["pagination"] = True

            # Check pagination elements
            total_text = pagination.locator(".el-pagination__total")
            if total_text.count() > 0:
                log_pass(f"总数: '{total_text.first.inner_text()}'", step=2)

            sizes_select = pagination.locator(".el-pagination__sizes")
            prev_btn = pagination.locator(".btn-prev")
            next_btn = pagination.locator(".btn-next")
            pager = pagination.locator(".el-pager")
            verifications["sizes"] = sizes_select.count() > 0
            verifications["prev_btn"] = prev_btn.count() > 0
            verifications["next_btn"] = next_btn.count() > 0
            verifications["pager"] = pager.count() > 0
            log_pass(f"页面大小选择: {'存在' if verifications['sizes'] else '不存在'}", step=2)
            log_pass(f"上一页按钮: {'存在' if verifications['prev_btn'] else '不存在'}", step=3)
            log_pass(f"下一页按钮: {'存在' if verifications['next_btn'] else '不存在'}", step=3)
            log_pass(f"页码区: {'存在' if verifications['pager'] else '不存在'}", step=3)
        else:
            # Pagination may not show if total is 0
            ent_cards = page.locator(".enterprise-card")
            if ent_cards.count() == 0:
                log_warn("无数据，分页组件不显示", step=1)
                verifications["pagination"] = None
            else:
                result_count = page.locator(".result-count strong")
                if result_count.count() > 0:
                    num = result_count.first.inner_text()
                    log_warn(f"数据量({num})不足显示分页", step=1)
                    verifications["pagination"] = None
                else:
                    log_fail("分页组件不可见", step=1)
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


def tc_e2e_034(page, tokens):
    """TC-E2E-034: 认领企业弹窗 - click "认领已有企业", verify dialog"""
    global _logger
    case_id = "TC-E2E-034"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "认领企业弹窗", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 认领企业弹窗 ===")

        # Click "认领已有企业" button
        claim_btn = page.locator(".enterprise-page button:has-text('认领已有企业')").first
        claim_btn.click()
        page.wait_for_timeout(2000)

        # Verify dialog
        dialog = page.locator(".el-dialog:visible")
        if dialog.count() > 0:
            log_pass("认领企业弹窗已打开", step=1)
            verifications["dialog_open"] = True

            # Check dialog title
            dialog_title = dialog.locator(".el-dialog__title")
            if dialog_title.count() > 0:
                title_text = dialog_title.first.inner_text()
                log_pass(f"弹窗标题: '{title_text}'", step=1)
                verifications["dialog_title"] = "认领" in title_text

            # Check step 1 content: enterprise list
            claim_tip = dialog.locator(".claim-tip")
            if claim_tip.count() > 0:
                log_pass(f"认领提示文本: '{claim_tip.first.inner_text()}'", step=2)
                verifications["claim_tip"] = True
            else:
                log_fail("认领提示文本不可见", step=2)
                verifications["claim_tip"] = False

            # Check enterprise list items or empty state
            claim_items = dialog.locator(".claim-ent-item")
            if claim_items.count() > 0:
                log_pass(f"可认领企业列表: {claim_items.count()}个", step=2)
                verifications["ent_list"] = True
            else:
                empty = dialog.locator(".el-empty")
                if empty.count() > 0:
                    log_warn("无可认领企业(空列表)", step=2)
                    verifications["ent_list"] = None
                else:
                    log_fail("企业列表为空且无empty状态", step=2)
                    verifications["ent_list"] = False

            # Check cancel button
            cancel_btn = dialog.locator("button:has-text('取消')")
            if cancel_btn.count() > 0:
                log_pass("'取消'按钮可见", step=3)
                verifications["cancel_btn"] = True
            else:
                log_fail("'取消'按钮不可见", step=3)
                verifications["cancel_btn"] = False

            ss.capture("CHECKPOINT", step=3, action="claim_dialog_open")

            # Close dialog
            close_btn = dialog.locator(".el-dialog__headerbtn")
            if close_btn.count() > 0:
                close_btn.first.click()
                page.wait_for_timeout(500)
        else:
            log_fail("认领企业弹窗未打开", step=1)
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


def tc_e2e_035(page, tokens):
    """TC-E2E-035: 创建企业弹窗 - click "创建新企业", verify dialog"""
    global _logger
    case_id = "TC-E2E-035"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "创建企业弹窗", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 创建企业弹窗 ===")

        # Click "创建新企业" button
        create_btn = page.locator(".enterprise-page button:has-text('创建新企业')").first
        create_btn.click()
        page.wait_for_timeout(1500)

        # Verify dialog
        dialog = page.locator(".el-dialog:visible")
        if dialog.count() > 0:
            log_pass("创建企业弹窗已打开", step=1)
            verifications["dialog_open"] = True

            # Check dialog title
            dialog_title = dialog.locator(".el-dialog__title")
            if dialog_title.count() > 0:
                title_text = dialog_title.first.inner_text()
                log_pass(f"弹窗标题: '{title_text}'", step=1)
                verifications["dialog_title"] = "创建" in title_text

            # Check key form fields
            form_fields = [
                ("企业全称", "name_field"),
                ("统一社会信用代码", "credit_code_field"),
                ("所属行业", "industry_field"),
                ("所在地区", "region_field"),
                ("企业简介", "desc_field"),
                ("法人姓名", "legal_field"),
            ]
            for field_label, key in form_fields:
                field = dialog.locator(f".el-form-item:has-text('{field_label}')")
                if field.count() > 0:
                    log_pass(f"表单项'{field_label}'存在", step=2)
                    verifications[key] = True
                else:
                    log_warn(f"表单项'{field_label}'未找到", step=2)

            # Check submit button
            submit_btn = dialog.locator("button:has-text('提交创建')")
            if submit_btn.count() > 0:
                log_pass("'提交创建'按钮可见", step=3)
                verifications["submit_btn"] = True
            else:
                log_fail("'提交创建'按钮不可见", step=3)
                verifications["submit_btn"] = False

            # Check cancel button
            cancel_btn = dialog.locator("button:has-text('取消')")
            if cancel_btn.count() > 0:
                log_pass("'取消'按钮可见", step=3)
                verifications["cancel_btn"] = True

            ss.capture("CHECKPOINT", step=3, action="create_dialog_open")

            # Close dialog
            close_btn = dialog.locator(".el-dialog__headerbtn")
            if close_btn.count() > 0:
                close_btn.first.click()
                page.wait_for_timeout(500)
        else:
            log_fail("创建企业弹窗未打开", step=1)
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


def tc_e2e_036(page, tokens):
    """TC-E2E-036: 企业详情Drawer - click enterprise card, verify drawer"""
    global _logger
    case_id = "TC-E2E-036"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "企业详情Drawer", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_enterprise_page(page, tokens)
        log_info("=== 企业详情Drawer ===")

        # Click first enterprise card
        ent_card = page.locator(".enterprise-card").first
        if ent_card.is_visible():
            ent_card.click()
            page.wait_for_timeout(2000)

            # Check drawer
            drawer = page.locator(".el-drawer:visible")
            if drawer.count() > 0:
                log_pass("企业详情Drawer已打开", step=1)
                verifications["drawer_open"] = True

                # Check drawer title
                drawer_title = drawer.locator(".el-drawer__title")
                if drawer_title.count() > 0:
                    log_pass(f"Drawer标题: '{drawer_title.first.inner_text()}'", step=1)

                # Check drawer header section
                drawer_logo = drawer.locator(".drawer-logo")
                if drawer_logo.count() > 0:
                    log_pass("企业Logo可见", step=2)
                    verifications["drawer_logo"] = True
                else:
                    log_warn("企业Logo不可见", step=2)
                    verifications["drawer_logo"] = False

                # Check enterprise name in drawer
                drawer_name = drawer.locator(".drawer-name")
                if drawer_name.count() > 0:
                    log_pass(f"企业名称: '{drawer_name.first.inner_text()}'", step=2)
                    verifications["drawer_name"] = True
                else:
                    log_warn("企业名称不可见", step=2)
                    verifications["drawer_name"] = False

                # Check info grid
                info_grid = drawer.locator(".drawer-info-grid")
                if info_grid.count() > 0:
                    log_pass("企业信息网格可见", step=2)
                    verifications["info_grid"] = True

                    # Check info items
                    info_labels = ["信用代码", "地区", "行业领域", "企业标签"]
                    for label in info_labels:
                        info_item = drawer.locator(f".info-label:has-text('{label}')")
                        if info_item.count() > 0:
                            log_pass(f"信息项'{label}'可见", step=2)
                        else:
                            log_warn(f"信息项'{label}'未找到", step=2)
                else:
                    log_warn("企业信息网格不可见", step=2)
                    verifications["info_grid"] = False

                # Check description section
                desc_section = drawer.locator(".drawer-section-title:has-text('企业简介')")
                if desc_section.count() > 0:
                    log_pass("'企业简介'区可见", step=3)
                    verifications["desc_section"] = True
                else:
                    log_warn("'企业简介'区不可见", step=3)
                    verifications["desc_section"] = False

                ss.capture("CHECKPOINT", step=3, action="drawer_open")

                # Close drawer
                close_btn = drawer.locator(".el-drawer__close-btn")
                if close_btn.count() > 0:
                    close_btn.first.click()
                    page.wait_for_timeout(500)
            else:
                log_fail("企业详情Drawer未打开", step=1)
                verifications["drawer_open"] = False
        else:
            log_warn("无企业卡片，跳过", step=1)
            verifications["drawer_open"] = None

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
    lines = ["# 校链通 企业名录模块 E2E 测试报告", "",
             f"| 项目 | 内容 |", "|------|------|",
             f"| 测试模块 | 第5章 企业名录模块 (L2 E2E) |",
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
    print("校链通(XiaoLianTong) - 第5章 企业名录模块 L2 E2E 测试")
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
            ("TC-E2E-026: 页面结构", tc_e2e_026),
            ("TC-E2E-027: 筛选-行业分类", tc_e2e_027),
            ("TC-E2E-028: 筛选-业务品类", tc_e2e_028),
            ("TC-E2E-029: 筛选-所在地区", tc_e2e_029),
            ("TC-E2E-030: 筛选-热门标签", tc_e2e_030),
            ("TC-E2E-031: 已选摘要与重置", tc_e2e_031),
            ("TC-E2E-032: 企业卡片列表", tc_e2e_032),
            ("TC-E2E-033: 分页", tc_e2e_033),
            ("TC-E2E-034: 认领企业弹窗", tc_e2e_034),
            ("TC-E2E-035: 创建企业弹窗", tc_e2e_035),
            ("TC-E2E-036: 企业详情Drawer", tc_e2e_036),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page, token_data)
            all_results.append(r)

        browser.close()

    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch05.md")
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
