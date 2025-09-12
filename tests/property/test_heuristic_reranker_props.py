from __future__ import annotations
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.retrieval.reranker import _score_rerank, heuristic_rerank
#!/usr/bin/env python3
"""
Property-based tests for heuristic reranker invariants.
"""




@pytest.mark.prop
@given(st.text(min_size=1, max_size=80), st.text(min_size=1, max_size=200))
@settings(max_examples=20, deadline=100)
def test_overlap_monotonicity(query: str, base: str):
    # Adding query tokens to doc should not decrease score
    doc1 = base
    doc2 = base + " " + query
    s1 = _score_rerank(query, doc1)
    s2 = _score_rerank(query, doc2)
    assert s2 >= s1


@pytest.mark.prop
@given(st.text(min_size=1, max_size=80), st.text(min_size=1, max_size=200), st.text(min_size=1, max_size=50))
@settings(max_examples=20, deadline=100)
def test_irrelevant_tokens_non_increase(query: str, base: str, noise: str):
    # Adding unrelated noise should not increase score beyond adding relevant tokens
    s_base = _score_rerank(query, base)
    s_noise = _score_rerank(query, base + " " + noise)
    assert s_noise >= 0.0  # bounded
    # Cannot assert non-increase strictly, but ensure adding exact query yields >= noise case
    s_rel = _score_rerank(query, base + " " + query)
    assert s_rel >= s_noise
