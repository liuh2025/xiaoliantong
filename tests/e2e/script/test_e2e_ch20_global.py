"""
E2E 测试 - 第20章 全局公共交互
TC-E2E-049 ~ TC-E2E-055
"""
import pytest
from conftest import BASE_URL, take_screenshot, login_via_api


@pytest.mark.e2e
class TestGlobalHeaderNav:
    """第20章 Header导航一致性"""

    def test_e2e_49_header_nav_consistency(self, page, base_url):
        """
        TC-E2E-049: Header导航一致性
        预期: 首页/商机/企业/校友圈导航在多个页面一致
        """
        # 先登录
        login_via_api(page, '13800000001', 'Admin123!')

        pages_to_check = [
            f'{base_url}/',
            f'{base_url}/opportunity',
            f'{base_url}/enterprise',
        ]

        nav_count = None
        for url in pages_to_check:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1500)

            nav_links = page.locator('header .nav-link, header nav a, .header-nav a')
            count = nav_links.count()
            if nav_count is None:
                nav_count = count
            else:
                assert count == nav_count, f'导航数量不一致: {url} 有 {count} 个，期望 {nav_count}'

        take_screenshot(page, 'TC-E2E-049', '成功')


@pytest.mark.e2e
class TestGlobalNotification:
    """第20章 通知铃铛一致性"""

    def test_e2e_50_notification_bell(self, page, base_url):
        """
        TC-E2E-050: 通知铃铛
        预期: 已登录页面均显示铃铛
        """
        login_via_api(page, '13800000001', 'Admin123!')
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        bell = page.locator('.notification-bell, [class*="bell"], .notification-icon, header [class*="notification"]')
        if bell.first.is_visible():
            take_screenshot(page, 'TC-E2E-050', '成功')
        else:
            take_screenshot(page, 'TC-E2E-050', '失败', '铃铛不可见')


@pytest.mark.e2e
class TestGlobalUserMenu:
    """第20章 用户菜单一致性"""

    def test_e2e_51_user_menu(self, page, base_url):
        """
        TC-E2E-051: 用户菜单
        预期: 点击头像出现下拉菜单
        """
        login_via_api(page, '13800000001', 'Admin123!')
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        # 点击用户头像/名称
        avatar = page.locator('header .user-avatar, header .user-info, header .user-dropdown, .header-right .user')
        if avatar.first.is_visible():
            avatar.first.click()
            page.wait_for_timeout(1000)

            # 检查下拉菜单
            dropdown = page.locator('.el-dropdown-menu, .user-menu, .dropdown-menu')
            if dropdown.first.is_visible():
                take_screenshot(page, 'TC-E2E-051', '成功')
            else:
                take_screenshot(page, 'TC-E2E-051', '失败', '下拉菜单未出现')
        else:
            take_screenshot(page, 'TC-E2E-051', '失败', '头像不可见')


@pytest.mark.e2e
class TestGlobalLogout:
    """第20章 登出"""

    def test_e2e_52_logout(self, page, base_url):
        """
        TC-E2E-052: 退出登录
        预期: 退出后跳转到登录页，localStorage已清空
        """
        login_via_api(page, '13800000001', 'Admin123!')
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        # 点击头像打开菜单
        avatar = page.locator('header .user-avatar, header .user-info, header .user-dropdown, .header-right .user')
        if avatar.first.is_visible():
            avatar.first.click()
            page.wait_for_timeout(500)

        # 点击退出登录
        logout_btn = page.locator('text=退出登录, .el-dropdown-menu-item:has-text("退出")')
        if logout_btn.first.is_visible():
            logout_btn.first.click()
            page.wait_for_timeout(3000)

            # 验证跳转到登录页
            current_url = page.url
            if '/login' in current_url:
                # 验证localStorage已清空
                token = page.evaluate("() => localStorage.getItem('access_token')")
                assert token is None, '退出后token应被清空'
                take_screenshot(page, 'TC-E2E-052', '成功')
            else:
                take_screenshot(page, 'TC-E2E-052', '失败', '未跳转到登录页')
        else:
            take_screenshot(page, 'TC-E2E-052', '失败', '退出按钮不可见')


@pytest.mark.e2e
class TestGlobalUnauth:
    """第20章 未登录保护"""

    def test_e2e_53_unauth_redirect(self, page, base_url):
        """
        TC-E2E-053: 未登录访问受保护页面
        预期: 跳转到登录页
        """
        # 不登录，直接访问企业管理页
        page.goto(f'{base_url}/ent-admin/employee')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        current_url = page.url
        if '/login' in current_url:
            take_screenshot(page, 'TC-E2E-053', '成功')
        else:
            take_screenshot(page, 'TC-E2E-053', '失败', '未重定向到登录页')


@pytest.mark.e2e
class TestGlobalPermission:
    """第20章 权限不足"""

    def test_e2e_54_permission_denied(self, page, base_url):
        """
        TC-E2E-054: 普通用户访问平台管理
        预期: 路由守卫拦截，跳转首页或提示
        """
        # 先登录获取token，然后在已认证的页面修改角色
        login_via_api(page, '13800000001', 'Admin123!')

        # 导航到首页确保localStorage可用
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)

        # 修改角色为普通员工
        page.evaluate("""() => {
            try {
                const info = JSON.parse(localStorage.getItem('user_info'));
                if (info) {
                    info.role_code = 'employee';
                    localStorage.setItem('user_info', JSON.stringify(info));
                }
            } catch(e) {}
        }""")

        page.goto(f'{base_url}/plat-admin/dashboard')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        current_url = page.url
        # 应被重定向到首页或登录页
        if '/plat-admin/dashboard' not in current_url:
            take_screenshot(page, 'TC-E2E-054', '成功')
        else:
            take_screenshot(page, 'TC-E2E-054', '失败', '未拦截权限不足的访问')


@pytest.mark.e2e
class TestGlobalDialogOverlay:
    """第20章 弹窗遮罩关闭"""

    def test_e2e_55_dialog_overlay_close(self, page, base_url):
        """
        TC-E2E-055: 弹窗遮罩关闭
        预期: 点击弹窗遮罩层关闭弹窗
        """
        login_via_api(page, '13800000001', 'Admin123!')
        page.goto(f'{base_url}/ent-admin/employee')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)

        # 打开新增员工弹窗
        add_btn = page.locator('button:has-text("邀请"), button:has-text("新增员工")')
        if add_btn.first.is_visible():
            add_btn.first.click()
            page.wait_for_timeout(1000)

            dialog = page.locator('.el-dialog')
            if dialog.is_visible():
                # 点击遮罩层
                overlay = page.locator('.el-overlay')
                if overlay.is_visible():
                    overlay.click()
                    page.wait_for_timeout(500)

                    # 验证弹窗已关闭
                    if not dialog.is_visible():
                        take_screenshot(page, 'TC-E2E-055', '成功')
                    else:
                        take_screenshot(page, 'TC-E2E-055', '失败', '弹窗未关闭')
                else:
                    take_screenshot(page, 'TC-E2E-055', '失败', '遮罩层不可见')
            else:
                take_screenshot(page, 'TC-E2E-055', '失败', '弹窗未打开')
        else:
            take_screenshot(page, 'TC-E2E-055', '失败', '新增按钮不可见')
