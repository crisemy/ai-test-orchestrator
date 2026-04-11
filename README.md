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

1.  **AI Generation**: Calls `ollama-ai.py` to prompt the local LLM for test code.
2.  **Normalization**: Sanitizes the output, removes markdown, and applies logic-based fixes to provide stable code.
3.  **Validation**: Executes the generated tests using Playwright.
4.  **POM Generation**: Analyzes the passing tests to create reusable Page Objects in the `pom/` directory.

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
The orchestrator will run the AI agent, fix the code, execute tests, and generate POMs:
```bash
python orchestrator.py
```

### Run Tests Individually
If you just want to run the generated tests:
```bash
npx playwright test
```

## Project Structure

- `orchestrator.py`: The brain of the project. Manages the execution flow.
- `ollama-ai.py`: Interface with the local LLM for test generation.
- `pom_generator.py`: Generates Page Object Models from test files.
- `generated-tests/`: Directory where the AI-generated code is stored.
- `pom/`: Directory for generated Page Objects.
- `test-results/`: Artifacts from Playwright executions.

## License
This project is licensed under the ISC License.
