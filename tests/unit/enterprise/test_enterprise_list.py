"""
ENT-002: Enterprise List API unit tests.
Tests cover: normal listing, filtering, keyword search, pagination, desensitization.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.enterprise.models import Enterprise


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
        'auth_status': Enterprise.AuthStatus.VERIFIED,
    }
    defaults.update(overrides)
    return Enterprise(**defaults)


def _create_enterprise(**overrides):
    """Helper to create and return a saved Enterprise instance."""
    ent = _build_enterprise(**overrides)
    ent.save()
    return ent


def _create_batch(count, **overrides):
    """Helper to create a batch of enterprises with unique credit_codes."""
    enterprises = []
    for i in range(count):
        defaults = {
            'name': f'Enterprise {i:03d}',
            'credit_code': f'91MA{i:06d}1X',
        }
        defaults.update(overrides)
        enterprises.append(_create_enterprise(**defaults))
    return enterprises


@pytest.mark.django_db
class TestEnterpriseListAPI:
    """ENT-002: Enterprise List API tests."""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('enterprise:enterprise-list')

    # ==================== Normal listing tests ====================

    def test_list_returns_200(self):
        """GET /ent/enterprise returns 200 OK."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_response_format(self):
        """Response follows the unified format: {code, message, data}."""
        _create_enterprise()
        response = self.client.get(self.url)
        data = response.data
        assert data['code'] == 200
        assert data['message'] == 'success'
        assert 'data' in data
        assert 'items' in data['data']
        assert 'total' in data['data']
        assert 'page' in data['data']
        assert 'page_size' in data['data']

    def test_list_returns_enterprises(self):
        """List endpoint returns created enterprises."""
        _create_batch(3)
        response = self.client.get(self.url)
        assert response.data['data']['total'] == 3

    def test_list_fields_verified_enterprise(self):
        """Verified enterprise returns all required fields with values."""
        _create_enterprise(
            name='Full Info Corp',
            credit_code='91MA01ABCD1234X',
            logo_url='https://example.com/logo.png',
            industry_id=1,
            sub_industry_id=101,
            category_id=5,
            province_id=110000,
            region_id=110100,
            tags=['cloud', 'AI'],
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1
        item = items[0]
        assert item['id'] is not None
        assert item['name'] == 'Full Info Corp'
        assert item['credit_code'] == '91MA01ABCD1234X'
        assert item['logo_url'] == 'https://example.com/logo.png'
        assert item['industry_name'] == ''
        assert item['sub_industry_name'] == ''
        assert item['category_name'] == ''
        assert item['province_name'] == ''
        assert item['region_name'] == ''
        assert item['tags'] == ['cloud', 'AI']
        assert item['auth_status'] == Enterprise.AuthStatus.VERIFIED
        # description should NOT be in list response
        assert 'description' not in item

    # ==================== Default filter tests ====================

    def test_default_filters_verified_only(self):
        """By default, only VERIFIED enterprises are returned."""
        _create_enterprise(
            credit_code='AAA', auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='BBB', auth_status=Enterprise.AuthStatus.UNCLAIMED,
        )
        _create_enterprise(
            credit_code='CCC', auth_status=Enterprise.AuthStatus.PENDING,
        )
        _create_enterprise(
            credit_code='DDD', auth_status=Enterprise.AuthStatus.REJECTED,
        )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['auth_status'] == Enterprise.AuthStatus.VERIFIED

    # ==================== Filtering tests ====================

    def test_filter_by_industry_id(self):
        """Filter by industry_id returns matching enterprises."""
        _create_enterprise(
            credit_code='IND1', industry_id=1, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='IND2', industry_id=2, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'industry_id': 1})
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['id'] is not None

    def test_filter_by_sub_industry_id(self):
        """Filter by sub_industry_id returns matching enterprises."""
        _create_enterprise(
            credit_code='SUB1', sub_industry_id=101, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='SUB2', sub_industry_id=202, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'sub_industry_id': 101})
        items = response.data['data']['items']
        assert len(items) == 1

    def test_filter_by_category_id(self):
        """Filter by category_id returns matching enterprises."""
        _create_enterprise(
            credit_code='CAT1', category_id=5, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='CAT2', category_id=6, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'category_id': 5})
        items = response.data['data']['items']
        assert len(items) == 1

    def test_filter_by_province_id(self):
        """Filter by province_id returns matching enterprises."""
        _create_enterprise(
            credit_code='PV1', province_id=110000, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='PV2', province_id=310000, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'province_id': 110000})
        items = response.data['data']['items']
        assert len(items) == 1

    def test_filter_by_region_id(self):
        """Filter by region_id returns matching enterprises."""
        _create_enterprise(
            credit_code='RG1', region_id=110100, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='RG2', region_id=310100, auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'region_id': 110100})
        items = response.data['data']['items']
        assert len(items) == 1

    def test_filter_by_auth_status_explicit(self):
        """Explicitly passing auth_status overrides default VERIFIED filter."""
        _create_enterprise(
            credit_code='EXP1', auth_status=Enterprise.AuthStatus.PENDING,
        )
        _create_enterprise(
            credit_code='EXP2', auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(
            self.url, {'auth_status': Enterprise.AuthStatus.PENDING},
        )
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['auth_status'] == Enterprise.AuthStatus.PENDING

    def test_multiple_filters_combined(self):
        """Multiple filters applied together work correctly."""
        _create_enterprise(
            credit_code='COMBO1',
            industry_id=1,
            province_id=110000,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='COMBO2',
            industry_id=2,
            province_id=110000,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='COMBO3',
            industry_id=1,
            province_id=310000,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {
            'industry_id': 1,
            'province_id': 110000,
        })
        items = response.data['data']['items']
        assert len(items) == 1

    # ==================== Tags filter tests ====================

    def test_filter_by_single_tag(self):
        """Filter by a single tag returns matching enterprises."""
        _create_enterprise(
            credit_code='TAG1',
            name='Cloud Corp',
            tags=['cloud', 'AI'],
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='TAG2',
            name='Hardware Corp',
            tags=['hardware', 'IoT'],
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'tags': 'cloud'})
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['name'] == 'Cloud Corp'

    def test_filter_by_multiple_tags_comma_separated(self):
        """Filter by multiple comma-separated tags (OR logic)."""
        _create_enterprise(
            credit_code='TM1',
            name='AI Corp',
            tags=['AI'],
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='TM2',
            name='IoT Corp',
            tags=['IoT'],
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='TM3',
            name='Finance Corp',
            tags=['finance'],
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'tags': 'AI,IoT'})
        items = response.data['data']['items']
        assert len(items) == 2
        names = {item['name'] for item in items}
        assert names == {'AI Corp', 'IoT Corp'}

    def test_filter_by_tag_no_match(self):
        """Filter by tag with no matches returns empty items."""
        _create_enterprise(
            credit_code='TN1',
            name='Some Corp',
            tags=['cloud'],
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'tags': 'nonexistent'})
        items = response.data['data']['items']
        assert len(items) == 0

    def test_filter_by_tags_with_none_tags_field(self):
        """Enterprises with null tags field are excluded from tag filter."""
        _create_enterprise(
            credit_code='TN2',
            name='No Tags Corp',
            tags=None,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='TN3',
            name='Has Tags Corp',
            tags=['cloud'],
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'tags': 'cloud'})
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['name'] == 'Has Tags Corp'

    # ==================== Keyword search tests ====================

    def test_keyword_search_by_name(self):
        """Keyword search matches enterprise name (case-insensitive contains)."""
        _create_enterprise(
            credit_code='KW1', name='Beijing Tech Innovation Co',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='KW2', name='Shanghai Data Solutions Ltd',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'keyword': 'Beijing'})
        items = response.data['data']['items']
        assert len(items) == 1
        assert 'Beijing' in items[0]['name']

    def test_keyword_search_by_description(self):
        """Keyword search matches enterprise description."""
        _create_enterprise(
            credit_code='KD1',
            name='Corp Alpha',
            description='Leading cloud computing provider',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='KD2',
            name='Corp Beta',
            description='Hardware manufacturing',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'keyword': 'cloud'})
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['name'] == 'Corp Alpha'

    def test_keyword_search_case_insensitive(self):
        """Keyword search is case-insensitive."""
        _create_enterprise(
            credit_code='KC1', name='UPPERCASE CORP',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'keyword': 'uppercase'})
        items = response.data['data']['items']
        assert len(items) == 1

    def test_keyword_search_no_match(self):
        """Keyword search with no matches returns empty results."""
        _create_enterprise(
            credit_code='KN1', name='Some Company',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {'keyword': 'nonexistent'})
        items = response.data['data']['items']
        assert len(items) == 0
        assert response.data['data']['total'] == 0

    def test_keyword_search_with_filter_combined(self):
        """Keyword search works together with other filters."""
        _create_enterprise(
            credit_code='KFC1',
            name='Beijing Tech',
            description='AI company',
            industry_id=1,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='KFC2',
            name='Beijing Food',
            description='Food delivery',
            industry_id=2,
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url, {
            'keyword': 'Beijing',
            'industry_id': 1,
        })
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['name'] == 'Beijing Tech'

    # ==================== Pagination tests ====================

    def test_default_page_size(self):
        """Default page size is 20."""
        _create_batch(25, auth_status=Enterprise.AuthStatus.VERIFIED)
        response = self.client.get(self.url)
        data = response.data['data']
        assert len(data['items']) == 20
        assert data['total'] == 25
        assert data['page'] == 1
        assert data['page_size'] == 20

    def test_custom_page_size(self):
        """Custom page_size parameter works."""
        _create_batch(10, auth_status=Enterprise.AuthStatus.VERIFIED)
        response = self.client.get(self.url, {'page_size': 5})
        data = response.data['data']
        assert len(data['items']) == 5
        assert data['total'] == 10

    def test_page_2(self):
        """Page 2 returns correct subset."""
        _create_batch(25, auth_status=Enterprise.AuthStatus.VERIFIED)
        response = self.client.get(self.url, {'page': 2, 'page_size': 10})
        data = response.data['data']
        assert len(data['items']) == 10
        assert data['total'] == 25
        assert data['page'] == 2
        assert data['page_size'] == 10

    def test_page_beyond_range(self):
        """Requesting page beyond range returns empty items with total count."""
        _create_batch(5, auth_status=Enterprise.AuthStatus.VERIFIED)
        response = self.client.get(self.url, {'page': 999})
        data = response.data['data']
        assert data['items'] == []
        assert data['total'] == 5
        assert data['page'] == 999

    def test_pagination_metadata_format(self):
        """Pagination response uses DESN format: total, page, page_size, items."""
        _create_batch(25, auth_status=Enterprise.AuthStatus.VERIFIED)
        response = self.client.get(self.url, {'page_size': 10})
        data = response.data['data']
        assert data['total'] == 25
        assert data['page'] == 1
        assert data['page_size'] == 10
        assert 'items' in data
        # Old format fields should NOT be present
        assert 'count' not in data
        assert 'next' not in data
        assert 'previous' not in data
        assert 'results' not in data

    def test_response_code_is_200(self):
        """Response code field should be 200 (not 0)."""
        _create_enterprise()
        response = self.client.get(self.url)
        assert response.data['code'] == 200

    # ==================== Desensitization tests ====================

    def test_verified_enterprise_full_info(self):
        """VERIFIED enterprise returns all fields with actual values."""
        _create_enterprise(
            credit_code='FULL',
            name='Full Corp',
            logo_url='https://example.com/logo.png',
            industry_id=1,
            sub_industry_id=101,
            category_id=5,
            province_id=110000,
            region_id=110100,
            tags=['AI'],
            description='Full description',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(
            self.url, {'auth_status': Enterprise.AuthStatus.VERIFIED},
        )
        item = response.data['data']['items'][0]
        assert item['name'] == 'Full Corp'
        assert item['credit_code'] == 'FULL'
        assert item['logo_url'] == 'https://example.com/logo.png'
        assert item['tags'] == ['AI']
        # description should NOT be in list response
        assert 'description' not in item

    def test_unclaimed_enterprise_desensitized(self):
        """UNCLAIMED enterprise returns only id, name, auth_status; other fields null/empty."""
        _create_enterprise(
            credit_code='UNCL',
            name='Unclaimed Corp',
            logo_url='https://example.com/logo.png',
            description='Secret info',
            tags=['secret'],
            auth_status=Enterprise.AuthStatus.UNCLAIMED,
        )
        response = self.client.get(
            self.url, {'auth_status': Enterprise.AuthStatus.UNCLAIMED},
        )
        item = response.data['data']['items'][0]
        assert item['name'] == 'Unclaimed Corp'
        assert item['auth_status'] == Enterprise.AuthStatus.UNCLAIMED
        assert item['id'] is not None
        # Desensitized fields should be null or empty
        assert item['credit_code'] is None
        assert item['logo_url'] is None or item['logo_url'] == ''
        assert item['industry_name'] == ''
        assert item['sub_industry_name'] == ''
        assert item['category_name'] == ''
        assert item['province_name'] == ''
        assert item['region_name'] == ''
        assert item['tags'] is None or item['tags'] == [] or item['tags'] == ''
        # description should NOT be in list response at all
        assert 'description' not in item

    def test_pending_enterprise_desensitized(self):
        """PENDING enterprise returns only id, name, auth_status; other fields null/empty."""
        _create_enterprise(
            credit_code='PEND',
            name='Pending Corp',
            logo_url='https://example.com/logo.png',
            description='Pending info',
            tags=['pending'],
            auth_status=Enterprise.AuthStatus.PENDING,
        )
        response = self.client.get(
            self.url, {'auth_status': Enterprise.AuthStatus.PENDING},
        )
        item = response.data['data']['items'][0]
        assert item['name'] == 'Pending Corp'
        assert item['auth_status'] == Enterprise.AuthStatus.PENDING
        assert item['id'] is not None
        # Desensitized
        assert item['credit_code'] is None
        assert item['logo_url'] is None or item['logo_url'] == ''
        assert 'description' not in item

    def test_rejected_enterprise_desensitized(self):
        """REJECTED enterprise returns only id, name, auth_status; other fields null/empty."""
        _create_enterprise(
            credit_code='REJ',
            name='Rejected Corp',
            logo_url='https://example.com/logo.png',
            description='Rejected info',
            auth_status=Enterprise.AuthStatus.REJECTED,
        )
        response = self.client.get(
            self.url, {'auth_status': Enterprise.AuthStatus.REJECTED},
        )
        item = response.data['data']['items'][0]
        assert item['name'] == 'Rejected Corp'
        assert item['auth_status'] == Enterprise.AuthStatus.REJECTED
        assert item['id'] is not None
        assert item['credit_code'] is None
        assert item['logo_url'] is None or item['logo_url'] == ''
        assert 'description' not in item

    def test_mixed_auth_statuses_desensitization(self):
        """Mix of VERIFIED and non-VERIFIED: VERIFIED full, others desensitized."""
        _create_enterprise(
            credit_code='MIX1',
            name='Verified Corp',
            description='Visible',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        _create_enterprise(
            credit_code='MIX2',
            name='Pending Corp',
            description='Hidden',
            auth_status=Enterprise.AuthStatus.PENDING,
        )
        # Test with explicit single non-default status
        response = self.client.get(
            self.url, {'auth_status': Enterprise.AuthStatus.PENDING},
        )
        items = response.data['data']['items']
        assert len(items) == 1
        assert items[0]['credit_code'] is None
        assert 'description' not in items[0]

    # ==================== Empty result tests ====================

    def test_empty_list(self):
        """No enterprises returns empty items with total 0."""
        response = self.client.get(self.url)
        data = response.data['data']
        assert data['total'] == 0
        assert data['items'] == []

    # ==================== Permission tests ====================

    def test_no_auth_required(self):
        """Enterprise list is a public endpoint, no authentication needed."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    # ==================== Ordering tests ====================

    def test_default_ordering_by_created_at_desc(self):
        """Enterprises are ordered by created_at descending by default."""
        import time
        ent1 = _create_enterprise(
            credit_code='ORD1', name='First Created',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        time.sleep(0.01)
        ent2 = _create_enterprise(
            credit_code='ORD2', name='Second Created',
            auth_status=Enterprise.AuthStatus.VERIFIED,
        )
        response = self.client.get(self.url)
        items = response.data['data']['items']
        assert items[0]['name'] == 'Second Created'
        assert items[1]['name'] == 'First Created'
