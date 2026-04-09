from django.urls import path
from apps.enterprise.views import (
    EnterpriseListView,
    EnterpriseDetailView,
    EnterpriseClaimView,
    EnterpriseCreateView,
    MyEnterpriseView,
    IndustryListView,
    CategoryListView,
    RegionListView,
    NewestEnterpriseView,
)

app_name = 'enterprise'

urlpatterns = [
    path('enterprise', EnterpriseListView.as_view(), name='enterprise-list'),
    path('enterprise/newest', NewestEnterpriseView.as_view(), name='enterprise-newest'),
    path('enterprise/claim', EnterpriseClaimView.as_view(), name='enterprise-claim'),
    path('enterprise/create', EnterpriseCreateView.as_view(), name='enterprise-create'),
    path('enterprise/my', MyEnterpriseView.as_view(), name='enterprise-my'),
    path('enterprise/<int:pk>', EnterpriseDetailView.as_view(), name='enterprise-detail'),
    path('industry', IndustryListView.as_view(), name='industry-list'),
    path('category', CategoryListView.as_view(), name='category-list'),
    path('region', RegionListView.as_view(), name='region-list'),
]
