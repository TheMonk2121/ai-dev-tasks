#!/usr/bin/env bash
# Preflight Environment Diff
# Compares current shell env against a selected profile and reports differences.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/preflight_env_diff.sh --env-file configs/stable_bedrock.env
  bash scripts/preflight_env_diff.sh --script throttle_free_eval.sh
  bash scripts/preflight_env_diff.sh --profile stable
  bash scripts/preflight_env_diff.sh --profile throttle

Notes:
  - This script is read-only: it does not modify your environment.
  - "--script throttle_free_eval.sh" loads stable env then strict overrides.
EOF
}

# Default
mode=""
target=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-file)
      mode="env-file"; target="${2:-}"; shift 2 ;;
    --script)
      mode="script"; target="${2:-}"; shift 2 ;;
    --profile)
      mode="profile"; target="${2:-}"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$mode" ]]; then
  usage; exit 1
fi

# Resolve profile → actual file
case "$mode:$target" in
  profile:stable)
    mode="env-file"; target="configs/stable_bedrock.env" ;;
  profile:throttle)
    mode="script"; target="throttle_free_eval.sh" ;;
esac

if [[ ! -f "$target" ]]; then
  echo "❌ Target not found: $target" >&2
  exit 1
fi

# Keys to compare (cover both legacy and standardized names)
keys=(
  ASYNC_MAX_CONCURRENCY
  USE_BEDROCK_QUEUE
  BEDROCK_ENABLE_QUEUE
  BEDROCK_MAX_IN_FLIGHT
  BEDROCK_MAX_CONCURRENCY
  BEDROCK_MAX_RPS
  BEDROCK_COOLDOWN_SEC
  BEDROCK_MAX_RETRIES
  BEDROCK_RETRY_MAX
  BEDROCK_BASE_BACKOFF
  BEDROCK_RETRY_BASE
  BEDROCK_MAX_BACKOFF
  BEDROCK_RETRY_MAX_SLEEP
  RAGCHECKER_JSON_PROMPTS
  RAGCHECKER_COVERAGE_REWRITE
  RAGCHECKER_EVIDENCE_JACCARD
  RAGCHECKER_EVIDENCE_COVERAGE
  BEDROCK_MODEL_ID
  AWS_REGION
)

# Capture current env values
declare -A CURRENT
for k in "${keys[@]}"; do
  CURRENT[$k]="${!k-}"
done

# Function to print selected keys from a subshell after sourcing a file
subshell_dump() {
  local file="$1"
  local is_script="$2"  # "1" for script, "0" for env-file
  local joined_keys
  joined_keys=$(printf '%s ' "${keys[@]}")
  if [[ "$is_script" == "1" ]]; then
    bash -lc "set -a; source '$file'; for k in $joined_keys; do printf '%s=%s\n' \"\$k\" \"\${!k-}\"; done"
  else
    bash -lc "set -a; source '$file'; for k in $joined_keys; do printf '%s=%s\n' \"\$k\" \"\${!k-}\"; done"
  fi
}

echo "🔍 Preflight Env Diff"
echo "Target: $mode → $target"
echo "------------------------------------------------------------"

# Dump profile values
profile_dump=$(subshell_dump "$target" "$([[ "$mode" == "script" ]] && echo 1 || echo 0)")

declare -A PROFILE
while IFS='=' read -r k v; do
  [[ -z "$k" ]] && continue
  PROFILE[$k]="$v"
done <<< "$profile_dump"

# Report
diff_count=0
same_count=0

printf "%-28s | %-20s | %-20s\n" "Key" "Current" "Profile"
printf "%-28s-+-%-20s-+-%-20s\n" "----------------------------" "--------------------" "--------------------"
for k in "${keys[@]}"; do
  cur="${CURRENT[$k]}"
  prof="${PROFILE[$k]-}"
  if [[ "$cur" == "$prof" ]]; then
    ((same_count++))
    printf "%-28s | %-20s | %-20s\n" "$k" "${cur:-<unset>}" "${prof:-<unset>}"
  else
    ((diff_count++))
    printf "%-28s | %-20s | %-20s\n" "$k" "${cur:-<unset>}" "${prof:-<unset>}"
  fi
done

echo "------------------------------------------------------------"
echo "✅ Matches: $same_count  ⚠️  Diffs: $diff_count"

if [[ $diff_count -gt 0 ]]; then
  echo "💡 Tip: For hermetic runs, use: ./scripts/run_hermetic_eval.sh"
fi

