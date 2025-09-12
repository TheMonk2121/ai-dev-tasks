import sys
import os
#!/usr/bin/env python3
"""
Property-based tests for retrieval system invariants.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.dspy_modules.retriever.rerank import mmr_rerank
from ._regression_capture import record_case


def create_retrieval_candidate(
    content: str,
    score: float,
    metadata: dict | None = None,
) -> dict:
    """Create a retrieval candidate for testing."""
    if metadata is None:
        metadata = {}

    return {
        "content": content,
        "score": score,
        "metadata": metadata,
        "embedding": np.random.rand(128).tolist(),  # Random embedding
    }


class TestRerankingProperties:
    """Property-based tests for reranking system invariants."""

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
            max_size=20,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_preserves_input_count(self, rows: list[dict], alpha: float, penalty: float, k: int) -> None:
        """MMR reranking should not change the total number of items."""
        original_count = len(rows)
        reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=penalty, k=k)

        # Should not exceed original count
        if len(reranked) > original_count:
            record_case("test_mmr_preserve_count", {"orig": original_count, "got": len(reranked), "k": k, "alpha": alpha, "penalty": penalty})
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
            max_size=20,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_respects_k_limit(self, rows: list[dict], alpha: float, penalty: float, k: int) -> None:
        """MMR reranking should respect the k limit."""
        reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=penalty, k=k)

        if len(reranked) > k:
            record_case("test_mmr_respects_k", {"got": len(reranked), "k": k})
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
            max_size=20,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_preserves_content(self, rows: list[dict], alpha: float, penalty: float, k: int) -> None:
        """MMR reranking should preserve content integrity."""
        reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=penalty, k=k)

        # All reranked items should be from the original set
        original_contents = {row["content"] for row in rows}
        reranked_contents = {row["content"] for row in reranked}

        if not reranked_contents.issubset(original_contents):
            record_case("test_mmr_preserves_content", {"missing": list(reranked_contents - original_contents)})
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
            max_size=20,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_deterministic(self, rows: list[dict], alpha: float, penalty: float, k: int) -> None:
        """MMR reranking should be deterministic for the same inputs."""
        reranked1 = mmr_rerank(rows, alpha=alpha, per_file_penalty=penalty, k=k)
        reranked2 = mmr_rerank(rows, alpha=alpha, per_file_penalty=penalty, k=k)

        # Results should be identical
        if len(reranked1) != len(reranked2):
            record_case("test_mmr_deterministic_len", {"len1": len(reranked1), "len2": len(reranked2)})
        assert len(reranked1) == len(reranked2), "Reranking not deterministic - different lengths"

        for i, (r1, r2) in enumerate(zip(reranked1, reranked2)):
            if r1["content"] != r2["content"]:
                record_case("test_mmr_deterministic_content", {"pos": i, "c1": r1["content"], "c2": r2["content"]})
            assert r1["content"] == r2["content"], f"Reranking not deterministic at position {i}"

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=1,
            max_size=20,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_handles_empty_input(self, rows: list[dict], alpha: float, penalty: float, k: int) -> None:
        """MMR reranking should handle edge cases gracefully."""
        if not rows:
            # Empty input should return empty output
            reranked = mmr_rerank([], alpha=alpha, per_file_penalty=penalty, k=k)
            assert reranked == [], "Empty input should return empty output"
        else:
            # Non-empty input should return non-empty output (if k > 0)
            reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=penalty, k=k)
            if k > 0 and len(rows) > 0:
                if len(reranked) == 0:
                    record_case("test_mmr_handles_nonempty", {"rows": len(rows), "k": k})
                assert len(reranked) > 0, "Non-empty input with k > 0 should return non-empty output"

    @pytest.mark.prop
    @given(
        st.lists(
            st.builds(
                create_retrieval_candidate,
                content=st.text(min_size=1, max_size=500),
                score=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=1,
            max_size=20,
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_mmr_rerank_preserves_metadata(self, rows: list[dict], alpha: float, penalty: float, k: int) -> None:
        """MMR reranking should preserve metadata integrity."""
        reranked = mmr_rerank(rows, alpha=alpha, per_file_penalty=penalty, k=k)

        # Create lookup for original metadata
        original_metadata = {row["content"]: row["metadata"] for row in rows}

        for row in reranked:
            content = row["content"]
            original_meta = original_metadata[content]

            # MMR reranking adds system fields: ingest_run_id, chunk_variant, chunk_id
            # Check that original metadata is preserved (subset check)
            for key, value in original_meta.items():
                assert key in row["metadata"], f"Original metadata key '{key}' missing for content: {content}"
                assert (
                    row["metadata"][key] == value
                ), f"Original metadata value for '{key}' not preserved for content: {content}"

            # Check that system fields are present
            for key in ("ingest_run_id", "chunk_variant", "chunk_id"):
                if key not in row["metadata"]:
                    record_case("test_mmr_system_fields", {"content": content, "missing": key})
                assert key in row["metadata"], f"System field '{key}' missing for content: {content}"
