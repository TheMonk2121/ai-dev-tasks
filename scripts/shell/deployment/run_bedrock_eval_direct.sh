#!/usr/bin/env bash

# Simple, safe one-liner runner for Bedrock eval
# Usage:
#   bash scripts/run_bedrock_eval_direct.sh            # Bedrock (default)
#   bash scripts/run_bedrock_eval_direct.sh --local    # Use local LLM (Ollama)
#
# Optional env overrides before the command (examples):
#   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0 bash scripts/run_bedrock_eval_direct.sh
#   UV_PYTHON=3.12 bash scripts/run_bedrock_eval_direct.sh --local

set -euo pipefail

# Move to repo root (this file lives in scripts/)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd "${SCRIPT_DIR}/.." && pwd)
cd "${ROOT_DIR}"

# Ensure uv is available
if ! command -v uv >/dev/null 2>&1; then
  echo "📦 Installing uv (Python toolchain manager)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  source "$HOME/.local/bin/env"
fi

# Ensure Python 3.12 is available for psycopg2-binary compatibility
UV_PY=${UV_PYTHON:-3.12}
echo "🐍 Ensuring Python ${UV_PY} is available for uv..."
uv python install "${UV_PY}" >/dev/null 2>&1 || true

# Default configuration (can be overridden via environment)
export AWS_REGION=${AWS_REGION:-us-east-1}
export BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID:-anthropic.claude-3-5-sonnet-20240620-v1:0}

# Prevent auto-loading the stable env (which disables coverage rewrite)
export RAGCHECKER_ENV_FILE=${RAGCHECKER_ENV_FILE:-manual}

# Force in-process path + compose in text mode
export RAGCHECKER_BYPASS_CLI=1
# Force compose/coverage rewrite ON (override any prior shell value)
export RAGCHECKER_COVERAGE_REWRITE=1
export RAGCHECKER_JSON_PROMPTS=${RAGCHECKER_JSON_PROMPTS:-0}

# Encourage multi-sentence answers (draft + fallback)
export RAGCHECKER_MIN_OUTPUT_SENTENCES=${RAGCHECKER_MIN_OUTPUT_SENTENCES:-3}
export RAGCHECKER_EXTRACTIVE_MIN_SENT=${RAGCHECKER_EXTRACTIVE_MIN_SENT:-3}

# Compose budget
export RAGCHECKER_TARGET_WORDS=${RAGCHECKER_TARGET_WORDS:-600}
export RAGCHECKER_COMPOSE_MAX_TOKENS=${RAGCHECKER_COMPOSE_MAX_TOKENS:-1400}

# Bedrock anti-throttle clamps (safe, proven)
export USE_BEDROCK_QUEUE=${USE_BEDROCK_QUEUE:-1}
export BEDROCK_MAX_IN_FLIGHT=${BEDROCK_MAX_IN_FLIGHT:-1}
export BEDROCK_MAX_RPS=${BEDROCK_MAX_RPS:-0.12}
export BEDROCK_COOLDOWN_SEC=${BEDROCK_COOLDOWN_SEC:-30}
export BEDROCK_MAX_RETRIES=${BEDROCK_MAX_RETRIES:-8}
export BEDROCK_RETRY_BASE=${BEDROCK_RETRY_BASE:-1.8}
export BEDROCK_RETRY_MAX_SLEEP=${BEDROCK_RETRY_MAX_SLEEP:-20}

# Mode selection
MODE="bedrock"  # default
if [[ "${1:-}" == "--local" ]]; then
  MODE="local"
fi

echo "" 
echo "🚀 Running RAGChecker eval (${MODE})"
echo "   Python:        ${UV_PY}"
echo "   AWS Region:    ${AWS_REGION}"
if [[ "${MODE}" == "bedrock" ]]; then
  echo "   Bedrock Model: ${BEDROCK_MODEL_ID}"
fi
echo "   Compose:       RAGCHECKER_COVERAGE_REWRITE=${RAGCHECKER_COVERAGE_REWRITE} (text-mode compose)"
echo "   Throttle caps: IN_FLIGHT=${BEDROCK_MAX_IN_FLIGHT}, RPS=${BEDROCK_MAX_RPS}, COOLDOWN=${BEDROCK_COOLDOWN_SEC}s"
echo "   Min sentences: draft=${RAGCHECKER_MIN_OUTPUT_SENTENCES}, extractive=${RAGCHECKER_EXTRACTIVE_MIN_SENT}"
echo ""

if [[ "${MODE}" == "bedrock" ]]; then
  uv run -p "${UV_PY}" python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli
else
  uv run -p "${UV_PY}" python scripts/ragchecker_official_evaluation.py --use-local-llm --bypass-cli
fi
