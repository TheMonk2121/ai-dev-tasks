#!/bin/bash
# Load evaluation profile configuration
# Usage: source scripts/shell/setup/load_profile.sh [gold|real|mock]

PROFILE="${1:-real}"
PROFILE_DIR="scripts/configs/profiles"
PROFILE_FILE="$PROFILE_DIR/$PROFILE.env"

echo "🔧 Loading evaluation profile: $PROFILE"

# Check if profile file exists
if [ ! -f "$PROFILE_FILE" ]; then
    echo "❌ Profile file not found: $PROFILE_FILE"
    echo "   Available profiles: gold, real, mock"
    exit 1
fi

# Load the profile
# shellcheck source=/dev/null
source "$PROFILE_FILE"

echo "✅ Profile '$PROFILE' loaded successfully"
echo "   📊 Database: ${POSTGRES_DSN:0:30}..."
echo "   🔧 Evaluation: $EVAL_DRIVER"
echo "   🐍 UV Environment: $UV_PROJECT_ENVIRONMENT"
echo "   🎯 RAG System: $([ "$RAGCHECKER_USE_REAL_RAG" = "1" ] && echo "Real" || echo "Synthetic")"
