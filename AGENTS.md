# AI Agent Instructions — `ai-test-orchestrator`

This file defines the mandatory behavior, verification protocol, and operational constraints for any AI agent modifying this project. It derives from the `ai-qa-core-framework` CORE Agent architecture and its 13 skills.

---

## 1. Mandatory Pre-Flight

Before making any code change, the agent MUST:

1. **Read `CONTEXT.md`** — Understand project architecture, data flow, and module responsibilities.
2. **Read files to be modified** — Full read, not just grep snippets.
3. **Identify affected skills** — Map the change to the relevant CORE skill(s) and verify which other modules depend on it.
4. **Check the pipeline integrity** — Ensure the proposed change does not break any stage of the linear pipeline (Generation → Normalization → Execution → POM).

---

## 2. Change Protocol

### 2.1 No Breaking the Core

The linear pipeline MUST remain functional after every change:

```bash
User Input → AI Generation → Normalization (self-healing) → Playwright Execution → POM Generation
```

Any modification to a downstream stage (e.g. normalizer, POM generator) requires verifying ALL upstream stages still produce valid output for it.

### 2.2 Verify End-to-End

After any change, the agent MUST run the full verification suite:

| Step | Command | Expected Result |
| --- | --- | --- |
| Python syntax | `python -c "import ast; [ast.parse(open(f).read()) for f in ['config.py','orchestrator.py','ollama_ai.py','cloud_ai.py','pom_generator.py','persistence.py','kpi.py','failure_analysis.py']]; print('OK')"` | No syntax errors |
| Module imports | `python -c "import config; import orchestrator; import ollama_ai; import cloud_ai; import pom_generator; import persistence; import kpi; import failure_analysis; import contracts; print('OK')"` | No ImportError |
| AI Generation | `python ollama_ai.py <url> <model>` | Test saved to `generated-tests/login.spec.ts` |
| Playwright execution | `npx playwright test ci/smoke.spec.ts --reporter=line` | All tests pass |
| POM generation | `python -c "import pom_generator; pom_generator.run_pom_generation('login')"` | Valid POM at `pom/login_page.ts` |
| POM TS validity | `npx tsc --noEmit --project tsconfig.json` | No compilation errors |
| Full test suite | `python -m pytest tests/ -q` | 201+ tests pass |

### 2.3 Normalizer Safety

The Hard Normalizer (`normalize_code` in `orchestrator.py`) uses regex-based replacements. Every regex change MUST be tested against:

- A generated test that the LLM produces correctly (ensure no false positives)
- A test with known LLM hallucinations (ensure false negatives still get fixed)
- Edge cases: markdown fences, broken async syntax, invalid selectors

### 2.4 POM Generator Safety

The POM generator (`pom_generator.py`) must always produce valid TypeScript identifiers. After changes:

- Run `clean_selector_name` against all known selector patterns (`#id`, `.class`, `text=...`, `[attr=val]`)
- Verify the `login()` method correctly detects username, password, and submit button locators

---

## 3. Skill Application Matrix

Every change maps to one or more CORE skills. The agent MUST apply the corresponding constraints:

| CORE Skill | When Triggered | Constraints |
|---|---|---|
| **AI System Design** | Any architectural change | Single-agent pattern; no multi-agent overhead; shared context via files |
| **Data Contracts** | Adding new data structures | Define typed schemas (Pydantic); canonical metadata (execution_id, timestamp, env) |
| **KPI Governance** | Adding metrics/reporting | Define success rate, pass rate, hallucination rate, execution duration |
| **Failure Analysis** | Changing error handling | Classify failures as test_issue / environment_issue / product_bug / unknown |
| **Experimentation** | Modifying prompts or LLM config | Document variants tested; compare KPIs; use `experiments/` directory |
| **Quality Economics** | Adding resource-intensive ops | Measure cost (tokens, CPU time, execution time); log to `reports/` |
| **Red Team** | Accepting user input → LLM prompt | Sanitize `--url`, `--feature`; prevent prompt injection |
| **Human Override** | Adding automation gates | Support `--review` flag; pause before execution for approval |
| **Rollback** | Changing generation/execution logic | Previous working version must be recoverable (git or file backup) |

---

## 4. Anti-Patterns to Avoid

From `ai-qa-core-framework/03_personal_tooling/rules/anti_patterns.md`:

| Anti-Pattern | Why |
|---|---|
| **Blind trust in LLM output** | Always validate generated code structurally (`is_valid_playwright`) and via normalizer |
| **Ignoring cost** | Every LLM call has token cost; log and measure |
| **Full regression by default** | Not applicable to this project (targeted test generation); do not run full suites unless changed |
| **Lack of observability** | After changes, print KPI-relevant output (generation success, test pass rate) |
| **Hardcoded assumptions** | Never hardcode `login` feature name; support `--feature` parameterization |

---

## 5. Pre-Commit Verification Checklist

Before considering a change complete, the agent MUST confirm:

- [ ] Python syntax valid in all modified files (including `config.py`)
- [ ] All existing modules import without errors (including `config`)
- [ ] AI generation produces valid test file
- [ ] Normalizer preserves correct assertions (`.alert-success` / `.alert-error`)
- [ ] All Playwright tests pass (`ci/smoke.spec.ts` + any generated)
- [ ] POM generator produces valid TypeScript identifiers
- [ ] No hardcoded feature names (use parameterization)
- [ ] Pipeline output logged / observable

---

## 6. CORE Agent Architecture (Applied)

This project follows the CORE Agent pattern implicitly:

| CORE Component | Implementation |
|---|---|
| **Router** | `orchestrator.py` — decides flow based on `--engine` and pipeline stage |
| **Shared Context** | Files on disk (`generated-tests/`, `pom/`, `reports/`) |
| **Skill Registry** | Independent Python modules: `ollama_ai.py`, `pom_generator.py` |
| **Skills** | AI Generation, Hard Normalizer, Playwright Execution, POM Generation |

Any refactoring MUST maintain or formalize this pattern — never introduce ad-hoc multi-agent orchestration or out-of-band state.
