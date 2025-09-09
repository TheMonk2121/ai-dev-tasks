#!/usr/bin/env bash
set -euo pipefail

# Container venv setup for full test suite (Linux wheels for torch, psycopg2, etc.)
# This script sets up a Linux container environment with all dependencies

echo "Setting up container venv for full test suite..."

# Environment vars for deterministic, non-networked runs
export RAGCHECKER_BYPASS_CLI=1
export TOKENIZERS_PARALLELISM=false
export DSPY_CACHE=0
export AWS_REGION=us-east-1

# Run in Docker with separate venv
docker run --rm -t --platform linux/amd64 \
  -e POSTGRES_DSN=mock://test \
  -e RAGCHECKER_BYPASS_CLI=1 \
  -e TOKENIZERS_PARALLELISM=false \
  -e DSPY_CACHE=0 \
  -e AWS_REGION=us-east-1 \
  -e UV_PROJECT_ENVIRONMENT=.venv-linux \
  -v "$PWD":/work -w /work \
  python:3.12-bookworm \
  bash -lc "
    echo 'Installing system dependencies...'
    apt-get update -qq && apt-get install -y -qq build-essential git curl
    
    echo 'Installing uv...'
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH=/root/.local/bin:\$PATH
    
    echo 'Installing Python dependencies...'
    uv sync --all-extras --dev
    
    echo 'Downloading spaCy model (if network available)...'
    python -m spacy download en_core_web_sm || echo 'spaCy model download failed, continuing...'
    
    echo 'Container venv setup complete!'
    echo 'To run tests: ./scripts/docker_pytest.sh [test_files...]'
  "

echo "Container venv setup complete!"
