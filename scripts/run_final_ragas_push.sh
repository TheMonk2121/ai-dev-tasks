#!/usr/bin/env bash

# Final RAGAS Push Execution Script
# Implements the three-move strategy to push precision past 0.20 while maintaining recall ≥0.60

set -e

echo "🚀 Final RAGAS Push - Three-Move Strategy"
echo "=========================================="
echo "🎯 Target: Precision ≥ 0.20, Recall@20 ≥ 0.65, F1 ≥ 0.175, Unsupported ≤ 15%"
echo ""

# Set up environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Move 1: Risk-aware 3-of-3 (risky only) + multi-evidence
echo "🎯 Move 1: Risk-aware 3-of-3 + Multi-evidence"
echo "=============================================="

# Risk-aware support rules
export RAGCHECKER_SUPPORT_TWO_OF_THREE="1"  # 2-of-3 for normal sentences
export RAGCHECKER_RISKY_REQUIRE_ALL="1"     # 3-of-3 for risky sentences

# Evidence thresholds
export RAGCHECKER_EVIDENCE_JACCARD="0.07"
export RAGCHECKER_EVIDENCE_COVERAGE="0.20"
export ROUGE_FLOOR="0.20"
export COS_FLOOR="0.58"

# Multi-evidence for risky content
export RAGCHECKER_NUMERIC_MUST_MATCH="1"
export RAGCHECKER_ENTITY_MUST_MATCH="1"
export RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC="2"
export RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY="2"

echo "✅ Move 1 applied: Risk-aware 3-of-3 + multi-evidence"
echo "   Expected: +0.01–0.02 precision, Unsupported ↓, recall ≈ flat"
echo ""

# Move 2: Lightweight cross-encoder rerank with decisive blending
echo "🎯 Move 2: Cross-encoder Rerank with Decisive Blending"
echo "====================================================="

# Cross-encoder configuration
export RAGCHECKER_CROSS_ENCODER_ENABLED="1"
export RAGCHECKER_CE_RERANK_ENABLE="1"
export RAGCHECKER_CE_RERANK_TOPN="80"
export RAGCHECKER_CE_WEIGHT="0.12"  # Nudged up from 0.10

# Redundancy controls (if needed)
export RAGCHECKER_PER_CHUNK_CAP="2"  # Strict if flooding
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX="0.40"

echo "✅ Move 2 applied: Cross-encoder rerank with decisive blending"
echo "   Expected: +0.02–0.04 precision, minimal recall hit"
echo ""

# Move 3: Borderline NLI gate for unsupported reduction
echo "🎯 Move 3: Borderline NLI Gate"
echo "=============================="

# NLI configuration
export RAGCHECKER_NLI_ENABLE="1"
export RAGCHECKER_NLI_ON_BORDERLINE="1"
export RAGCHECKER_BORDERLINE_BAND="0.02"
export RAGCHECKER_NLI_P_THRESHOLD="0.60"

echo "✅ Move 3 applied: Borderline NLI gate"
echo "   Expected: Unsupported → ≤15–18%, precision +~0.01, tiny recall cost"
echo ""

# Recall health maintenance
echo "🏗️ Recall Health Maintenance"
echo "============================"

# Anchor-biased fusion (retain)
export RAGCHECKER_RRF_K="50"
export RAGCHECKER_BM25_BOOST_ANCHORS="1.8"
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR="0.75"
export RAGCHECKER_PER_DOC_LINE_CAP="8"
export RAGCHECKER_LONG_TAIL_SLOT="1"

# Facet yield (selective)
export RAGCHECKER_REWRITE_YIELD_MIN="1.5"  # Global default
export RAGCHECKER_REWRITE_YIELD_MIN_SPARSE="1.2"  # For sparse cases

# Claim binding
export RAGCHECKER_CLAIM_TOPK="2"
export RAGCHECKER_CLAIM_TOPK_STRONG="3"
export RAGCHECKER_MIN_WORDS_AFTER_BINDING="160"
export RAGCHECKER_DROP_UNSUPPORTED="0"  # Keep soft-drop

# Dynamic-K
export RAGCHECKER_EVIDENCE_KEEP_MODE="target_k"
export RAGCHECKER_TARGET_K_WEAK="3"
export RAGCHECKER_TARGET_K_BASE="5"
export RAGCHECKER_TARGET_K_STRONG="9"

echo "✅ Recall health maintenance applied"
echo ""

# Telemetry configuration
echo "📊 Enabling Comprehensive Telemetry"
echo "==================================="
export RAGCHECKER_TELEMETRY_ENABLED="1"
export RAGCHECKER_LOG_RISKY_PASS_RATE="1"
export RAGCHECKER_LOG_CE_USED_PERCENT="1"
export RAGCHECKER_LOG_NLI_USED_PERCENT="1"
export RAGCHECKER_LOG_UNSUPPORTED_PERCENT="1"
export RAGCHECKER_LOG_FUSION_GAIN="1"
export RAGCHECKER_LOG_ANCHOR_COVERAGE="1"
export RAGCHECKER_LOG_KEPT_SENTENCES="1"
export RAGCHECKER_LOG_CLAIMS_EXTRACTED_KEPT="1"

echo "✅ Comprehensive telemetry enabled"
echo ""

# Additional precision-focused settings
export RAGCHECKER_JUDGE_MODE="haiku"
export RAGCHECKER_HAIKU_FLOORS="1"
export RAGCHECKER_FAITHFULNESS_REPORTING="1"
export RAGCHECKER_FINAL_PRECISION_PUSH="1"
export RAGCHECKER_AGGRESSIVE_MODE="1"

# Run the final RAGAS push evaluation
echo "🚀 Starting Final RAGAS Push Evaluation..."
echo "=========================================="
echo ""

# Check if we should validate only
if [ "$1" = "--validate" ]; then
    echo "🔍 Running configuration validation only..."
    python3 scripts/ragchecker_final_ragas_push_evaluation.py --validate-only
else
    echo "🎯 Running full 15-case evaluation with Haiku judge..."
    python3 scripts/ragchecker_final_ragas_push_evaluation.py --output "final_ragas_push_results.json"
fi

echo ""
echo "📊 Final RAGAS Push Evaluation Complete!"
echo "========================================"

# Print effective configuration summary
echo ""
echo "📋 Effective Configuration Summary:"
echo "=================================="
echo "Move 1 - Risk-aware: SUPPORT_TWO_OF_THREE=$RAGCHECKER_SUPPORT_TWO_OF_THREE, RISKY_REQUIRE_ALL=$RAGCHECKER_RISKY_REQUIRE_ALL"
echo "Move 1 - Evidence: EVIDENCE_JACCARD=$RAGCHECKER_EVIDENCE_JACCARD, EVIDENCE_COVERAGE=$RAGCHECKER_EVIDENCE_COVERAGE"
echo "Move 1 - Multi-evidence: NUMERIC_MUST_MATCH=$RAGCHECKER_NUMERIC_MUST_MATCH, ENTITY_MUST_MATCH=$RAGCHECKER_ENTITY_MUST_MATCH"
echo "Move 2 - Cross-encoder: CE_RERANK_ENABLE=$RAGCHECKER_CE_RERANK_ENABLE, CE_WEIGHT=$RAGCHECKER_CE_WEIGHT"
echo "Move 3 - NLI Gate: NLI_ENABLE=$RAGCHECKER_NLI_ENABLE, NLI_P_THRESHOLD=$RAGCHECKER_NLI_P_THRESHOLD"
echo "Recall Health: RRF_K=$RAGCHECKER_RRF_K, BM25_BOOST_ANCHORS=$RAGCHECKER_BM25_BOOST_ANCHORS"
echo "Claim Binding: CLAIM_TOPK=$RAGCHECKER_CLAIM_TOPK, MIN_WORDS_AFTER_BINDING=$RAGCHECKER_MIN_WORDS_AFTER_BINDING"
echo ""

# Show RAGAS targets
echo "🎯 RAGAS Target Metrics:"
echo "========================"
echo "Precision ≥ 0.20"
echo "Recall@20 ≥ 0.65"
echo "F1 ≥ 0.175"
echo "Unsupported ≤ 15%"
echo "Faithfulness ≥ 0.60"
echo ""

echo "✅ Final RAGAS Push execution complete!"
echo "📊 Check final_ragas_push_results.json for detailed results"
