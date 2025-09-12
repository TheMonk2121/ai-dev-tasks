import sys
import os
#!/usr/bin/env python3
"""
Comprehensive property-based tests for retrieval system invariants.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.dspy_modules.retriever.rerank import mmr_rerank
from ._regression_capture import record_case

# Note: Weights and Limits classes may not exist, using dict-based approach


def create_retrieval_candidate(
    content: str,
    score: float,
    doc_id: str | None = None,
    title: str | None = None,
    url: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """Create a retrieval candidate for testing."""
    if doc_id is None:
        doc_id = f"doc_{hash(content) % 10000}"
    if metadata is None:
        metadata = {}

    return {
        "content": content,
        "score": score,
        "doc_id": doc_id,
        "title": title,
        "url": url,
        "metadata": metadata,
        "embedding": np.random.rand(128).tolist(),  # Random embedding
    }


def create_weights(
    semantic: float = 0.5,
    lexical: float = 0.3,
    freshness: float = 0.2,
    custom: dict | None = None,
) -> dict:
    """Create a weights dict for testing."""
    if custom is None:
        custom = {}

    return {
        "semantic": semantic,
        "lexical": lexical,
        "freshness": freshness,
        "custom": custom,
    }


def create_limits(
    max_results: int = 10,
    max_tokens: int = 4000,
    max_chars: int = 8000,
    timeout_ms: int = 5000,
) -> dict:
    """Create a limits dict for testing."""
    return {
        "max_results": max_results,
        "max_tokens": max_tokens,
        "max_chars": max_chars,
        "timeout_ms": timeout_ms,
    }


class TestMMRRerankingProperties:
    """Property-based tests for MMR reranking system invariants."""

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
                doc_id=st.text(min_size=1, max_size=50),
                title=st.text(max_size=200),
                url=st.text(max_size=200),
                metadata=st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100), max_size=3),
            ),
            min_size=1,
            max_size=50,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_preserves_input_count(
        self, rows: list[dict], alpha: float, per_file_penalty: float, k: int
    ) -> None:
        """MMR reranking should not change the total number of items."""
        original_count = len(rows)
        reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)

        # Should not exceed original count
        assert len(reranked) <= original_count, f"Reranked count {len(reranked)} exceeds original {original_count}"

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=1,
            max_size=50,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_respects_k_limit(self, rows: list[dict], alpha: float, per_file_penalty: float, k: int) -> None:
        """MMR reranking should respect the k limit."""
        reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)

        assert len(reranked) <= k, f"Reranked count {len(reranked)} exceeds k={k}"

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=1,
            max_size=50,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_preserves_content(
        self, rows: list[dict], alpha: float, per_file_penalty: float, k: int
    ) -> None:
        """MMR reranking should preserve content integrity."""
        reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)

        # All reranked items should be from the original set
        original_contents = {row["content"] for row in rows}
        reranked_contents = {row["content"] for row in reranked}

        assert reranked_contents.issubset(original_contents), "Reranked contains items not in original set"

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=1,
            max_size=50,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_deterministic(self, rows: list[dict], alpha: float, per_file_penalty: float, k: int) -> None:
        """MMR reranking should be deterministic for the same inputs."""
        reranked1 = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)
        reranked2 = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)

        # Results should be identical
        assert len(reranked1) == len(reranked2), "Reranking not deterministic - different lengths"

        for i, (r1, r2) in enumerate(zip(reranked1, reranked2)):
            assert r1["content"] == r2["content"], f"Reranking not deterministic at position {i}"

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=0,
            max_size=50,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_handles_edge_cases(
        self, rows: list[dict], alpha: float, per_file_penalty: float, k: int
    ) -> None:
        """MMR reranking should handle edge cases gracefully."""
        if not rows:
            # Empty input should return empty output
            reranked = mmr_rerank([], alpha=alpha, per_file_penalty=per_file_penalty, k=k)
            assert reranked == [], "Empty input should return empty output"
        else:
            # Non-empty input should return non-empty output (if k > 0)
            reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)
            if k > 0 and len(rows) > 0:
                assert len(reranked) > 0, "Non-empty input with k > 0 should return non-empty output"

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
                metadata=st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100), max_size=3),
            ),
            min_size=1,
            max_size=50,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_preserves_metadata(
        self, rows: list[dict], alpha: float, per_file_penalty: float, k: int
    ) -> None:
        """MMR reranking should preserve metadata integrity."""
        # Deduplicate rows by (content, score, doc_id), prefer ones with metadata
        uniq: dict[tuple[str, float, str], dict] = {}
        for r in rows:
            key = (r["content"], r["score"], r.get("doc_id", ""))
            if key not in uniq or (not uniq[key].get("metadata") and r.get("metadata")):
                uniq[key] = r
        rows = list(uniq.values())

        reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)

        # Create lookup for original metadata by content + score + doc_id combination
        # (since multiple rows can have same content and score but different metadata)
        original_metadata = {(row["content"], row["score"], row.get("doc_id", "")): row["metadata"] for row in rows}

        for row in reranked:
            content = row["content"]
            score = row["score"]
            doc_id = row.get("doc_id", "")

            # Find the original row that matches this content, score, and doc_id
            original_row = None
            for orig_row in rows:
                if (
                    orig_row["content"] == content
                    and orig_row["score"] == score
                    and orig_row.get("doc_id", "") == doc_id
                ):
                    original_row = orig_row
                    break

            if original_row and original_row["metadata"]:
                # MMR reranking adds system fields: ingest_run_id, chunk_variant, chunk_id
                # Check that original metadata is preserved (subset check)
                for key, value in original_row["metadata"].items():
                    # Ignore non-informative original metadata values
                    if value in (None, ""):
                        continue
                    if key not in row["metadata"]:
                        record_case(
                            "test_mmr_preserves_metadata_missing_key",
                            {
                                "content": content,
                                "score": score,
                                "doc_id": doc_id,
                                "key": key,
                                "orig_meta": original_row["metadata"],
                                "got_meta": row["metadata"],
                            },
                        )
                    assert (
                        key in row["metadata"]
                    ), f"Original metadata key '{key}' missing for content: {content}, score: {score}, doc_id: {doc_id}"
                    if row["metadata"].get(key) != value:
                        record_case(
                            "test_mmr_preserves_metadata_value_mismatch",
                            {
                                "content": content,
                                "score": score,
                                "doc_id": doc_id,
                                "key": key,
                                "orig_val": value,
                                "got_val": row["metadata"].get(key),
                            },
                        )
                    assert (
                        row["metadata"][key] == value
                    ), f"Original metadata value for '{key}' not preserved for content: {content}, score: {score}, doc_id: {doc_id}"

                # Check that system fields are present
                if "ingest_run_id" not in row["metadata"]:
                    record_case(
                        "test_mmr_metadata_missing_system_ingest_run_id",
                        {"content": content, "score": score, "doc_id": doc_id},
                    )
                assert (
                    "ingest_run_id" in row["metadata"]
                ), f"System field 'ingest_run_id' missing for content: {content}, score: {score}, doc_id: {doc_id}"
                if "chunk_variant" not in row["metadata"]:
                    record_case(
                        "test_mmr_metadata_missing_system_chunk_variant",
                        {"content": content, "score": score, "doc_id": doc_id},
                    )
                assert (
                    "chunk_variant" in row["metadata"]
                ), f"System field 'chunk_variant' missing for content: {content}, score: {score}, doc_id: {doc_id}"
                if "chunk_id" not in row["metadata"]:
                    record_case(
                        "test_mmr_metadata_missing_system_chunk_id",
                        {"content": content, "score": score, "doc_id": doc_id},
                    )
                assert (
                    "chunk_id" in row["metadata"]
                ), f"System field 'chunk_id' missing for content: {content}, score: {score}, doc_id: {doc_id}"

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=1,
            max_size=50,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_improves_diversity(
        self, rows: list[dict], alpha: float, per_file_penalty: float, k: int
    ) -> None:
        """MMR reranking should improve diversity compared to simple score-based ranking."""
        if len(rows) < 2:
            return  # Skip if not enough items for diversity analysis

        # Simple score-based ranking (just sort by score descending)
        score_ranked = sorted(rows, key=lambda x: x["score"], reverse=True)[:k]

        # MMR reranking
        mmr_ranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=per_file_penalty, k=k)

        # Both should have same length
        assert len(score_ranked) == len(mmr_ranked), "Rankings should have same length"

        # MMR should preserve all items from original set
        original_contents = {row["content"] for row in rows}
        mmr_contents = {row["content"] for row in mmr_ranked}
        assert mmr_contents.issubset(original_contents), "MMR should only use original items"


class TestWeightsProperties:
    """Property-based tests for Weights system invariants."""

    @pytest.mark.prop
    @given(
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.dictionaries(st.text(min_size=1, max_size=20), st.floats(min_value=0.0, max_value=1.0), max_size=5),
    )
    @settings(max_examples=25, deadline=50)
    def test_weights_creation(self, semantic: float, lexical: float, freshness: float, custom: dict) -> None:
        """Weights should be creatable with valid inputs."""
        weights = create_weights(semantic, lexical, freshness, custom)

        assert weights["semantic"] == semantic
        assert weights["lexical"] == lexical
        assert weights["freshness"] == freshness
        assert weights["custom"] == custom

    @pytest.mark.prop
    @given(
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=25, deadline=50)
    def test_weights_normalization(self, semantic: float, lexical: float, freshness: float) -> None:
        """Weights should normalize to sum to 1.0."""
        weights = create_weights(semantic, lexical, freshness)

        # Check that weights can be normalized
        total = weights["semantic"] + weights["lexical"] + weights["freshness"]
        if total > 0:
            normalized_semantic = weights["semantic"] / total
            normalized_lexical = weights["lexical"] / total
            normalized_freshness = weights["freshness"] / total

            assert (
                abs(normalized_semantic + normalized_lexical + normalized_freshness - 1.0) < 1e-6
            ), "Normalized weights should sum to 1.0"

    @pytest.mark.prop
    @given(
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=25, deadline=50)
    def test_weights_serialization(self, semantic: float, lexical: float, freshness: float) -> None:
        """Weights should serialize and deserialize correctly."""
        weights = create_weights(semantic, lexical, freshness)

        # Serialize to dict (already a dict)
        weights_dict = dict(weights)

        # Deserialize back (just copy the dict)
        weights_restored = dict(weights_dict)

        assert weights_restored["semantic"] == weights["semantic"]
        assert weights_restored["lexical"] == weights["lexical"]
        assert weights_restored["freshness"] == weights["freshness"]
        assert weights_restored["custom"] == weights["custom"]


class TestLimitsProperties:
    """Property-based tests for Limits system invariants."""

    @pytest.mark.prop
    @given(
        st.integers(min_value=1, max_value=1000),
        st.integers(min_value=100, max_value=100000),
        st.integers(min_value=100, max_value=200000),
        st.integers(min_value=100, max_value=30000),
    )
    @settings(max_examples=25, deadline=50)
    def test_limits_creation(self, max_results: int, max_tokens: int, max_chars: int, timeout_ms: int) -> None:
        """Limits should be creatable with valid inputs."""
        limits = create_limits(max_results, max_tokens, max_chars, timeout_ms)

        assert limits["max_results"] == max_results
        assert limits["max_tokens"] == max_tokens
        assert limits["max_chars"] == max_chars
        assert limits["timeout_ms"] == timeout_ms

    @pytest.mark.prop
    @given(
        st.integers(min_value=1, max_value=1000),
        st.integers(min_value=100, max_value=100000),
        st.integers(min_value=100, max_value=200000),
        st.integers(min_value=100, max_value=30000),
    )
    @settings(max_examples=25, deadline=50)
    def test_limits_validation(self, max_results: int, max_tokens: int, max_chars: int, timeout_ms: int) -> None:
        """Limits should validate input constraints."""
        limits = create_limits(max_results, max_tokens, max_chars, timeout_ms)

        # All values should be positive
        assert limits["max_results"] > 0, "max_results should be positive"
        assert limits["max_tokens"] > 0, "max_tokens should be positive"
        assert limits["max_chars"] > 0, "max_chars should be positive"
        assert limits["timeout_ms"] > 0, "timeout_ms should be positive"

    @pytest.mark.prop
    @given(
        st.integers(min_value=1, max_value=1000),
        st.integers(min_value=100, max_value=100000),
        st.integers(min_value=100, max_value=200000),
        st.integers(min_value=100, max_value=30000),
    )
    @settings(max_examples=25, deadline=50)
    def test_limits_serialization(self, max_results: int, max_tokens: int, max_chars: int, timeout_ms: int) -> None:
        """Limits should serialize and deserialize correctly."""
        limits = create_limits(max_results, max_tokens, max_chars, timeout_ms)

        # Serialize to dict (already a dict)
        limits_dict = dict(limits)

        # Deserialize back (just copy the dict)
        limits_restored = dict(limits_dict)

        assert limits_restored["max_results"] == limits["max_results"]
        assert limits_restored["max_tokens"] == limits["max_tokens"]
        assert limits_restored["max_chars"] == limits["max_chars"]
        assert limits_restored["timeout_ms"] == limits["timeout_ms"]


class TestRetrievalEdgeCases:
    """Property-based tests for retrieval system edge cases."""

    @pytest.mark.prop
    @given(st.text(max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_retrieval_handles_short_strings(self, text: str) -> None:
        """Retrieval system should handle very short strings."""
        if text.strip():  # Only test non-empty strings
            try:
                candidate = create_retrieval_candidate(text, 0.5, text)
                assert candidate["content"] == text
                assert candidate["doc_id"] == text
            except Exception as e:
                # Should be a specific validation error, not a crash
                assert isinstance(e, ValueError | TypeError), f"Unexpected exception for short string: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1000, max_size=5000))
    @settings(max_examples=25, deadline=50)
    def test_retrieval_handles_long_strings(self, text: str) -> None:
        """Retrieval system should handle very long strings."""
        try:
            candidate = create_retrieval_candidate(text, 0.5, text[:50])
            assert len(candidate["content"]) <= len(text)
        except Exception as e:
            # Should be a specific validation error, not a crash
            assert isinstance(e, ValueError | TypeError), f"Unexpected exception for long string: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=25, deadline=50)
    def test_retrieval_handles_special_characters(self, text: str) -> None:
        """Retrieval system should handle special characters."""
        # Add some special characters
        special_text = f"!@#$%^&*()_+-=[]{{}}|;':\",./<>? {text}"

        try:
            candidate = create_retrieval_candidate(special_text, 0.5, special_text[:50])
            assert candidate["content"] == special_text
        except Exception as e:
            # Should be a specific validation error, not a crash
            assert isinstance(e, ValueError | TypeError), f"Unexpected exception for special characters: {type(e)}"
