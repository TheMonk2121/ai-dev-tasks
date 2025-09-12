from __future__ import annotations
import asyncio
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.retrieval.windowing import DocumentWindower, count_tokens
from ._regression_capture import record_case
import os
#!/usr/bin/env python3
"""
Property-based tests for windowing invariants.
"""





def _doc_strategy():
    return st.fixed_dictionaries(
        {
            "document_id": st.text(min_size=1, max_size=12),
            "text": st.text(min_size=1, max_size=1200),
            "score": st.floats(min_value=0.0, max_value=1.0),
            "metadata": st.dictionaries(st.text(min_size=1, max_size=10), st.text(max_size=30), max_size=3),
        }
    )


@pytest.mark.prop
@given(st.lists(_doc_strategy(), min_size=1, max_size=5))
@settings(max_examples=15, deadline=200)
def test_windowing_basic_invariants(candidates):
    w = DocumentWindower(window_size_tokens=100, overlap_pct=25, min_window_tokens=10)
    windows = w.create_windows(candidates, max_windows_per_doc=3)
    # Count per doc
    per_doc = {}
    for win in windows:
        per_doc.setdefault(win.document_id, 0)
        per_doc[win.document_id] += 1
        # Non-empty
        assert win.text.strip()
        # Bound token window
        if count_tokens(win.text) > w.window_size_tokens + 5:
            record_case("window_token_excess", {"id": win.window_id, "tok": count_tokens(win.text)})
        assert count_tokens(win.text) <= w.window_size_tokens + 5
        # Token positions coherent
        assert win.end_token > win.start_token
    # Not exceeding max per doc
    assert all(c <= 3 for c in per_doc.values())


@pytest.mark.prop
@given(_doc_strategy())
@settings(max_examples=15, deadline=200)
def test_window_ordering_and_indices(doc):
    w = DocumentWindower(window_size_tokens=80, overlap_pct=33, min_window_tokens=10)
    outs = w.create_windows([doc], max_windows_per_doc=5)
    # Indices monotonic
    idxs = [win.window_index for win in outs]
    assert idxs == sorted(idxs)
    # Grouped by doc id
    assert all(win.document_id == doc.get("document_id") or win.document_id == (doc.get("id") or "unknown") for win in outs)
