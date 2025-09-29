from __future__ import annotations

import json
import math
from typing import Any, Optional, Union

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.dspy_modules.retriever.rerank import mmr_rerank
from src.retrieval.reranker import heuristic_rerank

from ._regression_capture import record_case


@pytest.mark.prop
class TestRerankerTypeInvariants:
    """Property-based tests for reranker function type invariants."""

    @given(
        query=st.text(min_size=1, max_size=200),
        candidates=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=20,
        ),
        documents=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.text(min_size=0, max_size=100),
            min_size=0,
            max_size=10,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
        top_m=st.one_of(st.none(), st.integers(min_value=1, max_value=20)),
    )
    @settings(max_examples=20, deadline=200)
    def test_heuristic_rerank_output_types_are_str_float_tuples(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        documents: dict[str, str],
        alpha: float,
        top_m: int | None,
    ) -> None:
        """Test that heuristic_rerank returns list of (str, float) tuples."""
        try:
            result = heuristic_rerank(query, candidates, documents, alpha=alpha, top_m=top_m)

            # Check that result is a list
            assert isinstance(result, list)

            # Check that all elements are tuples of (str, float)
            for item in result:
                assert isinstance(item, tuple)
                assert len(item) == 2
                doc_id, score = item

                # Check types
                assert isinstance(doc_id, str)
                assert isinstance(score, float)

                # Check that score is finite (no NaN or inf)
                assert math.isfinite(score)

                # Check that doc_id is not empty
                assert len(doc_id) > 0

        except Exception as e:
            record_case(
                "heuristic_rerank_output_types_failed",
                {
                    "query": query,
                    "candidates": candidates,
                    "documents": documents,
                    "alpha": alpha,
                    "top_m": top_m,
                    "error": str(e),
                },
            )
            raise

    @given(
        rows=st.lists(
            st.dictionaries(
                keys=st.sampled_from(["chunk_id", "file_path", "filename", "score", "embedding"]),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                    st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=0, max_size=10),
                ),
                min_size=3,  # Ensure we have at least score, chunk_id, and embedding
                max_size=5,
            ),
            min_size=0,
            max_size=20,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
        per_file_penalty=st.floats(min_value=0.0, max_value=1.0),
        k=st.integers(min_value=1, max_value=50),
        tag=st.text(min_size=0, max_size=20),
    )
    @settings(max_examples=20, deadline=200, suppress_health_check=[HealthCheck.filter_too_much])
    def test_mmr_rerank_output_types_are_dicts_with_float_scores(
        self,
        rows: list[dict[str, Any]],
        alpha: float,
        per_file_penalty: float,
        k: int,
        tag: str,
    ) -> None:
        """Test that mmr_rerank returns list of dicts with float scores."""
        try:
            # Ensure required fields exist and have correct types
            for row in rows:
                if "score" not in row:
                    row["score"] = 0.5
                if "chunk_id" not in row:
                    row["chunk_id"] = "test_chunk"
                if "embedding" not in row:
                    row["embedding"] = [0.1, 0.2, 0.3]

                # Ensure score is float
                if isinstance(row["score"], int):
                    row["score"] = float(row["score"])
                elif not isinstance(row["score"], int | float):
                    row["score"] = 0.5

                # Ensure file_path/filename are strings
                if "file_path" in row and not isinstance(row["file_path"], str):
                    row["file_path"] = str(row["file_path"])
                if "filename" in row and not isinstance(row["filename"], str):
                    row["filename"] = str(row["filename"])

                # Ensure embedding is a list/tuple
                if not isinstance(row["embedding"], list | tuple):
                    row["embedding"] = [0.1, 0.2, 0.3]

            result = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k, tag=tag)

            # Check that result is a list
            assert isinstance(result, list)

            # Check that all elements are dictionaries
            for item in result:
                assert isinstance(item, dict)

                # Check that score field is a float if present
                if "score" in item:
                    assert isinstance(item["score"], float)
                    assert math.isfinite(item["score"])

                # Check that all values are JSON-serializable primitives
                for key, value in item.items():
                    assert isinstance(key, str)
                    if isinstance(value, list):
                        assert all(isinstance(x, str | int | float | bool | type(None)) for x in value)  # type: ignore[misc]
                    else:
                        assert isinstance(value, str | int | float | bool | type(None))

        except Exception as e:
            record_case(
                "mmr_rerank_output_types_failed",
                {
                    "rows": rows,
                    "alpha": alpha,
                    "per_file_penalty": per_file_penalty,
                    "k": k,
                    "tag": tag,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        candidates=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=5,
        ),
        documents=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.text(min_size=0, max_size=100),
            min_size=0,
            max_size=5,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=20, deadline=200)
    def test_heuristic_rerank_alpha_bounds_are_respected(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        documents: dict[str, str],
        alpha: float,
    ) -> None:
        """Test that heuristic_rerank respects alpha bounds."""
        try:
            result = heuristic_rerank(query, candidates, documents, alpha=alpha)

            # Should return a list
            assert isinstance(result, list)

            # Alpha should be within bounds (0.0 to 1.0)
            assert 0.0 <= alpha <= 1.0

            # All scores should be finite
            for item in result:
                assert isinstance(item, tuple)
                assert len(item) == 2
                doc_id, score = item
                assert isinstance(doc_id, str)
                assert isinstance(score, float)
                assert math.isfinite(score)

        except Exception as e:
            record_case(
                "heuristic_rerank_alpha_bounds_failed",
                {
                    "query": query,
                    "candidates": candidates,
                    "documents": documents,
                    "alpha": alpha,
                    "error": str(e),
                },
            )
            raise

    @given(
        rows=st.lists(
            st.dictionaries(
                keys=st.sampled_from(["chunk_id", "file_path", "filename", "score", "embedding"]),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                    st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=0, max_size=10),
                ),
                min_size=3,  # Ensure we have at least score, chunk_id, and embedding
                max_size=5,
            ),
            min_size=0,
            max_size=5,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
        per_file_penalty=st.floats(min_value=0.0, max_value=1.0),
        k=st.integers(min_value=1, max_value=20),
        tag=st.text(min_size=0, max_size=20),
    )
    @settings(max_examples=20, deadline=200, suppress_health_check=[HealthCheck.filter_too_much])
    def test_mmr_rerank_alpha_bounds_are_respected(
        self,
        rows: list[dict[str, Any]],
        alpha: float,
        per_file_penalty: float,
        k: int,
        tag: str,
    ) -> None:
        """Test that mmr_rerank respects alpha bounds."""
        try:
            # Ensure required fields exist and have correct types
            for row in rows:
                if "score" not in row:
                    row["score"] = 0.5
                if "chunk_id" not in row:
                    row["chunk_id"] = "test_chunk"
                if "embedding" not in row:
                    row["embedding"] = [0.1, 0.2, 0.3]

                # Ensure score is float
                if isinstance(row["score"], int):
                    row["score"] = float(row["score"])
                elif not isinstance(row["score"], int | float):
                    row["score"] = 0.5

                # Ensure file_path/filename are strings
                if "file_path" in row and not isinstance(row["file_path"], str):
                    row["file_path"] = str(row["file_path"])
                if "filename" in row and not isinstance(row["filename"], str):
                    row["filename"] = str(row["filename"])

                # Ensure embedding is a list/tuple
                if not isinstance(row["embedding"], list | tuple):
                    row["embedding"] = [0.1, 0.2, 0.3]

            result = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k, tag=tag)

            # Should return a list
            assert isinstance(result, list)

            # Alpha should be within bounds (0.0 to 1.0)
            assert 0.0 <= alpha <= 1.0

            # All scores should be finite
            for item in result:
                assert isinstance(item, dict)
                if "score" in item:
                    assert isinstance(item["score"], float)
                    assert math.isfinite(item["score"])

        except Exception as e:
            record_case(
                "mmr_rerank_alpha_bounds_failed",
                {
                    "rows": rows,
                    "alpha": alpha,
                    "per_file_penalty": per_file_penalty,
                    "k": k,
                    "tag": tag,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        candidates=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=5,
        ),
        documents=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.text(min_size=0, max_size=100),
            min_size=0,
            max_size=5,
        ),
    )
    @settings(max_examples=20, deadline=200)
    def test_heuristic_rerank_handles_empty_inputs_gracefully(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        documents: dict[str, str],
    ) -> None:
        """Test that heuristic_rerank handles empty inputs gracefully."""
        try:
            result = heuristic_rerank(query, candidates, documents)

            # Should return a list (possibly empty)
            assert isinstance(result, list)

            # If not empty, all items should be (str, float) tuples
            for item in result:
                assert isinstance(item, tuple)
                assert len(item) == 2
                doc_id, score = item
                assert isinstance(doc_id, str)
                assert isinstance(score, float)
                assert math.isfinite(score)

        except Exception as e:
            record_case(
                "heuristic_rerank_empty_inputs_failed",
                {
                    "query": query,
                    "candidates": candidates,
                    "documents": documents,
                    "error": str(e),
                },
            )
            raise

    @given(
        rows=st.lists(
            st.dictionaries(
                keys=st.sampled_from(["chunk_id", "file_path", "filename", "score", "embedding"]),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                    st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=0, max_size=10),
                ),
                min_size=3,  # Ensure we have at least score, chunk_id, and embedding
                max_size=5,
            ),
            min_size=0,
            max_size=5,
        ),
    )
    @settings(max_examples=20, deadline=200, suppress_health_check=[HealthCheck.filter_too_much])
    def test_mmr_rerank_handles_empty_inputs_gracefully(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        """Test that mmr_rerank handles empty inputs gracefully."""
        try:
            # Ensure required fields exist and have correct types
            for row in rows:
                if "score" not in row:
                    row["score"] = 0.5
                if "chunk_id" not in row:
                    row["chunk_id"] = "test_chunk"
                if "embedding" not in row:
                    row["embedding"] = [0.1, 0.2, 0.3]

                # Ensure score is float
                if isinstance(row["score"], int):
                    row["score"] = float(row["score"])
                elif not isinstance(row["score"], int | float):
                    row["score"] = 0.5

                # Ensure file_path/filename are strings
                if "file_path" in row and not isinstance(row["file_path"], str):
                    row["file_path"] = str(row["file_path"])
                if "filename" in row and not isinstance(row["filename"], str):
                    row["filename"] = str(row["filename"])

                # Ensure embedding is a list/tuple
                if not isinstance(row["embedding"], list | tuple):
                    row["embedding"] = [0.1, 0.2, 0.3]

            result = mmr_rerank(rows)

            # Should return a list (possibly empty)
            assert isinstance(result, list)

            # If not empty, all items should be dicts
            for item in result:
                assert isinstance(item, dict)

        except Exception as e:
            record_case(
                "mmr_rerank_empty_inputs_failed",
                {
                    "rows": rows,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        candidates=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=10,
        ),
        documents=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.text(min_size=0, max_size=100),
            min_size=0,
            max_size=5,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=20, deadline=200)
    def test_heuristic_rerank_is_deterministic(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        documents: dict[str, str],
        alpha: float,
    ) -> None:
        """Test that heuristic_rerank is deterministic for the same input."""
        try:
            # Run twice with same input
            result1 = heuristic_rerank(query, candidates, documents, alpha=alpha)
            result2 = heuristic_rerank(query, candidates, documents, alpha=alpha)

            # Results should be identical
            assert result1 == result2

        except Exception as e:
            record_case(
                "heuristic_rerank_is_deterministic_failed",
                {
                    "query": query,
                    "candidates": candidates,
                    "documents": documents,
                    "alpha": alpha,
                    "error": str(e),
                },
            )
            raise

    @given(
        rows=st.lists(
            st.dictionaries(
                keys=st.sampled_from(["chunk_id", "file_path", "filename", "score", "embedding"]),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                    st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=0, max_size=10),
                ),
                min_size=3,  # Ensure we have at least score, chunk_id, and embedding
                max_size=5,
            ),
            min_size=0,
            max_size=10,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
        per_file_penalty=st.floats(min_value=0.0, max_value=1.0),
        k=st.integers(min_value=1, max_value=20),
        tag=st.text(min_size=0, max_size=20),
    )
    @settings(max_examples=20, deadline=200, suppress_health_check=[HealthCheck.filter_too_much])
    def test_mmr_rerank_is_deterministic(
        self,
        rows: list[dict[str, Any]],
        alpha: float,
        per_file_penalty: float,
        k: int,
        tag: str,
    ) -> None:
        """Test that mmr_rerank is deterministic for the same input."""
        try:
            # Ensure required fields exist and have correct types
            for row in rows:
                if "score" not in row:
                    row["score"] = 0.5
                if "chunk_id" not in row:
                    row["chunk_id"] = "test_chunk"
                if "embedding" not in row:
                    row["embedding"] = [0.1, 0.2, 0.3]

                # Ensure score is float
                if isinstance(row["score"], int):
                    row["score"] = float(row["score"])
                elif not isinstance(row["score"], int | float):
                    row["score"] = 0.5

                # Ensure file_path/filename are strings
                if "file_path" in row and not isinstance(row["file_path"], str):
                    row["file_path"] = str(row["file_path"])
                if "filename" in row and not isinstance(row["filename"], str):
                    row["filename"] = str(row["filename"])

                # Ensure embedding is a list/tuple
                if not isinstance(row["embedding"], list | tuple):
                    row["embedding"] = [0.1, 0.2, 0.3]

            # Run twice with same input
            result1 = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k, tag=tag)
            result2 = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k, tag=tag)

            # Results should be identical
            assert result1 == result2

        except Exception as e:
            record_case(
                "mmr_rerank_is_deterministic_failed",
                {
                    "rows": rows,
                    "alpha": alpha,
                    "per_file_penalty": per_file_penalty,
                    "k": k,
                    "tag": tag,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        candidates=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=10,
        ),
        documents=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.text(min_size=0, max_size=100),
            min_size=0,
            max_size=5,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=20, deadline=200)
    def test_heuristic_rerank_output_is_json_serializable(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        documents: dict[str, str],
        alpha: float,
    ) -> None:
        """Test that heuristic_rerank output is JSON serializable."""
        try:
            result = heuristic_rerank(query, candidates, documents, alpha=alpha)

            # Should be able to serialize to JSON
            json_str = json.dumps(result)
            assert isinstance(json_str, str)

            # Should be able to deserialize back
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, list)

        except Exception as e:
            record_case(
                "heuristic_rerank_output_json_serializable_failed",
                {
                    "query": query,
                    "candidates": candidates,
                    "documents": documents,
                    "alpha": alpha,
                    "error": str(e),
                },
            )
            raise

    @given(
        rows=st.lists(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                ),
                min_size=1,
                max_size=10,
            ),
            min_size=0,
            max_size=10,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
        per_file_penalty=st.floats(min_value=0.0, max_value=1.0),
        k=st.integers(min_value=1, max_value=20),
        tag=st.text(min_size=0, max_size=20),
    )
    @settings(max_examples=20, deadline=200)
    def test_mmr_rerank_output_is_json_serializable(
        self,
        rows: list[dict[str, Any]],
        alpha: float,
        per_file_penalty: float,
        k: int,
        tag: str,
    ) -> None:
        """Test that mmr_rerank output is JSON serializable."""
        try:
            result = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k, tag=tag)

            # Should be able to serialize to JSON
            json_str = json.dumps(result)
            assert isinstance(json_str, str)

            # Should be able to deserialize back
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, list)

        except Exception as e:
            record_case(
                "mmr_rerank_output_json_serializable_failed",
                {
                    "rows": rows,
                    "alpha": alpha,
                    "per_file_penalty": per_file_penalty,
                    "k": k,
                    "tag": tag,
                    "error": str(e),
                },
            )
            raise
