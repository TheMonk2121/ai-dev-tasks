#!/usr/bin/env bash
# Canonical wrapper to "run the evals"
# - Loads the stable config
# - Prefers Bedrock when credentials are valid
# - Falls back to local LLM evaluation if Bedrock is unavailable
#
# Note: For shellcheck validation, run: shellcheck run_evals.sh throttle_free_eval.sh

set -euo pipefail

echo "🧪 Run the Evals — Canonical Wrapper"
echo "===================================="

# Ensure we're at repo root (presence of throttle_free_eval.sh and scripts/)
if [ ! -f "throttle_free_eval.sh" ] || [ ! -d "scripts" ]; then
  echo "❌ Please run from the repo root (where throttle_free_eval.sh exists)"
  exit 1
fi

# Load stable configuration (prints lock banner)
# shellcheck disable=SC1091
source throttle_free_eval.sh

# Detect Bedrock credentials via AWS CLI if available
USE_BEDROCK=0
if command -v aws >/dev/null 2>&1; then
  if aws sts get-caller-identity >/dev/null 2>&1; then
    echo "🔐 AWS credentials detected; preferring Bedrock path"
    USE_BEDROCK=1
  else
    echo "⚠️ AWS credentials not available via CLI; will try local LLM fallback"
  fi
else
  echo "ℹ️ aws CLI not found; will try local LLM fallback"
fi

# Choose python launcher (prefer uv-managed env)
if command -v uv >/dev/null 2>&1; then
  PY="uv run python"
else
  PY="bin/py"
fi

# Run evaluation
if [ "$USE_BEDROCK" = "1" ]; then
  echo "🚀 Running stable Bedrock evaluation..."
  $PY scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
else
  echo "🚀 Running stable local-LLM evaluation..."
  $PY scripts/ragchecker_official_evaluation.py --use-local-llm --bypass-cli --stable
fi

echo
echo "📦 Results are written under: metrics/baseline_evaluations/"
echo "🧭 SOP: 000_core/000_evaluation-system-entry-point.md"
