# AI Test Orchestrator

[![Playwright](https://img.shields.io/badge/playwright-%232EAD33.svg?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)

An intelligent, self-healing E2E testing pipeline that leverages Local LLMs (via Ollama) to generate, validate, and evolve Playwright test suites.

## Key Features

- **AI-Powered Test Generation**: Automatically generates multi-scenario Playwright tests using `qwen2.5-coder`.
- **Self-Healing Normalization**: A custom "Hard Normalizer" loop that corrects common LLM hallucinations, fixes selectors, and maps generic URLs to real test environments.
- **Automated Execution**: Seamlessly triggers Playwright runners and captures real-time results.
- **Page Object Model (POM) Evolution**: Dynamically extracts selectors from generated tests and refactors them into professional POM structures.
- **Local & Private**: Powered by Ollama, ensuring your testing logic and data stay on your machine.

## Orchestration Workflow

The `orchestrator.py` script manages the entire lifecycle:

1. **AI Generation**: Calls `ollama-ai.py` to prompt the local LLM for test code.
2. **Normalization**: Sanitizes the output, removes markdown, and applies logic-based fixes to provide stable code.
3. **Validation**: Executes the generated tests using Playwright.
4. **POM Generation**: Analyzes the passing tests to create reusable Page Objects in the `pom/` directory.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Ollama**: [Download and Install Ollama](https://ollama.com/)
- **Model**: Pull the required model:

```bash
  ollama pull qwen2.5-coder:7b
```

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

## Usage

### Run the Full Pipeline

The orchestrator will now run the AI agent, fix the code, execute tests, and generate POMs with enhanced terminal output and refactoring capabilities.
Make sure to download the proper LLM in your .venv. For instance: "ollama pull qwen2.5-coder:7b"

```bash
# Updated command:
python orchestrator.py --url "https://the-internet.herokuapp.com/login" --feature "Login Page" --model "qwen2.5-coder:7b" --engine "ollama"
```

### Rich Terminal Output

The orchestrator now uses `rich` for enhanced terminal output, including tables and panels for better readability.

### Refactoring to POM

After validation, the orchestrator automatically refactors tests to use Page Object Models (POMs). The refactored tests are stored in the `pom/` directory.

## HTML Report

Playwright generates an HTML report for test results, providing a detailed view of test execution, including passed and failed tests, screenshots, and logs. To view the report, run:

```bash
npx playwright show-report reports/html-report
```

Ensure that the `reports/html-report` directory is accessible after running the tests.

## External Prompt Template

The `ollama-ai.py` script uses a dynamic prompt template stored in an external JSON file. This allows for easy customization and reuse of prompt configurations. The JSON file should be structured as follows:

```json
{
  "PROMPT_TEMPLATE": "Your dynamic prompt here with placeholders."
}
```

Update the file to include your desired prompt logic. The script dynamically loads this template at runtime, ensuring flexibility and modularity.

## Project Structure

```bash
- `orchestrator.py`: The brain of the project. Manages the execution flow.
- `ollama-ai.py`: Interface with the local LLM for test generation.
- `pom_generator.py`: Generates Page Object Models from test files.
- `generated-tests/`: Directory where the AI-generated code is stored.
- `pom/`: Directory for generated Page Objects.
- `test-results/`: Artifacts from Playwright executions.
```

## License

This project is licensed under the MIT License.
