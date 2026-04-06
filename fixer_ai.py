import ollama

MODEL = 'qwen2.5-coder:7b'


def fix_test(code, issues):

    prompt = f"""
Fix the following Playwright test code.

Problems detected:
{issues}

Rules:
- Return ONLY JavaScript
- Keep Playwright syntax
- Fix selectors and assertions
- Do NOT add explanations

Code:
{code}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1}
    )

    return response["message"]["content"]