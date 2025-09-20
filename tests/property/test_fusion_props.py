from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.fusion import weighted_rrf

from ._regression_capture import record_case

#!/usr/bin/env python3
"""
Property-based tests for retrieval fusion invariants.
"""


def _doc_ids() -> Any:
    return st.lists(st.text(min_size=1, max_size=8), min_size=1, max_size=20, unique=True)


@pytest.mark.prop
@given(_doc_ids(), _doc_ids(), st.integers(min_value=1, max_value=50))
@settings(max_examples=20, deadline=100)
def test_weighted_rrf_subset_and_limit(bm_ids, vec_ids, limit: Any):
    fused = weighted_rrf(bm_ids, vec_ids, limit=limit)
    # All IDs are from either input
    allowed = set(bm_ids) | set(vec_ids)
    out_ids = [d for d, _ in fused]
    if not set(out_ids).issubset(allowed):
        record_case("fusion_rrf_not_subset", {"bm": bm_ids, "vec": vec_ids, "out": out_ids})
    assert set(out_ids).issubset(allowed)
    # Limit respected
    assert len(out_ids) <= limit


@pytest.mark.prop
@given(
    st.lists(
        st.tuples(st.text(min_size=1, max_size=8), st.floats(min_value=0.0, max_value=1.0)), min_size=1, max_size=20
    ),
    st.lists(
        st.tuples(st.text(min_size=1, max_size=8), st.floats(min_value=0.0, max_value=1.0)), min_size=1, max_size=20
    ),
)
@settings(max_examples=15, deadline=100)
def test_weighted_rrf_deterministic(bm, vec: Any):
    out1 = weighted_rrf(bm, vec)
    out2 = weighted_rrf(bm, vec)
    if out1 != out2:
        record_case("fusion_rrf_nondeterministic", {"bm": bm, "vec": vec, "o1": out1, "o2": out2})
    assert out1 == out2


@pytest.mark.prop
@given(st.text(min_size=1, max_size=8), st.text(min_size=1, max_size=8))
@settings(max_examples=20, deadline=100)
def test_weighted_rrf_weight_flip(doc_a, doc_b: Any):
    # A only in BM25; B only in vector
    out_lex = weighted_rrf([doc_a], [doc_b], lambda_lex=0.99, lambda_sem=0.01)
    out_sem = weighted_rrf([doc_a], [doc_b], lambda_lex=0.01, lambda_sem=0.99)
    top_lex = out_lex[0][0] if out_lex else None
    top_sem = out_sem[0][0] if out_sem else None
    # With high lexical weight, A should dominate; with high semantic, B should dominate
    if not (top_lex == doc_a and top_sem == doc_b):
        record_case(
            "fusion_rrf_weight_flip_unexpected", {"lex_top": top_lex, "sem_top": top_sem, "A": doc_a, "B": doc_b}
        )
    assert top_lex == doc_a
    assert top_sem == doc_b
