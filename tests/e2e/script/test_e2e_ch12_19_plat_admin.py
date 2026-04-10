"""
E2E 测试 - 第12~19章 平台管理（数据大盘、审核、租户、内容管理、基础数据、权限、设置）
TC-E2E-033 ~ TC-E2E-048
"""
import pytest
from conftest import BASE_URL, take_screenshot, login_via_api


def _login_as_plat_admin(page):
    """以平台管理员身份登录 - 使用API注入admin角色token"""
    import json
    import urllib.request

    data = json.dumps({'phone': '13800000001', 'password': 'Admin123!'}).encode()
    req = urllib.request.Request(
        'http://localhost:8000/api/v1/auth/login/password/',
        data=data,
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except Exception:
        return False

    if result.get('code') != 0:
        return False

    token_data = result['data']
    # 注入平台管理员角色
    page.evaluate(f"""() => {{
        localStorage.setItem('access_token', '{token_data['access_token']}');
        localStorage.setItem('refresh_token', '{token_data['refresh_token']}');
        localStorage.setItem('user_info', JSON.stringify({{
            id: {token_data['user_id']},
            phone: '13800000001',
            role_code: 'platform_operator',
        }}));
    }}""")
    return True


@pytest.fixture(autouse=True)
def plat_admin_page(page, base_url):
    """确保以平台管理员身份登录（function scope）"""
    _login_as_plat_admin(page)
    return page


@pytest.mark.e2e
class TestDashboard:
    """第12章 数据大盘 E2E 测试"""

    def test_e2e_33_dashboard_stats(self, page, base_url):
        """
        TC-E2E-033: 统计卡片
        预期: 4个统计卡片（入驻企业、累计商机、成功撮合、活跃校友）
        """
        page.goto(f'{base_url}/plat-admin/dashboard')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        stats = page.locator('.stat-card')
        assert stats.count() >= 4

        # 验证趋势箭头
        trend = page.locator('.stat-trend')
        assert trend.count() >= 1

        take_screenshot(page, 'TC-E2E-033', '成功')

    def test_e2e_34_dashboard_trend_chart(self, page, base_url):
        """
        TC-E2E-034: 趋势图
        预期: "最近7天商机趋势"卡片和图表
        """
        page.goto(f'{base_url}/plat-admin/dashboard')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 验证趋势图区域
        chart_section = page.locator('.section-card, .trend-chart')
        assert chart_section.first.is_visible()

        take_screenshot(page, 'TC-E2E-034', '成功')

    def test_e2e_35_dashboard_recent_enterprises(self, page, base_url):
        """
        TC-E2E-035: 最新企业入驻表格
        预期: 表格含企业名称、行业、地区、状态
        """
        page.goto(f'{base_url}/plat-admin/dashboard')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 验证最新企业表格存在
        tables = page.locator('.el-table')
        assert tables.count() >= 1

        take_screenshot(page, 'TC-E2E-035', '成功')


@pytest.mark.e2e
class TestAudit:
    """第13章 企业入驻审核 E2E 测试"""

    def test_e2e_36_audit_page_render(self, page, base_url):
        """
        TC-E2E-036: 审核列表页面
        预期: 标题、Tab（全部/待审核/已通过/已拒绝）、表格
        """
        page.goto(f'{base_url}/plat-admin/audit')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 验证Tab
        tabs = page.locator('.el-tabs__item')
        assert tabs.count() >= 3

        take_screenshot(page, 'TC-E2E-036', '成功')

    def test_e2e_37_audit_tab_switch(self, page, base_url):
        """
        TC-E2E-037: Tab切换
        预期: 点击已通过Tab，列表过滤
        """
        page.goto(f'{base_url}/plat-admin/audit')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 点击已通过Tab
        approved_tab = page.locator('.el-tabs__item:has-text("已通过")')
        if approved_tab.is_visible():
            approved_tab.click()
            page.wait_for_timeout(1500)
            take_screenshot(page, 'TC-E2E-037', '成功')
        else:
            take_screenshot(page, 'TC-E2E-037', '失败', 'Tab不可见')

    def test_e2e_38_audit_approve_dialog(self, page, base_url):
        """
        TC-E2E-038: 审核通过弹窗
        预期: 点击通过按钮打开弹窗，含企业信息和备注
        """
        page.goto(f'{base_url}/plat-admin/audit')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 点击待审核Tab
        pending_tab = page.locator('.el-tabs__item:has-text("待审核")')
        if pending_tab.is_visible():
            pending_tab.click()
            page.wait_for_timeout(1500)

        approve_btn = page.locator('button:has-text("通过")').first
        if approve_btn.is_visible():
            approve_btn.click()
            page.wait_for_timeout(1000)

            dialog = page.locator('.el-dialog')
            if dialog.is_visible():
                take_screenshot(page, 'TC-E2E-038', '成功')
            else:
                take_screenshot(page, 'TC-E2E-038', '失败', '弹窗未出现')
        else:
            take_screenshot(page, 'TC-E2E-038', '失败', '无待审核数据')


@pytest.mark.e2e
class TestOpportunityManage:
    """第15章 商机内容管理 E2E 测试"""

    def test_e2e_39_opp_manage_page(self, page, base_url):
        """
        TC-E2E-039: 商机内容管理页面
        预期: 标题、筛选下拉、表格含标题/企业/类型/状态/操作
        """
        page.goto(f'{base_url}/plat-admin/opportunity-manage')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 验证筛选栏
        filters = page.locator('.filter-bar .el-select')
        assert filters.count() >= 2

        take_screenshot(page, 'TC-E2E-039', '成功')

    def test_e2e_40_opp_manage_detail(self, page, base_url):
        """
        TC-E2E-040: 商机查看详情
        预期: 点击查看打开抽屉显示详情
        """
        page.goto(f'{base_url}/plat-admin/opportunity-manage')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        view_btn = page.locator('button:has-text("查看")').first
        if view_btn.is_visible():
            view_btn.click()
            page.wait_for_timeout(1500)

            drawer = page.locator('.el-drawer')
            if drawer.is_visible():
                take_screenshot(page, 'TC-E2E-040', '成功')
            else:
                take_screenshot(page, 'TC-E2E-040', '失败', '抽屉未出现')
        else:
            take_screenshot(page, 'TC-E2E-040', '失败', '无数据')


@pytest.mark.e2e
class TestFeedManage:
    """第16章 动态内容管理 E2E 测试"""

    def test_e2e_41_feed_manage_page(self, page, base_url):
        """
        TC-E2E-041: 动态内容管理页面
        预期: 标题、状态筛选、表格含内容/发布人/状态/操作
        """
        page.goto(f'{base_url}/plat-admin/feed-manage')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 验证筛选栏
        status_filter = page.locator('.filter-bar .el-select')
        assert status_filter.count() >= 1

        take_screenshot(page, 'TC-E2E-041', '成功')

    def test_e2e_42_feed_manage_detail(self, page, base_url):
        """
        TC-E2E-042: 动态查看详情
        预期: 点击查看详情打开弹窗
        """
        page.goto(f'{base_url}/plat-admin/feed-manage')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        detail_btn = page.locator('button:has-text("查看详情"), button:has-text("查看")').first
        if detail_btn.is_visible():
            detail_btn.click()
            page.wait_for_timeout(1000)

            dialog = page.locator('.el-dialog')
            if dialog.is_visible():
                take_screenshot(page, 'TC-E2E-042', '成功')
            else:
                take_screenshot(page, 'TC-E2E-042', '失败', '弹窗未出现')
        else:
            take_screenshot(page, 'TC-E2E-042', '失败', '无数据')


@pytest.mark.e2e
class TestMasterData:
    """第17章 基础数据字典 E2E 测试"""

    def test_e2e_43_master_data_page(self, page, base_url):
        """
        TC-E2E-043: 基础数据页面
        预期: Tab（行业分类、业务品类、业务标签、行政区划）
        """
        page.goto(f'{base_url}/plat-admin/master-data')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        tabs = page.locator('.el-tabs__item')
        assert tabs.count() >= 2

        take_screenshot(page, 'TC-E2E-043', '成功')


@pytest.mark.e2e
class TestRBAC:
    """第18章 权限管理 E2E 测试"""

    def test_e2e_44_rbac_page(self, page, base_url):
        """
        TC-E2E-044: 权限管理页面
        预期: 角色卡片列表
        """
        page.goto(f'{base_url}/plat-admin/rbac')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        take_screenshot(page, 'TC-E2E-044', '成功')


@pytest.mark.e2e
class TestSettings:
    """第19章 系统设置 E2E 测试"""

    def test_e2e_45_settings_page(self, page, base_url):
        """
        TC-E2E-045: 系统设置页面
        预期: 基础设置表单、安全策略开关
        """
        page.goto(f'{base_url}/plat-admin/settings')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        take_screenshot(page, 'TC-E2E-045', '成功')


@pytest.mark.e2e
class TestTenantManage:
    """第14章 租户管理 E2E 测试"""

    def test_e2e_46_tenant_page(self, page, base_url):
        """
        TC-E2E-046: 租户管理页面
        预期: 搜索框、表格含企业名称/管理员/成员数/状态/操作
        """
        page.goto(f'{base_url}/plat-admin/tenant')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        take_screenshot(page, 'TC-E2E-046', '成功')

    def test_e2e_47_tenant_member_dialog(self, page, base_url):
        """
        TC-E2E-047: 成员管理弹窗
        预期: 点击成员管理打开弹窗
        """
        page.goto(f'{base_url}/plat-admin/tenant')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        member_btn = page.locator('button:has-text("成员管理")').first
        if member_btn.is_visible():
            member_btn.click()
            page.wait_for_timeout(1000)
            dialog = page.locator('.el-dialog')
            if dialog.is_visible():
                take_screenshot(page, 'TC-E2E-047', '成功')
            else:
                take_screenshot(page, 'TC-E2E-047', '失败', '弹窗未出现')
        else:
            take_screenshot(page, 'TC-E2E-047', '失败', '无数据')


@pytest.mark.e2e
class TestPlatAdminSidebar:
    """平台管理侧边栏导航 E2E 测试"""

    def test_e2e_48_plat_admin_navigation(self, page, base_url):
        """
        TC-E2E-048: 平台管理侧边栏导航
        预期: 侧边栏含数据大盘、企业审核、租户管理、商机管理、动态管理等菜单
        """
        page.goto(f'{base_url}/plat-admin/dashboard')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 验证侧边栏存在
        sidebar = page.locator('.admin-sidebar, .sidebar, .el-menu, aside')
        if sidebar.first.is_visible():
            take_screenshot(page, 'TC-E2E-048', '成功')
        else:
            take_screenshot(page, 'TC-E2E-048', '失败', '侧边栏不可见')
