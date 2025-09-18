#!/bin/bash
# =============================================================================
# GOLD PROFILE EVALUATION SCRIPT
# =============================================================================
# Purpose: Run gold profile evaluations for production baselines
# Use Case: CI gates, baseline enforcement, regression detection
# Status: OPTIMIZED for production stability

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$PROJECT_ROOT"

# Load gold profile configuration
export RAGCHECKER_ENV_FILE="${RAGCHECKER_ENV_FILE:-scripts/configs/profiles/gold.env}"
if [ -f "$RAGCHECKER_ENV_FILE" ]; then
    echo "📁 Loading gold profile config: $RAGCHECKER_ENV_FILE"
    # shellcheck source=/dev/null
    source "$RAGCHECKER_ENV_FILE"
    echo "🔒 Loaded gold profile configuration"
else
    echo "❌ Gold profile config not found: $RAGCHECKER_ENV_FILE"
    exit 1
fi

# =============================================================================
# GOLD PROFILE EVALUATION
# =============================================================================
echo "🚀 GOLD PROFILE EVALUATION - Production Baselines"
echo "=" * 80
echo "Profile: Gold (Production Baselines & CI Gates)"
echo "Purpose: Curated test cases for reliable performance tracking"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Run gold profile evaluation
if [ "$USE_BEDROCK" = "1" ]; then
    echo "🚀 Running gold profile Bedrock evaluation..."
    uv run python evals/scripts/evaluation/clean_dspy_evaluator.py --profile gold --limit 5
else
    echo "🚀 Running gold profile local-LLM evaluation..."
    uv run python evals/scripts/evaluation/clean_dspy_evaluator.py --profile gold --limit 5
fi

# =============================================================================
# BASELINE VALIDATION
# =============================================================================
echo ""
echo "📊 BASELINE VALIDATION"
echo "=" * 40

# Check if baseline enforcement is enabled
if [ "${RAGCHECKER_BASELINE_ENFORCEMENT:-0}" = "1" ]; then
    echo "🔍 Checking baseline compliance..."
    uv run python scripts/abp_validation.py --profile gold
else
    echo "⚠️  Baseline enforcement disabled - skipping validation"
fi

echo ""
echo "✅ Gold profile evaluation completed successfully"
echo "📁 Results saved to: metrics/baseline_evaluations/"
echo "🔒 Baseline enforcement: ${RAGCHECKER_BASELINE_ENFORCEMENT:-0}"
