import subprocess
import os

from fixer_ai import fix_test  # ✅ IMPORT CORRECTO

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
# SEMANTIC VALIDATION
# -------------------------
def validate_semantics(code):
    issues = []

    if "example.com" in code:
        issues.append("Invalid URL: example.com")

    if "text=Dashboard" in code:
        issues.append("Invalid assertion: Dashboard not present")

    if "text=Required" in code:
        issues.append("Invalid assertion: Required not present")

    if "text=Invalid" in code:
        issues.append("Weak assertion: use real error message")

    return issues


# -------------------------
# VALIDATE TEST FILE + AUTO FIX
# -------------------------
def validate_test_file(max_attempts=3):

    for attempt in range(max_attempts):

        print(f"\nValidating generated test... (attempt {attempt + 1})")

        if not os.path.exists(GENERATED_TEST_PATH):
            print("Test file not found")
            exit(1)

        with open(GENERATED_TEST_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        issues = validate_semantics(content)

        if not issues:
            print("Test file looks valid")
            return

        print("\nValidation issues found:")
        for issue in issues:
            print(f"- {issue}")

        print("\nAttempting auto-fix...")

        fixed_code = fix_test(content, "\n".join(issues))

        with open(GENERATED_TEST_PATH, "w", encoding="utf-8") as f:
            f.write(fixed_code)

    print("\nMax fix attempts reached. Continuing with last version...")


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
# MAIN FLOW
# -------------------------
if __name__ == "__main__":
    print("Starting AI Test Orchestrator\n")

    run_ollama_agent()
    validate_test_file()
    run_playwright()

    print("\nE2E flow completed")