#!/usr/bin/env bash
set -euo pipefail
# Mock evaluation profile - infra-only, synthetic by design
uv run python scripts/ragchecker_official_evaluation.py --profile mock "$@"
