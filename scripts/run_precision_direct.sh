#!/bin/bash

# Precision Optimization - Direct Environment Variables
# Bypasses all shell scripts that might override our settings

set -e

echo "🎯 Precision Optimization - Direct Environment Variables"
echo "========================================================"
echo "Bypassing all shell scripts that might override settings"
echo ""

# Set up base environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Base Bedrock configuration
export USE_BEDROCK_QUEUE=1
export ASYNC_MAX_CONCURRENCY=1
export BEDROCK_MAX_CONCURRENCY=1
export BEDROCK_MAX_RPS=0.15
export BEDROCK_COOLDOWN_SEC=30
export BEDROCK_RETRY_MAX=8
export BEDROCK_RETRY_BASE=1.8
export BEDROCK_RETRY_MAX_SLEEP=20
export BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# RAGChecker configuration - DIRECT SETTINGS
echo "🔧 Setting RAGChecker configuration directly..."

# Disable coverage rewrite
export RAGCHECKER_COVERAGE_REWRITE=0

# JSON settings
export RAGCHECKER_JSON_PROMPTS=0
export RAGCHECKER_JSON_MAX_TOKENS=200

# PRECISION OPTIMIZATION SETTINGS
export RAGCHECKER_CONCISE=1
export RAGCHECKER_MAX_WORDS=1000
export RAGCHECKER_ROBUST_PARSER=1
export RAGCHECKER_EVIDENCE_GUARD=1
export RAGCHECKER_CLAIM_BINDING=1
export RAGCHECKER_DROP_UNSUPPORTED=1
export RAGCHECKER_SEMANTIC_FEATURES=1
export RAGCHECKER_USE_EMBED_GUARD=1
export RAGCHECKER_USE_ROUGE_L=1
export RAGCHECKER_REQUIRE_CITATIONS=1
# Respect pre-set fast mode; default to 1 for direct run
export RAGCHECKER_FAST_MODE="${RAGCHECKER_FAST_MODE:-1}"

# Evidence selection (keep minimal for precision)
export RAGCHECKER_EVIDENCE_JACCARD=0.05
export RAGCHECKER_EVIDENCE_COVERAGE=0.15

echo "✅ Direct configuration applied:"
echo "   RAGCHECKER_CONCISE=1 (response limiting)"
echo "   RAGCHECKER_EVIDENCE_GUARD=1 (evidence selection)"
echo "   RAGCHECKER_CLAIM_BINDING=1 (claim binding)"
echo "   RAGCHECKER_DROP_UNSUPPORTED=1 (drop unsupported claims)"
echo "   RAGCHECKER_FAST_MODE=${RAGCHECKER_FAST_MODE} (precision focus)"
echo "   RAGCHECKER_EVIDENCE_JACCARD=0.05 (tighter evidence)"
echo "   RAGCHECKER_EVIDENCE_COVERAGE=0.15 (tighter coverage)"
echo ""

# Run evaluation WITHOUT --stable flag to avoid loading stable config
echo "🚀 Running evaluation with direct precision optimization..."
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli

echo ""
echo "📊 Check results for:"
echo "  - Precision: Should be ≥0.135 (target: +1.8 points from 0.117)"
echo "  - Recall: Should be ~0.16 (maintain current level)"
echo "  - F1 Score: Should be ≥0.145 (target: +1.2 points from 0.133)"
echo ""
echo "🎯 If targets are met, this configuration can be applied to production!"
