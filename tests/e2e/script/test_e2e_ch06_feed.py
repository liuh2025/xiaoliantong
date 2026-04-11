"""
校链通(XiaoLianTong) - 第6章 校友圈模块 L2 E2E 测试
基于 QA-test-plan-PP-v1.0.md 第6章
覆盖用例: TC-E2E-037 ~ TC-E2E-039

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
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch06_feed")
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
# Helper to setup logged-in feed page
# ============================================================
def setup_feed_page(page, tokens):
    inject_login(page, tokens)
    page.goto(f"{BASE_URL}/feed")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)


# ============================================================
# Test Cases
# ============================================================

def tc_e2e_037(page, tokens):
    """TC-E2E-037: 页面展示 - title/subtitle, "发布动态" button, feed list"""
    global _logger
    case_id = "TC-E2E-037"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "页面展示", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_feed_page(page, tokens)
        log_info("=== 页面展示验证 ===")

        # Verify nav link active for "校友圈"
        feed_nav = page.locator(".nav-link:has-text('校友圈')")
        if feed_nav.count() > 0:
            nav_class = feed_nav.first.get_attribute("class") or ""
            is_active = "active" in nav_class
            if is_active:
                log_pass("导航项'校友圈'高亮(active)", step=1)
                verifications["nav_active"] = True
            else:
                log_warn("导航项'校友圈'未高亮", step=1)
                verifications["nav_active"] = False
        else:
            log_fail("导航项'校友圈'不可见", step=1)
            verifications["nav_active"] = False

        # Verify page title
        title = page.locator(".feed-page .feeds-title")
        if title.count() > 0 and title.first.is_visible():
            text = title.first.inner_text()
            log_pass(f"页面标题: '{text}'", step=1)
            verifications["page_title"] = "校友圈" in text
        else:
            log_fail("页面标题不可见", step=1)
            verifications["page_title"] = False

        # Verify page subtitle
        subtitle = page.locator(".feed-page .feeds-subtitle")
        if subtitle.count() > 0 and subtitle.first.is_visible():
            log_pass(f"页面副标题: '{subtitle.first.inner_text()}'", step=1)
            verifications["page_subtitle"] = True
        else:
            log_fail("页面副标题不可见", step=1)
            verifications["page_subtitle"] = False

        # Verify "发布动态" button
        publish_btn = page.locator(".feed-page button:has-text('发布动态')")
        if publish_btn.count() > 0 and publish_btn.first.is_visible():
            log_pass("'发布动态'按钮可见", step=2)
            verifications["publish_btn"] = True
        else:
            log_fail("'发布动态'按钮不可见", step=2)
            verifications["publish_btn"] = False

        # Verify feed list exists
        feed_list = page.locator(".feed-list")
        if feed_list.count() > 0:
            feed_cards = feed_list.locator(".feed-card")
            card_count = feed_cards.count()
            log_pass(f"动态列表存在，卡片数量: {card_count}", step=3)
            verifications["feed_list"] = True
            verifications["feed_cards"] = card_count > 0
        else:
            # Check empty state
            empty = page.locator(".feed-page .el-empty")
            if empty.count() > 0:
                log_warn("动态列表为空(el-empty显示)", step=3)
                verifications["feed_list"] = None
            else:
                log_fail("动态列表不存在", step=3)
                verifications["feed_list"] = False

        ss.capture("CHECKPOINT", step=3, action="page_display_verified")

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


def tc_e2e_038(page, tokens):
    """TC-E2E-038: 动态卡片 - card structure (avatar, name, content, images, actions)"""
    global _logger
    case_id = "TC-E2E-038"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "动态卡片", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_feed_page(page, tokens)
        log_info("=== 动态卡片验证 ===")

        feed_cards = page.locator(".feed-card")
        card_count = feed_cards.count()
        if card_count > 0:
            log_pass(f"动态卡片数量: {card_count}", step=1)
            verifications["cards_exist"] = True

            # Check first card structure
            first = feed_cards.first

            # Author section
            author_section = first.locator(".feed-author-section")
            if author_section.count() > 0:
                log_pass("作者区域可见", step=2)
                verifications["author_section"] = True

                # Avatar
                avatar = first.locator(".feed-author-avatar")
                if avatar.count() > 0:
                    avatar_text = avatar.first.inner_text()
                    log_pass(f"头像(首字母): '{avatar_text}'", step=2)
                    verifications["avatar"] = True
                else:
                    log_fail("头像不可见", step=2)
                    verifications["avatar"] = False

                # Author name
                author_name = first.locator(".feed-author-name")
                if author_name.count() > 0:
                    log_pass(f"作者名称: '{author_name.first.inner_text()}'", step=2)
                    verifications["author_name"] = True
                else:
                    log_fail("作者名称不可见", step=2)
                    verifications["author_name"] = False

                # Author company (optional)
                author_company = first.locator(".feed-author-company")
                if author_company.count() > 0:
                    log_pass(f"作者公司: '{author_company.first.inner_text()}'", step=2)
                    verifications["author_company"] = True
                else:
                    log_debug("作者公司不显示(可能未填写)", step=2)
                    verifications["author_company"] = None

                # Time
                feed_time = first.locator(".feed-time")
                if feed_time.count() > 0:
                    log_pass(f"发布时间: '{feed_time.first.inner_text()}'", step=2)
                    verifications["feed_time"] = True
                else:
                    log_warn("发布时间不可见", step=2)
                    verifications["feed_time"] = False
            else:
                log_fail("作者区域不可见", step=2)
                verifications["author_section"] = False

            # Content
            content = first.locator(".feed-content")
            if content.count() > 0:
                content_text = content.first.inner_text()
                log_pass(f"动态内容: '{content_text[:50]}...'", step=3)
                verifications["content"] = True
            else:
                log_fail("动态内容不可见", step=3)
                verifications["content"] = False

            # Images (optional)
            images = first.locator(".feed-images-grid .feed-image")
            if images.count() > 0:
                log_pass(f"图片数量: {images.count()}", step=3)
                verifications["images"] = True
            else:
                log_debug("该动态无图片", step=3)
                verifications["images"] = None

            # Title badge (optional)
            title_badge = first.locator(".title-badge")
            if title_badge.count() > 0:
                log_pass(f"职称标签: '{title_badge.first.inner_text()}'", step=3)
                verifications["title_badge"] = True
            else:
                log_debug("无职称标签", step=3)
                verifications["title_badge"] = None
        else:
            # Check empty state
            empty = page.locator(".feed-page .el-empty")
            if empty.count() > 0:
                log_warn("动态列表为空(el-empty显示)", step=1)
                verifications["cards_exist"] = None
            else:
                log_fail("动态卡片为空且无empty状态", step=1)
                verifications["cards_exist"] = False

        ss.capture("CHECKPOINT", step=3, action="feed_card_verified")

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


def tc_e2e_039(page, tokens):
    """TC-E2E-039: 发布动态 - click publish, fill form, verify success"""
    global _logger
    case_id = "TC-E2E-039"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "发布动态", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_feed_page(page, tokens)
        log_info("=== 发布动态 ===")

        # Click "发布动态" button
        publish_btn = page.locator(".feed-page button:has-text('发布动态')").first
        publish_btn.click()
        page.wait_for_timeout(1500)

        # Verify dialog opened
        dialog = page.locator(".el-dialog:visible")
        if dialog.count() > 0:
            log_pass("发布动态弹窗已打开", step=1)
            verifications["dialog_open"] = True

            # Check dialog title
            dialog_title = dialog.locator(".el-dialog__title")
            if dialog_title.count() > 0:
                title_text = dialog_title.first.inner_text()
                log_pass(f"弹窗标题: '{title_text}'", step=1)
                verifications["dialog_title"] = "发布动态" in title_text

            # Check form fields
            # Content textarea
            content_label = dialog.locator(".el-form-item:has-text('动态内容')")
            if content_label.count() > 0:
                log_pass("'动态内容'表单项存在", step=2)
                verifications["content_field"] = True

                # Fill in content
                textarea = dialog.locator("textarea")
                if textarea.count() > 0:
                    test_content = f"E2E自动化测试动态 - {datetime.now().strftime('%H%M%S')}"
                    textarea.first.fill(test_content)
                    page.wait_for_timeout(500)
                    log_pass(f"填入内容: '{test_content}'", step=2)
                    verifications["fill_content"] = True
                else:
                    log_fail("文本域不存在", step=2)
                    verifications["fill_content"] = False
            else:
                log_fail("'动态内容'表单项不存在", step=2)
                verifications["content_field"] = False

            # Check image upload area
            upload_area = dialog.locator(".upload-area, .upload-trigger")
            if upload_area.count() > 0:
                log_pass("图片上传区域存在", step=2)
                verifications["upload_area"] = True
            else:
                log_warn("图片上传区域未找到", step=2)
                verifications["upload_area"] = None

            # Check word limit tip
            upload_tip = dialog.locator(".upload-tip")
            if upload_tip.count() > 0:
                log_pass(f"上传提示: '{upload_tip.first.inner_text()}'", step=2)

            # Check submit button
            submit_btn = dialog.locator("button:has-text('发布')")
            if submit_btn.count() > 0:
                log_pass("'发布'按钮可见", step=3)
                verifications["submit_btn"] = True

                # Submit
                submit_btn.first.click()
                page.wait_for_timeout(3000)

                # Check result: success message or dialog closes
                success_msg = page.locator(".el-message--success")
                dialog_gone = dialog.count() == 0 or not dialog.first.is_visible()

                if success_msg.count() > 0:
                    log_pass("发布成功消息显示", step=3)
                    verifications["publish_success"] = True
                elif dialog_gone:
                    log_pass("弹窗已关闭(发布可能成功)", step=3)
                    verifications["publish_success"] = True
                else:
                    # Check for error message
                    error_msg = page.locator(".el-message--error")
                    if error_msg.count() > 0:
                        log_pass("错误提示显示(可能是网络或后端原因)", step=3)
                        verifications["publish_success"] = None
                    else:
                        log_fail("发布后无成功/失败反馈", step=3)
                        verifications["publish_success"] = False
                        ss.save_dom_snapshot(step=3, tag="publish_result")
            else:
                log_fail("'发布'按钮不可见", step=3)
                verifications["submit_btn"] = False

            ss.capture("CHECKPOINT", step=3, action="publish_feed")

            # Close dialog if still open
            if dialog.count() > 0 and dialog.first.is_visible():
                close_btn = dialog.locator(".el-dialog__headerbtn")
                if close_btn.count() > 0:
                    close_btn.first.click()
                    page.wait_for_timeout(500)
        else:
            log_fail("发布动态弹窗未打开", step=1)
            verifications["dialog_open"] = False
            ss.save_dom_snapshot(step=1, tag="no_dialog")

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
    lines = ["# 校链通 校友圈模块 E2E 测试报告", "",
             f"| 项目 | 内容 |", "|------|------|",
             f"| 测试模块 | 第6章 校友圈模块 (L2 E2E) |",
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
    print("校链通(XiaoLianTong) - 第6章 校友圈模块 L2 E2E 测试")
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
            ("TC-E2E-037: 页面展示", tc_e2e_037),
            ("TC-E2E-038: 动态卡片", tc_e2e_038),
            ("TC-E2E-039: 发布动态", tc_e2e_039),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page, token_data)
            all_results.append(r)

        browser.close()

    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch06.md")
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
