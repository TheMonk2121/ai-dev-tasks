#!/usr/bin/env bash
set -euo pipefail

# Simple helper to run pytest inside Linux Docker without clobbering host .venv
# - Uses UV_PROJECT_ENVIRONMENT=.venv-linux (container-only)
# - Installs uv and dependencies inside the container
# - Forwards any pytest args passed to this script

quoted_args=""
for arg in "$@"; do
  # shellcheck disable=SC2089
  quoted_args+=" "
  # shellescape each arg
  printf -v escaped '%q' "$arg"
  quoted_args+="$escaped"
done

docker run --rm -t --platform linux/amd64 \
  -e POSTGRES_DSN=mock://test \
  -e UV_PROJECT_ENVIRONMENT=.venv-linux \
  -e PYTEST_ARGS="${quoted_args:-}" \
  -v "$PWD":/work -w /work \
  python:3.12-bookworm \
  bash -lc "apt-get update -qq && apt-get install -y -qq build-essential git curl && \
            curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH=/root/.local/bin:\$PATH && \
            uv --version && uv sync --all-extras --dev && \
            eval \"uv run pytest -q \$PYTEST_ARGS\""


