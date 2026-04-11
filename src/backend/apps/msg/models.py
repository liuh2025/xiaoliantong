from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """消息通知表"""

    class MessageType(models.TextChoices):
        AUDIT_APPROVED = 'AUDIT_APPROVED', '审核通过'
        AUDIT_REJECTED = 'AUDIT_REJECTED', '审核驳回'
        CONTACT_RECEIVED = 'CONTACT_RECEIVED', '收到联系方式'
        SYSTEM = 'SYSTEM', '系统通知'

    receiver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='messages',
        verbose_name='接收人',
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sent_messages',
        null=True,
        blank=True,
        verbose_name='发送人',
    )
    type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        verbose_name='消息类型',
    )
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    related_type = models.CharField(
        max_length=50, blank=True, default='', verbose_name='关联对象类型',
    )
    related_id = models.BigIntegerField(
        null=True, blank=True, verbose_name='关联对象ID',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'msg_message'
        verbose_name = '消息通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"Message({self.id} - {self.title})"
