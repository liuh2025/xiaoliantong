from django.db import models
from django.contrib.auth.models import User


class Enterprise(models.Model):
    """企业表 - 存储企业基本信息和认证状态。"""

    class AuthStatus(models.TextChoices):
        UNCLAIMED = 'UNCLAIMED', '未认领'
        PENDING = 'PENDING', '审核中'
        VERIFIED = 'VERIFIED', '已认证'
        REJECTED = 'REJECTED', '已拒绝'

    name = models.CharField(max_length=200, verbose_name='企业全称')
    credit_code = models.CharField(
        max_length=18, unique=True, verbose_name='统一社会信用代码'
    )
    legal_representative = models.CharField(
        max_length=100, verbose_name='法人姓名'
    )
    business_license = models.CharField(
        max_length=500, verbose_name='营业执照URL'
    )
    logo_url = models.CharField(
        max_length=500, null=True, blank=True, verbose_name='Logo地址'
    )
    industry_id = models.BigIntegerField(verbose_name='一级行业ID')
    sub_industry_id = models.BigIntegerField(verbose_name='二级行业ID（末级）')
    category_id = models.BigIntegerField(
        null=True, blank=True, verbose_name='主营业务品类ID'
    )
    province_id = models.BigIntegerField(verbose_name='省份ID')
    region_id = models.BigIntegerField(verbose_name='市ID')
    tags = models.JSONField(null=True, blank=True, verbose_name='业务标签')
    description = models.TextField(blank=True, default='', verbose_name='企业简介')
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='administered_enterprises',
        verbose_name='企业管理员',
    )
    auth_status = models.CharField(
        max_length=20,
        choices=AuthStatus.choices,
        default=AuthStatus.UNCLAIMED,
        verbose_name='认证状态',
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ent_enterprise'
        verbose_name = '企业'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class AuditRecord(models.Model):
    """审核记录表 - 记录企业认证审核流程。"""

    class AuditStatus(models.TextChoices):
        PENDING = 'PENDING', '待审核'
        APPROVED = 'APPROVED', '已通过'
        REJECTED = 'REJECTED', '已拒绝'

    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        related_name='audit_records',
        verbose_name='关联企业',
    )
    auditor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_records',
        verbose_name='审核人',
    )
    status = models.CharField(
        max_length=20,
        choices=AuditStatus.choices,
        verbose_name='审核状态',
    )
    audit_reason = models.TextField(
        null=True, blank=True, verbose_name='审核原因/备注'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'ent_audit_record'
        verbose_name = '审核记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"AuditRecord({self.enterprise.name} - {self.status})"


class MasterData(models.Model):
    """主数据字典表 - 存储行业、品类、地区等字典数据。"""

    category = models.CharField(max_length=50, verbose_name='数据类别')
    name = models.CharField(max_length=200, verbose_name='名称')
    code = models.CharField(max_length=50, verbose_name='编码')
    parent_id = models.BigIntegerField(
        null=True, blank=True, verbose_name='父级ID',
    )
    industry_id = models.BigIntegerField(
        null=True, blank=True, verbose_name='关联行业ID',
    )
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'plat_master_data'
        verbose_name = '主数据字典'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.category}: {self.name}"
