"""PLAT-001: Platform admin profile and notification tests."""
import pytest
from django.urls import reverse
from apps.msg.models import Message


@pytest.mark.django_db
class TestPlatformProfile:
    """Tests for GET /api/v1/plat-admin/profile."""

    def setup_method(self):
        self.url = reverse('plat_admin:profile')

    def test_profile_returns_info(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.status_code == 200
        data = response.data
        assert data['code'] == 200
        assert data['data']['id'] == platform_admin.id
        assert data['data']['role_code'] == 'super_admin'
        assert data['data']['role_name'] == '超级管理员'

    def test_profile_unauthenticated(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_profile_non_admin_denied(self, api_client, guest_user):
        api_client.force_authenticate(user=guest_user)
        response = api_client.get(self.url)
        assert response.status_code == 403

    def test_profile_operator_allowed(self, api_client, platform_operator):
        api_client.force_authenticate(user=platform_operator)
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data['data']['role_code'] == 'platform_operator'


@pytest.mark.django_db
class TestPlatformNotification:
    """Tests for GET /api/v1/plat-admin/notification."""

    def setup_method(self):
        self.url = reverse('plat_admin:notification-list')

    def test_list_notifications(self, api_client, platform_admin):
        Message.objects.create(
            receiver=platform_admin,
            type='SYSTEM',
            title='Test Notification',
            content='Test content',
        )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data['data']['total'] == 1
        assert len(response.data['data']['items']) == 1

    def test_list_notifications_empty(self, api_client, platform_admin):
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url)
        assert response.data['data']['total'] == 0

    def test_list_notifications_pagination(self, api_client, platform_admin):
        for i in range(5):
            Message.objects.create(
                receiver=platform_admin,
                type='SYSTEM',
                title=f'Notification {i}',
                content='Content',
            )
        api_client.force_authenticate(user=platform_admin)
        response = api_client.get(self.url, {'page': 1, 'page_size': 2})
        assert response.data['data']['total'] == 5
        assert len(response.data['data']['items']) == 2

    def test_notification_read_all(self, api_client, platform_admin):
        Message.objects.create(
            receiver=platform_admin, type='SYSTEM',
            title='Msg 1', content='c', is_read=False,
        )
        Message.objects.create(
            receiver=platform_admin, type='SYSTEM',
            title='Msg 2', content='c', is_read=False,
        )
        url = reverse('plat_admin:notification-read-all')
        api_client.force_authenticate(user=platform_admin)
        response = api_client.post(url)
        assert response.data['data']['updated_count'] == 2
