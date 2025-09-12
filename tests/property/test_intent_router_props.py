from __future__ import annotations
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.retrieval.intent_router import IntentRouter, IntentRouterConfig
import os
#!/usr/bin/env python3
"""
Property-based tests for IntentRouter invariants.
"""




@pytest.mark.prop
@given(st.text(min_size=1, max_size=200))
@settings(max_examples=20, deadline=100)
def test_classify_idempotent_whitespace_and_case(query: str):
    r = IntentRouter(IntentRouterConfig())
    a = r.classify_intent(query)
    b = r.classify_intent("  " + query + "  ")
    c = r.classify_intent(query.upper())
    # Intent type should remain stable across trivial formatting
    assert a.intent_type == b.intent_type
    assert a.intent_type == c.intent_type
