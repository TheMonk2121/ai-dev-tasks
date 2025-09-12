from __future__ import annotations

import json
import math
from typing import Any, Optional, Union

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.freshness_enhancer import FreshnessConfig, FreshnessEnhancer

from ._regression_capture import record_case


@pytest.mark.prop
class TestFreshnessEnhancerTypeInvariants:
    """Property-based tests for freshness enhancer type invariants."""

    @given(
        query=st.text(min_size=1, max_size=200),
        results=st.lists(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                    st.lists(
                        st.one_of(
                            st.text(min_size=0, max_size=50),
                            st.floats(min_value=0.0, max_value=1.0),
                            st.integers(min_value=0, max_value=100),
                            st.booleans(),
                        ),
                        min_size=0,
                        max_size=10,
                    ),
                ),
                min_size=1,
                max_size=10,
            ),
            min_size=0,
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_returns_tuple_of_list_and_dict(
        self,
        query: str,
        results: list[dict[str, Any]],
        current_time: float | None,
    ) -> None:
        """Test that enhance_retrieval_results returns tuple of (list, dict)."""
        try:
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)
            enhanced_results, metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that result is a tuple
            assert isinstance(enhanced_results, list)
            assert isinstance(metadata, dict)

            # Check that enhanced_results is a list of dicts
            for item in enhanced_results:
                assert isinstance(item, dict)

        except Exception as e:
            record_case(
                "enhance_retrieval_results_returns_tuple_failed",
                {
                    "query": query,
                    "results": results,
                    "current_time": current_time,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        results=st.lists(
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
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_scores_are_floats(
        self,
        query: str,
        results: list[dict[str, Any]],
        current_time: float | None,
    ) -> None:
        """Test that enhanced results have float scores."""
        try:
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)
            enhanced_results, metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that all items with score fields have float scores
            for item in enhanced_results:
                if "score" in item:
                    assert isinstance(item["score"], float)
                    assert math.isfinite(item["score"])

        except Exception as e:
            record_case(
                "enhance_retrieval_results_scores_are_floats_failed",
                {
                    "query": query,
                    "results": results,
                    "current_time": current_time,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        results=st.lists(
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
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_metadata_fields_are_serializable_primitives(
        self,
        query: str,
        results: list[dict[str, Any]],
        current_time: float | None,
    ) -> None:
        """Test that metadata fields are serializable primitives."""
        try:
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)
            enhanced_results, metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that all metadata values are JSON-serializable primitives
            for key, value in metadata.items():
                assert isinstance(key, str)
                if isinstance(value, list):
                    # Check that all list elements are JSON-serializable primitives
                    for item in value:  # type: ignore[misc]
                        assert isinstance(item, (str, int, float, bool, type(None)))
                else:
                    # Check that non-list values are JSON-serializable primitives
                    assert isinstance(value, (str, int, float, bool, type(None)))

        except Exception as e:
            record_case(
                "enhance_retrieval_results_metadata_serializable_failed",
                {
                    "query": query,
                    "results": results,
                    "current_time": current_time,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        results=st.lists(
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
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_applied_flags_are_list_of_strings(
        self,
        query: str,
        results: list[dict[str, Any]],
        current_time: float | None,
    ) -> None:
        """Test that applied flags are list of strings."""
        try:
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)
            enhanced_results, metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that applied flags are list of strings if present
            for item in enhanced_results:
                if "applied_flags" in item:
                    assert isinstance(item["applied_flags"], list)
                    for flag in item["applied_flags"]:  # type: ignore[misc]
                        assert isinstance(flag, str)

        except Exception as e:
            record_case(
                "enhance_retrieval_results_applied_flags_list_of_strings_failed",
                {
                    "query": query,
                    "results": results,
                    "current_time": current_time,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        results=st.lists(
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
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_handles_empty_inputs_gracefully(
        self,
        query: str,
        results: list[dict[str, Any]],
        current_time: float | None,
    ) -> None:
        """Test that enhance_retrieval_results handles empty inputs gracefully."""
        try:
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)
            enhanced_results, metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Should return a list and dict even for empty inputs
            assert isinstance(enhanced_results, list)
            assert isinstance(metadata, dict)

            # If results were empty, enhanced_results should also be empty
            if not results:
                assert len(enhanced_results) == 0

        except Exception as e:
            record_case(
                "enhance_retrieval_results_handles_empty_inputs_failed",
                {
                    "query": query,
                    "results": results,
                    "current_time": current_time,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        results=st.lists(
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
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_is_deterministic(
        self,
        query: str,
        results: list[dict[str, Any]],
        current_time: float | None,
    ) -> None:
        """Test that enhance_retrieval_results is deterministic for the same input."""
        try:
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)

            # Run twice with same input
            result1 = enhancer.enhance_retrieval_results(query, results, current_time)
            result2 = enhancer.enhance_retrieval_results(query, results, current_time)

            # Results should be identical
            assert result1 == result2

        except Exception as e:
            record_case(
                "enhance_retrieval_results_is_deterministic_failed",
                {
                    "query": query,
                    "results": results,
                    "current_time": current_time,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        results=st.lists(
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
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_output_is_json_serializable(
        self,
        query: str,
        results: list[dict[str, Any]],
        current_time: float | None,
    ) -> None:
        """Test that enhance_retrieval_results output is JSON serializable."""
        try:
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)
            enhanced_results, metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Should be able to serialize to JSON
            json_str = json.dumps({"results": enhanced_results, "metadata": metadata})
            assert isinstance(json_str, str)

            # Should be able to deserialize back
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)

        except Exception as e:
            record_case(
                "enhance_retrieval_results_output_json_serializable_failed",
                {
                    "query": query,
                    "results": results,
                    "current_time": current_time,
                    "error": str(e),
                },
            )
            raise
