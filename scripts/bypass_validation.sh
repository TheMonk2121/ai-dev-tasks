#!/usr/bin/env bash
set -euo pipefail

# Validation Bypass Script
# Temporarily disables pre-commit validation for a single commit

if [ $# -eq 0 ]; then
    echo "Usage: $0 <commit_message>"
    echo ""
    echo "This script temporarily bypasses validation for one commit."
    echo "The validation will be re-enabled for subsequent commits."
    echo ""
    echo "Examples:"
    echo "  $0 'fix: resolve markdown issues'"
    echo "  $0 'feat: add new feature'"
    exit 1
fi

COMMIT_MESSAGE="$1"

echo "!️  Temporarily bypassing validation..."
echo "Commit message: $COMMIT_MESSAGE"
echo ""

# Check if pre-commit hook exists
if [ -f ".git/hooks/pre-commit" ]; then
    echo "📋 Backing up pre-commit hook..."
    cp ".git/hooks/pre-commit" ".git/hooks/pre-commit.backup"

    echo "🚫 Temporarily disabling pre-commit hook..."
    mv ".git/hooks/pre-commit" ".git/hooks/pre-commit.disabled"
fi

# Add and commit
git add .
git commit -m "$COMMIT_MESSAGE"

# Restore pre-commit hook
if [ -f ".git/hooks/pre-commit.disabled" ]; then
    echo "OK Re-enabling pre-commit hook..."
    mv ".git/hooks/pre-commit.disabled" ".git/hooks/pre-commit"
fi

echo "OK Commit successful with temporary validation bypass!"
echo ""
echo "Note: Pre-commit validation is now re-enabled."
