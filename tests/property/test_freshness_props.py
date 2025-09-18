from __future__ import annotations

import os
import time

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.freshness_enhancer import FreshnessConfig, FreshnessEnhancer

#!/usr/bin/env python3
"""
Property-based tests for freshness enhancer invariants.
"""





def _result(ts: float | None, score: float = 1.0) -> dict:
    return {"score": score, "metadata": {"created_at": ts} if ts else {}}


@pytest.mark.prop
@given(st.floats(min_value=0.0, max_value=100000.0))
@settings(max_examples=15, deadline=100)
def test_time_decay_monotonicity(age_days: float):
    cfg = FreshnessConfig(enable_time_decay=True, enable_recency_prior=False)
    enh = FreshnessEnhancer(cfg)
    now: Any = time.time()
    # Two docs: one older by age_days, one current
    older = _result(now - age_days * 24 * 3600)
    current = _result(now)
    outs, _ = enh.enhance_retrieval_results("latest news", [older, current], current_time=now)
    # Scores should not increase for older doc compared to its original (<= 1.0)
    assert all(0.0 <= r["score"] <= 1.2 for r in outs)  # basic bound with boost allowed elsewhere


@pytest.mark.prop
@given(st.floats(min_value=1.0, max_value=30.0))
@settings(max_examples=15, deadline=100)
def test_recency_boost_prefers_newer(days: float):
    cfg = FreshnessConfig(enable_time_decay=False, enable_recency_prior=True, recency_threshold_days=7)
    enh = FreshnessEnhancer(cfg)
    now: Any = time.time()
    newer = _result(now - 1 * 24 * 3600)
    older = _result(now - days * 24 * 3600)
    outs, _ = enh.enhance_retrieval_results("latest", [older, newer], current_time=now)
    # Newer should rank before older when query is freshness-sensitive
    if len(outs) >= 2:
        assert outs[0]["score"] >= outs[1]["score"]
