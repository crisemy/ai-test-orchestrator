const { test, expect } = require('@playwright/test');
test('Successful login', async ({ page }) => {
  await page.goto('http://example.com/login');
  await page.fill('#username', 'user');
  await page.fill('#password', 'pass');
  await page.click('#login');
  await expect(page.locator('text=Dashboard')).toBeVisible();
});

test('Invalid login', async ({ page }) => {
  await page.fill('#username', 'invalid');
  await page.fill('#password', 'wrong');
  await expect(page.locator('text=Invalid')).toBeVisible();
});

test('Empty fields', async ({ page }) => {
  await expect(page.locator('text=Required')).toBeVisible();
});