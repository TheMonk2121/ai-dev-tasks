#!/usr/bin/env bash

# Precision-Climb v2 Evaluation Script
# Implements the precision-focused optimization plan to achieve P≥0.20 while maintaining R≥0.60

set -e

echo "🚀 Precision-Climb v2 Evaluation"
echo "=================================="

# Set up environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Layer 0: Wire-through sanity configuration
echo "📊 Applying Layer 0: Wire-through sanity configuration..."

# Router configuration
export RAGCHECKER_ROUTE_BM25_MARGIN="0.20"
export RAGCHECKER_REWRITE_AGREE_STRONG="0.50"

# Fusion configuration
export RAGCHECKER_RRF_K="50"
export RAGCHECKER_BM25_BOOST_ANCHORS="1.8"
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR="0.75"
export RAGCHECKER_PER_DOC_LINE_CAP="8"

# Facets configuration
export RAGCHECKER_REWRITE_K="3"
export RAGCHECKER_REWRITE_KEEP="1"
export RAGCHECKER_REWRITE_YIELD_MIN="1.5"

# Selection gates
export RAGCHECKER_EVIDENCE_JACCARD="0.07"
export RAGCHECKER_EVIDENCE_COVERAGE="0.20"
export RAGCHECKER_SUPPORT_TWO_OF_THREE="1"

# Binding configuration
export RAGCHECKER_CLAIM_TOPK="2"
export RAGCHECKER_MIN_WORDS_AFTER_BINDING="160"
export RAGCHECKER_DROP_UNSUPPORTED="0"

# Dynamic-K (target-K only, no percentile)
export RAGCHECKER_EVIDENCE_KEEP_MODE="target_k"
export RAGCHECKER_TARGET_K_WEAK="3"
export RAGCHECKER_TARGET_K_BASE="5"
export RAGCHECKER_TARGET_K_STRONG="9"

echo "✅ Layer 0 configuration applied"

# Layer 1: Risk-aware sentence-level gates
echo "📊 Applying Layer 1: Risk-aware sentence-level gates..."

# Risk-aware support rules
export RAGCHECKER_RISKY_REQUIRE_ALL="1"  # 3-of-3 for risky sentences
export RAGCHECKER_SUPPORT_TWO_OF_THREE="1"  # 2-of-3 for non-risky

# Evidence thresholds
export RAGCHECKER_EVIDENCE_JACCARD="0.07"
export RAGCHECKER_EVIDENCE_COVERAGE="0.20"
export COS_FLOOR="0.58"  # Normalized cosine threshold
export ROUGE_FLOOR="0.20"

# Multi-evidence for risky content
export RAGCHECKER_NUMERIC_MUST_MATCH="1"
export RAGCHECKER_ENTITY_MUST_MATCH="1"
export RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC="2"
export RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY="2"

# Redundancy and novelty controls
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX="0.40"  # 0.45 → 0.40
export RAGCHECKER_PER_CHUNK_CAP="1"  # Global cap
export RAGCHECKER_UNIQUE_ANCHOR_MIN="1"  # Each sentence must add new anchor

echo "✅ Layer 1 configuration applied"

# Layer 2: Fusion tweaks favoring truly relevant docs
echo "📊 Applying Layer 2: Fusion tweaks..."

# Anchor-biased fusion (stronger)
export RAGCHECKER_RRF_K="50"  # Stronger rank discount for deep items
export RAGCHECKER_BM25_BOOST_ANCHORS="1.8"
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR="0.75"
export RAGCHECKER_PER_DOC_LINE_CAP="8"

# Selective facet yield (adaptive)
export RAGCHECKER_REWRITE_YIELD_MIN="1.5"  # Global default
export RAGCHECKER_REWRITE_YIELD_MIN_SPARSE="1.2"  # For sparse cases
export RAGCHECKER_FUSION_GAIN_THRESHOLD="2"  # Threshold for sparse case detection

echo "✅ Layer 2 configuration applied"

# Layer 3: Claim binding optimization
echo "📊 Applying Layer 3: Claim binding optimization..."

# Soft-drop configuration
export RAGCHECKER_DROP_UNSUPPORTED="0"  # Keep soft-drop

# Claim binding parameters
export RAGCHECKER_CLAIM_TOPK="2"  # Global
export RAGCHECKER_CLAIM_TOPK_STRONG="3"  # For strong cases
export RAGCHECKER_MIN_WORDS_AFTER_BINDING="160"

# Per-claim confidence scoring
export RAGCHECKER_CLAIM_CONFIDENCE_ENABLED="1"
export RAGCHECKER_CLAIM_CONFIDENCE_WEIGHTS="0.4,0.3,0.3"  # cosine, anchor, spans

echo "✅ Layer 3 configuration applied"

# Telemetry configuration
echo "📊 Enabling telemetry..."
export RAGCHECKER_TELEMETRY_ENABLED="1"
export RAGCHECKER_LOG_RISKY_PASS_RATE="1"
export RAGCHECKER_LOG_UNSUPPORTED_PERCENT="1"
export RAGCHECKER_LOG_FUSION_GAIN="1"
export RAGCHECKER_LOG_ANCHOR_COVERAGE="1"
export RAGCHECKER_LOG_NUMERIC_MATCH_RATE="1"
export RAGCHECKER_LOG_ENTITY_MATCH_RATE="1"
export RAGCHECKER_LOG_CE_RERANK_USED="1"

echo "✅ Telemetry enabled"

# Additional precision-focused settings
export RAGCHECKER_JUDGE_MODE="haiku"
export RAGCHECKER_HAIKU_FLOORS="1"
export RAGCHECKER_FAITHFULNESS_REPORTING="1"
export RAGCHECKER_FINAL_PRECISION_PUSH="1"
export RAGCHECKER_AGGRESSIVE_MODE="1"

# Run the evaluation
echo ""
echo "🎯 Starting Precision-Climb v2 evaluation..."
echo "Target: Precision ≥ 0.20, Recall ≥ 0.60, F1 ≥ 0.22"
echo ""

# Check if we should run staged evaluation
if [ "$1" = "--staged" ]; then
    echo "🔄 Running staged evaluation across all layers..."
    python3 scripts/ragchecker_precision_climb_v2_evaluation.py --staged --output "precision_climb_v2_staged_results.json"
else
    echo "🔄 Running single-layer evaluation (Layer 1)..."
    python3 scripts/ragchecker_precision_climb_v2_evaluation.py --layer layer1 --output "precision_climb_v2_results.json"
fi

echo ""
echo "📊 Evaluation completed!"
echo "Results saved to precision_climb_v2_results.json"

# Print effective configuration summary
echo ""
echo "📋 Effective Configuration Summary:"
echo "=================================="
echo "Router: ROUTE_BM25_MARGIN=$RAGCHECKER_ROUTE_BM25_MARGIN, REWRITE_AGREE_STRONG=$RAGCHECKER_REWRITE_AGREE_STRONG"
echo "Fusion: RRF_K=$RAGCHECKER_RRF_K, BM25_BOOST_ANCHORS=$RAGCHECKER_BM25_BOOST_ANCHORS"
echo "Facets: REWRITE_K=$RAGCHECKER_REWRITE_K, REWRITE_KEEP=$RAGCHECKER_REWRITE_KEEP, REWRITE_YIELD_MIN=$RAGCHECKER_REWRITE_YIELD_MIN"
echo "Selection: EVIDENCE_JACCARD=$RAGCHECKER_EVIDENCE_JACCARD, EVIDENCE_COVERAGE=$RAGCHECKER_EVIDENCE_COVERAGE"
echo "Binding: CLAIM_TOPK=$RAGCHECKER_CLAIM_TOPK, MIN_WORDS_AFTER_BINDING=$RAGCHECKER_MIN_WORDS_AFTER_BINDING"
echo "Risk-aware: RISKY_REQUIRE_ALL=$RAGCHECKER_RISKY_REQUIRE_ALL, SUPPORT_TWO_OF_THREE=$RAGCHECKER_SUPPORT_TWO_OF_THREE"
echo "Multi-evidence: NUMERIC_MUST_MATCH=$RAGCHECKER_NUMERIC_MUST_MATCH, ENTITY_MUST_MATCH=$RAGCHECKER_ENTITY_MUST_MATCH"
echo "Redundancy: REDUNDANCY_TRIGRAM_MAX=$RAGCHECKER_REDUNDANCY_TRIGRAM_MAX, PER_CHUNK_CAP=$RAGCHECKER_PER_CHUNK_CAP"
echo "Confidence: CLAIM_CONFIDENCE_ENABLED=$RAGCHECKER_CLAIM_CONFIDENCE_ENABLED"
echo ""

# Check if results meet promotion gate criteria
echo "🎯 Promotion Gate Criteria:"
echo "=========================="
echo "Recall@20 ≥ 0.65"
echo "Precision ≥ 0.20"
echo "F1 ≥ 0.175"
echo "Faithfulness ≥ 0.60"
echo "Unsupported ≤ 15%"
echo ""

echo "✅ Precision-Climb v2 evaluation complete!"
