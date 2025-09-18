#!/bin/bash
# =============================================================================
# MOCK PROFILE EVALUATION SCRIPT
# =============================================================================
# Purpose: Run mock profile evaluations for infrastructure testing
# Use Case: CI infrastructure, unit tests, development setup
# Status: OPTIMIZED for speed and reliability

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$PROJECT_ROOT"

# Load mock profile configuration
export RAGCHECKER_ENV_FILE="${RAGCHECKER_ENV_FILE:-scripts/configs/profiles/mock.env}"
if [ -f "$RAGCHECKER_ENV_FILE" ]; then
    echo "📁 Loading mock profile config: $RAGCHECKER_ENV_FILE"
    # shellcheck source=/dev/null
    source "$RAGCHECKER_ENV_FILE"
    echo "⚡ Loaded mock profile configuration"
else
    echo "❌ Mock profile config not found: $RAGCHECKER_ENV_FILE"
    exit 1
fi

# =============================================================================
# MOCK PROFILE EVALUATION
# =============================================================================
echo "🚀 MOCK PROFILE EVALUATION - Infrastructure Testing"
echo "=" * 80
echo "Profile: Mock (Infrastructure Testing)"
echo "Purpose: Fast plumbing tests without external dependencies"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Run mock profile evaluation
echo "⚡ Running mock profile evaluation..."
uv run python evals/scripts/evaluation/clean_dspy_evaluator.py --profile mock --limit 5

# =============================================================================
# INFRASTRUCTURE VALIDATION
# =============================================================================
echo ""
echo "📊 INFRASTRUCTURE VALIDATION"
echo "=" * 40

# Check if CI mode is enabled
if [ "${RAGCHECKER_CI_MODE:-0}" = "1" ]; then
    echo "🔍 CI mode enabled - running infrastructure checks..."
    uv run python scripts/infrastructure_validation.py --profile mock
else
    echo "⚠️  CI mode disabled - skipping infrastructure checks"
fi

# Check if fast iteration is enabled
if [ "${RAGCHECKER_FAST_ITERATION:-0}" = "1" ]; then
    echo "⚡ Fast iteration enabled - running quick tests..."
    uv run python scripts/quick_tests.py --profile mock
else
    echo "⚠️  Fast iteration disabled - skipping quick tests"
fi

echo ""
echo "✅ Mock profile evaluation completed successfully"
echo "📁 Results saved to: metrics/infrastructure_tests/"
echo "⚡ CI mode: ${RAGCHECKER_CI_MODE:-0}"
echo "🔍 Fast iteration: ${RAGCHECKER_FAST_ITERATION:-0}"
