#!/usr/bin/env python3
"""
Property-based tests for text normalization functions.
Surgical Hypothesis wedge - pure functions only, nightly runs.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Import your text normalization functions
# TODO: Replace with actual imports once we identify the functions
# from src.dspy_modules.enhanced_rag_system import normalize_query


def normalize_query(query: str) -> str:
    """
    Placeholder normalization function.
    Replace with actual implementation.
    """
    if not query:
        return ""

    # Basic normalization: strip, lowercase, collapse whitespace
    # Use Unicode-aware case conversion with special handling for ß
    normalized = query.strip().casefold()

    # Handle special Unicode cases
    normalized = normalized.replace("ß", "ss")
    normalized = normalized.replace("ı", "i")  # Turkish dotless i
    normalized = normalized.replace("i̇", "i")  # Turkish dotted i (İ -> i̇ -> i)

    # Collapse whitespace
    normalized = " ".join(normalized.split())
    return normalized


class TestNormalizeProperties:
    """Property-based tests for text normalization invariants."""

    @pytest.mark.prop
    @given(st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=500))
    @settings(max_examples=25, deadline=50)
    def test_normalize_idempotent(self, s: str) -> None:
        """Normalization should be idempotent: norm(norm(q)) == norm(q)"""
        n1 = normalize_query(s)
        n2 = normalize_query(n1)
        assert n1 == n2, f"Normalization not idempotent: '{s}' -> '{n1}' -> '{n2}'"

    @pytest.mark.prop
    @given(st.text(max_size=500))
    @settings(max_examples=25, deadline=50)
    def test_normalize_whitespace_invariant(self, s: str) -> None:
        """Normalization should handle whitespace consistently"""
        # Test that different whitespace patterns normalize to same result
        variants = [
            s,
            s.replace(" ", "  "),  # Double spaces
            s.replace(" ", "\t"),  # Tabs
            s.replace(" ", "\n"),  # Newlines
            " " + s + " ",  # Leading/trailing spaces
        ]

        normalized_variants = [normalize_query(v) for v in variants]
        # All variants should normalize to the same result
        assert (
            len(set(normalized_variants)) == 1
        ), f"Whitespace variants don't normalize consistently: {normalized_variants}"

    @pytest.mark.prop
    @given(st.text(max_size=500))
    @settings(max_examples=25, deadline=50)
    def test_normalize_case_invariant(self, s: str) -> None:
        """Normalization should handle case consistently"""
        # Test that different case patterns normalize to same result
        variants = [
            s,
            s.upper(),
            s.lower(),
            s.title(),
            s.swapcase(),
        ]

        normalized_variants = [normalize_query(v) for v in variants]
        # All variants should normalize to the same result
        assert len(set(normalized_variants)) == 1, f"Case variants don't normalize consistently: {normalized_variants}"

    @pytest.mark.prop
    @given(st.text(max_size=500))
    @settings(max_examples=25, deadline=50)
    def test_normalize_empty_handling(self, s: str) -> None:
        """Normalization should handle empty/whitespace-only strings consistently"""
        # Test various empty patterns
        empty_variants = [
            "",
            " ",
            "\t",
            "\n",
            "   ",
            "\t\n ",
        ]

        normalized_empty = [normalize_query(v) for v in empty_variants]
        # All empty variants should normalize to empty string
        assert all(
            n == "" for n in normalized_empty
        ), f"Empty variants don't normalize consistently: {normalized_empty}"

    @pytest.mark.prop
    @given(st.text(max_size=500))
    @settings(max_examples=25, deadline=50)
    def test_normalize_preserves_content(self, s: str) -> None:
        """Normalization should preserve essential content (no data loss)"""
        normalized = normalize_query(s)

        # If original had non-whitespace content, normalized should too
        if s.strip():
            assert normalized, f"Normalization lost non-whitespace content: '{s}' -> '{normalized}'"

        # Normalized should not be significantly longer than original
        # Allow for Unicode expansion (e.g., ß -> ss)
        assert len(normalized) <= len(s) * 2, f"Normalization expanded content too much: '{s}' -> '{normalized}'"
