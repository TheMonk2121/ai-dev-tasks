#!/usr/bin/env bash

# Phase 1 RAGChecker Enhancement Flags
export RAGCHECKER_CONCISE=1          # Enable concise response generation
export RAGCHECKER_MAX_WORDS=500      # Limit responses to 500 words
export RAGCHECKER_ROBUST_PARSER=1    # Use improved score parser
export RAGCHECKER_REQUIRE_CITATIONS=1 # Require citation of sources
export RAGCHECKER_CONTEXT_TOPK=3     # Use top 3 context chunks

echo '✅ Phase 1 flags configured:'
echo '  RAGCHECKER_CONCISE: ' $RAGCHECKER_CONCISE
echo '  RAGCHECKER_MAX_WORDS: ' $RAGCHECKER_MAX_WORDS
echo '  RAGCHECKER_ROBUST_PARSER: ' $RAGCHECKER_ROBUST_PARSER
echo '  RAGCHECKER_REQUIRE_CITATIONS: ' $RAGCHECKER_REQUIRE_CITATIONS
echo '  RAGCHECKER_CONTEXT_TOPK: ' $RAGCHECKER_CONTEXT_TOPK
