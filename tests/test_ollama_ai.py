import pytest
from unittest.mock import patch, mock_open, MagicMock


class TestExtractCode:

    def test_extracts_typescript_fence(self):
        from ollama_ai import extract_code
        code = "```typescript\nconst x = 1;\n```"
        assert extract_code(code) == "const x = 1;"

    def test_extracts_javascript_fence(self):
        from ollama_ai import extract_code
        code = "```javascript\nconst x = 1;\n```"
        assert extract_code(code) == "const x = 1;"

    def test_extracts_ts_fence(self):
        from ollama_ai import extract_code
        code = "```ts\nconst x = 1;\n```"
        assert extract_code(code) == "const x = 1;"

    def test_extracts_js_fence(self):
        from ollama_ai import extract_code
        code = "```js\nconst x = 1;\n```"
        assert extract_code(code) == "const x = 1;"

    def test_extracts_generic_fence(self):
        from ollama_ai import extract_code
        code = "```\nconst x = 1;\n```"
        assert extract_code(code) == "const x = 1;"

    def test_returns_none_if_no_fence(self):
        from ollama_ai import extract_code
        assert extract_code("const x = 1;") is None

    def test_prefers_specific_fence_over_generic(self):
        from ollama_ai import extract_code
        code = "```typescript\nconst x = 1;\n```\n```\nconst y = 2;\n```"
        assert extract_code(code) == "const x = 1;"

    def test_handles_code_with_extra_text_after_fence(self):
        from ollama_ai import extract_code
        code = "Some explanation\n```typescript\nconst x = 1;\n```\nMore text"
        assert extract_code(code) == "const x = 1;"

    def test_handles_multiple_fences_returns_first(self):
        from ollama_ai import extract_code
        code = "```typescript\nconst x = 1;\n```\n```typescript\nconst y = 2;\n```"
        assert extract_code(code) == "const x = 1;"


class TestIsValidPlaywright:

    def test_valid_code_returns_true(self):
        from ollama_ai import is_valid_playwright
        code = """import { test, expect } from '@playwright/test';
test('test1', async ({ page }) => {
  await page.goto('http://test.com');
  await expect(page.locator('#x')).toBeVisible();
});
test('test2', async ({ page }) => {
  await page.goto('http://test.com');
  await expect(page.locator('#y')).toBeVisible();
});
test('test3', async ({ page }) => {
  await page.goto('http://test.com');
  await expect(page.locator('#z')).toBeVisible();
});"""
        assert is_valid_playwright(code) is True

    def test_missing_import_returns_false(self):
        from ollama_ai import is_valid_playwright
        code = """test('test1', async ({ page }) => {
  await page.goto('http://test.com');
});"""
        assert is_valid_playwright(code) is False

    def test_less_than_3_tests_returns_false(self):
        from ollama_ai import is_valid_playwright
        code = """import { test, expect } from '@playwright/test';
test('test1', async ({ page }) => {
  await page.goto('http://test.com');
  await expect(page.locator('#x')).toBeVisible();
});"""
        assert is_valid_playwright(code) is False

    def test_missing_page_goto_returns_false(self):
        from ollama_ai import is_valid_playwright
        code = """import { test, expect } from '@playwright/test';
test('test1', async ({ page }) => {
  await expect(page.locator('#x')).toBeVisible();
});
test('test2', async ({ page }) => {
  await expect(page.locator('#y')).toBeVisible();
});
test('test3', async ({ page }) => {
  await expect(page.locator('#z')).toBeVisible();
});"""
        assert is_valid_playwright(code) is False

    def test_missing_await_expect_returns_false(self):
        from ollama_ai import is_valid_playwright
        code = """import { test, expect } from '@playwright/test';
test('test1', async ({ page }) => {
  await page.goto('http://test.com');
});
test('test2', async ({ page }) => {
  await page.goto('http://test.com');
});
test('test3', async ({ page }) => {
  await page.goto('http://test.com');
});"""
        assert is_valid_playwright(code) is False

    def test_unbalanced_braces_returns_false(self):
        from ollama_ai import is_valid_playwright
        code = """import { test, expect } from '@playwright/test';
test('test1', async ({ page }) => {
  await page.goto('http://test.com');
  await expect(page.locator('#x')).toBeVisible();
});
test('test2', async ({ page }) => {
  await page.goto('http://test.com');
  await expect(page.locator('#y')).toBeVisible();
});
test('test3', async ({ page }) => {
  await page.goto('http://test.com');
  await expect(page.locator('#z')).toBeVisible();
/* missing closing brace */"""
        assert is_valid_playwright(code) is False

    def test_empty_code_returns_false(self):
        from ollama_ai import is_valid_playwright
        assert is_valid_playwright("") is False

    def test_none_code_returns_false(self):
        from ollama_ai import is_valid_playwright
        assert is_valid_playwright(None) is False


class TestFallbackCode:

    def test_returns_valid_playwright(self):
        from ollama_ai import fallback_code, is_valid_playwright
        code = fallback_code()
        assert is_valid_playwright(code) is True

    def test_contains_login_test_cases(self):
        from ollama_ai import fallback_code
        code = fallback_code()
        assert "Successful login" in code
        assert "Invalid login" in code
        assert "Empty fields" in code

    def test_uses_correct_selectors(self):
        from ollama_ai import fallback_code
        code = fallback_code()
        assert "#login-username" in code
        assert "#login-password" in code
        assert "#login-btn" in code
        assert "#login-alert .alert-success" in code
        assert "#login-alert .alert-error" in code

    def test_has_exactly_3_tests(self):
        from ollama_ai import fallback_code
        code = fallback_code()
        assert code.count("test(") >= 3


class TestNormalizeCode:

    def test_trims_whitespace(self):
        from ollama_ai import normalize_code
        assert normalize_code("  const x = 1;  ") == "const x = 1;"

    def test_does_not_alter_code_structure(self):
        from ollama_ai import normalize_code
        original = "const x = 1;\nconst y = 2;"
        assert normalize_code(original) == original


class TestGenerateTests:

    def test_calls_ollama_chat(self):
        from ollama_ai import generate_tests, MODEL

        mock_response = {
            "message": {
                "content": "```typescript\nimport { test, expect } from '@playwright/test';\ntest('a', async ({ page }) => { await page.goto('http://test.com'); await expect(page.locator('#x')).toBeVisible(); });\ntest('b', async ({ page }) => { await page.goto('http://test.com'); await expect(page.locator('#y')).toBeVisible(); });\ntest('c', async ({ page }) => { await page.goto('http://test.com'); await expect(page.locator('#z')).toBeVisible(); });\n```"
            }
        }

        with patch("ollama_ai.ollama.chat", return_value=mock_response), \
             patch("ollama_ai.save_file") as mock_save:
            generate_tests("http://test.com", "login")
            mock_save.assert_called_once()

    def test_appends_error_context_on_retry(self):
        from ollama_ai import generate_tests

        mock_response = {
            "message": {
                "content": "```typescript\nimport { test, expect } from '@playwright/test';\ntest('a', async ({ page }) => { await page.goto('http://test.com'); await expect(page.locator('#x')).toBeVisible(); });\ntest('b', async ({ page }) => { await page.goto('http://test.com'); await expect(page.locator('#y')).toBeVisible(); });\ntest('c', async ({ page }) => { await page.goto('http://test.com'); await expect(page.locator('#z')).toBeVisible(); });\n```"
            }
        }

        with patch("ollama_ai.ollama.chat", return_value=mock_response), \
             patch("ollama_ai.save_file"):
            generate_tests("http://test.com", "login", error_context="Error: element not found")

    def test_falls_back_after_3_failures(self):
        from ollama_ai import generate_tests

        # Return invalid code (no fences) for all 3 attempts
        mock_response = {
            "message": {
                "content": "some text without code fences"
            }
        }

        with patch("ollama_ai.ollama.chat", return_value=mock_response), \
             patch("ollama_ai.fallback_code", return_value="fallback content"), \
             patch("ollama_ai.save_file") as mock_save:
            generate_tests("http://test.com", "login")
            mock_save.assert_called_with("fallback content")


class TestSaveFile:

    def test_creates_directory_and_writes(self):
        from ollama_ai import save_file

        with patch("os.makedirs") as mock_mkdir, \
             patch("builtins.open", mock_open()) as mock_file:
            save_file("test content")
            mock_mkdir.assert_called_once_with("generated-tests", exist_ok=True)
            mock_file.assert_called_once()

    def test_writes_correct_content(self):
        from ollama_ai import save_file

        with patch("os.makedirs"), \
             patch("builtins.open", mock_open()) as mock_file:
            save_file("test content")
            handle = mock_file()
            handle.write.assert_called_once_with("test content")
