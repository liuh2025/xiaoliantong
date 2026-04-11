from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.auth_app.urls')),
    path('api/v1/ent/', include('apps.enterprise.urls')),
    path('api/v1/opp/', include('apps.opportunity.urls')),
    path('api/v1/feed/', include('apps.feed.urls')),
    path('api/v1/ent-admin/', include('apps.ent_admin.urls')),
    path('api/v1/plat-admin/', include('apps.plat_admin.urls')),
    path('api/v1/msg/', include('apps.msg.urls')),
    path('api/v1/', include('apps.search.urls')),
]
