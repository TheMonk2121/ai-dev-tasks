#!/usr/bin/env bash
set -euo pipefail

# 6-run testing grid for systematic recall improvement
# Based on the user's analysis of recall leak points

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/scripts}"

echo "🧪 Running 6-run recall testing grid..."
echo "======================================"

# Ensure virtual environment is active
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo "⚠️ Activating virtual environment..."
    # shellcheck disable=SC1091  # Virtual environment activation script
    source "${REPO_ROOT}/venv/bin/activate"
fi

# Function to run evaluation with specific config
run_eval() {
    local config_name="$1"
    local config_file="$2"
    local description="$3"

    echo ""
    echo "🧪 Running: $description"
    echo "Config: $config_name"
    echo "Command: source $config_file && python3 scripts/ragchecker_official_evaluation.py --use-bedrock --stable"

    # shellcheck disable=SC1090  # Dynamic config file sourcing is intentional
    if source "$config_file" && python3 "${REPO_ROOT}/scripts/ragchecker_official_evaluation.py" --use-bedrock --stable; then
        echo "✅ $config_name completed successfully"
        return 0
    else
        echo "❌ $config_name failed"
        return 1
    fi
}

# Run 1: Baseline-plus (A + C light)
echo ""
echo "📊 Run 1: Baseline-plus (A + C light)"
run_eval "baseline_plus" "${REPO_ROOT}/configs/recall_path_a.env" "Retrieval breadth + evidence budget"

# Run 2: + HyDE
echo ""
echo "📊 Run 2: + HyDE"
run_eval "hyde" "${REPO_ROOT}/configs/recall_path_b.env" "Query expansion with HyDE"

# Run 3: + PRF
echo ""
echo "📊 Run 3: + PRF"
# Create PRF-only config
cat > "${REPO_ROOT}/configs/recall_path_b_prf.env" << 'EOF'
# Path B: PRF only (no HyDE)
export PRF_ENABLE=1
export PRF_TOPN=8
export PRF_TERMS=10
export PRF_WEIGHT=0.35

# Include Path A settings
export RETR_TOPK_VEC=140
export RETR_TOPK_BM25=140
export FUSION_METHOD=RRF
export RRF_K=60
export RERANK_ENABLE=1
export RERANK_TOPN=18

# Conservative settings
export PIPELINE_WORKERS=2
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_MAX_RPS=0.12
export RAGCHECKER_BYPASS_CLI=1
export RAGCHECKER_DISABLE_EMBEDDINGS=1
EOF

run_eval "prf" "${REPO_ROOT}/configs/recall_path_b_prf.env" "Pseudo-relevance feedback"

# Run 4: Aggressive K, conservative rerank
echo ""
echo "📊 Run 4: Aggressive K, conservative rerank"
cat > "${REPO_ROOT}/configs/recall_aggressive_k.env" << 'EOF'
# Aggressive K with conservative rerank
export RETR_TOPK_VEC=220
export RETR_TOPK_BM25=220
export FUSION_METHOD=RRF
export RRF_K=60
export RERANK_ENABLE=1
export RERANK_TOPN=16

# Conservative settings
export PIPELINE_WORKERS=2
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_MAX_RPS=0.12
export RAGCHECKER_BYPASS_CLI=1
export RAGCHECKER_DISABLE_EMBEDDINGS=1
EOF

run_eval "aggressive_k" "${REPO_ROOT}/configs/recall_aggressive_k.env" "Aggressive retrieval with conservative rerank"

# Run 5: Answerability safety net
echo ""
echo "📊 Run 5: Answerability safety net"
run_eval "safety_net" "${REPO_ROOT}/configs/recall_path_d.env" "Reader loop with answerability check"

# Run 6: ColBERT-lite rerank (if available) or bge-large
echo ""
echo "📊 Run 6: Enhanced reranker"
cat > "${REPO_ROOT}/configs/recall_enhanced_rerank.env" << 'EOF'
# Enhanced reranker
export RETR_TOPK_VEC=140
export RETR_TOPK_BM25=140
export FUSION_METHOD=RRF
export RRF_K=60
export RERANK_ENABLE=1
export RERANK_MODEL=bge-reranker-large
export RERANK_TOPN=18

# Conservative settings
export PIPELINE_WORKERS=2
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_MAX_RPS=0.12
export RAGCHECKER_BYPASS_CLI=1
export RAGCHECKER_DISABLE_EMBEDDINGS=1
EOF

run_eval "enhanced_rerank" "${REPO_ROOT}/configs/recall_enhanced_rerank.env" "Enhanced reranker (bge-large)"

echo ""
echo "🎯 Testing grid completed!"
echo "========================="
echo "Check metrics/baseline_evaluations/ for results"
echo "Look for oracle hit metrics to identify recall leak points:"
echo "  - retrieval_oracle_hit: <85% → widen K/fusion"
echo "  - filter_oracle_hit: <75% → adjust filter knobs"
echo "  - reader_used_gold: <80% → improve generation loop"
