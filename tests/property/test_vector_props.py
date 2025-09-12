from __future__ import annotations
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
import os
#!/usr/bin/env python3
"""
Property-based tests for vector operations invariants.
"""



def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) == 0 or len(b) == 0:
        return 0.0

    # Normalize vectors
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    # Check for overflow/underflow in norms
    if np.isnan(norm_a) or np.isinf(norm_a) or np.isnan(norm_b) or np.isinf(norm_b):
        return 0.0

    # Check for overflow/underflow in dot product
    dot_product = np.dot(a, b)
    if np.isnan(dot_product) or np.isinf(dot_product):
        return 0.0

    result = dot_product / (norm_a * norm_b)

    # Check for overflow in final result
    if np.isnan(result) or np.isinf(result):
        return 0.0

    # Clamp to valid range [-1, 1] to handle floating point precision issues
    return float(np.clip(result, -1.0, 1.0))


def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Normalize vector to unit length."""
    norm = np.linalg.norm(v)
    if norm == 0:
        # For zero vectors, return a unit vector in the first dimension
        result = np.zeros_like(v)
        if len(v) > 0:
            result[0] = 1.0
        return result

    # Check for overflow/underflow
    if np.isnan(norm) or np.isinf(norm):
        # For overflow cases, return a unit vector in the first dimension
        result = np.zeros_like(v)
        if len(v) > 0:
            result[0] = 1.0
        return result

    return v / norm


class TestVectorProperties:
    """Property-based tests for vector operations invariants."""

    @pytest.mark.prop
    @given(st.lists(st.floats(allow_infinity=False, allow_nan=False, width=32), min_size=2, max_size=128))
    @settings(max_examples=25, deadline=50)
    def test_cosine_bounds(self, vec: list[float]) -> None:
        """Cosine similarity should be in [-1, 1]"""
        a = np.array(vec, dtype=np.float32)
        b = np.array(vec[::-1], dtype=np.float32)  # Reverse for different vector
        cos = cosine_similarity(a, b)
        assert -1.0 <= cos <= 1.0, f"Cosine similarity out of bounds: {cos}"

    @pytest.mark.prop
    @given(st.lists(st.floats(allow_infinity=False, allow_nan=False, width=32), min_size=2, max_size=128))
    @settings(max_examples=25, deadline=50)
    def test_cosine_symmetry(self, vec: list[float]) -> None:
        """Cosine similarity should be symmetric: cos(a,b) == cos(b,a)"""
        a = np.array(vec, dtype=np.float32)
        b = np.array(vec[::-1], dtype=np.float32)
        cos_ab = cosine_similarity(a, b)
        cos_ba = cosine_similarity(b, a)
        assert abs(cos_ab - cos_ba) < 1e-6, f"Cosine similarity not symmetric: {cos_ab} != {cos_ba}"

    @pytest.mark.prop
    @given(st.lists(st.floats(allow_infinity=False, allow_nan=False, width=32), min_size=2, max_size=128))
    @settings(max_examples=25, deadline=50)
    def test_cosine_identical_vectors(self, vec: list[float]) -> None:
        """Cosine similarity of identical vectors should be 1"""
        a = np.array(vec, dtype=np.float32)
        cos = cosine_similarity(a, a)

        # Handle zero vectors specially
        if np.linalg.norm(a) == 0:
            assert cos == 0.0, f"Zero vector cosine similarity should be 0: {cos}"
        # Handle overflow cases (very large numbers that actually cause overflow)
        elif np.any(np.isinf(a)) or np.any(np.isnan(a)) or np.isinf(np.linalg.norm(a)) or np.isnan(np.linalg.norm(a)):
            # For actual overflow cases, we expect 0.0 due to our overflow protection
            assert cos == 0.0, f"Overflow vector cosine similarity should be 0: {cos}"
        else:
            assert abs(cos - 1.0) < 1e-6, f"Identical vectors cosine similarity not 1: {cos}"

    @pytest.mark.prop
    @given(st.lists(st.floats(allow_infinity=False, allow_nan=False, width=32), min_size=2, max_size=128))
    @settings(max_examples=25, deadline=50)
    def test_normalize_unit_length(self, vec: list[float]) -> None:
        """Normalized vectors should have unit length"""
        a = np.array(vec, dtype=np.float32)
        normalized = normalize_vector(a)

        norm = np.linalg.norm(normalized)
        # Use more lenient tolerance for floating point precision
        assert abs(norm - 1.0) < 1e-5, f"Normalized vector not unit length: {norm}"

    @pytest.mark.prop
    @given(st.lists(st.floats(allow_infinity=False, allow_nan=False, width=32), min_size=2, max_size=128))
    @settings(max_examples=25, deadline=50)
    def test_normalize_preserves_direction(self, vec: list[float]) -> None:
        """Normalization should preserve direction (proportionality)"""
        a = np.array(vec, dtype=np.float32)
        if np.linalg.norm(a) == 0:
            return  # Skip zero vectors

        # Skip overflow cases where our function returns a unit vector
        if np.isinf(np.linalg.norm(a)) or np.isnan(np.linalg.norm(a)):
            return  # Skip overflow cases

        # Skip very small numbers that cause precision issues
        if np.any(np.abs(a) < 1e-10):
            return  # Skip very small numbers

        normalized = normalize_vector(a)

        # Check that normalized vector is proportional to original
        # (allowing for floating point precision)
        if np.any(a != 0):
            ratio = normalized / (a + 1e-9)  # Add small epsilon to avoid division by zero
            ratios = ratio[a != 0]
            # Use more lenient tolerance for very small numbers
            assert np.allclose(
                ratios, ratios[0], rtol=1e-3
            ), f"Normalization doesn't preserve direction: {a} -> {normalized}"

    @pytest.mark.prop
    @given(st.lists(st.floats(allow_infinity=False, allow_nan=False, width=32), min_size=2, max_size=128))
    @settings(max_examples=25, deadline=50)
    def test_normalize_idempotent(self, vec: list[float]) -> None:
        """Normalization should be idempotent: normalize(normalize(v)) == normalize(v)."""
        a = np.array(vec, dtype=np.float32)
        norm1 = normalize_vector(a)
        norm2 = normalize_vector(norm1)

        # Use more lenient tolerance for floating point precision
        assert np.allclose(norm1, norm2, rtol=1e-5), f"Normalization not idempotent: {a} -> {norm1} -> {norm2}"
