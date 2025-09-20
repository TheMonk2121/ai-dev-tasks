from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.memory_graphs.consolidate import collect_turns, run, summarize

#!/usr/bin/env python3
"""
Property tests for memory consolidation graph stubs.
"""


def _turns() -> Any:
    return st.lists(
        st.fixed_dictionaries(
            {"role": st.sampled_from(["user", "assistant"]), "content": st.text(min_size=0, max_size=200)}
        ),
        min_size=0,
        max_size=20,
    )


@pytest.mark.prop
@given(_turns())
@settings(max_examples=10, deadline=100)
def test_collect_and_summarize_idempotent(raw: Any):
    turns = collect_turns(raw)
    s1 = summarize(turns)
    s2 = summarize(turns)
    assert s1 == s2
