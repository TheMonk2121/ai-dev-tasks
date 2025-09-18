from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.uncertainty.confidence_calibration import CalibrationConfig, ConfidenceCalibrator

#!/usr/bin/env python3
"""
Property tests for ConfidenceCalibrator bounds and stability.
"""




@pytest.mark.prop
@given(
    st.lists(st.floats(min_value=0.01, max_value=0.99), min_size=10, max_size=50),
    st.lists(st.booleans(), min_size=10, max_size=50),
)
@settings(max_examples=5, deadline=500)
def test_temperature_calibration_bounds(scores, labels: Any):
    n = min(len(scores), len(labels))
    scores: Any = np.array(scores[:n])
    labels: Any = np.array([1 if b else 0 for b in labels[:n]])
    if n < 10:
        pytest.skip("need enough samples")
    cfg = CalibrationConfig(temperature_scaling=True, isotonic_calibration=False, platt_calibration=False)
    c = ConfidenceCalibrator(cfg)
    c.calibrate_confidence(scores, labels, method="temperature")
    out: Any = c.apply_calibration(scores, method="temperature")
    assert np.all(np.isfinite(out))
    assert np.all(out >= 0.0) and np.all(out <= 1.0)
