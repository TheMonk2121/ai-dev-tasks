#!/usr/bin/env bash
set -euo pipefail

# Smart Commit Script
# Analyzes changes and chooses appropriate validation level

if [ $# -eq 0 ]; then
    echo "Usage: $0 <commit_message>"
    echo ""
    echo "This script analyzes your changes and chooses the best commit strategy:"
    echo "  - Full validation for core documentation changes"
    echo "  - Bypass validation for simple fixes"
    echo "  - Quick commit for non-documentation changes"
    echo ""
    echo "Examples:"
    echo "  $0 'fix: typo in comment'"
    echo "  $0 'feat: add new feature'"
    echo "  $0 'docs: update system overview'"
    exit 1
fi

COMMIT_MESSAGE="$1"

echo "🧠 Smart commit analysis..."
echo "Commit message: $COMMIT_MESSAGE"
echo ""

# Get staged files
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")
CHANGED_FILES=$(git diff --name-only 2>/dev/null || echo "")

# If no staged files, stage all changes
if [ -z "$STAGED_FILES" ]; then
    echo "📁 Staging all changes..."
    git add .
    STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")
fi

# Analyze file types
CORE_DOCS=0
MARKDOWN_FILES=0
CODE_FILES=0
CONFIG_FILES=0

for file in $STAGED_FILES; do
    if [[ "$file" =~ \.md$ ]]; then
        MARKDOWN_FILES=$((MARKDOWN_FILES + 1))
        # Check if it's a core documentation file
        if [[ "$file" =~ ^(000_backlog|100_cursor-memory-context|400_system-overview|400_project-overview|400_context-priority-guide)\.md$ ]]; then
            CORE_DOCS=$((CORE_DOCS + 1))
        fi
    elif [[ "$file" =~ \.(py|js|ts|sh)$ ]]; then
        CODE_FILES=$((CODE_FILES + 1))
    elif [[ "$file" =~ \.(json|yaml|yml|toml|config)$ ]]; then
        CONFIG_FILES=$((CONFIG_FILES + 1))
    fi
done

echo "📊 Change Analysis:"
echo "  - Core documentation files: $CORE_DOCS"
echo "  - Markdown files: $MARKDOWN_FILES"
echo "  - Code files: $CODE_FILES"
echo "  - Config files: $CONFIG_FILES"
echo ""

# Determine commit strategy
if [ $CORE_DOCS -gt 0 ]; then
    echo "🔍 Core documentation changed - using full validation..."
    echo "⚠️  This may fail due to existing markdown issues."
    echo "   Consider using: ./scripts/bypass_validation.sh '$COMMIT_MESSAGE'"
    echo ""
    read -p "Continue with full validation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit -m "$COMMIT_MESSAGE"
    else
        echo "❌ Commit cancelled. Use bypass_validation.sh for quick commits."
        exit 1
    fi
elif [ $MARKDOWN_FILES -gt 0 ]; then
    echo "📝 Markdown files changed - using validation bypass..."
    echo "   (Non-core documentation changes)"
    ./scripts/bypass_validation.sh "$COMMIT_MESSAGE"
elif [ $CODE_FILES -gt 0 ] || [ $CONFIG_FILES -gt 0 ]; then
    echo "⚙️  Code/config files changed - using quick commit..."
    ./scripts/quick_commit.sh "$COMMIT_MESSAGE"
else
    echo "📄 Other files changed - using quick commit..."
    ./scripts/quick_commit.sh "$COMMIT_MESSAGE"
fi

echo "✅ Smart commit completed!"
