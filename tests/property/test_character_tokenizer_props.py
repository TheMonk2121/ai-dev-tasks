from __future__ import annotations
import unicodedata
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.llm.character_tokenizer import (
from ._regression_capture import record_case
import os
#!/usr/bin/env python3
"""
Property-based tests for character-level tokenizer monotonicity.

Tests that character-level tokenizers guarantee the monotonicity property
count(a + b) = count(a) + count(b) for any strings a and b.
"""



    grapheme_cluster_tokenizer,
    make_character_tokenizer,
    strict_character_tokenizer,
    unicode_character_tokenizer,
)



@pytest.mark.prop
@given(s=st.text(max_size=400))
@settings(max_examples=20, deadline=100)
def test_character_tokenizer_non_negativity(s: str) -> None:
    """Test that character tokenizer never returns negative counts."""
    tokenizer = unicode_character_tokenizer()
    n = tokenizer.count(s)
    if n < 0:
        record_case("test_character_nonneg", {"raw": s, "count": n})
    assert n >= 0


@pytest.mark.prop
@given(a=st.text(max_size=200), b=st.text(max_size=200))
@settings(max_examples=15, deadline=150)
def test_character_tokenizer_monotonicity(a: str, b: str) -> None:
    """Test that character tokenizer satisfies strict monotonicity."""
    tokenizer = unicode_character_tokenizer()

    ca = tokenizer.count(a)
    cb = tokenizer.count(b)
    ab = tokenizer.count(a + b)

    # Character tokenizer should satisfy strict monotonicity: count(a + b) = count(a) + count(b)
    expected = ca + cb
    if ab != expected:
        record_case(
            "test_character_monotonicity", {"a": a, "b": b, "ca": ca, "cb": cb, "cab": ab, "expected": expected}
        )

    assert ab == expected, f"Character tokenizer monotonicity violation: {ca} + {cb} = {expected}, got {ab}"


@pytest.mark.prop
@given(a=st.text(max_size=200), b=st.text(max_size=200))
@settings(max_examples=15, deadline=150)
def test_grapheme_tokenizer_monotonicity(a: str, b: str) -> None:
    """Test that grapheme cluster tokenizer satisfies monotonicity."""
    tokenizer = grapheme_cluster_tokenizer()

    ca = tokenizer.count(a)
    cb = tokenizer.count(b)
    ab = tokenizer.count(a + b)

    # Grapheme tokenizer should satisfy monotonicity: count(a + b) >= count(a) and count(a + b) >= count(b)
    if ab < ca or ab < cb:
        record_case("test_grapheme_monotonicity", {"a": a, "b": b, "ca": ca, "cb": cb, "cab": ab})

    assert ab >= ca, f"Grapheme tokenizer monotonicity violation: {ab} < {ca}"
    assert ab >= cb, f"Grapheme tokenizer monotonicity violation: {ab} < {cb}"


@pytest.mark.prop
@given(s=st.text(max_size=400))
@settings(max_examples=20, deadline=100)
def test_character_tokenizer_consistency(s: str) -> None:
    """Test that character tokenizer count matches tokenize length."""
    tokenizer = unicode_character_tokenizer()

    count = tokenizer.count(s)
    tokens = tokenizer.tokenize(s)

    if count != len(tokens):
        record_case("test_character_consistency", {"text": s, "count": count, "token_count": len(tokens)})

    assert count == len(tokens), f"Count {count} != token count {len(tokens)}"


@pytest.mark.prop
@given(s=st.text(max_size=400))
@settings(max_examples=20, deadline=100)
def test_grapheme_tokenizer_consistency(s: str) -> None:
    """Test that grapheme tokenizer count matches tokenize length."""
    tokenizer = grapheme_cluster_tokenizer()

    count = tokenizer.count(s)
    tokens = tokenizer.tokenize(s)

    if count != len(tokens):
        record_case("test_grapheme_consistency", {"text": s, "count": count, "token_count": len(tokens)})

    assert count == len(tokens), f"Count {count} != token count {len(tokens)}"


# Test different tokenizer configurations
@pytest.mark.parametrize("include_whitespace", [True, False])
@pytest.mark.parametrize("include_control_chars", [True, False])
def test_unicode_tokenizer_configurations(include_whitespace: bool, include_control_chars: bool) -> None:
    """Test Unicode tokenizer with different configurations."""
    tokenizer = make_character_tokenizer(
        "unicode",
        normalize_unicode=True,
        include_whitespace=include_whitespace,
        include_control_chars=include_control_chars,
    )

    # Test with various text types
    test_cases = [
        "hello world",  # Basic text
        "hello\tworld\n",  # With whitespace
        "hello\x00world",  # With control characters
        "héllo wörld",  # With Unicode
        "👋🌍",  # With emoji
    ]

    for text in test_cases:
        count = tokenizer.count(text)
        tokens = tokenizer.tokenize(text)

        # Count should match token count
        assert count == len(tokens)

        # Count should be non-negative
        assert count >= 0


def test_strict_character_tokenizer() -> None:
    """Test strict character tokenizer (no whitespace, no control chars)."""
    tokenizer = strict_character_tokenizer()

    # Test cases
    test_cases = [
        ("hello world", "helloworld"),  # Whitespace should be removed
        ("hello\tworld\n", "helloworld"),  # Control chars should be removed
        ("hello\x00world", "helloworld"),  # Null char should be removed
        ("héllo wörld", "héllowörld"),  # Unicode should be preserved
    ]

    for input_text, expected_text in test_cases:
        count = tokenizer.count(input_text)
        tokens = tokenizer.tokenize(input_text)

        # Count should match expected text length
        assert count == len(expected_text)
        assert count == len(tokens)

        # Reconstructed text should match expected
        reconstructed = "".join(tokens)
        assert reconstructed == expected_text


# Unicode-specific edge cases
UNICODE_EDGE_CASES = [
    # Combining characters
    ("a", "́"),  # a + combining acute
    ("e", "̀"),  # e + combining grave
    ("c", "̧"),  # c + combining cedilla
    # Precomposed vs decomposed
    ("é", ""),  # precomposed e with acute
    ("e", "́"),  # decomposed e + combining acute
    # Special Unicode characters
    ("ﬃ", ""),  # ligature ffi
    ("ﬀ", ""),  # ligature ff
    ("ﬄ", ""),  # ligature ffl
    # Mathematical symbols
    ("∑", "∏"),  # summation and product
    ("α", "β"),  # Greek letters
    # Currency symbols
    ("$", "€"),  # dollar and euro
    ("£", "¥"),  # pound and yen
    # Zero-width characters
    ("a", "\u200b"),  # zero-width space
    ("b", "\u200c"),  # zero-width non-joiner
    ("c", "\u200d"),  # zero-width joiner
]


@pytest.mark.parametrize("a,b", UNICODE_EDGE_CASES)
def test_unicode_edge_cases_character_tokenizer(a: str, b: str) -> None:
    """Test character tokenizer with Unicode edge cases."""
    tokenizer = unicode_character_tokenizer()

    ca = tokenizer.count(a)
    cb = tokenizer.count(b)
    ab = tokenizer.count(a + b)

    # Character tokenizer with Unicode normalization may combine characters
    # This is expected behavior - combining characters get merged with base characters
    # We should have: ab >= ca and ab >= cb (monotonicity)
    # But not necessarily: ab == ca + cb (due to normalization)
    assert ab >= ca, f"Unicode edge case violation: {repr(a)} + {repr(b)} -> {ab} < {ca}"
    assert ab >= cb, f"Unicode edge case violation: {repr(a)} + {repr(b)} -> {ab} < {cb}"

    # For non-combining characters, we should have strict equality
    if not (b and unicodedata.category(b).startswith("M")):  # Not a combining character
        expected = ca + cb
        assert (
            ab == expected
        ), f"Non-combining case violation: {repr(a)} + {repr(b)} -> {ca} + {cb} = {expected}, got {ab}"


@pytest.mark.parametrize("a,b", UNICODE_EDGE_CASES)
def test_unicode_edge_cases_grapheme_tokenizer(a: str, b: str) -> None:
    """Test grapheme tokenizer with Unicode edge cases."""
    tokenizer = grapheme_cluster_tokenizer()

    ca = tokenizer.count(a)
    cb = tokenizer.count(b)
    ab = tokenizer.count(a + b)

    # Grapheme tokenizer should satisfy monotonicity
    assert ab >= ca, f"Grapheme edge case violation: {repr(a)} + {repr(b)} -> {ab} < {ca}"
    assert ab >= cb, f"Grapheme edge case violation: {repr(a)} + {repr(b)} -> {ab} < {cb}"


def test_empty_string_handling() -> None:
    """Test that tokenizers handle empty strings correctly."""
    tokenizer = unicode_character_tokenizer()

    # Empty string should have count 0
    assert tokenizer.count("") == 0
    assert tokenizer.tokenize("") == []

    # Concatenation with empty string should preserve count
    test_string = "hello"
    assert tokenizer.count(test_string + "") == tokenizer.count(test_string)
    assert tokenizer.count("" + test_string) == tokenizer.count(test_string)


def test_unicode_normalization() -> None:
    """Test that Unicode normalization works correctly."""
    # Create tokenizer with and without normalization
    tokenizer_norm = make_character_tokenizer("unicode", normalize_unicode=True)
    tokenizer_no_norm = make_character_tokenizer("unicode", normalize_unicode=False)

    # Test cases with different Unicode representations
    test_cases = [
        "é",  # Precomposed
        "e\u0301",  # Decomposed (e + combining acute)
        "ñ",  # Precomposed
        "n\u0303",  # Decomposed (n + combining tilde)
    ]

    for text in test_cases:
        count_norm = tokenizer_norm.count(text)
        count_no_norm = tokenizer_no_norm.count(text)

        # Normalized version should be consistent
        assert count_norm >= 0
        assert count_no_norm >= 0

        # For these specific cases, normalization should reduce count
        # (combining characters get merged with base characters)
        if len(text) > 1:  # Only for decomposed forms
            assert count_norm <= count_no_norm
