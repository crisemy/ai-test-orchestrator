<#
.SYNOPSIS
  One-command demo of the AI Test Orchestrator pipeline.
.DESCRIPTION
  Checks prerequisites, sets up the environment, serves the test app,
  runs the orchestrator pipeline, and shows the dashboard URL.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\demo.ps1
#>

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "AI Test Orchestrator — Demo"

$RED   = "`e[31m"
$GREEN = "`e[32m"
$YELLOW = "`e[33m"
$CYAN  = "`e[36m"
$RESET = "`e[0m"

function Write-Status($icon, $text) { Write-Host "${icon} ${text}" }
function Write-Ok($text)    { Write-Host "${GREEN}✓ ${text}${RESET}" }
function Write-Warn($text)  { Write-Host "${YELLOW}⚠ ${text}${RESET}" }
function Write-Err($text)   { Write-Host "${RED}✗ ${text}${RESET}" ; exit 1 }

# ─── Prerequisites ────────────────────────────────────────────────
Write-Host "${CYAN}══════════════════════════════════════════════${RESET}" -NoNewline
Write-Host "${CYAN}  AI Test Orchestrator — Demo${RESET}"
Write-Host "${CYAN}══════════════════════════════════════════════${RESET}`n"

Write-Status "🔍" "Checking prerequisites..."

$pyVer = python --version 2>$null
if (-not $pyVer) { Write-Err "Python not found. Install Python 3.10+ and try again." }
Write-Ok "Python: $pyVer"

$nodeVer = node --version 2>$null
if (-not $nodeVer) { Write-Err "Node.js not found. Install Node.js 18+ and try again." }
Write-Ok "Node.js: $nodeVer"

$ollamaRunning = curl -s http://localhost:11434/api/tags 2>$null
if (-not $ollamaRunning) { Write-Warn "Ollama not detected on port 11434. Generation will fail." }
else { Write-Ok "Ollama is running" }

# Check for the model
if ($ollamaRunning) {
    $models = (curl -s http://localhost:11434/api/tags | ConvertFrom-Json).models
    $hasModel = $models | Where-Object { $_.name -like "qwen2.5-coder*" }
    if (-not $hasModel) {
        Write-Warn "qwen2.5-coder model not found. Run: ollama pull qwen2.5-coder:7b"
    } else {
        Write-Ok "Model qwen2.5-coder available"
    }
}

# ─── Python virtual environment ──────────────────────────────────
Write-Status "🔧" "Setting up Python virtual environment..."
if (-not (Test-Path -LiteralPath ".venv")) {
    python -m venv .venv
    Write-Ok "Created .venv"
} else {
    Write-Ok ".venv already exists"
}

$pip = if ($IsWindows -or $env:OS) { ".\.venv\Scripts\pip" } else { ".venv/bin/pip" }
& $pip install -q -r requirements.txt
Write-Ok "Python dependencies installed"

# ─── Node.js dependencies ────────────────────────────────────────
Write-Status "📦" "Installing Node.js dependencies..."
if (-not (Test-Path -LiteralPath "node_modules")) {
    npm install --silent 2>$null
    Write-Ok "Node.js dependencies installed"
} else {
    Write-Ok "node_modules already exists"
}

# ─── Start test app server ──────────────────────────────────────
Write-Status "🌐" "Starting ui-testing-lab on port 3000..."
$serverProcess = Start-Process -PassThru -NoNewWindow powershell -ArgumentList @(
    "-NoProfile", "-Command",
    "npx http-server ui-testing-lab -p 3000 --silent"
)
Start-Sleep -Seconds 2
Write-Ok "Test app running at http://localhost:3000/playwright-ui-testing-lab.html"

# ─── Run the orchestrator ────────────────────────────────────────
Write-Status "🚀" "Running the orchestrator pipeline..."
Write-Host ""

$python = if ($IsWindows -or $env:OS) { ".\.venv\Scripts\python" } else { ".venv/bin/python" }
& $python orchestrator.py `
    --url "http://localhost:3000/playwright-ui-testing-lab.html" `
    --feature "login" `
    --model "qwen2.5-coder:7b" `
    --engine "ollama"

$exitCode = $LASTEXITCODE
Write-Host ""

if ($exitCode -eq 0) {
    Write-Ok "Pipeline completed successfully"
} else {
    Write-Warn "Pipeline exited with code $exitCode (may be expected if no Ollama model)"
}

# ─── Done ─────────────────────────────────────────────────────────
Write-Host "${CYAN}══════════════════════════════════════════════${RESET}"
Write-Host "${GREEN}  Demo complete!${RESET}"
Write-Host "${CYAN}══════════════════════════════════════════════${RESET}`n"
Write-Host "  📊 QA Dashboard:   streamlit run dashboard/app.py"
Write-Host "  📝 Execution log:  Get-Content reports/execution_log.json"
Write-Host "  📋 Pipeline audit: Get-Content logs/pipeline.log"
Write-Host "  🗑  Cleanup:       Stop-Process -Id $($serverProcess.Id)`n"

# Wait for user to stop the server
Write-Host "Press Enter to stop the server and exit."
Read-Host | Out-Null
Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
Write-Ok "Server stopped. Goodbye!"
