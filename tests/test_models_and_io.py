"""Comprehensive tests for Pydantic models and I/O operations."""

from pathlib import Path
from typing import Any

# Import QAAnswer directly to avoid agent initialization
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from pydantic_ai.models.test import TestModel

from src.schemas.eval import CaseResult, EvaluationRun, RerankerConfig, RetrievalCandidate


class QAAnswer(BaseModel):
    """Structured answer output for QA tasks."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float | None = None


def test_roundtrip_json(tmp_path: Path):
    """Test JSON round-trip serialization."""
    run = EvaluationRun(
        profile="gold",
        pass_id="p1",
        reranker=RerankerConfig(),
        started_at=__import__("datetime").datetime.utcnow(),
        cases=[CaseResult(case_id="1", mode="rag", query="hi")],
    )
    p = tmp_path / "run.json"
    p.write_text(run.model_dump_json(indent=2, exclude={"n_cases"}))
    loaded = EvaluationRun.model_validate_json(p.read_text())
    assert loaded.n_cases == 1


def test_list_validation() -> Any:
    """Test list validation with TypeAdapter."""
    raw = [{"doc_id": "A", "score": 0.7, "chunk": "x"}]
    ta = TypeAdapter(list[RetrievalCandidate])
    items: Any = ta.validate_python(raw)
    assert items[0].doc_id == "A"


def test_qa_answer_schema() -> Any:
    """Test QAAnswer schema validation."""
    # Test valid QAAnswer
    answer = QAAnswer(answer="This is a test answer", confidence=0.95)
    assert answer.answer == "This is a test answer"
    assert answer.confidence == 0.95

    # Test validation
    from pydantic import ValidationError

    try:
        QAAnswer(answer="", confidence=0.5)  # empty answer should fail
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass


def test_strict_validation() -> Any:
    """Test strict validation prevents invalid data."""
    from pydantic import ValidationError

    # This should fail due to strict validation
    try:
        CaseResult(case_id="", mode="rag", query="")  # empty strings should fail
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass


def test_computed_field() -> Any:
    """Test computed fields work correctly."""
    run = EvaluationRun(
        profile="test",
        pass_id="p1",
        reranker=RerankerConfig(),
        started_at=__import__("datetime").datetime.utcnow(),
        cases=[
            CaseResult(case_id="1", mode="rag", query="q1"),
            CaseResult(case_id="2", mode="rag", query="q2"),
        ],
    )
    assert run.n_cases == 2


def test_non_empty_string_validation() -> Any:
    """Test NonEmptyStr validation."""
    from pydantic import ValidationError

    try:
        RetrievalCandidate(doc_id="", score=0.5, chunk="test")  # empty doc_id should fail
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass


def test_extra_forbid() -> Any:
    """Test that extra fields are forbidden."""
    from pydantic import ValidationError

    try:
        # This should fail due to extra="forbid" in model_config
        CaseResult(case_id="test", mode="rag", query="test", extra_field="should_fail")  # type: ignore
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass
