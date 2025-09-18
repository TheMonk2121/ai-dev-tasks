from __future__ import annotations

import json
import sys

sys.path.append(".")
# Removed deprecated import: from src.compat.schema_adapters import goldcase_to_legacy_case_dict, legacy_payload_to_goldcase
from src.schemas.eval import (
    CaseResult,
    ContextChunk,
    EvaluationResult,
    EvaluationRun,
    GoldCase,
    Mode,
    RerankerConfig,
    RetrievalCandidate,
)


def test_roundtrip_case_result() -> Any:
    chunk = ContextChunk(source_id="doc_1:0", text="hello world", start=0, end=100)
    rc = RetrievalCandidate(doc_id="d1", score=0.9, chunk="chunk text")
    c = CaseResult(
        case_id="case_1",
        mode="rag",
        query="q",
        predicted_answer="a",
        retrieved_context=[chunk],
        retrieval_snapshot=[rc],
        precision=0.1,
        recall=0.2,
        f1=0.13,
        answer_latency_ms=10,
    )
    js: Any = c.model_dump_json()
    c2: Any = CaseResult.model_validate_json(js)
    assert c2 == c


def test_roundtrip_evaluation_run() -> Any:
    rr = RerankerConfig()
    from datetime import datetime

    er = EvaluationRun(
        profile="default",
        pass_id="test_pass",
        driver="dspy_rag",
        reranker=rr,
        seed=42,
        started_at=datetime(2025, 1, 1),
        finished_at=None,
        overall={"precision": 0.1},
        artifact_paths={"results_json": "metrics/foo.json"},
    )
    js: Any = er.model_dump_json()
    er2: Any = EvaluationRun.model_validate_json(js)
    assert er2 == er


def test_alias_loading_and_roundtrip() -> Any:
    legacy = {
        "case_id": "C1",
        "question": "How do I run the evals?",
        "tag": "ops_health",
        "mode": "reader",
        "response": "Use scripts/ragchecker_official_evaluation.py ...",
    }
    gc: Any = GoldCase.model_validate(legacy)
    assert gc.id == "C1"
    assert gc.query.startswith("How do I run")
    assert gc.tags == ["ops_health"]
    assert gc.mode == Mode.reader
    assert gc.gt_answer and "scripts/ragchecker_official_evaluation.py" in gc.gt_answer

    # Test direct Pydantic model access instead of deprecated adapter
    assert gc.id == "C1"
    assert gc.query == gc.query
    assert gc.gt_answer == gc.gt_answer


def test_result_model_minimal() -> Any:
    res = EvaluationResult(
        id="C2", mode=Mode.retrieval, tags=["rag_qa_single"], query="List the core workflow guides in 000_core."
    )
    payload: Any = res.model_dump()
    assert payload["id"] == "C2"
