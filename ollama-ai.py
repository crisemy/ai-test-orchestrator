import ollama
import re
import os
import string
import json

# Load template from external JSON file
with open('prompt_template.json', 'r') as file:
    PROMPT_TEMPLATE = json.load(file)['template']

# Adding different models. 
# Alternatively, you can use "glm-5.1:cloud", "qwen3.5:cloud", etc for a more code-focused models.
MODEL = 'qwen2.5-coder:7b'

OUTPUT_FILE = "generated-tests/login.spec.ts"

# -------------------------
# Dynamic Prompt Template
# -------------------------
PROMPT_TEMPLATE = string.Template(
    """
    Generate VALID Playwright test code in TypeScript.

    STRICT:
    - Output ONLY TypeScript
    - NO explanations
    - NO comments
    - Use EXACTLY this structure

    import { test, expect } from '@playwright/test';

    test('Successful login', async ({ page }) => {
      await page.goto('$url');
      await page.fill('#username', 'user');
      await page.fill('#password', 'pass');
      await page.click('#login');

      await expect(page.locator('text=Dashboard')).toBeVisible();
    });

    test('Invalid login', async ({ page }) => {
      await page.goto('$url');
      await page.fill('#username', 'invalid');
      await page.fill('#password', 'wrong');
      await page.click('#login');

      await expect(page.locator('text=Invalid')).toBeVisible();
    });

    test('Empty fields', async ({ page }) => {
      await page.goto('$url');
      await page.click('#login');

      await expect(page.locator('text=Required')).toBeVisible();
    });

    Do not change structure.
    """
)

# -------------------------
# Extract code block from LLM output
# -------------------------
def extract_code(text):
    for fence in ["```typescript", "```javascript", "```ts", "```js", "```"]:
        if fence in text:
            return text.split(fence)[1].split("```")[0].strip()
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
        "import { test, expect }" in code and
        code.count("test(") >= 3 and
        "await page.goto" in code and
        "await expect" in code and
        code.count("{") == code.count("}")  # basic syntax sanity check
    )

# -------------------------
# Fallback code (safe baseline)
# -------------------------
def fallback_code():
    return """import { test, expect } from '@playwright/test';

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
# Generate tests using LLM (TypeScript output)
# -------------------------
def generate_tests(url):

    print("Generating Playwright tests (TypeScript)...\n")

    for attempt in range(3):

        print(f"\nAttempt {attempt + 1}")

        dynamic_prompt = PROMPT_TEMPLATE.substitute(url=url)

        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": dynamic_prompt}],
            options={
                "temperature": 0.2
            }
        )

        raw_output = response["message"]["content"]

        print("\nRAW OUTPUT:\n")
        print(raw_output)

        code = extract_code(raw_output)

        if not code:
            print("No code block detected, retrying...")
            continue

        normalized = normalize_code(code)

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
    import sys
    if len(sys.argv) != 3:
        print("Usage: python ollama-ai.py <url> <model>")
        exit(1)

    url = sys.argv[1]
    MODEL = sys.argv[2]

    generate_tests(url)