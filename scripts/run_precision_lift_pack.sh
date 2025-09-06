#!/usr/bin/env bash
# Precision Lift Pack Evaluation
# Surgical precision improvements with minimal recall loss

set -e

echo "🎯 Precision Lift Pack Evaluation"
echo "================================="

# Set AWS region for Bedrock
export AWS_REGION=us-east-1

echo "📋 Applying precision lift pack configuration..."
python3 scripts/precision_lift_pack_config.py

echo ""
echo "🚀 Running precision lift pack evaluation..."
echo "Expected: +0.01-0.03 precision with ≤0.01 recall loss"
echo "Target: P ≥ 0.135, R ≥ 0.20-0.26, F1 ≥ 0.155"
echo ""

# Run the evaluation (respect RAGCHECKER_FAST_MODE)
FAST_FLAG=
if [ "${RAGCHECKER_FAST_MODE:-1}" = "1" ]; then
  FAST_FLAG="--fast-mode"
fi

python3 scripts/ragchecker_precision_lift_evaluation.py \
    ${FAST_FLAG} \
    --output "metrics/baseline_evaluations/precision_lift_pack_evaluation_$(date +%s).json"

echo ""
echo "✅ Precision lift pack evaluation complete!"
echo ""
echo "📊 Check results for:"
echo "   - Precision improvement (+0.01-0.03 expected)"
echo "   - Recall maintenance (≤0.01 loss expected)"
echo "   - F1 score improvement"
echo "   - Baseline compliance (P ≥ 0.135, R ≥ 0.16, F1 ≥ 0.145)"
echo ""
echo "🔍 To view detailed results:"
echo "   ls -la metrics/baseline_evaluations/precision_lift_pack_evaluation_*.json"
