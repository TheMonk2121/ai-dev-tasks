#!/usr/bin/env python3
"""
Unit tests for the unified gold dataset system
"""
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.gold_loader import filter_cases, load_gold_cases, load_manifest, stratified_sample


@pytest.mark.critical
def test_gold_loads_and_has_modes():
    """Test that gold dataset loads and has all required modes."""
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")

    assert len(cases) >= 50, f"Expected at least 50 cases, got {len(cases)}"
    assert all(c.mode in {"retrieval", "reader", "decision"} for c in cases), "All cases must have valid mode"
    assert len({c.id for c in cases}) == len(cases), "All case IDs must be unique"

    # Check we have cases of each mode
    modes = {c.mode for c in cases}
    assert "retrieval" in modes, "Must have retrieval cases"
    assert "reader" in modes, "Must have reader cases"
    assert "decision" in modes, "Must have decision cases"


def test_manifest_loading():
    """Test that manifest loads and has required views."""
    manifest = load_manifest()

    assert "views" in manifest, "Manifest must have views section"
    assert "ops_smoke" in manifest["views"], "Must have ops_smoke view"
    assert "repo_gold" in manifest["views"], "Must have repo_gold view"

    # Check view structure
    for view_name, view_config in manifest["views"].items():
        assert "seed" in view_config, f"View {view_name} must have seed"
        assert "strata" in view_config, f"View {view_name} must have strata"
        assert "size" in view_config, f"View {view_name} must have size"

        # Check strata sum to 1.0
        strata_sum = sum(view_config["strata"].values())
        assert abs(strata_sum - 1.0) < 0.01, f"View {view_name} strata sum is {strata_sum}, should be 1.0"


def test_stratified_sampling():
    """Test that stratified sampling works correctly."""
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")
    manifest = load_manifest()

    view = manifest["views"]["ops_smoke"]
    sampled = stratified_sample(cases, strata=view["strata"], size=view["size"], seed=view["seed"])

    assert len(sampled) == view["size"], f"Expected {view['size']} cases, got {len(sampled)}"
    assert all(c.mode in {"retrieval", "reader", "decision"} for c in sampled), "All sampled cases must have valid mode"


def test_filter_cases():
    """Test that case filtering works correctly."""
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")

    # Test mode filtering
    retrieval_cases = filter_cases(cases, mode="retrieval")
    assert all(c.mode == "retrieval" for c in retrieval_cases), "All filtered cases must be retrieval mode"

    # Test tag filtering
    ops_cases = filter_cases(cases, include_tags=["ops_health"])
    assert all("ops_health" in c.tags for c in ops_cases), "All filtered cases must have ops_health tag"

    # Test size limiting
    limited = filter_cases(cases, size=5)
    assert len(limited) <= 5, "Size limit must be respected"


if __name__ == "__main__":
    print("🧪 Running gold dataset tests...")

    try:
        test_gold_loads_and_has_modes()
        print("✅ test_gold_loads_and_has_modes passed")

        test_manifest_loading()
        print("✅ test_manifest_loading passed")

        test_stratified_sampling()
        print("✅ test_stratified_sampling passed")

        test_filter_cases()
        print("✅ test_filter_cases passed")

        print("\n🎯 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
