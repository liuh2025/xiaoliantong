"""
校链通(XiaoLianTong) - 第7章 搜索模块 L2 E2E 测试
基于 QA-test-plan-PP-v1.0.md 第7章
覆盖用例: TC-E2E-040 ~ TC-E2E-041

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
CAPTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captures", "ch07_search")
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
# Helper to setup search page with login
# ============================================================
def setup_search_page(page, tokens, query="test"):
    inject_login(page, tokens)
    page.goto(f"{BASE_URL}/search?q={query}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    return tokens


# ============================================================
# Test Cases
# ============================================================

def tc_e2e_040(page, tokens):
    """TC-E2E-040: 搜索页面 - 搜索输入框、结果展示"""
    global _logger
    case_id = "TC-E2E-040"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "搜索页面展示", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_search_page(page, tokens, query="test")
        log_info("=== 搜索页面展示验证 ===")

        # Step 1: Verify search bar exists with input
        # Vue uses: <div class="search-bar"> containing <el-input> with placeholder
        search_bar = page.locator(".search-bar")
        if search_bar.count() > 0 and search_bar.first.is_visible():
            log_pass("搜索栏区域可见", step=1)
            verifications["search_bar"] = True
        else:
            log_fail("搜索栏区域不可见", step=1)
            verifications["search_bar"] = False

        # Check the el-input inside search-bar has correct placeholder
        search_input = page.locator(".search-bar .el-input__inner")
        if search_input.count() > 0:
            placeholder = search_input.first.get_attribute("placeholder") or ""
            if "搜索" in placeholder:
                log_pass(f"搜索输入框placeholder: '{placeholder}'", step=1)
                verifications["search_input"] = True
            else:
                log_warn(f"搜索输入框placeholder: '{placeholder}' (未包含'搜索')", step=1)
                verifications["search_input"] = False
        else:
            log_fail("搜索输入框(.el-input__inner)不可见", step=1)
            verifications["search_input"] = False

        # Verify input value equals query param "test"
        if search_input.count() > 0:
            input_value = search_input.first.input_value()
            if input_value == "test":
                log_pass(f"搜索框已填入查询词: '{input_value}'", step=1)
                verifications["query_filled"] = True
            else:
                log_warn(f"搜索框内容: '{input_value}' (期望'test')", step=1)
                verifications["query_filled"] = False

        # Step 2: Verify search button (append button "搜索")
        search_btn = page.locator(".search-bar .el-input-group__append button, .search-bar button:has-text('搜索')")
        if search_btn.count() > 0 and search_btn.first.is_visible():
            log_pass("搜索按钮可见", step=1)
            verifications["search_button"] = True
        else:
            log_fail("搜索按钮不可见", step=1)
            verifications["search_button"] = False

        # Step 3: Verify results area
        # Vue: <div class="search-results"> contains <div class="results-list"> or <el-empty>
        search_results = page.locator(".search-results")
        if search_results.count() > 0:
            log_pass("搜索结果区域可见", step=2)
            verifications["results_area"] = True
        else:
            log_fail("搜索结果区域不可见", step=2)
            verifications["results_area"] = False

        # Check if results are displayed or empty state shown
        results_list = page.locator(".results-list")
        empty_state = page.locator(".search-results .el-empty")

        if results_list.count() > 0 and results_list.first.is_visible():
            # Results found - check result cards
            result_cards = page.locator(".result-card")
            card_count = result_cards.count()
            if card_count > 0:
                log_pass(f"搜索结果列表可见, 共{card_count}条结果", step=2)
                verifications["results_list"] = True

                # Check result card structure (opportunity type by default)
                first_card = result_cards.first
                result_header = first_card.locator(".result-header")
                result_title = first_card.locator(".result-title")
                result_sub = first_card.locator(".result-sub")
                result_desc = first_card.locator(".result-desc")

                if result_header.count() > 0:
                    log_pass("结果卡片头部(.result-header)可见", step=2)
                    verifications["card_header"] = True
                else:
                    log_warn("结果卡片头部不可见", step=2)
                    verifications["card_header"] = False

                if result_title.count() > 0:
                    title_text = result_title.first.inner_text()
                    log_pass(f"结果标题: '{title_text}'", step=2)
                    verifications["card_title"] = True
                else:
                    log_warn("结果标题不可见", step=2)
                    verifications["card_title"] = False

                if result_sub.count() > 0:
                    log_pass("结果副标题(.result-sub)可见", step=2)
                    verifications["card_sub"] = True
                else:
                    log_warn("结果副标题不可见", step=2)
                    verifications["card_sub"] = False
            else:
                log_warn("搜索结果列表容器可见但无卡片", step=2)
                verifications["results_list"] = False
        elif empty_state.count() > 0 and empty_state.first.is_visible():
            log_warn("搜索结果为空, 显示el-empty(未找到相关结果)", step=2)
            verifications["results_list"] = None  # N/A - no data
        else:
            log_fail("搜索结果列表和空状态均不可见", step=2)
            verifications["results_list"] = False

        ss.capture("CHECKPOINT", step=2, action="search_page_verified")

        # Step 4: Verify page container
        search_page_div = page.locator(".search-page")
        if search_page_div.count() > 0:
            log_pass("搜索页面容器(.search-page)存在", step=3)
            verifications["page_container"] = True
        else:
            log_fail("搜索页面容器不存在", step=3)
            verifications["page_container"] = False

        ss.capture("CHECKPOINT", step=3, action="full_page")

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


def tc_e2e_041(page, tokens):
    """TC-E2E-041: 搜索Tab - 商机/企业/动态切换"""
    global _logger
    case_id = "TC-E2E-041"
    case_dir = os.path.join(SCREENSHOT_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    _logger = TestLogger(case_id, case_dir)
    ss = SmartScreenshot(page, case_dir, case_id)
    result = {"case_id": case_id, "name": "搜索Tab切换", "status": "FAIL", "details": []}
    verifications = {}

    try:
        setup_search_page(page, tokens, query="test")
        log_info("=== 搜索Tab切换验证 ===")

        # Step 1: Verify el-tabs exist with 3 tab panes
        # Vue: <el-tabs v-model="activeTab"> with panes: 商机(opportunity), 企业(enterprise), 动态(feed)
        el_tabs = page.locator(".el-tabs")
        if el_tabs.count() > 0 and el_tabs.first.is_visible():
            log_pass("Tab组件(.el-tabs)可见", step=1)
            verifications["tabs_component"] = True
        else:
            log_fail("Tab组件(.el-tabs)不可见", step=1)
            verifications["tabs_component"] = False

        # Check tab labels: 商机, 企业, 动态
        expected_tabs = [
            {"label": "商机", "name": "opportunity"},
            {"label": "企业", "name": "enterprise"},
            {"label": "动态", "name": "feed"},
        ]

        for tab_info in expected_tabs:
            tab_label = tab_info["label"]
            tab_item = page.locator(f".el-tabs__item:has-text('{tab_label}')")
            if tab_item.count() > 0 and tab_item.first.is_visible():
                log_pass(f"Tab项'{tab_label}'可见", step=1)
                verifications[f"tab_{tab_info['name']}"] = True
            else:
                log_fail(f"Tab项'{tab_label}'不可见", step=1)
                verifications[f"tab_info['name']"] = False

        # Step 2: Verify default tab is "商机" (active)
        active_tab = page.locator(".el-tabs__item.is-active")
        if active_tab.count() > 0:
            active_text = active_tab.first.inner_text()
            if "商机" in active_text:
                log_pass(f"默认激活Tab: '{active_text}'", step=2)
                verifications["default_active"] = True
            else:
                log_warn(f"默认激活Tab: '{active_text}' (期望包含'商机')", step=2)
                verifications["default_active"] = False
        else:
            log_fail("未找到激活状态的Tab", step=2)
            verifications["default_active"] = False

        ss.capture("CHECKPOINT", step=2, action="default_tab")

        # Step 3: Click "企业" tab
        ent_tab = page.locator(".el-tabs__item:has-text('企业')")
        if ent_tab.count() > 0:
            ent_tab.first.click()
            page.wait_for_timeout(1500)

            # Verify "企业" tab is now active
            active_tab_after = page.locator(".el-tabs__item.is-active")
            if active_tab_after.count() > 0 and "企业" in active_tab_after.first.inner_text():
                log_pass("点击'企业'Tab后, '企业'Tab已激活", step=3)
                verifications["ent_tab_switch"] = True
            else:
                log_fail("点击'企业'Tab后, 激活状态未切换", step=3)
                verifications["ent_tab_switch"] = False

            # Verify URL updated with tab param
            current_url = page.url
            if "tab=enterprise" in current_url:
                log_pass(f"URL已更新: {current_url}", step=3)
                verifications["ent_url_update"] = True
            else:
                log_warn(f"URL未更新tab参数: {current_url}", step=3)
                verifications["ent_url_update"] = False

            # Check enterprise result structure (if results exist)
            ent_cards = page.locator(".result-card")
            if ent_cards.count() > 0:
                first_card = ent_cards.first
                ent_title = first_card.locator(".result-title")
                if ent_title.count() > 0:
                    log_pass(f"企业结果卡片标题: '{ent_title.first.inner_text()}'", step=3)
                verifications["ent_results"] = True
            else:
                empty = page.locator(".search-results .el-empty")
                if empty.count() > 0:
                    log_warn("企业Tab搜索结果为空", step=3)
                    verifications["ent_results"] = None
                else:
                    log_warn("企业Tab无结果卡片", step=3)
                    verifications["ent_results"] = None

            ss.capture("CHECKPOINT", step=3, action="enterprise_tab")
        else:
            log_fail("'企业'Tab项不可见, 无法点击", step=3)
            verifications["ent_tab_switch"] = False

        # Step 4: Click "动态" tab
        feed_tab = page.locator(".el-tabs__item:has-text('动态')")
        if feed_tab.count() > 0:
            feed_tab.first.click()
            page.wait_for_timeout(1500)

            # Verify "动态" tab is now active
            active_tab_after = page.locator(".el-tabs__item.is-active")
            if active_tab_after.count() > 0 and "动态" in active_tab_after.first.inner_text():
                log_pass("点击'动态'Tab后, '动态'Tab已激活", step=4)
                verifications["feed_tab_switch"] = True
            else:
                log_fail("点击'动态'Tab后, 激活状态未切换", step=4)
                verifications["feed_tab_switch"] = False

            # Verify URL updated with tab=feed
            current_url = page.url
            if "tab=feed" in current_url:
                log_pass(f"URL已更新: {current_url}", step=4)
                verifications["feed_url_update"] = True
            else:
                log_warn(f"URL未更新tab参数: {current_url}", step=4)
                verifications["feed_url_update"] = False

            # Check feed result structure (if results exist)
            feed_cards = page.locator(".result-card")
            if feed_cards.count() > 0:
                first_card = feed_cards.first
                feed_author = first_card.locator(".result-author")
                feed_time = first_card.locator(".result-time")
                feed_desc = first_card.locator(".result-desc")
                if feed_author.count() > 0 and feed_desc.count() > 0:
                    log_pass(f"动态结果卡片结构完整: author={feed_author.first.inner_text()}", step=4)
                    verifications["feed_results"] = True
                else:
                    log_warn("动态结果卡片结构不完整", step=4)
                    verifications["feed_results"] = False
            else:
                empty = page.locator(".search-results .el-empty")
                if empty.count() > 0:
                    log_warn("动态Tab搜索结果为空", step=4)
                    verifications["feed_results"] = None
                else:
                    log_warn("动态Tab无结果卡片", step=4)
                    verifications["feed_results"] = None

            ss.capture("CHECKPOINT", step=4, action="feed_tab")
        else:
            log_fail("'动态'Tab项不可见, 无法点击", step=4)
            verifications["feed_tab_switch"] = False

        # Step 5: Switch back to "商机" tab
        opp_tab = page.locator(".el-tabs__item:has-text('商机')")
        if opp_tab.count() > 0:
            opp_tab.first.click()
            page.wait_for_timeout(1500)

            active_tab_final = page.locator(".el-tabs__item.is-active")
            if active_tab_final.count() > 0 and "商机" in active_tab_final.first.inner_text():
                log_pass("切回'商机'Tab后, '商机'Tab已激活", step=5)
                verifications["opp_tab_switch_back"] = True
            else:
                log_fail("切回'商机'Tab失败", step=5)
                verifications["opp_tab_switch_back"] = False

            ss.capture("CHECKPOINT", step=5, action="back_to_opportunity")
        else:
            log_warn("'商机'Tab项不可见", step=5)
            verifications["opp_tab_switch_back"] = False

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


# ============================================================
# Report
# ============================================================
def _generate_report(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = ["# 校链通 搜索模块 E2E 测试报告", "",
             f"| 项目 | 内容 |", "|------|------|",
             f"| 测试模块 | 第7章 搜索模块 (L2 E2E) |",
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
    print("校链通(XiaoLianTong) - 第7章 搜索模块 L2 E2E 测试")
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
            ("TC-E2E-040: 搜索页面展示", tc_e2e_040),
            ("TC-E2E-041: 搜索Tab切换", tc_e2e_041),
        ]

        for name, func in test_cases:
            print(f"\n{'='*70}")
            print(f">> {name}")
            print(f"{'='*70}")
            r = func(page, token_data)
            all_results.append(r)

        browser.close()

    report = _generate_report(all_results)
    report_path = os.path.join(SCREENSHOT_DIR, "test_report_ch07.md")
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
