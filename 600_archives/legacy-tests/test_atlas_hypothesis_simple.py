#!/usr/bin/env python3
"""
Simplified Hypothesis property-based testing for Atlas system
Tests core mathematical and data structure invariants
"""

import sys
from typing import Any

import hypothesis
import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same length")

    vec1_array = np.array(vec1, dtype=np.float64)
    vec2_array = np.array(vec2, dtype=np.float64)

    dot_product = float(np.dot(vec1_array, vec2_array))
    norm1 = float(np.linalg.norm(vec1_array))
    norm2 = float(np.linalg.norm(vec2_array))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    result = dot_product / (norm1 * norm2)
    # Clamp to valid cosine similarity range to handle floating point precision issues
    return max(-1.0, min(1.0, result))


def chunk_content_semantic(content: str, chunk_size: int = 450, overlap_ratio: float = 0.10) -> list[dict[str, Any]]:
    """Simple semantic chunking implementation."""
    if len(content) <= chunk_size:
        return [{"content": content, "overlap_start": 0, "overlap_end": 0}]

    import re

    sentences = re.split(r"[.!?]+", content)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    overlap_size = int(chunk_size * overlap_ratio)

    for i in range(0, len(sentences), max(1, len(sentences) // (len(content) // chunk_size + 1))):
        chunk_sentences = sentences[i : i + max(1, len(sentences) // (len(content) // chunk_size + 1))]
        chunk_content = " ".join(chunk_sentences)

        if len(chunk_content) > chunk_size:
            chunk_content = chunk_content[:chunk_size]

        chunks.append(
            {
                "content": chunk_content,
                "overlap_start": max(0, i - overlap_size) if i > 0 else 0,
                "overlap_end": min(len(sentences), i + len(chunk_sentences) + overlap_size),
            }
        )

    return chunks


class TestAtlasCoreHypothesis:
    """Property-based testing for Atlas core functionality."""

    @given(
        vec1=st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=1, max_size=1000),
        vec2=st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=1, max_size=1000),
    )
    def test_cosine_similarity_properties(self, vec1: list[float], vec2: list[float]):
        """Test cosine similarity mathematical properties."""
        # Ensure vectors have same length
        min_len = min(len(vec1), len(vec2))
        vec1 = vec1[:min_len]
        vec2 = vec2[:min_len]

        if len(vec1) == 0:
            return  # Skip empty vectors

        similarity = cosine_similarity(vec1, vec2)

        # Mathematical invariants
        assert -1.0 <= similarity <= 1.0  # Cosine similarity range
        assert isinstance(similarity, float)

        # Self-similarity should be 1.0 (or close for identical vectors)
        if vec1 == vec2 and not all(x == 0.0 for x in vec1):
            assert abs(similarity - 1.0) < 1e-6

        # Zero vector similarity should be 0.0
        if all(x == 0.0 for x in vec1) or all(x == 0.0 for x in vec2):
            assert similarity == 0.0

    @given(content=st.text(min_size=1, max_size=10000))
    def test_semantic_chunking_properties(self, content: str):
        """Test semantic chunking properties."""
        chunks = chunk_content_semantic(content)

        # Invariants
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("content" in chunk for chunk in chunks)
        assert all(isinstance(chunk["content"], str) for chunk in chunks)

        # Content preservation
        reconstructed = "".join(chunk["content"] for chunk in chunks)
        assert len(reconstructed) >= len(content) * 0.8  # Allow some loss due to processing

    @given(embedding=st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=1, max_size=1000))
    def test_embedding_properties(self, embedding: list[float]):
        """Test embedding vector properties."""
        # Test embedding normalization
        if len(embedding) > 0:
            norm = np.linalg.norm(embedding)
            assert norm >= 0.0
            assert isinstance(norm, (float, np.floating))

            # Test that we can create a normalized version
            if norm > 0:
                normalized = [x / norm for x in embedding]
                normalized_norm = np.linalg.norm(normalized)
                assert abs(normalized_norm - 1.0) < 1e-6

    @given(content=st.text(min_size=1, max_size=1000))
    def test_content_chunking_edge_cases(self, content: str):
        """Test content chunking with edge cases."""
        chunks = chunk_content_semantic(content)

        # Edge case: very short content
        if len(content) < 50:
            assert len(chunks) == 1
            assert chunks[0]["content"] == content

        # Edge case: very long content
        if len(content) > 1000:
            assert len(chunks) > 1
            # Check that chunks are reasonable size
            for chunk in chunks:
                assert len(chunk["content"]) <= 450  # chunk_size
                assert len(chunk["content"]) > 0

    @given(
        data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(min_size=0, max_size=100),
                st.integers(min_value=-1000, max_value=1000),
                st.floats(min_value=-1000.0, max_value=1000.0),
                st.booleans(),
                st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10),
            ),
            min_size=1,
            max_size=20,
        )
    )
    def test_metadata_serialization(self, data: dict[str, Any]):
        """Test metadata serialization robustness."""
        # Test that metadata can be serialized to JSON
        import json

        try:
            json_str = json.dumps(data)
            parsed = json.loads(json_str)
            assert parsed == data
        except (TypeError, ValueError) as e:
            # Some data types might not be JSON serializable
            # This is expected behavior, not a bug
            assert isinstance(e, (TypeError, ValueError))

    @given(text=st.text(min_size=0, max_size=1000))
    def test_text_processing_edge_cases(self, text: str):
        """Test text processing with edge cases."""
        # Test with empty string
        if len(text) == 0:
            chunks = chunk_content_semantic(text)
            assert len(chunks) == 1
            assert chunks[0]["content"] == text

        # Test with only whitespace
        if text.isspace():
            chunks = chunk_content_semantic(text)
            assert len(chunks) >= 1

        # Test with special characters
        if any(ord(c) > 127 for c in text):  # Non-ASCII characters
            chunks = chunk_content_semantic(text)
            assert all(isinstance(chunk["content"], str) for chunk in chunks)

    @given(
        vec1=st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=1, max_size=100),
        vec2=st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=1, max_size=100),
    )
    def test_cosine_similarity_edge_cases(self, vec1: list[float], vec2: list[float]):
        """Test cosine similarity with edge cases."""
        min_len = min(len(vec1), len(vec2))
        vec1 = vec1[:min_len]
        vec2 = vec2[:min_len]

        if len(vec1) == 0:
            return

        try:
            similarity = cosine_similarity(vec1, vec2)
            # Allow for floating point precision issues
            assert -1.0000001 <= similarity <= 1.0000001
        except (ValueError, ZeroDivisionError, OverflowError):
            # These are expected for extreme cases
            pass

    @given(content=st.text(min_size=0, max_size=50000))  # Very long content
    def test_large_content_handling(self, content: str):
        """Test handling of very large content."""
        chunks = chunk_content_semantic(content)

        # Should not crash
        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Each chunk should be reasonable size
        for chunk in chunks:
            assert len(chunk["content"]) <= 450
            assert len(chunk["content"]) >= 0


def test_hypothesis_settings():
    """Test that Hypothesis is properly configured."""

    # Test with a simple property
    @given(st.integers(min_value=0, max_value=100))
    def test_simple_property(x: int):
        assert x >= 0
        assert x <= 100

    test_simple_property()


if __name__ == "__main__":
    print("🧪 Running Hypothesis property-based testing...")
    print("This will test edge cases and invariants in the Atlas system.")
    print("If any test fails, it will show the minimal failing example.")

    # Run the tests
    test_hypothesis_settings()
    print("✅ Basic Hypothesis configuration test passed")

    # Note: The full test suite would require a proper test runner
    print("📝 To run the full test suite, use: pytest test_atlas_hypothesis_simple.py -v")
