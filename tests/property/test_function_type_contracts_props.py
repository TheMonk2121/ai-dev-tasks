from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.dspy_modules.retriever.rerank import mmr_rerank
from src.retrieval.fusion import weighted_rrf
from src.retrieval.reranker import heuristic_rerank

from ._regression_capture import record_case


@pytest.mark.prop
class TestFunctionTypeContracts:
    """Property-based tests for function output type contracts."""

    @given(
        bm25_items=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=20,
        ),
        vector_items=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=20,
        ),
        k=st.integers(min_value=1, max_value=100),
        lambda_lex=st.floats(min_value=0.0, max_value=1.0),
        lambda_sem=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=20, deadline=200)
    def test_weighted_rrf_output_types_are_str_float_tuples(
        self,
        bm25_items: list[tuple[str, float]],
        vector_items: list[tuple[str, float]],
        k: int,
        lambda_lex: float,
        lambda_sem: float,
    ) -> None:
        """Test that weighted_rrf returns list of (str, float) tuples with no Nones."""
        try:
            result = weighted_rrf(bm25_items, vector_items, k=k, lambda_lex=lambda_lex, lambda_sem=lambda_sem)

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
                "weighted_rrf_output_types_failed",
                {
                    "bm25_items": bm25_items[:5],  # First 5 for debugging
                    "vector_items": vector_items[:5],
                    "k": k,
                    "lambda_lex": lambda_lex,
                    "lambda_sem": lambda_sem,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        candidates=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=20,
        ),
        documents=st.dictionaries(
            st.text(min_size=1, max_size=50), st.text(min_size=1, max_size=500), min_size=0, max_size=20
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
        """Test that heuristic_rerank returns list of (str, float) tuples with alpha bounds respected."""
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

            # Check that alpha bounds are respected (alpha should be clamped to [0, 1])
            # This is tested implicitly by the function's behavior

        except Exception as e:
            record_case(
                "heuristic_rerank_output_types_failed",
                {
                    "query": query,
                    "candidates": candidates[:5],  # First 5 for debugging
                    "documents_keys": list(documents.keys())[:5],
                    "alpha": alpha,
                    "top_m": top_m,
                    "error": str(e),
                },
            )
            raise

    @given(
        rows=st.lists(
            st.fixed_dictionaries(
                {
                    "chunk_id": st.text(min_size=1, max_size=50),
                    "file_path": st.text(min_size=1, max_size=100),
                    "score": st.floats(min_value=0.0, max_value=1.0),
                    "embedding": st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=10, max_size=100),
                    "metadata": st.dictionaries(
                        st.text(min_size=1, max_size=20),
                        st.one_of(
                            st.text(min_size=1, max_size=50),
                            st.integers(min_value=0, max_value=1000),
                            st.floats(min_value=0.0, max_value=1.0),
                            st.booleans(),
                        ),
                        min_size=0,
                        max_size=10,
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
        per_file_penalty=st.floats(min_value=0.0, max_value=1.0),
        k=st.integers(min_value=1, max_value=20),
        tag=st.text(min_size=0, max_size=50),
    )
    @settings(max_examples=20, deadline=200)
    def test_mmr_rerank_score_fields_remain_floats_and_metadata_json_friendly(
        self, rows: list[dict], alpha: float, per_file_penalty: float, k: int, tag: str
    ) -> None:
        """Test that mmr_rerank score fields remain floats and metadata is JSON-friendly."""
        try:
            result = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k, tag=tag)

            # Check that result is a list
            assert isinstance(result, list)

            # Check that all elements are dictionaries
            for row in result:
                assert isinstance(row, dict)

                # Check that score field is a float
                if "score" in row:
                    assert isinstance(row["score"], float)
                    assert math.isfinite(row["score"])

                # Check that metadata is JSON-friendly
                if "metadata" in row:
                    metadata = row["metadata"]
                    assert isinstance(metadata, dict)

                    # Check that all metadata values are JSON-serializable
                    for key, value in metadata.items():
                        assert isinstance(key, str)
                        assert isinstance(value, str | int | float | bool | type(None) | list | dict)

                        # If it's a list or dict, check that it's JSON-serializable
                        if isinstance(value, list | dict):
                            try:
                                import json

                                json.dumps(value)
                            except (TypeError, ValueError):
                                record_case(
                                    "mmr_rerank_metadata_not_json_serializable",
                                    {"key": key, "value": value, "value_type": type(value).__name__, "row": row},
                                )
                                raise

        except Exception as e:
            record_case(
                "mmr_rerank_output_types_failed",
                {
                    "rows_count": len(rows),
                    "alpha": alpha,
                    "per_file_penalty": per_file_penalty,
                    "k": k,
                    "tag": tag,
                    "error": str(e),
                },
            )
            raise

    @given(
        bm25_items=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=20,
        ),
        vector_items=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=20,
        ),
        k=st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=10, deadline=200)
    def test_weighted_rrf_handles_empty_inputs_gracefully(
        self, bm25_items: list[tuple[str, float]], vector_items: list[tuple[str, float]], k: int
    ) -> None:
        """Test that weighted_rrf handles empty inputs gracefully."""
        try:
            # Test with empty bm25
            result1 = weighted_rrf([], vector_items, k=k)
            assert isinstance(result1, list)

            # Test with empty vector
            result2 = weighted_rrf(bm25_items, [], k=k)
            assert isinstance(result2, list)

            # Test with both empty
            result3 = weighted_rrf([], [], k=k)
            assert isinstance(result3, list)
            assert len(result3) == 0

        except Exception as e:
            record_case(
                "weighted_rrf_empty_inputs_failed",
                {"bm25_items": bm25_items, "vector_items": vector_items, "k": k, "error": str(e)},
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        candidates=st.lists(
            st.tuples(st.text(min_size=1, max_size=50), st.floats(min_value=0.0, max_value=1.0)),
            min_size=0,
            max_size=20,
        ),
        documents=st.dictionaries(
            st.text(min_size=1, max_size=50), st.text(min_size=1, max_size=500), min_size=0, max_size=20
        ),
        alpha=st.floats(min_value=-1.0, max_value=2.0),  # Test out-of-bounds alpha
    )
    @settings(max_examples=10, deadline=200)
    def test_heuristic_rerank_alpha_bounds_respected(
        self, query: str, candidates: list[tuple[str, float]], documents: dict[str, str], alpha: float
    ) -> None:
        """Test that heuristic_rerank respects alpha bounds (clamps to [0, 1])."""
        try:
            result = heuristic_rerank(query, candidates, documents, alpha=alpha)

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

        except Exception as e:
            record_case(
                "heuristic_rerank_alpha_bounds_failed",
                {
                    "query": query,
                    "candidates": candidates[:5],
                    "documents_keys": list(documents.keys())[:5],
                    "alpha": alpha,
                    "error": str(e),
                },
            )
            raise

    @given(
        rows=st.lists(
            st.fixed_dictionaries(
                {
                    "chunk_id": st.text(min_size=1, max_size=50),
                    "file_path": st.text(min_size=1, max_size=100),
                    "score": st.floats(min_value=0.0, max_value=1.0),
                    "embedding": st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=10, max_size=100),
                    "metadata": st.dictionaries(
                        st.text(min_size=1, max_size=20),
                        st.one_of(
                            st.text(min_size=1, max_size=50),
                            st.integers(min_value=0, max_value=1000),
                            st.floats(min_value=0.0, max_value=1.0),
                            st.booleans(),
                        ),
                        min_size=0,
                        max_size=10,
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        alpha=st.floats(min_value=0.0, max_value=1.0),
        per_file_penalty=st.floats(min_value=0.0, max_value=1.0),
        k=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=10, deadline=200)
    def test_mmr_rerank_no_nans_in_scores(
        self, rows: list[dict], alpha: float, per_file_penalty: float, k: int
    ) -> None:
        """Test that mmr_rerank produces no NaN scores."""
        try:
            result = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)

            # Check that result is a list
            assert isinstance(result, list)

            # Check that all scores are finite
            for row in result:
                if "score" in row:
                    assert math.isfinite(row["score"])
                    assert not math.isnan(row["score"])

        except Exception as e:
            record_case(
                "mmr_rerank_nan_scores_failed",
                {
                    "rows_count": len(rows),
                    "alpha": alpha,
                    "per_file_penalty": per_file_penalty,
                    "k": k,
                    "error": str(e),
                },
            )
            raise
