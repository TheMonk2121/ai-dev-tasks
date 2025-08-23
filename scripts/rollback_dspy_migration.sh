#!/bin/bash

# DSPy Migration Rollback Script
# Usage: ./scripts/rollback_dspy_migration.sh

set -e

echo "🔄 Starting DSPy migration rollback..."

# Check if we're on the migration branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "dspy-3.0-migration" ]; then
    echo "❌ Error: Not on dspy-3.0-migration branch"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Revert to DSPy 2.6.27 in requirements.txt
echo "📦 Reverting DSPy version to 2.6.27..."
sed -i '' 's/dspy==3.0.1/dspy==2.6.27/g' requirements.txt
sed -i '' 's/dspy==3.0.2/dspy==2.6.27/g' requirements.txt

# Reinstall requirements
echo "🔧 Reinstalling requirements..."
source venv/bin/activate
pip install -r requirements.txt

# Verify DSPy version
echo "✅ Verifying DSPy version..."
python3 -c "import dspy; print(f'DSPy version: {dspy.__version__}')"

# Run smoke tests
echo "🧪 Running smoke tests..."
pytest tests/ -v --tb=short | tail -10

echo "✅ Rollback completed successfully!"
echo "📝 Next steps:"
echo "   - Review test results"
echo "   - Check if system is stable"
echo "   - Consider investigating migration issues"
