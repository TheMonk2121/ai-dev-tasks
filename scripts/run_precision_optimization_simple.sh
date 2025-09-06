#!/bin/bash

# Precision Optimization - Simple A/B Testing
# Based on analysis: Need +1.8 precision points to clear Haiku baseline
# Current: P=0.117, R=0.165, F1=0.133
# Target: P≥0.135, R~0.16, F1≥0.145

set -e

echo "🎯 Precision Optimization - Simple A/B Testing"
echo "==============================================="
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

echo "🚀 Testing optimized configuration..."
echo ""

# Test the recommended configuration from analysis
echo "🔧 Applying recommended precision optimization:"
echo "   CE_WEIGHT=0.28 (up from 0.16)"
echo "   RERANK_TOP_N=10 (down from 80)"
echo "   BM25_ANCHOR=1.3 (down from 1.9)"
echo "   RETRIEVER_TOP_K=100"
echo "   MMR_LAMBDA=0.2"
echo "   ANSWER_EVIDENCE_GATE=0.60"
echo ""

# Set optimized configuration
export RAGCHECKER_CE_WEIGHT=0.28
export RERANK_TOP_N=10
export RAGCHECKER_BM25_BOOST_ANCHORS=1.3
export RAGCHECKER_CE_RERANK_TOPN=10
export RETRIEVER_TOP_K=100
export MMR_LAMBDA=0.2
export ANSWER_EVIDENCE_GATE=0.60

# Run evaluation
echo "🚀 Running evaluation with optimized configuration..."
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli

echo ""
echo "📊 Check results for:"
echo "  - Precision: Should be ≥0.135 (target)"
echo "  - Recall: Should be ~0.16 (maintain current level)"
echo "  - F1 Score: Should be ≥0.145 (target)"
echo ""
echo "🎯 If targets are met, this configuration can be applied to production!"
