#!/usr/bin/env bash
set -euo pipefail

# -------- Config (edit if you want different models/ports) ----------
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"
LLM_MODEL="${OLLAMA_LLM_MODEL:-llama3}"
PYTHONPATH="backend"
UVICORN_APP="backend.app:app"
# --------------------------------------------------------------------

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/.logs"
mkdir -p "$LOG_DIR"

# Track PIDs for clean shutdown
PIDS=()

cleanup() {
  echo ""
  echo ">> Stopping processes..."
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" || true
      wait "$pid" 2>/dev/null || true
    fi
  done
  echo ">> Done."
}
trap cleanup EXIT

# --- Helpers ---------------------------------------------------------
require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: '$1' not found. Please install it and re-run."
    exit 1
  fi
}

wait_for_http() {
  local url=$1
  local name=$2
  local max_tries=${3:-30}
  local sleep_s=${4:-1}
  local i=0
  echo ">> Waiting for $name at $url ..."
  until curl -sSf "$url" >/dev/null 2>&1; do
    i=$((i+1))
    if (( i >= max_tries )); then
      echo "ERROR: $name not responding at $url"
      exit 1
    fi
    sleep "$sleep_s"
  done
  echo ">> $name is up: $url"
}

# --- Checks ----------------------------------------------------------
require_cmd ollama
require_cmd uvicorn
require_cmd python
require_cmd npm
if [ ! -f "$ROOT_DIR/.venv/bin/activate" ]; then
  echo "WARNING: .venv not found; skipping venv activation (make sure deps are installed)."
else
  echo ">> Activating virtualenv"
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

# --- Start / verify Ollama ------------------------------------------
echo ">> Checking Ollama at $OLLAMA_HOST ..."
if ! curl -sSf "$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then
  echo ">> Ollama not responding; starting 'ollama serve' in the background..."
  # On macOS, you can also open the app instead of serve; we use CLI for portability
  (OLLAMA_ORIGINS="*" ollama serve >> "$LOG_DIR/ollama.log" 2>&1) &
  PIDS+=($!)
  # wait for server
  wait_for_http "$OLLAMA_HOST/api/tags" "Ollama"
else
  echo ">> Ollama already running."
fi

echo ">> Ensuring models are present (this is idempotent):"
echo "   - Embedding model: $EMBED_MODEL"
ollama pull "$EMBED_MODEL"   >> "$LOG_DIR/ollama.log" 2>&1 || true
echo "   - LLM model:       $LLM_MODEL"
ollama pull "$LLM_MODEL"     >> "$LOG_DIR/ollama.log" 2>&1 || true

# --- Train models if missing (optional, quick check) -----------------
if [ ! -f "$ROOT_DIR/backend/models/intent_classifier.joblib" ]; then
  echo ">> intent_classifier.joblib not found; training once..."
  (PYTHONPATH=$PYTHONPATH python -m src.nlp.intent_train \
     --data_csv backend/data/intents.csv \
     --out_dir backend/models >> "$LOG_DIR/train_intent.log" 2>&1) || true
fi
if [ ! -f "$ROOT_DIR/backend/models/safety_classifier.joblib" ]; then
  echo ">> safety_classifier.joblib not found; training once..."
  (PYTHONPATH=$PYTHONPATH python -m src.nlp.safety_train \
     --data_csv backend/data/safety.csv \
     --out_dir backend/models >> "$LOG_DIR/train_safety.log" 2>&1) || true
fi

# --- Start backend ---------------------------------------------------
echo ">> Starting backend on :$BACKEND_PORT ..."
( PYTHONPATH=$PYTHONPATH uvicorn "$UVICORN_APP" --host 0.0.0.0 --port "$BACKEND_PORT" --reload \
    >> "$LOG_DIR/backend.log" 2>&1 ) &
PIDS+=($!)
wait_for_http "http://localhost:${BACKEND_PORT}/healthz" "FastAPI backend"

# --- Start frontend --------------------------------------------------
echo ">> Installing frontend deps (if needed) ..."
( cd "$ROOT_DIR/frontend" && npm install >> "$LOG_DIR/frontend.log" 2>&1 ) || true

echo ">> Starting frontend on :$FRONTEND_PORT ..."
( cd "$ROOT_DIR/frontend" && PORT="$FRONTEND_PORT" npm run dev >> "$LOG_DIR/frontend.log" 2>&1 ) &
PIDS+=($!)
# Give Next.js a moment; it doesn't expose a health endpoint by default
sleep 3

echo ""
echo "===================================================================="
echo "  ✅ All services started"
echo "  Backend:  http://localhost:${BACKEND_PORT}   (health: /healthz)"
echo "  Frontend: http://localhost:${FRONTEND_PORT}"
echo "  Ollama:   $OLLAMA_HOST"
echo "--------------------------------------------------------------------"
echo "  Logs dir: $LOG_DIR"
echo "  Stop all: press Ctrl+C"
echo "===================================================================="
echo ""

# Keep script running to own the child processes
wait
