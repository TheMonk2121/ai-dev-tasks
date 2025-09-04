#!/bin/bash
# Precision Recovery Step 2: Add Selective Facet Query Decomposition
# Adds facet selection with yield-based filtering

set -e

echo "🎯 Precision Recovery Step 2: Facet Query Decomposition"
echo "======================================================"

# Set AWS region for Bedrock
export AWS_REGION=us-east-1

# Apply Step 2 configuration
echo "📋 Applying Step 2 configuration..."
python3 scripts/precision_recovery_config.py 2

echo ""
echo "🚀 Running precision recovery evaluation (Step 2)..."
echo "Expected: +0.03-0.06 recall (precision neutral)"
echo ""

# Run the evaluation
python3 scripts/ragchecker_precision_recovery_evaluation.py \
    --step 2 \
    --fast-mode \
    --output "metrics/baseline_evaluations/precision_recovery_step2_$(date +%s).json"

echo ""
echo "✅ Step 2 evaluation complete!"
echo ""
echo "📊 Check results and if fusion_gain > 0 and macro R ↑, proceed to Step 3:"
echo "   ./scripts/run_precision_recovery_step3.sh"
echo ""
echo "🔍 To view detailed results:"
echo "   ls -la metrics/baseline_evaluations/precision_recovery_step2_*.json"
