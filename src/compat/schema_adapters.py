# src/compat/schema_adapters.py
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from src.schemas.eval import EvaluationResult, GoldCase

# ---- Legacy "Case" (minimal) ----------------------------------------------
# If some code still imports evals/load_cases.Case (dataclass),
# we provide a dict shape they expect. Replace gradually.


def goldcase_to_legacy_case_dict(gc: GoldCase) -> dict[str, Any]:
    """Map canonical -> legacy minimal Case dict."""
    return {
        "id": gc.id,
        "query": gc.query,
        "tags": gc.tags,
        "category": gc.category,
        # Leave supervision fields available; legacy consumers may ignore
        "gt_answer": gc.gt_answer,
        "expected_files": gc.expected_files,
        "globs": gc.globs,
        "expected_decisions": gc.expected_decisions,
        "mode": gc.mode.value,
        "notes": gc.notes,
    }


def legacy_payload_to_goldcase(payload: dict[str, Any]) -> GoldCase:
    """Accept any legacy keys (question, case_id, tag, response, expected_answer, etc.)."""
    return GoldCase.parse_obj(payload)


# ---- DSPy / RAGChecker TypedDicts ------------------------------------------


def goldcase_for_dspy(gc: GoldCase) -> dict[str, Any]:
    # Some DSPy utils expect "question" and "id"
    return {
        "id": gc.id,
        "question": gc.query,
        "tags": gc.tags,
        "category": gc.category,
        "expected_files": gc.expected_files,
        "globs": gc.globs,
        "expected_decisions": gc.expected_decisions,
        "gt_answer": gc.gt_answer,
        "mode": gc.mode.value,
        "notes": gc.notes,
    }


def goldcase_for_ragchecker(gc: GoldCase) -> dict[str, Any]:
    # RAGChecker variants sometimes use "query" and "gt_answer"
    return gc.dict(by_alias=True, exclude_none=True)
