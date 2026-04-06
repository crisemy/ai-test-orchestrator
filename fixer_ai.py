import ollama
import re

MODEL = "qwen2.5-coder:7b"


# -------------------------
# EXTRACT PURE JS (REMOVE MARKDOWN)
# -------------------------
def extract_js(text):
    match = re.search(r"```javascript(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


# -------------------------
# FIX TEST USING LLM + HARD RULES
# -------------------------
def fix_test(original_code, issues):

    prompt = f"""
Fix the following Playwright test code.

STRICT:
- Output ONLY valid JavaScript
- NO markdown
- NO triple backticks
- Keep Playwright syntax valid

Issues:
{issues}

Code:
{original_code}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1}
    )

    raw_output = response["message"]["content"]

    fixed = extract_js(raw_output)

    # -------------------------
    # HARD GUARDS (CRITICAL)
    # -------------------------
    
    # Fix URL
    fixed = fixed.replace(
        "http://example.com/login",
        "https://the-internet.herokuapp.com/login"
    )

    # Replace ALL assertions with correct selectors

    fixed = re.sub(
        r"await expect\(page\.locator\([^)]+\)\)\.toBeVisible\(\);",
        "await expect(page.locator('#flash')).toBeVisible();",
        fixed
    )

    # Fix credentials for valid login
    fixed = fixed.replace(
        "await page.fill('#username', 'user');",
        "await page.fill('#username', 'tomsmith');"
    )

    fixed = fixed.replace(
        "await page.fill('#password', 'pass');",
        "await page.fill('#password', 'SuperSecretPassword!');"
    )

    # Fix invalid login scenario
    fixed = fixed.replace(
        "await page.fill('#username', 'invalid');",
        "await page.fill('#username', 'wronguser');"
    )

    fixed = fixed.replace(
        "await page.fill('#password', 'wrong');",
        "await page.fill('#password', 'wrongpass');"
    )