#!/usr/bin/env bash
# =============================================================================
#  AI Test Orchestrator — Interactive Menu
# =============================================================================
#  Usage:  bash menu.sh
#  Deps:   Requires Python venv activated, Node.js installed.
# =============================================================================
set -euo pipefail

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
FEATURE="${FEATURE:-login}"
MODEL="${MODEL:-qwen2.5-coder:7b}"
ENGINE="${ENGINE:-ollama}"
URL="${URL:-http://localhost:3000/playwright-ui-testing-lab.html}"

# ── Helpers ──────────────────────────────────────────────────────────────────
check_venv() {
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        echo -e "${YELLOW}⚠  No Python venv detected. Activate one:${NC}"
        echo "   source .venv/bin/activate"
        echo "   (5s pause…)"
        sleep 5
    fi
}

check_server() {
    if ! curl -s -o /dev/null --connect-timeout 2 "$URL"; then
        echo -e "${RED}✗  Test app not reachable at $URL${NC}"
        echo -e "   Start it with menu option ${BOLD}6${NC} first."
        echo ""
        read -rp "   Continue anyway? (y/N) " yn
        if [[ ! "$yn" =~ ^[Yy]$ ]]; then
            echo "Aborted."
            return 1
        fi
    fi
}

pause() {
    echo ""
    read -rp "Press Enter to continue…" _
}

# ── Menu ─────────────────────────────────────────────────────────────────────
while true; do
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   ${BOLD}AI Test Orchestrator — Main Menu${NC}${CYAN}            ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}1${NC})  Run unit tests (pytest)                ${GREEN}201+ expected${NC}"
    echo -e "  ${BOLD}2${NC})  Run Streamlit dashboard"
    echo -e "  ${BOLD}3${NC})  Run full pipeline                       ${YELLOW}needs server${NC}"
    echo -e "  ${BOLD}4${NC})  Run Playwright smoke tests              ${YELLOW}needs server${NC}"
    echo -e "  ${BOLD}5${NC})  Generate POM from existing test         ${YELLOW}needs test${NC}"
    echo -e "  ${BOLD}6${NC})  Start test app server (background)"
    echo -e "  ${BOLD}7${NC})  Validate TypeScript"
    echo -e "  ${BOLD}8${NC})  Run ML analysis"
    echo -e "  ${BOLD}9${NC})  View pipeline log"
    echo -e "  ${BOLD}i${NC})  Install / verify dependencies"
    echo -e "  ${BOLD}r${NC})  Reset: delete generated tests + POMs"
    echo -e "  ${BOLD}q${NC})  Quit"
    echo ""
    read -rp "  Choose an option: " choice
    echo ""

    case "$choice" in
        1)  # ── pytest ──────────────────────────────────────────────────────
            check_venv
            python -m pytest tests/ -q --tb=short
            pause
            ;;

        2)  # ── Streamlit ───────────────────────────────────────────────────
            check_venv
            if ! python -c "import streamlit" 2>/dev/null; then
                echo -e "${RED}streamlit not installed. Run option 'i' first.${NC}"
            else
                echo -e "${GREEN}Starting Streamlit…${NC}"
                streamlit run dashboard/app.py
            fi
            pause
            ;;

        3)  # ── Full pipeline ───────────────────────────────────────────────
            check_venv
            check_server || { pause; continue; }

            # Prompt for overrides
            read -rp "  Feature [${FEATURE}]: " inp
            FEATURE="${inp:-$FEATURE}"
            read -rp "  Model [${MODEL}]: " inp
            MODEL="${inp:-$MODEL}"
            read -rp "  Engine (ollama/cloud) [${ENGINE}]: " inp
            ENGINE="${inp:-$ENGINE}"

            REVIEW=""
            read -rp "  Enable human review? (y/N): " yn
            [[ "$yn" =~ ^[Yy]$ ]] && REVIEW="--review"

            ML=""
            read -rp "  Enable ML analysis? (y/N): " yn
            [[ "$yn" =~ ^[Yy]$ ]] && ML="--ml"

            echo ""
            echo -e "${GREEN}→  python orchestrator.py --url \"$URL\" --feature \"$FEATURE\" --model \"$MODEL\" --engine \"$ENGINE\" $REVIEW $ML${NC}"
            echo ""

            # ── Ordered steps ───────────────────────────────────────────────
            # Step 1: AI Generation
            python orchestrator.py --url "$URL" --feature "$FEATURE" \
                --model "$MODEL" --engine "$ENGINE" $REVIEW $ML

            EXIT_CODE=$?
            if [ "$EXIT_CODE" -ne 0 ]; then
                echo -e "${RED}✗  Pipeline failed (exit $EXIT_CODE).${NC}"
                pause; continue
            fi

            echo -e "${GREEN}✓  Pipeline completed successfully.${NC}"
            pause
            ;;

        4)  # ── Playwright smoke tests ─────────────────────────────────────
            check_server || { pause; continue; }
            echo -e "${GREEN}Running npx playwright test ci/smoke.spec.ts --reporter=line${NC}"
            echo ""
            npx playwright test ci/smoke.spec.ts --reporter=line
            pause
            ;;

        5)  # ── POM generation ──────────────────────────────────────────────
            read -rp "  Feature name [${FEATURE}]: " inp
            FEATURE="${inp:-$FEATURE}"

            TEST_FILE="generated-tests/${FEATURE}.spec.ts"
            if [ ! -f "$TEST_FILE" ]; then
                echo -e "${YELLOW}⚠  No test file found at $TEST_FILE${NC}"
                echo "   Run the full pipeline (option 3) first to generate one."
                pause; continue
            fi

            python -c "
from pom_generator import run_pom_generation
run_pom_generation('$FEATURE')
"
            echo ""
            echo -e "${GREEN}✓  POM generated at pom/${FEATURE}_page.ts${NC}"
            pause
            ;;

        6)  # ── Start test app server ──────────────────────────────────────
            SERVER_PID=""
            if [ -f "ui-testing-lab/server.pid" ]; then
                SERVER_PID=$(cat ui-testing-lab/server.pid 2>/dev/null || true)
            fi
            if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
                echo -e "${YELLOW}Server already running (PID $SERVER_PID)${NC}"
            else
                npx http-server ui-testing-lab -p 3000 --silent &
                SERVER_PID=$!
                echo "$SERVER_PID" > ui-testing-lab/server.pid
                disown "$SERVER_PID" 2>/dev/null || true
                echo -e "${GREEN}✓  Server started (PID $SERVER_PID) on http://localhost:3000${NC}"
                echo "   Stop it with: kill $SERVER_PID"
            fi
            pause
            ;;

        7)  # ── TypeScript validation ──────────────────────────────────────
            echo -e "${GREEN}npx tsc --noEmit --project tsconfig.json${NC}"
            echo ""
            npx tsc --noEmit --project tsconfig.json && \
                echo -e "${GREEN}✓  TypeScript validation passed${NC}"
            pause
            ;;

        8)  # ── ML analysis sub-menu ───────────────────────────────────────
            echo -e "${CYAN}── ML Analysis ──${NC}"
            echo -e "  ${BOLD}a${NC})  Run all ML analyses"
            echo -e "  ${BOLD}1${NC})  Prioritization"
            echo -e "  ${BOLD}2${NC})  Flakiness detection"
            echo -e "  ${BOLD}3${NC})  Model router"
            echo -e "  ${BOLD}4${NC})  Risk scorer"
            echo -e "  ${BOLD}b${NC})  Back"
            read -rp "  Choose: " ml_choice
            echo ""

            case "$ml_choice" in
                a)
                    python -c "from ml.prioritization import compute_priorities; print('Priorities:', compute_priorities())"
                    python -c "from ml.flakiness import detect_flaky_tests; print('Flaky:', detect_flaky_tests())"
                    python -c "from ml.model_router import select_model; print('Model:', select_model('$FEATURE'))"
                    python -c "from ml.risk_scorer import compute_risk_score; print('Risk:', compute_risk_score('$FEATURE'))"
                    ;;
                1) python -c "from ml.prioritization import compute_priorities; print(compute_priorities())" ;;
                2) python -c "from ml.flakiness import detect_flaky_tests; print(detect_flaky_tests())" ;;
                3) python -c "from ml.model_router import select_model; print(select_model('$FEATURE'))" ;;
                4) python -c "from ml.risk_scorer import compute_risk_score; print(compute_risk_score('$FEATURE'))" ;;
                b) continue ;;
                *) echo -e "${RED}Invalid choice${NC}" ;;
            esac
            pause
            ;;

        9)  # ── View pipeline log ──────────────────────────────────────────
            LOG="logs/pipeline.log"
            if [ -f "$LOG" ]; then
                echo -e "${GREEN}Tailing $LOG (Ctrl+C to stop)${NC}"
                tail -f "$LOG"
            else
                echo -e "${YELLOW}No log file found at $LOG${NC}"
                echo "Run the pipeline (option 3) first to generate logs."
                pause
            fi
            ;;

        i|I)  # ── Install dependencies ─────────────────────────────────────
            check_venv

            echo -e "${CYAN}── Python dependencies ──${NC}"
            pip install -r requirements.txt

            echo ""
            echo -e "${CYAN}── Node.js dependencies ──${NC}"
            npm install

            echo ""
            echo -e "${CYAN}── Playwright browsers ──${NC}"
            npx playwright install --with-deps

            echo ""
            echo -e "${GREEN}✓  Dependencies installed${NC}"
            pause
            ;;

        r|R)  # ── Reset artifacts ──────────────────────────────────────────
            echo -e "${RED}This will delete:${NC}"
            echo "  • generated-tests/"
            echo "  • pom/"
            echo "  • logs/"
            echo "  • reports/"
            read -rp "Are you sure? (y/N): " yn
            if [[ "$yn" =~ ^[Yy]$ ]]; then
                rm -rf generated-tests pom logs reports
                mkdir -p generated-tests pom logs reports
                echo -e "${GREEN}✓  Reset complete${NC}"
            else
                echo "Skipped."
            fi
            pause
            ;;

        q|Q)  echo "Goodbye."; exit 0 ;;

        *)  echo -e "${RED}Invalid option${NC}" ; pause ;;
    esac
done
