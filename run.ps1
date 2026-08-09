# Run State-Adaptive Panchang API (Windows PowerShell)
# Usage: .\run.ps1
# Optional: .\run.ps1 -SkipInstall

param(
    [switch]$SkipInstall,
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
$EnvFile = Join-Path $Backend ".env"
$EnvExample = Join-Path $Backend ".env.example"

Set-Location $Backend

if (-not (Test-Path $EnvFile)) {
    if (-not (Test-Path $EnvExample)) {
        Write-Error "Missing .env.example at $EnvExample"
    }
    Copy-Item $EnvExample $EnvFile
    Write-Host "Created backend\.env from .env.example"
    Write-Host ""
    Write-Host "Optional env vars (edit backend\.env):"
    Write-Host "  GEMINI_API_KEY     - Gemini Rashifal (empty = deterministic fallback)"
    Write-Host "  GEMINI_MODEL       - default gemini-2.5-flash"
    Write-Host "  REDIS_ENABLED      - true to use Redis cache (default false)"
    Write-Host "  REDIS_URL          - redis://localhost:6379/0"
    Write-Host "  POSTGRES_ENABLED   - true for Postgres audit (default false)"
    Write-Host "  DATABASE_URL       - postgresql+psycopg://postgres:postgres@localhost:5432/panchang"
    Write-Host ""
    Write-Host "Defaults work with JSON file storage only (no Redis/Postgres/Gemini required)."
    Write-Host ""
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating virtualenv..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Failed to create venv. Is Python 3.11+ on PATH?" }
    $SkipInstall = $false
}

if (-not $SkipInstall) {
    Write-Host "Installing dependencies..."
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
}

$Frontend = Join-Path $Root "frontend"
$DistIndex = Join-Path $Frontend "dist\index.html"
if (-not (Test-Path $DistIndex)) {
    Write-Host "Building React frontend..."
    Push-Location $Frontend
    try {
        if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
            npm install
            if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
        }
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "frontend build failed" }
    } finally {
        Pop-Location
    }
}

Write-Host "Starting API at http://localhost:$Port (docs: http://localhost:$Port/docs)"
& $VenvPython -m uvicorn app.main:app --reload --host $HostAddress --port $Port
