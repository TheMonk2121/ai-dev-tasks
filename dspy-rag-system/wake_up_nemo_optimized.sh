#!/usr/bin/env bash
set -euo pipefail

# Optimized wake script: prefer parallel startup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/wake_up_nemo.sh" --parallel "$@"
