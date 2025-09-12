from __future__ import annotations
import os
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from src.dspy_modules.retriever.reranker_config import load_reranker_config
from src.dspy_modules.retriever.weights import DEFAULT, load_weights
from ._regression_capture import record_case
    import importlib
    import src.rag.reranker_env
#!/usr/bin/env python3
"""
Property-based tests for retriever weights and reranker config.
"""





@pytest.mark.prop
@given(tag=st.sampled_from(["", "ops_health", "rag_qa_single", "db_workflows"]))
@settings(max_examples=10, deadline=50)
def test_load_weights_contains_defaults(tag: str) -> None:
    w = load_weights(tag=tag, file_path="/nonexistent.yaml")  # force defaults
    for k in DEFAULT.keys():
        if k not in w or not isinstance(w[k], float):
            record_case("test_load_weights_defaults", {"tag": tag, "got": w})
        assert k in w
        assert isinstance(w[k], float)


@pytest.mark.prop
@given(
    enabled=st.booleans(),
    input_topk=st.integers(min_value=1, max_value=100),
    keep=st.integers(min_value=1, max_value=100),
    batch=st.integers(min_value=1, max_value=64),
    device=st.sampled_from(["cpu", "cuda", "mps", "auto"]),
)
@settings(max_examples=10, deadline=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_reranker_env_overrides(
    monkeypatch: pytest.MonkeyPatch, enabled: bool, input_topk: int, keep: int, batch: int, device: str
) -> None:
    # Clear potential file influence
    monkeypatch.delenv("RETRIEVER_WEIGHTS_FILE", raising=False)
    # Set environment overrides used by loader when reranker_env is absent
    monkeypatch.setenv("RERANKER_ENABLED", "1" if enabled else "0")
    monkeypatch.setenv("RERANK_INPUT_TOPK", str(input_topk))
    monkeypatch.setenv("RERANK_KEEP", str(keep))
    monkeypatch.setenv("RERANK_BATCH", str(batch))
    monkeypatch.setenv("TORCH_DEVICE", device)

    # Clear the cache to ensure fresh environment variable reading
    load_reranker_config.cache_clear()

    # Reload the reranker_env module to pick up new environment variables


    importlib.reload(src.rag.reranker_env)

    cfg = load_reranker_config(tag="", file_path="/nonexistent.yaml")
    if cfg["enabled"] is not (enabled is True):
        record_case("test_reranker_env_enabled", {"env": {"RERANKER_ENABLED": "1" if enabled else "0"}, "cfg": cfg})
    assert cfg["enabled"] is (enabled is True)
    if cfg["input_topk"] != input_topk or cfg["keep"] != keep or cfg["batch_size"] != batch:
        record_case(
            "test_reranker_env_counts",
            {"env": {"RERANK_INPUT_TOPK": input_topk, "RERANK_KEEP": keep, "RERANK_BATCH": batch}, "cfg": cfg},
        )
    assert cfg["input_topk"] == input_topk
    assert cfg["keep"] == keep
    assert cfg["batch_size"] == batch
    if cfg["device"] not in ("cpu", "cuda", "mps", "auto"):
        record_case("test_reranker_env_device_cfg", {"env": {"TORCH_DEVICE": device}, "cfg": cfg})
    assert cfg["device"] in ("cpu", "cuda", "mps", "auto")