const { test, expect } = require('@playwright/test');

test('Successful login', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.fill('#username', 'tomsmith');
  await page.fill('#password', 'SuperSecretPassword!');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/secure/);
  await expect(page.locator('.flash.success')).toContainText('You logged into a secure area!');
});

test('Invalid login', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.fill('#username', 'tomsmith');
  await page.fill('#password', 'wrong');
  await page.click('button[type="submit"]');

  await expect(page.locator('.flash.error')).toContainText('Your password is invalid!');
});

test('Empty fields', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');
  await page.click('button[type="submit"]');

  await expect(page.locator('.flash.error')).toContainText('Your username is invalid!');
});