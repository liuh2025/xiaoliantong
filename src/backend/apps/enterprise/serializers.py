from rest_framework import serializers
from apps.enterprise.models import Enterprise, MasterData
from apps.opportunity.models import Opportunity


class EnterpriseListSerializer(serializers.ModelSerializer):
    """Serializer for enterprise list with desensitization logic."""

    industry_name = serializers.SerializerMethodField()
    sub_industry_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()

    class Meta:
        model = Enterprise
        fields = [
            'id', 'name', 'credit_code', 'logo_url',
            'industry_name', 'sub_industry_name', 'category_name',
            'province_name', 'region_name',
            'tags', 'auth_status',
        ]

    def _is_verified(self, obj):
        """Check if the enterprise is verified."""
        return obj.auth_status == Enterprise.AuthStatus.VERIFIED

    def get_industry_name(self, obj):
        """Return industry name from MasterData."""
        if not self._is_verified(obj) or not obj.industry_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.industry_id, category='industry', is_active=True,
        ).first()
        return md.name if md else ''

    def get_sub_industry_name(self, obj):
        """Return sub-industry name from MasterData."""
        if not self._is_verified(obj) or not obj.sub_industry_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.sub_industry_id, category='industry', is_active=True,
        ).first()
        return md.name if md else ''

    def get_category_name(self, obj):
        """Return category name from MasterData."""
        if not self._is_verified(obj) or not obj.category_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.category_id, category='category', is_active=True,
        ).first()
        return md.name if md else ''

    def get_province_name(self, obj):
        """Return province name from MasterData."""
        if not self._is_verified(obj) or not obj.province_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.province_id, category='region', is_active=True,
        ).first()
        return md.name if md else ''

    def get_region_name(self, obj):
        """Return region (city) name from MasterData."""
        if not self._is_verified(obj) or not obj.region_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.region_id, category='region', is_active=True,
        ).first()
        return md.name if md else ''

    def to_representation(self, instance):
        """Apply desensitization for non-VERIFIED enterprises."""
        data = super().to_representation(instance)
        if not self._is_verified(instance):
            # Only return id, name, auth_status; other fields set to null/empty
            data['credit_code'] = None
            data['logo_url'] = None
            data['industry_name'] = ''
            data['sub_industry_name'] = ''
            data['category_name'] = ''
            data['province_name'] = ''
            data['region_name'] = ''
            data['tags'] = None
        return data


class EnterpriseDetailSerializer(serializers.ModelSerializer):
    """Serializer for enterprise detail with conditional desensitization.

    VERIFIED enterprises return full information including contact details.
    Non-VERIFIED enterprises have sensitive fields desensitized (set to None).
    """

    industry_name = serializers.SerializerMethodField()
    sub_industry_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()
    admin_user_name = serializers.SerializerMethodField()
    contact_phone = serializers.SerializerMethodField()
    opportunities = serializers.SerializerMethodField()

    class Meta:
        model = Enterprise
        fields = [
            'id', 'name', 'credit_code', 'logo_url',
            'legal_representative', 'business_license',
            'industry_name', 'sub_industry_name', 'category_name',
            'province_name', 'region_name',
            'tags', 'description', 'auth_status',
            'admin_user_name', 'contact_phone', 'opportunities',
            'created_at',
        ]

    def _is_verified(self, obj):
        """Check if the enterprise is verified."""
        return obj.auth_status == Enterprise.AuthStatus.VERIFIED

    def get_industry_name(self, obj):
        """Return industry name from MasterData."""
        if not obj.industry_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.industry_id, category='industry', is_active=True,
        ).first()
        return md.name if md else ''

    def get_sub_industry_name(self, obj):
        """Return sub-industry name from MasterData."""
        if not obj.sub_industry_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.sub_industry_id, category='industry', is_active=True,
        ).first()
        return md.name if md else ''

    def get_category_name(self, obj):
        """Return category name from MasterData."""
        if not obj.category_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.category_id, category='category', is_active=True,
        ).first()
        return md.name if md else ''

    def get_province_name(self, obj):
        """Return province name from MasterData."""
        if not obj.province_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.province_id, category='region', is_active=True,
        ).first()
        return md.name if md else ''

    def get_region_name(self, obj):
        """Return region (city) name from MasterData."""
        if not obj.region_id:
            return ''
        md = MasterData.objects.filter(
            id=obj.region_id, category='region', is_active=True,
        ).first()
        return md.name if md else ''

    def get_admin_user_name(self, obj):
        """Return admin user's full name (VERIFIED only, None otherwise)."""
        if not self._is_verified(obj):
            return None
        if obj.admin_user:
            parts = [
                obj.admin_user.first_name,
                obj.admin_user.last_name,
            ]
            full_name = ' '.join(p for p in parts if p)
            return full_name if full_name else None
        return None

    def get_contact_phone(self, obj):
        """Return contact phone from admin user's UserProfile (VERIFIED only).

        Retrieves contact_phone from admin_user.ent_user_profile.
        Returns None if enterprise is not VERIFIED, or admin_user / profile /
        contact_phone is not available.
        """
        if not self._is_verified(obj):
            return None
        if not obj.admin_user:
            return None
        try:
            profile = obj.admin_user.ent_user_profile
            return profile.contact_phone if profile.contact_phone else None
        except Exception:
            return None

    def get_opportunities(self, obj):
        """Return latest 5 active opportunities published by the enterprise."""
        opps = Opportunity.objects.filter(
            enterprise=obj, status=Opportunity.OppStatus.ACTIVE,
        ).order_by('-created_at')[:5]
        return [
            {
                'id': o.id,
                'title': o.title,
                'type': o.type,
                'created_at': o.created_at.strftime('%Y-%m-%d') if o.created_at else '',
            }
            for o in opps
        ]

    def to_representation(self, instance):
        """Apply desensitization for non-VERIFIED enterprises."""
        data = super().to_representation(instance)
        if not self._is_verified(instance):
            # Sensitive fields: set to None for non-VERIFIED
            data['credit_code'] = None
            data['legal_representative'] = None
            data['contact_phone'] = None
            data['admin_user_name'] = None
        return data


class EnterpriseClaimSerializer(serializers.Serializer):
    """Serializer for enterprise claim request."""

    credit_code = serializers.CharField(required=False, max_length=18, allow_blank=True)
    enterprise_id = serializers.IntegerField(required=False)
    legal_representative = serializers.CharField(required=False, max_length=50, allow_blank=True)
    business_license = serializers.CharField(required=False, max_length=500, allow_blank=True)
    position = serializers.CharField(required=False, max_length=50, allow_blank=True)


class EnterpriseCreateSerializer(serializers.ModelSerializer):
    """Serializer for enterprise create request."""

    class Meta:
        model = Enterprise
        fields = [
            'name', 'credit_code', 'legal_representative', 'business_license',
            'industry_id', 'sub_industry_id', 'category_id',
            'province_id', 'region_id', 'tags', 'description',
        ]

    def validate_credit_code(self, value):
        """Validate credit_code uniqueness."""
        if Enterprise.objects.filter(credit_code=value).exists():
            raise serializers.ValidationError('该统一社会信用代码已被使用')
        return value


class EnterpriseUpdateSerializer(serializers.Serializer):
    """Serializer for enterprise update request - only updatable fields."""

    category_id = serializers.IntegerField(required=False, allow_null=True)
    province_id = serializers.IntegerField(required=False)
    region_id = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    logo_url = serializers.CharField(required=False, allow_blank=True, max_length=500)
    tags = serializers.JSONField(required=False, allow_null=True)


class MasterDataSerializer(serializers.ModelSerializer):
    """Serializer for MasterData dictionary entries."""

    class Meta:
        model = MasterData
        fields = ['id', 'category', 'name', 'code', 'parent_id',
                  'industry_id', 'sort_order', 'is_active']


class NewestEnterpriseSerializer(serializers.Serializer):
    """Serializer for newest enterprises list (simplified fields)."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    logo_url = serializers.CharField(allow_null=True)
    industry_name = serializers.SerializerMethodField()
    sub_industry_name = serializers.SerializerMethodField()
    auth_status = serializers.CharField()

    def get_industry_name(self, obj):
        """Return industry name (placeholder until dict API resolves names)."""
        md = MasterData.objects.filter(
            id=obj.industry_id, category='industry', is_active=True,
        ).first()
        return md.name if md else ''

    def get_sub_industry_name(self, obj):
        """Return sub-industry name."""
        md = MasterData.objects.filter(
            id=obj.sub_industry_id, category='industry', is_active=True,
        ).first()
        return md.name if md else ''
