"""
OPP-001: Opportunity & ContactLog model unit tests.
Tests cover model creation, field constraints, choices, ordering, and FK relationships.
"""
import itertools

import pytest
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from apps.enterprise.models import Enterprise
from apps.opportunity.models import Opportunity, ContactLog

_counter = itertools.count(1)


def _unique_int():
    """Return a monotonically increasing unique integer for test data."""
    return next(_counter)


def _build_enterprise(**overrides):
    """Helper to build and save a valid Enterprise instance with unique defaults."""
    n = _unique_int()
    defaults = {
        'name': f'Test Enterprise {n}',
        'credit_code': f'91{n:014d}X',
        'legal_representative': 'Zhang San',
        'business_license': f'https://example.com/license/test{n}.jpg',
        'industry_id': 1,
        'sub_industry_id': 101,
        'province_id': 110000,
        'region_id': 110100,
    }
    defaults.update(overrides)
    ent = Enterprise(**defaults)
    ent.save()
    return ent


def _build_user(**overrides):
    """Helper to create and return a User instance with unique username."""
    n = _unique_int()
    defaults = {'username': f'testuser_{n}', 'password': 'testpass123'}
    defaults.update(overrides)
    return User.objects.create_user(**defaults)


def _build_opportunity(**overrides):
    """Helper to build a valid Opportunity instance with sensible defaults."""
    if 'enterprise' not in overrides:
        overrides['enterprise'] = _build_enterprise()
    if 'publisher' not in overrides:
        overrides['publisher'] = _build_user()
    defaults = {
        'type': Opportunity.OppType.BUY,
        'title': 'Test Opportunity',
        'industry_id': 1,
        'sub_industry_id': 101,
        'category_id': 5,
        'province_id': 110000,
        'region_id': 110100,
        'detail': 'This is a test opportunity detail.',
    }
    defaults.update(overrides)
    return Opportunity(**defaults)


def _create_opportunity(**overrides):
    """Helper to create and return a saved Opportunity instance."""
    opp = _build_opportunity(**overrides)
    opp.save()
    return opp


@pytest.mark.django_db
class TestOpportunityModel:
    """Opportunity model unit tests."""

    # ---- creation tests ----

    def test_create_opportunity_with_required_fields_only(self):
        """Opportunity can be created with all required fields and no optional fields."""
        opp = _build_opportunity()
        opp.save()
        assert opp.id is not None
        assert opp.type == Opportunity.OppType.BUY
        assert opp.title == 'Test Opportunity'
        assert opp.industry_id == 1
        assert opp.sub_industry_id == 101
        assert opp.category_id == 5
        assert opp.province_id == 110000
        assert opp.region_id == 110100
        assert opp.detail == 'This is a test opportunity detail.'
        assert opp.status == Opportunity.OppStatus.ACTIVE
        assert opp.view_count == 0
        assert opp.created_at is not None
        assert opp.updated_at is not None

    def test_create_opportunity_with_all_optional_fields(self):
        """Opportunity can be created with optional fields populated."""
        ent = _build_enterprise()
        user = _build_user()
        opp = _create_opportunity(
            enterprise=ent,
            publisher=user,
            tags=['cloud', 'AI'],
            contact_name='Li Si',
            contact_phone='13800138000',
            contact_wechat='test_wechat',
        )
        assert opp.tags == ['cloud', 'AI']
        assert opp.contact_name == 'Li Si'
        assert opp.contact_phone == '13800138000'
        assert opp.contact_wechat == 'test_wechat'

    def test_optional_fields_default_to_empty(self):
        """Optional fields default to empty/zero when not provided."""
        opp = _create_opportunity()
        assert opp.tags == []
        assert opp.contact_name == ''
        assert opp.contact_phone == ''
        assert opp.contact_wechat == ''
        assert opp.view_count == 0

    # ---- field constraint tests ----

    def test_type_is_required(self):
        """type field is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(type=None)

    def test_title_is_required(self):
        """title field is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(title=None)

    def test_enterprise_fk_is_required(self):
        """enterprise FK is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(enterprise=None)

    def test_publisher_fk_is_required(self):
        """publisher FK is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(publisher=None)

    def test_industry_id_is_required(self):
        """industry_id field is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(industry_id=None)

    def test_sub_industry_id_is_required(self):
        """sub_industry_id field is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(sub_industry_id=None)

    def test_category_id_is_required(self):
        """category_id field is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(category_id=None)

    def test_province_id_is_required(self):
        """province_id field is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(province_id=None)

    def test_region_id_is_required(self):
        """region_id field is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(region_id=None)

    def test_detail_is_required(self):
        """detail field is required."""
        with pytest.raises(IntegrityError):
            _create_opportunity(detail=None)

    # ---- choices tests ----

    def test_type_choices(self):
        """type accepts all defined choices."""
        for type_val in [Opportunity.OppType.BUY, Opportunity.OppType.SUPPLY]:
            opp = _create_opportunity(
                type=type_val,
                title=f'Test {type_val}',
            )
            opp.refresh_from_db()
            assert opp.type == type_val

    def test_status_choices(self):
        """status accepts all defined choices."""
        for status_val in [Opportunity.OppStatus.ACTIVE, Opportunity.OppStatus.OFFLINE]:
            opp = _create_opportunity(
                status=status_val,
                title=f'Test {status_val}',
            )
            opp.refresh_from_db()
            assert opp.status == status_val

    def test_status_default_is_active(self):
        """Default status should be ACTIVE."""
        opp = _create_opportunity()
        assert opp.status == Opportunity.OppStatus.ACTIVE

    # ---- FK relationship tests ----

    def test_enterprise_fk_links_to_enterprise(self):
        """enterprise FK correctly links to Enterprise model."""
        ent = _build_enterprise(name='FK Test Corp')
        opp = _create_opportunity(enterprise=ent)
        assert opp.enterprise == ent
        assert opp.enterprise.name == 'FK Test Corp'

    def test_publisher_fk_links_to_user(self):
        """publisher FK correctly links to auth.User."""
        user = _build_user(username='pub_user')
        opp = _create_opportunity(publisher=user)
        assert opp.publisher == user
        assert opp.publisher.username == 'pub_user'

    def test_enterprise_protect_on_delete(self):
        """Deleting an enterprise with opportunities is blocked (PROTECT)."""
        from django.db.models import ProtectedError
        ent = _build_enterprise()
        _create_opportunity(enterprise=ent)
        with pytest.raises(ProtectedError):
            ent.delete()

    def test_publisher_protect_on_delete(self):
        """Deleting a publisher user with opportunities is blocked (PROTECT)."""
        from django.db.models import ProtectedError
        user = _build_user(username='protected_pub')
        _create_opportunity(publisher=user)
        with pytest.raises(ProtectedError):
            user.delete()

    def test_related_opportunities_on_enterprise(self):
        """Enterprise can access related opportunities via reverse relation."""
        ent = _build_enterprise()
        _create_opportunity(enterprise=ent, title='Opp 1')
        _create_opportunity(enterprise=ent, title='Opp 2')
        related = ent.opportunities.all()
        assert related.count() == 2

    def test_related_opportunities_on_user(self):
        """User can access related published opportunities via reverse relation."""
        user = _build_user(username='multi_pub')
        _create_opportunity(publisher=user, title='Opp A')
        _create_opportunity(publisher=user, title='Opp B')
        related = user.published_opportunities.all()
        assert related.count() == 2

    # ---- meta tests ----

    def test_db_table_name(self):
        """Model uses the correct db_table name."""
        assert Opportunity._meta.db_table == 'opp_opportunity'

    def test_ordering(self):
        """Default ordering is by -created_at."""
        assert Opportunity._meta.ordering == ['-created_at']

    def test_str_representation(self):
        """__str__ returns the opportunity title."""
        opp = _create_opportunity(title='My Opportunity')
        assert str(opp) == 'My Opportunity'

    def test_auto_timestamps(self):
        """created_at and updated_at are auto-populated."""
        opp = _create_opportunity()
        assert opp.created_at is not None
        assert opp.updated_at is not None


@pytest.mark.django_db
class TestContactLogModel:
    """ContactLog model unit tests."""

    def _create_contact_log(self, **overrides):
        """Helper to create and return a saved ContactLog instance."""
        if 'opportunity' not in overrides:
            overrides['opportunity'] = _create_opportunity()
        if 'getter_user' not in overrides:
            overrides['getter_user'] = _build_user()
        if 'getter_enterprise' not in overrides:
            overrides['getter_enterprise'] = _build_enterprise()
        defaults = {
            'status': ContactLog.ContactStatus.COMPLETED,
        }
        defaults.update(overrides)
        log = ContactLog(**defaults)
        log.save()
        return log

    # ---- creation tests ----

    def test_create_contact_log_with_all_fields(self):
        """ContactLog can be created with all fields."""
        log = self._create_contact_log()
        assert log.id is not None
        assert log.status == ContactLog.ContactStatus.COMPLETED
        assert log.created_at is not None

    def test_status_default_is_completed(self):
        """Default status should be COMPLETED."""
        opp = _create_opportunity()
        user = _build_user()
        ent = _build_enterprise()
        log = ContactLog(
            opportunity=opp,
            getter_user=user,
            getter_enterprise=ent,
        )
        log.save()
        assert log.status == ContactLog.ContactStatus.COMPLETED

    # ---- field constraint tests ----

    def test_opportunity_fk_is_required(self):
        """opportunity FK is required."""
        with pytest.raises(IntegrityError):
            self._create_contact_log(opportunity=None)

    def test_getter_user_fk_is_required(self):
        """getter_user FK is required."""
        with pytest.raises(IntegrityError):
            self._create_contact_log(getter_user=None)

    def test_getter_enterprise_fk_is_required(self):
        """getter_enterprise FK is required."""
        with pytest.raises(IntegrityError):
            self._create_contact_log(getter_enterprise=None)

    def test_status_is_required(self):
        """status field is required."""
        with pytest.raises(IntegrityError):
            self._create_contact_log(status=None)

    # ---- choices tests ----

    def test_status_choices(self):
        """status accepts all defined choices."""
        opp = _create_opportunity()
        user = _build_user()
        ent = _build_enterprise()
        for status_val in [
            ContactLog.ContactStatus.INITIATED,
            ContactLog.ContactStatus.CONFIRMED,
            ContactLog.ContactStatus.COMPLETED,
            ContactLog.ContactStatus.CANCELLED,
        ]:
            log = ContactLog(
                opportunity=opp,
                getter_user=user,
                getter_enterprise=ent,
                status=status_val,
            )
            log.save()
            log.refresh_from_db()
            assert log.status == status_val

    # ---- FK relationship tests ----

    def test_opportunity_cascade_on_delete(self):
        """Deleting opportunity cascades and deletes related contact logs."""
        log = self._create_contact_log()
        log_id = log.id
        log.opportunity.delete()
        assert not ContactLog.objects.filter(id=log_id).exists()

    def test_getter_user_protect_on_delete(self):
        """Deleting getter_user is blocked if contact logs exist (PROTECT)."""
        from django.db.models import ProtectedError
        user = _build_user()
        self._create_contact_log(getter_user=user)
        with pytest.raises(ProtectedError):
            user.delete()

    def test_getter_enterprise_protect_on_delete(self):
        """Deleting getter_enterprise is blocked if contact logs exist (PROTECT)."""
        from django.db.models import ProtectedError
        ent = _build_enterprise()
        self._create_contact_log(getter_enterprise=ent)
        with pytest.raises(ProtectedError):
            ent.delete()

    def test_multiple_contact_logs_for_opportunity(self):
        """Multiple contact logs can exist for one opportunity."""
        opp = _create_opportunity()
        user1 = _build_user()
        user2 = _build_user()
        ent1 = _build_enterprise()
        ent2 = _build_enterprise()
        ContactLog.objects.create(
            opportunity=opp,
            getter_user=user1,
            getter_enterprise=ent1,
            status=ContactLog.ContactStatus.COMPLETED,
        )
        ContactLog.objects.create(
            opportunity=opp,
            getter_user=user2,
            getter_enterprise=ent2,
            status=ContactLog.ContactStatus.INITIATED,
        )
        assert opp.contact_logs.count() == 2

    def test_related_contacts_on_user(self):
        """User can access related contacts via reverse relation."""
        user = _build_user()
        ent = _build_enterprise()
        self._create_contact_log(getter_user=user, getter_enterprise=ent)
        assert user.opp_contacts.count() == 1

    def test_related_contacts_on_enterprise(self):
        """Enterprise can access related contacts via reverse relation."""
        ent = _build_enterprise()
        user = _build_user()
        self._create_contact_log(getter_user=user, getter_enterprise=ent)
        assert ent.opp_contacts.count() == 1

    # ---- meta tests ----

    def test_db_table_name(self):
        """Model uses the correct db_table name."""
        assert ContactLog._meta.db_table == 'opp_contact_log'

    def test_ordering(self):
        """Default ordering is by -created_at."""
        assert ContactLog._meta.ordering == ['-created_at']

    def test_str_representation(self):
        """__str__ returns meaningful info."""
        opp = _create_opportunity(title='StrTest Opp')
        log = self._create_contact_log(opportunity=opp)
        result = str(log)
        assert 'StrTest Opp' in result
