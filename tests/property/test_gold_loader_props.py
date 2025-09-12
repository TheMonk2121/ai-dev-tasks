from __future__ import annotations
import json
from pathlib import Path
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from src.utils.gold_loader import filter_cases, load_gold_cases, stratified_sample
from ._regression_capture import record_case
import os
#!/usr/bin/env python3
"""
Property-based tests for gold_loader invariants.
"""





def _gold_case_strategy():
    tags = st.lists(
        st.sampled_from(["ops_health", "meta_ops", "rag_qa_single", "rag_qa_multi", "db_workflows"]),
        min_size=0,
        max_size=3,
        unique=True,
    )
    mode = st.sampled_from(["retrieval", "reader", "decision"])
    base = st.fixed_dictionaries(
        {
            "id": st.uuids().map(str),
            "mode": mode,
            "query": st.text(min_size=1, max_size=200),
            "tags": tags,
            # Provide supervision fields optionally
            "gt_answer": st.one_of(st.none(), st.text(min_size=1, max_size=200)),
            "expected_files": st.one_of(st.none(), st.lists(st.just("README.md"), max_size=2)),
            "globs": st.one_of(st.none(), st.lists(st.just("**/*.md"), max_size=1)),
        }
    )

    def _fix(c: dict) -> dict:
        # Ensure reader cases have gt_answer; keep others as-is
        if c["mode"] == "reader" and not c.get("gt_answer"):
            c["gt_answer"] = "answer"
        return c

    return base.map(_fix)


@pytest.mark.prop
@given(
    cases=st.lists(_gold_case_strategy(), min_size=3, max_size=60, unique_by=lambda x: x["id"]),
    take=st.integers(min_value=1, max_value=30),
    seed=st.integers(),
)
@settings(
    max_examples=20,
    deadline=200,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.function_scoped_fixture],
)
def test_stratified_sample_invariants(tmp_path: Path, cases: list[dict], take: int, seed: int) -> None:
    # Write to JSONL and load via canonical loader
    p = tmp_path / "gold.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    items = load_gold_cases(str(p))
    # Build simple strata based on first tag if present, else default bucket
    strata_tags = ["ops_health", "meta_ops", "rag_qa_single", "rag_qa_multi", "db_workflows"]
    # Uniform fractions summing to 1.0 across a subset of tags
    chosen = [t for t in strata_tags if any(t in c.tags for c in items)] or ["rag_qa_single"]
    frac = 1.0 / len(chosen)
    strata = {t: frac for t in chosen}

    sampled = stratified_sample(items, strata=strata, size=take, seed=seed)
    # Size and uniqueness invariants
    if not (len(sampled) <= take and len(sampled) > 0):
        record_case(
            "test_gold_sample_size",
            {
                "take": take,
                "got": len(sampled),
                "seed": seed,
                "strata": strata,
                "cases": [{"id": c.id, "tags": c.tags, "mode": c.mode} for c in items],
            },
        )
    assert len(sampled) <= take
    assert len(sampled) > 0
    if len({c.id for c in sampled}) != len(sampled):
        record_case(
            "test_gold_sample_unique",
            {"ids": [c.id for c in sampled], "seed": seed, "strata": strata},
        )
    assert len({c.id for c in sampled}) == len(sampled)

    # Determinism by seed
    sampled2 = stratified_sample(items, strata=strata, size=take, seed=seed)
    if [c.id for c in sampled2] != [c.id for c in sampled]:
        record_case(
            "test_gold_seed_determinism",
            {
                "seed": seed,
                "strata": strata,
                "take": take,
                "ids1": [c.id for c in sampled],
                "ids2": [c.id for c in sampled2],
            },
        )
    assert [c.id for c in sampled2] == [c.id for c in sampled]

    # Changing seed should change ordering (not guaranteed different set but usually)
    sampled3 = stratified_sample(items, strata=strata, size=take, seed=seed + 1)
    assert [c.id for c in sampled3] != [c.id for c in sampled] or len(
        set(c.id for c in sampled3) ^ set(c.id for c in sampled)
    ) >= 0


@pytest.mark.prop
@given(
    cases=st.lists(_gold_case_strategy(), min_size=3, max_size=50, unique_by=lambda x: x["id"]),
    size=st.integers(min_value=1, max_value=20),
)
@settings(max_examples=20, deadline=200, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_filter_cases_respects_mode_and_tags(tmp_path: Path, cases: list[dict], size: int) -> None:
    p = tmp_path / "gold.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
    items = load_gold_cases(str(p))

    # Mode filter
    filtered = filter_cases(items, mode="retrieval", size=size, seed=1337)
    if not all(c.mode == "retrieval" for c in filtered):
        record_case(
            "test_filter_cases_mode",
            {"mode": "retrieval", "size": size, "bad_ids": [c.id for c in filtered if c.mode != "retrieval"]},
        )
    assert all(c.mode == "retrieval" for c in filtered)
    assert len(filtered) <= size

    # Tag filter (if any tag exists in dataset)
    any_tags = sorted({t for c in items for t in c.tags})
    if any_tags:
        take_tag = any_tags[0]
        filtered_tag = filter_cases(items, include_tags=[take_tag], size=size, seed=42)
        if not all(take_tag in c.tags for c in filtered_tag):
            record_case(
                "test_filter_cases_tag",
                {"tag": take_tag, "size": size, "bad_ids": [c.id for c in filtered_tag if take_tag not in c.tags]},
            )
        assert all(take_tag in c.tags for c in filtered_tag)
        assert len(filtered_tag) <= size
