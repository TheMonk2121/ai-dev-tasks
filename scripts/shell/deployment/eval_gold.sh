#!/usr/bin/env bash
set -euo pipefail
# Gold evaluation profile - real RAG + gold cases
uv run python scripts/ragchecker_official_evaluation.py --profile gold "$@"
