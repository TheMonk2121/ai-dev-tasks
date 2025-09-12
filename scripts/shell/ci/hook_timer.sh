#!/usr/bin/env bash
# Usage: hook_timer.sh <command> [args...]
# Runs the given command, prints its duration, and exits with the command's status.

start_ts=$(date +%s)
"$@"
status=$?
end_ts=$(date +%s)

dur=$(( end_ts - start_ts ))
cmd_name=$1
# Trim path if present
cmd_base=${cmd_name##*/}

echo "[hook:${cmd_base}] duration=${dur}s status=${status}"
exit ${status}
