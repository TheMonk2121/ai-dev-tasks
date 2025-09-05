#!/usr/bin/env bash
# Canonical Stable Evaluation Configuration
# Loads locked environment for regression tracking

echo "🔒 Loading Canonical Stable Configuration"
echo "=========================================="

# Queue Client Concurrency Control (Critical for USE_BEDROCK_QUEUE=1)
export USE_BEDROCK_QUEUE=1
export ASYNC_MAX_CONCURRENCY=1                    # Single async operation at a time
export BEDROCK_MAX_IN_FLIGHT=1                    # Single concurrent request (effective var)

# Evaluator-Level Rate Limiting (Conservative)
export BEDROCK_MAX_RPS=0.08                       # Very conservative rate
export BEDROCK_COOLDOWN_SEC=20                    # Long cooldown after 429s
export BEDROCK_MAX_RETRIES=8                      # More retries (effective var)
export BEDROCK_BASE_BACKOFF=2.0                   # Exponential backoff (effective var)
export BEDROCK_MAX_BACKOFF=16.0                   # Max sleep time (effective var)

# Disable Coverage Rewrite (Major Source of Bedrock Calls)
export RAGCHECKER_COVERAGE_REWRITE=0              # Disable coverage rewrite

# Reduce JSON Usage (Prevent Repair Loops)
export RAGCHECKER_JSON_PROMPTS=0                  # Disable JSON prompts
export RAGCHECKER_JSON_MAX_TOKENS=200

# Model + Region
export BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
export AWS_REGION=us-east-1

# Load stable configuration
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
echo "🚫 Queue Concurrency: 1 (BEDROCK_MAX_IN_FLIGHT)"
echo "🚫 Max RPS: ${BEDROCK_MAX_RPS}"
echo "🚫 Cooldown: ${BEDROCK_COOLDOWN_SEC}s"
echo "🧩 Backoff: base=${BEDROCK_BASE_BACKOFF}, max=${BEDROCK_MAX_BACKOFF}"
echo "🧠 Model: ${BEDROCK_MODEL_ID}"
echo "🔒 Env lock file: ${RAGCHECKER_ENV_FILE}"
echo "🎯 Target: Zero throttling, stable evaluation"
echo "🚀 Ready for: python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli"
