from __future__ import annotations
import json
from pathlib import Path
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.utils.gold_loader import load_gold_cases, stratified_sample
from ._regression_capture import record_case
import os
#!/usr/bin/env python3
"""
Property-style tests for manifest-driven sampling against real v1 gold.
"""




MANIFEST = (
    json.loads(Path("evals/gold/v1/manifest.json").read_text())
    if Path("evals/gold/v1/manifest.json").exists()
    else {"views": {}}
)


@pytest.mark.prop
@pytest.mark.skipif(not MANIFEST.get("views"), reason="manifest not available")
@given(view=st.sampled_from(list(MANIFEST["views"].keys())))
@settings(max_examples=5, deadline=200)
def test_manifest_view_sampling_determinism(view: str) -> None:
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")
    cfg = MANIFEST["views"][view]
    sample1 = stratified_sample(
        cases,
        strata=cfg["strata"],
        size=cfg["size"],
        seed=cfg["seed"],
        mode=cfg.get("mode"),
    )
    sample2 = stratified_sample(
        cases,
        strata=cfg["strata"],
        size=cfg["size"],
        seed=cfg["seed"],
        mode=cfg.get("mode"),
    )
    # Check determinism
    ids1 = [c.id for c in sample1]
    ids2 = [c.id for c in sample2]
    if ids1 != ids2:
        record_case("test_manifest_seed_determinism", {"view": view, "ids1": ids1, "ids2": ids2})
    assert ids1 == ids2

    # Check that we get at most the requested size, and at least 1 if cases are available
    if len(sample1) > cfg["size"]:
        record_case("test_manifest_view_size", {"view": view, "expected": cfg["size"], "got": len(sample1)})
    assert len(sample1) <= cfg["size"]
    if cases:  # If cases are available, we should get some
        if len(sample1) == 0:
            record_case("test_manifest_view_nonempty", {"view": view})
        assert len(sample1) > 0
