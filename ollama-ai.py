import ollama
import re
import os

MODEL = 'qwen2.5-coder:7b'

OUTPUT_FILE = "generated-tests/login.spec.js"


PROMPT = """
Generate VALID Playwright test code.

STRICT:
- Output ONLY JavaScript
- NO explanations
- NO comments
- Use EXACTLY this structure

const { test, expect } = require('@playwright/test');

test('Successful login', async ({ page }) => {
  await page.goto('http://example.com/login');
  await page.fill('#username', 'user');
  await page.fill('#password', 'pass');
  await page.click('#login');

  await expect(page.locator('text=Dashboard')).toBeVisible();
});

test('Invalid login', async ({ page }) => {
  await page.goto('http://example.com/login');
  await page.fill('#username', 'invalid');
  await page.fill('#password', 'wrong');
  await page.click('#login');

  await expect(page.locator('text=Invalid')).toBeVisible();
});

test('Empty fields', async ({ page }) => {
  await page.goto('http://example.com/login');
  await page.click('#login');

  await expect(page.locator('text=Required')).toBeVisible();
});

Do not change structure.
"""


# -------------------------
# Extract only JavaScript code block
# -------------------------
def extract_js(text):
    if "```javascript" in text:
        return text.split("```javascript")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return None


# -------------------------
# Normalize code (non-destructive)
# -------------------------
def normalize_code(code):
    # Only trim whitespace, do not alter structure
    return code.strip()


# -------------------------
# Validate Playwright code
# -------------------------
def is_valid_playwright(code):
    if not code:
        return False

    return (
        "const { test, expect }" in code and
        code.count("test(") >= 3 and
        "await page.goto" in code and
        "await expect" in code and
        code.count("{") == code.count("}")  # basic syntax sanity check
    )


# -------------------------
# Fallback code (safe baseline)
# -------------------------
def fallback_code():
    return """const { test, expect } = require('@playwright/test');

test('Successful login', async ({ page }) => {
  await page.goto('http://example.com/login');
  await page.fill('#username', 'user');
  await page.fill('#password', 'pass');
  await page.click('#login');
  await expect(page.locator('text=Dashboard')).toBeVisible();
});

test('Invalid login', async ({ page }) => {
  await page.goto('http://example.com/login');
  await page.fill('#username', 'invalid');
  await page.fill('#password', 'wrong');
  await page.click('#login');
  await expect(page.locator('text=Invalid')).toBeVisible();
});

test('Empty fields', async ({ page }) => {
  await page.goto('http://example.com/login');
  await page.click('#login');
  await expect(page.locator('text=Required')).toBeVisible();
});"""


# -------------------------
# Generate tests using LLM
# -------------------------
def generate_tests():

    print("Generating Playwright tests...\n")

    for attempt in range(3):

        print(f"\nAttempt {attempt + 1}")

        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
            options={
                "temperature": 0.2
            }
        )

        raw_output = response["message"]["content"]

        print("\nRAW OUTPUT:\n")
        print(raw_output)

        js_code = extract_js(raw_output)

        if not js_code:
            print("No JavaScript block detected, retrying...")
            continue

        normalized = normalize_code(js_code)

        print("\nNORMALIZED CODE:\n")
        print(normalized)

        if is_valid_playwright(normalized):
            save_file(normalized)
            return

        print("Invalid code based on validation, retrying...")

    print("\nUsing fallback code...\n")
    save_file(fallback_code())


# -------------------------
# Save file
# -------------------------
def save_file(code):

    os.makedirs("generated-tests", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\nTest saved in: {OUTPUT_FILE}")


# -------------------------
# Entry point
# -------------------------
if __name__ == "__main__":
    generate_tests()