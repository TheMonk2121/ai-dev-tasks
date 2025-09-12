#!/usr/bin/env bash
set -euo pipefail

# Quick runner for recall-optimized evaluation.
# Defaults to Bedrock backend; pass --local to use local LLM (Ollama).
# Additional args are forwarded to ragchecker_official_evaluation.py.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/scripts}"

BACKEND_FLAG="--use-bedrock"
if [[ "${1:-}" == "--local" ]]; then
  BACKEND_FLAG="--use-local-llm"
  shift
fi

# Prefer the profile loader (loads configs/recall_optimized_bedrock.env).
# If you want backend-agnostic recall tuning, you can also do:
#   --env-file configs/recall_optimized.env

exec uv run python "${REPO_ROOT}/scripts/ragchecker_official_evaluation.py" \
  "${BACKEND_FLAG}" \
  --profile recall \
  --stable \
  "$@"

