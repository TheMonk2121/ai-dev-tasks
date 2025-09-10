#!/usr/bin/env bash

# RAGAS-Competitive Evaluation Runner
# Implements LIMIT features to achieve RAGAS-competitive performance

set -e

echo "🎯 RAGAS-Competitive Evaluation with LIMIT Features"
echo "=================================================="

# Activate virtual environment (prefer .venv, then venv)
VENV_DIR="${VENV_DIR:-.venv}"
if [ -f "$VENV_DIR/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$VENV_DIR/bin/activate"
elif [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "venv/bin/activate"
else
  echo "⚠️  No virtualenv found at .venv/ or venv/. Continuing without activation." >&2
fi

# Set RAGAS-competitive environment variables
echo "🔧 Setting RAGAS-competitive configuration..."

# Geometry Router Configuration
export RAGCHECKER_ROUTE_BM25_MARGIN="0.20"
export RAGCHECKER_REWRITE_AGREE_STRONG="0.50"

# Facet Selection Configuration
export RAGCHECKER_REWRITE_K="4"
export RAGCHECKER_REWRITE_KEEP="2"
export RAGCHECKER_REWRITE_YIELD_MIN="1.5"

# Hybrid Retrieval Configuration
export RAGCHECKER_USE_RRF="1"
export RAGCHECKER_USE_MMR="1"
export RAGCHECKER_MMR_LAMBDA="0.65"
export RAGCHECKER_CONTEXT_TOPK="14"
export RAGCHECKER_PER_DOC_LINE_CAP="8"
export RAGCHECKER_LONG_TAIL_SLOT="1"

# Boolean Logic Configuration
export RAGCHECKER_BM25_BOOST_ANCHORS="1.6"
export RAGCHECKER_ENABLE_BOOLEAN_LOGIC="1"

# Precision Lift Pack Configuration
export RAGCHECKER_EVIDENCE_JACCARD="0.07"
export RAGCHECKER_EVIDENCE_COVERAGE="0.20"
export RAGCHECKER_SUPPORT_TWO_OF_THREE="1"
export RAGCHECKER_NUMERIC_MUST_MATCH="1"
export RAGCHECKER_ENTITY_MUST_MATCH="1"
export RAGCHECKER_PENALTY_NUM_MISMATCH="0.15"
export RAGCHECKER_PENALTY_UNBACKED_NEG="0.08"

# Anti-Redundancy Configuration
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX="0.40"
export RAGCHECKER_PER_CHUNK_CAP="1"
export RAGCHECKER_UNIQUE_ANCHOR_MIN="1"

# Claim Binding Configuration
export RAGCHECKER_CLAIM_TOPK="2"
export RAGCHECKER_CLAIM_TOPK_STRONG="3"
export RAGCHECKER_MIN_WORDS_AFTER_BINDING="160"
export RAGCHECKER_DROP_UNSUPPORTED="0"

# Facet Influence Configuration
export RAGCHECKER_RRF_K="60"
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR="0.80"
export RAGCHECKER_REWRITE_YIELD_MIN="1.5"

# Additional Precision Gates
export RAGCHECKER_STRICT_SEMANTIC_MATCH="1"
export RAGCHECKER_REQUIRE_QUERY_ANCHORS="1"
export RAGCHECKER_PENALTY_WEAK_SUPPORT="0.10"
export RAGCHECKER_MAX_SENTENCE_LENGTH="200"

# Judge Configuration
export RAGCHECKER_JUDGE_MODE="haiku"
export RAGCHECKER_HAIKU_FLOORS="1"
export RAGCHECKER_FINAL_PRECISION_PUSH="1"
export RAGCHECKER_AGGRESSIVE_MODE="1"

# Chunking Configuration
export RAGCHECKER_CHUNK_TOK="160"
export RAGCHECKER_CHUNK_OVERLAP="40"
export RAGCHECKER_ENTITY_SNIPPETS="0"

# Faithfulness Configuration
export RAGCHECKER_FAITHFULNESS_REPORTING="1"

echo "✅ Configuration applied successfully"
echo ""

# Run RAGAS-competitive evaluation
echo "🚀 Running RAGAS-Competitive Evaluation..."
echo ""

bin/py scripts/ragchecker_ragas_competitive_evaluation.py \
    --output "metrics/ragas_competitive_evaluation_$(date +%Y%m%d_%H%M%S).json" \
    --test-cases 15

# Check exit code
EXIT_CODE=$?

echo ""
echo "📊 Evaluation completed with exit code: $EXIT_CODE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 RAGAS-COMPETITIVE PERFORMANCE ACHIEVED!"
    echo "   All targets met - system is production ready"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "📈 Floor A passed - approaching RAGAS-competitive performance"
    echo "   System is close to production ready"
else
    echo "⚠️ Below Floor A - more optimization needed"
    echo "   System needs further improvement"
fi

echo ""
echo "🔍 Check the output file for detailed results and metrics"
echo "📈 Review promotion gate status for next steps"

exit $EXIT_CODE
