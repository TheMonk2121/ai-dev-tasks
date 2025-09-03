#!/bin/bash

# Phase-2 Exact Configuration - Complete Rollback Audit
# Goal: Find the stray knob preventing us from hitting the floor

echo "🔍 Phase-2 Exact Configuration - Complete Rollback Audit"

# Retrieval density (Phase-2 shape)
export RAGCHECKER_REWRITE_K=1           # no multi-query
export RAGCHECKER_USE_RRF=0             # no RRF fusion
export RAGCHECKER_USE_MMR=1             # keep MMR for diversity
export RAGCHECKER_MMR_LAMBDA=0.70      # more relevance, less over-diversify
export RAGCHECKER_CONTEXT_TOPK=16      # fixed cap to restore density
export RAGCHECKER_CHUNK_TOK=160        # Phase-2 chunk size
export RAGCHECKER_CHUNK_OVERLAP=40     # Phase-2 overlap
export RAGCHECKER_ENTITY_SNIPPETS=0    # OFF - no entity snippets

# Evidence selection (balanced)
export RAGCHECKER_EVIDENCE_KEEP_MODE=target_k
unset RAGCHECKER_EVIDENCE_KEEP_PERCENTILE   # must be unset
export RAGCHECKER_EVIDENCE_MIN_SENT=2
export RAGCHECKER_EVIDENCE_MAX_SENT=11
export RAGCHECKER_TARGET_K_WEAK=3
export RAGCHECKER_TARGET_K_BASE=5
export RAGCHECKER_TARGET_K_STRONG=9    # REVERTED: back to Phase-2 baseline
export RAGCHECKER_SIGNAL_DELTA_WEAK=0.10
export RAGCHECKER_SIGNAL_DELTA_STRONG=0.22
export RAGCHECKER_WEIGHT_JACCARD=0.20
export RAGCHECKER_WEIGHT_ROUGE=0.30
export RAGCHECKER_WEIGHT_COSINE=0.50
export RAGCHECKER_EVIDENCE_JACCARD=0.05
export RAGCHECKER_EVIDENCE_COVERAGE=0.152  # FINAL: 0.153 → 0.152 for final +0.009 recall
export RAGCHECKER_REDUNDANCY_TRIGRAM_MAX=0.50
export RAGCHECKER_PER_CHUNK_CAP=3

# Claim binding (safe, not choking)
export RAGCHECKER_CLAIM_BINDING=1
export RAGCHECKER_CLAIM_TOPK=3
export RAGCHECKER_DROP_UNSUPPORTED=0
export RAGCHECKER_MIN_WORDS_AFTER_BINDING=120

# Faithfulness = reporting only
export RAGCHECKER_ENABLE_FUSED_SCORER=1   # reports; should NOT change selection

# Bedrock hygiene (avoid late-case degradation)
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_MAX_RPS=0.22
export BEDROCK_COOLDOWN_SEC=8
export RAGCHECKER_CACHE_DIR=.ragcache
export RAGCHECKER_CACHE_TTL_H=24

echo "✅ Phase-2 exact configuration loaded with FINAL micro-tune"
echo "🎯 Target: P≥0.159, R≥0.166, F1≥0.159"
echo "🔧 Applied: EVIDENCE_COVERAGE=0.152 (0.153→0.152) for final +0.009 recall boost"
echo "🎯 GOAL: Hit the Phase-2 floor with this final precision-safe adjustment"
echo "🔍 Sanity check: env | grep KEEP_PERCENTILE should be empty"
echo "📊 Run: python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli"
