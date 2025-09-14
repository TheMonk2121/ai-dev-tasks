from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.prefilter import PrefilterConfig, RecallFriendlyPrefilter

from ._regression_capture import record_case

#!/usr/bin/env python3
"""
Property-based tests for RecallFriendlyPrefilter invariants.
"""




def _docs_strategy():
    return st.dictionaries(
        keys=st.text(min_size=1, max_size=8),
        values=st.text(min_size=0, max_size=300),
        min_size=0,
        max_size=30,
    )


def _results_strategy(doc_ids):
    return st.lists(
        st.tuples(st.sampled_from(doc_ids) if doc_ids else st.text(min_size=1, max_size=8), st.floats(0.0, 1.0)),
        min_size=0,
        max_size=30,
    )


@pytest.mark.prop
@given(_docs_strategy())
@settings(max_examples=20, deadline=100)
def test_filter_bm25_subset_and_quality(documents: dict[str, str]) -> None:
    pf = RecallFriendlyPrefilter(PrefilterConfig())
    doc_ids = list(documents.keys())
    results = [(doc_id, 1.0) for doc_id in doc_ids[:10]]

    filtered = pf.filter_bm25_results(results, documents)

    # size monotonicity
    if len(filtered) > len(results):
        record_case("prefilter_bm25_count_increase", {"orig": len(results), "filtered": len(filtered)})
    assert len(filtered) <= len(results)

    # subset doc ids
    orig_ids = {d for d, _ in results}
    filt_ids = {d for d, _ in filtered}
    if not filt_ids.issubset(orig_ids):
        record_case("prefilter_bm25_not_subset", {"orig": list(orig_ids), "filt": list(filt_ids)})
    assert filt_ids.issubset(orig_ids)

    # length constraints
    for d, _ in filtered:
        text = documents.get(d, "")
        if not (pf.config.min_doc_length <= len(text) <= pf.config.max_doc_length):
            record_case("prefilter_bm25_length_violation", {"id": d, "len": len(text)})
        assert pf.config.min_doc_length <= len(text) <= pf.config.max_doc_length


@pytest.mark.prop
@given(_docs_strategy())
@settings(max_examples=20, deadline=100)
def test_filter_vector_subset_and_quality(documents: dict[str, str]) -> None:
    pf = RecallFriendlyPrefilter(PrefilterConfig())
    doc_ids = list(documents.keys())
    results = [(doc_id, 1.0) for doc_id in doc_ids[:10]]

    filtered = pf.filter_vector_results(results, documents)

    # size monotonicity
    assert len(filtered) <= len(results)

    # subset doc ids
    orig_ids = {d for d, _ in results}
    filt_ids = {d for d, _ in filtered}
    assert filt_ids.issubset(orig_ids)

    # length constraints
    for d, _ in filtered:
        text = documents.get(d, "")
        assert pf.config.min_doc_length <= len(text) <= pf.config.max_doc_length


@pytest.mark.prop
@given(_docs_strategy())
@settings(max_examples=15, deadline=100)
def test_diversity_filter_never_increases(documents: dict[str, str]) -> None:
    pf = RecallFriendlyPrefilter(PrefilterConfig())
    ids = list(documents.keys())
    base = [(doc_id, 0.5) for doc_id in ids[:10]]

    filtered = pf.apply_diversity_filter(base, documents)
    if len(filtered) > len(base):
        record_case("prefilter_diversity_increase", {"orig": len(base), "filt": len(filtered)})
    assert len(filtered) <= len(base)
    assert {d for d, _ in filtered}.issubset({d for d, _ in base})


@pytest.mark.prop
@given(_docs_strategy())
@settings(max_examples=15, deadline=100)
def test_prefilter_all_stats_consistency(documents: dict[str, str]) -> None:
    pf = RecallFriendlyPrefilter(PrefilterConfig())
    ids = list(documents.keys())
    bm25 = [(doc_id, 0.8) for doc_id in ids[:10]]
    vec = [(doc_id, 0.9) for doc_id in ids[5:15]]

    fb, fv = pf.prefilter_all(bm25, vec, documents)
    stats = pf.get_filter_stats(bm25, vec, fb, fv)
    assert 0 <= stats["bm25_filtered"] <= stats["bm25_original"]
    assert 0 <= stats["vector_filtered"] <= stats["vector_original"]
    assert 0.0 <= stats["bm25_retention_rate"] <= 1.0
    assert 0.0 <= stats["vector_retention_rate"] <= 1.0
