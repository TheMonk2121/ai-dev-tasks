from __future__ import annotations
import os
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from src.rag import reranker_env as env
from ._regression_capture import record_case
#!/usr/bin/env python3
"""
Property-based tests for reranker_env helpers.
"""





@pytest.mark.prop
@given(val=st.one_of(st.booleans(), st.integers(), st.text(max_size=5)))
@settings(max_examples=20, deadline=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_bool_int_str_resolve_precedence(monkeypatch: pytest.MonkeyPatch, val) -> None:
    # Precedence: first present wins
    for name in ("A", "B", "C"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("B", "1")
    assert env._b("A", "B", default=False) is True
    assert env._i("A", "B", default=0) == 1
    monkeypatch.setenv("A", "0")
    if env._b("A", "B", default=True) is not False:
        record_case("test_reranker_env_precedence_bool", {"A": "0", "B": "1"})
    assert env._b("A", "B", default=True) is False
    if env._i("A", "B", default=2) != 0:
        record_case("test_reranker_env_precedence_int", {"A": "0", "B": "1"})
    assert env._i("A", "B", default=2) == 0
    # Strings fall back to default if not parseable for ints
    monkeypatch.setenv("C", "xyz")
    if env._i("C", default=7) != 7:
        record_case("test_reranker_env_parse_int_default", {"C": "xyz"})
    assert env._i("C", default=7) == 7
    assert isinstance(env._s("C", default=""), str)


@pytest.mark.prop
@given(spec=st.sampled_from(["auto", "cpu", "mps", "cuda", "weird"]))
@settings(max_examples=10, deadline=50)
def test_device_resolution(spec: str) -> None:
    d = env._device(spec)
    if d not in ("cpu", "cuda", "mps"):
        record_case("test_reranker_env_device", {"spec": spec, "resolved": d})
    assert d in ("cpu", "cuda", "mps")