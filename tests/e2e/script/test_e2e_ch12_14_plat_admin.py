"""
校链通(XiaoLianTong) - 第12~14章 平台管理模块 L2 E2E 测试
基于 QA-test-plan-PP-v1.0.md 第12~14章
覆盖用例: TC-E2E-057 ~ TC-E2E-067

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
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch12_14_plat_admin")
SCREENSHOT_DIR = os.path.join(CAPTURES_DIR, datetime.now().strftime("%Y-%m-%d_%H%M%S"))
VIEWPORT = {"width": 1280, "height": 900}
DEFAULT_TIMEOUT = 30000
ADMIN_NAV_WAIT = 4000  # Admin pages need longer mount time


# ============================================================
# Auth helper - get JWT tokens via API, with admin user fallback
# ============================================================
def get_admin_tokens():
    """Try multiple admin credentials; return token data dict or None."""
    import urllib.request
    credentials = [
        ("13800000001", "Admin123!"),
        ("admin", "admin"),
    ]
    for phone, pwd in credentials:
        try:
            url = "http://localhost:8000/api/v1/auth/login/password/"
            data = json.dumps({"phone": phone, "password": pwd}).encode("utf-8")
            req = urllib.request.Request(
                url, data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("code") == 0 and result.get("data"):
                    return result["data"]
        except Exception:
            continue
    return None


def inject_admin_login(page, token_data):
    """Inject both tokens AND user_info (required by router guard)."""
    user_info = {
        "id": token_data.get("user_id", 1),
        "phone": "13800000001",
        "role_code": "super_admin",
        "enterprise_id": None,
    }
    page.evaluate(f"""() => {{
        localStorage.setItem('access_token', '{token_data.get("access_token", "")}');
        localStorage.setItem('refresh_token', '{token_data.get("refresh_token", "")}');
        localStorage.setItem('user_info', JSON.stringify({json.dumps(user_info)}));
    }}""")


# ============================================================
# Screenshot & Logger (reuse pattern from ch03_homepage)
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
# Helper to navigate to admin page with auth
# ============================================================
def goto_admin_page(page, tokens, path="/plat-admin/dashboard"):
    """Navigate to an admin page with full auth injection."""
    inject_admin_login(page, tokens)
    page.goto(f"{BASE_URL}{path}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(ADMIN_NAV_WAIT)
    return tokens


# ============================================================
# Test Cases
# ============================================================

def tc_e2e_057(page, tokens):
    """TC-E2E-057: 侧边栏结构 - verify admin sidebar menu groups"""
    global _logger
    case_id = "TC-E2E-057"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "侧边栏结构", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/dashboard")
        log_info("=== 侧边栏结构验证 ===")

        # Verify sidebar container
        sidebar = page.locator(".admin-sidebar")
        if sidebar.count() > 0 and sidebar.first.is_visible():
            log_pass("admin-sidebar 可见", step=1)
            verifications["sidebar"] = True
        else:
            log_fail("admin-sidebar 不可见", step=1)
            verifications["sidebar"] = False

        # Verify brand
        brand = page.locator(".sidebar-brand")
        if brand.count() > 0 and brand.first.is_visible():
            brand_text = brand.first.inner_text()
            log_pass(f"品牌区域可见: '{brand_text}'", step=1)
            verifications["brand"] = True
        else:
            log_fail("品牌区域不可见", step=1)
            verifications["brand"] = False

        # Verify sidebar nav links (from AdminLayout.vue menuItems)
        expected_menu_items = [
            ("数据大盘", "/plat-admin/dashboard"),
            ("企业审核", "/plat-admin/audit"),
            ("企业租户", "/plat-admin/tenant"),
            ("商机管理", "/plat-admin/opportunity-manage"),
            ("动态管理", "/plat-admin/feed-manage"),
            ("基础数据", "/plat-admin/master-data"),
            ("账号权限", "/plat-admin/rbac"),
            ("系统设置", "/plat-admin/settings"),
        ]
        for label, path in expected_menu_items:
            link = page.locator(f".sidebar-link:has-text('{label}')")
            if link.count() > 0 and link.first.is_visible():
                href = link.first.get_attribute("href") or ""
                log_pass(f"侧边栏菜单'{label}'可见, href={href}", step=2)
                verifications[f"menu_{label}"] = True
            else:
                log_fail(f"侧边栏菜单'{label}'不可见", step=2)
                verifications[f"menu_{label}"] = False

        # Verify active state on Dashboard link
        active_link = page.locator(".sidebar-link--active")
        if active_link.count() > 0:
            active_text = active_link.first.inner_text()
            log_pass(f"当前激活菜单: '{active_text}'", step=3)
            verifications["active_link"] = True
        else:
            log_warn("无激活菜单项", step=3)
            verifications["active_link"] = False

        # Verify admin header
        header = page.locator(".admin-header")
        if header.count() > 0 and header.first.is_visible():
            log_pass("admin-header 可见", step=3)
            verifications["header"] = True
        else:
            log_fail("admin-header 不可见", step=3)
            verifications["header"] = False

        ss.capture("CHECKPOINT", step=3, action="sidebar_verified")

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


def tc_e2e_058(page, tokens):
    """TC-E2E-058: 统计卡片 - 4 stat cards with trend arrows"""
    global _logger
    case_id = "TC-E2E-058"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "统计卡片", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/dashboard")
        log_info("=== 统计卡片验证 ===")

        # Verify stat cards count
        cards = page.locator(".stat-card")
        card_count = cards.count()
        if card_count == 4:
            log_pass(f"统计卡片数量: {card_count}", step=1)
            verifications["card_count"] = True
        else:
            log_fail(f"统计卡片数量: {card_count} (期望4)", step=1)
            verifications["card_count"] = False

        # Verify each card label (from Dashboard.vue statsConfig)
        expected_labels = ["入驻企业", "累计商机", "成功撮合", "活跃校友"]
        for i, label in enumerate(expected_labels):
            card_label = page.locator(f".stat-label:has-text('{label}')")
            if card_label.count() > 0:
                log_pass(f"卡片[{i}]: '{label}'标签可见", step=2)
                verifications[f"label_{i}"] = True
            else:
                log_fail(f"卡片[{i}]: '{label}'标签未找到", step=2)
                verifications[f"label_{i}"] = False

        # Verify stat icons (emoji in .stat-icon)
        icons = page.locator(".stat-icon")
        if icons.count() >= 4:
            log_pass(f"统计图标数量: {icons.count()}", step=2)
            verifications["icons"] = True
        else:
            log_warn(f"统计图标数量: {icons.count()}", step=2)
            verifications["icons"] = icons.count() > 0

        # Verify stat values
        values = page.locator(".stat-value")
        if values.count() >= 4:
            log_pass(f"统计数值区域: {values.count()}个", step=2)
            verifications["values"] = True
        else:
            log_fail(f"统计数值区域不足: {values.count()}", step=2)
            verifications["values"] = False

        # Verify trend arrows
        trends = page.locator(".stat-trend")
        trend_count = trends.count()
        if trend_count >= 1:
            log_pass(f"趋势箭头: {trend_count}个", step=3)
            # Check for up/down class
            up_trends = page.locator(".stat-trend.up")
            down_trends = page.locator(".stat-trend.down")
            log_pass(f"上升趋势: {up_trends.count()}, 下降趋势: {down_trends.count()}", step=3)
            verifications["trends"] = True
        else:
            log_fail("无趋势箭头", step=3)
            verifications["trends"] = False

        ss.capture("CHECKPOINT", step=3, action="stat_cards_verified")

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


def tc_e2e_059(page, tokens):
    """TC-E2E-059: 趋势图 - chart area exists"""
    global _logger
    case_id = "TC-E2E-059"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "趋势图", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/dashboard")
        log_info("=== 趋势图验证 ===")

        # Verify trend chart section card
        chart_card = page.locator(".section-card")
        if chart_card.count() > 0:
            log_pass("趋势图卡片可见", step=1)
            verifications["card"] = True
        else:
            log_fail("趋势图卡片不可见", step=1)
            verifications["card"] = False

        # Verify chart header "最近7天商机趋势"
        chart_header = page.locator("text=最近7天商机趋势")
        if chart_header.count() > 0:
            log_pass("'最近7天商机趋势'标题可见", step=1)
            verifications["header"] = True
        else:
            log_fail("'最近7天商机趋势'标题不可见", step=1)
            verifications["header"] = False

        # Verify trend chart area
        trend_chart = page.locator(".trend-chart")
        if trend_chart.count() > 0 and trend_chart.first.is_visible():
            log_pass("趋势图区域可见", step=2)
            verifications["chart_area"] = True
        else:
            log_fail("趋势图区域不可见", step=2)
            verifications["chart_area"] = False

        # Verify chart bars
        chart_bars = page.locator(".chart-bar")
        if chart_bars.count() >= 7:
            log_pass(f"趋势柱状条: {chart_bars.count()}个(期望7)", step=2)
            verifications["bars"] = True
        else:
            log_fail(f"趋势柱状条不足: {chart_bars.count()}个(期望7)", step=2)
            verifications["bars"] = False

        # Verify chart labels (周一~周日)
        chart_labels = page.locator(".chart-label")
        if chart_labels.count() >= 7:
            label_texts = [chart_labels.nth(i).inner_text() for i in range(min(chart_labels.count(), 7))]
            log_pass(f"图表标签: {label_texts}", step=3)
            verifications["labels"] = True
        else:
            log_fail(f"图表标签不足: {chart_labels.count()}个", step=3)
            verifications["labels"] = False

        # Verify chart bars container
        chart_bars_container = page.locator(".chart-bars")
        if chart_bars_container.count() > 0:
            log_pass("chart-bars 容器可见", step=3)
            verifications["bars_container"] = True
        else:
            log_warn("chart-bars 容器不可见", step=3)
            verifications["bars_container"] = False

        ss.capture("CHECKPOINT", step=3, action="trend_chart_verified")

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


def tc_e2e_060(page, tokens):
    """TC-E2E-060: 审核列表 - tabs and table columns"""
    global _logger
    case_id = "TC-E2E-060"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "审核列表", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/audit")
        log_info("=== 审核列表页面验证 ===")

        # Verify page title
        page_title = page.locator(".admin-page-title")
        if page_title.count() > 0:
            title_text = page_title.first.inner_text()
            log_pass(f"页面标题: '{title_text}'", step=1)
            verifications["title"] = True
        else:
            log_warn("页面标题不可见", step=1)
            verifications["title"] = False

        # Verify card header "企业审核"
        card_header = page.locator(".el-card__header:has-text('企业审核')")
        if card_header.count() > 0:
            log_pass("'企业审核'卡片标题可见", step=1)
            verifications["card_title"] = True
        else:
            log_fail("'企业审核'卡片标题不可见", step=1)
            verifications["card_title"] = False

        # Verify tabs (from Audit.vue: 全部/待审核/已通过/已拒绝)
        expected_tabs = ["全部", "待审核", "已通过", "已拒绝"]
        tab_items = page.locator(".el-tabs__item")
        tab_count = tab_items.count()
        if tab_count >= 4:
            tab_texts = [tab_items.nth(i).inner_text() for i in range(tab_count)]
            log_pass(f"Tab数量: {tab_count}, 内容: {tab_texts}", step=2)
            verifications["tab_count"] = True
        else:
            log_fail(f"Tab数量不足: {tab_count}(期望4)", step=2)
            verifications["tab_count"] = False

        # Verify each expected tab exists
        for tab_name in expected_tabs:
            tab = page.locator(f".el-tabs__item:has-text('{tab_name}')")
            if tab.count() > 0:
                log_pass(f"Tab '{tab_name}' 可见", step=2)
                verifications[f"tab_{tab_name}"] = True
            else:
                log_fail(f"Tab '{tab_name}' 不可见", step=2)
                verifications[f"tab_{tab_name}"] = False

        # Verify table exists
        table = page.locator(".audit-page .el-table")
        if table.count() > 0:
            log_pass("审核表格可见", step=3)
            verifications["table"] = True
        else:
            log_fail("审核表格不可见", step=3)
            verifications["table"] = False

        # Verify table column headers (from Audit.vue)
        expected_columns = ["企业名称", "统一社会信用代码", "法定代表人", "状态", "申请时间", "操作"]
        for col_name in expected_columns:
            col_header = page.locator(f".el-table__header th:has-text('{col_name}')")
            if col_header.count() > 0:
                log_pass(f"列'{col_name}'存在", step=3)
                verifications[f"col_{col_name}"] = True
            else:
                log_fail(f"列'{col_name}'未找到", step=3)
                verifications[f"col_{col_name}"] = False

        ss.capture("CHECKPOINT", step=3, action="audit_list_verified")

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


def tc_e2e_061(page, tokens):
    """TC-E2E-061: Tab切换 - click between tabs"""
    global _logger
    case_id = "TC-E2E-061"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "Tab切换", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/audit")
        log_info("=== Tab切换验证 ===")

        tabs_to_test = ["待审核", "已通过", "已拒绝", "全部"]
        for i, tab_name in enumerate(tabs_to_test):
            tab = page.locator(f".el-tabs__item:has-text('{tab_name}')")
            if tab.count() > 0 and tab.first.is_visible():
                tab.first.click()
                page.wait_for_timeout(1500)

                # Verify tab is active
                active_tab = page.locator(".el-tabs__item.is-active")
                if active_tab.count() > 0:
                    active_text = active_tab.first.inner_text()
                    if tab_name in active_text:
                        log_pass(f"点击'{tab_name}' -> 激活'{active_text}'", step=i + 1)
                        verifications[f"tab_{tab_name}"] = True
                    else:
                        log_fail(f"点击'{tab_name}' -> 激活'{active_text}'", step=i + 1)
                        verifications[f"tab_{tab_name}"] = False
                else:
                    log_fail(f"点击'{tab_name}' -> 无激活Tab", step=i + 1)
                    verifications[f"tab_{tab_name}"] = False

                ss.capture("CHECKPOINT", step=i + 1, action=f"tab_{tab_name}")
            else:
                log_fail(f"Tab'{tab_name}'不可见", step=i + 1)
                verifications[f"tab_{tab_name}"] = False

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


def tc_e2e_062(page, tokens):
    """TC-E2E-062: 审核通过 - click audit approve button, verify dialog"""
    global _logger
    case_id = "TC-E2E-062"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "审核通过", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/audit")
        log_info("=== 审核通过弹窗验证 ===")

        # Click "待审核" tab first
        pending_tab = page.locator(".el-tabs__item:has-text('待审核')")
        if pending_tab.count() > 0 and pending_tab.first.is_visible():
            pending_tab.first.click()
            page.wait_for_timeout(1500)

        # Look for "通过" button (only shown for pending rows)
        approve_btn = page.locator("button:has-text('通过')").first
        if approve_btn.is_visible():
            approve_btn.click()
            page.wait_for_timeout(1500)

            # Verify dialog opened
            dialog = page.locator(".el-dialog:visible")
            if dialog.count() > 0:
                log_pass("审核通过弹窗已打开", step=1)
                verifications["dialog_open"] = True

                # Verify dialog title
                dialog_title = dialog.locator(".el-dialog__title")
                if dialog_title.count() > 0:
                    title_text = dialog_title.first.inner_text()
                    log_pass(f"弹窗标题: '{title_text}'", step=1)

                # Verify enterprise info descriptions
                descriptions = dialog.locator(".el-descriptions")
                if descriptions.count() > 0:
                    log_pass("企业信息描述表格可见", step=2)
                    verifications["ent_info"] = True
                else:
                    log_warn("企业信息描述表格不可见", step=2)
                    verifications["ent_info"] = False

                # Verify remark textarea (备注)
                textarea = dialog.locator(".el-textarea__inner")
                if textarea.count() > 0:
                    log_pass("备注输入框可见", step=2)
                    verifications["remark_field"] = True
                else:
                    log_fail("备注输入框不可见", step=2)
                    verifications["remark_field"] = False

                # Verify buttons
                confirm_btn = dialog.locator("button:has-text('确认通过')")
                cancel_btn = dialog.locator("button:has-text('取消')")
                if confirm_btn.count() > 0:
                    log_pass("'确认通过'按钮可见", step=3)
                    verifications["confirm_btn"] = True
                else:
                    log_fail("'确认通过'按钮不可见", step=3)
                    verifications["confirm_btn"] = False
                if cancel_btn.count() > 0:
                    log_pass("'取消'按钮可见", step=3)
                    verifications["cancel_btn"] = True

                ss.capture("CHECKPOINT", step=3, action="approve_dialog")

                # Close dialog via cancel
                if cancel_btn.count() > 0:
                    cancel_btn.first.click()
                    page.wait_for_timeout(500)
            else:
                log_fail("审核通过弹窗未打开", step=1)
                verifications["dialog_open"] = False
                ss.save_dom_snapshot(step=1, tag="no_dialog")
        else:
            log_warn("无待审核数据,无法测试通过弹窗", step=1)
            verifications["dialog_open"] = None  # N/A - no data

            # Try clicking "全部" tab and check if any pending rows exist
            all_tab = page.locator(".el-tabs__item:has-text('全部')")
            if all_tab.count() > 0:
                all_tab.first.click()
                page.wait_for_timeout(1500)
                approve_btn2 = page.locator("button:has-text('通过')").first
                if approve_btn2.is_visible():
                    approve_btn2.click()
                    page.wait_for_timeout(1500)
                    dialog2 = page.locator(".el-dialog:visible")
                    if dialog2.count() > 0:
                        log_pass("从全部Tab找到待审核数据，弹窗已打开", step=1)
                        verifications["dialog_open"] = True
                        ss.capture("CHECKPOINT", step=1, action="approve_dialog_from_all")
                        cancel = dialog2.locator("button:has-text('取消')")
                        if cancel.count() > 0:
                            cancel.first.click()
                            page.wait_for_timeout(500)

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
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


def tc_e2e_063(page, tokens):
    """TC-E2E-063: 审核驳回 - fill reject reason"""
    global _logger
    case_id = "TC-E2E-063"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "审核驳回", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/audit")
        log_info("=== 审核驳回弹窗验证 ===")

        # Click "待审核" tab first
        pending_tab = page.locator(".el-tabs__item:has-text('待审核')")
        if pending_tab.count() > 0 and pending_tab.first.is_visible():
            pending_tab.first.click()
            page.wait_for_timeout(1500)

        # Look for "拒绝" button (only shown for pending rows)
        reject_btn = page.locator("button:has-text('拒绝')").first
        if reject_btn.is_visible():
            reject_btn.click()
            page.wait_for_timeout(1500)

            # Verify reject dialog opened
            dialog = page.locator(".el-dialog:visible")
            if dialog.count() > 0:
                log_pass("审核拒绝弹窗已打开", step=1)
                verifications["dialog_open"] = True

                # Verify dialog title contains "拒绝"
                dialog_title = dialog.locator(".el-dialog__title")
                if dialog_title.count() > 0:
                    title_text = dialog_title.first.inner_text()
                    log_pass(f"弹窗标题: '{title_text}'", step=1)

                # Verify enterprise info descriptions
                descriptions = dialog.locator(".el-descriptions")
                if descriptions.count() > 0:
                    log_pass("企业信息描述表格可见", step=2)
                    verifications["ent_info"] = True
                else:
                    log_warn("企业信息描述表格不可见", step=2)
                    verifications["ent_info"] = False

                # Verify reject reason textarea (required field)
                textarea = dialog.locator(".el-textarea__inner")
                if textarea.count() > 0:
                    log_pass("拒绝原因输入框可见", step=2)
                    verifications["reason_field"] = True

                    # Fill in reject reason
                    textarea.first.fill("E2E测试驳回原因-不符合审核要求")
                    page.wait_for_timeout(500)
                    log_pass("已填写拒绝原因", step=3)
                    verifications["fill_reason"] = True
                else:
                    log_fail("拒绝原因输入框不可见", step=2)
                    verifications["reason_field"] = False

                # Verify confirm reject button
                confirm_btn = dialog.locator("button:has-text('确认拒绝')")
                if confirm_btn.count() > 0:
                    log_pass("'确认拒绝'按钮可见", step=3)
                    verifications["confirm_btn"] = True
                else:
                    log_fail("'确认拒绝'按钮不可见", step=3)
                    verifications["confirm_btn"] = False

                # Verify cancel button
                cancel_btn = dialog.locator("button:has-text('取消')")
                if cancel_btn.count() > 0:
                    log_pass("'取消'按钮可见", step=3)
                    verifications["cancel_btn"] = True

                ss.capture("CHECKPOINT", step=3, action="reject_dialog")

                # Close dialog via cancel (do NOT actually submit reject)
                if cancel_btn.count() > 0:
                    cancel_btn.first.click()
                    page.wait_for_timeout(500)
            else:
                log_fail("审核拒绝弹窗未打开", step=1)
                verifications["dialog_open"] = False
                ss.save_dom_snapshot(step=1, tag="no_dialog")
        else:
            log_warn("无待审核数据,无法测试拒绝弹窗", step=1)
            verifications["dialog_open"] = None  # N/A - no data

            # Try from "全部" tab
            all_tab = page.locator(".el-tabs__item:has-text('全部')")
            if all_tab.count() > 0:
                all_tab.first.click()
                page.wait_for_timeout(1500)
                reject_btn2 = page.locator("button:has-text('拒绝')").first
                if reject_btn2.is_visible():
                    reject_btn2.click()
                    page.wait_for_timeout(1500)
                    dialog2 = page.locator(".el-dialog:visible")
                    if dialog2.count() > 0:
                        log_pass("从全部Tab找到待审核数据，拒绝弹窗已打开", step=1)
                        verifications["dialog_open"] = True
                        ss.capture("CHECKPOINT", step=1, action="reject_dialog_from_all")
                        cancel = dialog2.locator("button:has-text('取消')")
                        if cancel.count() > 0:
                            cancel.first.click()
                            page.wait_for_timeout(500)

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
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


def tc_e2e_064(page, tokens):
    """TC-E2E-064: 租户列表 - table with correct columns"""
    global _logger
    case_id = "TC-E2E-064"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "租户列表", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/tenant")
        log_info("=== 租户列表页面验证 ===")

        # Verify page title
        page_title = page.locator(".admin-page-title")
        if page_title.count() > 0:
            title_text = page_title.first.inner_text()
            log_pass(f"页面标题: '{title_text}'", step=1)
            verifications["title"] = True
        else:
            log_warn("页面标题不可见", step=1)
            verifications["title"] = False

        # Verify card header "企业租户管理"
        card_header = page.locator(".el-card__header:has-text('企业租户管理')")
        if card_header.count() > 0:
            log_pass("'企业租户管理'卡片标题可见", step=1)
            verifications["card_title"] = True
        else:
            log_fail("'企业租户管理'卡片标题不可见", step=1)
            verifications["card_title"] = False

        # Verify filter bar (search input + status select + search button)
        filter_bar = page.locator(".filter-bar")
        if filter_bar.count() > 0:
            log_pass("筛选栏可见", step=1)
            verifications["filter_bar"] = True
        else:
            log_fail("筛选栏不可见", step=1)
            verifications["filter_bar"] = False

        # Verify search input
        search_input = page.locator(".filter-bar .el-input")
        if search_input.count() > 0:
            placeholder = search_input.first.get_attribute("placeholder") or ""
            log_pass(f"搜索框可见, placeholder='{placeholder}'", step=1)
            verifications["search_input"] = True
        else:
            log_fail("搜索框不可见", step=1)
            verifications["search_input"] = False

        # Verify status filter select
        status_select = page.locator(".filter-bar .el-select")
        if status_select.count() > 0:
            log_pass("认证状态下拉可见", step=1)
            verifications["status_select"] = True
        else:
            log_fail("认证状态下拉不可见", step=1)
            verifications["status_select"] = False

        # Verify table exists
        table = page.locator(".tenant-page .el-table")
        if table.count() > 0:
            log_pass("租户表格可见", step=2)
            verifications["table"] = True
        else:
            log_fail("租户表格不可见", step=2)
            verifications["table"] = False

        # Verify table column headers (from Tenant.vue)
        expected_columns = ["企业名称", "统一社会信用代码", "认证状态", "启用状态", "创建时间", "操作"]
        for col_name in expected_columns:
            col_header = page.locator(f".el-table__header th:has-text('{col_name}')")
            if col_header.count() > 0:
                log_pass(f"列'{col_name}'存在", step=2)
                verifications[f"col_{col_name}"] = True
            else:
                log_fail(f"列'{col_name}'未找到", step=2)
                verifications[f"col_{col_name}"] = False

        # Verify expand column exists (for member management)
        expand_col = page.locator(".el-table__header th .el-table__expand-icon, .el-table__expand-column")
        if expand_col.count() > 0:
            log_pass("展开列(成员管理)存在", step=3)
            verifications["expand_col"] = True
        else:
            log_warn("展开列(成员管理)未找到(可能表格为空)", step=3)
            verifications["expand_col"] = False

        ss.capture("CHECKPOINT", step=3, action="tenant_list_verified")

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


def tc_e2e_065(page, tokens):
    """TC-E2E-065: 成员管理弹窗 - click member management, verify dialog"""
    global _logger
    case_id = "TC-E2E-065"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "成员管理弹窗", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/tenant")
        log_info("=== 成员管理弹窗验证 ===")

        # In Tenant.vue, the expand arrow icon must be clicked to expand.
        # Element Plus renders .el-table__expand-icon inside the expand column.
        table_rows = page.locator(".tenant-page .el-table__body-wrapper .el-table__row")
        if table_rows.count() > 0:
            # Click the expand arrow icon on the first row
            expand_icon = table_rows.first.locator(".el-table__expand-icon")
            if expand_icon.count() > 0:
                expand_icon.first.click()
                page.wait_for_timeout(2000)  # Wait for member data to load
            else:
                # Fallback: click the row itself
                table_rows.first.click()
                page.wait_for_timeout(2000)

            # Check if expand content is visible
            expand_content = page.locator(".expand-content")
            if expand_content.count() > 0:
                log_pass("展开区域(成员列表)可见", step=1)
                verifications["expand_content"] = True

                # Verify "成员列表" header
                member_header = expand_content.locator("text=成员列表")
                if member_header.count() > 0:
                    log_pass("'成员列表'标题可见", step=1)
                    verifications["member_header"] = True
                else:
                    log_fail("'成员列表'标题不可见", step=1)
                    verifications["member_header"] = False

                # Verify "添加成员" button
                add_member_btn = expand_content.locator("button:has-text('添加成员')")
                if add_member_btn.count() > 0:
                    log_pass("'添加成员'按钮可见", step=2)
                    verifications["add_member_btn"] = True

                    # Click "添加成员" to open dialog
                    add_member_btn.first.click()
                    page.wait_for_timeout(1000)

                    # Verify dialog
                    dialog = page.locator(".el-dialog:visible")
                    if dialog.count() > 0:
                        log_pass("添加成员弹窗已打开", step=2)
                        verifications["dialog_open"] = True

                        # Verify dialog title
                        dialog_title = dialog.locator(".el-dialog__title")
                        if dialog_title.count() > 0:
                            title_text = dialog_title.first.inner_text()
                            log_pass(f"弹窗标题: '{title_text}'", step=2)

                        # Verify phone input
                        phone_input = dialog.locator(".el-input__inner")
                        if phone_input.count() > 0:
                            log_pass("手机号输入框可见", step=3)
                            verifications["phone_input"] = True
                        else:
                            log_fail("手机号输入框不可见", step=3)
                            verifications["phone_input"] = False

                        # Verify role select
                        role_select = dialog.locator(".el-select")
                        if role_select.count() > 0:
                            log_pass("角色选择框可见", step=3)
                            verifications["role_select"] = True
                        else:
                            log_fail("角色选择框不可见", step=3)
                            verifications["role_select"] = False

                        # Verify buttons
                        confirm_btn = dialog.locator("button:has-text('确定')")
                        cancel_btn = dialog.locator("button:has-text('取消')")
                        if confirm_btn.count() > 0:
                            log_pass("'确定'按钮可见", step=3)
                        if cancel_btn.count() > 0:
                            log_pass("'取消'按钮可见", step=3)

                        ss.capture("CHECKPOINT", step=3, action="member_dialog")

                        # Close dialog
                        if cancel_btn.count() > 0:
                            cancel_btn.first.click()
                            page.wait_for_timeout(500)
                    else:
                        log_fail("添加成员弹窗未打开", step=2)
                        verifications["dialog_open"] = False
                else:
                    log_fail("'添加成员'按钮不可见", step=2)
                    verifications["add_member_btn"] = False

                ss.capture("CHECKPOINT", step=2, action="expand_content")
            else:
                log_fail("展开区域(成员列表)不可见", step=1)
                verifications["expand_content"] = False
        else:
            log_warn("租户表格无数据,无法测试成员管理", step=1)
            verifications["expand_content"] = None  # N/A

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
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


def tc_e2e_066(page, tokens):
    """TC-E2E-066: 新增成员 - click add member button"""
    global _logger
    case_id = "TC-E2E-066"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "新增成员", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/tenant")
        log_info("=== 新增成员验证 ===")

        # Expand a row first - click the expand arrow icon
        table_rows = page.locator(".tenant-page .el-table__body-wrapper .el-table__row")
        if table_rows.count() > 0:
            expand_icon = table_rows.first.locator(".el-table__expand-icon")
            if expand_icon.count() > 0:
                expand_icon.first.click()
            else:
                table_rows.first.click()
            page.wait_for_timeout(2000)

            # Click "添加成员"
            add_btn = page.locator(".expand-content button:has-text('添加成员')")
            if add_btn.count() > 0 and add_btn.first.is_visible():
                add_btn.first.click()
                page.wait_for_timeout(1000)

                dialog = page.locator(".el-dialog:visible")
                if dialog.count() > 0:
                    log_pass("新增成员弹窗已打开", step=1)
                    verifications["dialog_open"] = True

                    # Verify title is "添加成员"
                    title = dialog.locator(".el-dialog__title")
                    if title.count() > 0 and "添加成员" in title.first.inner_text():
                        log_pass(f"弹窗标题正确: '{title.first.inner_text()}'", step=1)
                        verifications["title"] = True
                    else:
                        log_fail("弹窗标题不正确", step=1)
                        verifications["title"] = False

                    # Fill in phone number
                    phone_input = dialog.locator(".el-form-item:has-text('手机号') .el-input__inner")
                    if phone_input.count() > 0:
                        phone_input.first.fill("13900001234")
                        log_pass("已输入手机号: 13900001234", step=2)
                        verifications["fill_phone"] = True
                    else:
                        log_fail("手机号输入框不可见", step=2)
                        verifications["fill_phone"] = False

                    # Verify role select and options
                    role_select = dialog.locator(".el-form-item:has-text('角色') .el-select")
                    if role_select.count() > 0:
                        log_pass("角色选择框可见", step=2)
                        verifications["role_select"] = True

                        # Click to open dropdown
                        role_select.first.click()
                        page.wait_for_timeout(500)

                        # Verify role options
                        option_employee = page.locator(".el-select-dropdown__item:has-text('普通员工')")
                        option_admin = page.locator(".el-select-dropdown__item:has-text('管理员')")
                        if option_employee.count() > 0:
                            log_pass("角色选项'普通员工'可见", step=2)
                            verifications["role_employee"] = True
                        else:
                            log_fail("角色选项'普通员工'不可见", step=2)
                            verifications["role_employee"] = False
                        if option_admin.count() > 0:
                            log_pass("角色选项'管理员'可见", step=2)
                            verifications["role_admin"] = True
                        else:
                            log_fail("角色选项'管理员'不可见", step=2)
                            verifications["role_admin"] = False

                        # Select "普通员工"
                        if option_employee.count() > 0:
                            option_employee.first.click()
                            page.wait_for_timeout(500)

                        page.keyboard.press("Escape")
                        page.wait_for_timeout(300)
                    else:
                        log_fail("角色选择框不可见", step=2)
                        verifications["role_select"] = False

                    # Verify submit button
                    submit_btn = dialog.locator("button:has-text('确定')")
                    if submit_btn.count() > 0:
                        log_pass("'确定'按钮可见", step=3)
                        verifications["submit_btn"] = True
                    else:
                        log_fail("'确定'按钮不可见", step=3)
                        verifications["submit_btn"] = False

                    ss.capture("CHECKPOINT", step=3, action="add_member_form")

                    # Close without submitting
                    cancel_btn = dialog.locator("button:has-text('取消')")
                    if cancel_btn.count() > 0:
                        cancel_btn.first.click()
                        page.wait_for_timeout(500)
                else:
                    log_fail("新增成员弹窗未打开", step=1)
                    verifications["dialog_open"] = False
            else:
                log_warn("无展开行或添加成员按钮不可见", step=1)
                verifications["dialog_open"] = None
        else:
            log_warn("租户表格无数据,无法测试新增成员", step=1)
            verifications["dialog_open"] = None

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
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


def tc_e2e_067(page, tokens):
    """TC-E2E-067: 禁用/启用 - toggle tenant status"""
    global _logger
    case_id = "TC-E2E-067"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "禁用启用", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/tenant")
        log_info("=== 禁用/启用租户验证 ===")

        # Look for toggle buttons in the table (操作 column)
        # Tenant.vue shows "停用" or "启用" buttons depending on is_active status
        table_rows = page.locator(".tenant-page .el-table__body-wrapper .el-table__row")
        if table_rows.count() > 0:
            # Check for any toggle button (停用 or 启用)
            disable_btn = page.locator("button:has-text('停用')").first
            enable_btn = page.locator("button:has-text('启用')").first

            target_btn = None
            btn_text = ""
            if disable_btn.is_visible():
                target_btn = disable_btn
                btn_text = "停用"
            elif enable_btn.is_visible():
                target_btn = enable_btn
                btn_text = "启用"

            if target_btn:
                log_pass(f"找到'{btn_text}'按钮", step=1)
                verifications["toggle_btn"] = True

                # Click the toggle button
                target_btn.click()
                page.wait_for_timeout(1000)

                # Expect ElMessageBox.confirm dialog
                msgbox = page.locator(".el-message-box, .el-overlay:visible .el-message-box__wrapper")
                if msgbox.count() > 0:
                    log_pass(f"确认弹窗已出现(操作: {btn_text})", step=2)
                    verifications["confirm_dialog"] = True

                    # Verify confirm dialog content
                    msgbox_content = page.locator(".el-message-box__message")
                    if msgbox_content.count() > 0:
                        content_text = msgbox_content.first.inner_text()
                        log_pass(f"确认内容: '{content_text}'", step=2)

                    # Verify confirm/cancel buttons in message box
                    confirm_btn = page.locator(".el-message-box__btns button:has-text('确定')")
                    cancel_btn = page.locator(".el-message-box__btns button:has-text('取消')")
                    if confirm_btn.count() > 0:
                        log_pass("'确定'按钮可见", step=3)
                        verifications["confirm_btn"] = True
                    else:
                        log_fail("'确定'按钮不可见", step=3)
                        verifications["confirm_btn"] = False
                    if cancel_btn.count() > 0:
                        log_pass("'取消'按钮可见", step=3)
                        verifications["cancel_btn"] = True

                    ss.capture("CHECKPOINT", step=3, action=f"toggle_{btn_text}")

                    # Click cancel to NOT actually change status
                    if cancel_btn.count() > 0:
                        cancel_btn.first.click()
                        page.wait_for_timeout(500)
                        log_pass("已取消操作,状态未变更", step=3)
                else:
                    log_fail("确认弹窗未出现", step=2)
                    verifications["confirm_dialog"] = False
                    ss.save_dom_snapshot(step=2, tag="no_confirm")
            else:
                log_warn("表格有行但无停用/启用按钮", step=1)
                verifications["toggle_btn"] = False
        else:
            log_warn("租户表格无数据,无法测试禁用/启用", step=1)
            verifications["toggle_btn"] = None  # N/A

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
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
# Report
# ============================================================
def _generate_report(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 校链通 平台管理模块 E2E 测试报告", "",
        "| 项目 | 内容 |",
        "|------|------|",
        f"| 测试模块 | 第12~14章 平台管理模块 (L2 E2E) |",
        f"| 测试日期 | {now} |",
        f"| 用例数量 | {len(results)} |",
        "",
        "## 测试结果汇总", "",
        "| 用例ID | 用例名称 | 结果 | 置信度 |",
        "|--------|----------|------|--------|",
    ]
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
    print("校链通(XiaoLianTong) - 第12~14章 平台管理模块 L2 E2E 测试")
    print(f"目标地址: {BASE_URL}")
    print(f"截图目录: {SCREENSHOT_DIR}")
    print("=" * 70)

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Get admin auth tokens
    print("获取平台管理员Token...")
    token_data = get_admin_tokens()
    if not token_data:
        print("获取Token失败: 所有凭据均无法登录")
        return
    print(f"  access_token: {token_data.get('access_token', '')[:20]}...")
    print(f"  user_id: {token_data.get('user_id', 'N/A')}")
    print(f"  role_code: {token_data.get('role_code', 'N/A')}")

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
            ("TC-E2E-057: 侧边栏结构", tc_e2e_057),
            ("TC-E2E-058: 统计卡片", tc_e2e_058),
            ("TC-E2E-059: 趋势图", tc_e2e_059),
            ("TC-E2E-060: 审核列表", tc_e2e_060),
            ("TC-E2E-061: Tab切换", tc_e2e_061),
            ("TC-E2E-062: 审核通过", tc_e2e_062),
            ("TC-E2E-063: 审核驳回", tc_e2e_063),
            ("TC-E2E-064: 租户列表", tc_e2e_064),
            ("TC-E2E-065: 成员管理弹窗", tc_e2e_065),
            ("TC-E2E-066: 新增成员", tc_e2e_066),
            ("TC-E2E-067: 禁用/启用", tc_e2e_067),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page, token_data)
            all_results.append(r)

        browser.close()

    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch12_14.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 70)
    print("测试执行完成")
    print("=" * 70)
    print(f"\n--- 结果汇总 ---")
    for r in all_results:
        print(f"  {r['case_id']} {r['name']}: {r['status']} (置信度 {r.get('confidence', 'N/A')})")

    pass_count = sum(1 for r in all_results if r["status"] == "PASS")
    print(f"\n通过率: {pass_count}/{len(all_results)} ({pass_count/len(all_results)*100:.0f}%)")
    print(f"截图目录: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    main()
