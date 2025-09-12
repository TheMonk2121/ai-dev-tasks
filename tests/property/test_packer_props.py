from __future__ import annotations
import re
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.retrieval.packer import pack_candidates
#!/usr/bin/env python3
"""
Property-based tests for packer invariants.
"""





def _docs():
    return st.dictionaries(
        st.from_regex(r"[A-Za-z0-9]{1,8}", fullmatch=True),
        st.text(min_size=1, max_size=600),
        min_size=1,
        max_size=12,
    )


def _cands(doc_ids):
    return st.lists(st.tuples(st.sampled_from(doc_ids), st.floats(0.0, 1.0)), min_size=1, max_size=25)


@pytest.mark.prop
@given(_docs())
@settings(max_examples=15, deadline=100)
def test_pack_respects_limits_and_headers(documents):
    ids = list(documents.keys())
    candidates = [(i, 1.0) for i in ids]
    out = pack_candidates(candidates, documents, max_chars=500, max_per_document=1)
    assert len(out) <= 500
    # Headers present and per-document cap respected
    blocks = [b for b in out.split("\n\n") if b.strip()]
    seen_counts = {}
    for b in blocks:
        m = re.match(r"\[doc:(.+?)\] ", b)
        assert m, f"Missing header in block: {b!r}"
        did = m.group(1)
        seen_counts[did] = seen_counts.get(did, 0) + 1
    assert all(c <= 1 for c in seen_counts.values())