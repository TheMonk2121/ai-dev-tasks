#!/usr/bin/env bash
# RAGChecker Smoke Test Runner
# Fast iteration with subset of representative test cases

set -eo pipefail

echo "🚀 RAGChecker Smoke Test Runner"
echo "==============================="

# Load stable configuration
STABLE_ENV_FILE="${RAGCHECKER_ENV_FILE:-configs/stable_bedrock.env}"
if [ -f "$STABLE_ENV_FILE" ]; then
  echo "📁 Loading stable config: $STABLE_ENV_FILE"
  source "$STABLE_ENV_FILE"
  echo "🔒 Loaded env from $STABLE_ENV_FILE … lock=True"
else
  echo "❌ Stable config not found: $STABLE_ENV_FILE"
  echo "💡 Run: cp configs/stable_bedrock.env.template configs/stable_bedrock.env"
  exit 1
fi

# Set smoke test mode (respect pre-set RAGCHECKER_FAST_MODE)
export RAGCHECKER_FAST_MODE="${RAGCHECKER_FAST_MODE:-1}"
export RAGCHECKER_SMOKE_TEST=1

echo "✅ Smoke Test Configuration Loaded"
echo "🚫 Coverage Rewrite: DISABLED"
echo "🚫 JSON Prompts: DISABLED"
echo "🚫 Queue Concurrency: $BEDROCK_MAX_CONCURRENCY"
echo "🚫 Max RPS: $BEDROCK_MAX_RPS"
echo "🚫 Cooldown: ${BEDROCK_COOLDOWN_SEC}s"
echo "🎯 Model: $BEDROCK_MODEL_ID"
echo "🌍 Region: $AWS_REGION"
if [ "${RAGCHECKER_FAST_MODE}" = "1" ]; then
  echo "💨 Smoke Test Mode: ENABLED (fast mode)"
else
  echo "💨 Smoke Test Mode: DISABLED (full cases)"
fi
echo "🎯 Target: Fast iteration with representative subset"
echo

# Run smoke test evaluation
echo "🚀 Starting smoke test evaluation..."
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable

echo "✅ Smoke test completed"
echo "💡 For full evaluation, run: source throttle_free_eval.sh && python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable"
