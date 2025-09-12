#!/usr/bin/env bash
# Quick Scribe Update - Simple alias for triggering Scribe updates

# Default to recent changes if no message provided
if [ $# -eq 0 ]; then
    python3 scripts/trigger_scribe_update.py --recent
else
    python3 scripts/trigger_scribe_update.py --message "$*"
fi
