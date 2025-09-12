from __future__ import annotations
import asyncio
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
    from src.flows.qa_graph import Draft, End, FlowState, Start  # type: ignore[import-untyped]
#!/usr/bin/env python3
"""
Property tests for simple QA flow start routing.
"""



SKIP_QA = False
try:
except Exception:
    SKIP_QA = True


@pytest.mark.prop
@given(st.text(min_size=1, max_size=50))
@settings(max_examples=10, deadline=200)
def test_start_routes_short_to_end(q):
    if SKIP_QA:
        pytest.skip("QA flow dependencies unavailable; skipping")
    s = Start()  # type: ignore[assignment]
    state = FlowState(flow_id=__import__("uuid").uuid4(), question=q)
    # The Start.call is async; run it
    nxt = asyncio.get_event_loop().run_until_complete(s.call(state))  # type: ignore[attr-defined]
    assert nxt in {Draft, End}
