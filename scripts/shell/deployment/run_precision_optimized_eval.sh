#!/bin/bash

# Precision Optimized Evaluation
# Uses the precision_optimized_bedrock.env configuration

set -e

echo "🎯 Precision Optimized Evaluation"
echo "=================================="
echo "Using precision_optimized_bedrock.env configuration"
echo ""

# Set up base environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Set the optimized configuration file
export RAGCHECKER_ENV_FILE="configs/precision_optimized_bedrock.env"

echo "🔧 Loading precision optimized configuration..."
echo "   CE_WEIGHT=0.28 (up from 0.16)"
echo "   RERANK_TOP_N=10 (down from 80)"
echo "   BM25_ANCHOR=1.3 (down from 1.9)"
echo "   RETRIEVER_TOP_K=100"
echo "   MMR_LAMBDA=0.2"
echo "   ANSWER_EVIDENCE_GATE=0.60"
echo ""

# Run evaluation with optimized configuration
echo "🚀 Running evaluation with precision optimized configuration..."
bin/py scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable

echo ""
echo "📊 Check results for:"
echo "  - Precision: Should be ≥0.135 (target: +1.8 points from 0.117)"
echo "  - Recall: Should be ~0.16 (maintain current level)"
echo "  - F1 Score: Should be ≥0.145 (target: +1.2 points from 0.133)"
echo ""
echo "🎯 If targets are met, this configuration can be applied to production!"
