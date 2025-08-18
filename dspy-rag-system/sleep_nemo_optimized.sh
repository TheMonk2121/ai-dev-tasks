#!/usr/bin/env bash
set -euo pipefail

# Optimized sleep script: prefer fast shutdown
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/sleep_nemo.sh" --fast "$@"
