import subprocess
import os

GENERATED_TEST_PATH = "generated-tests/login.spec.js"

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


def validate_test_file():
    print("Validating generated test...")
    if not os.path.exists(GENERATED_TEST_PATH):
        print("Test file not found")
        exit(1)

    with open(GENERATED_TEST_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "test(" not in content:
        print("Invalid test content")
        exit(1)

    print("Test file looks valid")


def run_playwright():
    print("Running Playwright tests...")
    result = subprocess.run(
        ["npx", "playwright", "test"],
        text=True
    )

    if result.returncode != 0:
        print("Tests failed")
        exit(1)

    print("Tests passed")


if __name__ == "__main__":
    print("Starting AI Test Orchestrator\n")

    run_ollama_agent()
    validate_test_file()
    run_playwright()

    print("\nE2E flow completed")