const { test, expect } = require('@playwright/test');

test('Successful login', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.fill('#username', 'tomsmith');
  await page.fill('#password', 'SuperSecretPassword!');
  await page.click('button[type="submit"]');

  try {
    await expect(page.getByRole('heading', { name: 'Welcome to the Secure Area.' })).toBeVisible();
  } catch (error) {
    await page.screenshot({ path: 'test-results/successful-login-failure.png' });
    throw error;
  }
});

test('Invalid login', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.fill('#username', 'invalid');
  await page.fill('#password', 'wrong');
  await page.click('button[type="submit"]');

  try {
    await expect(page.locator('#flash:has-text("Your username is invalid!")')).toBeVisible();
  } catch (error) {
    await page.screenshot({ path: 'test-results/invalid-login-failure.png' });
    throw error;
  }
});

test('Empty fields', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.click('button[type="submit"]');

  try {
    await expect(page.locator('#flash:has-text("Your username is invalid!")')).toBeVisible();
  } catch (error) {
    await page.screenshot({ path: 'test-results/empty-fields-failure.png' });
    throw error;
  }
});