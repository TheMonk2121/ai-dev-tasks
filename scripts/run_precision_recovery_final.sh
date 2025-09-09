#!/usr/bin/env bash
# Precision Recovery Final: Tighten Selection for Precision Target
# Since recall is excellent (0.263 vs 0.160), we can tighten selection

set -e

echo "🎯 Precision Recovery Final: Tighten Selection for Precision Target"
echo "=================================================================="

# Set AWS region for Bedrock
export AWS_REGION=us-east-1

# Apply tighter precision-focused configuration
echo "📋 Applying precision-focused configuration..."
bin/py scripts/precision_recovery_config.py 1

# Tighten selection parameters for precision
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX=0.40     # 0.45 → 0.40 (tighter)
export RAGCHECKER_PER_CHUNK_CAP=1                 # 2 → 1 (stricter)
export RAGCHECKER_MIN_WORDS_AFTER_BINDING=160     # 140 → 160 (more selective)
export RAGCHECKER_TARGET_K_STRONG=7               # 8 → 7 (precision focus)
export RAGCHECKER_CONTEXT_TOPK=14                 # 16 → 14 (tighter)

echo "Set RAGCHECKER_REDUNDANCY_TRIGRAM_MAX=0.40"
echo "Set RAGCHECKER_PER_CHUNK_CAP=1"
echo "Set RAGCHECKER_MIN_WORDS_AFTER_BINDING=160"
echo "Set RAGCHECKER_TARGET_K_STRONG=7"
echo "Set RAGCHECKER_CONTEXT_TOPK=14"

echo ""
echo "🚀 Running precision-focused evaluation..."
echo "Expected: P rises to ≥0.135, R may dip slightly but stay above 0.160"
echo ""

# Run the evaluation (respect RAGCHECKER_FAST_MODE)
FAST_FLAG=
if [ "${RAGCHECKER_FAST_MODE:-1}" = "1" ]; then
  FAST_FLAG="--fast-mode"
fi

bin/py scripts/ragchecker_precision_recovery_evaluation.py \
    --step 1 \
    ${FAST_FLAG} \
    --output "metrics/baseline_evaluations/precision_recovery_final_$(date +%s).json"

echo ""
echo "✅ Final precision recovery evaluation complete!"
echo ""
echo "📊 Check results - if P ≥ 0.135 and R ≥ 0.160, we've achieved full compliance!"
echo ""
echo "🔍 To view detailed results:"
echo "   ls -la metrics/baseline_evaluations/precision_recovery_final_*.json"
