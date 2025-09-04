#!/bin/bash

# Production RAGAS Evaluation - Tight, No-Drama Rollout
# Converts three moves into production wins with precision ≥ 0.20
# while maintaining recall ≥ 0.60 and unsupported ≤ 15%

set -e

echo "🚀 Production RAGAS Evaluation - Tight, No-Drama Rollout"
echo "========================================================"
echo "🎯 Target: Precision ≥ 0.20, Recall@20 ≥ 0.65, F1 ≥ 0.175, Unsupported ≤ 15%"
echo ""

# Set up environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Step 0: Wire-through & Go-Live Checklist
echo "🔧 Step 0: Wire-through & Go-Live Checklist"
echo "============================================"

# Router configuration
export RAGCHECKER_ROUTE_BM25_MARGIN="0.1"
export RAGCHECKER_REWRITE_AGREE_STRONG="0.5"

# Fusion configuration
export RAGCHECKER_RRF_K="50"
export RAGCHECKER_BM25_BOOST_ANCHORS="1.8"
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR="0.75"
export RAGCHECKER_PER_DOC_LINE_CAP="8"

# Facets configuration
export RAGCHECKER_REWRITE_K="10"
export RAGCHECKER_REWRITE_KEEP="0.8"
export RAGCHECKER_REWRITE_YIELD_MIN="1.5"

# Selection gates configuration
export RAGCHECKER_EVIDENCE_JACCARD="0.07"
export RAGCHECKER_EVIDENCE_COVERAGE="0.20"
export RAGCHECKER_SUPPORT_TWO_OF_THREE="1"
export RAGCHECKER_RISKY_REQUIRE_ALL="1"
export ROUGE_FLOOR="0.20"
export COS_FLOOR="0.58"

# Claim binding configuration
export RAGCHECKER_CLAIM_TOPK="2"
export RAGCHECKER_CLAIM_TOPK_STRONG="3"
export RAGCHECKER_MIN_WORDS_AFTER_BINDING="160"
export RAGCHECKER_DROP_UNSUPPORTED="0"

# Cross-encoder and NLI configuration
export RAGCHECKER_CE_RERANK_ENABLE="1"
export RAGCHECKER_CE_RERANK_TOPN="80"
export RAGCHECKER_CE_WEIGHT="0.14"
export RAGCHECKER_NLI_ENABLE="1"
export RAGCHECKER_NLI_ON_BORDERLINE="1"
export RAGCHECKER_BORDERLINE_BAND="0.02"
export RAGCHECKER_NLI_P_THRESHOLD="0.62"

# Dynamic-K configuration
export RAGCHECKER_EVIDENCE_KEEP_MODE="target_k"
export RAGCHECKER_TARGET_K_WEAK="3"
export RAGCHECKER_TARGET_K_BASE="5"
export RAGCHECKER_TARGET_K_STRONG="9"

echo "✅ Wire-through checklist applied"
echo ""

# Step 1: Precision Climb - Turn the Screws Where It Matters (Risky Only)
echo "🎯 Step 1: Precision Climb - Risky Only"
echo "========================================"

# Risk-aware evidence (strengthened for risky sentences)
export RAGCHECKER_SUPPORT_TWO_OF_THREE="1"
export RAGCHECKER_RISKY_REQUIRE_ALL="1"
export RAGCHECKER_EVIDENCE_JACCARD="0.07"
export RAGCHECKER_EVIDENCE_COVERAGE="0.20"
export ROUGE_FLOOR="0.20"
export COS_FLOOR="0.58"

# Multi-evidence for risky content
export RAGCHECKER_NUMERIC_MUST_MATCH="1"
export RAGCHECKER_ENTITY_MUST_MATCH="1"
export RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC="2"
export RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY="2"

echo "✅ Precision climb applied: 3-of-3 for risky, 2-of-3 for non-risky"
echo ""

# Step 2: Retain Recall While Tightening Precision
echo "🏗️ Step 2: Retain Recall While Tightening Precision"
echo "==================================================="

# Anchor-biased fusion (keep on)
export RAGCHECKER_RRF_K="50"
export RAGCHECKER_BM25_BOOST_ANCHORS="1.8"
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR="0.75"
export RAGCHECKER_PER_DOC_LINE_CAP="8"
export RAGCHECKER_LONG_TAIL_SLOT="1"  # Always preserve one novel doc

# Facet yield - selective strictness
export RAGCHECKER_REWRITE_YIELD_MIN="1.5"  # Global default
export RAGCHECKER_REWRITE_YIELD_MIN_SPARSE="1.2"  # For sparse cases

echo "✅ Recall retention applied: anchor-biased fusion + selective facet yield"
echo ""

# Step 3: Claim Binding That Slashes Unsupported ≤ 15%
echo "🎯 Step 3: Claim Binding - Slash Unsupported Claims"
echo "==================================================="

# Soft-drop stays
export RAGCHECKER_DROP_UNSUPPORTED="0"

# Breadth and length controls
export RAGCHECKER_CLAIM_TOPK="2"  # Global
export RAGCHECKER_CLAIM_TOPK_STRONG="3"  # Strong cases only
export RAGCHECKER_MIN_WORDS_AFTER_BINDING="160"

echo "✅ Claim binding applied: soft-drop + confidence ordering"
echo ""

# Cross-Encoder & NLI Configuration
echo "🔄 Cross-Encoder & NLI Configuration"
echo "===================================="

# Make CE decisive (but bounded)
export RAGCHECKER_CE_RERANK_ENABLE="1"
export RAGCHECKER_CE_RERANK_TOPN="80"
export RAGCHECKER_CE_WEIGHT="0.14"  # 0.12 → 0.14

# NLI on the edge (borderline only)
export RAGCHECKER_NLI_ENABLE="1"
export RAGCHECKER_NLI_ON_BORDERLINE="1"
export RAGCHECKER_BORDERLINE_BAND="0.02"
export RAGCHECKER_NLI_P_THRESHOLD="0.62"  # 0.60 → 0.62

echo "✅ Cross-encoder & NLI applied: decisive CE + borderline NLI"
echo ""

# Telemetry Configuration
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

# Additional production settings
export RAGCHECKER_JUDGE_MODE="haiku"
export RAGCHECKER_HAIKU_FLOORS="1"
export RAGCHECKER_FAITHFULNESS_REPORTING="1"
export RAGCHECKER_PRODUCTION_MODE="1"
export RAGCHECKER_TIGHT_ROLLOUT="1"

# Run the production RAGAS evaluation
echo "🚀 Starting Production RAGAS Evaluation..."
echo "=========================================="
echo ""

# Check if we should validate only
if [ "$1" = "--validate" ]; then
    echo "🔍 Running configuration validation only..."
    python3 scripts/ragchecker_production_evaluation.py --validate-only
else
    echo "🎯 Running full production evaluation with wire-through checklist..."
    python3 scripts/ragchecker_production_evaluation.py --output "production_ragas_results.json"
fi

echo ""
echo "📊 Production RAGAS Evaluation Complete!"
echo "======================================="

# Print effective configuration summary
echo ""
echo "📋 Effective Configuration Summary:"
echo "=================================="
echo "Router: ROUTE_BM25_MARGIN=$RAGCHECKER_ROUTE_BM25_MARGIN, REWRITE_AGREE_STRONG=$RAGCHECKER_REWRITE_AGREE_STRONG"
echo "Fusion: RRF_K=$RAGCHECKER_RRF_K, BM25_BOOST_ANCHORS=$RAGCHECKER_BM25_BOOST_ANCHORS"
echo "Selection: EVIDENCE_JACCARD=$RAGCHECKER_EVIDENCE_JACCARD, EVIDENCE_COVERAGE=$RAGCHECKER_EVIDENCE_COVERAGE"
echo "Risk-Aware: SUPPORT_TWO_OF_THREE=$RAGCHECKER_SUPPORT_TWO_OF_THREE, RISKY_REQUIRE_ALL=$RAGCHECKER_RISKY_REQUIRE_ALL"
echo "Cross-Encoder: CE_WEIGHT=$RAGCHECKER_CE_WEIGHT, CE_RERANK_TOPN=$RAGCHECKER_CE_RERANK_TOPN"
echo "NLI Gate: NLI_P_THRESHOLD=$RAGCHECKER_NLI_P_THRESHOLD, BORDERLINE_BAND=$RAGCHECKER_BORDERLINE_BAND"
echo "Claim Binding: CLAIM_TOPK=$RAGCHECKER_CLAIM_TOPK, MIN_WORDS_AFTER_BINDING=$RAGCHECKER_MIN_WORDS_AFTER_BINDING"
echo "Dynamic-K: TARGET_K_STRONG=$RAGCHECKER_TARGET_K_STRONG, EVIDENCE_KEEP_MODE=$RAGCHECKER_EVIDENCE_KEEP_MODE"
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

# Show precision knobs for fine-tuning
echo "🔧 Precision Knobs (if P < 0.20):"
echo "=================================="
echo "• CE_WEIGHT: 0.14 → 0.16 (max 0.18)"
echo "• EVIDENCE_COVERAGE: 0.20 → 0.22 (risky only)"
echo "• REDUNDANCY_TRIGRAM_MAX: 0.40 → 0.38"
echo "• TARGET_K_STRONG: 9 → 8 (strong cases only)"
echo ""

# Show recall knobs for maintaining R@20
echo "📈 Recall Knobs (if R@20 < 0.65):"
echo "=================================="
echo "• CONTEXT_TOPK: 16-18 → 20-22 (adaptive based on rewrite_agreement)"
echo "• LONG_TAIL_SLOT: 1 (always preserve one novel doc)"
echo ""

echo "✅ Production RAGAS execution complete!"
echo "📊 Check production_ragas_results.json for detailed results"
echo ""
echo "🔄 Next Steps:"
echo "=============="
echo "1. If Precision ≥ 0.20 and R@20 ≥ 0.60: Repeat once (two-run rule) and lock floors"
echo "2. If Precision < 0.20: Apply one precision knob and rerun"
echo "3. If R@20 < 0.65: Apply recall knob and rerun"
echo "4. Monitor telemetry: risky_pass_rate, ce_used%, nli_used%, unsupported%"
