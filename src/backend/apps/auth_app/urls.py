from django.urls import path
from .views import (
    SmsSendView, SmsLoginView, RegisterView, PasswordLoginView,
    PasswordResetVerifyView, PasswordResetView,
    LogoutView, CustomTokenRefreshView,
    CurrentUserInfoView,
)

urlpatterns = [
    path('sms/send/', SmsSendView.as_view(), name='sms-send'),
    path('sms/login/', SmsLoginView.as_view(), name='sms-login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/password/', PasswordLoginView.as_view(), name='password-login'),
    path('password/reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('password/reset/', PasswordResetView.as_view(), name='password-reset'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', CurrentUserInfoView.as_view(), name='current-user-info'),
]
