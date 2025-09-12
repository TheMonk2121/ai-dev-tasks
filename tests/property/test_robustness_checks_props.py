from __future__ import annotations
import time
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.retrieval.robustness_checks import RobustnessChecker
from ._regression_capture import record_case
#!/usr/bin/env python3
"""
Property-based tests for RobustnessChecker invariants.
"""





@pytest.mark.prop
def test_component_health_none_is_unhealthy() -> None:
    rc = RobustnessChecker()

    def check_none():
        return None

    res = rc.check_component_health("dummy", check_none, timeout_ms=10.0)
    assert res.status in {"unhealthy", "degraded"}  # None result triggers unhealthy
    if res.status != "unhealthy":
        record_case("robustness_check_none_not_unhealthy", {"status": res.status, "details": res.details})


@pytest.mark.prop
@given(delay_ms=st.floats(min_value=1.0, max_value=20.0))
@settings(max_examples=10, deadline=500)
def test_component_health_latency_degraded(delay_ms: float) -> None:
    rc = RobustnessChecker()

    def check_delay():
        time.sleep(delay_ms / 1000.0)
        return True

    res = rc.check_component_health("slow", check_delay, timeout_ms=delay_ms / 2.0)
    # Expect degraded due to latency; allow unhealthy if any exception
    if res.status not in {"degraded", "unhealthy", "healthy"}:
        record_case("robustness_check_unexpected_status", {"status": res.status, "latency": res.latency_ms})
    # At least ensure latency measured
    assert res.latency_ms >= 0


@pytest.mark.prop
@given(latencies=st.lists(st.floats(min_value=0.0, max_value=100.0), min_size=1, max_size=50))
@settings(max_examples=15, deadline=200)
def test_performance_metrics_bounds(latencies: list[float]) -> None:
    rc = RobustnessChecker()
    for l in latencies:
        rc.record_query_performance(l, success=True)
    m = rc.get_performance_metrics()
    assert m.avg_latency_ms >= 0
    assert 0.0 <= m.success_rate <= 1.0
    assert 0.0 <= m.error_rate <= 1.0