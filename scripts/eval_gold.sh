#!/usr/bin/env bash
set -euo pipefail
# Gold evaluation profile - real RAG + gold cases
python3 scripts/ragchecker_official_evaluation.py --profile gold "$@"
