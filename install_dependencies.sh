#!/usr/bin/env bash
# AI Development Tasks - Dependency Installation Script
# Uses UV for fast, reliable dependency management

set -e

echo "🚀 Installing AI Development Tasks Dependencies with UV"
echo "======================================================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Source UV environment if it exists
    if [ -f "$HOME/.local/bin/env" ]; then
        # shellcheck source=/dev/null
        source "$HOME/.local/bin/env"
    fi
fi

# Create virtual environment with UV
echo "📦 Creating virtual environment with Python 3.12..."
uv venv --python 3.12

# Install dependencies using UV
echo "📥 Installing dependencies from pyproject.toml..."
uv sync

# Install development dependencies
echo "📥 Installing development dependencies..."
uv sync --extra dev

# Install subproject dependencies where pyproject exists
echo "📥 Installing DSPy RAG system dependencies (reusing root .venv)..."
if [ -d dspy-rag-system ]; then
  pushd dspy-rag-system >/dev/null
  if [ -f "pyproject.toml" ]; then
    # Reuse the repository root .venv; avoid creating a nested env
    UV_PROJECT_ENVIRONMENT=../.venv uv sync
  fi
  popd >/dev/null
fi

# Dashboard and conflict detection reference root requirements; root uv sync already covers them.
# If these subfolders gain their own pyproject.toml later, add a similar uv sync block.

# Verify installation
echo "✅ Verifying installation..."
uv run python -c "import dspy, flask, psycopg2, pytest; print('✅ Core dependencies verified')"

echo ""
echo "🎉 Installation complete!"
echo "========================="
echo "Virtual environment: ./.venv"
echo "Activate with: source .venv/bin/activate"
echo ""
echo "Available commands:"
echo "  uv run pytest dspy-rag-system/tests/    # Run DSPy tests"
echo "  uv run python dspy-rag-system/src/dashboard.py  # Start dashboard"
echo "  uv run python scripts/process_tasks.py   # Run task processor"
echo ""
echo "UV commands:"
echo "  uv run <command>     # Run any command in the environment"
echo "  uv sync              # Sync dependencies from lock file"
echo "  uv lock              # Update lock file"
