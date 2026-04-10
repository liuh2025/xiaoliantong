"""
E2E Test Shared Configuration and Fixtures
"""
import pytest
import os
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, BrowserContext


BASE_URL = os.environ.get('E2E_BASE_URL', 'http://localhost:3000')
API_URL = os.environ.get('E2E_API_URL', 'http://localhost:8000')
SCREENSHOT_DIR = None


def pytest_configure(config):
    global SCREENSHOT_DIR
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    SCREENSHOT_DIR = Path(f"tests/e2e/screenshots/{timestamp}")
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def screenshot_dir():
    return SCREENSHOT_DIR


@pytest.fixture
def page_with_utils(page, screenshot_dir):
    """Page with screenshot utility attached."""
    page.screenshot_dir = screenshot_dir
    yield page


def take_screenshot(page, test_id: str, result: str, detail: str = None):
    """Take a screenshot and save to the timestamped directory."""
    if detail:
        filename = f"{test_id}-{result}-{detail}.png"
    else:
        filename = f"{test_id}-{result}.png"
    path = SCREENSHOT_DIR / filename
    page.screenshot(path=str(path), full_page=True)
    return str(path)


def login_via_api(page: Page, phone: str = '13800000001', password: str = 'Admin123!'):
    """Login by injecting auth tokens directly into localStorage."""
    import json
    import urllib.request

    # Call password login API
    data = json.dumps({'phone': phone, 'password': password}).encode()
    req = urllib.request.Request(
        f'{API_URL}/api/v1/auth/login/password/',
        data=data,
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except Exception:
        return False

    if result.get('code') != 0:
        return False

    token_data = result['data']
    role_code = token_data.get('role_code', 'guest')

    # Build user_info with enterprise_id for enterprise_admin users
    enterprise_id = 'null'
    # Known test users mapping
    known_users = {
        '13900001111': {'enterprise_id': 1},
        '13800000001': {'enterprise_id': None},
    }
    if phone in known_users and known_users[phone]['enterprise_id']:
        enterprise_id = known_users[phone]['enterprise_id']

    # Must navigate to the app domain first to set localStorage
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')

    # Inject into localStorage
    page.evaluate(f"""() => {{
        localStorage.setItem('access_token', '{token_data['access_token']}');
        localStorage.setItem('refresh_token', '{token_data['refresh_token']}');
        const userInfo = {{
            id: {token_data['user_id']},
            phone: '{phone}',
            role_code: '{role_code}',
            enterprise_id: {enterprise_id},
        }};
        localStorage.setItem('user_info', JSON.stringify(userInfo));
    }}""")

    # Reload page so Vue auth store picks up the localStorage values
    page.reload()
    page.wait_for_load_state('networkidle')
    # Wait for Vue store initialization to complete
    page.wait_for_timeout(1000)

    return True
