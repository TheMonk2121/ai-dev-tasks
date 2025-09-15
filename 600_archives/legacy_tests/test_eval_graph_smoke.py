#!/usr/bin/env python3
"""
Smoke test for eval_graph Retrieve node with guarded import and fallback.
Ensures it degrades gracefully (returns list, no exception) when RAGPipeline
or DB is unavailable in the environment.
"""

import pytest

from src.graphs.eval_graph import Retrieve


def test_retrieve_guarded_import_and_fallback() -> None:
    r = Retrieve()  # type: ignore[call-arg]
    out = r.run("What is the answer?")
    assert isinstance(out, list)
    # It's fine if empty when pipeline/DB missing; the key is no crash
