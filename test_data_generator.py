"""
Test Data Management — generate synthetic test data via LLM.

Instead of hardcoded "tomsmith / SuperSecretPassword!", generates
varied valid/invalid credential pairs for more robust testing.
"""

import ollama
import json
import os

MODEL = "qwen2.5-coder:7b"

SYNTHETIC_DATA_PROMPT = """Generate a JSON array of 5 test data sets for a login form test.

Requirements:
- Each entry must have: username, password, expected_result ("success" or "failure").
- Include 2 valid credentials that should pass.
- Include 3 invalid credentials (wrong password, empty fields, SQL-like injection).
- Use realistic-sounding usernames and passwords.
- Output ONLY the JSON array, no explanations, no markdown.

Example format:
[
  {"username": "jdoe", "password": "Pass123!", "expected_result": "success"},
  {"username": "jdoe", "password": "wrongpass", "expected_result": "failure"},
  {"username": "", "password": "", "expected_result": "failure"}
]"""


def generate_test_data():
    print("Generating synthetic test data via LLM...\n")

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": SYNTHETIC_DATA_PROMPT}],
        options={"temperature": 0.7},
    )

    raw = response["message"]["content"]
    print(f"Raw output:\n{raw}\n")

    # Extract JSON from response
    if "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("Failed to parse LLM output as JSON. Using fallback data.")
        data = get_fallback_data()

    os.makedirs("generated-tests", exist_ok=True)
    with open("generated-tests/test_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Test data saved: generated-tests/test_data.json ({len(data)} entries)")
    return data


def get_fallback_data():
    return [
        {"username": "tomsmith", "password": "SuperSecretPassword!", "expected_result": "success"},
        {"username": "admin", "password": "admin123", "expected_result": "success"},
        {"username": "tomsmith", "password": "wrongpass", "expected_result": "failure"},
        {"username": "", "password": "", "expected_result": "failure"},
        {"username": "' OR 1=1 --", "password": "anything", "expected_result": "failure"},
    ]


if __name__ == "__main__":
    generate_test_data()
