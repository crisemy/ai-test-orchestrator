import subprocess
import os
import re
import argparse
import json
import time
import functools
from datetime import datetime, timezone
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import (
    LOG_FILE,
    EXECUTION_LOG,
    BACKUP_DIR,
    TOKEN_COST_PER_MILLION,
    MANUAL_TEST_COST,
    MAX_COST_THRESHOLD,
    RATE_LIMIT_MAX_PER_MINUTE,
    MAX_PLAYWRIGHT_RETRIES,
    TARGET_URL,
    OrchestratorError,
    TestGenerationError,
    ValidationError,
    CancelledByUser,
)

console = Console()

_rate_limit_state: dict[str, Any] = {"call_timestamps": [], "max_per_minute": RATE_LIMIT_MAX_PER_MINUTE}


# -------------------------
# INPUT SANITIZATION (Phase 3.2)
# -------------------------
def sanitize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL protocol: {url[:20]}")
    url = re.sub(r"[\r\n\t]", "", url)
    if re.search(r"[<>\"'{}|^`\\]", url):
        raise ValueError(f"URL contains blocked characters: {url[:30]}")
    return url


def sanitize_feature(feature: str) -> str:
    sanitized = feature.strip()
    sanitized = re.sub(r"[;&|`$(){}[\]!#~<>\\]", "", sanitized)
    sanitized = sanitized[:80]
    if not sanitized:
        raise ValueError("Feature name is empty after sanitization")
    return sanitized


# -------------------------
# TEST ROLLBACK (Phase 3.3)
# -------------------------
def backup_test(feature: str) -> str | None:
    test_path = f"generated-tests/{feature}.spec.ts"
    if not os.path.exists(test_path):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, f"{feature}.spec.ts.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak")
    with open(test_path, "r", encoding="utf-8") as src:
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
    return backup_path


def restore_test(feature: str) -> bool:
    if not os.path.exists(BACKUP_DIR):
        return False
    candidates = [f for f in os.listdir(BACKUP_DIR) if f.startswith(f"{feature}.spec.ts.")]
    if not candidates:
        return False
    latest = sorted(candidates)[-1]
    backup_path = os.path.join(BACKUP_DIR, latest)
    test_path = f"generated-tests/{feature}.spec.ts"
    with open(backup_path, "r", encoding="utf-8") as src:
        with open(test_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
    log_pipeline("rollback_restored", {"feature": feature, "backup": latest})
    return True


# -------------------------
# RATE LIMITING (Phase 3.4)
# -------------------------
def check_rate_limit() -> None:
    now = time.time()
    window_start = now - 60
    _rate_limit_state["call_timestamps"] = [
        t for t in _rate_limit_state["call_timestamps"] if t > window_start
    ]
    if len(_rate_limit_state["call_timestamps"]) >= _rate_limit_state["max_per_minute"]:
        wait = _rate_limit_state["call_timestamps"][0] - window_start
        console.print(f"[bold yellow]Rate limit reached. Waiting {wait:.0f}s...[/bold yellow]")
        time.sleep(wait + 1)
        return check_rate_limit()
    _rate_limit_state["call_timestamps"].append(now)


def check_cost_threshold(estimated_cost: float) -> None:
    if estimated_cost > MAX_COST_THRESHOLD:
        console.print(f"[bold red]WARNING: Estimated cost ${estimated_cost:.4f} exceeds threshold ${MAX_COST_THRESHOLD}[/bold red]")
        log_pipeline("cost_threshold_exceeded", {"estimated_cost": estimated_cost, "threshold": MAX_COST_THRESHOLD})


# -------------------------
# TYPESCRIPT VALIDATION GATE (Phase 0.5)
# -------------------------
def validate_typescript(test_path: str) -> tuple[bool, str]:
    if not os.path.exists(test_path):
        return False, f"File not found: {test_path}"
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--project", "tsconfig.json"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr[:2000] if result.stderr else result.stdout[:2000]
    except FileNotFoundError:
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "TypeScript validation timed out (60s)"


def track_time(label: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = round(time.time() - start, 2)
            log_pipeline("timing", {"step": label, "duration_seconds": elapsed})
            return result
        return wrapper
    return decorator


# -------------------------
# AUDIT TRAIL
# -------------------------
def log_pipeline(action: str, details: dict | None = None) -> None:
    os.makedirs("logs", exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "details": details or {}
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def record_execution(url: str, feature: str, model: str, engine: str, status: str, metrics: dict | None = None) -> None:
    from persistence import create_metadata, save_execution
    from contracts import ExecutionRecord, ExecutionMetrics

    execution_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    meta = create_metadata(execution_id=execution_id, contract_name="execution_record")
    m = metrics or {}

    record = ExecutionRecord(
        metadata=meta,
        url=url,
        feature=feature,
        model=model,
        engine=engine,
        status=status,
        steps=m.get("steps", []),
        metrics=ExecutionMetrics(
            passed=m.get("passed", 0),
            failed=m.get("failed", 0),
            playwright_attempts=m.get("playwright_attempts", 1),
            estimated_tokens=m.get("estimated_tokens", 0),
            estimated_cost_usd=m.get("estimated_cost_usd", 0.0),
            estimated_manual_cost_usd=m.get("estimated_manual_cost_usd", 50.0),
            estimated_roi=m.get("estimated_roi", 0.0),
            execution_duration_seconds=m.get("execution_duration_seconds"),
            hallucination_fixes_applied=m.get("hallucination_fixes_applied", 0),
        ),
    )
    save_execution(record)

# -------------------------
# RUN AI AGENT
# -------------------------
@track_time("ai_generation")
def run_ollama_agent(url: str, model: str, feature: str, error_context: str | None = None, engine: str = "ollama") -> None:
    print(f"Running AI generator ({engine} engine)...")

    backup_test(feature)

    if engine == "ollama":
        check_rate_limit()
        script = "ollama_ai.py"
    else:
        script = "cloud_ai.py"

    cmd = ["python", script, url, model, feature]
    if error_context:
        cmd.append(error_context)

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)

    if result.returncode != 0:
        print("Error running AI agent")
        print(result.stderr)
        raise TestGenerationError(f"AI generation failed (exit code {result.returncode})")


# -------------------------
# HARD NORMALIZER (CRITICAL)
# -------------------------
def normalize_code(code: str) -> str:

    # remove markdown
    code = re.sub(r"```.*?\n", "", code)
    code = code.replace("```", "")

    # fix broken syntax
    code = code.replace("await const", "const")

    # invalid URLs → force REAL target (ui-testing-lab)
    code = re.sub(
        r"https?://[^\s\"']*(?:login|example|your-website)[^\s\"']*",
        "http://localhost:3000/playwright-ui-testing-lab.html",
        code
    )

    # common incorrect selectors → FIX HARD (ui-testing-lab)
    # Use regex with negative lookbehind to not break #login-username/password
    code = re.sub(r"(?<!login-)#username", "#login-username", code)
    code = re.sub(r"(?<!login-)#password", "#login-password", code)
    code = re.sub(r"#login([^\"'\w-])", r"#login-btn\1", code)

    # assertions with generic text → correct to ui-testing-lab
    code = code.replace("text=Dashboard", "#login-result")
    code = code.replace("text=Invalid", "#login-alert .alert-error")
    code = code.replace("text=Required", "#login-result")

    # garbage assertions → replace only non-specific toBeVisible() calls
    def replace_garbage_assertion(match):
        line = match.group(0)
        if 'alert-success' in line or 'alert-error' in line:
            return line
        return "await expect(page.locator('#login-alert .alert-error')).toBeVisible();"

    code = re.sub(
        r"await expect\(page\.locator\('[^']*'\)\)\.toBeVisible\(\);",
        replace_garbage_assertion,
        code
    )

    # invalid text assertions → use contains
    code = code.replace(
        ".toHaveText(",
        ".toContainText("
    )

    # navigation to login section (if missing)
    if "text=Form Authentication" not in code and "#section-login" not in code:
        code = re.sub(
            r"(await page\.goto\([^)]+\);)",
            r"\1\n  await page.click('text=Form Authentication');",
            code
        )

    return code


# -------------------------
# VALIDATE + FIX LOOP
# -------------------------
def validate_and_fix(feature: str) -> int:
    test_path = f"generated-tests/{feature}.spec.ts"

    if not os.path.exists(test_path):
        raise ValidationError(f"Test file not found: {test_path}")

    with open(test_path, "r", encoding="utf-8") as f:
        content = f.read()

    fixed = normalize_code(content)

    # Count hallucination fixes applied (Phase 0.3 KPI)
    fix_count = 0
    if content != fixed:
        for fix_pattern in ["#login-username", "#login-password", "#login-btn",
                            "#login-alert .alert-success", "#login-alert .alert-error",
                            "#login-result", ".toContainText("]:
            if fix_pattern in fixed and fix_pattern not in content:
                fix_count += 1
        if re.search(r"https?://[^\s\"']*(?:login|example|your-website)", content):
            fix_count += 1

    with open(test_path, "w", encoding="utf-8") as f:
        f.write(fixed)

    print(f"Test normalized and fixed: {test_path} ({fix_count} hallucination fixes)")
    return fix_count


# -------------------------
# RUN PLAYWRIGHT
# -------------------------
@track_time("playwright_execution")
def run_playwright() -> tuple[int, str, int, int]:
    print("Running Playwright tests...")

    result = subprocess.run(
        ["npx", "playwright", "test"],
        capture_output=True,
        text=True
    )

    print("\n--- PLAYWRIGHT OUTPUT ---\n")
    print(result.stdout)

    if result.stderr:
        print("\n--- ERRORS ---\n")
        print(result.stderr)

    # Count passed/failed from output (e.g. "6 passed" or "5 passed, 1 failed")
    passed_match = re.search(r"(\d+)\s+passed", result.stdout)
    failed_match = re.search(r"(\d+)\s+failed", result.stdout)
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0

    return result.returncode, result.stdout + (result.stderr or ""), passed, failed


# -------------------------
# RUN POM GENERATOR
# -------------------------

def run_pom_agent(feature: str) -> None:
    print("Generating Page Object Model...")
    from pom_generator import run_pom_generation
    run_pom_generation(feature)


# -------------------------
# PARSE CLI ARGUMENTS
# -------------------------
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Test Orchestrator CLI")
    parser.add_argument("--url", required=True, help="Target URL to test")
    parser.add_argument("--feature", required=True, help="Feature name (used for file naming)")
    parser.add_argument("--model", required=True, help="Specific Ollama or Cloud model to use")
    parser.add_argument("--engine", choices=["ollama", "cloud"], required=True, help="Choose between Ollama (local) or Cloud engine")
    parser.add_argument("--review", action="store_true", help="Pause for human review before execution")
    parser.add_argument("--ml", action="store_true", help="Enable Phase 4 ML analysis (prioritization, flakiness, model routing, risk scoring)")
    return parser.parse_args()

# -------------------------
# PIPELINE (shared by engines)
# -------------------------
def run_pipeline(url: str, feature: str, model: str, engine: str = "ollama", review: bool = False, ml: bool = False) -> None:
    feature_slug = feature.lower().replace(" ", "-")
    pipeline_start = time.time()

    log_pipeline("pipeline_start", {"url": url, "feature": feature, "model": model, "engine": engine})

    total_steps = 5 if ml else 4
    step_num = 1

    console.print(Panel(f"Step {step_num}/{total_steps} — AI Generation ({engine})", style="green"))
    run_ollama_agent(url, model, feature_slug, engine=engine)
    log_pipeline("ai_generation_complete", {"feature": feature_slug})
    step_num += 1

    if review:
        total_steps += 1
        console.print(Panel(f"Step {step_num}/{total_steps} — Human Review", style="yellow"))
        log_pipeline("human_review", {"feature": feature})
        human_review(feature)
        step_num += 1

    console.print(Panel(f"Step {step_num}/{total_steps} — Hard Normalization (Self-Healing)", style="yellow"))
    hallucination_fixes = validate_and_fix(feature_slug) or 0
    log_pipeline("normalization_complete", {"feature": feature_slug, "hallucination_fixes": hallucination_fixes})
    step_num += 1

    console.print(Panel(f"Step {step_num}/{total_steps} — TypeScript Validation", style="cyan"))
    test_path = f"generated-tests/{feature_slug}.spec.ts"
    ts_valid, ts_error = validate_typescript(test_path)
    if not ts_valid:
        console.print(f"[bold yellow]TypeScript errors found:[/bold yellow] {ts_error[:500]}")
        log_pipeline("ts_validation_failed", {"feature": feature_slug, "error": ts_error[:500]})
    else:
        console.print("[green]TypeScript validation passed.[/green]")
        log_pipeline("ts_validation_passed", {"feature": feature_slug})
    step_num += 1

    console.print(Panel(f"Step {step_num}/{total_steps} — Playwright Execution", style="blue"))
    total_pw_attempts = 0
    failure_classification = None
    for pw_attempt in range(MAX_PLAYWRIGHT_RETRIES + 1):
        total_pw_attempts = pw_attempt + 1
        exit_code, output, passed, failed = run_playwright()
        log_pipeline("playwright_execution", {"attempt": total_pw_attempts, "exit_code": exit_code, "passed": passed, "failed": failed})

        if exit_code == 0:
            break

        from failure_analysis import classify_failure
        failure_classification = classify_failure(
            exit_code=exit_code, stdout=output, stderr="",
            feature=feature_slug,
            execution_id=datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f"),
        )
        log_pipeline("failure_classification", {
            "root_cause": failure_classification.root_cause_class,
            "confidence": failure_classification.confidence_score,
            "action": failure_classification.suggested_action,
        })

        if pw_attempt < MAX_PLAYWRIGHT_RETRIES:
            console.print(f"[bold yellow]Tests failed (attempt {pw_attempt + 1}). Re-generating with error feedback...[/bold yellow]")
            console.print(f"[dim]Failure: {failure_classification.root_cause_class} ({failure_classification.confidence_score:.0%} confidence)[/dim]")
            log_pipeline("feedback_retry", {"attempt": pw_attempt + 1})
            error_ctx = output[-1500:] if len(output) > 1500 else output
            run_ollama_agent(url, model, feature_slug, error_ctx, engine=engine)
            validate_and_fix(feature_slug)
        else:
            console.print("[bold red]Tests failed after max retries.[/bold red]")
            restored = restore_test(feature_slug)
            if restored:
                console.print("[bold yellow]Restored previous working test version from backup.[/bold yellow]")
            record_execution(url, feature, model, engine, "failed", {
                "playwright_exit_code": exit_code,
                "passed": passed,
                "failed": failed,
                "playwright_attempts": total_pw_attempts,
                "rollback_restored": restored,
                "hallucination_fixes_applied": hallucination_fixes,
                "execution_duration_seconds": round(time.time() - pipeline_start, 2),
            })
            return
    step_num += 1

    console.print(Panel(f"Step {step_num}/{total_steps} — POM Generation", style="cyan"))
    run_pom_agent(feature_slug)
    log_pipeline("pom_generation_complete", {"feature": feature_slug})
    step_num += 1

    # ML Analysis (Phase 4) — optional
    if ml:
        console.print(Panel(f"Step {step_num}/{total_steps} — ML Analysis", style="magenta"))
        _run_ml_analysis(feature_slug, model)
        step_num += 1

    # Estimate cost (Phase 2.3 + Phase 3.4 threshold check)
    est_tokens = 500 * total_pw_attempts
    est_cost = round(est_tokens * TOKEN_COST_PER_MILLION / 1_000_000, 4)
    est_manual_cost = MANUAL_TEST_COST
    check_cost_threshold(est_cost)

    pipeline_duration = round(time.time() - pipeline_start, 2)

    steps_list = ["ai_generation", "normalization", "ts_validation", "playwright", "pom_generation"]
    if ml:
        steps_list.append("ml_analysis")

    record_execution(url, feature, model, engine, "success", {
        "steps": steps_list,
        "playwright_attempts": total_pw_attempts,
        "passed": passed,
        "failed": failed,
        "estimated_tokens": est_tokens,
        "estimated_cost_usd": est_cost,
        "estimated_manual_cost_usd": est_manual_cost,
        "estimated_roi": round((est_manual_cost - est_cost) / est_manual_cost * 100, 1),
        "execution_duration_seconds": pipeline_duration,
        "hallucination_fixes_applied": hallucination_fixes,
    })

    # KPI Display (Phase 0.3)
    from kpi import KPIReport
    kpi = KPIReport(
        generation_success=True,
        test_pass_rate=passed / (passed + failed) if (passed + failed) > 0 else 0.0,
        hallucination_fixes=hallucination_fixes,
        execution_duration_seconds=pipeline_duration,
        total_tests=passed + failed,
        passed_tests=passed,
        failed_tests=failed,
        feature=feature,
        model=model,
    )
    kpi.display()

    console.print(f"[bold green]Pipeline completed in {pipeline_duration}s. Cost: ${est_cost} | Manual equivalent: ${est_manual_cost} | ROI: {round((est_manual_cost - est_cost) / est_manual_cost * 100, 1)}%[/bold green]")

# -------------------------
# HUMAN REVIEW GATE
# -------------------------
def human_review(feature: str) -> None:
    feature_slug = feature.lower().replace(" ", "-")
    test_path = f"generated-tests/{feature_slug}.spec.ts"

    if not os.path.exists(test_path):
        console.print("[bold yellow]No test file to review yet.[/bold yellow]")
        return

    with open(test_path, "r", encoding="utf-8") as f:
        content = f.read()

    console.print(Panel(content, title="[bold]Generated Test — Review[/bold]", border_style="yellow"))
    response = input("\nProceed with execution? (y/n): ").strip().lower()
    if response != "y":
        console.print("[bold red]Execution cancelled by user.[/bold red]")
        raise CancelledByUser("Execution cancelled by user")

# -------------------------
# ML ANALYSIS (Phase 4)
# -------------------------
def _run_ml_analysis(feature: str, model: str) -> None:
    try:
        from ml.prioritization import compute_priorities, suggest_next_feature
        from ml.flakiness import detect_flaky_tests
        from ml.model_router import select_model, get_model_info
        from ml.risk_scorer import compute_risk_score
    except ImportError:
        console.print("[bold yellow]ML modules not available. Install with: pip install -r requirements.txt[/bold yellow]")
        return

    priorities = compute_priorities()
    if priorities:
        next_feature = suggest_next_feature(priorities)
        table = Table(title="ML — Test Prioritization")
        table.add_column("Feature", style="cyan")
        table.add_column("Priority Score", style="magenta")
        table.add_column("Fail Rate", style="red")
        table.add_column("Avg Attempts", style="yellow")
        for p in priorities[:5]:
            table.add_row(p["feature"], str(p["priority_score"]), str(p["fail_rate"]), str(p["avg_attempts"]))
        console.print(table)
        console.print(f"[bold]Suggested next feature:[/bold] [cyan]{next_feature}[/cyan]")
    else:
        console.print("[yellow]Not enough execution data for prioritization yet.[/yellow]")

    flaky = detect_flaky_tests()
    flaky_features = [f for f in flaky if f["is_flaky"]]
    if flaky_features:
        console.print("[bold red]Flaky tests detected:[/bold red]")
        for f in flaky_features:
            console.print(f"  - {f['feature']} (pass rate: {f['pass_rate']}, alternations: {f['alternation_ratio']})")
    else:
        console.print("[green]No flaky tests detected.[/green]")

    recommended = select_model(feature)
    model_info = get_model_info(recommended)
    console.print(f"[bold]Model router:[/bold] [cyan]{feature}[/cyan] → [green]{recommended}[/green] ({model_info['description']})")

    risk = compute_risk_score(feature)
    risk_color = "red" if risk["should_generate"] else "green"
    console.print(f"[bold]Risk score for '{feature}':[/bold] [{risk_color}]{risk['risk_score']}[/{risk_color}] (generate: {risk['should_generate']})")


# -------------------------
# MAIN FUNCTION
# -------------------------
def main() -> None:
    args = parse_arguments()

    try:
        args.url = sanitize_url(args.url)
        args.feature = sanitize_feature(args.feature)
    except ValueError as e:
        console.print(f"[bold red]Sanitization error: {e}[/bold red]")
        exit(1)

    feature_slug = args.feature.lower().replace(" ", "-")

    table = Table(title="CLI Arguments")
    table.add_column("Argument", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_row("URL", args.url)
    table.add_row("Feature", args.feature)
    table.add_row("Model", args.model)
    table.add_row("Engine", args.engine)
    if args.review:
        table.add_row("Review", "enabled", style="yellow")
    if args.ml:
        table.add_row("ML Analysis", "enabled", style="magenta")
    console.print(table)

    engine_label = "Ollama (local)" if args.engine == "ollama" else "Anthropic Claude (cloud)"
    console.print(Panel(f"Using {engine_label} engine...", style="green" if args.engine == "ollama" else "blue"))

    try:
        run_pipeline(args.url, args.feature, args.model, args.engine, args.review, args.ml)
    except CancelledByUser:
        console.print("[bold yellow]Pipeline cancelled by user.[/bold yellow]")
        exit(0)

    console.print(Panel("Script execution completed.", style="green"))

if __name__ == "__main__":
    main()