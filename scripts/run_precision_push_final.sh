#!/bin/bash

# Precision Push Final Configuration
# Export all environment variables for persistence across processes

echo "🚀 Precision Push Final Configuration"
echo "======================================"

# Faithfulness Fix
export RAGCHECKER_ENABLE_FUSED_SCORER=1
export RAGCHECKER_JSON_PROMPTS=1

# Precision Push - Risk-aware gates
export RAGCHECKER_SUPPORT_TWO_OF_THREE=1
export RAGCHECKER_RISKY_REQUIRE_ALL=1
export RAGCHECKER_NUMERIC_MUST_MATCH=1
export RAGCHECKER_ENTITY_MUST_MATCH=1
export RAGCHECKER_MULTI_EVIDENCE_FOR_NUMERIC=2
export RAGCHECKER_MULTI_EVIDENCE_FOR_ENTITY=2

# NLI bump on borderlines
export RAGCHECKER_NLI_ENABLE=1
export RAGCHECKER_NLI_ON_BORDERLINE=1
export RAGCHECKER_BORDERLINE_BAND=0.02
export RAGCHECKER_NLI_P_THRESHOLD=0.65

# CE weight bump
export RAGCHECKER_CE_RERANK_ENABLE=1
export RAGCHECKER_CE_RERANK_TOPN=80
export RAGCHECKER_CE_WEIGHT=0.16

# Keep floors modest so recall holds
export RAGCHECKER_EVIDENCE_JACCARD=0.07
export RAGCHECKER_EVIDENCE_COVERAGE=0.20
export ROUGE_FLOOR=0.20
export COS_FLOOR=0.58

# Fusion bias toward anchored docs (recall-safe)
export RAGCHECKER_RRF_K=50
export RAGCHECKER_BM25_BOOST_ANCHORS=1.9
export RAGCHECKER_FACET_DOWNWEIGHT_NO_ANCHOR=0.72
export RAGCHECKER_PER_DOC_LINE_CAP=8
export RAGCHECKER_LONG_TAIL_SLOT=1

# Tiny redundancy trim
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX=0.38

# Facet breadth — selective, not blanket
export RAGCHECKER_REWRITE_YIELD_MIN=1.8

# Adaptive TOPK only when facets agree
export RAGCHECKER_REWRITE_AGREE_STRONG=0.50
export RAGCHECKER_CONTEXT_TOPK_MIN=16
export RAGCHECKER_CONTEXT_TOPK_MAX=22

# Unsupported fix
export RAGCHECKER_MIN_WORDS_AFTER_BINDING=160
export RAGCHECKER_DROP_UNSUPPORTED=0

# Telemetry
export RAGCHECKER_TELEMETRY_ENABLED=1
export RAGCHECKER_LOG_RISKY_PASS_RATE=1
export RAGCHECKER_LOG_CE_USED_PERCENT=1
export RAGCHECKER_LOG_NLI_USED_PERCENT=1
export RAGCHECKER_LOG_UNSUPPORTED_PERCENT=1
export RAGCHECKER_LOG_FUSION_GAIN=1
export RAGCHECKER_LOG_ANCHOR_COVERAGE=1
export RAGCHECKER_LOG_KEPT_SENTENCES=1
export RAGCHECKER_LOG_CLAIMS_EXTRACTED_KEPT=1
export RAGCHECKER_LOG_REWRITE_AGREEMENT=1

echo "✅ Exported 31 precision push configuration variables"
echo "🎯 Target: Precision ≥ 0.20, Recall@20 ≥ 0.28, F1 ≥ 0.225, Faithfulness ≥ 0.60"

# Verify key variables
echo ""
echo "🔍 Verification:"
echo "  RAGCHECKER_CE_WEIGHT: $RAGCHECKER_CE_WEIGHT"
echo "  RAGCHECKER_NLI_P_THRESHOLD: $RAGCHECKER_NLI_P_THRESHOLD"
echo "  RAGCHECKER_EVIDENCE_COVERAGE: $RAGCHECKER_EVIDENCE_COVERAGE"
echo "  RAGCHECKER_BM25_BOOST_ANCHORS: $RAGCHECKER_BM25_BOOST_ANCHORS"
echo "  RAGCHECKER_ENABLE_FUSED_SCORER: $RAGCHECKER_ENABLE_FUSED_SCORER"

echo ""
echo "🚀 Running evaluation with precision push configuration..."
echo "=========================================================="

# Run the evaluation
source venv/bin/activate
python3 scripts/ragchecker_production_evaluation.py
