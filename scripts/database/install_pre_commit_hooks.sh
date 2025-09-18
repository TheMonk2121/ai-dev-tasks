#!/bin/bash
# Install Pre-commit Hooks for Database Schema Management
#
# This script installs pre-commit hooks that will:
# 1. Check for schema drift between repo and database
# 2. Validate migration file format
# 3. Warn about database changes that need migrations

set -e

echo "🔧 Installing pre-commit hooks for database schema management..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "❌ pre-commit not found. Installing..."
    uv add --dev pre-commit
fi

# Install the hooks
echo "📋 Installing pre-commit hooks..."
pre-commit install

# Test the installation
echo "🧪 Testing pre-commit hooks..."
pre-commit run --all-files --hook-stage manual database-pre-commit || true

echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "📋 What this does:"
echo "   • Checks for schema drift before commits"
echo "   • Validates migration file format"
echo "   • Warns about database changes that need migrations"
echo ""
echo "🔧 Commands:"
echo "   • Run all hooks: pre-commit run --all-files"
echo "   • Run database hook only: pre-commit run database-pre-commit"
echo "   • Bypass hooks: git commit --no-verify"
echo ""
echo "⚠️  Note: The database hook will warn if your database is out of sync"
echo "   but won't block commits. You can always bypass with --no-verify."
