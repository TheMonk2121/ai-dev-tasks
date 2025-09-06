#!/usr/bin/env bash
# Locked, reproducible RAGChecker evaluation runner
# - Creates per-run timestamped artifacts (logs, env)
# - Enforces stable config and safe guard
# - Hints for checkpoint commits to avoid losing results

set -euo pipefail

RUN_TS="${RUN_TS:-$(date +%Y%m%d-%H%M%S)}"
OUT_DIR="metrics/baseline_evaluations"
mkdir -p "$OUT_DIR"

echo "🚀 Locked RAGChecker run: $RUN_TS"

# Load canonical throttle-free baseline (will source configs/stable_bedrock.env)
if [[ -f "throttle_free_eval.sh" ]]; then
  # shellcheck source=/dev/null
  source throttle_free_eval.sh
else
  echo "⚠️ throttle_free_eval.sh not found; continuing with current env"
fi

# Enforce safe guard unless explicitly disabled
export RAGCHECKER_DISABLE_SAFE_GUARD="${RAGCHECKER_DISABLE_SAFE_GUARD:-0}"

# Select Python via UV or project venv, then fallback
if command -v uv >/dev/null 2>&1; then
  PY_RUN=(uv run python)
  echo "🧪 Using UV environment via 'uv run'"
elif [[ -x ".venv/bin/python" ]]; then
  PY_RUN=(".venv/bin/python")
  echo "🧪 Using project venv: .venv/bin/python"
elif [[ -x "venv/bin/python" ]]; then
  PY_RUN=("venv/bin/python")
  echo "🧪 Using project venv: venv/bin/python"
else
  PY_RUN=(python3)
  echo "🧪 Using system Python (fallback)"
fi

# Progress log and main log
PROGRESS_FILE="$OUT_DIR/progress-$RUN_TS.jl"
MAIN_LOG="$OUT_DIR/log-$RUN_TS.txt"
ENV_SNAPSHOT="$OUT_DIR/env-$RUN_TS.env"

# Snapshot relevant env
env | grep -E '^(RAGCHECKER_|BEDROCK_|AWS_REGION|USE_BEDROCK_QUEUE)=' | sort > "$ENV_SNAPSHOT" || true
echo "💾 Env snapshot: $ENV_SNAPSHOT"

echo "📜 Tailing output to: $MAIN_LOG"
set -o pipefail
RAGCHECKER_PROGRESS_LOG="$PROGRESS_FILE" "${PY_RUN[@]}" scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable "$@" 2>&1 | tee "$MAIN_LOG"
set +o pipefail

echo "✅ Run complete. Artifacts:"
echo "  • $MAIN_LOG"
echo "  • $PROGRESS_FILE"
echo "  • $ENV_SNAPSHOT"

echo "💡 Tip: checkpoint results to avoid loss:"
echo "   git add $OUT_DIR/*-$RUN_TS.* && scripts/commit_without_cursor.sh \"chore(eval): checkpoint RAGChecker $RUN_TS\""
