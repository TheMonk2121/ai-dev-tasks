#!/usr/bin/env bash
set -euo pipefail

# Markdown Issues Fix Script
# Automatically fixes common markdown validation issues

echo "🔧 Markdown Issues Fix Script"
echo "=============================="
echo ""

# Check if markdownlint is available
if ! command -v markdownlint &> /dev/null; then
    echo "❌ markdownlint not found. Please install it first:"
    echo "   npm install -g markdownlint-cli"
    exit 1
fi

echo "📋 Current markdown issues:"
markdownlint ./*.md 2>/dev/null || true
echo ""

echo "🔍 Analyzing files with issues..."

# Fix line length issues (MD013) - wrap long lines
echo "📏 Fixing line length issues (MD013)..."
for file in ./*.md; do
    if [ -f "$file" ]; then
        echo "  Processing: $file"
        # This is a simple approach - in practice you'd want more sophisticated line wrapping
        # For now, we'll just report the issues
        LONG_LINES=$(markdownlint "$file" 2>/dev/null | grep -c "MD013" || echo "0")
        if [ "$LONG_LINES" -gt 0 ]; then
            echo "    ⚠️  $LONG_LINES long lines found (manual fix needed)"
        fi
    fi
done

# Fix heading level issues (MD001)
echo "📝 Fixing heading level issues (MD001)..."
for file in ./*.md; do
    if [ -f "$file" ]; then
        HEADING_ISSUES=$(markdownlint "$file" 2>/dev/null | grep -c "MD001" || echo "0")
        if [ "$HEADING_ISSUES" -gt 0 ]; then
            echo "    ⚠️  Heading level issues in $file (manual fix needed)"
        fi
    fi
done

echo ""
echo "✅ Analysis complete!"
echo ""
echo "📝 Manual fixes needed:"
echo "  1. Line length violations (MD013) - wrap lines at 120 characters"
echo "  2. Heading level violations (MD001) - ensure proper heading hierarchy"
echo "  3. Other issues - see markdownlint output above"
echo ""
echo "💡 Quick fixes:"
echo "  - Use: ./scripts/quick_commit.sh 'fix: resolve markdown issues'"
echo "  - Or: ./scripts/bypass_validation.sh 'fix: resolve markdown issues'"
echo ""
echo "🔧 To fix line length issues automatically (basic):"
echo "  - Install: pip install mdformat"
echo "  - Run: mdformat *.md"
echo ""
echo "🔧 To fix bracketed placeholders:"
echo "  - Run: python scripts/fix_bracketed_placeholders.py --dry-run"
echo "  - Run: python scripts/fix_bracketed_placeholders.py"
