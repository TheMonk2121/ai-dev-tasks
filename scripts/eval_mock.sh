#!/usr/bin/env bash
set -euo pipefail
# Mock evaluation profile - infra-only, synthetic by design
python3 scripts/ragchecker_official_evaluation.py --profile mock "$@"
