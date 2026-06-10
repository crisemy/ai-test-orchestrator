import { test, expect } from '@playwright/test';

test('UI Testing Lab loads and shows login section', async ({ page }) => {
  await page.goto('/playwright-ui-testing-lab.html');
  await expect(page.locator('text=Form Authentication').first()).toBeVisible();
});

test('Login form elements are present', async ({ page }) => {
  await page.goto('/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await expect(page.locator('#login-username')).toBeVisible();
  await expect(page.locator('#login-password')).toBeVisible();
  await expect(page.locator('#login-btn')).toBeVisible();
});

test('Successful login flow', async ({ page }) => {
  await page.goto('/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.fill('#login-username', 'tomsmith');
  await page.fill('#login-password', 'SuperSecretPassword!');
  await page.click('#login-btn');
  await expect(page.locator('#login-alert .alert-success')).toBeVisible();
});

test('Invalid login shows error', async ({ page }) => {
  await page.goto('/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.fill('#login-username', 'invalid');
  await page.fill('#login-password', 'wrong');
  await page.click('#login-btn');
  await expect(page.locator('#login-alert .alert-error')).toBeVisible();
});
