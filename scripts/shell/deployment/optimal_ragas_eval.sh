#!/usr/bin/env bash
set -eo pipefail

# optimal_ragas_eval.sh — Wrapper for production RAGAS pipeline knobs used by run_production_ragas.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
  . "$REPO_ROOT/.venv/bin/activate"
elif [ -f "$REPO_ROOT/venv/bin/activate" ]; then
  . "$REPO_ROOT/venv/bin/activate"
fi

# Optionally load a precision/recall env file produced by precision_push_final_config.py
PRECISION_ENV_FILE=${PRECISION_ENV_FILE:-"$REPO_ROOT/300_evals/configs/precision_push.env"}
if [ -f "$PRECISION_ENV_FILE" ]; then
  echo "🔧 Loading precision env file: $PRECISION_ENV_FILE"
  # Export all keys from the file safely
  set -a
  # shellcheck disable=SC1090
  . "$PRECISION_ENV_FILE"
  set +a
fi

# Bedrock caps (safe defaults)
export BEDROCK_MAX_RPS=${BEDROCK_MAX_RPS:-0.3}
export BEDROCK_MAX_IN_FLIGHT=${BEDROCK_MAX_IN_FLIGHT:-1}
export BEDROCK_COOLDOWN_SEC=${BEDROCK_COOLDOWN_SEC:-8}
export BEDROCK_RETRY_BASE=${BEDROCK_RETRY_BASE:-1.6}
export BEDROCK_RETRY_MAX_SLEEP=${BEDROCK_RETRY_MAX_SLEEP:-12}

# Fusion / anchors / facets
export RAGCHECKER_RRF_K=${RAGCHECKER_RRF_K:-50}
export RAGCHECKER_BM25_BOOST_ANCHORS=${RAGCHECKER_BM25_BOOST_ANCHORS:-1.8}
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR=${RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR:-0.75}

# Selection gates
export RAGCHECKER_EVIDENCE_JACCARD=${RAGCHECKER_EVIDENCE_JACCARD:-0.07}
export RAGCHECKER_EVIDENCE_COVERAGE=${RAGCHECKER_EVIDENCE_COVERAGE:-0.20}
export RAGCHECKER_EVIDENCE_KEEP_MODE=${RAGCHECKER_EVIDENCE_KEEP_MODE:-target_k}
export RAGCHECKER_TARGET_K_STRONG=${RAGCHECKER_TARGET_K_STRONG:-9}

# Cross-encoder / NLI
export RAGCHECKER_CE_WEIGHT=${RAGCHECKER_CE_WEIGHT:-0.16}
export RAGCHECKER_NLI_P_THRESHOLD=${RAGCHECKER_NLI_P_THRESHOLD:-0.62}
export RAGCHECKER_BORDERLINE_BAND=${RAGCHECKER_BORDERLINE_BAND:-0.02}

echo "✅ RAGAS env applied: RRF_K=$RAGCHECKER_RRF_K, ANCHOR_BOOST=$RAGCHECKER_BM25_BOOST_ANCHORS, FACET_DOWN=$RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR"
echo "✅ CE/NLI: CE_WEIGHT=$RAGCHECKER_CE_WEIGHT, NLI_P=$RAGCHECKER_NLI_P_THRESHOLD, BAND=$RAGCHECKER_BORDERLINE_BAND"

exec bash "$REPO_ROOT/scripts/run_production_ragas.sh" "$@"
