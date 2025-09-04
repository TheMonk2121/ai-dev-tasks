#!/bin/bash
# Final Precision Push Evaluation
# Aggressive precision improvements to achieve P ≥ 0.135 target

set -e

echo "🎯 Final Precision Push Evaluation"
echo "=================================="

# Set AWS region for Bedrock
export AWS_REGION=us-east-1

echo "📋 Applying final precision push configuration..."
python3 scripts/final_precision_push_config.py

echo ""
echo "🚀 Running final precision push evaluation..."
echo "Expected: +0.016-0.025 precision to achieve P ≥ 0.135 target"
echo "Target: P ≥ 0.135, R ≥ 0.20, F1 ≥ 0.155"
echo "Risk: ≤0.02 recall loss (maintain ≥0.20)"
echo ""

# Run the evaluation
python3 scripts/ragchecker_final_precision_push_evaluation.py \
    --fast-mode \
    --output "metrics/baseline_evaluations/final_precision_push_evaluation_$(date +%s).json"

echo ""
echo "✅ Final precision push evaluation complete!"
echo ""
echo "📊 Check results for:"
echo "   - Precision improvement (+0.016-0.025 expected)"
echo "   - Recall maintenance (≥0.20 target)"
echo "   - F1 score improvement (≥0.155 target)"
echo "   - Full baseline compliance (P ≥ 0.135, R ≥ 0.16, F1 ≥ 0.145)"
echo ""
echo "🔍 To view detailed results:"
echo "   ls -la metrics/baseline_evaluations/final_precision_push_evaluation_*.json"
