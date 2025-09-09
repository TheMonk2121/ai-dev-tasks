from __future__ import annotations

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
