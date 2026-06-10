# AI Test Orchestrator

[![CI](https://github.com/crisemy/ai-test-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/crisemy/ai-test-orchestrator/actions/workflows/ci.yml)
[![Docker](https://github.com/crisemy/ai-test-orchestrator/actions/workflows/docker.yml/badge.svg)](https://github.com/crisemy/ai-test-orchestrator/actions/workflows/docker.yml)
[![Playwright](https://img.shields.io/badge/playwright-%232EAD33.svg?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)

An intelligent, self-healing E2E testing pipeline that leverages Local LLMs (via Ollama) to generate, validate, and evolve Playwright test suites against a local SPA test app (`ui-testing-lab`).

## Key Features

- **AI-Powered Test Generation**: Automatically generates multi-scenario Playwright tests using `qwen2.5-coder`.
- **Self-Healing Normalization**: A custom "Hard Normalizer" loop that corrects common LLM hallucinations, fixes selectors, and maps generic URLs to the local test app.
- **Multi-Feature Support**: Parameterized via `--feature` — generates `generated-tests/{feature}.spec.ts` and `pom/{feature}_page.ts` automatically.
- **Feedback Loop**: If Playwright tests fail, the pipeline re-generates them injecting the error as context for the LLM (up to 2 retries).
- **Human-in-the-Loop**: Optional `--review` flag pauses after generation to show the test in a Rich panel for approval before execution.
- **QA Dashboard**: Streamlit dashboard (`streamlit run dashboard/app.py`) showing execution history, KPI trends, cost/ROI metrics.
- **Quality Economics**: Cost estimation per run (token estimate), ROI % vs manual testing, displayed inline and persisted.
- **Prompt Experiments**: Run pipeline with different model/temperature configs, compare KPIs (`experiments/runner.py`).
- **Synthetic Test Data**: Generate varied credential sets via LLM (`test_data_generator.py`).
- **Input Sanitization**: CLI arguments (`--url`, `--feature`) are sanitized to prevent prompt injection.
- **Test Rollback**: Automatic file backup before each generation; restores previous version on persistent failure.
- **Rate Limiting + Cost Control**: Max 5 LLM calls/minute; warns if estimated cost exceeds $0.50.
- **Dual Engine**: Supports both `--engine ollama` (local, via Ollama) and `--engine cloud` (Anthropic Claude).
- **Data Contracts**: Pydantic-validated typed schemas (`contracts/`) with canonical metadata, used by all persistence.
- **KPI Dashboard per Run**: Rich table at end of pipeline — generation success rate, test pass rate, hallucination fixes, execution duration.
- **Failure Analysis**: Playwright failures classified as `test_issue` / `environment_issue` / `product_bug` / `unknown` with confidence scores and suggested actions.
- **TypeScript Pre-Validation**: `npx tsc --noEmit` gate runs before Playwright execution.
- **Red Team Suite**: `python red_team/suite.py` tests injection payloads and scans for unsafe code patterns.
- **ML Analysis** `--ml`: Post-pipeline intelligence — test prioritization, flakiness detection, model routing, risk scoring.
- **Audit Trail**: Every pipeline step logged to `logs/pipeline.log` (JSON) and structured execution records in `reports/execution_log.json`.
- **Local Test App**: Includes a full SPA (`ui-testing-lab/`) with 36 interaction scenarios served via `http-server`.
- **Automated Execution**: Seamlessly triggers Playwright runners and captures real-time results.
- **Page Object Model (POM) Evolution**: Dynamically extracts selectors from generated tests and refactors them into POM structures.
- **Local & Private**: Powered by Ollama, ensuring your testing logic and data stay on your machine.

## Orchestration Workflow

The `orchestrator.py` script manages the entire lifecycle:

1. **AI Generation**: Calls `ollama_ai.py` to prompt the local LLM for test code.
2. **Normalization**: Sanitizes the output, removes markdown, and applies logic-based fixes to provide stable code.
3. **Validation**: Executes the generated tests using Playwright.
4. **POM Generation**: Analyzes the passing tests to create reusable Page Objects in the `pom/` directory.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Ollama**: [Download and Install Ollama](https://ollama.com/)
- **Model**: Pull the required model:

```bash
  ollama pull qwen2.5-coder:7b # Or other models of your choice
```

## Docker (CI / Containerized Run)

A `Dockerfile` is provided for containerized execution and CI:

```bash
# Build the image
docker build -t ai-test-orchestrator .

# Run the orchestrator (shows --help by default)
docker run --rm ai-test-orchestrator

# Run with arguments (Ollama must be reachable from container)
docker run --rm --network host ai-test-orchestrator \
  --url "http://host.docker.internal:3000/playwright-ui-testing-lab.html" \
  --feature "login" --model "qwen2.5-coder:7b" --engine ollama

# Run standalone Playwright tests (auto-starts ui-testing-lab server)
docker run --rm -p 3000:3000 ai-test-orchestrator \
  sh -c "npx http-server ui-testing-lab -p 3000 --silent & npx playwright test --reporter=line"
```

The image is automatically built and pushed to `ghcr.io/crisemy/ai-test-orchestrator` on version tags. See `.github/workflows/` for CI pipeline and registry workflows.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/crisemy/ai-test-orchestrator.git
cd ai-test-orchestrator
```

### 2. Python Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows
. .venv/Scripts/activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Node.js Setup

Install Playwright and its dependencies:

```bash
npm install
npx playwright install --with-deps
```

## Serve the Test App

The project includes a local SPA (`ui-testing-lab/`) that serves as the target for all generated tests. You need to serve it before running the orchestrator:

```bash
# Start the server (port 3000)
npx http-server ui-testing-lab -p 3000 --silent
```

> The server is also auto-started by Playwright's `webServer` config when running `npx playwright test` directly, but the orchestrator pipeline requires it to be running beforehand.

## Usage

### Run the Full Pipeline

The orchestrator will now run the AI agent, fix the code, execute tests, and generate POMs with enhanced terminal output and refactoring capabilities.
Make sure to download the proper LLM in your .venv. For instance: "ollama pull qwen2.5-coder:7b"

```bash
# Make sure ui-testing-lab is served first (see "Serve the Test App" above)
python orchestrator.py --url "http://localhost:3000/playwright-ui-testing-lab.html" --feature "login" --model "qwen2.5-coder:7b" --engine "ollama"

# With human review gate (pauses after AI generation for approval)
python orchestrator.py --url "..." --feature "login" --model "qwen2.5-coder:7b" --engine "ollama" --review

# Multi-feature: generate and test any feature
python orchestrator.py --url "..." --feature "checkout" --model "qwen2.5-coder:7b" --engine "ollama"

# With cloud engine (Anthropic Claude)
python orchestrator.py --url "..." --feature "login" --model "claude-3-haiku-20240307" --engine "cloud"

# With ML analysis (prioritization, flakiness, model routing, risk scoring)
python orchestrator.py --url "..." --feature "login" --model "qwen2.5-coder:7b" --engine "ollama" --ml

# ML analysis standalone
python -c "from ml.prioritization import compute_priorities; print(compute_priorities())"
python -c "from ml.flakiness import detect_flaky_tests; print(detect_flaky_tests())"
python -c "from ml.model_router import select_model; print(select_model('login'))"
python -c "from ml.risk_scorer import compute_risk_score; print(compute_risk_score('login'))"
```

### Rich Terminal Output

The orchestrator uses `rich` for enhanced terminal output, including tables and panels for better readability.

### Pipeline Steps

1. **AI Generation**: Calls `ollama_ai.py` (local) or `cloud_ai.py` (Anthropic) to generate Playwright tests.
2. **Human Review** (optional): Pauses with `--review` flag for approval before proceeding.
3. **Hard Normalization**: Self-healing regex fixes (selectors, URLs, syntax). Counts hallucination fixes for KPI.
4. **TypeScript Validation**: `npx tsc --noEmit` gate ensures generated code compiles before execution.
5. **Playwright Execution**: Runs tests with automatic feedback loop — if tests fail, classifies the failure and re-generates injecting error context.
6. **POM Generation**: Extracts selectors and generates a typed Page Object Model.
7. **ML Analysis** (optional): Post-pipeline prioritization, flakiness detection, model routing, risk scoring.
8. **KPI Report**: Rich table with pass rate, hallucination fixes, execution duration, cost/ROI.

### Audit Trail

Each pipeline execution is logged:

- `logs/pipeline.log` — per-step JSON entries with timestamps (includes timing and cost metrics)
- `reports/execution_log.json` — structured execution history with metadata (execution_id, environment, status, metrics)

## QA Dashboard

Launch the Streamlit dashboard to visualize execution history and KPIs:

```bash
streamlit run dashboard/app.py
```

## Prompt Experiments

Run the pipeline with different model/temperature/prompt variants and compare results:

```bash
# Run a single experiment
python experiments/runner.py --label "high-temp" --temperature 0.7

# Compare all experiments
python experiments/runner.py --compare
```

## Synthetic Test Data

Generate varied credential sets via LLM for more robust testing:

```bash
python test_data_generator.py
# Output: generated-tests/test_data.json (5 entries)
```

## Security (Red Team)

Run the security suite to test prompt injection and scan for unsafe code:

```bash
python red_team/suite.py
# Output: red_team/report.json
```

## Test Rollback

If generation fails persistently, the pipeline automatically restores the previous working version. Backups are stored in `generated-tests/backups/`.

Manual rollback:

```bash
python -c "from orchestrator import restore_test; restore_test('login')"
```

## HTML Report

Playwright generates an HTML report for test results, providing a detailed view of test execution, including passed and failed tests, screenshots, and logs. To view the report, run:

```bash
npx playwright show-report reports/html-report
```

Ensure that the `reports/html-report` directory is accessible after running the tests.

## External Prompt Template

The `ollama_ai.py` script uses a dynamic prompt template stored in an external JSON file. This allows for easy customization and reuse of prompt configurations. The JSON file should be structured as follows:

```json
{
  "PROMPT_TEMPLATE": "Your dynamic prompt here with placeholders."
}
```

Update the file to include your desired prompt logic. The script dynamically loads this template at runtime, ensuring flexibility and modularity.

## Project Structure

```bash
- `orchestrator.py`: Pipeline orchestrator (router, normalizer, executor, cost metrics).
- `ollama_ai.py`: Interface with the local LLM for test generation.
- `cloud_ai.py`: Anthropic Claude cloud engine (--engine cloud).
- `pom_generator.py`: Generates Page Object Models from test files.
- `test_data_generator.py`: Synthetic test data generation via LLM.
- `persistence.py`: Structured persistence via Pydantic contracts (Phase 0).
- `kpi.py`: KPI measurement with Rich display (Phase 0).
- `failure_analysis.py`: Failure classifier (Phase 0).
- `contracts/`: Pydantic data contracts: ContractMetadata, ExecutionRecord, FailureRecord.
- `dashboard/app.py`: Streamlit QA dashboard.
- `experiments/runner.py`: Prompt experiment runner + comparator.
- `red_team/suite.py`: Red Team security testing suite.
- `ml/`: ML analysis modules (prioritization, flakiness, model router, risk scorer).
- `tests/`: Unit tests (pytest, 159+ tests covering all modules).
- `generated-tests/`: AI-generated Playwright test files + test_data.json.
- `pom/`: Generated Page Object Models.
- `logs/pipeline.log`: Per-step audit trail with timing (JSON).
- `reports/execution_log.json`: Structured execution history with cost/ROI metrics.
- `reports/html-report/`: Playwright HTML test reports.
- `Dockerfile`: Containerized runtime (Python + Node.js + Playwright).
- `.dockerignore`: Excludes unnecessary files from Docker builds.
- `.github/workflows/ci.yml`: GitHub Actions CI (pytest, Playwright, experiment archive, POM check).
- `.github/workflows/docker.yml`: GitHub Actions Docker registry push (ghcr.io).
```

## License

This project is licensed under the MIT License.
