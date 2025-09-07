#!/usr/bin/env bash
# Canonical Stable Evaluation Configuration
# Loads locked environment for regression tracking

echo "🔒 Loading Canonical Stable Configuration"
echo "=========================================="

# Load stable configuration FIRST, then apply stricter overrides
export RAGCHECKER_ENV_FILE="${RAGCHECKER_ENV_FILE:-configs/stable_bedrock.env}"
STABLE_ENV_FILE="$RAGCHECKER_ENV_FILE"
if [ -f "$STABLE_ENV_FILE" ]; then
  echo "📁 Loading stable config: $STABLE_ENV_FILE"
  # shellcheck source=configs/stable_bedrock.env
  source "$STABLE_ENV_FILE"
  echo "🔒 Loaded env from $STABLE_ENV_FILE … lock=True"
else
  echo "❌ Stable config not found: $STABLE_ENV_FILE"
  echo "💡 Run: cp configs/stable_bedrock.env.template configs/stable_bedrock.env"
  exit 1
fi

# Queue Client Concurrency Control (Critical for USE_BEDROCK_QUEUE=1)
export USE_BEDROCK_QUEUE=1
export ASYNC_MAX_CONCURRENCY=1
# Standardize both names
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_MAX_CONCURRENCY=1

# Evaluator-Level Rate Limiting (Throttle-free overrides)
export BEDROCK_MAX_RPS=0.08
export BEDROCK_COOLDOWN_SEC=20

# Retries/backoff — set both legacy and standardized names to avoid alias pitfalls
export BEDROCK_MAX_RETRIES=8
export BEDROCK_RETRY_MAX=${BEDROCK_MAX_RETRIES}
export BEDROCK_BASE_BACKOFF=2.0
export BEDROCK_RETRY_BASE=${BEDROCK_BASE_BACKOFF}
export BEDROCK_MAX_BACKOFF=16.0
export BEDROCK_RETRY_MAX_SLEEP=${BEDROCK_MAX_BACKOFF}

# Disable expensive features
export RAGCHECKER_COVERAGE_REWRITE=0
export RAGCHECKER_JSON_PROMPTS=0
export RAGCHECKER_JSON_MAX_TOKENS=200

# Model + Region (keep explicit for clarity)
export BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID:-anthropic.claude-3-haiku-20240307-v1:0}
export AWS_REGION=${AWS_REGION:-us-east-1}

# Verify lock status
if [ "${RAGCHECKER_LOCK_ENV:-0}" = "1" ]; then
  echo "🔒 Environment locked for regression tracking"
fi

# Evidence Selection (Minimal)
export RAGCHECKER_EVIDENCE_JACCARD=0.07
export RAGCHECKER_EVIDENCE_COVERAGE=0.20

# AWS Region
export AWS_REGION=us-east-1

echo "✅ Throttle-Free Configuration Loaded"
echo "🚫 Coverage Rewrite: DISABLED"
echo "🚫 JSON Prompts: DISABLED"
echo "🚫 Queue Concurrency: IN_FLIGHT=${BEDROCK_MAX_IN_FLIGHT} (CONCURRENCY=${BEDROCK_MAX_CONCURRENCY})"
echo "🚫 Max RPS: ${BEDROCK_MAX_RPS} (Cooldown: ${BEDROCK_COOLDOWN_SEC}s)"
echo "🧩 Backoff: base=${BEDROCK_BASE_BACKOFF} (RETRY_BASE=${BEDROCK_RETRY_BASE}), max=${BEDROCK_MAX_BACKOFF} (RETRY_MAX_SLEEP=${BEDROCK_RETRY_MAX_SLEEP})"
echo "🧠 Model: ${BEDROCK_MODEL_ID}"
echo "🔒 Env lock file: ${RAGCHECKER_ENV_FILE}"
echo "🎯 Target: Zero throttling, stable evaluation"
echo "🚀 Ready for: python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli"

# Convenience aliases (non-invasive): apply/revert recall boost safely
alias recall_boost_apply='python3 scripts/toggle_recall_boost.py apply && ./scripts/run_ragchecker_smoke_test.sh'
alias recall_boost_revert='python3 scripts/toggle_recall_boost.py revert && ./scripts/run_ragchecker_smoke_test.sh'

echo "💡 Tip: Use 'recall_boost_apply' to apply recall tuning, then run the full eval."
echo "          Revert anytime with 'recall_boost_revert'."
