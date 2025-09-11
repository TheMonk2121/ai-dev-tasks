# Product Requirements Document: B-1012 LTST Memory System – Foundation for Hybrid Retrieval & Closed-Loop Lessons
<!-- parent_backlog: B-1012 -->

> Auto-Skip Note: Points ≥5; PRD required.

## 0. Project Context & Implementation Guide
- Backend: Python 3.12, DSPy 3.x, PostgreSQL + pgvector
- Current: LTST provides conversation persistence/session/context merge
- This PRD aligns LTST as a lightweight foundation for B‑1025/B‑1026

## 1. Problem Statement
We need flags, hooks, instrumentation, and an eval seed to enable hybrid retrieval (B‑1025) and lessons capture (B‑1026) without overbuilding schema or indexing.

## 2. Solution Overview
- Add feature flags: FEATURE_HYBRID, FEATURE_RERANK, FEATURE_ROLLING_SUMMARY, FEATURE_FACTS (default off)
- Expose hook points in `memory_rehydrator.py` for HybridRetriever, Reranker, Rolling Summary, Facts
- Seed 100‑query eval set; add lightweight logging (dense/sparse winner fields reserved, reranker deltas placeholder, p50/p90)
- Keep pgvector exact; lexical as Postgres FTS; no BM25/HNSW/pruner

## 3. Acceptance Criteria
- Interfaces: pluggable hooks present (retriever, reranker, summary, facts)
- Flags exist (default off)
- `tests/data/eval_queries.jsonl` present with 100 queries+golds
- Logging includes candidate counts placeholders, p50/p90 timers
- No heavy schema; no regressions with flags off

## 4. Technical Approach
- Update `src/utils/memory_rehydrator.py` to add hook call sites
- Add flags via env and read in rehydrator/model_switcher
- Create eval seed file and simple harness shell
- Ensure indexing remains exact vector + FTS only

## 5. Risks & Mitigation
- Scope creep → enforce “no new tables/indexes”
- Perf regression → flags default off; measure p50/p90

## 6. Testing Strategy
- Unit: flags reading, hook invocation
- Integration: baseline run unchanged with flags off
- Artifact check: eval file exists

## 7. Implementation Plan
1) Flags + Hook scaffolding
2) Eval seed + minimal harness
3) Logging additions

## Dependencies
- B‑1006‑A (DSPy 3.x)

## Rollback
- Remove/ignore flags; hooks no‑op
