# Contributing to AI Test Orchestrator

First off, thanks for taking the time to contribute!

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to uphold its terms.

## How to Contribute

### 1. Understand the Architecture

Before making changes, read:

- **[CONTEXT.md](CONTEXT.md)** — Project architecture, data flow, module responsibilities
- **[AGENTS.md](AGENTS.md)** — AI agent behavior rules and the CORE skill matrix
- **[IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md)** — Current status and roadmap

### 2. Set Up the Development Environment

Follow the [Getting Started](README.md#getting-started) instructions in the README.

### 3. Run the Tests

```bash
python -m pytest tests/ -q
# Expected: 201+ passed
```

Verify the full pipeline works:

```bash
python -c "import ast; [ast.parse(open(f).read()) for f in ['config.py','orchestrator.py','ollama_ai.py','cloud_ai.py','pom_generator.py','persistence.py','kpi.py','failure_analysis.py']]; print('Syntax OK')"
python -c "import config; import orchestrator; import ollama_ai; import cloud_ai; import pom_generator; import persistence; import kpi; import failure_analysis; import contracts; print('Imports OK')"
```

### 4. Understand the Pipeline

The linear pipeline must remain functional after every change:

```
User Input → AI Generation → Normalization (self-healing) → Playwright Execution → POM Generation
```

### 5. Submit a Pull Request

1. Fork the repo and create your branch from `main`
2. Write clear, tested code — follow the patterns in existing modules
3. Run the full verification suite (see [AGENTS.md](AGENTS.md#22-verify-end-to-end))
4. Ensure Python syntax is valid across all modified files
5. Ensure all existing modules import without errors
6. Open a PR describing what you changed and why

### Code Style

- Follow the existing patterns in the codebase
- Use meaningful names for variables and functions
- Add type hints for Python functions
- Write tests for new functionality

### Questions?

Open a [GitHub Issue](https://github.com/crisemy/ai-test-orchestrator/issues) for discussion.
