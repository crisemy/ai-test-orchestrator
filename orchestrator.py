import subprocess
import os
import re
import argparse

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
# PARSE CLI ARGUMENTS
# -------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Test Orchestrator CLI")
    parser.add_argument("--url", required=True, help="Target URL to test")
    parser.add_argument("--feature", required=True, help="Description of the feature to test")
    parser.add_argument("--model", required=True, help="Specific Ollama or Cloud model to use")
    parser.add_argument("--engine", choices=["ollama", "cloud"], required=True, help="Choose between Ollama (local) or Cloud engine")
    return parser.parse_args()

# -------------------------
# EXTENDED MAIN FUNCTION
# -------------------------
def main():
    args = parse_arguments()

    # Validate URL
    if not args.url.startswith("http"):
        print("Invalid URL. Please provide a valid URL starting with http or https.")
        exit(1)

    print(f"URL: {args.url}")
    print(f"Feature: {args.feature}")
    print(f"Model: {args.model}")
    print(f"Engine: {args.engine}")

    # Call the appropriate engine
    if args.engine == "ollama":
        print("Using Ollama (local) engine...")
        run_ollama_agent()
    elif args.engine == "cloud":
        print("Using Cloud engine...")
        # Placeholder for cloud engine logic
        print("Cloud engine functionality not implemented yet.")

    # Placeholder for additional logic
    print("Script execution completed.")

if __name__ == "__main__":
    main()