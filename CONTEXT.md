# AI Test Orchestrator — Context

## Overview

**AI Test Orchestrator** is an intelligent, self-healing E2E testing pipeline that uses local LLMs (Ollama) to automatically generate, validate, normalize, execute, and evolve Playwright tests. Starting from a URL and a feature description, it generates test suites, runs them, and refactors them into Page Object Models (POMs).

Created by [Cristian Nadj](https://github.com/crisemy) — https://github.com/crisemy/ai-test-orchestrator

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | Python 3.12 |
| Testing (Node.js) | Playwright + TypeScript (`@playwright/test` ^1.59.1) |
| Local LLM | Ollama (Python SDK 0.4.7) + `qwen2.5-coder:7b` |
| Cloud LLM (exp.) | Anthropic Claude (`anthropic` SDK) |
| CLI/UI | Rich 13.7.1 |
| HTTP | Requests 2.32.3 |
| Validation | Pydantic 2.9.2 |
| Config | python-dotenv 1.0.1 |

---

## Project Structure

```
ai-test-orchestrator/
├── .env                          # ANTHROPIC_API_KEY (sensitive, gitignored)
├── .gitignore
├── .vscode/
│   ├── launch.json               # Debug config for "Run Ollama Script"
│   └── settings.json
├── LICENSE                       # MIT License
├── README.md
├── AGENTS.md                     # AI agent behavior rules (extends ai-qa-core-framework)
├── CONTEXT.md                    # This file
├── CONTRIBUTING.md               # Contribution guidelines
├── CODE_OF_CONDUCT.md            # Contributor Covenant v2.1
├── CHANGELOG.md                  # Release history
├── IMPROVEMENT-PLAN.md           # Phased improvement roadmap
├── pyproject.toml                # Python project metadata + tool config
├── demo.ps1                      # One-command Windows demo script
├── package.json                  # DevDependency: @playwright/test
├── package-lock.json
├── playwright.config.js          # HTML reporter + webServer ui-testing-lab
├── ui-testing-lab/               # Local test app (SPA with 36 scenarios)
├── requirements.txt              # requests, pydantic, rich, python-dotenv, ollama, anthropic, scikit-learn
│
├── config.py                     # Consolidated constants + env-var overrides + custom exception classes
├── orchestrator.py               # Pipeline orchestrator (router, normalizer, executor, cost metrics, TS gate)
├── ollama_ai.py                  # Ollama interface for test generation (+ feedback loop)
├── cloud_ai.py                   # Anthropic Claude cloud engine (--engine cloud)
├── pom_generator.py              # Page Object Model generator (multi-feature, camelCase)
├── test_data_generator.py        # Synthetic test data via LLM
├── persistence.py                # Structured persistence via Pydantic contracts (Phase 0.2)
├── kpi.py                        # KPI measurement + Rich display (Phase 0.3)
├── failure_analysis.py           # Failure classifier (Phase 0.4)
├── tsconfig.json                 # TypeScript config for tsc --noEmit gate (Phase 0.5)
├── contracts/
│   └── __init__.py               # Pydantic data contracts: ContractMetadata, ExecutionRecord, FailureRecord (Phase 0.1)
│
├── ci/
│   └── smoke.spec.ts             # Deterministic Playwright smoke test for CI
├── .github/
│   └── workflows/
│       ├── ci.yml                # GitHub Actions CI (pytest, Playwright, POM validation, experiments)
│       └── docker.yml            # GitHub Actions Docker registry push (ghcr.io)
├── Dockerfile                    # Containerized runtime (Python 3.12 + Node.js 22 + Playwright)
├── .dockerignore                 # Excludes dev artifacts from Docker builds
├── ai-qa-core-framework/         # External QA framework reference (skills, contracts, runbooks)
├── dashboard/
│   └── app.py                    # Streamlit QA dashboard
├── experiments/
│   └── runner.py                 # Prompt experiment runner + comparator
├── red_team/
│   └── suite.py                  # Security testing (injection, unsafe code scan)
├── ml/
│   ├── prioritization.py         # Test prioritization (heuristic + sklearn)
│   ├── flakiness.py              # Flaky test detection from execution patterns
│   ├── model_router.py           # Intelligent LLM model selection by complexity
│   └── risk_scorer.py            # Risk-based feature prioritization for generation
├── generated-tests/
│   ├── {feature}.spec.ts         # AI-generated test, named by --feature
│   ├── test_data.json            # Synthetic test data sets
│   └── backups/                  # Rollback backups (auto-managed)
├── pom/
│   └── {feature}_page.ts         # Generated POM, named by --feature
├── logs/
│   └── pipeline.log              # Per-step JSON audit trail (includes timing)
└── reports/                      # HTML reports + execution_log.json (includes cost metrics)
```

---

## Architecture and Flow

### Pipeline (orchestrator.py) — `run_pipeline()`

1. **Argument parsing** — `--url`, `--feature`, `--model`, `--engine`, `--review`
2. **AI Generation** — Calls `ollama_ai.py` via subprocess (supports error feedback context); timing tracked
3. **Human Review Gate** — If `--review` flag is set, pauses and shows test in Rich panel for approval
4. **Normalization (Self-Healing)** — Hard Normalizer via regex: fixes LLM hallucinations
5. **Playwright Execution + Feedback Loop** — Runs `npx playwright test`; if tests fail, re-generates injecting error context (up to 2 retries); timing tracked; passed/failed counted
6. **POM Generation** — Extracts selectors via regex and generates `{Feature}Page` class; timing tracked
7. **Cost Estimation** — Token estimate × cost/M tokens, vs manual test cost, ROI % displayed and persisted in `reports/execution_log.json`

### Key Patterns

- **Subprocess Orchestration**: Python orchestrates Node.js processes (Playwright, generation)
- **Multi-Feature Pipeline**: `--feature` parameter drives file naming: `generated-tests/{feature}.spec.ts`, `pom/{feature}_page.ts`
- **Self-Healing**: Deterministic regex-based normalizer + retry loop in `ollama_ai.py` (3 attempts + fallback)
- **Feedback Loop**: Playwright failures trigger re-generation with error context injected into the LLM prompt (architecture step from ai-qa-core-framework)
- **POM Generation**: Selector extraction via regex, valid TypeScript camelCase identifiers, dynamic class names
- **Audit Trail**: Every pipeline step logged to `logs/pipeline.log` (JSONL); structured execution records in `reports/execution_log.json`
- **Human-in-the-Loop**: Optional `--review` flag adds a manual approval gate between generation and execution
- **Input Sanitization**: `sanitize_url()` and `sanitize_feature()` strip shell metacharacters/control chars before LLM prompt injection
- **Test Rollback**: `backup_test()` snapshots existing test before overwriting; `restore_test()` recovers on persistent failure
- **Rate Limiting + Cost Control**: Max 5 Ollama calls/minute; cost threshold warning at $0.50/run
- **Red Team Suite**: `red_team/suite.py` tests prompt injection via `--feature`/`--url` and scans for unsafe code patterns
- **ML Analysis** (`--ml` flag): Post-pipeline analysis including test prioritization, flakiness detection, intelligent model routing, and risk scoring (Phase 4)
- **Test Prioritization**: `ml/prioritization.py` ranks features by fail rate + attempts + cost (heuristic, optional sklearn)
- **Flakiness Detection**: `ml/flakiness.py` identifies tests with alternating pass/fail patterns from execution history
- **Model Router**: `ml/model_router.py` selects optimal LLM model based on estimated test complexity (1–10 scale)
- **Risk Scorer**: `ml/risk_scorer.py` computes risk scores from business criticality + bug history + change frequency
- **Dual Engine**: Supports `--engine ollama` (local, implemented) and `--engine cloud` (stub, not implemented)

---

## Main Modules

### `orchestrator.py` (~400 lines)
Entry point. Key functions:
- `parse_arguments()` — CLI args (`--url`, `--feature`, `--model`, `--engine`, `--review`)
- `sanitize_url()` / `sanitize_feature()` — input sanitization (Phase 3.2)
- `backup_test()` / `restore_test()` — rollback mechanism (Phase 3.3)
- `check_rate_limit()` — max 5 Ollama calls/min (Phase 3.4)
- `check_cost_threshold()` — alert if cost exceeds $0.50 (Phase 3.4)
- `run_ollama_agent(url, model, feature, error_context)` — spawn `ollama_ai.py` with backup + rate limit
- `normalize_code(code)` — Hard Normalizer (regex fixes)
- `validate_and_fix(feature)` — read, normalize, and write the test
- `run_playwright()` — run tests, returns exit code + output for feedback loop
- `run_pom_agent(feature)` — call `pom_generator` with feature name
- `log_pipeline(action, details)` — append JSON entry to `logs/pipeline.log`
- `record_execution(url, feature, model, engine, status, metrics)` — save structured record to `reports/execution_log.json`
- `human_review(feature)` — display test in Rich panel, prompt for confirmation
- `run_pipeline(url, feature, model, review)` — full pipeline with feedback loop + rollback
- `main()` — parse args + sanitize, dispatch to `run_pipeline()` or cloud stub

### `ollama_ai.py` (~200 lines)
Local LLM interface:
- `generate_tests(url, feature, error_context)` — up to 3 attempts, temp 0.2, accepts error feedback for retry loop
- `extract_code(text)` — extract TypeScript/JS from markdown blocks
- `is_valid_playwright(code)` — structure validation
- `save_file(code)` — save to `generated-tests/{feature}.spec.ts`
- Loads prompt from `prompt_template.json`

### `pom_generator.py` (~140 lines)
POM generation:
- `clean_selector_name(sel)` — converts selectors to valid TypeScript camelCase identifiers
- `feature_class_name(feature)` — generates `{Feature}Page` class name from feature slug
- `extract_selectors(code)` — regex on `page.fill()`, `page.click()`, `page.locator()`, `locator()`
- `generate_pom(selectors, feature)` — generates TypeScript class with dynamic name and camelCase locators
- `run_pom_generation(feature)` — entry point

### `test-cloud-ai.py` (19 lines)
Experimental Claude prototype (incomplete).

### `playwright.config.js` (6 lines)
Configures HTML reporter at `reports/html-report`, `open: never`.

### `prompt_template.json` (3 lines)
Externalized prompt template with strict generation instructions.

### `dashboard/app.py` (~100 lines)
Streamlit QA Dashboard:
- Overview metrics (total runs, success rate, cost, models)
- Execution history table with per-run metrics
- KPI trend charts (cost per run, ROI %)
- Pipeline log viewer
- Status distribution chart

### `experiments/runner.py` (~90 lines)
Prompt experiment system:
- `run_experiment()` — runs pipeline with custom model/temperature, saves card with output
- `compare_experiments()` — loads all experiment cards, displays comparison table

### `red_team/suite.py` (~120 lines)
Security testing suite:
- `test_injection()` — runs orchestrator with injection payloads via `--feature`
- `scan_for_unsafe_code()` — regex scan for eval/exec/subprocess patterns in generated tests
- `run_suite()` — executes all tests, saves report to `red_team/report.json`

### `test_data_generator.py` (~60 lines)
Synthetic test data generation:
- `generate_test_data()` — prompts LLM for 5 varied credential sets (valid + invalid + edge)
- `get_fallback_data()` — hardcoded fallback set
- Saves as `generated-tests/test_data.json`

### `ml/prioritization.py` (~90 lines)
Test prioritization using execution history:
- `_extract_features(executions)` — builds feature vectors (fail rate, avg attempts, cost per run)
- `_compute_priority_score(fail_rate, avg_attempts, cost_per_run)` — heuristic scoring (higher = more urgent)
- `compute_priorities()` — loads execution log, computes scores, saves to `reports/priorities.json`
- `suggest_next_feature(priorities)` — returns highest-priority feature name
- Optional: `RandomForestRegressor` when sklearn is available (auto-detected)

### `ml/flakiness.py` (~60 lines)
Flaky test detection:
- `detect_flaky_tests(min_runs=3)` — analyzes execution history for alternating pass/fail patterns
- `get_flaky_features(min_runs=3)` — returns names of tests classified as flaky

### `ml/model_router.py` (~65 lines)
Intelligent LLM model selection:
- `_estimate_complexity(feature_name, selectors, assertions)` — scores feature from 1–10
- `select_model(feature_name, selectors, assertions, preference)` — maps complexity to model tier
- `get_model_info(model_name)` — returns description for any known model

### `ml/risk_scorer.py` (~65 lines)
Risk-based feature prioritization:
- `compute_risk_score(feature_name, custom_config)` — computes risk from criticality + bug rate + change frequency
- `prioritize_features(feature_names, custom_config)` — sorts features by descending risk score

---

## Useful Commands

```bash
# Run full pipeline (uses local ui-testing-lab by default)
python orchestrator.py --url "http://localhost:3000/playwright-ui-testing-lab.html" --feature "login" --model "qwen2.5-coder:7b" --engine ollama

# With human review gate
python orchestrator.py --url "..." --feature "login" --model "qwen2.5-coder:7b" --engine ollama --review

# Multi-feature: generate tests for any feature
python orchestrator.py --url "..." --feature "checkout" --model "qwen2.5-coder:7b" --engine ollama

# Run test generation only (standalone)
python ollama_ai.py <url> <model> [feature] [error_context]

# Run tests with automatic server (webServer in playwright.config.js)
npx playwright test

# Run pipeline with ML analysis (Phase 4)
python orchestrator.py --url "..." --feature "login" --model "qwen2.5-coder:7b" --engine ollama --ml

# Run ML analysis only (prioritization, flakiness, risk scoring)
python -c "from ml.prioritization import compute_priorities; print(compute_priorities())"
python -c "from ml.flakiness import detect_flaky_tests; print(detect_flaky_tests())"
python -c "from ml.model_router import select_model; print(select_model('login'))"
python -c "from ml.risk_scorer import compute_risk_score; print(compute_risk_score('login'))"

# Generate POM standalone
python -c "import pom_generator; pom_generator.run_pom_generation('login')"

# View audit trail
Get-Content logs/pipeline.log

# View execution history (with cost metrics)
Get-Content reports/execution_log.json | ConvertFrom-Json

# Launch QA dashboard
streamlit run dashboard/app.py

# Run a prompt experiment
python experiments/runner.py --label "temp-0-5" --temperature 0.5

# Compare all experiments
python experiments/runner.py --compare

# Generate synthetic test data
python test_data_generator.py

# Run Red Team security suite
python red_team/suite.py

# View rollback backups
Get-ChildItem generated-tests/backups/
```

---

## Project Status

### Phase 1 ✅ — Architectural Maturity

- [x] Multi-feature support (parameterized `--feature`)
- [x] Feedback loop (re-generate on failure with error context)
- [x] Human-in-the-Loop (`--review` flag)
- [x] Audit trail (`logs/pipeline.log` + `reports/execution_log.json`)
- [x] CORE Agent formalized (Router, Context, Skills)

### Phase 2 ✅ — Observability and Experimentation

- [x] QA Dashboard (`streamlit run dashboard/app.py`)
- [x] Prompt experiments (`experiments/runner.py`)
- [x] Quality economics (cost metrics, ROI % on each run)
- [x] Test data generation (`test_data_generator.py`)

### Phase 3 ✅ — Security and Operations

- [x] Red Team security suite (`red_team/suite.py`)
- [x] Input sanitization (`sanitize_url` / `sanitize_feature`)
- [x] Test rollback (`backup_test` / `restore_test`)
- [x] Rate limiting + cost threshold control

### Phase 4 ✅ — Advanced ML

- [x] Test prioritization model (`ml/prioritization.py`)
- [x] Flakiness detection (`ml/flakiness.py`)
- [x] Intelligent LLM model selection (`ml/model_router.py`)
- [x] Risk-based test generation scoring (`ml/risk_scorer.py`)
- [x] `--ml` flag integrated into orchestrator pipeline

### Phase 0 ✅ — Foundation

- [x] **Data Contracts** (`contracts/`) — Pydantic models: `ContractMetadata`, `GenerationRecord`, `ExecutionRecord`, `FailureRecord`, `ExecutionMetrics`. Typed schemas with canonical metadata per `data_contracts.md`.
- [x] **Persistence Pipeline** (`persistence.py`) — Structured save/load using Pydantic contracts, compatible with existing `reports/execution_log.json` and `logs/pipeline.log`.
- [x] **KPI Measurement** (`kpi.py`) — `KPIReport` class with Rich display: generation success rate, test pass rate, hallucination fixes, execution duration. Green/Yellow/Red thresholds. `compute_historical_kpis()` for trend analysis.
- [x] **Failure Analysis** (`failure_analysis.py`) — `classify_failure()` parses Playwright output and classifies as `test_issue`, `environment_issue`, `product_bug`, or `unknown` with confidence scores, evidence, and suggested actions.
- [x] **TypeScript Validation Gate** (`orchestrator.py:validate_typescript`) — `npx tsc --noEmit` runs before Playwright execution. Graceful degrade if tsc unavailable. `tsconfig.json` created for the project.

### Phase 3 ✅ — Security and Operations

- [x] Red Team security suite (`red_team/suite.py`)
- [x] Input sanitization (`sanitize_url` / `sanitize_feature`)
- [x] Test rollback (`backup_test` / `restore_test`)
- [x] Rate limiting + cost threshold control
- [x] Cloud engine (`cloud_ai.py`) — Anthropic Claude integration, fully wired into `--engine cloud`

### Phase 5 ✅ — CI/CD

- [x] **Dockerfile** — multi-stage Python 3.12 + Node.js 22 + Playwright chromium + TypeScript
- [x] **.dockerignore** — excludes venv, node_modules, generated-tests, reports, logs, etc.
- [x] **GitHub Actions CI** (`.github/workflows/ci.yml`) — 4 jobs: pytest, Playwright execution, experiment card archive, POM TS validity
- [x] **GitHub Actions Docker registry** (`.github/workflows/docker.yml`) — push to ghcr.io on version tags + latest on main
- [x] **package.json** — added `typescript` as devDependency for TS validation gate
