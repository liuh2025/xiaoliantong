from django.apps import AppConfig


class MsgConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.msg'
    verbose_name = '消息通知模块'
