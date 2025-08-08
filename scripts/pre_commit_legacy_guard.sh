#!/bin/bash

# Lightweight pre-commit guard for legacy model mentions in active docs
# Blocks commits that introduce references to legacy models in non-archived markdown files.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${1}"; }
info() { log "${YELLOW}[INFO]${NC} $1"; }
error() { log "${RED}[ERROR]${NC} $1"; }
success() { log "${GREEN}[SUCCESS]${NC} $1"; }

# Get staged markdown files (Added/Copied/Modified)
STAGED_MD=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.md$' || true)

if [[ -z "${STAGED_MD}" ]]; then
  info "No markdown files staged; skipping legacy guard"
  exit 0
fi

# Exclude archives/legacy directories
ACTIVE_MD=$(echo "${STAGED_MD}" | grep -Ev '^(600_archives/|docs/legacy/)' || true)

if [[ -z "${ACTIVE_MD}" ]]; then
  info "Only archived/legacy markdown changed; skipping legacy guard"
  exit 0
fi

BLOCK_PATTERNS='mistral|yi[ -]?coder|mixtral'

VIOLATIONS=()
while IFS= read -r file; do
  if grep -niE "${BLOCK_PATTERNS}" "$file" >/dev/null 2>&1; then
    VIOLATIONS+=("$file")
  fi
done <<< "${ACTIVE_MD}"

if (( ${#VIOLATIONS[@]} > 0 )); then
  error "Legacy model references detected in active docs:"
  for f in "${VIOLATIONS[@]}"; do
    echo "  - $f"
    # Show matching lines for context
    grep -niE "${BLOCK_PATTERNS}" "$f" | sed 's/^/    > /'
  done
  error "Commit blocked. Move content to 600_archives/ or update to Cursor-native references."
  exit 1
fi

success "No legacy references detected in active docs"
exit 0


