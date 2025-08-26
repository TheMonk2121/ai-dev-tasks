# Product Requirements Document: B-1025 Lean Hybrid Memory System
<!-- parent_backlog: B-1025 -->

> Auto-Skip Note: Points ≥5; PRD required.

## 0. Context
- Build on B‑1012 hooks/flags to deliver hybrid union + reranker + light facts + rolling summary

## 1. Problem
LTST ranking (relevance+recency) underperforms hybrid retrieval; need measurable lift with minimal schema.

## 2. Solution
- Retrieval: dense (pgvector exact) ∪ sparse (Postgres FTS via websearch_to_tsquery)
- Rerank: local cross‑encoder (BAAI/bge‑reranker‑base ONNX INT8); recency tiebreak
- Light facts: versioned upsert; tiny CLI
- Rolling summary: 200–300 tokens; cadence 4–6 turns/idle ≥10s; pin at edge
- Flags: FEATURE_HYBRID, FEATURE_RERANK, FEATURE_ROLLING_SUMMARY, FEATURE_FACTS (default off)

## 3. Acceptance
- Storage: only messages + facts created and indexed; no episodic/pruner
- Quality: +15–25% Recall@10 or +10% MRR@10 vs LTST (100‑query eval)
- Perf: ≤ +300 ms p50 added; < 2 s end‑to‑end
- Observability: candidate counts, winner source, reranker deltas, p50/p90
- Naming: lexical is “Postgres FTS (tsvector + ts_rank)”

## 4. Technical Approach
- SQL: messages (fts generated col + GIN), facts with active index
- Python: `HybridRetriever`, `CrossEncoderReranker`, summary module; integrate in `memory_rehydrator.py`
- Optional RRF if reranker disabled

## 5. Risks
- Latency budget → batch rerank; keep k≈40; measure
- Overbuild → no BM25/HNSW/pruner here

## 6. Tests
- A/B harness LTST vs Hybrid+Rerank; Recall/MRR/NDCG@k, latency p50/p90
- Facts upsert/versioning unit tests
- Summary placement tests

## 7. Plan
1) Schema (messages/facts)
2) Hybrid union + de‑dup
3) Reranker + recency tiebreak
4) Rolling summary
5) A/B & accept

## Flags & Rollback
- Flags default off; one‑flip rollback to LTST
