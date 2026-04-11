"""
ENT-001: Enterprise & AuditRecord model unit tests.
Tests cover model creation, field constraints, choices, indexes, and FK relationships.
"""
import pytest
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise, AuditRecord


def _build_enterprise(**overrides):
    """Helper to build a valid Enterprise dict with sensible defaults."""
    defaults = {
        'name': 'Test Enterprise Co., Ltd.',
        'credit_code': '91MA01ABCD1234X',
        'legal_representative': 'Zhang San',
        'business_license': 'https://example.com/license/test.jpg',
        'industry_id': 1,
        'sub_industry_id': 101,
        'province_id': 110000,
        'region_id': 110100,
        'auth_status': Enterprise.AuthStatus.UNCLAIMED,
    }
    defaults.update(overrides)
    return Enterprise(**defaults)


def _create_enterprise(**overrides):
    """Helper to create and return a saved Enterprise instance."""
    ent = _build_enterprise(**overrides)
    ent.save()
    return ent


@pytest.mark.django_db
class TestEnterpriseModel:
    """Enterprise model unit tests."""

    # ---- creation tests ----

    def test_create_enterprise_with_required_fields_only(self):
        """Enterprise can be created with all required fields and no optional fields."""
        ent = _build_enterprise()
        ent.save()
        assert ent.id is not None
        assert ent.name == 'Test Enterprise Co., Ltd.'
        assert ent.credit_code == '91MA01ABCD1234X'
        assert ent.legal_representative == 'Zhang San'
        assert ent.business_license == 'https://example.com/license/test.jpg'
        assert ent.industry_id == 1
        assert ent.sub_industry_id == 101
        assert ent.province_id == 110000
        assert ent.region_id == 110100
        assert ent.auth_status == Enterprise.AuthStatus.UNCLAIMED
        assert ent.created_at is not None
        assert ent.updated_at is not None

    def test_create_enterprise_with_all_optional_fields(self):
        """Enterprise can be created with optional fields populated."""
        user = User.objects.create_user(username='admin1', password='pass')
        ent = _build_enterprise(
            logo_url='https://example.com/logo.png',
            category_id=5,
            tags=['cloud', 'AI'],
            description='A test company.',
            admin_user=user,
        )
        ent.save()
        assert ent.logo_url == 'https://example.com/logo.png'
        assert ent.category_id == 5
        assert ent.tags == ['cloud', 'AI']
        assert ent.description == 'A test company.'
        assert ent.admin_user == user

    def test_optional_fields_default_to_none_or_empty(self):
        """Optional fields default to None/blank when not provided."""
        ent = _create_enterprise()
        assert ent.logo_url is None
        assert ent.category_id is None
        assert ent.tags is None
        assert ent.description == ''
        assert ent.admin_user is None

    # ---- field constraint tests ----

    def test_credit_code_must_be_unique(self):
        """credit_code has a unique constraint; duplicate raises IntegrityError."""
        _create_enterprise(credit_code='91MA01ABCD1234X')
        with pytest.raises(IntegrityError):
            _create_enterprise(credit_code='91MA01ABCD1234X')

    def test_name_is_required(self):
        """name field is required; saving without it should raise error."""
        with pytest.raises(IntegrityError):
            _create_enterprise(name=None)

    def test_credit_code_is_required(self):
        """credit_code field is required."""
        with pytest.raises(IntegrityError):
            _create_enterprise(credit_code=None)

    def test_legal_representative_is_required(self):
        """legal_representative field is required."""
        with pytest.raises(IntegrityError):
            _create_enterprise(legal_representative=None)

    def test_business_license_is_required(self):
        """business_license field is required."""
        with pytest.raises(IntegrityError):
            _create_enterprise(business_license=None)

    def test_industry_id_is_required(self):
        """industry_id field is required."""
        with pytest.raises(IntegrityError):
            _create_enterprise(industry_id=None)

    def test_sub_industry_id_is_required(self):
        """sub_industry_id field is required."""
        with pytest.raises(IntegrityError):
            _create_enterprise(sub_industry_id=None)

    def test_province_id_is_required(self):
        """province_id field is required."""
        with pytest.raises(IntegrityError):
            _create_enterprise(province_id=None)

    def test_region_id_is_required(self):
        """region_id field is required."""
        with pytest.raises(IntegrityError):
            _create_enterprise(region_id=None)

    def test_auth_status_is_required(self):
        """auth_status field is required."""
        with pytest.raises(IntegrityError):
            _create_enterprise(auth_status=None)

    # ---- choices tests ----

    def test_auth_status_choices(self):
        """auth_status accepts all defined choices."""
        for status_val in [
            Enterprise.AuthStatus.UNCLAIMED,
            Enterprise.AuthStatus.PENDING,
            Enterprise.AuthStatus.VERIFIED,
            Enterprise.AuthStatus.REJECTED,
        ]:
            ent = _create_enterprise(
                credit_code=f'code-{status_val}',
                auth_status=status_val,
            )
            ent.refresh_from_db()
            assert ent.auth_status == status_val

    def test_auth_status_default_is_unclaimed(self):
        """Default auth_status should be UNCLAIMED."""
        ent = _create_enterprise()
        assert ent.auth_status == Enterprise.AuthStatus.UNCLAIMED

    # ---- FK relationship tests ----

    def test_admin_user_fk_can_be_null(self):
        """admin_user is nullable (UNCLAIMED enterprises have no admin)."""
        ent = _create_enterprise()
        assert ent.admin_user is None

    def test_admin_user_fk_links_to_user(self):
        """admin_user FK correctly links to auth.User."""
        user = User.objects.create_user(username='ent_admin', password='pass')
        ent = _create_enterprise(admin_user=user)
        assert ent.admin_user == user
        assert ent.admin_user.username == 'ent_admin'

    def test_admin_user_set_null_on_delete(self):
        """Deleting admin_user sets the FK to NULL (SET_NULL)."""
        user = User.objects.create_user(username='temp_admin', password='pass')
        ent = _create_enterprise(admin_user=user)
        user.delete()
        ent.refresh_from_db()
        assert ent.admin_user is None

    def test_related_enterprises_on_user(self):
        """User can access related enterprises via reverse relation."""
        user = User.objects.create_user(username='multi_admin', password='pass')
        _create_enterprise(credit_code='AAA', admin_user=user)
        _create_enterprise(credit_code='BBB', admin_user=user)
        related = user.administered_enterprises.all()
        assert related.count() == 2

    # ---- meta tests ----

    def test_db_table_name(self):
        """Model uses the correct db_table name."""
        assert Enterprise._meta.db_table == 'ent_enterprise'

    def test_str_representation(self):
        """__str__ returns the enterprise name."""
        ent = _create_enterprise(name='My Corp')
        assert str(ent) == 'My Corp'

    def test_auto_timestamps(self):
        """created_at and updated_at are auto-populated."""
        ent = _create_enterprise()
        assert ent.created_at is not None
        assert ent.updated_at is not None


@pytest.mark.django_db
class TestAuditRecordModel:
    """AuditRecord model unit tests."""

    def _create_audit_enterprise(self, **overrides):
        """Helper to create an Enterprise for audit tests."""
        defaults = {
            'name': 'Audit Test Corp.',
            'credit_code': '91310000MA02EFGH2Y',
            'legal_representative': 'Li Si',
            'business_license': 'https://example.com/license/audit.jpg',
            'industry_id': 2,
            'sub_industry_id': 201,
            'province_id': 310000,
            'region_id': 310100,
        }
        defaults.update(overrides)
        return _create_enterprise(**defaults)

    def test_create_audit_record_with_auditor(self):
        """AuditRecord can be created with all fields."""
        ent = self._create_audit_enterprise()
        auditor = User.objects.create_user(username='auditor1', password='pass')
        record = AuditRecord(
            enterprise=ent,
            auditor=auditor,
            status=AuditRecord.AuditStatus.APPROVED,
            audit_reason='All documents verified.',
        )
        record.save()
        assert record.id is not None
        assert record.enterprise == ent
        assert record.auditor == auditor
        assert record.status == AuditRecord.AuditStatus.APPROVED
        assert record.audit_reason == 'All documents verified.'
        assert record.created_at is not None

    def test_create_audit_record_without_auditor(self):
        """AuditRecord can be created without an auditor."""
        ent = self._create_audit_enterprise()
        record = AuditRecord(
            enterprise=ent,
            status=AuditRecord.AuditStatus.PENDING,
        )
        record.save()
        assert record.auditor is None

    def test_audit_reason_optional(self):
        """audit_reason is optional."""
        ent = self._create_audit_enterprise()
        record = AuditRecord(
            enterprise=ent,
            status=AuditRecord.AuditStatus.PENDING,
        )
        record.save()
        assert record.audit_reason is None

    def test_enterprise_fk_required(self):
        """enterprise FK is required."""
        record = AuditRecord(status='PENDING')
        with pytest.raises(IntegrityError):
            record.save()

    def test_status_required(self):
        """status field is required."""
        ent = self._create_audit_enterprise()
        record = AuditRecord(enterprise=ent, status=None)
        with pytest.raises(IntegrityError):
            record.save()

    def test_status_choices(self):
        """status accepts all defined choices."""
        ent = self._create_audit_enterprise()
        for status_val in [
            AuditRecord.AuditStatus.PENDING,
            AuditRecord.AuditStatus.APPROVED,
            AuditRecord.AuditStatus.REJECTED,
        ]:
            record = AuditRecord(
                enterprise=ent,
                status=status_val,
                audit_reason=f'Test {status_val}',
            )
            record.save()
            record.refresh_from_db()
            assert record.status == status_val

    def test_auditor_set_null_on_delete(self):
        """Deleting auditor user sets auditor to NULL."""
        auditor = User.objects.create_user(username='aud_del', password='pass')
        ent = self._create_audit_enterprise()
        record = AuditRecord(
            enterprise=ent,
            auditor=auditor,
            status=AuditRecord.AuditStatus.APPROVED,
        )
        record.save()
        auditor.delete()
        record.refresh_from_db()
        assert record.auditor is None

    def test_enterprise_cascade_on_delete(self):
        """Deleting enterprise cascades and deletes related audit records."""
        ent = self._create_audit_enterprise()
        record = AuditRecord(
            enterprise=ent,
            status=AuditRecord.AuditStatus.PENDING,
        )
        record.save()
        record_id = record.id
        ent.delete()
        assert not AuditRecord.objects.filter(id=record_id).exists()

    def test_multiple_audit_records_for_enterprise(self):
        """Multiple audit records can exist for one enterprise."""
        ent = self._create_audit_enterprise()
        AuditRecord.objects.create(
            enterprise=ent,
            status=AuditRecord.AuditStatus.PENDING,
        )
        AuditRecord.objects.create(
            enterprise=ent,
            status=AuditRecord.AuditStatus.REJECTED,
            audit_reason='Missing document.',
        )
        assert ent.audit_records.count() == 2

    def test_db_table_name(self):
        """Model uses the correct db_table name."""
        assert AuditRecord._meta.db_table == 'ent_audit_record'

    def test_str_representation(self):
        """__str__ returns meaningful info."""
        ent = self._create_audit_enterprise(name='StrTest Corp')
        record = AuditRecord(
            enterprise=ent,
            status=AuditRecord.AuditStatus.PENDING,
        )
        record.save()
        result = str(record)
        assert 'StrTest Corp' in result
        assert AuditRecord.AuditStatus.PENDING in result


@pytest.mark.django_db
class TestEnterpriseUserProfileIntegration:
    """Tests for UserProfile.enterprise_id interaction with Enterprise model."""

    def test_userprofile_enterprise_id_field_exists(self):
        """UserProfile should have an enterprise_id field."""
        from apps.auth_app.models import UserProfile
        field = UserProfile._meta.get_field('enterprise_id')
        assert field is not None
        assert field.null is True

    def test_userprofile_can_reference_enterprise_id(self):
        """UserProfile.enterprise_id can store an enterprise id value."""
        from apps.auth_app.models import UserProfile
        user = User.objects.create_user(username='ent_user', password='pass')
        # Signal auto-creates UserProfile, so we update it instead
        profile = user.ent_user_profile
        profile.enterprise_id = 42
        profile.save()
        profile.refresh_from_db()
        assert profile.enterprise_id == 42
