from django.urls import path
from apps.opportunity.views import (
    OpportunityListView,
    OpportunityDetailView,
    OpportunityOfflineView,
    OpportunityContactView,
    OpportunityRecommendedView,
)

app_name = 'opportunity'

urlpatterns = [
    path('opportunity', OpportunityListView.as_view(), name='opp-list'),
    # Recommended must be before <int:pk> to avoid being matched as a pk
    path('opportunity/recommended', OpportunityRecommendedView.as_view(), name='opp-recommended'),
    path('opportunity/<int:pk>', OpportunityDetailView.as_view(), name='opp-detail'),
    path('opportunity/<int:pk>/offline', OpportunityOfflineView.as_view(), name='opp-offline'),
    path('opportunity/<int:pk>/contact', OpportunityContactView.as_view(), name='opp-contact'),
]
