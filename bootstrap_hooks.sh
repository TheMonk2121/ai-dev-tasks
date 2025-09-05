#!/usr/bin/env bash
# Bootstrap script for git hooks setup
# Ensures all team members have consistent hook configuration

set -euo pipefail

echo "🔧 Bootstrapping Git Hooks"
echo "=========================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Set git to use versioned hooks
echo "📁 Setting git hooksPath to .githooks/"
git config core.hooksPath .githooks

# Check if .githooks directory exists
if [ ! -d ".githooks" ]; then
    echo "❌ Error: .githooks/ directory not found"
    echo "   Make sure you're in the project root and hooks are committed"
    exit 1
fi

# Set executable permissions
echo "🔐 Setting executable permissions"
chmod +x .githooks/*

# Install pre-commit hooks
echo "⚙️  Installing pre-commit hooks"
if command -v pre-commit > /dev/null 2>&1; then
    pre-commit install --hook-type pre-commit --hook-type commit-msg -f
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  Warning: pre-commit not found, skipping pre-commit installation"
    echo "   Install with: pip install pre-commit"
fi

# Verify setup
echo "🧪 Verifying setup"
if [ "$(git config core.hooksPath)" = ".githooks" ]; then
    echo "✅ Git hooksPath configured correctly"
else
    echo "❌ Error: Git hooksPath not set correctly"
    exit 1
fi

if [ -x ".githooks/pre-commit" ]; then
    echo "✅ Pre-commit hook is executable"
else
    echo "❌ Error: Pre-commit hook not executable"
    exit 1
fi

echo ""
echo "🎉 Git hooks bootstrap complete!"
echo ""
echo "📋 What was configured:"
echo "   • Git hooksPath: .githooks/"
echo "   • Executable permissions: Set"
echo "   • Pre-commit hooks: Installed"
echo ""
echo "🔍 To verify hooks are working:"
echo "   git commit --allow-empty -m 'test: verify hooks'"
echo ""
echo "📚 For more information, see .githooks/README.md"
