from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """当创建User时，自动创建对应的UserProfile"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """当User保存时，保存对应的UserProfile"""
    # 如果通过管理后台或者某些没有关联profile的情况下保存，避免报错
    if hasattr(instance, 'ent_user_profile'):
        instance.ent_user_profile.save()
