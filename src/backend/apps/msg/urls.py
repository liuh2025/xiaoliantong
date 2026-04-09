from django.urls import path
from apps.msg.views import (
    NotificationListView,
    NotificationReadView,
    NotificationReadAllView,
    NotificationRecentView,
)

app_name = 'msg'

urlpatterns = [
    path('notifications/read-all', NotificationReadAllView.as_view(), name='msg-read-all'),
    path('notifications/recent', NotificationRecentView.as_view(), name='msg-recent'),
    path('notifications/<int:pk>/read', NotificationReadView.as_view(), name='msg-read'),
    path('notifications', NotificationListView.as_view(), name='msg-list'),
]
