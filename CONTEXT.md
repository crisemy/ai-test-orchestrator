# AI Test Orchestrator — Context

## Descripción General

**AI Test Orchestrator** es un pipeline de testing E2E inteligente y auto-curativo que usa LLMs locales (Ollama) para generar, validar, normalizar, ejecutar y evolucionar tests de Playwright de forma automática. Partiendo de una URL y una descripción de funcionalidad, genera suites de tests, las ejecuta y refactoriza en Page Object Models (POMs).

Creado por [Cristian Nadj](https://github.com/crisemy) — https://github.com/crisemy/ai-test-orchestrator

---

## Tech Stack

| Capa | Tecnología |
|---|---|
| Orquestación | Python 3.12 |
| Testing (Node.js) | Playwright + TypeScript (`@playwright/test` ^1.59.1) |
| LLM Local | Ollama (SDK Python 0.4.7) + `qwen2.5-coder:7b` |
| LLM Cloud (exp.) | Anthropic Claude (SDK `anthropic`) |
| CLI/UI | Rich 13.7.1 |
| HTTP | Requests 2.32.3 |
| Validación | Pydantic 2.9.2 |
| Config | python-dotenv 1.0.1 |

---

## Estructura del Proyecto

```
ai-test-orchestrator/
├── .env                          # ANTHROPIC_API_KEY (sensible, gitignored)
├── .gitignore
├── .vscode/
│   ├── launch.json               # Debug config para "Run Ollama Script"
│   └── settings.json
├── README.md
├── CONTEXT.md                    # Este archivo
├── package.json                  # DevDependency: @playwright/test
├── package-lock.json
├── playwright.config.js          # HTML reporter + webServer ui-testing-lab
├── ui-testing-lab/               # App local de prueba (SPA con 36 scenarios)
├── prompt_template.json          # Prompt externalizado para el LLM
├── requirements.txt              # requests, pydantic, rich, python-dotenv, ollama
│
├── orchestrator.py               # Entry point principal (orquestador)
├── ollama-ai.py                  # Interfaz con Ollama para generación de tests
├── pom_generator.py              # Generador de Page Object Models
├── test-cloud-ai.py              # Prototipo experimental con Anthropic Claude
│
├── generated-tests/
│   └── login.spec.ts             # Test generado por IA (TypeScript)
├── pom/
│   └── login_page.ts             # POM generado (TypeScript)
└── reports/                      # Reportes HTML (gitignored)
```

---

## Arquitectura y Flujo

### Pipeline (orquestador.py)

1. **Parseo de argumentos** — `--url`, `--feature`, `--model`, `--engine`
2. **Generación AI** — Llama a `ollama-ai.py` vía subprocess
3. **Normalización (Self-Healing)** — Hard Normalizer vía regex: corrige alucinaciones del LLM (markdown, URLs inválidas, selectores incorrectos, sintaxis rota)
4. **Ejecución Playwright** — `npx playwright test` vía subprocess
5. **Generación de POM** — Extrae selectores vía regex y genera clase `LoginPage`

### Patrones Clave

- **Subprocess Orchestration**: Python orquesta procesos Node.js (Playwright, generación)
- **Pipeline lineal**: cada etapa escribe/lee archivos en disco (`generated-tests/login.spec.ts`)
- **Self-Healing**: Normalizador determinístico basado en regex + retry loop en `ollama-ai.py` (3 intentos + fallback)
- **POM Generation**: Extracción de selectores vía regex (no AST)
- **Dual Engine**: Soporta `--engine ollama` (local, implementado) y `--engine cloud` (stub, no implementado)

---

## Módulos Principales

### `orchestrator.py` (181 líneas)
Entry point. Funciones clave:
- `parse_arguments()` — CLI args
- `run_ollama_agent(url, model)` — spawn `ollama-ai.py`
- `normalize_code(code)` — Hard Normalizer (regex fixes)
- `validate_and_fix()` — lee, normaliza y escribe el test
- `run_playwright()` — ejecuta tests
- `run_pom_agent()` — llama a `pom_generator`
- `main()` — orquesta el flujo completo

### `ollama-ai.py` (195 líneas)
Interfaz con el LLM local:
- `generate_tests(url)` — hasta 3 intentos, temperatura 0.2, fallback hardcoded
- `extract_code(text)` — extrae TypeScript/JS de bloques markdown
- `is_valid_playwright(code)` — validación de estructura
- `save_file(code)` — guarda en `generated-tests/login.spec.ts`
- Carga prompt desde `prompt_template.json`

### `pom_generator.py` (99 líneas)
Generación de POM:
- `extract_selectors(code)` — regex sobre `page.fill()`, `page.click()`, `page.locator()`, `locator()`
- `generate_pom(selectors)` — genera clase TypeScript con `export class`
- `run_pom_generation()` — entry point

### `test-cloud-ai.py` (19 líneas)
Prototipo experimental con Claude (incompleto).

### `playwright.config.js` (6 líneas)
Configura reporter HTML en `reports/html-report`, `open: never`.

### `prompt_template.json` (3 líneas)
Template de prompt externalizado con instrucciones estrictas de generación.

---

## Comandos Útiles

```bash
# Ejecutar pipeline completo (usa ui-testing-lab local por defecto)
python orchestrator.py --url "http://localhost:3000/playwright-ui-testing-lab.html" --feature "Login Page"

# Especificar modelo y engine
python orchestrator.py --url "..." --feature "..." --model "qwen2.5-coder:7b" --engine ollama

# Ejecutar solo generación de tests
python ollama-ai.py

# Ejecutar tests con servidor automático (webServer en playwright.config.js)
npx playwright test

# Generar POM standalone
python -c "import pom_generator; pom_generator.run_pom_generation()"
```

---

## Estado del Proyecto

- [x] Generación de tests vía Ollama
- [x] Hard Normalizer (self-healing)
- [x] Ejecución con Playwright
- [x] Generación de POM básica
- [ ] Refactor test → POM (placeholder)
- [ ] Cloud engine con Anthropic Claude (stub)
- [ ] Soporte multi-test / múltiples features
- [ ] Tests unitarios del orquestador
- [ ] CI/CD
