#!/usr/bin/env bash
# Recall-Optimized Evaluation Runner
# Loads recall-focused env then runs the official evaluator with Bedrock.

set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")"/.. && pwd)

ENV_FILE="${REPO_ROOT}/configs/recall_optimized_bedrock.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Recall env not found: $ENV_FILE"
  exit 1
fi

echo "🔎 Loading recall-optimized configuration"
echo "📁 $ENV_FILE"

export RAGCHECKER_ENV_FILE="$ENV_FILE"
export RAGCHECKER_LOCK_ENV=1

# Source the env file for the current shell too (visibility + downstream tools)
# shellcheck source=/dev/null
source "$ENV_FILE"

echo "✅ Recall config loaded (locked)"
echo "🧠 Model: ${BEDROCK_MODEL_ID} | Region: ${AWS_REGION}"
echo "📈 RPS=${BEDROCK_MAX_RPS}, InFlight=${BEDROCK_MAX_IN_FLIGHT}, JSON=${RAGCHECKER_JSON_PROMPTS}, COVERAGE=${RAGCHECKER_COVERAGE_REWRITE}"
echo "🧪 Running evaluation..."

uv run python "${REPO_ROOT}/scripts/ragchecker_official_evaluation.py" \
  --use-bedrock \
  --bypass-cli \
  --profile recall

