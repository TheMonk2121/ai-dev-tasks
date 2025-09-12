from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.freshness_enhancer import FreshnessConfig, FreshnessEnhancer

from ._regression_capture import record_case


@pytest.mark.prop
class TestFreshnessTypesProps:
    """Property-based tests for freshness enhancer type contracts."""

    @given(
        query=st.text(min_size=1, max_size=500),
        results=st.lists(
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
                    "timestamp": st.one_of(
                        st.none(),
                        st.floats(min_value=0.0, max_value=2000000000.0),  # Reasonable timestamp range
                        st.text(min_size=1, max_size=50),  # String timestamps
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=2000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_scores_are_floats(
        self, query: str, results: list[dict], current_time: float | None
    ) -> None:
        """Test that enhance_retrieval_results result scores are floats."""
        try:
            # Create freshness enhancer
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)

            # Enhance retrieval results
            enhanced_results, enhancement_metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that enhanced_results is a list
            assert isinstance(enhanced_results, list)

            # Check that all scores are floats
            for result in enhanced_results:
                if "score" in result:
                    assert isinstance(result["score"], float)
                    assert math.isfinite(result["score"])
                    assert not math.isnan(result["score"])

        except Exception as e:
            record_case(
                "freshness_enhance_scores_floats_failed",
                {"query": query, "results_count": len(results), "current_time": current_time, "error": str(e)},
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        results=st.lists(
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
                    "timestamp": st.one_of(
                        st.none(),
                        st.floats(min_value=0.0, max_value=2000000000.0),
                        st.text(min_size=1, max_size=50),
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=2000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_metadata_fields_serializable_primitives(
        self, query: str, results: list[dict], current_time: float | None
    ) -> None:
        """Test that enhance_retrieval_results metadata fields are serializable primitives."""
        try:
            # Create freshness enhancer
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)

            # Enhance retrieval results
            enhanced_results, enhancement_metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that enhancement_metadata is a dict
            assert isinstance(enhancement_metadata, dict)

            # Check that all metadata fields are serializable primitives
            for key, value in enhancement_metadata.items():
                assert isinstance(key, str)
                assert isinstance(value, (str, int, float, bool, list, dict, type(None)))

                # If it's a list or dict, check that it's JSON-serializable
                if isinstance(value, (list, dict)):
                    try:
                        import json

                        json.dumps(value)
                    except (TypeError, ValueError):
                        record_case(
                            "freshness_metadata_not_json_serializable",
                            {
                                "key": key,
                                "value": value,
                                "value_type": type(value).__name__,
                                "enhancement_metadata": enhancement_metadata,
                            },
                        )
                        raise

        except Exception as e:
            record_case(
                "freshness_enhance_metadata_serializable_failed",
                {"query": query, "results_count": len(results), "current_time": current_time, "error": str(e)},
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        results=st.lists(
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
                    "timestamp": st.one_of(
                        st.none(),
                        st.floats(min_value=0.0, max_value=2000000000.0),
                        st.text(min_size=1, max_size=50),
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=2000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_applied_flags_are_list_str(
        self, query: str, results: list[dict], current_time: float | None
    ) -> None:
        """Test that enhance_retrieval_results applied flags are list[str]."""
        try:
            # Create freshness enhancer
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)

            # Enhance retrieval results
            enhanced_results, enhancement_metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that enhancement_metadata is a dict
            assert isinstance(enhancement_metadata, dict)

            # Check that enhancements_applied is a list of strings
            if "enhancements_applied" in enhancement_metadata:
                enhancements_applied = enhancement_metadata["enhancements_applied"]
                assert isinstance(enhancements_applied, list)
                assert all(isinstance(flag, str) for flag in enhancements_applied)

        except Exception as e:
            record_case(
                "freshness_enhance_applied_flags_failed",
                {"query": query, "results_count": len(results), "current_time": current_time, "error": str(e)},
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        results=st.lists(
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
                    "timestamp": st.one_of(
                        st.none(),
                        st.floats(min_value=0.0, max_value=2000000000.0),
                        st.text(min_size=1, max_size=50),
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=2000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_freshness_metadata_numeric_or_none(
        self, query: str, results: list[dict], current_time: float | None
    ) -> None:
        """Test that enhance_retrieval_results freshness_metadata numeric/None."""
        try:
            # Create freshness enhancer
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)

            # Enhance retrieval results
            enhanced_results, enhancement_metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that enhanced_results is a list
            assert isinstance(enhanced_results, list)

            # Check that freshness_metadata fields are numeric or None
            for result in enhanced_results:
                if "freshness_metadata" in result:
                    freshness_metadata = result["freshness_metadata"]
                    assert isinstance(freshness_metadata, dict)

                    for key, value in freshness_metadata.items():
                        assert isinstance(key, str)
                        assert isinstance(value, (int, float, type(None)))

                        # If it's a number, check that it's finite
                        if isinstance(value, (int, float)) and value is not None:
                            assert math.isfinite(value)

        except Exception as e:
            record_case(
                "freshness_enhance_metadata_numeric_failed",
                {"query": query, "results_count": len(results), "current_time": current_time, "error": str(e)},
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        results=st.lists(
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
                    "timestamp": st.one_of(
                        st.none(),
                        st.floats(min_value=0.0, max_value=2000000000.0),
                        st.text(min_size=1, max_size=50),
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=2000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_handles_empty_results(
        self, query: str, results: list[dict], current_time: float | None
    ) -> None:
        """Test that enhance_retrieval_results handles empty results correctly."""
        try:
            # Create freshness enhancer
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)

            # Enhance retrieval results
            enhanced_results, enhancement_metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that enhanced_results is a list
            assert isinstance(enhanced_results, list)

            # Check that enhancement_metadata is a dict
            assert isinstance(enhancement_metadata, dict)

            # Check that total_results matches input length
            if "total_results" in enhancement_metadata:
                assert enhancement_metadata["total_results"] == len(results)

        except Exception as e:
            record_case(
                "freshness_enhance_empty_results_failed",
                {"query": query, "results_count": len(results), "current_time": current_time, "error": str(e)},
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        results=st.lists(
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
                    "timestamp": st.one_of(
                        st.none(),
                        st.floats(min_value=0.0, max_value=2000000000.0),
                        st.text(min_size=1, max_size=50),
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=2000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_handles_unicode_queries(
        self, query: str, results: list[dict], current_time: float | None
    ) -> None:
        """Test that enhance_retrieval_results handles unicode queries correctly."""
        try:
            # Create freshness enhancer
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)

            # Enhance retrieval results
            enhanced_results, enhancement_metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that enhanced_results is a list
            assert isinstance(enhanced_results, list)

            # Check that enhancement_metadata is a dict
            assert isinstance(enhancement_metadata, dict)

        except Exception as e:
            record_case(
                "freshness_enhance_unicode_queries_failed",
                {"query": query, "results_count": len(results), "current_time": current_time, "error": str(e)},
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        results=st.lists(
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
                    "timestamp": st.one_of(
                        st.none(),
                        st.floats(min_value=0.0, max_value=2000000000.0),
                        st.text(min_size=1, max_size=50),
                    ),
                }
            ),
            min_size=0,
            max_size=20,
        ),
        current_time=st.one_of(st.none(), st.floats(min_value=0.0, max_value=2000000000.0)),
    )
    @settings(max_examples=20, deadline=200)
    def test_enhance_retrieval_results_handles_special_timestamps(
        self, query: str, results: list[dict], current_time: float | None
    ) -> None:
        """Test that enhance_retrieval_results handles special timestamps correctly."""
        try:
            # Create freshness enhancer
            config = FreshnessConfig()
            enhancer = FreshnessEnhancer(config)

            # Enhance retrieval results
            enhanced_results, enhancement_metadata = enhancer.enhance_retrieval_results(query, results, current_time)

            # Check that enhanced_results is a list
            assert isinstance(enhanced_results, list)

            # Check that enhancement_metadata is a dict
            assert isinstance(enhancement_metadata, dict)

        except Exception as e:
            record_case(
                "freshness_enhance_special_timestamps_failed",
                {"query": query, "results_count": len(results), "current_time": current_time, "error": str(e)},
            )
            raise
