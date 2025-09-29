from __future__ import annotations

import json
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from src.schemas.eval import CaseResult, GoldCase, Mode

from ._regression_capture import record_case


@pytest.mark.prop
class TestSchemaTypeInvariants:
    """Property-based tests for schema type invariants and validation."""

    @given(
        case_id=st.text(min_size=1, max_size=100),
        mode=st.sampled_from(["rag", "baseline", "oracle"]),
        query=st.text(min_size=1, max_size=500),
        precision=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
        recall=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
        f1=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
        faithfulness=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_caseresult_numeric_fields_accept_only_numbers(
        self,
        case_id: str,
        mode: str,
        query: str,
        precision: float | None,
        recall: float | None,
        f1: float | None,
        faithfulness: float | None,
    ) -> None:
        """Test that CaseResult numeric fields accept only numeric values."""
        try:
            case = CaseResult(
                case_id=case_id,
                mode=mode,  # type: ignore
                query=query,
                precision=precision,
                recall=recall,
                f1=f1,
                faithfulness=faithfulness,
            )

            # Check that numeric fields are preserved correctly
            assert case.precision == precision
            assert case.recall == recall
            assert case.f1 == f1
            assert case.faithfulness == faithfulness

        except Exception as e:
            record_case(
                "caseresult_numeric_fields_failed",
                {
                    "case_id": case_id,
                    "mode": mode,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "faithfulness": faithfulness,
                    "error": str(e),
                },
            )
            raise

    @given(
        case_id=st.text(min_size=1, max_size=100),
        mode=st.sampled_from(["rag", "baseline", "oracle"]),
        query=st.text(min_size=1, max_size=500),
        precision=st.one_of(
            st.just("invalid"), st.just({"nested": "dict"}), st.lists(st.just("list")), st.just(True), st.just(False)
        ),
    )
    @settings(max_examples=10, deadline=200)
    def test_caseresult_rejects_invalid_types_for_numeric_fields(
        self, case_id: str, mode: str, query: str, precision: str | dict | list | bool
    ) -> None:
        """Test that CaseResult rejects invalid types for numeric fields."""
        with pytest.raises(ValidationError) as exc_info:
            CaseResult(
                case_id=case_id,
                mode=mode,  # type: ignore
                query=query,
                precision=precision,  # type: ignore
            )

        # Verify the error message indicates type validation failure
        error_msg = str(exc_info.value)
        assert any(keyword in error_msg.lower() for keyword in ["type", "validation", "input"])

    @given(
        case_id=st.text(min_size=1, max_size=100),
        mode=st.sampled_from(["retrieval", "reader", "decision"]),
        query=st.text(min_size=1, max_size=500),
        tags=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
    )
    @settings(max_examples=20, deadline=200)
    def test_goldcase_tags_must_be_list_of_strings(self, case_id: str, mode: str, query: str, tags: list[str]) -> None:
        """Test that GoldCase tags field accepts only list[str]."""
        try:
            case = GoldCase(
                id=case_id,
                mode=Mode(mode),
                query=query,
                gt_answer="test answer",
                tags=tags,
            )

            # Check that tags are preserved correctly
            assert case.tags == tags
            assert all(isinstance(tag, str) for tag in case.tags)

        except Exception as e:
            record_case(
                "goldcase_tags_list_strings_failed",
                {"case_id": case_id, "mode": mode, "query": query, "tags": tags, "error": str(e)},
            )
            raise

    @given(
        case_id=st.text(min_size=1, max_size=100),
        mode=st.sampled_from(["retrieval", "reader", "decision"]),
        query=st.text(min_size=1, max_size=500),
        tags=st.one_of(
            st.lists(st.integers(), min_size=1, max_size=5),  # list[int]
            st.lists(st.one_of(st.integers(), st.text()), min_size=1, max_size=5),  # mixed types
            st.just("single_string"),  # single string instead of list
            st.just(123),  # integer instead of list
        ),
    )
    @settings(max_examples=10, deadline=200)
    def test_goldcase_rejects_invalid_tags_types(
        self, case_id: str, mode: str, query: str, tags: list[int] | list[str | int] | str | int
    ) -> None:
        """Test that GoldCase rejects invalid types for tags field."""
        with pytest.raises(ValidationError) as exc_info:
            GoldCase(
                id=case_id,
                mode=Mode(mode),
                query=query,
                gt_answer="test answer",
                tags=tags,  # type: ignore
            )

        # Verify the error message indicates type validation failure
        error_msg = str(exc_info.value)
        assert any(keyword in error_msg.lower() for keyword in ["type", "validation", "input", "tags"])

    @given(
        case_id=st.text(min_size=1, max_size=100),
        mode=st.sampled_from(["retrieval", "reader", "decision"]),
        query=st.text(min_size=1, max_size=500),
        tags=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
        invalid_mode=st.one_of(
            st.just("invalid_mode"),
            st.just(""),
            st.just("RAG"),
            st.just("READER"),
        ),
    )
    @settings(max_examples=10, deadline=200)
    def test_goldcase_mode_only_accepts_enum_values(
        self, case_id: str, mode: str, query: str, tags: list[str], invalid_mode: str
    ) -> None:
        """Test that GoldCase mode field only accepts valid enum values."""
        # Test valid mode
        try:
            case = GoldCase(
                id=case_id,
                mode=Mode(mode),
                query=query,
                gt_answer="test answer",
                tags=tags,
            )
            assert case.mode == Mode(mode)
        except Exception as e:
            record_case(
                "goldcase_valid_mode_failed",
                {"case_id": case_id, "mode": mode, "query": query, "tags": tags, "error": str(e)},
            )
            raise

        # Test invalid mode
        with pytest.raises(ValidationError) as exc_info:
            GoldCase(
                id=case_id,
                mode=invalid_mode,  # type: ignore
                query=query,
                gt_answer="test answer",
                tags=tags,
            )

        # Verify the error message indicates enum validation failure
        error_msg = str(exc_info.value)
        assert any(keyword in error_msg.lower() for keyword in ["type", "validation", "input", "mode"])

    @given(
        case_id=st.text(min_size=1, max_size=100),
        mode=st.sampled_from(["rag", "baseline", "oracle"]),
        query=st.text(min_size=1, max_size=500),
        precision=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
        recall=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
        f1=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
    )
    @settings(max_examples=10, deadline=200)
    def test_caseresult_roundtrip_preserves_types(
        self, case_id: str, mode: str, query: str, precision: float | None, recall: float | None, f1: float | None
    ) -> None:
        """Test that model_dump and model_validate preserve types correctly."""
        try:
            original = CaseResult(
                case_id=case_id,
                mode=mode,  # type: ignore
                query=query,
                precision=precision,
                recall=recall,
                f1=f1,
            )

            # Serialize to dict
            data: Any = original.model_dump()

            # Deserialize from dict
            restored: Any = CaseResult.model_validate(data)

            # Check that types are preserved
            assert isinstance(restored.precision, type(original.precision))
            assert isinstance(restored.recall, type(original.recall))
            assert isinstance(restored.f1, type(original.f1))

            # Check that values are preserved
            assert restored.precision == original.precision
            assert restored.recall == original.recall
            assert restored.f1 == original.f1

        except Exception as e:
            record_case(
                "caseresult_roundtrip_failed",
                {"case_id": case_id, "mode": mode, "precision": precision, "recall": recall, "f1": f1, "error": str(e)},
            )
            raise

    @given(
        case_id=st.text(min_size=1, max_size=100),
        mode=st.sampled_from(["retrieval", "reader", "decision"]),
        query=st.text(min_size=1, max_size=500),
        tags=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
    )
    @settings(max_examples=10, deadline=200)
    def test_goldcase_roundtrip_preserves_types(self, case_id: str, mode: str, query: str, tags: list[str]) -> None:
        """Test that GoldCase model_dump and model_validate preserve types correctly."""
        try:
            original = GoldCase(
                id=case_id,
                mode=Mode(mode),
                query=query,
                gt_answer="test answer",
                tags=tags,
            )

            # Serialize to dict
            data: Any = original.model_dump()

            # Deserialize from dict
            restored: Any = GoldCase.model_validate(data)

            # Check that types are preserved
            assert isinstance(restored.tags, list)
            assert all(isinstance(tag, str) for tag in restored.tags)
            assert isinstance(restored.mode, Mode)

            # Check that values are preserved
            assert restored.tags == original.tags
            assert restored.mode == original.mode

        except Exception as e:
            record_case(
                "goldcase_roundtrip_failed",
                {"case_id": case_id, "mode": mode, "query": query, "tags": tags, "error": str(e)},
            )
            raise

    @given(
        case_id=st.text(min_size=1, max_size=100),
        mode=st.sampled_from(["rag", "baseline", "oracle"]),
        query=st.text(min_size=1, max_size=500),
        precision=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
        recall=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
        f1=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0)),
    )
    @settings(max_examples=10, deadline=200)
    def test_caseresult_json_serialization_preserves_types(
        self, case_id: str, mode: str, query: str, precision: float | None, recall: float | None, f1: float | None
    ) -> None:
        """Test that JSON serialization preserves types correctly."""
        try:
            original = CaseResult(
                case_id=case_id,
                mode=mode,  # type: ignore
                query=query,
                precision=precision,
                recall=recall,
                f1=f1,
            )

            # Serialize to JSON
            json_str: Any = original.model_dump_json()
            data: Any = json.loads(json_str)

            # Check that JSON contains correct types
            if precision is not None:
                assert isinstance(data["precision"], int | float)
            else:
                assert data["precision"] is None

            if recall is not None:
                assert isinstance(data["recall"], int | float)
            else:
                assert data["recall"] is None

            if f1 is not None:
                assert isinstance(data["f1"], int | float)
            else:
                assert data["f1"] is None

        except Exception as e:
            record_case(
                "caseresult_json_serialization_failed",
                {"case_id": case_id, "mode": mode, "precision": precision, "recall": recall, "f1": f1, "error": str(e)},
            )
            raise
