"""
L1 API 集成测试 - msg + search 模块
用例编号: TC-API-msg-001 ~ 004, TC-API-search-001
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.msg.models import Message
from apps.enterprise.models import Enterprise
from apps.opportunity.models import Opportunity
from apps.feed.models import Feed
from apps.auth_app.models import UserProfile


# ============================================================
# Message / Notification API Tests
# ============================================================


@pytest.mark.django_db
class TestNotificationAPI:
    """TC-API-msg-001 ~ 004: 通知消息接口"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='msg_user', password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def _create_notification(self, **kwargs):
        defaults = {
            'receiver': self.user,
            'type': 'system',
            'title': '测试通知',
            'content': '这是一条测试通知内容',
            'is_read': False,
        }
        defaults.update(kwargs)
        return Message.objects.create(**defaults)

    # TC-API-msg-001: 通知列表
    def test_api_msg_001_notification_list(self):
        """
        TC-API-msg-001: 获取通知列表-成功
        预期: HTTP 200, 含通知列表
        """
        self._create_notification(title='通知1')
        self._create_notification(title='通知2')
        url = '/api/v1/msg/notifications'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 200
        assert data['data']['total'] >= 2
        assert len(data['data']['items']) >= 2

    # TC-API-msg-002: 标记单条已读
    def test_api_msg_002_mark_read(self):
        """
        TC-API-msg-002: 标记单条通知已读
        预期: HTTP 200, is_read=True
        """
        msg = self._create_notification()
        url = f'/api/v1/msg/notifications/{msg.id}/read'
        response = self.client.put(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['is_read'] is True

        # DB校验
        msg.refresh_from_db()
        assert msg.is_read is True

    # TC-API-msg-003: 全部标记已读
    def test_api_msg_003_mark_all_read(self):
        """
        TC-API-msg-003: 全部标记已读
        预期: HTTP 200, updated_count >= 3
        """
        self._create_notification(title='未读1')
        self._create_notification(title='未读2')
        self._create_notification(title='未读3')
        url = '/api/v1/msg/notifications/read-all'
        response = self.client.put(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['updated_count'] >= 3

    # TC-API-msg-004: 最近未读通知
    def test_api_msg_004_recent_notifications(self):
        """
        TC-API-msg-004: 获取最近未读通知
        预期: HTTP 200, 含unread_count和items
        """
        self._create_notification(title='最近未读1')
        self._create_notification(title='最近未读2')
        url = '/api/v1/msg/notifications/recent'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['unread_count'] >= 2
        assert len(response.data['data']['items']) <= 5


# ============================================================
# Search API Tests
# ============================================================


@pytest.mark.django_db
class TestSearchAPI:
    """TC-API-search-001: 全局搜索"""

    def setup_method(self):
        self.client = APIClient()
        # 创建测试数据
        self.user = User.objects.create_user(username='search_user', password='TestPass123!')
        self.ent = Enterprise.objects.create(
            name='搜索测试科技有限公司',
            credit_code='91MA00SEARCH01X',
            legal_representative='测试',
            business_license='https://example.com/license.jpg',
            industry_id=1,
            sub_industry_id=101,
            province_id=110000,
            region_id=110100,
            auth_status=Enterprise.AuthStatus.VERIFIED,
            admin_user=self.user,
        )

    # TC-API-search-001: 全局搜索-按企业名称
    def test_api_search_001_search_enterprise(self):
        """
        TC-API-search-001: 全局搜索-企业
        预期: HTTP 200, 返回匹配结果
        """
        url = '/api/v1/search'
        response = self.client.get(url, {'keyword': '搜索测试'})
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['code'] == 200
        assert 'ent' in data['data']
        assert data['data']['ent']['total'] >= 1

    # TC-API-search-002: 全局搜索-无结果
    def test_api_search_002_search_no_result(self):
        """
        TC-API-search-002: 全局搜索-无匹配结果
        预期: HTTP 200, 所有tab total=0
        """
        url = '/api/v1/search'
        response = self.client.get(url, {'keyword': 'ZZZZZ不存在的关键词YYYYY'})
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['data']['opp']['total'] == 0
        assert data['data']['ent']['total'] == 0
        assert data['data']['feed']['total'] == 0

    # TC-API-search-003: 全局搜索-缺少关键词
    def test_api_search_003_search_missing_keyword(self):
        """
        TC-API-search-003: 全局搜索-缺少关键词
        预期: HTTP 400
        """
        url = '/api/v1/search'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 400

    # TC-API-search-004: 全局搜索-指定tab
    def test_api_search_004_search_by_tab(self):
        """
        TC-API-search-004: 全局搜索-指定tab
        预期: HTTP 200, 仅返回指定tab结果
        """
        url = '/api/v1/search'
        response = self.client.get(url, {'keyword': '搜索测试', 'tab': 'ent'})
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert 'ent' in data['data']
        assert 'opp' not in data['data']
        assert 'feed' not in data['data']
