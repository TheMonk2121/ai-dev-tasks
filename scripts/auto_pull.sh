#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/danieljacobs/Code/ai-dev-tasks"
LOG="$REPO/.git/autopull.log"

cd "$REPO"

# Ensure clean working tree (no staged or unstaged changes)
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "$(date '+%Y-%m-%dT%H:%M:%S%z') skipped: uncommitted changes" >> "$LOG"
  exit 0
fi

# Fetch latest refs
git fetch origin --prune

CURRENT_BRANCH=$(git branch --show-current)

# Compute ahead/behind
STATUS=$(git rev-list --left-right --count "HEAD...origin/$CURRENT_BRANCH" || echo "0 0")
AHEAD=$(echo "$STATUS" | awk '{print $1}')
BEHIND=$(echo "$STATUS" | awk '{print $2}')

if [ "${BEHIND}" -gt 0 ] && [ "${AHEAD}" -eq 0 ]; then
  if git pull --ff-only --prune; then
    echo "$(date '+%Y-%m-%dT%H:%M:%S%z') pulled: ${BEHIND} new commit(s) on ${CURRENT_BRANCH}" >> "$LOG"
    # Post-pull syncs (best-effort)
    if command -v python3 >/dev/null 2>&1; then
      (python3 scripts/update_cursor_memory.py || true) >> "$LOG" 2>&1
    fi
  else
    echo "$(date '+%Y-%m-%dT%H:%M:%S%z') pull failed (non-ff or error) on ${CURRENT_BRANCH}" >> "$LOG"
  fi
else
  echo "$(date '+%Y-%m-%dT%H:%M:%S%z') no-ff pull (ahead=${AHEAD} behind=${BEHIND}) on ${CURRENT_BRANCH}, skipped" >> "$LOG"
fi
