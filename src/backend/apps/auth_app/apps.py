from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth_app'
    verbose_name = '认证模块'

    def ready(self):
        import apps.auth_app.signals  # noqa: F401
