#!/usr/bin/env bash
set -eo pipefail

# optimal_phase2_eval.sh — Minimal envs actually consumed by the official evaluator
# Focus: stable, Phase-2-style settings with conservative Bedrock caps

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Activate virtualenv if present
if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
  . "$REPO_ROOT/.venv/bin/activate"
elif [ -f "$REPO_ROOT/venv/bin/activate" ]; then
  . "$REPO_ROOT/venv/bin/activate"
fi

# Bedrock throttling caps used by scripts/ragchecker_official_evaluation.py
export USE_BEDROCK_QUEUE=${USE_BEDROCK_QUEUE:-1}
export BEDROCK_MAX_RPS=${BEDROCK_MAX_RPS:-0.15}
export BEDROCK_MAX_IN_FLIGHT=${BEDROCK_MAX_IN_FLIGHT:-1}
export BEDROCK_COOLDOWN_SEC=${BEDROCK_COOLDOWN_SEC:-30}
export BEDROCK_RETRY_BASE=${BEDROCK_RETRY_BASE:-1.8}
export BEDROCK_RETRY_MAX_SLEEP=${BEDROCK_RETRY_MAX_SLEEP:-20}

# Queue client pacing (when USE_BEDROCK_QUEUE=1)
export ASYNC_MAX_CONCURRENCY=${ASYNC_MAX_CONCURRENCY:-1}
export BEDROCK_MAX_CONCURRENCY=${BEDROCK_MAX_CONCURRENCY:-1}

# Non-queue enhanced client pacing (when USE_BEDROCK_QUEUE=0)
export BEDROCK_BASE_RPS=${BEDROCK_BASE_RPS:-0.05}

# Evidence gates honored by official evaluator
export RAGCHECKER_EVIDENCE_JACCARD=${RAGCHECKER_EVIDENCE_JACCARD:-0.07}
export RAGCHECKER_EVIDENCE_COVERAGE=${RAGCHECKER_EVIDENCE_COVERAGE:-0.20}

# Target-K selection (optional but supported)
export RAGCHECKER_EVIDENCE_KEEP_MODE=${RAGCHECKER_EVIDENCE_KEEP_MODE:-target_k}
export RAGCHECKER_SIGNAL_DELTA_WEAK=${RAGCHECKER_SIGNAL_DELTA_WEAK:-0.10}
export RAGCHECKER_SIGNAL_DELTA_STRONG=${RAGCHECKER_SIGNAL_DELTA_STRONG:-0.22}
export RAGCHECKER_TARGET_K_WEAK=${RAGCHECKER_TARGET_K_WEAK:-3}
export RAGCHECKER_TARGET_K_BASE=${RAGCHECKER_TARGET_K_BASE:-5}
export RAGCHECKER_TARGET_K_STRONG=${RAGCHECKER_TARGET_K_STRONG:-9}
export RAGCHECKER_EVIDENCE_MIN_SENT=${RAGCHECKER_EVIDENCE_MIN_SENT:-2}
export RAGCHECKER_EVIDENCE_MAX_SENT=${RAGCHECKER_EVIDENCE_MAX_SENT:-11}

# Coverage rewrite toggle (already parsed in evaluator; keep conservative)
export RAGCHECKER_COVERAGE_REWRITE=${RAGCHECKER_COVERAGE_REWRITE:-0}

# Prefer fewer JSON passes to avoid throttling
export RAGCHECKER_JSON_PROMPTS=${RAGCHECKER_JSON_PROMPTS:-0}
export RAGCHECKER_JSON_MAX_TOKENS=${RAGCHECKER_JSON_MAX_TOKENS:-200}

echo "✅ Phase-2 env applied: MAX_RPS=$BEDROCK_MAX_RPS, IN_FLIGHT=$BEDROCK_MAX_IN_FLIGHT, COOLDOWN=$BEDROCK_COOLDOWN_SEC"
echo "✅ Queue pacing: ASYNC_MAX_CONCURRENCY=$ASYNC_MAX_CONCURRENCY, BEDROCK_MAX_CONCURRENCY=$BEDROCK_MAX_CONCURRENCY"
echo "✅ JSON mode: PROMPTS=$RAGCHECKER_JSON_PROMPTS, MAX_TOKENS=$RAGCHECKER_JSON_MAX_TOKENS, COVERAGE_REWRITE=$RAGCHECKER_COVERAGE_REWRITE"
echo "✅ Evidence: JACCARD=$RAGCHECKER_EVIDENCE_JACCARD, COVERAGE=$RAGCHECKER_EVIDENCE_COVERAGE, MODE=$RAGCHECKER_EVIDENCE_KEEP_MODE"

# If executed (not sourced), run the evaluator now. If sourced, only export envs.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  exec python3 "$REPO_ROOT/scripts/ragchecker_official_evaluation.py" "$@"
else
  echo "ℹ️  Script was sourced; env loaded. Next run:"
  echo "    python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli"
fi
