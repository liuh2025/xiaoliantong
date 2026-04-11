from django.urls import path
from apps.feed.views import (
    FeedListView,
    FeedDetailView,
    FeedOfflineView,
    FeedNewestView,
)

app_name = 'feed'

urlpatterns = [
    path('feed/newest', FeedNewestView.as_view(), name='feed-newest'),
    path('feed/<int:pk>/offline', FeedOfflineView.as_view(), name='feed-offline'),
    path('feed/<int:pk>', FeedDetailView.as_view(), name='feed-detail'),
    path('feed', FeedListView.as_view(), name='feed-list'),
]
