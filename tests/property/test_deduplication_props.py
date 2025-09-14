from __future__ import annotations

import os
import time

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.deduplication import HAS_SKLEARN, NearDuplicateFilter

from ._regression_capture import record_case

#!/usr/bin/env python3
"""
Property-based tests for deduplication invariants across methods.
"""





def _candidates_strategy():
    return st.lists(
        st.fixed_dictionaries(
            {
                "text": st.text(min_size=0, max_size=120),
                "score": st.floats(min_value=0.0, max_value=1.0),
            }
        ),
        min_size=0,
        max_size=20,
    )


@pytest.mark.prop
@given(_candidates_strategy())
@settings(max_examples=20, deadline=200)
def test_simple_deduplication_removes_exact_duplicates(cands):
    # Force duplicates
    base = [{"text": "same text", "score": 0.5}, {"text": "same text", "score": 0.4}] + cands
    nf = NearDuplicateFilter(method="simple")
    out = nf.filter_duplicates(list(base), text_field="text")
    if sum(1 for c in out if c.get("text") == "same text") > 1:
        record_case("dedupe_simple_kept_duplicates", {"out": out})
    assert sum(1 for c in out if c.get("text") == "same text") <= 1


@pytest.mark.prop
@given(_candidates_strategy())
@settings(max_examples=20, deadline=200)
def test_deduplication_never_increases_count(cands):
    methods = ["simple", "minhash"] + (["cosine"] if HAS_SKLEARN else [])
    for m in methods:
        nf = NearDuplicateFilter(method=m)
        out = nf.filter_duplicates(list(cands), text_field="text")
        if len(out) > len(cands):
            record_case("dedupe_increased_count", {"method": m, "orig": len(cands), "out": len(out)})
        assert len(out) <= len(cands)
        # Each output text must exist in input
        orig_texts = [c.get("text", "") for c in cands]
        for c in out:
            if c.get("text", "") not in orig_texts:
                record_case("dedupe_output_not_in_input", {"method": m, "text": c.get("text", "")})
            assert c.get("text", "") in orig_texts
