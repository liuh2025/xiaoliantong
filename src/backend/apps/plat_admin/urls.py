from django.urls import path
from . import views

app_name = 'plat_admin'

urlpatterns = [
    # PLAT-001: Profile & Notification
    path('profile', views.PlatformProfileView.as_view(), name='profile'),
    path(
        'notification/read-all',
        views.PlatformNotificationReadAllView.as_view(),
        name='notification-read-all',
    ),
    path(
        'notification',
        views.PlatformNotificationListView.as_view(),
        name='notification-list',
    ),

    # PLAT-002: Dashboard
    path('dashboard/stats', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/trend', views.DashboardTrendView.as_view(), name='dashboard-trend'),

    # PLAT-003: Enterprise Audit
    path(
        'audit/enterprise/<int:pk>/approve',
        views.AuditEnterpriseApproveView.as_view(),
        name='audit-enterprise-approve',
    ),
    path(
        'audit/enterprise/<int:pk>/reject',
        views.AuditEnterpriseRejectView.as_view(),
        name='audit-enterprise-reject',
    ),
    path(
        'audit/enterprise',
        views.AuditEnterpriseListView.as_view(),
        name='audit-enterprise-list',
    ),

    # PLAT-004: Tenant Management
    path(
        'tenant/enterprise/<int:pk>/toggle-status',
        views.TenantEnterpriseToggleStatusView.as_view(),
        name='tenant-enterprise-toggle-status',
    ),
    path(
        'tenant/enterprise/<int:pk>/member',
        views.TenantMemberListView.as_view(),
        name='tenant-member-list',
    ),
    path(
        'tenant/enterprise/<int:pk>',
        views.TenantEnterpriseDetailView.as_view(),
        name='tenant-enterprise-detail',
    ),
    path(
        'tenant/enterprise',
        views.TenantEnterpriseListView.as_view(),
        name='tenant-enterprise-list',
    ),
    path(
        'tenant/member/<int:pk>/reset-password',
        views.TenantMemberResetPasswordView.as_view(),
        name='tenant-member-reset-password',
    ),
    path(
        'tenant/member/<int:pk>/unbind',
        views.TenantMemberUnbindView.as_view(),
        name='tenant-member-unbind',
    ),
    path(
        'tenant/member/<int:pk>',
        views.TenantMemberDetailView.as_view(),
        name='tenant-member-detail',
    ),

    # PLAT-005: Opportunity Content
    path(
        'content/opportunity/<int:pk>/offline',
        views.ContentOpportunityOfflineView.as_view(),
        name='content-opportunity-offline',
    ),
    path(
        'content/opportunity/<int:pk>',
        views.ContentOpportunityDetailView.as_view(),
        name='content-opportunity-detail',
    ),
    path(
        'content/opportunity',
        views.ContentOpportunityListView.as_view(),
        name='content-opportunity-list',
    ),

    # PLAT-006: Feed Content
    path(
        'content/feed/<int:pk>/offline',
        views.ContentFeedOfflineView.as_view(),
        name='content-feed-offline',
    ),
    path(
        'content/feed/<int:pk>',
        views.ContentFeedDetailView.as_view(),
        name='content-feed-detail',
    ),
    path(
        'content/feed',
        views.ContentFeedListView.as_view(),
        name='content-feed-list',
    ),

    # PLAT-007: Master Data CRUD
    path(
        'master-data/<int:pk>/toggle-status',
        views.MasterDataToggleStatusView.as_view(),
        name='master-data-toggle-status',
    ),
    path(
        'master-data/<int:pk>',
        views.MasterDataDetailView.as_view(),
        name='master-data-detail',
    ),
    path(
        'master-data',
        views.MasterDataListView.as_view(),
        name='master-data-list',
    ),

    # PLAT-008: RBAC
    path(
        'role/<int:pk>/permissions',
        views.RolePermissionUpdateView.as_view(),
        name='role-permissions',
    ),
    path('role/<int:pk>', views.RoleDetailView.as_view(), name='role-detail'),
    path('role', views.RoleListView.as_view(), name='role-list'),

    # PLAT-009: Settings
    path('settings', views.SettingsGetView.as_view(), name='settings'),
]
