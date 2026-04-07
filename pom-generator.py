import ollama
import os
import re

PAGES_DIR = "pages"
TEST_FILE = "generated-tests/login.spec.js"


def clean_code(code: str) -> str:
    code = re.sub(r"```.*?\n", "", code)
    code = code.replace("```", "")
    return code.strip()


def generate_pom(test_code: str) -> str:

    prompt = f"""
You are a QA automation architect.

Convert this Playwright test into a Page Object Model.

STRICT RULES:
- Create a class called LoginPage
- Use Playwright (JavaScript)
- Include:
    - constructor(page)
    - async goto()
    - async login(username, password)
    - getFlashMessage()
- Use correct selectors for https://the-internet.herokuapp.com/login
- DO NOT include markdown
- ONLY return valid JavaScript code

TEST:
{test_code}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return clean_code(response["message"]["content"])


def save_pom(code: str):
    os.makedirs(PAGES_DIR, exist_ok=True)
    path = os.path.join(PAGES_DIR, "LoginPage.js")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"POM saved in: {path}")


def run_pom_generation():

    if not os.path.exists(TEST_FILE):
        print("Test file not found")
        return

    with open(TEST_FILE, "r", encoding="utf-8") as f:
        test_code = f.read()

    pom_code = generate_pom(test_code)
    save_pom(pom_code)