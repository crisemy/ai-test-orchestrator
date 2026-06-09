import os
import re

TEST_PATH = "generated-tests/login.spec.ts"
OUTPUT_PATH = "pom/login_page.ts"

# -------------------------
# EXTRACT SELECTORS
# -------------------------
def extract_selectors(code):
    selectors = set()

    patterns = [
        r"page\.fill\(['\"](.*?)['\"]",
        r"page\.click\(['\"](.*?)['\"]",
        r"locator\(['\"](.*?)['\"]",
        r"page\.locator\(['\"](.*?)['\"]",
        r"page\.locator\((.*?)\)\.click\(\)",
        r"page\.locator\((.*?)\)\.fill\((.*?)\)"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, code)
        selectors.update(matches if isinstance(matches, list) else [matches])

    return list(selectors)


# -------------------------
# GENERATE POM (DETERMINISTIC)
# -------------------------
def generate_pom(selectors):
    lines = []

    lines.append("import { Page, Locator } from '@playwright/test';")
    lines.append("")
    lines.append("export class LoginPage {")
    lines.append("  readonly page: Page;")

    for sel in selectors:
        clean_name = sel.replace("#", "").replace(".", "").replace("[", "").replace("]", "").replace("=", "").replace('"', "").replace("'", "")
        clean_name = clean_name.replace("type", "btn").replace("submit", "submit")
        lines.append(f"  readonly {clean_name}: Locator;")

    lines.append("")
    lines.append("  constructor(page: Page) {")
    lines.append("    this.page = page;")

    for sel in selectors:
        clean_name = sel.replace("#", "").replace(".", "").replace("[", "").replace("]", "").replace("=", "").replace('"', "").replace("'", "")
        clean_name = clean_name.replace("type", "btn").replace("submit", "submit")
        lines.append(f"    this.{clean_name} = page.locator('{sel}');")

    lines.append("  }\n")

    lines.append("  async login(username: string, password: string) {")
    lines.append("    await this.username.fill(username);")
    lines.append("    await this.password.fill(password);")
    lines.append("    await this.login.click();")
    lines.append("  }")
    lines.append("}")

    return "\n".join(lines)


# -------------------------
# MAIN
# -------------------------
def run_pom_generation():
    print("Generating POM (deterministic)...")

    if not os.path.exists(TEST_PATH):
        print("Test file not found")
        return

    with open(TEST_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    selectors = extract_selectors(code)

    if not selectors:
        print("No selectors found")
        return

    pom_code = generate_pom(selectors)

    os.makedirs("pom", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(pom_code)

    print(f"POM generated at: {OUTPUT_PATH}")

def inject_pom_into_test(test_path, pom_path):
    """
    Replace direct page.fill and page.click calls with POM methods in the test file.
    """
    with open(test_path, 'r') as test_file:
        test_code = test_file.read()

    # Replace direct calls with POM methods
    test_code = re.sub(r"page\.fill\(['\"](.*?)['\"], ['\"](.*?)['\"]\)", r"loginPage.\1.fill(\2)", test_code)
    test_code = re.sub(r"page\.click\(['\"](.*?)['\"]\)", r"loginPage.\1.click()", test_code)

    with open(test_path, 'w') as test_file:
        test_file.write(test_code)