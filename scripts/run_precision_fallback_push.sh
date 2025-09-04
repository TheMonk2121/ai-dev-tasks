#!/bin/bash

# Precision Fallback Push - Apply fallback configurations to reach RAGAS targets
# Based on the evaluation results showing we need precision improvements

set -e

echo "🎯 Precision Fallback Push - Surgical Precision Improvements"
echo "============================================================"
echo "📊 Current: Precision 0.119 → Target: ≥0.20"
echo "📊 Current: Recall 0.263 → Target: ≥0.65"
echo ""

# Set up environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Apply precision fallback configurations
echo "🔧 Applying Precision Fallback Configurations"
echo "=============================================="

# Drop TARGET_K_STRONG by 1 (from 9 to 8)
export RAGCHECKER_TARGET_K_STRONG="8"

# Raise EVIDENCE_COVERAGE to 0.22 for risky sentences only
export RAGCHECKER_EVIDENCE_COVERAGE="0.22"
export RAGCHECKER_EVIDENCE_COVERAGE_RISKY="0.22"

# Apply recall fallback if needed
export RAGCHECKER_CONTEXT_TOPK="18"

# Enhanced precision-focused settings
export RAGCHECKER_EVIDENCE_JACCARD="0.08"  # Slightly higher threshold
export RAGCHECKER_SUPPORT_TWO_OF_THREE="1"
export RAGCHECKER_RISKY_REQUIRE_ALL="1"
export ROUGE_FLOOR="0.22"  # Slightly higher
export COS_FLOOR="0.60"    # Slightly higher

# Multi-evidence for risky content
export RAGCHECKER_NUMERIC_MUST_MATCH="1"
export RAGCHECKER_ENTITY_MUST_MATCH="1"
export RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC="2"
export RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY="2"

# Cross-encoder with higher weight
export RAGCHECKER_CROSS_ENCODER_ENABLED="1"
export RAGCHECKER_CE_RERANK_ENABLE="1"
export RAGCHECKER_CE_RERANK_TOPN="60"  # Reduced for more focused reranking
export RAGCHECKER_CE_WEIGHT="0.15"     # Higher weight for more impact

# NLI gate for borderline sentences
export RAGCHECKER_NLI_ENABLE="1"
export RAGCHECKER_NLI_ON_BORDERLINE="1"
export RAGCHECKER_BORDERLINE_BAND="0.015"  # Tighter band
export RAGCHECKER_NLI_P_THRESHOLD="0.65"   # Higher threshold

# Redundancy controls
export RAGCHECKER_PER_CHUNK_CAP="2"
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX="0.35"  # Stricter

# Anchor-biased fusion (retain)
export RAGCHECKER_RRF_K="50"
export RAGCHECKER_BM25_BOOST_ANCHORS="1.9"  # Slightly higher
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR="0.70"  # Stricter
export RAGCHECKER_PER_DOC_LINE_CAP="7"  # Reduced

# Claim binding
export RAGCHECKER_CLAIM_TOPK="2"
export RAGCHECKER_CLAIM_TOPK_STRONG="3"
export RAGCHECKER_MIN_WORDS_AFTER_BINDING="180"  # Higher threshold
export RAGCHECKER_DROP_UNSUPPORTED="0"  # Keep soft-drop

# Dynamic-K with precision focus
export RAGCHECKER_EVIDENCE_KEEP_MODE="target_k"
export RAGCHECKER_TARGET_K_WEAK="2"  # Reduced
export RAGCHECKER_TARGET_K_BASE="4"  # Reduced
export RAGCHECKER_TARGET_K_STRONG="8"  # Reduced from 9

# Facet yield (stricter)
export RAGCHECKER_REWRITE_YIELD_MIN="1.8"  # Higher threshold
export RAGCHECKER_REWRITE_YIELD_MIN_SPARSE="1.3"

echo "✅ Precision fallback configurations applied"
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
export RAGCHECKER_PRECISION_FALLBACK_MODE="1"

# Run the precision fallback push evaluation
echo "🚀 Starting Precision Fallback Push Evaluation..."
echo "=================================================="
echo ""

python3 scripts/ragchecker_final_ragas_push_evaluation.py --output "precision_fallback_push_results.json"

echo ""
echo "📊 Precision Fallback Push Evaluation Complete!"
echo "==============================================="

# Print effective configuration summary
echo ""
echo "📋 Precision Fallback Configuration Summary:"
echo "============================================"
echo "Precision Focus: TARGET_K_STRONG=$RAGCHECKER_TARGET_K_STRONG, EVIDENCE_COVERAGE=$RAGCHECKER_EVIDENCE_COVERAGE"
echo "Evidence Thresholds: EVIDENCE_JACCARD=$RAGCHECKER_EVIDENCE_JACCARD, ROUGE_FLOOR=$ROUGE_FLOOR, COS_FLOOR=$COS_FLOOR"
echo "Cross-Encoder: CE_WEIGHT=$RAGCHECKER_CE_WEIGHT, CE_RERANK_TOPN=$RAGCHECKER_CE_RERANK_TOPN"
echo "NLI Gate: NLI_P_THRESHOLD=$RAGCHECKER_NLI_P_THRESHOLD, BORDERLINE_BAND=$RAGCHECKER_BORDERLINE_BAND"
echo "Redundancy: PER_CHUNK_CAP=$RAGCHECKER_PER_CHUNK_CAP, REDUNDANCY_TRIGRAM_MAX=$RAGCHECKER_REDUNDANCY_TRIGRAM_MAX"
echo "Fusion: BM25_BOOST_ANCHORS=$RAGCHECKER_BM25_BOOST_ANCHORS, FACET_DOWNWEIGHT_NO_ANCHOR=$RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR"
echo "Claim Binding: MIN_WORDS_AFTER_BINDING=$RAGCHECKER_MIN_WORDS_AFTER_BINDING"
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

echo "✅ Precision Fallback Push execution complete!"
echo "📊 Check precision_fallback_push_results.json for detailed results"
