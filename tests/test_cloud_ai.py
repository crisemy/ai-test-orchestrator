from unittest.mock import patch, mock_open


class TestExtractCode:
    def test_extracts_typescript_fence(self):
        from cloud_ai import extract_code
        code = "```typescript\nconst x = 1;\n```"
        assert extract_code(code) == "const x = 1;"

    def test_returns_none_if_no_fence(self):
        from cloud_ai import extract_code
        assert extract_code("const x = 1;") is None


class TestIsValidPlaywright:
    def test_valid_code_returns_true(self):
        from cloud_ai import is_valid_playwright
        code = """import { test, expect } from '@playwright/test';
test('a', async ({ page }) => { await page.goto('http://t.com'); await expect(page.locator('#x')).toBeVisible(); });
test('b', async ({ page }) => { await page.goto('http://t.com'); await expect(page.locator('#y')).toBeVisible(); });
test('c', async ({ page }) => { await page.goto('http://t.com'); await expect(page.locator('#z')).toBeVisible(); });"""
        assert is_valid_playwright(code) is True

    def test_empty_code_returns_false(self):
        from cloud_ai import is_valid_playwright
        assert is_valid_playwright("") is False

    def test_none_code_returns_false(self):
        from cloud_ai import is_valid_playwright
        assert is_valid_playwright(None) is False


class TestFallbackCode:
    def test_returns_valid_playwright(self):
        from cloud_ai import fallback_code, is_valid_playwright
        code = fallback_code()
        assert is_valid_playwright(code) is True

    def test_contains_login_tests(self):
        from cloud_ai import fallback_code
        code = fallback_code()
        assert "Successful login" in code
        assert "Invalid login" in code
        assert "Empty fields" in code


class TestGenerateTests:
    def test_fallback_no_api_key(self):
        from cloud_ai import generate_tests
        with patch("cloud_ai.save_file") as mock_save, \
             patch("cloud_ai.fallback_code", return_value="fallback"):
            generate_tests("http://test.com", "mock-model", "login")
            mock_save.assert_called_once()

    def test_saves_valid_code(self):
        from cloud_ai import generate_tests
        mock_response = type("Response", (), {
            "content": [type("Content", (), {"text": "```typescript\nimport { test, expect } from '@playwright/test';\ntest('a', async ({ page }) => { await page.goto('http://t.com'); await expect(page.locator('#x')).toBeVisible(); });\ntest('b', async ({ page }) => { await page.goto('http://t.com'); await expect(page.locator('#y')).toBeVisible(); });\ntest('c', async ({ page }) => { await page.goto('http://t.com'); await expect(page.locator('#z')).toBeVisible(); });\n```"})]
        })

        mock_client = type("Client", (), {"messages": type("Messages", (), {"create": lambda **kw: mock_response})()})()
        mock_anthropic_module = type("Module", (), {"Anthropic": lambda *a, **kw: mock_client})()

        with patch("cloud_ai.save_file") as mock_save, \
             patch("cloud_ai.os.getenv", return_value="fake-key"), \
             patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
            generate_tests("http://test.com", "mock-model", "login")
            mock_save.assert_called_once()


class TestSaveFile:
    def test_creates_directory_and_writes(self):
        from cloud_ai import save_file
        with patch("os.makedirs") as mock_mkdir, \
             patch("builtins.open", mock_open()) as mock_file:
            save_file("test content")
            mock_mkdir.assert_called_once_with("generated-tests", exist_ok=True)
            mock_file.assert_called_once()

    def test_writes_correct_content(self):
        from cloud_ai import save_file
        with patch("os.makedirs"), \
             patch("builtins.open", mock_open()) as mock_file:
            save_file("test content")
            handle = mock_file()
            handle.write.assert_called_once_with("test content")
