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
# EXTRAER SOLO JS
# -------------------------
def extract_js(text):
    match = re.search(r"```javascript(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


# -------------------------
# NORMALIZAR CÓDIGO
# -------------------------
def normalize_code(code):
    lines = code.split("\n")

    clean_lines = []
    seen = set()

    for line in lines:
        l = line.strip()

        # eliminar líneas vacías repetidas
        if l == "":
            continue

        # eliminar duplicados exactos
        if l in seen:
            continue

        seen.add(l)
        clean_lines.append(line)

    return "\n".join(clean_lines)


# -------------------------
# VALIDAR CÓDIGO
# -------------------------
def is_valid_playwright(code):
    if not code:
        return False

    # checks mínimos reales
    return (
        "const { test, expect }" in code and
        code.count("test(") >= 3 and
        "await page.goto" in code and
        "await expect" in code
    )


# -------------------------
# FALLBACK
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
# GENERAR TESTS
# -------------------------
def generate_tests():

    print("🚀 Generating Playwright tests...\n")

    for attempt in range(3):

        print(f"\n🔁 Attempt {attempt + 1}")

        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
            options={
                "temperature": 0.2
            }
        )

        raw_output = response["message"]["content"]

        print("\n🧪 RAW OUTPUT:\n")
        print(raw_output)

        js_code = extract_js(raw_output)

        if not js_code:
            print("⚠️ No se detectó bloque JS, reintentando...")
            continue

        normalized = normalize_code(js_code)

        print("\n🧼 NORMALIZED CODE:\n")
        print(normalized)

        if is_valid_playwright(normalized):
            save_file(normalized)
            return

        print("⚠️ Código inválido según validación, reintentando...")

    print("\n❌ Using fallback code...\n")
    save_file(fallback_code())


# -------------------------
# GUARDAR ARCHIVO
# -------------------------
def save_file(code):

    os.makedirs("generated-tests", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n💾 Test saved in: {OUTPUT_FILE}")


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    generate_tests()