#!/usr/bin/env bash
set -euo pipefail

# Cached Docker pytest runner with persistent venv
# - Uses a persistent .venv-linux directory for caching
# - Only reinstalls if pyproject.toml or uv.lock changes
# - Much faster for repeated runs

quoted_args=""
for arg in "$@"; do
  # shellcheck disable=SC2089
  quoted_args+=" "
  # shellescape each arg
  printf -v escaped '%q' "$arg"
  quoted_args+="$escaped"
done

# Check if we need to rebuild the venv
NEED_REBUILD=false
if [ ! -d ".venv-linux" ]; then
    echo "No cached venv found, will install..."
    NEED_REBUILD=true
elif [ "pyproject.toml" -nt ".venv-linux/.last-sync" ] || [ "uv.lock" -nt ".venv-linux/.last-sync" ]; then
    echo "Dependencies changed, will reinstall..."
    NEED_REBUILD=true
else
    echo "Using cached venv..."
fi

if [ "$NEED_REBUILD" = true ]; then
    echo "Installing/updating dependencies in container..."
    docker run --rm -t --platform linux/amd64 \
      -e POSTGRES_DSN=mock://test \
      -e RAGCHECKER_BYPASS_CLI=1 \
      -e TOKENIZERS_PARALLELISM=false \
      -e DSPY_CACHE=0 \
      -e AWS_REGION=us-east-1 \
      -e UV_PROJECT_ENVIRONMENT=.venv-linux \
      -v "$PWD":/work -w /work \
      python:3.12-bookworm \
      bash -lc "apt-get update -qq && apt-get install -y -qq build-essential git curl && \
                curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH=/root/.local/bin:\$PATH && \
                uv --version && uv sync --all-extras --dev && \
                touch .venv-linux/.last-sync"
fi

echo "Running tests with cached venv..."
docker run --rm -t --platform linux/amd64 \
  -e POSTGRES_DSN=mock://test \
  -e RAGCHECKER_BYPASS_CLI=1 \
  -e TOKENIZERS_PARALLELISM=false \
  -e DSPY_CACHE=0 \
  -e AWS_REGION=us-east-1 \
  -e UV_PROJECT_ENVIRONMENT=.venv-linux \
  -e PYTEST_ARGS="${quoted_args:-}" \
  -v "$PWD":/work -w /work \
  python:3.12-bookworm \
  bash -lc \
  ". .venv-linux/bin/activate && pytest -q \"$PYTEST_ARGS\""
