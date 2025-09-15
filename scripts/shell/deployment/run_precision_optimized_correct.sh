#!/bin/bash

# Precision Optimized Evaluation - CORRECT VARIABLE NAMES
# Uses the precision_optimized_bedrock_correct.env configuration

set -e

echo "🎯 Precision Optimized Evaluation - CORRECT VARIABLES"
echo "====================================================="
echo "Using precision_optimized_bedrock_correct.env configuration"
echo ""

# Set up base environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Set the optimized configuration file
export RAGCHECKER_ENV_FILE="300_evals/configs/precision_optimized_bedrock_correct.env"

echo "🔧 Loading precision optimized configuration (correct variables)..."
echo "   RAGCHECKER_CONCISE=1 (response limiting)"
echo "   RAGCHECKER_EVIDENCE_GUARD=1 (evidence selection)"
echo "   RAGCHECKER_CLAIM_BINDING=1 (claim binding)"
echo "   RAGCHECKER_DROP_UNSUPPORTED=1 (drop unsupported claims)"
echo "   RAGCHECKER_FAST_MODE=1 (precision focus)"
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
