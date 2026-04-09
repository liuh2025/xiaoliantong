from django.db import models
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise


class Feed(models.Model):
    """动态表 - 存储校友圈发布的动态信息。"""

    class FeedStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', '在线'
        OFFLINE = 'OFFLINE', '下线'

    publisher = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='published_feeds',
        verbose_name='发布人',
    )
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.PROTECT,
        related_name='feeds',
        verbose_name='发布人所属企业',
    )
    content = models.TextField(verbose_name='动态内容')
    images = models.JSONField(
        default=list, blank=True, verbose_name='图片URL数组',
    )
    status = models.CharField(
        max_length=20,
        choices=FeedStatus.choices,
        default=FeedStatus.ACTIVE,
        verbose_name='状态',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'feed_feed'
        verbose_name = '动态'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"Feed({self.id} - {self.publisher.username})"
