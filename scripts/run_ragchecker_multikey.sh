#!/usr/bin/env bash

# RAGChecker with Multi-Key Enhanced Bedrock Client
# Optimized for maximum throughput and minimal rate limiting

set -eo pipefail

echo "🚀 Starting RAGChecker with Multi-Key Enhanced Bedrock Client"
echo "============================================================"

# Activate virtual environment (prefer .venv, then venv)
VENV_DIR="${VENV_DIR:-.venv}"
if [ -f "$VENV_DIR/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$VENV_DIR/bin/activate"
elif [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "venv/bin/activate"
else
  echo "⚠️  No virtualenv found at .venv/ or venv/. Continuing without activation." >&2
fi

# Load multi-key configuration from env file if available (avoids hardcoding secrets)
MULTI_ENV="config/multi_key_bedrock.env"
if [ -f "$MULTI_ENV" ]; then
  echo "🔧 Loading multi-key configuration from $MULTI_ENV"
  # shellcheck source=config/multi_key_bedrock.env
  # shellcheck disable=SC1091
  . "$MULTI_ENV"
else
  echo "⚠️  $MULTI_ENV not found. Ensure AWS_*_1/2/3 variables are exported." >&2
fi

# If no multi-key credentials are present, continue in single-key mode
if [ -z "${AWS_ACCESS_KEY_ID_1:-}" ] && [ -z "${AWS_ACCESS_KEY_ID_2:-}" ] && [ -z "${AWS_ACCESS_KEY_ID_3:-}" ]; then
  echo "ℹ️  No multi-key AWS credentials detected (AWS_ACCESS_KEY_ID_1/2/3)." >&2
  echo "   Proceeding with single-key environment if configured." >&2
fi

echo "✅ Multi-key configuration loaded"
echo "📊 Expected performance: 2-5x faster than single key"
echo "🔄 Starting evaluation..."
echo

# Evaluation quality tuning (JSON compliance + evidence coverage)
export RAGCHECKER_JSON_PROMPTS=1
export RAGCHECKER_JSON_MAX_TOKENS=1200
export RAGCHECKER_ROBUST_PARSER=1
export RAGCHECKER_CONCISE=1
export RAGCHECKER_MAX_WORDS=1000

# Evidence selection tuning
export RAGCHECKER_EVIDENCE_KEEP_MODE=target_k
export RAGCHECKER_SIGNAL_DELTA_WEAK=0.12
export RAGCHECKER_SIGNAL_DELTA_STRONG=0.25
export RAGCHECKER_TARGET_K_WEAK=3
export RAGCHECKER_TARGET_K_BASE=6
export RAGCHECKER_TARGET_K_STRONG=8
export RAGCHECKER_EVIDENCE_MIN_SENT=2
export RAGCHECKER_EVIDENCE_MAX_SENT=8
# Fallback percentile when needed
export RAGCHECKER_EVIDENCE_KEEP_PERCENTILE=70

# Run RAGChecker with enhanced client
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli

echo
echo "🏁 RAGChecker evaluation completed!"
echo "📈 Check metrics/baseline_evaluations/ for results"
