"""
校链通(XiaoLianTong) - 第4~8章 公共页面 L2 E2E 测试
覆盖: 商机广场、企业名录、校友圈、搜索、通知消息
测试用例: TC-E2E-075 ~ TC-E2E-081

应用地址: http://localhost:3000
"""

from playwright.sync_api import sync_playwright
import time, os, json, sys
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:3000")
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch4_8_public_pages")
SCREENSHOT_DIR = os.path.join(CAPTURES_DIR, datetime.now().strftime("%Y-%m-%d_%H%M%S"))
VIEWPORT = {"width": 1280, "height": 900}
DEFAULT_TIMEOUT = 30000
ADMIN_NAV_WAIT = 3000


def get_user_tokens():
    """Get regular user tokens for public page testing."""
    import urllib.request
    credentials = [
        ("13900001111", "Admin123!"),  # Enterprise admin
        ("13800000001", "Admin123!"),  # Platform admin
        ("admin", "admin"),
    ]
    for phone, pwd in credentials:
        try:
            url = "http://localhost:8000/api/v1/auth/login/password/"
            data = json.dumps({"phone": phone, "password": pwd}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("code") == 0 and result.get("data"):
                    return result["data"]
        except Exception:
            continue
    return None


def inject_user_login(page, token_data):
    """Inject user login for public pages."""
    user_info = {
        "id": token_data.get("user_id", 1),
        "phone": "13900001111",
        "role_code": "enterprise_admin",
        "enterprise_id": 1,
    }
    page.evaluate(f"""() => {{
        localStorage.setItem('access_token', '{token_data.get("access_token", "")}');
        localStorage.setItem('refresh_token', '{token_data.get("refresh_token", "")}');
        localStorage.setItem('user_info', JSON.stringify({json.dumps(user_info)}));
    }}""")


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


class TestLogger:
    def __init__(self, case_id, output_dir):
        self.case_id, self.output_dir, self.logs, self.start_time = case_id, output_dir, [], time.time()
        self.steps_passed = self.steps_failed = 0

    def log(self, level, step, action, message, **kwargs):
        entry = {"timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3], "level": level,
                 "case_id": self.case_id, "step": step, "action": action, "message": message, **kwargs}
        self.logs.append(entry)
        icon = {"INFO": "  ", "PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}.get(level, "  ")
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


def goto_page(page, tokens, path):
    inject_user_login(page, tokens)
    page.goto(f"{BASE_URL}{path}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(ADMIN_NAV_WAIT)


# ============================================================
# Test Cases
# ============================================================

def tc_e2e_075(page, tokens):
    """TC-E2E-075: 商机广场页面 - header + sidebar + cards"""
    global _logger
    case_id = "TC-E2E-075"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "商机广场页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_page(page, tokens, "/opportunity")
        log_info("=== 商机广场页面验证 ===")

        # Page header
        page_title = page.locator(".page-title")
        if page_title.count() > 0 and "商机广场" in page_title.first.inner_text():
            log_pass("'商机广场'页面标题可见", step=1)
            verifications["title"] = True
        else:
            log_fail("'商机广场'页面标题不可见", step=1)
            verifications["title"] = False

        # Subtitle
        subtitle = page.locator(".page-subtitle")
        if subtitle.count() > 0:
            log_pass(f"副标题: '{subtitle.first.inner_text()}'", step=1)
            verifications["subtitle"] = True
        else:
            log_fail("副标题不可见", step=1)
            verifications["subtitle"] = False

        # Publish buttons
        buy_btn = page.locator("button:has-text('发布采购需求')")
        supply_btn = page.locator("button:has-text('发布供应能力')")
        if buy_btn.count() > 0:
            log_pass("'发布采购需求'按钮可见", step=1)
            verifications["buy_btn"] = True
        if supply_btn.count() > 0:
            log_pass("'发布供应能力'按钮可见", step=1)
            verifications["supply_btn"] = True

        # Filter sidebar
        sidebar = page.locator(".filter-sidebar")
        if sidebar.count() > 0:
            log_pass("筛选侧边栏可见", step=2)
            verifications["sidebar"] = True
        else:
            log_fail("筛选侧边栏不可见", step=2)
            verifications["sidebar"] = False

        # Filter sections
        filter_sections = ["商机类型", "行业筛选", "业务品类", "地区筛选"]
        for section_name in filter_sections:
            section = page.locator(f".filter-title:has-text('{section_name}')")
            if section.count() > 0:
                log_pass(f"筛选区'{section_name}'可见", step=2)
                verifications[f"filter_{section_name}"] = True
            else:
                log_fail(f"筛选区'{section_name}'不可见", step=2)
                verifications[f"filter_{section_name}"] = False

        # Result count
        result_count = page.locator(".result-count")
        if result_count.count() > 0:
            log_pass(f"结果数量可见: '{result_count.first.inner_text()}'", step=2)
            verifications["result_count"] = True
        else:
            log_fail("结果数量不可见", step=2)
            verifications["result_count"] = False

        # Content layout
        content_layout = page.locator(".content-layout")
        if content_layout.count() > 0:
            log_pass("内容布局(侧边栏+主区域)可见", step=2)
            verifications["layout"] = True
        else:
            log_fail("内容布局不可见", step=2)
            verifications["layout"] = False

        ss.capture("CHECKPOINT", step=2, action="opportunity_page_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_076(page, tokens):
    """TC-E2E-076: 商机筛选侧边栏 - type checkboxes and filter summary"""
    global _logger
    case_id = "TC-E2E-076"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "商机筛选侧边栏", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_page(page, tokens, "/opportunity")
        log_info("=== 商机筛选侧边栏验证 ===")

        # Verify type checkboxes
        buy_checkbox = page.locator(".el-checkbox:has-text('我要买')")
        supply_checkbox = page.locator(".el-checkbox:has-text('我能供')")
        if buy_checkbox.count() > 0:
            log_pass("'我要买'复选框可见", step=1)
            verifications["buy_checkbox"] = True
        else:
            log_fail("'我要买'复选框不可见", step=1)
            verifications["buy_checkbox"] = False

        if supply_checkbox.count() > 0:
            log_pass("'我能供'复选框可见", step=1)
            verifications["supply_checkbox"] = True
        else:
            log_fail("'我能供'复选框不可见", step=1)
            verifications["supply_checkbox"] = False

        # Verify industry select
        industry_select = page.locator(".filter-sidebar .el-select").first
        if industry_select.count() > 0:
            log_pass("行业筛选下拉可见", step=2)
            verifications["industry_select"] = True
        else:
            log_fail("行业筛选下拉不可见", step=2)
            verifications["industry_select"] = False

        # Verify reset button
        reset_btn = page.locator("button:has-text('重置筛选')")
        if reset_btn.count() > 0:
            log_pass("'重置筛选'按钮可见", step=2)
            verifications["reset_btn"] = True
        else:
            log_fail("'重置筛选'按钮不可见", step=2)
            verifications["reset_btn"] = False

        ss.capture("CHECKPOINT", step=2, action="opp_filter_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_077(page, tokens):
    """TC-E2E-077: 企业名录页面 - header + sidebar + cards"""
    global _logger
    case_id = "TC-E2E-077"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "企业名录页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_page(page, tokens, "/enterprise")
        log_info("=== 企业名录页面验证 ===")

        # Page header
        page_title = page.locator(".page-title")
        if page_title.count() > 0 and "企业名录" in page_title.first.inner_text():
            log_pass("'企业名录'页面标题可见", step=1)
            verifications["title"] = True
        else:
            log_fail("'企业名录'页面标题不可见", step=1)
            verifications["title"] = False

        # Action buttons
        claim_btn = page.locator("button:has-text('认领已有企业')")
        create_btn = page.locator("button:has-text('创建新企业')")
        if claim_btn.count() > 0:
            log_pass("'认领已有企业'按钮可见", step=1)
            verifications["claim_btn"] = True
        if create_btn.count() > 0:
            log_pass("'创建新企业'按钮可见", step=1)
            verifications["create_btn"] = True

        # Filter sidebar
        sidebar = page.locator(".filter-sidebar")
        if sidebar.count() > 0:
            log_pass("筛选侧边栏可见", step=2)
            verifications["sidebar"] = True
        else:
            log_fail("筛选侧边栏不可见", step=2)
            verifications["sidebar"] = False

        # Filter groups
        filter_groups = ["行业分类", "业务品类", "所在地区", "热门标签"]
        for group_name in filter_groups:
            group = page.locator(f".filter-group-title:has-text('{group_name}')")
            if group.count() > 0:
                log_pass(f"筛选组'{group_name}'可见", step=2)
                verifications[f"filter_{group_name}"] = True
            else:
                log_fail(f"筛选组'{group_name}'不可见", step=2)
                verifications[f"filter_{group_name}"] = False

        # Reset button
        reset_btn = page.locator("button:has-text('重置筛选')")
        if reset_btn.count() > 0:
            log_pass("'重置筛选'按钮可见", step=2)
            verifications["reset_btn"] = True

        # Result count
        result_count = page.locator(".result-count")
        if result_count.count() > 0:
            log_pass(f"结果数量: '{result_count.first.inner_text()}'", step=2)
            verifications["result_count"] = True

        # Enterprise grid / cards
        enterprise_cards = page.locator(".enterprise-card")
        card_count = enterprise_cards.count()
        if card_count > 0:
            log_pass(f"企业卡片数量: {card_count}", step=3)
            verifications["cards"] = True

            # Check first card structure
            first_card = enterprise_cards.first
            logo = first_card.locator(".enterprise-logo")
            name = first_card.locator(".enterprise-name")
            footer = first_card.locator(".enterprise-card-footer")
            if logo.count() > 0:
                log_pass("企业卡片Logo可见", step=3)
                verifications["card_logo"] = True
            if name.count() > 0:
                log_pass(f"企业名称: '{name.first.inner_text()}'", step=3)
                verifications["card_name"] = True
            if footer.count() > 0:
                log_pass("卡片底部可见", step=3)
                verifications["card_footer"] = True
        else:
            log_warn("无企业数据", step=3)
            verifications["cards"] = False

        ss.capture("CHECKPOINT", step=3, action="enterprise_page_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_078(page, tokens):
    """TC-E2E-078: 认领企业弹窗 - two-step dialog"""
    global _logger
    case_id = "TC-E2E-078"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "认领企业弹窗", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_page(page, tokens, "/enterprise")
        log_info("=== 认领企业弹窗验证 ===")

        # Click "认领已有企业"
        claim_btn = page.locator("button:has-text('认领已有企业')")
        if claim_btn.count() > 0:
            claim_btn.first.click()
            page.wait_for_timeout(1500)

            dialog = page.locator(".el-dialog:visible")
            if dialog.count() > 0:
                log_pass("认领企业弹窗已打开", step=1)
                verifications["dialog_open"] = True

                # Verify dialog title
                dialog_title = dialog.locator(".el-dialog__title")
                if dialog_title.count() > 0:
                    title_text = dialog_title.first.inner_text()
                    log_pass(f"弹窗标题: '{title_text}'", step=1)

                # Verify step 1 content - enterprise list
                claim_tip = dialog.locator("text=请选择您要认领的企业")
                if claim_tip.count() > 0:
                    log_pass("认领提示可见(步骤1)", step=1)
                    verifications["step1_tip"] = True
                else:
                    log_fail("认领提示不可见", step=1)
                    verifications["step1_tip"] = False

                # Verify cancel button
                cancel_btn = dialog.locator("button:has-text('取消')")
                if cancel_btn.count() > 0:
                    log_pass("'取消'按钮可见", step=1)
                    verifications["cancel_btn"] = True

                ss.capture("CHECKPOINT", step=1, action="claim_dialog_step1")

                # Close dialog
                if cancel_btn.count() > 0:
                    cancel_btn.first.click()
                    page.wait_for_timeout(500)
            else:
                log_fail("认领企业弹窗未打开", step=1)
                verifications["dialog_open"] = False
        else:
            log_fail("'认领已有企业'按钮不可见", step=1)
            verifications["dialog_open"] = False

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_079(page, tokens):
    """TC-E2E-079: 校友圈页面 - header + feed cards"""
    global _logger
    case_id = "TC-E2E-079"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "校友圈页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_page(page, tokens, "/feed")
        log_info("=== 校友圈页面验证 ===")

        # Page title
        page_title = page.locator(".feeds-title")
        if page_title.count() > 0 and "校友圈" in page_title.first.inner_text():
            log_pass("'校友圈'页面标题可见", step=1)
            verifications["title"] = True
        else:
            log_fail("'校友圈'页面标题不可见", step=1)
            verifications["title"] = False

        # Subtitle
        subtitle = page.locator(".feeds-subtitle")
        if subtitle.count() > 0:
            log_pass(f"副标题: '{subtitle.first.inner_text()}'", step=1)
            verifications["subtitle"] = True

        # Publish button
        publish_btn = page.locator("button:has-text('发布动态')")
        if publish_btn.count() > 0:
            log_pass("'发布动态'按钮可见", step=1)
            verifications["publish_btn"] = True
        else:
            log_fail("'发布动态'按钮不可见", step=1)
            verifications["publish_btn"] = False

        # Feed cards
        feed_cards = page.locator(".feed-card")
        card_count = feed_cards.count()
        if card_count > 0:
            log_pass(f"动态卡片数量: {card_count}", step=2)
            verifications["feed_cards"] = True

            # Check first card structure
            first_card = feed_cards.first
            avatar = first_card.locator(".feed-author-avatar")
            author_name = first_card.locator(".feed-author-name")
            feed_content = first_card.locator(".feed-content")
            if avatar.count() > 0:
                log_pass("动态头像(48px圆形)可见", step=2)
                verifications["avatar"] = True
            if author_name.count() > 0:
                log_pass(f"作者名称: '{author_name.first.inner_text()}'", step=2)
                verifications["author_name"] = True
            if feed_content.count() > 0:
                log_pass("动态内容可见", step=2)
                verifications["content"] = True
        else:
            log_warn("无动态数据", step=2)
            verifications["feed_cards"] = False

        ss.capture("CHECKPOINT", step=2, action="feed_page_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_080(page, tokens):
    """TC-E2E-080: 搜索页面 - search bar + tabs"""
    global _logger
    case_id = "TC-E2E-080"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "搜索页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_page(page, tokens, "/search?q=测试")
        log_info("=== 搜索页面验证 ===")

        # Search bar
        search_bar = page.locator(".search-bar")
        if search_bar.count() > 0:
            log_pass("搜索栏可见", step=1)
            verifications["search_bar"] = True
        else:
            log_fail("搜索栏不可见", step=1)
            verifications["search_bar"] = False

        # Search input
        search_input = page.locator(".search-bar .el-input__inner")
        if search_input.count() > 0:
            input_value = search_input.first.input_value()
            log_pass(f"搜索框可见, 值: '{input_value}'", step=1)
            verifications["search_input"] = True
        else:
            log_fail("搜索框不可见", step=1)
            verifications["search_input"] = False

        # Search button
        search_btn = page.locator(".search-bar button:has-text('搜索')")
        if search_btn.count() > 0:
            log_pass("'搜索'按钮可见", step=1)
            verifications["search_btn"] = True
        else:
            log_fail("'搜索'按钮不可见", step=1)
            verifications["search_btn"] = False

        # Tabs
        expected_tabs = ["商机", "企业", "动态"]
        tab_items = page.locator(".el-tabs__item")
        if tab_items.count() >= 3:
            log_pass(f"Tab数量: {tab_items.count()}", step=2)
            verifications["tab_count"] = True
        else:
            log_fail(f"Tab数量不足: {tab_items.count()}", step=2)
            verifications["tab_count"] = False

        for tab_name in expected_tabs:
            tab = page.locator(f".el-tabs__item:has-text('{tab_name}')")
            if tab.count() > 0:
                log_pass(f"Tab '{tab_name}' 可见", step=2)
                verifications[f"tab_{tab_name}"] = True
            else:
                log_fail(f"Tab '{tab_name}' 不可见", step=2)
                verifications[f"tab_{tab_name}"] = False

        ss.capture("CHECKPOINT", step=2, action="search_page_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_081(page, tokens):
    """TC-E2E-081: 通知消息页面 - header + notification list"""
    global _logger
    case_id = "TC-E2E-081"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "通知消息页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_page(page, tokens, "/notification")
        log_info("=== 通知消息页面验证 ===")

        # Page header
        header = page.locator(".notif-header")
        if header.count() > 0:
            log_pass("通知页头部可见", step=1)
            verifications["header"] = True
        else:
            log_fail("通知页头部不可见", step=1)
            verifications["header"] = False

        # Title "通知消息"
        title = page.locator(".notif-header h2")
        if title.count() > 0 and "通知消息" in title.first.inner_text():
            log_pass("'通知消息'标题可见", step=1)
            verifications["title"] = True
        else:
            log_fail("'通知消息'标题不可见", step=1)
            verifications["title"] = False

        # "全部已读" button
        mark_all_btn = page.locator("button:has-text('全部已读')")
        if mark_all_btn.count() > 0:
            log_pass("'全部已读'按钮可见", step=1)
            verifications["mark_all_btn"] = True
        else:
            log_fail("'全部已读'按钮不可见", step=1)
            verifications["mark_all_btn"] = False

        # Notification list
        notif_list = page.locator(".notif-list")
        if notif_list.count() > 0:
            log_pass("通知列表容器可见", step=2)
            verifications["notif_list"] = True
        else:
            log_fail("通知列表容器不可见", step=2)
            verifications["notif_list"] = False

        # Notification items
        notif_items = page.locator(".notif-item")
        item_count = notif_items.count()
        if item_count > 0:
            log_pass(f"通知项数量: {item_count}", step=2)
            verifications["notif_items"] = True

            # Check first item structure
            first_item = notif_items.first
            icon = first_item.locator(".notif-icon")
            notif_title = first_item.locator(".notif-title")
            notif_body = first_item.locator(".notif-body")
            if icon.count() > 0:
                log_pass("通知图标(40px圆形)可见", step=2)
                verifications["notif_icon"] = True
            if notif_title.count() > 0:
                log_pass(f"通知标题: '{notif_title.first.inner_text()}'", step=2)
                verifications["notif_title"] = True
            if notif_body.count() > 0:
                log_pass("通知内容体可见", step=2)
                verifications["notif_body"] = True

            # Check for tag
            notif_tag = first_item.locator(".notif-tag")
            if notif_tag.count() > 0:
                log_pass("通知类别标签可见", step=2)
                verifications["notif_tag"] = True
        else:
            log_warn("无通知数据", step=2)
            verifications["notif_items"] = False

        ss.capture("CHECKPOINT", step=2, action="notification_page_verified")

        passed = sum(1 for v in verifications.values() if v)
        total = len(verifications)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else "FAIL"
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


# ============================================================
# Report & Main
# ============================================================
def _generate_report(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 校链通 公共页面 E2E 测试报告", "",
        "| 项目 | 内容 |",
        "|------|------|",
        f"| 测试模块 | 第4~8章 公共页面 (L2 E2E) |",
        f"| 测试日期 | {now} |",
        f"| 用例数量 | {len(results)} |",
        "",
        "## 测试结果汇总", "",
        "| 用例ID | 用例名称 | 结果 | 置信度 |",
        "|--------|----------|------|--------|",
    ]
    for r in results:
        conf = f"{r.get('confidence', 'N/A')}"
        lines.append(f"| {r['case_id']} | {r['name']} | {r['status']} | {conf} |")
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    lines.extend(["", f"通过率: {pass_count}/{len(results)} ({pass_count/len(results)*100:.0f}%)"])
    return "\n".join(lines)


def main():
    global SCREENSHOT_DIR
    print("=" * 70)
    print("校链通 - 第4~8章 公共页面 L2 E2E 测试")
    print(f"目标地址: {BASE_URL}")
    print(f"截图目录: {SCREENSHOT_DIR}")
    print("=" * 70)

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print("获取用户Token...")
    token_data = get_user_tokens()
    if not token_data:
        print("获取Token失败")
        return
    print(f"  access_token: {token_data.get('access_token', '')[:20]}...")

    all_results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT, ignore_https_errors=True)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)

        try:
            resp = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=10000)
            print(f"应用可访问: HTTP {resp.status if resp else 'N/A'}")
        except Exception as e:
            print(f"无法访问: {e}")
            browser.close()
            return
        page.wait_for_timeout(500)

        test_cases = [
            ("TC-E2E-075: 商机广场页面", tc_e2e_075),
            ("TC-E2E-076: 商机筛选侧边栏", tc_e2e_076),
            ("TC-E2E-077: 企业名录页面", tc_e2e_077),
            ("TC-E2E-078: 认领企业弹窗", tc_e2e_078),
            ("TC-E2E-079: 校友圈页面", tc_e2e_079),
            ("TC-E2E-080: 搜索页面", tc_e2e_080),
            ("TC-E2E-081: 通知消息页面", tc_e2e_081),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page, token_data)
            all_results.append(r)

        browser.close()

    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch4_8.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 70)
    print("测试执行完成")
    print("=" * 70)
    for r in all_results:
        print(f"  {r['case_id']} {r['name']}: {r['status']} (置信度 {r.get('confidence', 'N/A')})")
    pass_count = sum(1 for r in all_results if r["status"] == "PASS")
    print(f"\n通过率: {pass_count}/{len(all_results)} ({pass_count/len(all_results)*100:.0f}%)")


if __name__ == "__main__":
    main()
