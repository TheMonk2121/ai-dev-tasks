#!/usr/bin/env bash

# Check for duplicate numeric prefixes in HIGH priority files
# HIGH ranges: 000-099 (core workflow), 400-499 (documentation), 500-599 (testing)

echo "🔍 Checking for duplicate numeric prefixes in HIGH priority files..."

# Find all markdown files with numeric prefixes
files=$(find . -name "*.md" -not -path "./backup_before_migration/*" | grep -E "^\./[0-9]+_" | sort)

# Extract prefixes and check for duplicates
prefixes=$(echo "$files" | grep -oE '^\./[0-9]+' | sort | uniq -d)

if [ ! -z "$prefixes" ]; then
    echo "⚠️  WARNING: Duplicate numeric prefixes found:"
    echo "$prefixes" | while read prefix; do
        echo "   $prefix"
        # Show which files have this prefix
        echo "$files" | grep "^$prefix" | sed 's/^\.\//     /'
    done
    echo ""
else
    echo "✅ No duplicate numeric prefixes found"
fi

# Check for files that should be three-digit but aren't
echo "🔍 Checking for files that should use three-digit prefixes..."
two_digit_files=$(find . -name "*.md" -not -path "./backup_before_migration/*" | grep -E "^\./[0-9]{1,2}_" | sort)

if [ ! -z "$two_digit_files" ]; then
    echo "📝 Files that should be renamed to three-digit prefixes:"
    echo "$two_digit_files" | sed 's/^\.\//   /'
    echo ""
fi

# Always exit successfully (warning only, doesn't block commit)
exit 0 
