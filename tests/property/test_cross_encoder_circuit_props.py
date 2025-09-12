from __future__ import annotations
import time
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.retrieval.cross_encoder_client import CircuitBreaker
import os
#!/usr/bin/env python3
"""
Property-based tests for CircuitBreaker behavior in cross encoder client.
"""





@pytest.mark.prop
@given(st.integers(min_value=2, max_value=5))
@settings(max_examples=10, deadline=200)
def test_circuit_breaker_opens_on_failures(threshold: int):
    cb = CircuitBreaker(failure_threshold=threshold, recovery_timeout=0.1)

    def fail():
        raise RuntimeError("boom")

    # Trigger failures
    for _ in range(threshold):
        with pytest.raises(RuntimeError):
            cb.call(fail)

    assert cb.state in {"open", "half_open"}

    # After timeout, next call moves to half_open then closed if success
    cb.last_failure_time = time.time() - 1.0

    def ok():
        return 42

    # Should return without raising and reset failures
    _ = cb.call(ok)
    assert cb.state in {"closed", "half_open"}
