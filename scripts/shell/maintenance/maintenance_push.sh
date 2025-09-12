#!/usr/bin/env bash
# Maintenance Push Wrapper (B-052-e Integration)
#
# Simple wrapper script to integrate auto-push prompt into maintenance workflows.
# This can be called after maintenance operations to prompt for pushing changes.
#
# Usage:
#     ./scripts/maintenance_push.sh [--force] [--message "custom message"]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Check if Python script exists
if [ ! -f "scripts/auto_push_prompt.py" ]; then
    echo "❌ auto_push_prompt.py not found"
    exit 1
fi

# Pass all arguments to the Python script
echo "🚀 Running maintenance push prompt..."
uv run python scripts/auto_push_prompt.py "$@"
