#!/bin/bash

set -eo pipefail

echo "🚀 Starting RAGChecker with Intelligent Queue System"
echo "============================================================"

# Resolve repo root relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Activate virtual environment (prefer .venv, then venv)
VENV_DIR="${VENV_DIR:-$REPO_ROOT/.venv}"
if [ -f "$VENV_DIR/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "$VENV_DIR/bin/activate"
elif [ -f "$REPO_ROOT/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "$REPO_ROOT/venv/bin/activate"
else
    echo "⚠️  No virtualenv found at .venv/ or venv/. Continuing without activation." >&2
fi

# Set up single key configuration
export AWS_REGION=us-east-1

# Queue system settings - stable defaults (single choke point)
export BEDROCK_BASE_DELAY=0.2
export BEDROCK_BATCH_SIZE=3
export BEDROCK_BATCH_WINDOW=1.0
export BEDROCK_ENABLE_QUEUE=true
export BEDROCK_ENABLE_BATCHING=true
export BEDROCK_ENABLE_PRIORITY=true

# Deterministic concurrency and gentle RPS caps
export USE_BEDROCK_QUEUE=1
export ASYNC_MAX_CONCURRENCY=${ASYNC_MAX_CONCURRENCY:-1}
export BEDROCK_MAX_CONCURRENCY=${BEDROCK_MAX_CONCURRENCY:-1}
export BEDROCK_MAX_RPS=${BEDROCK_MAX_RPS:-0.15}
export BEDROCK_RETRY_MAX=${BEDROCK_RETRY_MAX:-8}
export BEDROCK_RETRY_BASE=${BEDROCK_RETRY_BASE:-1.8}
export BEDROCK_RETRY_MAX_SLEEP=${BEDROCK_RETRY_MAX_SLEEP:-20}
export BEDROCK_COOLDOWN_SEC=${BEDROCK_COOLDOWN_SEC:-12}

# Performance optimization flags
export BEDROCK_ENABLE_CACHING=true
export BEDROCK_ENABLE_METRICS=true
export BEDROCK_ENABLE_HEALTH_CHECK=true

# Evaluation quality tuning (JSON compliance; reduced load)
export RAGCHECKER_JSON_PROMPTS=1
export RAGCHECKER_JSON_MAX_TOKENS=${RAGCHECKER_JSON_MAX_TOKENS:-900}
export RAGCHECKER_ROBUST_PARSER=1
export RAGCHECKER_CONCISE=1
export RAGCHECKER_MAX_WORDS=1000

# Reduce costly coverage rewrite during eval to prevent throttling
export RAGCHECKER_COVERAGE_REWRITE=${RAGCHECKER_COVERAGE_REWRITE:-0}

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

echo "✅ Queue system configuration loaded"
echo "🧰 Active Bedrock caps: ASYNC_MAX_CONCURRENCY=$ASYNC_MAX_CONCURRENCY, BEDROCK_MAX_CONCURRENCY=$BEDROCK_MAX_CONCURRENCY, BEDROCK_MAX_RPS=$BEDROCK_MAX_RPS, RETRY_MAX=$BEDROCK_RETRY_MAX"
echo "🧪 Eval JSON: PROMPTS=$RAGCHECKER_JSON_PROMPTS, MAX_TOKENS=$RAGCHECKER_JSON_MAX_TOKENS, COVERAGE_REWRITE=$RAGCHECKER_COVERAGE_REWRITE"
echo "🔄 Starting evaluation..."

# Run RAGChecker with queue system
python3 "$REPO_ROOT/scripts/ragchecker_official_evaluation.py" --use-bedrock --bypass-cli
