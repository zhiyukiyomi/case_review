#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOGS_DIR="$ROOT_DIR/logs"

mkdir -p "$LOGS_DIR"

BACKEND_PID_FILE="$LOGS_DIR/backend.pid"
FRONTEND_PID_FILE="$LOGS_DIR/frontend.pid"

if [[ -x "$BACKEND_DIR/.venv/bin/python" ]]; then
  BACKEND_PYTHON="$BACKEND_DIR/.venv/bin/python"
else
  echo "Backend virtual environment not found. Run ./setup_backend.sh first."
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "Frontend dependencies are missing. Run ./setup_frontend.sh first."
  exit 1
fi

cd "$BACKEND_DIR"
nohup "$BACKEND_PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >"$LOGS_DIR/backend.out.log" 2>"$LOGS_DIR/backend.err.log" &
echo $! >"$BACKEND_PID_FILE"

cd "$FRONTEND_DIR"
nohup npm run dev -- --host 127.0.0.1 --port 5173 >"$LOGS_DIR/frontend.out.log" 2>"$LOGS_DIR/frontend.err.log" &
echo $! >"$FRONTEND_PID_FILE"

echo "Services are starting..."
echo "Frontend: http://127.0.0.1:5173"
echo "Backend:  http://127.0.0.1:8000"
