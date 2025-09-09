from __future__ import annotations

from typing import List

from src.schemas.eval import (
    CaseResult,
    ContextChunk,
    EvaluationRun,
    RerankerConfig,
    RetrievalCandidate,
)


def make_chunk(i: int = 0) -> ContextChunk:
    return ContextChunk(
        id=f"doc_{i}:0",
        source=f"/path/file_{i}.md",
        text=f"content {i}",
        score=0.9,
        metadata={"i": i},
    )


def make_candidate(q: str = "q", i: int = 0) -> RetrievalCandidate:
    chunk = make_chunk(i)
    return RetrievalCandidate(query=q, chunk=chunk, rank=i + 1, score=0.9, route="hybrid")


def make_case_result(case_id: str = "case_1", q: str = "q", k: int = 3) -> CaseResult:
    cands: List[RetrievalCandidate] = [make_candidate(q, i) for i in range(k)]
    chunks: List[ContextChunk] = [c.chunk for c in cands]
    return CaseResult(
        id=case_id,
        mode="retrieval",
        tags=["smoke"],
        query=q,
        predicted_answer="",
        retrieved_context=chunks,
        retrieval_snapshot=cands,
        metrics={"precision": 0.0, "recall": 0.0, "f1": 0.0},
        timings={},
    )


def make_eval_run() -> EvaluationRun:
    rr = RerankerConfig()
    return EvaluationRun(
        profile="default",
        driver="dspy_rag",
        reranker=rr,
        seed=123,
        started_at="2025-01-01T00:00:00",
        finished_at=None,
        overall={"precision": 0.0},
        artifact_paths={"results_json": "metrics/x.json"},
    )
