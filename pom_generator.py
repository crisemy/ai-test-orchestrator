import os
import re

TEST_PATH = "generated-tests/login.spec.js"
OUTPUT_PATH = "pom/login_page.js"

# -------------------------
# EXTRACT SELECTORS
# -------------------------
def extract_selectors(code):
    selectors = set()

    patterns = [
        r"page\.fill\(['\"](.*?)['\"]",
        r"page\.click\(['\"](.*?)['\"]",
        r"locator\(['\"](.*?)['\"]"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, code)
        selectors.update(matches)

    return list(selectors)


# -------------------------
# GENERATE POM (DETERMINISTIC)
# -------------------------
def generate_pom(selectors):
    lines = []

    lines.append("class LoginPage {")
    lines.append("  constructor(page) {")
    lines.append("    this.page = page;")

    for sel in selectors:
        clean_name = sel.replace("#", "").replace(".", "").replace("[", "").replace("]", "").replace("=", "").replace('"', "").replace("'", "")
        clean_name = clean_name.replace("type", "btn").replace("submit", "submit")

        lines.append(f"    this.{clean_name} = page.locator('{sel}');")

    lines.append("  }\n")

    lines.append("  async login(username, password) {")
    lines.append("    await this.username.fill(username);")
    lines.append("    await this.password.fill(password);")
    lines.append("    await this.login.click();")
    lines.append("  }")

    lines.append("}\n")
    lines.append("module.exports = { LoginPage };")

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