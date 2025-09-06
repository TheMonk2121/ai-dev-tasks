#!/usr/bin/env bash
# Precision Recovery Step 3: Add Adaptive TOPK Based on Facet Agreement
# Adds adaptive TOPK only when facets agree

set -e

echo "🎯 Precision Recovery Step 3: Adaptive TOPK on Facet Agreement"
echo "============================================================="

# Set AWS region for Bedrock
export AWS_REGION=us-east-1

# Apply Step 3 configuration
echo "📋 Applying Step 3 configuration..."
python3 scripts/precision_recovery_config.py 3

echo ""
echo "🚀 Running precision recovery evaluation (Step 3)..."
echo "Expected: +0.01-0.03 recall (precision neutral/slight +)"
echo ""

# Run the evaluation (respect RAGCHECKER_FAST_MODE)
FAST_FLAG=
if [ "${RAGCHECKER_FAST_MODE:-1}" = "1" ]; then
  FAST_FLAG="--fast-mode"
fi

python3 scripts/ragchecker_precision_recovery_evaluation.py \
    --step 3 \
    ${FAST_FLAG} \
    --output "metrics/baseline_evaluations/precision_recovery_step3_$(date +%s).json"

echo ""
echo "✅ Step 3 evaluation complete!"
echo ""
echo "📊 Final results analysis:"
echo "   - Check if R ~0.20-0.25 with P ≥ 0.135"
echo "   - Verify fusion_gain > 0 across cases"
echo "   - Confirm facet yield improvements"
echo ""
echo "🔍 To view detailed results:"
echo "   ls -la metrics/baseline_evaluations/precision_recovery_step3_*.json"
echo ""
echo "🎉 If targets met, precision recovery is complete!"
