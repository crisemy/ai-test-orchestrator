# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: generated-tests\login.spec.js >> Invalid login
- Location: generated-tests\login.spec.js:12:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Your username is invalid! credentials')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=Your username is invalid! credentials')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e4]:
    - link "Fork me on GitHub":
      - /url: https://github.com/tourdedave/the-internet
      - img "Fork me on GitHub" [ref=e5] [cursor=pointer]
    - generic [ref=e7]:
      - heading "Login Page" [level=2] [ref=e8]
      - heading "This is where you can log into the secure area. Enter tomsmith for the username and SuperSecretPassword! for the password. If the information is wrong you should see error messages." [level=4] [ref=e9]:
        - text: This is where you can log into the secure area. Enter
        - emphasis [ref=e10]: tomsmith
        - text: for the username and
        - emphasis [ref=e11]: SuperSecretPassword!
        - text: for the password. If the information is wrong you should see error messages.
      - generic [ref=e12]:
        - generic [ref=e14]:
          - generic [ref=e15] [cursor=pointer]: Username
          - textbox "Username" [ref=e16]: invalid
        - generic [ref=e18]:
          - generic [ref=e19] [cursor=pointer]: Password
          - textbox "Password" [ref=e20]: wrong
        - button " Login" [ref=e21] [cursor=pointer]:
          - generic [ref=e22]:  Login
  - generic [ref=e24]:
    - separator [ref=e25]
    - generic [ref=e26]:
      - text: Powered by
      - link "Elemental Selenium" [ref=e27] [cursor=pointer]:
        - /url: http://elementalselenium.com/
```

# Test source

```ts
  1  | const { test, expect } = require('@playwright/test');
  2  | 
  3  | test('Successful login', async ({ page }) => {
  4  |   await page.goto('https://the-internet.herokuapp.com/login');
  5  |   await page.fill('#username', 'user');
  6  |   await page.fill('#password', 'pass');
  7  |   await page.click('#login');
  8  | 
  9  |   await expect(page.locator('text=You logged into a secure area!')).toBeVisible();
  10 | });
  11 | 
  12 | test('Invalid login', async ({ page }) => {
  13 |   await page.goto('https://the-internet.herokuapp.com/login');
  14 |   await page.fill('#username', 'invalid');
  15 |   await page.fill('#password', 'wrong');
  16 |   await page.click('#login');
  17 | 
> 18 |   await expect(page.locator('text=Your username is invalid! credentials')).toBeVisible();
     |                                                                            ^ Error: expect(locator).toBeVisible() failed
  19 | });
  20 | 
  21 | test('Empty fields', async ({ page }) => {
  22 |   await page.goto('https://the-internet.herokuapp.com/login');
  23 |   await page.click('#login');
  24 | 
  25 |   await expect(page.locator('text=Username is required')).toBeVisible();
  26 |   await expect(page.locator('text=Password is required')).toBeVisible();
  27 | });
```