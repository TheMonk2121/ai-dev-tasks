#!/bin/bash
# Legacy model reference guard (active)
# Blocks commits that introduce references to legacy local model tools in active paths
set -euo pipefail

# Get staged files
STAGED=$(git diff --cached --name-only --diff-filter=ACM || true)
if [[ -z "$STAGED" ]]; then
  exit 0
fi

# Restrict to text files we care about
FILES=$(echo "$STAGED" | grep -Ev '^(docs/legacy/|600_archives/)' || true)
if [[ -z "$FILES" ]]; then
  exit 0
fi

# Patterns to block (case-insensitive)
BLOCK_PATTERNS='(ollama|lm[[:space:]-]?studio)'

VIOLATIONS=()
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  if grep -IinE "$BLOCK_PATTERNS" "$f" >/dev/null 2>&1; then
    VIOLATIONS+=("$f")
  fi
done <<< "$FILES"

if (( ${#VIOLATIONS[@]} > 0 )); then
  printf "\n❌ Legacy model references detected in active files:\n" >&2
  for f in "${VIOLATIONS[@]}"; do
    printf "  - %s\n" "$f" >&2
    grep -IinE "$BLOCK_PATTERNS" "$f" | sed 's/^/    > /' >&2
  done
  printf "\nMove content to docs/legacy/ or update to Cursor-native references. Commit blocked.\n" >&2
  exit 1
fi

exit 0
