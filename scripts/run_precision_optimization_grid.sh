#!/bin/bash

# Precision Optimization Grid - 3x3 A/B Testing
# Based on analysis: Need +1.8 precision points to clear Haiku baseline
# Current: P=0.117, R=0.165, F1=0.133
# Target: P≥0.135, R~0.16, F1≥0.145

set -e

echo "🎯 Precision Optimization Grid - 3x3 A/B Testing"
echo "================================================="
echo "Current: P=0.117, R=0.165, F1=0.133"
echo "Target: P≥0.135, R~0.16, F1≥0.145"
echo ""

# Set up base environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Base configuration (from stable_bedrock.env)
export USE_BEDROCK_QUEUE=1
export ASYNC_MAX_CONCURRENCY=1
export BEDROCK_MAX_CONCURRENCY=1
export BEDROCK_MAX_RPS=0.15
export BEDROCK_COOLDOWN_SEC=30
export BEDROCK_RETRY_MAX=8
export BEDROCK_RETRY_BASE=1.8
export BEDROCK_RETRY_MAX_SLEEP=20
export RAGCHECKER_COVERAGE_REWRITE=0
export RAGCHECKER_JSON_PROMPTS=0
export RAGCHECKER_JSON_MAX_TOKENS=200
export RAGCHECKER_EVIDENCE_JACCARD=0.07
export RAGCHECKER_EVIDENCE_COVERAGE=0.20
export RAGCHECKER_RRF_K=50
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR=0.72
export RAGCHECKER_PER_DOC_LINE_CAP=8
export RAGCHECKER_SUPPORT_TWO_OF_THREE=1
export RAGCHECKER_RISKY_REQUIRE_ALL=1
export RAGCHECKER_NUMERIC_MUST_MATCH=1
export RAGCHECKER_ENTITY_MUST_MATCH=1
export RAGCHECKER_NLI_ENABLE=1
export RAGCHECKER_NLI_ON_BORDERLINE=1
export RAGCHECKER_BORDERLINE_BAND=0.02
export RAGCHECKER_NLI_P_THRESHOLD=0.65
export RAGCHECKER_TELEMETRY_ENABLED=1
export RAGCHECKER_LOG_CE_USED_PERCENT=1
export RAGCHECKER_LOG_FUSION_GAIN=1
export RAGCHECKER_LOG_ANCHOR_COVERAGE=1

# Grid parameters
CE_WEIGHTS=(0.24 0.28 0.32)
RERANK_TOPS=(8 10 12)
BM25_ANCHORS=(1.2 1.3 1.4)

# Results tracking
declare -A results
best_precision=0
best_config=""
best_f1=0

echo "🚀 Starting 3x3 grid optimization..."
echo ""

# Run grid
for ce_weight in "${CE_WEIGHTS[@]}"; do
    for rerank_top in "${RERANK_TOPS[@]}"; do
        for bm25_anchor in "${BM25_ANCHORS[@]}"; do
            config_name="ce${ce_weight}_r${rerank_top}_b${bm25_anchor}"

            echo "🔧 Testing configuration: $config_name"
            echo "   CE_WEIGHT=$ce_weight, RERANK_TOP_N=$rerank_top, BM25_ANCHOR=$bm25_anchor"

            # Set configuration
            export RAGCHECKER_CE_WEIGHT=$ce_weight
            export RERANK_TOP_N=$rerank_top
            export RAGCHECKER_BM25_BOOST_ANCHORS=$bm25_anchor
            export RAGCHECKER_CE_RERANK_TOPN=$rerank_top
            export RETRIEVER_TOP_K=100
            export MMR_LAMBDA=0.2
            export ANSWER_EVIDENCE_GATE=0.60

            # Run evaluation
            echo "   Running evaluation..."
            python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli > "/tmp/grid_${config_name}.log" 2>&1

            # Extract results from log
            if grep -q "Overall Metrics:" "/tmp/grid_${config_name}.log"; then
                precision=$(grep "Precision:" "/tmp/grid_${config_name}.log" | awk '{print $2}')
                recall=$(grep "Recall:" "/tmp/grid_${config_name}.log" | awk '{print $2}')
                f1=$(grep "F1 Score:" "/tmp/grid_${config_name}.log" | awk '{print $3}')

                echo "   Results: P=$precision, R=$recall, F1=$f1"

                # Track best results
                if (( $(echo "$precision > $best_precision" | bc -l) )); then
                    best_precision=$precision
                    best_config=$config_name
                    best_f1=$f1
                fi

                results[$config_name]="$precision,$recall,$f1"
            else
                echo "   ❌ Evaluation failed"
                results[$config_name]="FAILED"
            fi

            echo ""
        done
    done
done

# Summary
echo "📊 Grid Optimization Results Summary"
echo "===================================="
echo ""

for config in "${!results[@]}"; do
    if [ "${results[$config]}" != "FAILED" ]; then
        IFS=',' read -r p r f1 <<< "${results[$config]}"
        echo "$config: P=$p, R=$r, F1=$f1"
    else
        echo "$config: FAILED"
    fi
done

echo ""
echo "🏆 Best Configuration: $best_config"
echo "   Precision: $best_precision"
echo "   F1 Score: $best_f1"
echo ""

# Check if we hit targets
if (( $(echo "$best_precision >= 0.135" | bc -l) )); then
    echo "✅ PRECISION TARGET HIT! (≥0.135)"
else
    echo "⚠️  Precision target not met (need ≥0.135, got $best_precision)"
fi

if (( $(echo "$best_f1 >= 0.145" | bc -l) )); then
    echo "✅ F1 TARGET HIT! (≥0.145)"
else
    echo "⚠️  F1 target not met (need ≥0.145, got $best_f1)"
fi

echo ""
echo "🎯 Next steps:"
echo "1. If targets hit: Apply best config to production"
echo "2. If targets missed: Try answer shaping optimizations"
echo "3. If still short: Implement outlier case fixes"
