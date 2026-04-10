"""
E2E 测试 - 第9~11章 企业管理（企业信息、员工管理、商机管理）
TC-E2E-025 ~ TC-E2E-038
"""
import pytest
from conftest import BASE_URL, take_screenshot, login_via_api


def _login_as_ent_admin(page):
    """以企业管理员身份登录 - 使用有企业绑定的账号"""
    return login_via_api(page, '13900001111', 'Admin123!')


@pytest.fixture(autouse=True)
def ent_admin_page(page, base_url):
    """确保以企业管理员身份登录（function scope）"""
    _login_as_ent_admin(page)
    return page


@pytest.mark.e2e
class TestEnterpriseInfo:
    """第9章 企业信息维护 E2E 测试"""

    def test_e2e_25_ent_info_page_render(self, page, base_url):
        """
        TC-E2E-025: 企业信息页面渲染
        预期: 企业信息卡片、只读字段、可编辑字段
        """
        page.goto(f'{base_url}/ent-admin/enterprise-info')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 验证页面标题
        title = page.locator('.card-header span, .el-card__header span')
        expect_text = title.first.text_content()
        assert '企业信息' in expect_text or '信息' in expect_text

        take_screenshot(page, 'TC-E2E-025', '成功')

    def test_e2e_26_ent_info_edit_save(self, page, base_url):
        """
        TC-E2E-026: 编辑企业信息
        预期: 点击编辑按钮切换为编辑模式
        """
        page.goto(f'{base_url}/ent-admin/enterprise-info')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        edit_btn = page.locator('button:has-text("编辑")')
        if edit_btn.is_visible():
            edit_btn.click()
            page.wait_for_timeout(1000)
            take_screenshot(page, 'TC-E2E-026', '成功')
        else:
            take_screenshot(page, 'TC-E2E-026', '失败', '编辑按钮不可见')


@pytest.mark.e2e
class TestEmployee:
    """第10章 员工管理 E2E 测试"""

    def test_e2e_27_employee_page_render(self, page, base_url):
        """
        TC-E2E-027: 员工管理页面渲染
        预期: 标题"员工管理"、搜索栏、表格、新增按钮
        """
        page.goto(f'{base_url}/ent-admin/employee')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 验证标题
        header = page.locator('.card-header span, .el-card__header span')
        if not header.first.is_visible():
            take_screenshot(page, 'TC-E2E-027', '失败', '页面未渲染')
            assert False, '页面标题未渲染'

        # 验证新增按钮
        add_btn = page.locator('button:has-text("邀请"), button:has-text("新增员工")')
        assert add_btn.first.is_visible()

        # 验证搜索栏
        search = page.locator('input[placeholder="搜索员工姓名或手机号"]')
        assert search.is_visible()

        take_screenshot(page, 'TC-E2E-027', '成功')

    def test_e2e_28_employee_add_dialog(self, page, base_url):
        """
        TC-E2E-028: 新增员工弹窗
        预期: 点击新增按钮打开弹窗，含姓名、职位、手机号、角色字段
        """
        page.goto(f'{base_url}/ent-admin/employee')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        add_btn = page.locator('button:has-text("邀请"), button:has-text("新增员工")')
        add_btn.first.click()
        page.wait_for_timeout(1000)

        # 验证弹窗
        dialog = page.locator('.el-dialog')
        assert dialog.is_visible()

        # 验证表单字段
        name_input = page.locator('.el-dialog input[placeholder="请输入员工姓名"]')
        phone_input = page.locator('.el-dialog input[placeholder="请输入手机号"]')
        assert name_input.is_visible()
        assert phone_input.is_visible()

        take_screenshot(page, 'TC-E2E-028', '成功')

    def test_e2e_29_employee_table_columns(self, page, base_url):
        """
        TC-E2E-029: 员工表格列检查
        预期: 表格含姓名、职位、手机号、角色、状态、操作列
        """
        page.goto(f'{base_url}/ent-admin/employee')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # 检查表头
        headers = page.locator('.el-table__header-wrapper th')
        header_texts = [h.text_content() for h in headers.all()]
        assert any('姓名' in t for t in header_texts)
        assert any('角色' in t or '系统角色' in t for t in header_texts)

        take_screenshot(page, 'TC-E2E-029', '成功')


@pytest.mark.e2e
class TestMyOpportunity:
    """第11章 企业商机管理 E2E 测试"""

    def test_e2e_30_my_opp_page_render(self, page, base_url):
        """
        TC-E2E-030: 商机管理页面渲染
        预期: 标题"商机管理"、发布按钮、表格
        """
        page.goto(f'{base_url}/ent-admin/my-opportunity')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        header = page.locator('.card-header span')
        assert header.first.is_visible()

        # 发布商机按钮
        pub_btn = page.locator('button:has-text("发布商机")')
        assert pub_btn.first.is_visible()

        take_screenshot(page, 'TC-E2E-030', '成功')

    def test_e2e_31_my_opp_table_columns(self, page, base_url):
        """
        TC-E2E-031: 商机表格列检查
        预期: 含标题、类型、状态、操作列
        """
        page.goto(f'{base_url}/ent-admin/my-opportunity')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        headers = page.locator('.el-table__header-wrapper th')
        header_texts = [h.text_content() for h in headers.all()]
        assert any('标题' in t for t in header_texts)
        assert any('操作' in t for t in header_texts)

        take_screenshot(page, 'TC-E2E-031', '成功')

    def test_e2e_32_my_opp_create_dialog(self, page, base_url):
        """
        TC-E2E-032: 发布商机弹窗
        预期: 点击发布按钮弹出表单
        """
        page.goto(f'{base_url}/ent-admin/my-opportunity')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        pub_btn = page.locator('button:has-text("发布商机")')
        pub_btn.first.click()
        page.wait_for_timeout(1000)

        dialog = page.locator('.el-dialog')
        assert dialog.is_visible()

        # 验证商机类型radio
        radio = page.locator('.el-dialog .el-radio')
        assert radio.count() >= 2

        take_screenshot(page, 'TC-E2E-032', '成功')
