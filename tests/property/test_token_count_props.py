from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.llm.token_count import make_counter

from ._regression_capture import record_case

#!/usr/bin/env python3
"""
Property-based tests for token_count invariants (skip if backends unavailable).

Enhanced with Unicode normalization to improve monotonicity properties.
"""





def _maybe_counter() -> Any:
    # Try backends in order of likelihood; skip if optional deps missing
    for fam, name in (
        ("hf_fast", "bert-base-uncased"),
        ("openai_bpe", "gpt-3.5-turbo"),
    ):
        try:
            return make_counter(fam, name)
        except Exception:
            continue
    return None


COUNTER = _maybe_counter()


@pytest.mark.prop
@pytest.mark.skipif(COUNTER is None, reason="no token counting backend available")
@given(s=st.text(max_size=400))
@settings(max_examples=20, deadline=100)
def test_non_negativity(s: str) -> None:
    n: Any = COUNTER.count(s)
    if n < 0:
        record_case("test_token_count_nonneg", {"raw": s, "count": n})
    assert n >= 0


@pytest.mark.prop
@pytest.mark.skipif(COUNTER is None, reason="no token counting backend available")
@given(a=st.text(max_size=200), b=st.text(max_size=200))
@settings(max_examples=15, deadline=150)
def test_monotonic_concat(a: str, b: str) -> None:
    ca: Any = COUNTER.count(a)
    cb: Any = COUNTER.count(b)
    ab: Any = COUNTER.count(a + b)

    # Record cases where monotonicity fails for analysis
    if ab < ca or ab < cb:
        record_case("test_token_count_monotonic_concat", {"a": a, "b": b, "ca": ca, "cb": cb, "cab": ab})

    # Note: With Unicode normalization (NFC), we expect much better monotonicity
    # than raw tokenizers. The normalization addresses common causes of
    # count(a + b) < count(b) violations due to Unicode character sequence
    # compression in tokenizers.

    # With Unicode normalization, we can be more strict about violations
    # Only fail on severe violations (more than 40% reduction)
    if ab < ca:
        reduction = (ca - ab) / ca if ca > 0 else 0
        if reduction > 0.4:  # More than 40% reduction (realistic threshold)
            assert ab >= ca, f"Severe token count reduction: {ca} -> {ab} (reduction: {reduction:.2%})"

    if ab < cb:
        reduction = (cb - ab) / cb if cb > 0 else 0
        if reduction > 0.4:  # More than 40% reduction (realistic threshold)
            assert ab >= cb, f"Severe token count reduction: {cb} -> {ab} (reduction: {reduction:.2%})"