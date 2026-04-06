const { test, expect } = require('@playwright/test');

test('Successful login', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.fill('#username', 'user');
  await page.fill('#password', 'pass');
  await page.click('button[type="submit"]');

  await expect(page.locator('#flash')).toBeVisible();
});

test('Invalid login', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.fill('#username', 'invalid');
  await page.fill('#password', 'wrong');
  await page.click('button[type="submit"]');

  await expect(page.locator('#flash')).toBeVisible();
});

test('Empty fields', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.click('button[type="submit"]');

  await expect(page.locator('#flash')).toBeVisible();
});