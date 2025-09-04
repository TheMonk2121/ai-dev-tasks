#!/bin/bash

set -eo pipefail

echo "🚀 Starting RAGChecker with Optimized Single Key"
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

# Use only your primary key with optimized settings
export AWS_REGION=us-east-1

# Very conservative rate limiting settings for single key
export BEDROCK_BASE_RPS=0.1
export BEDROCK_MAX_RPS=0.3
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_COOLDOWN_SEC=10
export BEDROCK_CIRCUIT_BREAKER_TIMEOUT=60
export BEDROCK_MAX_RETRIES=3
export BEDROCK_RETRY_BASE=2.0
export BEDROCK_RETRY_MAX_SLEEP=15

# Performance optimization flags
export BEDROCK_ENABLE_CACHING=true
export BEDROCK_ENABLE_METRICS=true
export BEDROCK_ENABLE_HEALTH_CHECK=true

echo "✅ Single key configuration loaded"
echo "📊 Expected performance: Optimized single key performance"
echo "🔄 Starting evaluation..."

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

# Run RAGChecker with optimized single key
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli
