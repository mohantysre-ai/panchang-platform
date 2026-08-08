#!/usr/bin/env bash
# Run State-Adaptive Panchang API (Linux/macOS)
# Usage: ./run.sh
# Optional: ./run.sh --skip-install

set -euo pipefail

SKIP_INSTALL=0
HOST_ADDRESS="0.0.0.0"
PORT=8000

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-install) SKIP_INSTALL=1; shift ;;
    --host) HOST_ADDRESS="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
VENV_PYTHON="$BACKEND/.venv/bin/python"
ENV_FILE="$BACKEND/.env"
ENV_EXAMPLE="$BACKEND/.env.example"

cd "$BACKEND"

if [[ ! -f "$ENV_FILE" ]]; then
  if [[ ! -f "$ENV_EXAMPLE" ]]; then
    echo "Missing .env.example at $ENV_EXAMPLE" >&2
    exit 1
  fi
  cp "$ENV_EXAMPLE" "$ENV_FILE"
  echo "Created backend/.env from .env.example"
  echo ""
  echo "Optional env vars (edit backend/.env):"
  echo "  GEMINI_API_KEY     - Gemini Rashifal (empty = deterministic fallback)"
  echo "  GEMINI_MODEL       - default gemini-2.5-flash"
  echo "  REDIS_ENABLED      - true to use Redis cache (default false)"
  echo "  REDIS_URL          - redis://localhost:6379/0"
  echo "  POSTGRES_ENABLED   - true for Postgres audit (default false)"
  echo "  DATABASE_URL       - postgresql+psycopg://postgres:postgres@localhost:5432/panchang"
  echo ""
  echo "Defaults work with JSON file storage only (no Redis/Postgres/Gemini required)."
  echo ""
fi

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Creating virtualenv..."
  python3 -m venv .venv
  SKIP_INSTALL=0
fi

if [[ "$SKIP_INSTALL" -eq 0 ]]; then
  echo "Installing dependencies..."
  "$VENV_PYTHON" -m pip install --upgrade pip
  "$VENV_PYTHON" -m pip install -r requirements.txt
fi

echo "Starting API at http://localhost:$PORT (docs: http://localhost:$PORT/docs)"
exec "$VENV_PYTHON" -m uvicorn app.main:app --reload --host "$HOST_ADDRESS" --port "$PORT"
