import os
import re


# -------------------------
# CLEAN SELECTOR → VALID TS IDENTIFIER
# -------------------------
def clean_selector_name(sel):
    name = sel
    # strip text= prefix
    name = re.sub(r'^text=', '', name)
    # remove selector syntax characters
    name = name.replace('#', '').replace('.', '').replace('[', '').replace(']', '').replace('"', '').replace("'", "")
    # split by any non-alphanumeric character
    parts = re.split(r'[^a-zA-Z0-9]+', name)
    parts = [p for p in parts if p]
    if not parts:
        return 'element'
    # camelCase: first part lowercase, rest capitalized
    result = parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])
    # avoid reserved-ish names
    if result == 'type':
        result = 'btn'
    return result


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
def feature_class_name(feature):
    words = feature.replace("-", " ").replace("_", " ").split()
    return "".join(w.capitalize() for w in words) + "Page"

def generate_pom(selectors, feature="login"):
    locators = []
    for sel in selectors:
        locators.append((clean_selector_name(sel), sel))

    class_name = feature_class_name(feature)

    lines = []

    lines.append("import { Page, Locator } from '@playwright/test';")
    lines.append("")
    lines.append(f"export class {class_name} {{")
    lines.append("  readonly page: Page;")

    for name, _ in locators:
        lines.append(f"  readonly {name}: Locator;")

    lines.append("")
    lines.append("  constructor(page: Page) {")
    lines.append("    this.page = page;")

    for name, sel in locators:
        lines.append(f"    this.{name} = page.locator('{sel}');")

    lines.append("  }\n")

    # detect field locators for the login method
    username_sel = next((n for n, s in locators if 'username' in s.lower()), None)
    password_sel = next((n for n, s in locators if 'password' in s.lower()), None)
    login_btn = next((n for n, s in locators if 'btn' in n.lower()), None)
    if not login_btn:
        login_btn = next((n for n, s in locators if 'login' in n.lower() and 'username' not in n.lower() and 'password' not in n.lower() and 'alert' not in n.lower() and 'result' not in n.lower()), None)

    lines.append("  async login(username: string, password: string) {")
    if username_sel:
        lines.append(f"    await this.{username_sel}.fill(username);")
    if password_sel:
        lines.append(f"    await this.{password_sel}.fill(password);")
    if login_btn:
        lines.append(f"    await this.{login_btn}.click();")
    lines.append("  }")
    lines.append("}")

    return "\n".join(lines)


# -------------------------
# MAIN
# -------------------------
def run_pom_generation(feature="login"):
    print("Generating POM (deterministic)...")

    test_path = f"generated-tests/{feature}.spec.ts"
    output_path = f"pom/{feature}_page.ts"

    if not os.path.exists(test_path):
        print(f"Test file not found: {test_path}")
        return

    with open(test_path, "r", encoding="utf-8") as f:
        code = f.read()

    selectors = extract_selectors(code)

    if not selectors:
        print("No selectors found")
        return

    pom_code = generate_pom(selectors, feature)

    os.makedirs("pom", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pom_code)

    print(f"POM generated at: {output_path}")

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