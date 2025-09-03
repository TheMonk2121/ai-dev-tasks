#!/bin/bash

# Phase-2 Rollback Configuration - Restore Stable Floor
# Goal: Snap metrics back to Phase-2 baseline (P≈0.16+, R≈0.16+, F1≈0.159+)

echo "🔄 Rolling back to Phase-2 stable configuration..."

# Retrieval rollback - disable noisy multi-query and RRF
export RAGCHECKER_REWRITE_K=1          # disable multi-query for now
export RAGCHECKER_USE_RRF=0             # disable RRF fusion
export RAGCHECKER_USE_MMR=1             # keep MMR for diversity
export RAGCHECKER_MMR_LAMBDA=0.70      # more relevance, less over-diversify
export RAGCHECKER_CONTEXT_TOPK=16      # fixed cap to restore density

# Chunking rollback - denser facts per span
export RAGCHECKER_CHUNK_TOK=160
export RAGCHECKER_CHUNK_OVERLAP=40
export RAGCHECKER_ENTITY_SNIPPETS=0    # off until we prove value

# Evidence selection - Phase-2 balanced
export RAGCHECKER_EVIDENCE_KEEP_MODE=target_k
unset RAGCHECKER_EVIDENCE_KEEP_PERCENTILE
export RAGCHECKER_EVIDENCE_MIN_SENT=2
export RAGCHECKER_EVIDENCE_MAX_SENT=11
export RAGCHECKER_WEIGHT_JACCARD=0.20
export RAGCHECKER_WEIGHT_ROUGE=0.30
export RAGCHECKER_WEIGHT_COSINE=0.50
export RAGCHECKER_EVIDENCE_JACCARD=0.05
export RAGCHECKER_EVIDENCE_COVERAGE=0.16
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX=0.50
export RAGCHECKER_PER_CHUNK_CAP=3

# Claim binding - loosened but safe
export RAGCHECKER_CLAIM_BINDING=1
export RAGCHECKER_CLAIM_TOPK=3
export RAGCHECKER_DROP_UNSUPPORTED=0
export RAGCHECKER_MIN_WORDS_AFTER_BINDING=120

# Bedrock hygiene & caching
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_MAX_RPS=0.22
export BEDROCK_COOLDOWN_SEC=8
export RAGCHECKER_CACHE_DIR=.ragcache
export RAGCHECKER_CACHE_TTL_H=24

echo "✅ Phase-2 rollback complete"
echo "🎯 Target: P≈0.16+, R≈0.16+, F1≈0.159+"
echo "📊 Run: python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli"
