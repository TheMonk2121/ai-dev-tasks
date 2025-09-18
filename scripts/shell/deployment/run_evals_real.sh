#!/bin/bash
# =============================================================================
# REAL PROFILE EVALUATION SCRIPT
# =============================================================================
# Purpose: Run real profile evaluations for development and tuning
# Use Case: Development, tuning, full pipeline validation
# Status: OPTIMIZED for development flexibility

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$PROJECT_ROOT"

# Load real profile configuration
export RAGCHECKER_ENV_FILE="${RAGCHECKER_ENV_FILE:-scripts/configs/profiles/real.env}"
if [ -f "$RAGCHECKER_ENV_FILE" ]; then
    echo "📁 Loading real profile config: $RAGCHECKER_ENV_FILE"
    # shellcheck source=/dev/null
    source "$RAGCHECKER_ENV_FILE"
    echo "🔧 Loaded real profile configuration"
else
    echo "❌ Real profile config not found: $RAGCHECKER_ENV_FILE"
    exit 1
fi

# =============================================================================
# REAL PROFILE EVALUATION
# =============================================================================
echo "🚀 REAL PROFILE EVALUATION - Development & Tuning"
echo "=" * 80
echo "Profile: Real (Development & Tuning)"
echo "Purpose: Full system testing with project data"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Run real profile evaluation
if [ "$USE_BEDROCK" = "1" ]; then
    echo "🚀 Running real profile Bedrock evaluation..."
    uv run python evals/scripts/evaluation/clean_dspy_evaluator.py --profile real --limit 5
else
    echo "🚀 Running real profile local-LLM evaluation..."
    uv run python evals/scripts/evaluation/clean_dspy_evaluator.py --profile real --limit 5
fi

# =============================================================================
# DEVELOPMENT VALIDATION
# =============================================================================
echo ""
echo "📊 DEVELOPMENT VALIDATION"
echo "=" * 40

# Check if tuning mode is enabled
if [ "${RAGCHECKER_TUNING_MODE:-0}" = "1" ]; then
    echo "🔧 Tuning mode enabled - running parameter optimization..."
    uv run python scripts/parameter_tuning.py --profile real
else
    echo "⚠️  Tuning mode disabled - skipping parameter optimization"
fi

# Check if performance monitoring is enabled
if [ "${RAGCHECKER_PERFORMANCE_MONITORING:-0}" = "1" ]; then
    echo "📈 Performance monitoring enabled - generating reports..."
    uv run python scripts/performance_analysis.py --profile real
else
    echo "⚠️  Performance monitoring disabled - skipping analysis"
fi

echo ""
echo "✅ Real profile evaluation completed successfully"
echo "📁 Results saved to: metrics/development_evaluations/"
echo "🔧 Tuning mode: ${RAGCHECKER_TUNING_MODE:-0}"
echo "📈 Performance monitoring: ${RAGCHECKER_PERFORMANCE_MONITORING:-0}"
