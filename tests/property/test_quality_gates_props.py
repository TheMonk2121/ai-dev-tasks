from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.quality_gates import QualityGateValidator, validate_evaluation_results

from ._regression_capture import record_case

#!/usr/bin/env python3
"""
Property-based tests for QualityGateValidator invariants.
"""




@pytest.mark.prop
@given(
    metric=st.sampled_from(["f1_score", "recall_at_20", "faithfulness", "precision", "ndcg_10"]),
    soft=st.floats(min_value=0.0, max_value=1.0),
    hard=st.floats(min_value=0.0, max_value=1.0),
    value=st.floats(min_value=0.0, max_value=1.0),
)
@settings(max_examples=30, deadline=100)
def test_quality_gates_hard_soft_behavior(metric: str, soft: float, hard: float, value: float) -> None:
    cfg = {"soft": {metric: soft}, "hard": {metric: hard}}
    qgv = QualityGateValidator(cfg)
    res = qgv.validate({metric: value})

    # Hard violations imply failure
    if value < hard and hard is not None:
        if res.passed:
            record_case(
                "quality_gates_hard_violation_not_failed",
                {"metric": metric, "soft": soft, "hard": hard, "value": value, "res": res.metrics},
            )
        assert res.passed is False
    else:
        # Above hard means passed, regardless of soft
        if not res.passed:
            # Could fail on other metrics, but we only provided one
            record_case(
                "quality_gates_unexpected_fail",
                {"metric": metric, "soft": soft, "hard": hard, "value": value, "res": res.metrics},
            )
        assert res.passed is True


@pytest.mark.prop
@given(value=st.floats(min_value=0.0, max_value=1.0))
@settings(max_examples=10, deadline=100)
def test_quality_gates_no_config_always_pass(value: float) -> None:
    # Point to a non-existent config to ensure no gates are loaded
    res = validate_evaluation_results({"f1_score": value}, config_path="__no_such_config__.yaml")
    assert res.passed is True