# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `LICENSE` — MIT license file
- `CONTRIBUTING.md` — Contribution guidelines for open source contributors
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1
- `CHANGELOG.md` — This file
- `pyproject.toml` — Modern Python project metadata and tool configuration
- `demo.ps1` — One-command Windows demo script

### Changed

- `package.json` license field corrected from `ISC` to `MIT` to match the project license
- `README.md` — Added Quick Demo section, contribution/badge links
- `CONTEXT.md` — Updated project tree with new files
- `AGENTS.md` — Added LICENSE/CONTRIBUTING.md to pre-flight read list

## [v1.0.0] — 2026-06-10

### Added

- Core pipeline: AI Generation → Normalization → Playwright Execution → POM Generation
- Dual engine: Ollama (local) and Anthropic Claude (cloud) via `--engine` flag
- Multi-feature support via `--feature` parameter
- Self-healing Hard Normalizer with regex-based hallucination fixes
- Feedback loop: automatic retry with error context on Playwright failure
- Human-in-the-Loop via `--review` flag
- Page Object Model (POM) generation with camelCase selectors
- Data contracts (Pydantic) with canonical metadata
- Persistence pipeline (`persistence.py`)
- KPI measurement with Rich terminal display
- Failure analysis with classification and confidence scores
- TypeScript validation gate (`npx tsc --noEmit`)
- QA Dashboard (Streamlit)
- Prompt experiment system (`experiments/runner.py`)
- Quality economics — cost estimation, ROI per run
- Synthetic test data generation
- Red Team security suite (prompt injection, unsafe code scan)
- Input sanitization, test rollback, rate limiting, cost thresholds
- ML modules: test prioritization, flakiness detection, model routing, risk scoring
- Docker multi-stage build (Python 3.12 + Node.js 22 + Playwright)
- GitHub Actions CI (pytest, Playwright, experiment archive, POM validation)
- GitHub Actions Docker registry push (ghcr.io)
- 200+ unit tests covering all modules
- `ui-testing-lab` — local SPA with 36 interaction scenarios

[v1.0.0]: https://github.com/crisemy/ai-test-orchestrator/releases/tag/v1.0.0
