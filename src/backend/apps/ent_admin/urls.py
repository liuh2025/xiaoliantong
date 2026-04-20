from django.urls import path
from apps.ent_admin.views import (
    EmployeeListView,
    EmployeeDetailView,
    EmployeeResetPasswordView,
    EmployeeDisableView,
    EmployeeUnbindView,
    OpportunityListView,
    OpportunityDetailView,
    OpportunityRepublishView,
    OpportunityOfflineView,
)

app_name = 'ent_admin'

urlpatterns = [
    # Employee management
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/reset-password/', EmployeeResetPasswordView.as_view(), name='employee-reset-password'),
    path('employees/<int:pk>/disable/', EmployeeDisableView.as_view(), name='employee-disable'),
    path('employees/<int:pk>/unbind/', EmployeeUnbindView.as_view(), name='employee-unbind'),
    # Opportunity management
    path('my-opportunities/', OpportunityListView.as_view(), name='opp-list'),
    path('my-opportunities/<int:pk>/', OpportunityDetailView.as_view(), name='opp-detail'),
    path('my-opportunities/<int:pk>/republish/', OpportunityRepublishView.as_view(), name='opp-republish'),
    path('my-opportunities/<int:pk>/offline/', OpportunityOfflineView.as_view(), name='opp-offline'),
]
