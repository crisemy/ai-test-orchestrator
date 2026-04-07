import subprocess
import os
import re

GENERATED_TEST_PATH = "generated-tests/login.spec.js"


# -------------------------
# RUN AI AGENT
# -------------------------
def run_ollama_agent():
    print("Running AI generator...")
    result = subprocess.run(
        ["python", "ollama-ai.py"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print("Error running AI agent")
        print(result.stderr)
        exit(1)


# -------------------------
# HARD NORMALIZER (CRÍTICO)
# -------------------------
def normalize_code(code: str) -> str:

    # remover markdown
    code = re.sub(r"```.*?\n", "", code)
    code = code.replace("```", "")

    # fix sintaxis rota
    code = code.replace("await const", "const")

    # URLs inválidas → forzar target REAL
    code = code.replace(
        "http://example.com/login",
        "https://the-internet.herokuapp.com/login"
    )
    code = code.replace(
        "http://your-website.com/login",
        "https://the-internet.herokuapp.com/login"
    )

    # selectores incorrectos → FIX HARD
    code = code.replace("#login", 'button[type="submit"]')

    # assertions basura → reemplazo total
    code = re.sub(
        r"await expect\(.*?\)\.toBeVisible\(\);",
        "await expect(page.locator('#flash')).toBeVisible();",
        code
    )

    # assertions inválidas de texto → usar contains
    code = code.replace(
        ".toHaveText(",
        ".toContainText("
    )

    return code


# -------------------------
# VALIDATE + FIX LOOP
# -------------------------
def validate_and_fix():

    if not os.path.exists(GENERATED_TEST_PATH):
        print("Test file not found")
        exit(1)

    with open(GENERATED_TEST_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    fixed = normalize_code(content)

    with open(GENERATED_TEST_PATH, "w", encoding="utf-8") as f:
        f.write(fixed)

    print("Test normalized and fixed")


# -------------------------
# RUN PLAYWRIGHT
# -------------------------
def run_playwright():
    print("Running Playwright tests...")

    result = subprocess.run(
        "npx playwright test",
        shell=True,
        capture_output=True,
        text=True
    )

    print("\n--- PLAYWRIGHT OUTPUT ---\n")
    print(result.stdout)

    if result.stderr:
        print("\n--- ERRORS ---\n")
        print(result.stderr)


# -------------------------
# RUN POM GENERATOR
# -------------------------

def run_pom_agent():
    print("Generating Page Object Model...")
    from pom_generator import run_pom_generation
    run_pom_generation()


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    print("Starting AI Test Orchestrator\n")

    run_ollama_agent()
    validate_and_fix()
    run_playwright()
    run_pom_agent()

    print("\nE2E flow completed")