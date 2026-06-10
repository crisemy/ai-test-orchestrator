from orchestrator import normalize_code


class TestNormalizeCode:

    def test_removes_markdown_fences(self):
        code = "```typescript\nconst x = 1;\n```"
        result = normalize_code(code)
        assert "```" not in result
        assert "const x = 1;" in result

    def test_fixes_await_const(self):
        code = "await const x = await page.goto('http://example.com');"
        result = normalize_code(code)
        assert "await const" not in result
        assert "const x" in result

    def test_replaces_invalid_urls(self):
        code = "await page.goto('https://example.com/login');"
        result = normalize_code(code)
        assert "example.com" not in result
        assert "localhost:3000" in result

    def test_replaces_your_website_url(self):
        code = "await page.goto('https://your-website.com/test');"
        result = normalize_code(code)
        assert "your-website" not in result
        assert "localhost:3000" in result

    def test_preserves_valid_url(self):
        code = "await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');"
        result = normalize_code(code)
        assert "localhost:3000/playwright-ui-testing-lab.html" in result

    def test_fixes_username_selector(self):
        code = "page.fill('#username', 'tomsmith')"
        result = normalize_code(code)
        assert "#login-username" in result

    def test_does_not_double_fix_login_username(self):
        code = "page.fill('#login-username', 'tomsmith')"
        result = normalize_code(code)
        assert "#login-login-username" not in result
        assert "#login-username" in result

    def test_fixes_password_selector(self):
        code = "page.fill('#password', 'secret')"
        result = normalize_code(code)
        assert "#login-password" in result

    def test_does_not_double_fix_login_password(self):
        code = "page.fill('#login-password', 'secret')"
        result = normalize_code(code)
        assert "#login-login-password" not in result
        assert "#login-password" in result

    def test_fixes_login_button_selector(self):
        code = "page.click('#login);"
        result = normalize_code(code)
        assert "#login-btn" in result

    def test_does_not_break_login_username_with_btn_fix(self):
        code = "page.fill('#login-username', 'tomsmith')"
        result = normalize_code(code)
        assert "#login-username" in result

    def test_replaces_text_dashboard_with_selector(self):
        code = "await expect(page.locator('text=Dashboard')).toBeVisible();"
        result = normalize_code(code)
        assert "text=Dashboard" not in result
        # text=Dashboard → #login-result, then garbage assertion regex catches toBeVisible
        assert "#login-alert .alert-error" in result

    def test_replaces_text_invalid_with_selector(self):
        code = "await expect(page.locator('text=Invalid')).toBeVisible();"
        result = normalize_code(code)
        assert "text=Invalid" not in result
        assert "#login-alert .alert-error" in result

    def test_replaces_text_required_with_selector(self):
        code = "await expect(page.locator('text=Required')).toBeVisible();"
        result = normalize_code(code)
        assert "text=Required" not in result
        # text=Required → #login-result, then garbage assertion regex catches toBeVisible
        assert "#login-alert .alert-error" in result

    def test_preserves_alert_success_assertion(self):
        code = "await expect(page.locator('#login-alert .alert-success')).toBeVisible();"
        result = normalize_code(code)
        assert "#login-alert .alert-success" in result
        assert "#login-alert .alert-error" not in result

    def test_preserves_alert_error_assertion(self):
        code = "await expect(page.locator('#login-alert .alert-error')).toBeVisible();"
        result = normalize_code(code)
        assert "#login-alert .alert-error" in result

    def test_replaces_generic_assertion(self):
        code = "await expect(page.locator('#some-random-element')).toBeVisible();"
        result = normalize_code(code)
        assert "#login-alert .alert-error" in result

    def test_converts_toHaveText_to_toContainText(self):
        code = "await expect(page.locator('#login-result')).toHaveText('ok');"
        result = normalize_code(code)
        assert ".toContainText" in result
        assert ".toHaveText" not in result

    def test_injects_form_authentication_click(self):
        code = """await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.fill('#login-username', 'tomsmith');"""
        result = normalize_code(code)
        assert "text=Form Authentication" in result
        assert "page.click" in result

    def test_skips_form_authentication_if_already_present(self):
        code = """await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.fill('#login-username', 'tomsmith');"""
        result = normalize_code(code)
        assert result.count("text=Form Authentication") == 1

    def test_skips_form_authentication_if_section_login_present(self):
        code = """await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.locator('#section-login').click();
  await page.fill('#login-username', 'tomsmith');"""
        result = normalize_code(code)
        assert "#section-login" in result

    def test_preserves_already_valid_code(self):
        result = normalize_code(self.sample_valid_code())
        assert "localhost:3000" in result
        assert "test(" in result
        assert "Form Authentication" in result

    def test_handles_empty_string(self):
        result = normalize_code("")
        assert result == ""

    def test_handles_code_without_goto(self):
        code = "const x = 1;"
        result = normalize_code(code)
        assert "const x = 1;" in result

    def test_handles_multiple_markdown_fences(self):
        code = "```\ncode here\n```\nmore\n```\n"
        result = normalize_code(code)
        assert "```" not in result
        assert "code here" in result
        assert "more" in result

    @staticmethod
    def sample_valid_code():
        return """import { test, expect } from '@playwright/test';

test('Successful login', async ({ page }) => {
  await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.fill('#login-username', 'tomsmith');
  await page.fill('#login-password', 'SuperSecretPassword!');
  await page.click('#login-btn');
  await expect(page.locator('#login-alert .alert-success')).toBeVisible();
});"""
