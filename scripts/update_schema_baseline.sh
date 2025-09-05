#!/usr/bin/env bash
# Update Schema Baseline Script
# Use this when you make intentional schema changes and want to update the baseline

set -e

echo "🔄 Updating schema baseline..."

# Generate fresh snapshots
echo "📋 Generating fresh schema snapshots..."
python3 scripts/validate_config.py --dump-schemas

# Update baseline
echo "📝 Updating baseline..."
cp dspy-rag-system/config/database/schemas/db_schema.snapshot.json dspy-rag-system/config/database/schemas/db_schema.baseline.json

echo "✅ Schema baseline updated successfully!"
echo "💡 Don't forget to commit the updated baseline:"
echo "   git add dspy-rag-system/config/database/schemas/db_schema.baseline.json"
echo "   git commit -m 'Update schema baseline'"
