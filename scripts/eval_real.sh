#!/usr/bin/env bash
set -euo pipefail
# Real evaluation profile - baseline/tuning on real RAG
uv run python scripts/ragchecker_official_evaluation.py --profile real "$@"
