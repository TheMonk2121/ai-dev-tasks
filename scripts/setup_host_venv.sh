#!/usr/bin/env bash
set -euo pipefail

# Host venv setup for quick dev checks and lightweight tests
# This script sets up a macOS-native environment for fast feedback

echo "Setting up host venv for quick dev checks..."

# Environment vars for deterministic runs
export RAGCHECKER_BYPASS_CLI=1
export TOKENIZERS_PARALLELISM=false
export DSPY_CACHE=0
export AWS_REGION=us-east-1
# Enforce local uv environment path
export UV_PROJECT_ENVIRONMENT=.venv

# Remove existing venv to ensure clean state
if [ -d ".venv" ]; then
    echo "Removing existing .venv..."
    rm -rf .venv
fi

echo "Installing dependencies with uv (target: $UV_PROJECT_ENVIRONMENT)..."
uv sync --all-extras --dev

echo "Downloading spaCy model (if network available)..."
uv run python -m spacy download en_core_web_sm || echo "spaCy model download failed, continuing..."

echo "Host venv setup complete!"
echo ""
echo "Quick gate tests you can run:"
echo "  uv run pytest -q tests/test_schema_roundtrip.py"
echo "  uv run pytest -q tests/test_doc_coherence_validator.py" 
echo "  uv run pytest -q tests/test_coder_role.py"
echo ""
echo "Full suite (may have torch issues on macOS):"
echo "  uv run pytest -q"
echo ""
echo "For reliable full suite, use container:"
echo "  ./scripts/setup_container_venv.sh"
echo "  ./scripts/docker_pytest.sh"
