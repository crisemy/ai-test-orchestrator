import os
import re
import string
import json
from dotenv import load_dotenv

load_dotenv()

OUTPUT_FILE = "generated-tests/login.spec.ts"

PROMPT_TEMPLATE = string.Template("""
    Generate VALID Playwright test code in TypeScript for the UI Testing Lab app.

    The app runs at $url and has a login form at section-login.

    STRICT:
    - Output ONLY TypeScript
    - NO explanations
    - NO comments
    - Use EXACTLY this structure

    import { test, expect } from '@playwright/test';

    test('Successful login', async ({ page }) => {
      await page.goto('$url');
      await page.click('text=Form Authentication');
      await page.fill('#login-username', 'tomsmith');
      await page.fill('#login-password', 'SuperSecretPassword!');
      await page.click('#login-btn');
      await expect(page.locator('#login-alert .alert-success')).toBeVisible();
    });

    test('Invalid login', async ({ page }) => {
      await page.goto('$url');
      await page.click('text=Form Authentication');
      await page.fill('#login-username', 'invalid');
      await page.fill('#login-password', 'wrong');
      await page.click('#login-btn');
      await expect(page.locator('#login-alert .alert-error')).toBeVisible();
    });

    test('Empty fields', async ({ page }) => {
      await page.goto('$url');
      await page.click('text=Form Authentication');
      await page.click('#login-btn');
      await expect(page.locator('#login-result')).toContainText('missing credentials');
    });

    Do not change structure.
""")


def extract_code(text):
    for fence in ["```typescript", "```javascript", "```ts", "```js", "```"]:
        if fence in text:
            return text.split(fence)[1].split("```")[0].strip()
    return None


def is_valid_playwright(code):
    if not code:
        return False
    return (
        "import { test, expect }" in code
        and code.count("test(") >= 3
        and "await page.goto" in code
        and "await expect" in code
        and code.count("{") == code.count("}")
    )


def fallback_code():
    return """import { test, expect } from '@playwright/test';

test('Successful login', async ({ page }) => {
  await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.fill('#login-username', 'tomsmith');
  await page.fill('#login-password', 'SuperSecretPassword!');
  await page.click('#login-btn');
  await expect(page.locator('#login-alert .alert-success')).toBeVisible();
});

test('Invalid login', async ({ page }) => {
  await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.fill('#login-username', 'invalid');
  await page.fill('#login-password', 'wrong');
  await page.click('#login-btn');
  await expect(page.locator('#login-alert .alert-error')).toBeVisible();
});

test('Empty fields', async ({ page }) => {
  await page.goto('http://localhost:3000/playwright-ui-testing-lab.html');
  await page.click('text=Form Authentication');
  await page.click('#login-btn');
  await expect(page.locator('#login-result')).toContainText('missing credentials');
});"""


def generate_tests(url, model="claude-3-haiku-20240307", feature="login", error_context=None):
    print("Generating Playwright tests via Anthropic Claude...\n")

    global OUTPUT_FILE
    OUTPUT_FILE = f"generated-tests/{feature}.spec.ts"

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in .env file")
        print("Falling back to hardcoded test template...")
        save_file(fallback_code())
        return

    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        print("Falling back to hardcoded test template...")
        save_file(fallback_code())
        return

    client = anthropic.Anthropic(api_key=api_key)
    prompt = PROMPT_TEMPLATE.substitute(url=url)

    if error_context:
        prompt += f"""

The previous version of this test failed with the following error:
{error_context}

Please fix the test to avoid this error."""
        print(f"\nFeedback loop — injecting error context:\n{error_context}\n")

    for attempt in range(3):
        print(f"\nAttempt {attempt + 1}")
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_output = response.content[0].text

            print("\nRAW OUTPUT:\n")
            print(raw_output)

            code = extract_code(raw_output)
            if not code:
                code = raw_output.strip()

            print("\nNORMALIZED CODE:\n")
            print(code)

            if is_valid_playwright(code):
                save_file(code)
                return

            print("Invalid code based on validation, retrying...")
        except Exception as e:
            print(f"API error: {e}")
            if attempt < 2:
                print("Retrying...")

    print("\nUsing fallback code...\n")
    save_file(fallback_code())


def save_file(code):
    os.makedirs("generated-tests", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"\nTest saved in: {OUTPUT_FILE}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python cloud_ai.py <url> <model> [feature] [error_context]")
        exit(1)
    url = sys.argv[1]
    model = sys.argv[2]
    feature = sys.argv[3] if len(sys.argv) > 3 else "login"
    error_context = sys.argv[4] if len(sys.argv) > 4 else None
    generate_tests(url, model, feature, error_context)
