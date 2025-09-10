from __future__ import annotations

import pytest

from src.schemas.eval import CaseResult, ContextChunk, EvaluationRun, RerankerConfig, RetrievalCandidate


@pytest.mark.critical
def test_roundtrip_case_result():
    chunk = ContextChunk(id="doc_1:0", source="/path/file.md", text="hello world", score=0.9, metadata={})
    rc = RetrievalCandidate(query="q", chunk=chunk, rank=1, score=0.9, route="hybrid")
    c = CaseResult(
        id="case_1",
        mode="retrieval",
        tags=["smoke"],
        query="q",
        predicted_answer="a",
        retrieved_context=[chunk],
        retrieval_snapshot=[rc],
        metrics={"precision": 0.1, "recall": 0.2, "f1": 0.13},
        timings={"retrieval_ms": 10},
    )
    js = c.model_dump_json()
    c2 = CaseResult.model_validate_json(js)
    assert c2 == c


def test_roundtrip_evaluation_run():
    rr = RerankerConfig()
    er = EvaluationRun(
        profile="default",
        driver="dspy_rag",
        reranker=rr,
        seed=42,
        started_at="2025-01-01T00:00:00",
        finished_at=None,
        overall={"precision": 0.1},
        artifact_paths={"results_json": "metrics/foo.json"},
    )
    js = er.model_dump_json()
    er2 = EvaluationRun.model_validate_json(js)
    assert er2 == er


import json
import sys

sys.path.append(".")
from src.compat.schema_adapters import goldcase_to_legacy_case_dict, legacy_payload_to_goldcase
from src.schemas.eval import EvaluationResult, GoldCase, Mode


def test_alias_loading_and_roundtrip():
    legacy = {
        "case_id": "C1",
        "question": "How do I run the evals?",
        "tag": "ops_health",
        "mode": "reader",
        "response": "Use scripts/ragchecker_official_evaluation.py ...",
    }
    gc = GoldCase.parse_obj(legacy)
    assert gc.id == "C1"
    assert gc.query.startswith("How do I run")
    assert gc.tags == ["ops_health"]
    assert gc.mode == Mode.reader
    assert gc.gt_answer and "scripts/ragchecker_official_evaluation.py" in gc.gt_answer

    back = goldcase_to_legacy_case_dict(gc)
    assert back["id"] == "C1"
    assert back["query"] == gc.query
    assert back["gt_answer"] == gc.gt_answer


def test_result_model_minimal():
    res = EvaluationResult(
        id="C2", mode=Mode.retrieval, tags=["rag_qa_single"], query="List the core workflow guides in 000_core."
    )
    payload = res.dict()
    assert payload["id"] == "C2"
