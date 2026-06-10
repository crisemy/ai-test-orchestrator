import pytest
from unittest.mock import patch, mock_open


class TestCleanSelectorName:

    def test_id_selector(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name("#login-btn") == "loginBtn"

    def test_class_selector(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name(".alert-error") == "alertError"

    def test_text_selector(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name("text=Form Authentication") == "formAuthentication"

    def test_attribute_selector(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name('[data-test="submit"]') == "dataTestSubmit"

    def test_id_with_hyphens(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name("#login-username") == "loginUsername"

    def test_id_with_underscores(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name("#submit_btn") == "submitBtn"

    def test_mixed_selector(self):
        from pom_generator import clean_selector_name
        result = clean_selector_name("#login-btn.btn-primary")
        assert "login" in result.lower()
        # #login-btn.btn-primary → strip #. → login-btnbtn-primary → loginBtnbtnPrimary
        assert result == "loginBtnbtnPrimary"

    def test_reserved_name_type_becomes_btn(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name("#type") == "btn"

    def test_empty_parts_returns_element(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name("#") != ""
        # Should not crash and return something reasonable

    def test_camel_case_first_word_lower(self):
        from pom_generator import clean_selector_name
        result = clean_selector_name("#MyButton")
        assert result[0].islower() or result == "element"

    def test_selector_with_quotes(self):
        from pom_generator import clean_selector_name
        result = clean_selector_name("button[data-id='123']")
        assert "123" in result

    def test_simple_text_selector_becomes_camel(self):
        from pom_generator import clean_selector_name
        assert clean_selector_name("text=Login") == "login"

    def test_handles_special_chars_gracefully(self):
        from pom_generator import clean_selector_name
        result = clean_selector_name("[type=submit]")
        assert isinstance(result, str)
        assert len(result) > 0


class TestFeatureClassName:

    def test_login(self):
        from pom_generator import feature_class_name
        assert feature_class_name("login") == "LoginPage"

    def test_user_login(self):
        from pom_generator import feature_class_name
        assert feature_class_name("user-login") == "UserLoginPage"

    def test_user_login_form(self):
        from pom_generator import feature_class_name
        assert feature_class_name("user-login-form") == "UserLoginFormPage"

    def test_with_underscores(self):
        from pom_generator import feature_class_name
        assert feature_class_name("user_login") == "UserLoginPage"

    def test_single_word(self):
        from pom_generator import feature_class_name
        assert feature_class_name("signup") == "SignupPage"


class TestExtractSelectors:

    def test_extracts_fill_selectors(self):
        from pom_generator import extract_selectors
        code = "await page.fill('#login-username', 'tomsmith');"
        selectors = extract_selectors(code)
        assert "#login-username" in selectors

    def test_extracts_click_selectors(self):
        from pom_generator import extract_selectors
        code = "await page.click('#login-btn');"
        selectors = extract_selectors(code)
        assert "#login-btn" in selectors

    def test_extracts_locator_selectors(self):
        from pom_generator import extract_selectors
        code = "const el = page.locator('.alert-error');"
        selectors = extract_selectors(code)
        assert ".alert-error" in selectors

    def test_deduplicates_selectors(self):
        from pom_generator import extract_selectors
        code = """page.fill('#login-username', 'a');
page.fill('#login-username', 'b');"""
        selectors = extract_selectors(code)
        assert selectors.count("#login-username") == 1

    def test_extracts_multiple_unique_selectors(self):
        from pom_generator import extract_selectors
        code = """page.fill('#login-username', 'a');
page.fill('#login-password', 'b');
page.click('#login-btn');
page.locator('.alert-success');"""
        selectors = extract_selectors(code)
        assert len(selectors) == 4

    def test_returns_empty_for_no_selectors(self):
        from pom_generator import extract_selectors
        code = "const x = 1;"
        assert extract_selectors(code) == []

    def test_extracts_text_selectors_from_click(self):
        from pom_generator import extract_selectors
        code = "await page.click('text=Form Authentication');"
        selectors = extract_selectors(code)
        assert "text=Form Authentication" in selectors


class TestGeneratePom:

    def test_generates_valid_class_structure(self):
        from pom_generator import generate_pom
        selectors = ["#login-username", "#login-password", "#login-btn"]
        pom = generate_pom(selectors, "login")
        assert "export class LoginPage" in pom
        assert "import { Page, Locator }" in pom
        assert "readonly page: Page;" in pom

    def test_creates_locator_fields(self):
        from pom_generator import generate_pom
        selectors = ["#login-username", "#login-btn"]
        pom = generate_pom(selectors, "login")
        assert "readonly loginUsername: Locator;" in pom
        assert "readonly loginBtn: Locator;" in pom

    def test_constructor_assigns_locators(self):
        from pom_generator import generate_pom
        selectors = ["#login-username"]
        pom = generate_pom(selectors, "login")
        assert "this.loginUsername = page.locator('#login-username');" in pom

    def test_login_method_with_all_fields(self):
        from pom_generator import generate_pom
        selectors = ["#login-username", "#login-password", "#login-btn"]
        pom = generate_pom(selectors, "login")
        assert "async login(username: string, password: string)" in pom
        assert "await this.loginUsername.fill(username);" in pom
        assert "await this.loginPassword.fill(password);" in pom
        assert "await this.loginBtn.click();" in pom

    def test_login_method_without_username(self):
        from pom_generator import generate_pom
        selectors = ["#login-btn"]
        pom = generate_pom(selectors, "login")
        assert "async login(username: string, password: string)" in pom
        assert "fill(username)" not in pom

    def test_login_method_without_password(self):
        from pom_generator import generate_pom
        selectors = ["#username", "#btn"]
        pom = generate_pom(selectors, "login")
        assert "fill(username)" in pom
        assert "fill(password)" not in pom

    def test_detects_btn_by_name_pattern(self):
        from pom_generator import generate_pom
        selectors = ["#username", "#password", "#submit-btn"]
        pom = generate_pom(selectors, "login")
        assert "await this.submitBtn.click();" in pom

    def test_falls_back_to_login_selector_for_btn(self):
        from pom_generator import generate_pom
        selectors = ["#username", "#password", "#login-button"]
        pom = generate_pom(selectors, "login")
        assert "await this.loginButton.click();" in pom
