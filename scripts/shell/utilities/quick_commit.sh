#!/usr/bin/env bash
set -euo pipefail

# Quick Commit Script - Bypasses validation for simple changes
# Use this for minor fixes that don't affect core documentation

if [ $# -eq 0 ]; then
    echo "Usage: $0 <commit_message>"
    echo ""
    echo "This script commits changes while bypassing documentation validation."
    echo "Use only for simple fixes that don't affect core documentation."
    echo ""
    echo "Examples:"
    echo "  $0 'fix: typo in comment'"
    echo "  $0 'feat: add new test file'"
    echo "  $0 'fix: update config setting'"
    exit 1
fi

COMMIT_MESSAGE="$1"

echo "🚀 Quick commit with bypassed validation..."
echo "Commit message: $COMMIT_MESSAGE"
echo ""

# Add all changes
git add .

# Commit with --no-verify to bypass pre-commit hooks
git commit --no-verify -m "$COMMIT_MESSAGE"

echo "✅ Quick commit successful!"
echo ""
echo "Note: This bypassed documentation validation."
echo "For core documentation changes, use regular 'git commit' instead."
