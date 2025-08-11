#!/usr/bin/env bash
set -euo pipefail

# Relaxed Validation Script
# Ignores line length violations but enforces critical structural issues

if [ $# -eq 0 ]; then
    echo "Usage: $0 <commit_message>"
    echo ""
    echo "This script runs relaxed validation that:"
    echo "  ✅ Ignores line length violations (MD013)"
    echo "  ❌ Enforces heading structure (MD001)"
    echo "  ❌ Enforces other critical markdown rules"
    echo "  ❌ Enforces documentation coherence"
    echo ""
    echo "Examples:"
    echo "  $0 'fix: update documentation'"
    echo "  $0 'feat: add new feature'"
    exit 1
fi

COMMIT_MESSAGE="$1"

echo "🔧 Relaxed validation commit..."
echo "Commit message: $COMMIT_MESSAGE"
echo ""

# Create temporary markdownlint config that ignores line length
TEMP_CONFIG=$(mktemp)
cat > "$TEMP_CONFIG" << 'EOF'
{
  "MD013": false,
  "MD001": true,
  "MD003": true,
  "MD007": true,
  "MD009": true,
  "MD010": true,
  "MD012": true,
  "MD032": true,
  "MD033": true,
  "MD040": true,
  "MD041": true,
  "MD042": true,
  "MD043": true,
  "MD044": true,
  "MD045": true,
  "MD046": true,
  "MD047": true,
  "MD048": true,
  "MD049": true,
  "MD050": true
}
EOF

echo "📋 Created temporary markdownlint config (ignoring MD013)..."
echo ""

# Stage all changes
git add .

# Run markdownlint with relaxed config
echo "🔍 Running markdownlint with relaxed rules..."
MARKDOWN_OUTPUT=$(markdownlint --config "$TEMP_CONFIG" *.md 2>/dev/null || true)
if [ -z "$MARKDOWN_OUTPUT" ]; then
    echo "✅ Markdown validation passed (relaxed rules)"
else
    echo "❌ Markdown validation failed (critical issues found)"
    echo ""
    echo "Critical issues that need fixing:"
    echo "$MARKDOWN_OUTPUT"
    echo ""
    echo "💡 These are structural issues that must be fixed before committing."
    echo "   Line length violations are ignored."
    
    # Clean up temp config
    rm "$TEMP_CONFIG"
    exit 1
fi

# Clean up temp config
rm "$TEMP_CONFIG"

# Run relaxed documentation coherence validation (ignoring line length)
echo "📚 Running relaxed documentation coherence validation..."
if python3 scripts/relaxed_validator.py --dry-run 2>/dev/null; then
    echo "✅ Relaxed documentation coherence validation passed"
else
    echo "❌ Relaxed documentation coherence validation failed"
    echo ""
    echo "💡 Critical documentation structure issues found. These must be fixed."
    echo "   Note: Line length violations are ignored."
    exit 1
fi

# Commit with relaxed validation
echo "🚀 Committing with relaxed validation..."
git commit -m "$COMMIT_MESSAGE"

echo "✅ Relaxed validation commit successful!"
echo ""
echo "Note: Line length violations were ignored, but structural issues were enforced."
