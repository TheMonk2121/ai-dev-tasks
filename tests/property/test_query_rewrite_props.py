from __future__ import annotations
import re
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.dspy_modules.retriever.query_rewrite import (
from ._regression_capture import record_case
#!/usr/bin/env python3
"""
Property-based tests for query_rewrite invariants.
"""



    build_channel_queries,
    filename_regex_from_query,
)


@pytest.mark.prop
@given(st.text(max_size=500))
@settings(max_examples=30, deadline=100)
def test_filename_regex_compiles_for_any_text(q: str) -> None:
    pat = filename_regex_from_query(q)
    # Always compile
    try:
        r = re.compile(pat)
        assert isinstance(r, re.Pattern)
    except Exception as e:
        record_case("test_query_rewrite_regex_compile", {"raw": q, "pattern": pat, "error": str(e)})
        raise
    # If there are no tokens, pattern is empty anchor; otherwise should not be '^$'
    toks = re.findall(r"[A-Za-z0-9_.-]{3,}", q or "")
    if toks:
        if pat == "^$":
            record_case("test_query_rewrite_regex_nonempty", {"raw": q, "tokens": toks})
        assert pat != "^$"


@pytest.mark.prop
@given(
    user_q=st.text(max_size=500),
    tag=st.sampled_from(["ops_health", "db_workflows", "meta_ops", "rag_qa_single", "unknown_tag"]),
)
@settings(max_examples=30, deadline=100)
def test_build_channel_queries_shape_and_flags(user_q: str, tag: str) -> None:
    out = build_channel_queries(user_q, tag)
    for key in ("short", "title", "bm25", "vec", "fname_regex", "cold_start"):
        assert key in out

    assert isinstance(out["cold_start"], bool)
    # vec should be non-empty even for empty input
    assert isinstance(out["vec"], str) and len(out["vec"]) > 0

    # cold_start mirrors lexical sparsity heuristic
    toks = re.findall(r"[A-Za-z0-9_]{3,}", (user_q or ""))
    expect_cold = len(toks) < 3
    if out["cold_start"] != expect_cold:
        record_case("test_query_rewrite_cold_start_flag", {"raw": user_q, "tag": tag, "expect": expect_cold, "got": out["cold_start"]})
    assert out["cold_start"] == expect_cold