#!/usr/bin/env bash
# Precision Recovery Step 1: Hybrid Retrieval Only
# Implements BM25 + vector with RRF fusion for precision recovery

set -e

echo "🎯 Precision Recovery Step 1: Hybrid Retrieval Only"
echo "=================================================="

# Set AWS region for Bedrock
export AWS_REGION=us-east-1

# Apply Step 1 configuration
echo "📋 Applying Step 1 configuration..."
python3 scripts/precision_recovery_config.py 1

echo ""
echo "🚀 Running precision recovery evaluation (Step 1)..."
echo "Expected: P rises ~+0.02, R dips slightly (≤-0.01)"
echo ""

# Run the evaluation (respect RAGCHECKER_FAST_MODE)
FAST_FLAG=
if [ "${RAGCHECKER_FAST_MODE:-1}" = "1" ]; then
  FAST_FLAG="--fast-mode"
fi

python3 scripts/ragchecker_precision_recovery_evaluation.py \
    --step 1 \
    ${FAST_FLAG} \
    --output "metrics/baseline_evaluations/precision_recovery_step1_$(date +%s).json"

echo ""
echo "✅ Step 1 evaluation complete!"
echo ""
echo "📊 Check results and if P ≥ 0.135 and R ↑, proceed to Step 2:"
echo "   ./scripts/run_precision_recovery_step2.sh"
echo ""
echo "🔍 To view detailed results:"
echo "   ls -la metrics/baseline_evaluations/precision_recovery_step1_*.json"
