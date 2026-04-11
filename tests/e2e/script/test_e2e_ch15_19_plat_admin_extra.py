"""
校链通(XiaoLianTong) - 第15~19章 平台管理扩展模块 L2 E2E 测试
覆盖: 商机内容管理、动态内容管理、基础数据字典、权限管理、系统设置
测试用例: TC-E2E-068 ~ TC-E2E-074

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
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch15_19_plat_admin_extra")
SCREENSHOT_DIR = os.path.join(CAPTURES_DIR, datetime.now().strftime("%Y-%m-%d_%H%M%S"))
VIEWPORT = {"width": 1280, "height": 900}
DEFAULT_TIMEOUT = 30000
ADMIN_NAV_WAIT = 4000


def get_admin_tokens():
    import urllib.request
    credentials = [("13800000001", "Admin123!"), ("admin", "admin")]
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


def inject_admin_login(page, token_data):
    user_info = {"id": token_data.get("user_id", 1), "phone": "13800000001",
                 "role_code": "super_admin", "enterprise_id": None}
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


def goto_admin_page(page, tokens, path="/plat-admin/dashboard"):
    inject_admin_login(page, tokens)
    page.goto(f"{BASE_URL}{path}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(ADMIN_NAV_WAIT)


# ============================================================
# Test Cases
# ============================================================

def tc_e2e_068(page, tokens):
    """TC-E2E-068: 商机内容管理页面 - filter bar + table columns"""
    global _logger
    case_id = "TC-E2E-068"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "商机内容管理页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/opportunity-manage")
        log_info("=== 商机内容管理页面验证 ===")

        # Card header
        card_header = page.locator(".el-card__header:has-text('商机内容管理')")
        if card_header.count() > 0:
            log_pass("'商机内容管理'卡片标题可见", step=1)
            verifications["card_title"] = True
        else:
            log_fail("'商机内容管理'卡片标题不可见", step=1)
            verifications["card_title"] = False

        # Filter bar
        filter_bar = page.locator(".filter-bar")
        if filter_bar.count() > 0:
            log_pass("筛选栏可见", step=1)
            verifications["filter_bar"] = True
        else:
            log_fail("筛选栏不可见", step=1)
            verifications["filter_bar"] = False

        # Type select
        selects = page.locator(".filter-bar .el-select")
        if selects.count() >= 2:
            log_pass(f"筛选下拉框: {selects.count()}个(期望2: 类型+状态)", step=1)
            verifications["filter_selects"] = True
        else:
            log_fail(f"筛选下拉框不足: {selects.count()}个", step=1)
            verifications["filter_selects"] = False

        # Table
        table = page.locator(".opportunity-manage-page .el-table")
        if table.count() > 0:
            log_pass("商机表格可见", step=2)
            verifications["table"] = True
        else:
            log_fail("商机表格不可见", step=2)
            verifications["table"] = False

        # Column headers
        expected_columns = ["标题", "所属企业", "类型", "状态", "浏览量", "创建时间", "操作"]
        for col_name in expected_columns:
            col_header = page.locator(f".el-table__header th:has-text('{col_name}')")
            if col_header.count() > 0:
                log_pass(f"列'{col_name}'存在", step=2)
                verifications[f"col_{col_name}"] = True
            else:
                log_fail(f"列'{col_name}'未找到", step=2)
                verifications[f"col_{col_name}"] = False

        ss.capture("CHECKPOINT", step=2, action="opp_manage_verified")

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


def tc_e2e_069(page, tokens):
    """TC-E2E-069: 商机查看详情 - drawer with detail info"""
    global _logger
    case_id = "TC-E2E-069"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "商机查看详情", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/opportunity-manage")
        log_info("=== 商机查看详情验证 ===")

        # Click "查看" button
        view_btn = page.locator("button:has-text('查看')").first
        if view_btn.is_visible():
            view_btn.click()
            page.wait_for_timeout(2000)

            # Verify drawer
            drawer = page.locator(".el-drawer:visible")
            if drawer.count() > 0:
                log_pass("商机详情抽屉已打开", step=1)
                verifications["drawer_open"] = True

                # Verify drawer title
                drawer_title = drawer.locator(".el-drawer__title")
                if drawer_title.count() > 0:
                    title_text = drawer_title.first.inner_text()
                    log_pass(f"抽屉标题: '{title_text}'", step=1)

                # Verify descriptions labels (Element Plus uses BEM: .el-descriptions__label)
                expected_labels = ["标题", "所属企业", "类型", "状态", "行业", "地区", "浏览量", "创建时间", "详情描述"]
                found_labels = 0
                for label in expected_labels:
                    label_el = drawer.locator(f".el-descriptions__label:has-text('{label}')")
                    if label_el.count() > 0:
                        log_pass(f"字段'{label}'可见", step=2)
                        verifications[f"field_{label}"] = True
                        found_labels += 1
                    else:
                        log_fail(f"字段'{label}'未找到", step=2)
                        verifications[f"field_{label}"] = False
                verifications["desc_items"] = found_labels >= 5

                ss.capture("CHECKPOINT", step=2, action="opp_detail_drawer")

                # Close drawer
                close_btn = drawer.locator(".el-drawer__close-btn")
                if close_btn.count() > 0:
                    close_btn.first.click()
                    page.wait_for_timeout(500)
            else:
                log_fail("商机详情抽屉未打开", step=1)
                verifications["drawer_open"] = False
        else:
            log_warn("无商机数据,无法测试详情", step=1)
            verifications["drawer_open"] = None

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


def tc_e2e_070(page, tokens):
    """TC-E2E-070: 动态内容管理页面 - filter + table"""
    global _logger
    case_id = "TC-E2E-070"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "动态内容管理页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/feed-manage")
        log_info("=== 动态内容管理页面验证 ===")

        # Card header
        card_header = page.locator(".el-card__header:has-text('动态内容管理')")
        if card_header.count() > 0:
            log_pass("'动态内容管理'卡片标题可见", step=1)
            verifications["card_title"] = True
        else:
            log_fail("'动态内容管理'卡片标题不可见", step=1)
            verifications["card_title"] = False

        # Filter bar
        filter_bar = page.locator(".filter-bar")
        if filter_bar.count() > 0:
            log_pass("筛选栏可见", step=1)
            verifications["filter_bar"] = True
        else:
            log_fail("筛选栏不可见", step=1)
            verifications["filter_bar"] = False

        # Status select
        status_select = page.locator(".filter-bar .el-select")
        if status_select.count() >= 1:
            log_pass("状态下拉筛选可见", step=1)
            verifications["status_select"] = True
        else:
            log_fail("状态下拉筛选不可见", step=1)
            verifications["status_select"] = False

        # Table
        table = page.locator(".feed-manage-page .el-table")
        if table.count() > 0:
            log_pass("动态表格可见", step=2)
            verifications["table"] = True
        else:
            log_fail("动态表格不可见", step=2)
            verifications["table"] = False

        # Column headers
        expected_columns = ["内容", "发布人", "所属企业", "状态", "发布时间", "操作"]
        for col_name in expected_columns:
            col_header = page.locator(f".el-table__header th:has-text('{col_name}')")
            if col_header.count() > 0:
                log_pass(f"列'{col_name}'存在", step=2)
                verifications[f"col_{col_name}"] = True
            else:
                log_fail(f"列'{col_name}'未找到", step=2)
                verifications[f"col_{col_name}"] = False

        ss.capture("CHECKPOINT", step=2, action="feed_manage_verified")

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


def tc_e2e_071(page, tokens):
    """TC-E2E-071: 动态查看详情 - dialog with detail info"""
    global _logger
    case_id = "TC-E2E-071"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "动态查看详情", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/feed-manage")
        log_info("=== 动态查看详情验证 ===")

        # Click "查看详情" button
        view_btn = page.locator("button:has-text('查看详情')").first
        if view_btn.is_visible():
            view_btn.click()
            page.wait_for_timeout(1500)

            dialog = page.locator(".el-dialog:visible")
            if dialog.count() > 0:
                log_pass("动态详情弹窗已打开", step=1)
                verifications["dialog_open"] = True

                # Verify dialog title
                dialog_title = dialog.locator(".el-dialog__title")
                if dialog_title.count() > 0:
                    title_text = dialog_title.first.inner_text()
                    log_pass(f"弹窗标题: '{title_text}'", step=1)

                # Verify descriptions labels (Element Plus BEM naming)
                desc_labels = dialog.locator(".el-descriptions__label")
                if desc_labels.count() > 0:
                    log_pass(f"描述标签数量: {desc_labels.count()}", step=2)
                    verifications["desc_items"] = True
                else:
                    log_fail("描述标签不可见", step=2)
                    verifications["desc_items"] = False

                # Check key fields
                expected_labels = ["发布人", "所属企业", "状态", "发布时间", "动态内容"]
                for label in expected_labels:
                    label_el = dialog.locator(f".el-descriptions__label:has-text('{label}')")
                    if label_el.count() > 0:
                        log_pass(f"字段'{label}'可见", step=2)
                        verifications[f"field_{label}"] = True
                    else:
                        log_fail(f"字段'{label}'未找到", step=2)
                        verifications[f"field_{label}"] = False

                ss.capture("CHECKPOINT", step=2, action="feed_detail_dialog")

                # Close dialog
                close_btn = dialog.locator(".el-dialog__headerbtn")
                if close_btn.count() > 0:
                    close_btn.first.click()
                    page.wait_for_timeout(500)
            else:
                log_fail("动态详情弹窗未打开", step=1)
                verifications["dialog_open"] = False
        else:
            log_warn("无动态数据,无法测试详情", step=1)
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


def tc_e2e_072(page, tokens):
    """TC-E2E-072: 基础数据页面 - tabs + tree table"""
    global _logger
    case_id = "TC-E2E-072"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "基础数据页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/master-data")
        log_info("=== 基础数据页面验证 ===")

        # Card header
        card_header = page.locator(".el-card__header:has-text('基础数据管理')")
        if card_header.count() > 0:
            log_pass("'基础数据管理'卡片标题可见", step=1)
            verifications["card_title"] = True
        else:
            log_fail("'基础数据管理'卡片标题不可见", step=1)
            verifications["card_title"] = False

        # Verify "新增根节点" button
        add_root_btn = page.locator("button:has-text('新增根节点')")
        if add_root_btn.count() > 0:
            log_pass("'新增根节点'按钮可见", step=1)
            verifications["add_root_btn"] = True
        else:
            log_fail("'新增根节点'按钮不可见", step=1)
            verifications["add_root_btn"] = False

        # Verify tabs (from MasterData.vue: 行业, 地区, 分类)
        expected_tabs = ["行业", "地区", "分类"]
        tab_items = page.locator(".el-tabs__item")
        if tab_items.count() >= 3:
            log_pass(f"Tab数量: {tab_items.count()}", step=1)
            verifications["tab_count"] = True
        else:
            log_fail(f"Tab数量不足: {tab_items.count()}", step=1)
            verifications["tab_count"] = False

        for tab_name in expected_tabs:
            tab = page.locator(f".el-tabs__item:has-text('{tab_name}')")
            if tab.count() > 0:
                log_pass(f"Tab '{tab_name}' 可见", step=1)
                verifications[f"tab_{tab_name}"] = True
            else:
                log_fail(f"Tab '{tab_name}' 不可见", step=1)
                verifications[f"tab_{tab_name}"] = False

        # Verify table
        table = page.locator(".master-data-page .el-table")
        if table.count() > 0:
            log_pass("数据表格可见", step=2)
            verifications["table"] = True
        else:
            log_fail("数据表格不可见", step=2)
            verifications["table"] = False

        # Verify table column headers
        expected_columns = ["名称", "编码", "状态", "操作"]
        for col_name in expected_columns:
            col_header = page.locator(f".el-table__header th:has-text('{col_name}')")
            if col_header.count() > 0:
                log_pass(f"列'{col_name}'存在", step=2)
                verifications[f"col_{col_name}"] = True
            else:
                log_fail(f"列'{col_name}'未找到", step=2)
                verifications[f"col_{col_name}"] = False

        # Verify action buttons (添加子项, 编辑, 删除) in table rows
        table_rows = page.locator(".master-data-page .el-table__body-wrapper .el-table__row")
        if table_rows.count() > 0:
            add_child_btn = table_rows.first.locator("button:has-text('添加子项')")
            edit_btn = table_rows.first.locator("button:has-text('编辑')")
            delete_btn = table_rows.first.locator("button:has-text('删除')")
            if add_child_btn.count() > 0:
                log_pass("'添加子项'按钮可见", step=3)
                verifications["add_child_btn"] = True
            if edit_btn.count() > 0:
                log_pass("'编辑'按钮可见", step=3)
                verifications["edit_btn"] = True
            if delete_btn.count() > 0:
                log_pass("'删除'按钮可见", step=3)
                verifications["delete_btn"] = True

        ss.capture("CHECKPOINT", step=3, action="master_data_verified")

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


def tc_e2e_073(page, tokens):
    """TC-E2E-073: 权限管理页面 - role cards"""
    global _logger
    case_id = "TC-E2E-073"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "权限管理页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/rbac")
        log_info("=== 权限管理页面验证 ===")

        # Card header
        card_header = page.locator(".el-card__header:has-text('角色与权限')")
        if card_header.count() > 0:
            log_pass("'角色与权限'卡片标题可见", step=1)
            verifications["card_title"] = True
        else:
            log_fail("'角色与权限'卡片标题不可见", step=1)
            verifications["card_title"] = False

        # Verify role cards
        role_cards = page.locator(".role-card")
        card_count = role_cards.count()
        if card_count > 0:
            log_pass(f"角色卡片数量: {card_count}", step=2)
            verifications["role_cards"] = True

            # Check each card has role name and code
            for i in range(min(card_count, 5)):
                card = role_cards.nth(i)
                role_name = card.locator(".role-name")
                role_tag = card.locator(".el-tag")
                perm_section = card.locator(".permission-section")
                if role_name.count() > 0:
                    name_text = role_name.first.inner_text()
                    log_pass(f"角色[{i}]: '{name_text}'", step=2)
                    verifications[f"role_{i}_name"] = True
                if perm_section.count() > 0:
                    log_pass(f"角色[{i}]: 权限列表区域可见", step=2)
                    verifications[f"role_{i}_perms"] = True
        else:
            log_fail("无角色卡片", step=2)
            verifications["role_cards"] = False

        ss.capture("CHECKPOINT", step=2, action="rbac_verified")

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


def tc_e2e_074(page, tokens):
    """TC-E2E-074: 系统设置页面 - descriptions + edit"""
    global _logger
    case_id = "TC-E2E-074"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "系统设置页面", "status": "FAIL", "details": []}
    verifications = {}

    try:
        goto_admin_page(page, tokens, "/plat-admin/settings")
        log_info("=== 系统设置页面验证 ===")

        # Card header
        card_header = page.locator(".el-card__header:has-text('系统设置')")
        if card_header.count() > 0:
            log_pass("'系统设置'卡片标题可见", step=1)
            verifications["card_title"] = True
        else:
            log_fail("'系统设置'卡片标题不可见", step=1)
            verifications["card_title"] = False

        # Verify "编辑" button
        edit_btn = page.locator("button:has-text('编辑')")
        if edit_btn.count() > 0:
            log_pass("'编辑'按钮可见", step=1)
            verifications["edit_btn"] = True
        else:
            log_fail("'编辑'按钮不可见", step=1)
            verifications["edit_btn"] = False

        # Verify descriptions
        desc_items = page.locator(".el-descriptions-item")
        if desc_items.count() > 0:
            log_pass(f"设置描述项: {desc_items.count()}个", step=2)
            verifications["desc_items"] = True
        else:
            log_fail("无设置描述项", step=2)
            verifications["desc_items"] = False

        ss.capture("CHECKPOINT", step=2, action="settings_view_mode")

        # Test edit mode
        if edit_btn.count() > 0:
            edit_btn.first.click()
            page.wait_for_timeout(1000)

            # Verify edit controls appeared
            cancel_btn = page.locator("button:has-text('取消')")
            save_btn = page.locator("button:has-text('保存')")
            if cancel_btn.count() > 0 and save_btn.count() > 0:
                log_pass("编辑模式: 取消+保存按钮可见", step=3)
                verifications["edit_mode"] = True
            else:
                log_fail("编辑模式按钮不可见", step=3)
                verifications["edit_mode"] = False

            ss.capture("CHECKPOINT", step=3, action="settings_edit_mode")

            # Cancel edit
            if cancel_btn.count() > 0:
                cancel_btn.first.click()
                page.wait_for_timeout(500)

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
        "# 校链通 平台管理扩展模块 E2E 测试报告", "",
        "| 项目 | 内容 |",
        "|------|------|",
        f"| 测试模块 | 第15~19章 平台管理扩展模块 (L2 E2E) |",
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
    print("校链通 - 第15~19章 平台管理扩展模块 L2 E2E 测试")
    print(f"目标地址: {BASE_URL}")
    print(f"截图目录: {SCREENSHOT_DIR}")
    print("=" * 70)

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print("获取平台管理员Token...")
    token_data = get_admin_tokens()
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
            ("TC-E2E-068: 商机内容管理页面", tc_e2e_068),
            ("TC-E2E-069: 商机查看详情", tc_e2e_069),
            ("TC-E2E-070: 动态内容管理页面", tc_e2e_070),
            ("TC-E2E-071: 动态查看详情", tc_e2e_071),
            ("TC-E2E-072: 基础数据页面", tc_e2e_072),
            ("TC-E2E-073: 权限管理页面", tc_e2e_073),
            ("TC-E2E-074: 系统设置页面", tc_e2e_074),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page, token_data)
            all_results.append(r)

        browser.close()

    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch15_19.md")
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
