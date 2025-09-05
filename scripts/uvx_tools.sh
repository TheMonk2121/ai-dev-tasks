#!/usr/bin/env bash
# UVX Tools - One-off tool execution without installing globally
# This script demonstrates how to use UVX for various development tasks

set -e

echo "🚀 UVX Tools - One-off Tool Execution"
echo "====================================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV not found. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Function to run a tool with UVX
run_uvx_tool() {
    local tool_name="$1"
    local command="$2"
    local description="$3"

    echo ""
    echo "🔧 Running: $description"
    echo "Command: uvx $command"
    echo "----------------------------------------"

    if uvx "$command" --help > /dev/null 2>&1; then
        echo "✅ $tool_name is available via UVX"
        echo "💡 Usage: uvx $command [args]"
    else
        echo "⚠️ $tool_name may not be available or may need different arguments"
    fi
}

echo ""
echo "📋 Available UVX Tools:"
echo ""

# Code Quality Tools
run_uvx_tool "Black" "black" "Python code formatter"
run_uvx_tool "Ruff" "ruff" "Fast Python linter"
run_uvx_tool "isort" "isort" "Python import sorter"
run_uvx_tool "mypy" "mypy" "Static type checker"

# Testing Tools
run_uvx_tool "pytest" "pytest" "Python testing framework"
run_uvx_tool "coverage" "coverage" "Code coverage tool"

# Documentation Tools
run_uvx_tool "mkdocs" "mkdocs" "Static site generator for documentation"
run_uvx_tool "sphinx" "sphinx-build" "Documentation generator"

# Development Tools
run_uvx_tool "pre-commit" "pre-commit" "Git hooks framework"
run_uvx_tool "bandit" "bandit" "Security linter"
run_uvx_tool "safety" "safety" "Security vulnerability scanner"

# Package Management
run_uvx_tool "pip-tools" "pip-compile" "Dependency management tools"
run_uvx_tool "pipdeptree" "pipdeptree" "Dependency tree visualization"

echo ""
echo "🎯 Common UVX Usage Examples:"
echo ""
echo "# Format code with Black"
echo "uvx black ."
echo ""
echo "# Lint with Ruff"
echo "uvx ruff check ."
echo ""
echo "# Run tests with pytest"
echo "uvx pytest tests/"
echo ""
echo "# Check types with mypy"
echo "uvx mypy src/"
echo ""
echo "# Run pre-commit hooks"
echo "uvx pre-commit run --all-files"
echo ""
echo "# Security scan with bandit"
echo "uvx bandit -r src/"
echo ""
echo "# Generate requirements.txt from pyproject.toml"
echo "uvx pip-tools compile pyproject.toml"
echo ""

echo "💡 Benefits of UVX:"
echo "- No global package installation needed"
echo "- Always uses latest version of tools"
echo "- Isolated execution environment"
echo "- Fast tool execution"
echo ""

echo "🔗 For more information:"
echo "- UVX Documentation: https://docs.astral.sh/uv/tools/uvx/"
echo "- Available tools: https://pypi.org/"
