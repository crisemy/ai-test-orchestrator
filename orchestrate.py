import subprocess
import os

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
def validate_semantics(file_path):
    issues = []

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

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
# VALIDATE TEST FILE
# -------------------------
def validate_test_file():
    print("Validating generated test...")

    if not os.path.exists(GENERATED_TEST_PATH):
        print("Test file not found")
        exit(1)

    with open(GENERATED_TEST_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Structural validation
    if "test(" not in content:
        print("Invalid test content")
        exit(1)

    # Semantic validation
    issues = validate_semantics(GENERATED_TEST_PATH)

    if issues:
        print("\nValidation issues found:")
        for issue in issues:
            print(f"- {issue}")

        print("\nAttempting auto-fix...\n")

        from fixer_ai import fix_test

        fixed_code = fix_test(content, issues)

        with open(GENERATED_TEST_PATH, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        print("Test auto-fixed. Re-validating...\n")

        return validate_test_file()  # 🔁 loop simple

        print("Test file looks valid")


# -------------------------
# RUN PLAYWRIGHT
# -------------------------
def run_playwright():
    print("Running Playwright tests...")

    result = subprocess.run(
        "npx playwright test",
        shell=True,  # Required for Windows
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