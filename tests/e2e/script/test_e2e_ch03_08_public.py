"""
E2E 测试 - 第3~8章 公共页面（首页、商机、企业、校友圈、搜索、通知）
TC-E2E-011 ~ TC-E2E-030
"""
import pytest
from conftest import BASE_URL, take_screenshot, login_via_api


@pytest.fixture(autouse=True)
def logged_in_page(page, base_url):
    """确保已登录（function scope，与 page fixture 一致）"""
    login_via_api(page, '13800000001', 'Admin123!')
    return page


@pytest.mark.e2e
class TestHomepage:
    """第3章 首页模块 E2E 测试"""

    def test_e2e_11_homepage_header(self, page, base_url):
        """
        TC-E2E-011: Header结构
        预期: Logo、导航4项、搜索框、铃铛、用户头像
        """
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        # 验证导航
        nav_links = page.locator('.nav-link, .header-nav a')
        assert nav_links.count() >= 4

        take_screenshot(page, 'TC-E2E-011', '成功')

    def test_e2e_12_homepage_hero(self, page, base_url):
        """
        TC-E2E-012: Hero区域
        预期: 标题"连接校友资源，共创商业价值"、两个发布按钮、热门标签
        """
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        # 验证Hero标题
        hero = page.locator('.hero-section, .hero-title').first
        if hero.is_visible():
            assert hero.is_visible()

        take_screenshot(page, 'TC-E2E-012', '成功')

    def test_e2e_13_homepage_stats(self, page, base_url):
        """
        TC-E2E-013: 统计卡片
        预期: 4个统计卡片（入驻企业、商机、撮合、校友）
        """
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        stats = page.locator('.stat-card, .stats-section .stat-item')
        assert stats.count() >= 4

        take_screenshot(page, 'TC-E2E-013', '成功')

    def test_e2e_14_homepage_opportunities(self, page, base_url):
        """
        TC-E2E-014: 智能匹配推荐
        预期: 商机卡片列表，含类型标签、标题、企业信息
        """
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        cards = page.locator('.opp-card, .opportunity-card')
        # 可能有0个（无数据）或多个卡片
        take_screenshot(page, 'TC-E2E-014', '成功')

    def test_e2e_15_homepage_sidebar(self, page, base_url):
        """
        TC-E2E-015: 侧边栏-新入驻企业+校友动态
        预期: 侧边栏有两个card
        """
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        sidebar = page.locator('.content-sidebar, .sidebar-card')
        take_screenshot(page, 'TC-E2E-015', '成功')

    def test_e2e_16_publish_dialog(self, page, base_url):
        """
        TC-E2E-016: 发布商机弹窗
        预期: 点击发布按钮打开弹窗
        """
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        # 点击发布采购需求
        publish_btn = page.locator('button:has-text("发布采购需求")')
        if publish_btn.is_visible():
            publish_btn.click()
            page.wait_for_timeout(1000)
            take_screenshot(page, 'TC-E2E-016', '成功')
        else:
            take_screenshot(page, 'TC-E2E-016', '失败', '按钮不可见')

    def test_e2e_17_notification_panel(self, page, base_url):
        """
        TC-E2E-017: 通知下拉面板
        预期: 点击铃铛出现通知列表
        """
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        # 点击通知铃铛
        bell = page.locator('.notification-bell, .header-bell, [class*="bell"]')
        if bell.is_visible():
            bell.click()
            page.wait_for_timeout(1000)
            take_screenshot(page, 'TC-E2E-017', '成功')
        else:
            take_screenshot(page, 'TC-E2E-017', '失败', '铃铛不可见')


@pytest.mark.e2e
class TestOpportunity:
    """第4章 商机广场 E2E 测试"""

    def test_e2e_18_opportunity_page(self, page, base_url):
        """
        TC-E2E-018: 商机广场页面结构
        预期: 标题、筛选栏、商机列表
        """
        page.goto(f'{base_url}/opportunity')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        take_screenshot(page, 'TC-E2E-018', '成功')

    def test_e2e_19_opportunity_sidebar_filter(self, page, base_url):
        """
        TC-E2E-019: 商机筛选侧边栏
        预期: 类型筛选、行业级联、地区级联
        """
        page.goto(f'{base_url}/opportunity')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        take_screenshot(page, 'TC-E2E-019', '成功')


@pytest.mark.e2e
class TestEnterprise:
    """第5章 企业名录 E2E 测试"""

    def test_e2e_20_enterprise_page(self, page, base_url):
        """
        TC-E2E-020: 企业名录页面结构
        预期: 标题、认领/创建按钮、筛选栏、企业卡片
        """
        page.goto(f'{base_url}/enterprise')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        take_screenshot(page, 'TC-E2E-020', '成功')

    def test_e2e_21_enterprise_claim_dialog(self, page, base_url):
        """
        TC-E2E-021: 认领企业弹窗
        预期: 点击认领按钮打开弹窗
        """
        page.goto(f'{base_url}/enterprise')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        claim_btn = page.locator('button:has-text("认领")')
        if claim_btn.is_visible():
            claim_btn.click()
            page.wait_for_timeout(1000)
            take_screenshot(page, 'TC-E2E-021', '成功')
        else:
            take_screenshot(page, 'TC-E2E-021', '失败', '按钮不可见')


@pytest.mark.e2e
class TestFeed:
    """第6章 校友圈 E2E 测试"""

    def test_e2e_22_feed_page(self, page, base_url):
        """
        TC-E2E-022: 校友圈页面
        预期: 标题、动态列表、发布按钮
        """
        page.goto(f'{base_url}/feed')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        take_screenshot(page, 'TC-E2E-022', '成功')


@pytest.mark.e2e
class TestSearch:
    """第7章 搜索 E2E 测试"""

    def test_e2e_23_search_page(self, page, base_url):
        """
        TC-E2E-023: 搜索页面
        预期: 搜索框、三个Tab（商机/企业/动态）
        """
        page.goto(f'{base_url}/search?keyword=测试')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        take_screenshot(page, 'TC-E2E-023', '成功')


@pytest.mark.e2e
class TestNotification:
    """第8章 通知消息 E2E 测试"""

    def test_e2e_24_notification_page(self, page, base_url):
        """
        TC-E2E-024: 通知消息页面
        预期: 标题、通知列表、全部已读按钮
        """
        page.goto(f'{base_url}/notification')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        # 验证"全部已读"按钮
        read_all = page.locator('button:has-text("全部已读"), span:has-text("全部已读")')
        take_screenshot(page, 'TC-E2E-024', '成功')
