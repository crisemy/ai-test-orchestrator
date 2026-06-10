import pytest
import tempfile
import os
import json


@pytest.fixture(autouse=True)
def reset_rate_limit_state():
    from orchestrator import _rate_limit_state
    _rate_limit_state["call_timestamps"] = []
    yield


@pytest.fixture
def sample_valid_code():
    return """import { test, expect } from '@playwright/test';

test('Successful login', async ({ page }) => {
  await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.fill('#login-username', 'tomsmith');
  await page.fill('#login-password', 'SuperSecretPassword!');
  await page.click('#login-btn');
  await expect(page.locator('#login-alert .alert-success')).toBeVisible();
});

test('Invalid login', async ({ page }) => {
  await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.fill('#login-username', 'invalid');
  await page.fill('#login-password', 'wrong');
  await page.click('#login-btn');
  await expect(page.locator('#login-alert .alert-error')).toBeVisible();
});

test('Empty fields', async ({ page }) => {
  await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.click('#login-btn');
  await expect(page.locator('#login-result')).toContainText('missing credentials');
});"""


@pytest.fixture
def temp_backup_dir():
    from orchestrator import BACKUP_DIR
    original = BACKUP_DIR
    tmp = tempfile.mkdtemp()
    import orchestrator
    orchestrator.BACKUP_DIR = tmp
    yield tmp
    orchestrator.BACKUP_DIR = original
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
