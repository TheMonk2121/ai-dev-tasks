#!/bin/bash

# Precision Optimization Evaluation Runner
# Fine-tunes LIMIT features to achieve precision target of 0.20

set -e

echo "🎯 Precision Optimization Evaluation"
echo "===================================="

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
else
    echo "❌ Virtual environment not found at venv/bin/activate"
    echo "   Please ensure you're running this script from the project root"
    exit 1
fi

# Set precision-optimized environment variables
echo "🔧 Setting precision-optimized configuration..."

# Aggressive precision tightening
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX="0.35"
export RAGCHECKER_PER_CHUNK_CAP="1"
export RAGCHECKER_EVIDENCE_JACCARD="0.08"
export RAGCHECKER_EVIDENCE_COVERAGE="0.22"
export RAGCHECKER_PENALTY_NUM_MISMATCH="0.18"

# Stricter claim binding
export RAGCHECKER_CLAIM_TOPK="1"
export RAGCHECKER_CLAIM_TOPK_STRONG="2"
export RAGCHECKER_MIN_WORDS_AFTER_BINDING="180"

# More aggressive facet filtering
export RAGCHECKER_REWRITE_YIELD_MIN="1.8"
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR="0.70"
export RAGCHECKER_RRF_K="50"
export RAGCHECKER_BM25_BOOST_ANCHORS="1.8"
export RAGCHECKER_CONTEXT_TOPK="12"

# Additional precision gates
export RAGCHECKER_STRICT_SEMANTIC_MATCH="1"
export RAGCHECKER_REQUIRE_QUERY_ANCHORS="1"
export RAGCHECKER_PENALTY_WEAK_SUPPORT="0.15"
export RAGCHECKER_MAX_SENTENCE_LENGTH="150"

# Precision-focused support validation
export RAGCHECKER_SUPPORT_TWO_OF_THREE="1"
export RAGCHECKER_NUMERIC_MUST_MATCH="1"
export RAGCHECKER_ENTITY_MUST_MATCH="1"
export RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC="2"
export RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY="2"

# Stricter geometry routing
export RAGCHECKER_ROUTE_BM25_MARGIN="0.25"
export RAGCHECKER_REWRITE_AGREE_STRONG="0.60"

# Precision-focused facet selection
export RAGCHECKER_REWRITE_K="3"
export RAGCHECKER_REWRITE_KEEP="1"

# Precision-focused MMR
export RAGCHECKER_MMR_LAMBDA="0.75"

# Precision-focused per-doc cap
export RAGCHECKER_PER_DOC_LINE_CAP="6"

# Precision-focused chunking
export RAGCHECKER_CHUNK_TOK="140"
export RAGCHECKER_CHUNK_OVERLAP="30"

# Precision-focused target K
export RAGCHECKER_TARGET_K_STRONG="6"

# Precision-focused long tail
export RAGCHECKER_LONG_TAIL_SLOT="0"

# Other required settings
export RAGCHECKER_USE_RRF="1"
export RAGCHECKER_USE_MMR="1"
export RAGCHECKER_LONG_TAIL_SLOT="0"
export RAGCHECKER_CHUNK_TOK="140"
export RAGCHECKER_CHUNK_OVERLAP="30"
export RAGCHECKER_ENTITY_SNIPPETS="0"
export RAGCHECKER_ENABLE_BOOLEAN_LOGIC="1"
export RAGCHECKER_UNIQUE_ANCHOR_MIN="1"
export RAGCHECKER_DROP_UNSUPPORTED="0"
export RAGCHECKER_JUDGE_MODE="haiku"
export RAGCHECKER_HAIKU_FLOORS="1"
export RAGCHECKER_FAITHFULNESS_REPORTING="1"
export RAGCHECKER_FINAL_PRECISION_PUSH="1"
export RAGCHECKER_AGGRESSIVE_MODE="1"

echo "✅ Precision-optimized configuration applied successfully"
echo ""

# Test single query first
echo "🧪 Testing precision optimization on single query..."
python3 scripts/ragchecker_precision_optimization.py \
    --test-query "DSPy integration patterns" \
    --output "test_precision_optimization.json"

echo ""
echo "📊 Single query test completed. Check results above."
echo ""

# Run full evaluation if single query shows promise
echo "🚀 Running full precision optimization evaluation..."
python3 scripts/ragchecker_ragas_competitive_evaluation.py \
    --output "metrics/precision_optimized_evaluation_$(date +%Y%m%d_%H%M%S).json" \
    --test-cases 15

# Check exit code
EXIT_CODE=$?

echo ""
echo "📊 Precision optimization evaluation completed with exit code: $EXIT_CODE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 PRECISION TARGET ACHIEVED!"
    echo "   Precision ≥0.20 achieved - system is production ready"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "📈 Floor A passed - approaching precision target"
    echo "   System is close to production ready"
else
    echo "⚠️ Below Floor A - more precision optimization needed"
    echo "   System needs further precision improvements"
fi

echo ""
echo "🔍 Check the output files for detailed results and metrics"
echo "📈 Review precision improvements and next optimization steps"

exit $EXIT_CODE
