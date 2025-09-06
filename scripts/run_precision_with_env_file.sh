#!/bin/bash

# Precision Optimization - Using RAGCHECKER_ENV_FILE
# Points RAGCHECKER_ENV_FILE to our optimized configuration

set -e

echo "🎯 Precision Optimization - Using RAGCHECKER_ENV_FILE"
echo "===================================================="
echo "Pointing RAGCHECKER_ENV_FILE to optimized configuration"
echo ""

# Set up base environment
export AWS_REGION=us-east-1
export POSTGRES_DSN="mock://test"

# Point to our optimized configuration
export RAGCHECKER_ENV_FILE="configs/precision_optimized_bedrock_correct.env"

echo "🔧 Using optimized configuration file: $RAGCHECKER_ENV_FILE"
echo ""

# Run evaluation - this should now load our optimized config
echo "🚀 Running evaluation with optimized configuration..."
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli

echo ""
echo "📊 Check results for:"
echo "  - Precision: Should be ≥0.135 (target: +1.8 points from 0.117)"
echo "  - Recall: Should be ~0.16 (maintain current level)"
echo "  - F1 Score: Should be ≥0.145 (target: +1.2 points from 0.133)"
echo ""
echo "🎯 If targets are met, this configuration can be applied to production!"
