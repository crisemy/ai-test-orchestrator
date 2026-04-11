# Implementation Plan - Iteration 2: Dynamic Integration & Intelligence

This iteration focuses on evolving the **AI Test Orchestrator** from a hardcoded prototype into a professional, flexible testing platform. We will introduce dynamic inputs, improved terminal UX, and deeper integration with Page Object Models.

## User Review Required

> [!IMPORTANT]
> **Cloud AI Costs**: Adding support for Anthropic/OpenAI will require the user to have their own API keys and credits. The project will default to Ollama (Local) to avoid unexpected costs.
> **Destructive Refactoring**: The "Auto-POM Injection" feature will overwrite `generated-tests/login.spec.js`. While this is intended, users should be aware that manual changes to that file will be lost if run again.

## Proposed Changes

---

### Core Orchestrator Evolution

#### [MODIFY] [orchestrator.py](file:///c:/Crisarch/Programming/ai-test-orchestrator/orchestrator.py)
- **CLI Arguments**: Implement `argparse` to support:
  - `--url`: Target URL to test.
  - `--feature`: Description of the feature to test (e.g., "Shopping Cart", "Contact Form").
  - `--model`: Specific Ollama or Cloud model to use.
  - `--engine`: Choose between `ollama` and `cloud`.
- **Rich Integration**: Replace standard `print` statements with `rich` Console, Panels, and Tables for a premium terminal experience.
- **Workflow Expansion**: Add a new step `refactor_test_to_pom()` after validation.

---

### AI Engine Enhancements

#### [MODIFY] [ollama-ai.py](file:///c:/Crisarch/Programming/ai-test-orchestrator/ollama-ai.py)
- **Dynamic Prompts**: Replace the hardcoded login prompt with a template that injects the user-provided URL and Feature Description.
- **Multi-Model Logic**: Allow the model name to be passed as an argument.

#### [NEW] [cloud_ai.py](file:///c:/Crisarch/Programming/ai-test-orchestrator/cloud_ai.py)
- Create a unified interface for Cloud LLMs (starting with Anthropic/OpenAI) using `.env` for credentials.

---

### POM & Refactoring Intelligence

#### [MODIFY] [pom_generator.py](file:///c:/Crisarch/Programming/ai-test-orchestrator/pom_generator.py)
- **Smart Extraction**: Enhance selector extraction to handle more complex scenarios beyond simple login fields.
- **Refactoring Logic**: Add a new function `inject_pom_into_test(test_path, pom_path)` that:
  - Adds `const { LoginPage } = require('../pom/login_page');` to the test.
  - Replaces direct `page.fill` and `page.click` calls with `loginPage.login(...)` or appropriate POM methods.

---

### UI & Documentation

#### [MODIFY] [README.md](file:///c:/Crisarch/Programming/ai-test-orchestrator/README.md)
- Update documentation to reflect new CLI usage and advanced features.

## Open Questions

- **POM Method Naming**: Should we use AI to name POM methods dynamically based on the feature, or keep it deterministic?
- **Multiple Pages**: Should we support generating multiple POMs for a single orchestration run if the test traverses multiple pages?

## Verification Plan

### Automated Tests
- Run `python orchestrator.py --url https://the-internet.herokuapp.com/login --feature "Authentication"` and verify:
  - Test is generated correctly.
  - Test is refactored to use `LoginPage`.
  - Final execution passes.

### Manual Verification
- Test with an invalid URL to ensure the "Self-Healing/Normalization" logic or error handling catches it gracefully.
- Verify `rich` output looks professional in different terminal sizes.
