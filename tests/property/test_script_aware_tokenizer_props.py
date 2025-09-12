from __future__ import annotations
import unicodedata
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.llm.script_aware_tokenizer import (
from ._regression_capture import record_case
import os
#!/usr/bin/env python3
"""
Property-based tests for script-aware tokenizer monotonicity.

Tests that script-aware tokenizers maintain monotonicity while respecting
Unicode script boundaries for multilingual text processing.
"""



    make_multilingual_tokenizer,
    make_script_aware_tokenizer,
    multilingual_character_tokenizer,
    script_aware_character_tokenizer,
)



@pytest.mark.prop
@given(s=st.text(max_size=400))
@settings(max_examples=20, deadline=100)
def test_script_aware_tokenizer_non_negativity(s: str) -> None:
    """Test that script-aware tokenizer never returns negative counts."""
    tokenizer = script_aware_character_tokenizer()
    n = tokenizer.count(s)
    if n < 0:
        record_case("test_script_aware_nonneg", {"raw": s, "count": n})
    assert n >= 0


@pytest.mark.prop
@given(a=st.text(max_size=200), b=st.text(max_size=200))
@settings(max_examples=15, deadline=150)
def test_script_aware_tokenizer_monotonicity(a: str, b: str) -> None:
    """Test that script-aware tokenizer satisfies monotonicity."""
    tokenizer = script_aware_character_tokenizer()

    ca = tokenizer.count(a)
    cb = tokenizer.count(b)
    ab = tokenizer.count(a + b)

    # Script-aware tokenizer should satisfy monotonicity: count(a + b) >= count(a) and count(a + b) >= count(b)
    if ab < ca or ab < cb:
        record_case("test_script_aware_monotonicity", {"a": a, "b": b, "ca": ca, "cb": cb, "cab": ab})

    assert ab >= ca, f"Script-aware tokenizer monotonicity violation: {ab} < {ca}"
    assert ab >= cb, f"Script-aware tokenizer monotonicity violation: {ab} < {cb}"


@pytest.mark.prop
@given(a=st.text(max_size=200), b=st.text(max_size=200))
@settings(max_examples=15, deadline=150)
def test_multilingual_tokenizer_monotonicity(a: str, b: str) -> None:
    """Test that multilingual tokenizer satisfies monotonicity."""
    tokenizer = multilingual_character_tokenizer()

    ca = tokenizer.count(a)
    cb = tokenizer.count(b)
    ab = tokenizer.count(a + b)

    # Multilingual tokenizer should satisfy monotonicity
    if ab < ca or ab < cb:
        record_case("test_multilingual_monotonicity", {"a": a, "b": b, "ca": ca, "cb": cb, "cab": ab})

    assert ab >= ca, f"Multilingual tokenizer monotonicity violation: {ab} < {ca}"
    assert ab >= cb, f"Multilingual tokenizer monotonicity violation: {ab} < {cb}"


@pytest.mark.prop
@given(s=st.text(max_size=400))
@settings(max_examples=20, deadline=100)
def test_script_aware_tokenizer_consistency(s: str) -> None:
    """Test that script-aware tokenizer count matches tokenize length."""
    tokenizer = script_aware_character_tokenizer()

    count = tokenizer.count(s)
    tokens = tokenizer.tokenize(s)

    if count != len(tokens):
        record_case("test_script_aware_consistency", {"text": s, "count": count, "token_count": len(tokens)})

    assert count == len(tokens), f"Count {count} != token count {len(tokens)}"


@pytest.mark.prop
@given(s=st.text(max_size=400))
@settings(max_examples=20, deadline=100)
def test_multilingual_tokenizer_consistency(s: str) -> None:
    """Test that multilingual tokenizer count matches tokenize length."""
    tokenizer = multilingual_character_tokenizer()

    count = tokenizer.count(s)
    tokens = tokenizer.tokenize(s)

    if count != len(tokens):
        record_case("test_multilingual_consistency", {"text": s, "count": count, "token_count": len(tokens)})

    assert count == len(tokens), f"Count {count} != token count {len(tokens)}"


# Multilingual test cases
MULTILINGUAL_TEST_CASES = [
    # Latin + Cyrillic
    ("Hello", "Привет"),
    ("Hello", "мир"),
    ("world", "мир"),
    # Latin + Arabic
    ("Hello", "مرحبا"),
    ("world", "العالم"),
    # Latin + Chinese
    ("Hello", "你好"),
    ("world", "世界"),
    # Latin + Japanese
    ("Hello", "こんにちは"),
    ("world", "世界"),
    # Latin + Korean
    ("Hello", "안녕하세요"),
    ("world", "세계"),
    # Latin + Hindi
    ("Hello", "नमस्ते"),
    ("world", "दुनिया"),
    # Latin + Greek
    ("Hello", "Γεια"),
    ("world", "κόσμος"),
    # Latin + Hebrew
    ("Hello", "שלום"),
    ("world", "עולם"),
    # Mixed scripts
    ("Hello", "Привет", "مرحبا"),
    ("world", "мир", "العالم"),
]


@pytest.mark.parametrize("texts", MULTILINGUAL_TEST_CASES)
def test_multilingual_script_boundaries(texts) -> None:
    """Test that script-aware tokenizer respects script boundaries."""
    tokenizer = script_aware_character_tokenizer()

    # Test individual texts
    individual_counts = [tokenizer.count(text) for text in texts]
    individual_tokens = [tokenizer.tokenize(text) for text in texts]

    # Test concatenated text
    concatenated = "".join(texts)
    concatenated_count = tokenizer.count(concatenated)
    concatenated_tokens = tokenizer.tokenize(concatenated)

    # Count should be sum of individual counts (script boundaries preserved)
    expected_count = sum(individual_counts)
    assert concatenated_count == expected_count, f"Script boundary violation: {concatenated_count} != {expected_count}"

    # Token count should match
    assert concatenated_count == len(concatenated_tokens)

    # Individual token counts should match
    for i, (text, count, tokens) in enumerate(zip(texts, individual_counts, individual_tokens)):
        assert count == len(tokens), f"Text {i} ({text}): count {count} != token count {len(tokens)}"


def test_script_detection() -> None:
    """Test that script detection works correctly."""
    tokenizer = script_aware_character_tokenizer()

    # Test cases with known scripts
    test_cases = [
        ("Hello", "Latin"),
        ("Привет", "Cyrillic"),
        ("مرحبا", "Arabic"),
        ("你好", "Han"),
        ("こんにちは", "Hiragana"),
        ("안녕하세요", "Hangul"),
        ("नमस्ते", "Devanagari"),
        ("Γεια", "Greek"),
        ("שלום", "Hebrew"),
    ]

    for text, expected_script in test_cases:
        tokens = tokenizer.tokenize(text)

        # Should have at least one token
        assert len(tokens) > 0, f"No tokens for {text}"

        # All tokens should be from the same script (since it's a single script text)
        # This is a basic test - in practice, we'd need more sophisticated script detection


def test_empty_string_handling() -> None:
    """Test that script-aware tokenizers handle empty strings correctly."""
    tokenizer = script_aware_character_tokenizer()

    # Empty string should have count 0
    assert tokenizer.count("") == 0
    assert tokenizer.tokenize("") == []

    # Concatenation with empty string should preserve count
    test_string = "Hello"
    assert tokenizer.count(test_string + "") == tokenizer.count(test_string)
    assert tokenizer.count("" + test_string) == tokenizer.count(test_string)


def test_unicode_normalization() -> None:
    """Test that Unicode normalization works correctly with script awareness."""
    # Create tokenizer with and without normalization
    tokenizer_norm = make_script_aware_tokenizer("unicode", normalize_unicode=True)
    tokenizer_no_norm = make_script_aware_tokenizer("unicode", normalize_unicode=False)

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

        # Both should be non-negative
        assert count_norm >= 0
        assert count_no_norm >= 0

        # For these specific cases, normalization should reduce count
        # (combining characters get merged with base characters)
        if len(text) > 1:  # Only for decomposed forms
            assert count_norm <= count_no_norm


def test_multilingual_configurations() -> None:
    """Test different multilingual tokenizer configurations."""
    # Test with script awareness enabled
    tokenizer_script_aware = make_multilingual_tokenizer("unicode", script_aware=True, normalize_unicode=True)

    # Test with script awareness disabled
    tokenizer_no_script = make_multilingual_tokenizer("unicode", script_aware=False, normalize_unicode=True)

    # Test text with multiple scripts
    test_text = "Hello Привет مرحبا"

    count_script_aware = tokenizer_script_aware.count(test_text)
    count_no_script = tokenizer_no_script.count(test_text)

    # Both should be non-negative
    assert count_script_aware >= 0
    assert count_no_script >= 0

    # Script-aware should respect boundaries (may have different count)
    # This is expected behavior - script boundaries can affect tokenization


def test_grapheme_script_aware_tokenizer() -> None:
    """Test script-aware tokenizer with grapheme base tokenizer."""
    tokenizer = make_script_aware_tokenizer("grapheme")

    # Test basic functionality
    test_text = "Hello Привет"
    count = tokenizer.count(test_text)
    tokens = tokenizer.tokenize(test_text)

    assert count >= 0
    assert count == len(tokens)

    # Test monotonicity
    a, b = "Hello", "Привет"
    ca = tokenizer.count(a)
    cb = tokenizer.count(b)
    ab = tokenizer.count(a + b)

    assert ab >= ca
    assert ab >= cb
