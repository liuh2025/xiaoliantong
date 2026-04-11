from django.db import models
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise


class Opportunity(models.Model):
    """商机表 - 存储企业发布的采购/供应商机信息。"""

    class OppType(models.TextChoices):
        BUY = 'BUY', '采购'
        SUPPLY = 'SUPPLY', '供应'

    class OppStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', '在线'
        OFFLINE = 'OFFLINE', '下线'

    type = models.CharField(
        max_length=10,
        choices=OppType.choices,
        verbose_name='商机类型',
    )
    title = models.CharField(max_length=200, verbose_name='商机标题')
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.PROTECT,
        related_name='opportunities',
        verbose_name='发布企业',
    )
    publisher = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='published_opportunities',
        verbose_name='发布人',
    )
    industry_id = models.BigIntegerField(verbose_name='一级行业ID')
    sub_industry_id = models.BigIntegerField(verbose_name='二级行业ID')
    category_id = models.BigIntegerField(verbose_name='业务品类')
    province_id = models.BigIntegerField(verbose_name='省份ID')
    region_id = models.BigIntegerField(verbose_name='市ID')
    tags = models.JSONField(default=list, blank=True, verbose_name='业务标签')
    detail = models.TextField(verbose_name='详细描述')
    status = models.CharField(
        max_length=20,
        choices=OppStatus.choices,
        default=OppStatus.ACTIVE,
        verbose_name='状态',
    )
    view_count = models.IntegerField(default=0, verbose_name='浏览量')
    contact_name = models.CharField(
        max_length=50, blank=True, default='', verbose_name='联系人'
    )
    contact_phone = models.CharField(
        max_length=11, blank=True, default='', verbose_name='联系电话'
    )
    contact_wechat = models.CharField(
        max_length=50, blank=True, default='', verbose_name='微信'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'opp_opportunity'
        verbose_name = '商机'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ContactLog(models.Model):
    """商机联系记录表 - 记录用户获取商机联系方式的行为。"""

    class ContactStatus(models.TextChoices):
        INITIATED = 'INITIATED', '已发起'
        CONFIRMED = 'CONFIRMED', '已确认'
        COMPLETED = 'COMPLETED', '已完成'
        CANCELLED = 'CANCELLED', '已取消'

    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='contact_logs',
        verbose_name='涉及的商机',
    )
    getter_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='opp_contacts',
        verbose_name='获取方用户',
    )
    getter_enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.PROTECT,
        related_name='opp_contacts',
        verbose_name='获取方企业',
    )
    status = models.CharField(
        max_length=20,
        choices=ContactStatus.choices,
        default=ContactStatus.COMPLETED,
        verbose_name='状态',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='获取时间')

    class Meta:
        db_table = 'opp_contact_log'
        verbose_name = '商机联系记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"ContactLog({self.opportunity.title} - {self.status})"
