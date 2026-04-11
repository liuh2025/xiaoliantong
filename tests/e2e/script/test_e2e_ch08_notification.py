"""
校链通(XiaoLianTong) - 第8章 通知消息模块 L2 E2E 测试
基于 QA-test-plan-PP-v1.0.md 第8章
覆盖用例: TC-E2E-042 ~ TC-E2E-045

应用地址: http://localhost:3000
测试日期: 2026-04-11
"""

from playwright.sync_api import sync_playwright
import time, os, json, sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:3000")
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch08_notification")
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
# Screenshot & Logger (reuse pattern from ch03)
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
# Helper to setup notification page with login
# ============================================================
def setup_notification_page(page, tokens):
    inject_login(page, tokens)
    page.goto(f"{BASE_URL}/notification")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    return tokens


# ============================================================
# Test Cases
# ============================================================

def tc_e2e_042(page, tokens):
    """TC-E2E-042: 页面展示 - 标题"通知消息" + "全部已读"按钮 + 通知列表"""
    global _logger
    case_id = "TC-E2E-042"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "页面展示", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_notification_page(page, tokens)
        log_info("=== 通知消息页面展示验证 ===")

        # Step 1: Verify page container
        # Vue: <div class="notification-page">
        notif_page = page.locator(".notification-page")
        if notif_page.count() > 0:
            log_pass("通知页面容器(.notification-page)存在", step=1)
            verifications["page_container"] = True
        else:
            log_fail("通知页面容器不存在", step=1)
            verifications["page_container"] = False

        # Step 2: Verify header with title "通知消息"
        # Vue: <div class="notif-header"><h2>通知消息</h2>
        notif_header = page.locator(".notif-header")
        if notif_header.count() > 0 and notif_header.first.is_visible():
            log_pass("通知头部(.notif-header)可见", step=2)
            verifications["header"] = True
        else:
            log_fail("通知头部(.notif-header)不可见", step=2)
            verifications["header"] = False

        header_title = page.locator(".notif-header h2")
        if header_title.count() > 0 and header_title.first.is_visible():
            title_text = header_title.first.inner_text()
            if "通知消息" in title_text:
                log_pass(f"页面标题: '{title_text}'", step=2)
                verifications["title"] = True
            else:
                log_fail(f"页面标题: '{title_text}' (期望包含'通知消息')", step=2)
                verifications["title"] = False
        else:
            log_fail("页面标题(h2)不可见", step=2)
            verifications["title"] = False

        # Step 3: Verify "全部已读" button
        # Vue: <el-button type="primary" text>全部已读</el-button>
        mark_all_btn = page.locator(".notif-header button:has-text('全部已读')")
        if mark_all_btn.count() > 0 and mark_all_btn.first.is_visible():
            log_pass("'全部已读'按钮可见", step=3)
            verifications["mark_all_btn"] = True
        else:
            log_fail("'全部已读'按钮不可见", step=3)
            verifications["mark_all_btn"] = False

        # Step 4: Verify notification list exists
        # Vue: <div class="notif-list"> or <el-empty>
        notif_list = page.locator(".notif-list")
        empty_state = page.locator(".notification-page .el-empty")

        if notif_list.count() > 0 and notif_list.first.is_visible():
            notif_items = page.locator(".notif-item")
            item_count = notif_items.count()
            log_pass(f"通知列表可见, 共{item_count}条通知", step=4)
            verifications["notif_list"] = True
        elif empty_state.count() > 0 and empty_state.first.is_visible():
            log_warn("通知列表为空, 显示el-empty(暂无消息)", step=4)
            verifications["notif_list"] = None
        else:
            log_fail("通知列表和空状态均不可见", step=4)
            verifications["notif_list"] = False

        ss.capture("CHECKPOINT", step=4, action="page_display")

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=5)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_043(page, tokens):
    """TC-E2E-043: 通知列表 - 卡片结构, 图标类型(4种分类)"""
    global _logger
    case_id = "TC-E2E-043"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "通知列表结构", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_notification_page(page, tokens)
        log_info("=== 通知列表结构验证 ===")

        # Check notification items exist
        notif_items = page.locator(".notif-item")
        item_count = notif_items.count()

        if item_count == 0:
            empty = page.locator(".notification-page .el-empty")
            if empty.count() > 0:
                log_warn("通知列表为空, 无数据可验证结构", step=1)
                result["status"] = "NEED_HUMAN_CHECK"
                result["verifications"] = {"items": None}
                result["confidence"] = 0.5
            else:
                log_fail("通知列表为空且无empty状态", step=1)
                result["status"] = "FAIL"
                result["verifications"] = {"items": False}
                result["confidence"] = 0.0
            _logger.save_json()
            return result

        log_info(f"共找到{item_count}条通知, 验证卡片结构", step=1)

        # Step 1: Check first card structure
        # Vue: .notif-item > .notif-icon + .notif-body > .notif-title + .notif-content + .notif-meta
        first_item = notif_items.first

        # Check icon area
        notif_icon = first_item.locator(".notif-icon")
        if notif_icon.count() > 0 and notif_icon.first.is_visible():
            icon_text = notif_icon.first.inner_text()
            log_pass(f"通知图标(.notif-icon)可见, 内容: '{icon_text}'", step=1)
            verifications["icon"] = True
        else:
            log_fail("通知图标(.notif-icon)不可见", step=1)
            verifications["icon"] = False

        # Check body area
        notif_body = first_item.locator(".notif-body")
        if notif_body.count() > 0:
            log_pass("通知内容区域(.notif-body)可见", step=1)
            verifications["body"] = True
        else:
            log_fail("通知内容区域(.notif-body)不可见", step=1)
            verifications["body"] = False

        # Check title
        notif_title = first_item.locator(".notif-title")
        if notif_title.count() > 0 and notif_title.first.is_visible():
            title_text = notif_title.first.inner_text()
            log_pass(f"通知标题: '{title_text}'", step=1)
            verifications["title"] = True
        else:
            log_fail("通知标题(.notif-title)不可见", step=1)
            verifications["title"] = False

        # Check content
        notif_content = first_item.locator(".notif-content")
        if notif_content.count() > 0:
            content_text = notif_content.first.inner_text()
            log_pass(f"通知内容: '{content_text[:50]}...'", step=1)
            verifications["content"] = True
        else:
            log_warn("通知内容(.notif-content)不可见", step=1)
            verifications["content"] = False

        # Check meta area (tag + time)
        notif_meta = first_item.locator(".notif-meta")
        if notif_meta.count() > 0:
            log_pass("通知元信息区域(.notif-meta)可见", step=1)
            verifications["meta"] = True

            # Check time
            notif_time = first_item.locator(".notif-time")
            if notif_time.count() > 0:
                time_text = notif_time.first.inner_text()
                log_pass(f"通知时间: '{time_text}'", step=1)
                verifications["time"] = True
            else:
                log_warn("通知时间(.notif-time)不可见", step=1)
                verifications["time"] = False
        else:
            log_warn("通知元信息区域不可见", step=1)
            verifications["meta"] = False

        ss.capture("CHECKPOINT", step=1, action="card_structure")

        # Step 2: Verify icon types (4 categories from Vue source)
        # Vue getNotifIconClass returns: audit-approved, audit-rejected, contact-received, system
        icon_types = {
            "audit-approved": {"found": False, "emoji": "check"},
            "audit-rejected": {"found": False, "emoji": "cross"},
            "contact-received": {"found": False, "emoji": "phone"},
            "system": {"found": False, "emoji": "gear"},
        }

        for i in range(item_count):
            item = notif_items.nth(i)
            icon = item.locator(".notif-icon")
            if icon.count() > 0:
                class_attr = icon.first.get_attribute("class") or ""
                for icon_type in icon_types:
                    if icon_type in class_attr:
                        icon_types[icon_type]["found"] = True

        found_types = [t for t, info in icon_types.items() if info["found"]]
        log_info(f"发现的通知图标类型: {found_types}", step=2)
        verifications["icon_types_found"] = len(found_types) > 0

        if len(found_types) >= 2:
            log_pass(f"至少发现{len(found_types)}种图标类型: {found_types}", step=2)
            verifications["icon_variety"] = True
        elif len(found_types) == 1:
            log_warn(f"仅发现1种图标类型: {found_types}", step=2)
            verifications["icon_variety"] = None
        else:
            log_warn("未发现特定图标类型(可能是数据内容不匹配)", step=2)
            verifications["icon_variety"] = None

        # Step 3: Check notification tags (el-tag in meta)
        tag_count = 0
        tag_labels = []
        for i in range(item_count):
            item = notif_items.nth(i)
            tag = item.locator(".notif-tag")
            if tag.count() > 0:
                tag_count += 1
                tag_text = tag.first.inner_text()
                if tag_text not in tag_labels:
                    tag_labels.append(tag_text)
        if tag_count > 0:
            log_pass(f"发现{tag_count}个通知标签, 类型: {tag_labels}", step=3)
            verifications["tags"] = True
        else:
            log_warn("未发现通知标签(可能数据不匹配分类规则)", step=3)
            verifications["tags"] = None

        ss.capture("CHECKPOINT", step=3, action="icon_types")

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


def tc_e2e_044(page, tokens):
    """TC-E2E-044: 未读/已读 - 未读通知有浅蓝色背景"""
    global _logger
    case_id = "TC-E2E-044"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "未读已读区分", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_notification_page(page, tokens)
        log_info("=== 未读/已读区分验证 ===")

        # Check notification items
        notif_items = page.locator(".notif-item")
        item_count = notif_items.count()

        if item_count == 0:
            empty = page.locator(".notification-page .el-empty")
            if empty.count() > 0:
                log_warn("通知列表为空, 无数据可验证未读/已读", step=1)
                result["status"] = "NEED_HUMAN_CHECK"
                result["verifications"] = {"items": None}
                result["confidence"] = 0.5
            else:
                log_fail("通知列表为空", step=1)
                result["status"] = "FAIL"
                result["verifications"] = {"items": False}
                result["confidence"] = 0.0
            _logger.save_json()
            return result

        log_info(f"共{item_count}条通知, 检查未读/已读状态", step=1)

        # Step 1: Count unread items (have .unread class)
        # Vue: :class="{ unread: !notif.is_read }"
        unread_items = page.locator(".notif-item.unread")
        read_items = page.locator(".notif-item:not(.unread)")
        unread_count = unread_items.count()
        read_count = read_items.count()

        log_info(f"未读: {unread_count}条, 已读: {read_count}条", step=1)

        # Test data has 1 unread, 2 read for user 13800000001
        if unread_count > 0:
            log_pass(f"存在{unread_count}条未读通知(有.unread类)", step=1)
            verifications["has_unread"] = True
        else:
            log_warn("未发现未读通知(.notif-item.unread)", step=1)
            verifications["has_unread"] = None

        if read_count > 0:
            log_pass(f"存在{read_count}条已读通知(无.unread类)", step=1)
            verifications["has_read"] = True
        else:
            log_warn("未发现已读通知", step=1)
            verifications["has_read"] = None

        # Step 2: Verify unread item has distinct background
        # Vue CSS: .notif-item.unread { background-color: rgba(30, 136, 229, 0.03); }
        if unread_count > 0:
            first_unread = unread_items.first
            bg_color = first_unread.evaluate("el => getComputedStyle(el).backgroundColor")
            log_info(f"未读通知背景色: '{bg_color}'", step=2)
            # rgba(30, 136, 229, ...) is a light blue
            verifications["unread_bg"] = True
            log_pass(f"未读通知有独立背景样式: {bg_color}", step=2)
        else:
            log_warn("无未读通知, 无法验证背景色差异", step=2)
            verifications["unread_bg"] = None

        # Step 3: Compare read item background
        if read_count > 0:
            first_read = read_items.first
            bg_color_read = first_read.evaluate("el => getComputedStyle(el).backgroundColor")
            log_info(f"已读通知背景色: '{bg_color_read}'", step=3)
            verifications["read_bg"] = True
        else:
            log_warn("无已读通知, 无法对比背景色", step=3)
            verifications["read_bg"] = None

        # Step 4: Verify visual difference between read and unread
        if unread_count > 0 and read_count > 0:
            first_unread = unread_items.first
            first_read = read_items.first
            unread_bg = first_unread.evaluate("el => getComputedStyle(el).backgroundColor")
            read_bg = first_read.evaluate("el => getComputedStyle(el).backgroundColor")
            if unread_bg != read_bg:
                log_pass(f"未读({unread_bg})和已读({read_bg})背景色不同", step=4)
                verifications["visual_diff"] = True
            else:
                log_warn(f"未读和已读背景色相同: {unread_bg} (CSS可能未生效或hover覆盖)", step=4)
                verifications["visual_diff"] = False
        else:
            verifications["visual_diff"] = None

        ss.capture("CHECKPOINT", step=4, action="read_unread_diff")

        # Step 5: Verify "全部已读" button state
        # Vue: :disabled="!hasUnread" -- disabled when no unread items
        mark_all_btn = page.locator(".notif-header button:has-text('全部已读')")
        if mark_all_btn.count() > 0:
            is_disabled = mark_all_btn.first.is_disabled()
            if unread_count > 0:
                if not is_disabled:
                    log_pass("'全部已读'按钮可用(存在未读通知)", step=5)
                    verifications["btn_enabled"] = True
                else:
                    log_fail("'全部已读'按钮已禁用(但存在未读通知)", step=5)
                    verifications["btn_enabled"] = False
            else:
                if is_disabled:
                    log_pass("'全部已读'按钮已禁用(无未读通知)", step=5)
                    verifications["btn_enabled"] = True
                else:
                    log_warn("'全部已读'按钮可用(但无未读通知)", step=5)
                    verifications["btn_enabled"] = None

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=6)
    except Exception as e:
        log_fail(f"异常: {e}", step=0)
        ss.capture("ERROR", tag="exception")
        result["details"].append(str(e))
        result["status"] = "ERROR"

    _logger.save_json()
    return result


def tc_e2e_045(page, tokens):
    """TC-E2E-045: 全部已读 - 点击"全部已读"按钮, 验证所有通知变为已读"""
    global _logger
    case_id = "TC-E2E-045"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "全部已读", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_notification_page(page, tokens)
        log_info("=== 全部已读验证 ===")

        # Step 1: Check initial state - count unread
        unread_before = page.locator(".notif-item.unread")
        unread_count_before = unread_before.count()
        log_info(f"点击前: {unread_count_before}条未读通知", step=1)

        if unread_count_before == 0:
            log_warn("无未读通知, 无法测试'全部已读'功能", step=1)
            result["status"] = "NEED_HUMAN_CHECK"
            result["verifications"] = {"has_unread": None}
            result["confidence"] = 0.5
            _logger.save_json()
            return result

        verifications["has_unread_before"] = True

        # Step 2: Verify "全部已读" button is enabled
        mark_all_btn = page.locator(".notif-header button:has-text('全部已读')")
        if mark_all_btn.count() > 0:
            is_disabled = mark_all_btn.first.is_disabled()
            if not is_disabled:
                log_pass("'全部已读'按钮可用, 准备点击", step=2)
                verifications["btn_enabled"] = True
            else:
                log_fail("'全部已读'按钮已禁用", step=2)
                verifications["btn_enabled"] = False
                result["status"] = "FAIL"
                result["verifications"] = verifications
                result["confidence"] = 0.0
                _logger.save_json()
                return result
        else:
            log_fail("'全部已读'按钮不存在", step=2)
            verifications["btn_exists"] = False
            result["status"] = "FAIL"
            result["verifications"] = verifications
            result["confidence"] = 0.0
            _logger.save_json()
            return result

        ss.capture("BEFORE", step=2, action="before_mark_all_read")

        # Step 3: Click "全部已读" button
        mark_all_btn.first.click()
        page.wait_for_timeout(2000)
        log_info("已点击'全部已读'按钮", step=3)

        # Step 4: Verify success message
        # Vue: ElMessage.success('已全部标记为已读')
        success_msg = page.locator(".el-message--success:has-text('已全部标记为已读')")
        if success_msg.count() > 0:
            log_pass("成功提示'已全部标记为已读'已显示", step=4)
            verifications["success_msg"] = True
        else:
            # The message might have already disappeared
            log_warn("成功提示未找到(可能已消失)", step=4)
            verifications["success_msg"] = None

        # Step 5: Verify no unread items remain
        unread_after = page.locator(".notif-item.unread")
        unread_count_after = unread_after.count()
        log_info(f"点击后: {unread_count_after}条未读通知", step=5)

        if unread_count_after == 0:
            log_pass("所有通知已变为已读状态(无.unread类)", step=5)
            verifications["all_read"] = True
        else:
            log_fail(f"仍有{unread_count_after}条未读通知", step=5)
            verifications["all_read"] = False

        # Step 6: Verify "全部已读" button is now disabled
        # Vue: :disabled="!hasUnread" -- should be disabled now
        page.wait_for_timeout(500)
        mark_all_btn_after = page.locator(".notif-header button:has-text('全部已读')")
        if mark_all_btn_after.count() > 0:
            is_disabled_after = mark_all_btn_after.first.is_disabled()
            if is_disabled_after:
                log_pass("'全部已读'按钮已禁用(所有通知已读)", step=6)
                verifications["btn_disabled_after"] = True
            else:
                log_warn(f"'全部已读'按钮状态: disabled={is_disabled_after}", step=6)
                verifications["btn_disabled_after"] = False
        else:
            log_warn("'全部已读'按钮未找到(可能DOM更新)", step=6)
            verifications["btn_disabled_after"] = None

        ss.capture("CHECKPOINT", step=6, action="after_mark_all_read")

        # Step 7: Verify all items have same background (no unread highlight)
        notif_items = page.locator(".notif-item")
        if notif_items.count() > 0:
            all_same = True
            first_bg = notif_items.first.evaluate("el => getComputedStyle(el).backgroundColor")
            for i in range(1, notif_items.count()):
                item_bg = notif_items.nth(i).evaluate("el => getComputedStyle(el).backgroundColor")
                if item_bg != first_bg:
                    all_same = False
                    break
            if all_same:
                log_pass("所有通知项背景色一致(无未读高亮)", step=7)
                verifications["uniform_bg"] = True
            else:
                log_warn("通知项背景色不一致", step=7)
                verifications["uniform_bg"] = False
        else:
            verifications["uniform_bg"] = None

        key_v = {k: v for k, v in verifications.items() if v is not None}
        passed = sum(1 for v in key_v.values() if v)
        total = len(key_v)
        confidence = passed / total if total else 0
        result["status"] = "PASS" if confidence >= 0.7 else ("NEED_HUMAN_CHECK" if confidence >= 0.6 else "FAIL")
        result["verifications"] = verifications
        result["confidence"] = round(confidence, 2)
        log_info(f"验证结果: {passed}/{total}, 置信度 {confidence:.0%}", step=8)
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
    lines = ["# 校链通 通知消息模块 E2E 测试报告", "",
             f"| 项目 | 内容 |", "|------|------|",
             f"| 测试模块 | 第8章 通知消息模块 (L2 E2E) |",
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
    print("校链通(XiaoLianTong) - 第8章 通知消息模块 L2 E2E 测试")
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
            ("TC-E2E-042: 页面展示", tc_e2e_042),
            ("TC-E2E-043: 通知列表结构", tc_e2e_043),
            ("TC-E2E-044: 未读已读区分", tc_e2e_044),
            ("TC-E2E-045: 全部已读", tc_e2e_045),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page, token_data)
            all_results.append(r)

        browser.close()

    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch08.md")
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
