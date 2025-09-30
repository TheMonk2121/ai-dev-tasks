from __future__ import annotations

from datetime import datetime

from src.schemas.eval import (
    CaseResult,
    ContextChunk,
    EvaluationRun,
    RerankerConfig,
    RetrievalCandidate,
)


def make_chunk(i: int = 0) -> ContextChunk:
    return ContextChunk(
        source_id=f"doc_{i}:0",
        text=f"content {i}",
        start=0,
        end=10,
    )


def make_candidate(_q: str = "q", i: int = 0) -> RetrievalCandidate:
    chunk = make_chunk(i)
    return RetrievalCandidate(
        doc_id=f"doc_{i}",
        score=0.9,
        title=f"Document {i}",
        url=f"https://example.com/doc_{i}",
        chunk=chunk.text
    )


def make_case_result(case_id: str = "case_1", q: str = "q", k: int = 3) -> CaseResult:
    cands: list[RetrievalCandidate] = [make_candidate(q, i) for i in range(k)]
    chunks: list[ContextChunk] = [make_chunk(i) for i in range(k)]
    return CaseResult(
        case_id=case_id,
        mode="rag",
        query=q,
        predicted_answer="answer",
        retrieved_context=chunks,
        retrieval_snapshot=cands,
        precision=0.8,
        recall=0.7,
        f1=0.75,
        faithfulness=0.9,
        answer_latency_ms=100,
    )


def make_eval_run() -> EvaluationRun:
    rr = RerankerConfig()
    return EvaluationRun(
        profile="default",
        pass_id="test_pass",
        driver="dspy_rag",
        reranker=rr,
        seed=123,
        started_at=datetime(2025, 1, 1, 0, 0, 0),
        finished_at=None,
        overall={"precision": 0.0},
        artifact_paths={"results_json": "metrics/x.json"},
    )
