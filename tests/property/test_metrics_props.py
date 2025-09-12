from __future__ import annotations
import math
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.evaluation.enhanced_metrics import ECECalculator, NDCGCalculator, TemperatureScaler
from ._regression_capture import record_case
#!/usr/bin/env python3
"""
Property-based tests for enhanced_metrics invariants.
"""





@pytest.mark.prop
@given(
    rels=st.lists(st.floats(min_value=0, max_value=3), min_size=1, max_size=30),
    k=st.integers(min_value=1, max_value=20),
)
@settings(max_examples=25, deadline=100)
def test_ndcg_bounds_and_ordering(rels: list[float], k: int) -> None:
    ideal = sorted(rels, reverse=True)
    nd = NDCGCalculator.ndcg(rels, ideal, k)
    assert 0.0 <= nd <= 1.0
    # Perfect ranking achieves max
    nd_perfect = NDCGCalculator.ndcg(ideal, ideal, k)
    if not (nd_perfect >= nd):
        record_case("test_ndcg_ordering", {"rels": rels, "k": k, "nd": nd, "nd_perfect": nd_perfect})
    assert nd_perfect >= nd


@pytest.mark.prop
@given(
    conf=st.lists(st.floats(min_value=0, max_value=1), min_size=1, max_size=200),
    corr=st.lists(st.booleans(), min_size=1, max_size=200),
)
@settings(max_examples=20, deadline=100)
def test_ece_bounds(conf: list[float], corr: list[bool]) -> None:
    n = min(len(conf), len(corr))
    e = ECECalculator.calculate_ece(conf[:n], corr[:n], n_bins=10)
    if not (0.0 <= e <= 1.0):
        record_case("test_ece_bounds", {"conf": conf[:n], "corr": corr[:n], "ece": e})
    assert 0.0 <= e <= 1.0


@pytest.mark.prop
@given(
    conf=st.lists(st.floats(min_value=0.01, max_value=0.99), min_size=5, max_size=50),
    corr=st.lists(st.booleans(), min_size=5, max_size=50),
)
@settings(max_examples=10, deadline=200)
def test_temperature_scaler_stability(conf: list[float], corr: list[bool]) -> None:
    # Align lengths and avoid degenerate arrays
    n = min(len(conf), len(corr))
    conf = conf[:n]
    corr = corr[:n]
    if n < 5:
        pytest.skip("not enough samples")
    ts = TemperatureScaler()
    t = ts.fit(conf, corr)
    if not math.isfinite(float(t)):
        record_case("test_temp_scaler_finite", {"conf": conf, "corr": corr, "t": t})
    assert math.isfinite(float(t))
    # Calibrate a point and ensure it is within [0,1]
    out = ts.calibrate(conf[0])
    if not (0.0 <= float(out) <= 1.0):
        record_case("test_temp_scaler_output_bounds", {"conf": conf, "t": float(t), "out": float(out)})
    assert 0.0 <= float(out) <= 1.0