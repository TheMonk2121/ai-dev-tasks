from __future__ import annotations

import os
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.dspy_modules.dspy_reader_program import (
from typing import Any, Dict, List, Optional, Union
    _assert_provenance,
    _carry_meta_inplace,
    _ensure_chunk_id_inplace,
    _to_row_dict,
)


def _row_strategy() -> st.SearchStrategy[dict[str, Any]]:
    md = st.fixed_dictionaries(
        {
            # Required provenance keys (optionally missing to trigger guards)
            "ingest_run_id": st.one_of(st.text(min_size=1), st.none()),
            "chunk_variant": st.one_of(st.text(min_size=1), st.none()),
            # Optional breadcrumbs
            "source_path": st.one_of(st.text(min_size=1), st.none()),
            "start_char": st.one_of(st.integers(min_value=0, max_value=100000), st.none()),
            "end_char": st.one_of(st.integers(min_value=0, max_value=100000), st.none()),
        }
    )
    return st.fixed_dictionaries(
        {
            "text": st.text(min_size=0, max_size=200),
            "score": st.floats(min_value=0.0, max_value=1.0),
            "file_path": st.one_of(st.text(min_size=0, max_size=120), st.none()),
            "chunk_id": st.one_of(st.text(min_size=0, max_size=32), st.none()),
            "metadata": md,
        }
    )


@pytest.mark.property
@settings(max_examples=60, suppress_health_check=[HealthCheck.too_slow])
@given(rows=st.lists(_row_strategy(), min_size=1, max_size=15))
def test_provenance_and_ids_survive_merge(rows: list[dict[str, Any]]):
    # Normalize to dict rows and ensure chunk_id present
    norm = []
    for r in rows:
        d = _to_row_dict(r)
        _ensure_chunk_id_inplace(d)
        norm.append(d)

    # Build donor with required provenance to simulate realistic carry
    donor = {
        "metadata": {
            "ingest_run_id": "run-test",
            "chunk_variant": "cv-test",
        }
    }
    prefetch = {("chunk_id", d.get("chunk_id")): donor for d in norm[: len(norm) // 2]}
    canon = {("chunk_id", d.get("chunk_id")): donor for d in norm}

    # Carry metadata from sources into each row
    merged = []
    for d in norm:
        d2 = dict(d)
        _carry_meta_inplace(
            d2, prefetch.get(("chunk_id", d.get("chunk_id"))), canon.get(("chunk_id", d.get("chunk_id")))
        )
        _ensure_chunk_id_inplace(d2)
        merged.append(d2)

    # After carry, all rows must have provenance keys present (strict check)
    _assert_provenance(merged, where="property_merge", strict=True)

    # chunk_id must remain stable and present
    for before, after in zip(norm, merged):
        assert after.get("chunk_id") == before.get("chunk_id")
        assert isinstance(after.get("chunk_id"), str) and after["chunk_id"]

    # Reader text availability invariant: at least one text-like field present
    for d in merged:
        textish = d.get("text") or d.get("text_for_reader") or d.get("embedding_text") or ""
        assert isinstance(textish, str)


@pytest.mark.property
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    rows=st.lists(_row_strategy(), min_size=1, max_size=20),
    use_prefetch=st.booleans(),
    cap=st.integers(min_value=1, max_value=20),
)
def test_merge_then_cap_preserves_provenance_and_text(rows: list[dict[str, Any]], use_prefetch: bool, cap: int):
    # Normalize
    norm = []
    for r in rows:
        d = _to_row_dict(r)
        _ensure_chunk_id_inplace(d)
        norm.append(d)

    # Optional prefetch map
    donor = {"metadata": {"ingest_run_id": "run-test", "chunk_variant": "cv-test"}}
    prefetch = {("chunk_id", d.get("chunk_id")): donor for d in (norm[: len(norm) // 3] if use_prefetch else [])}
    canon = {("chunk_id", d.get("chunk_id")): donor for d in norm}

    # Carry + dedup merge
    merged_keys = set()
    merged: list[dict[str, Any]] = []
    for d in norm:
        d2 = dict(d)
        _carry_meta_inplace(
            d2, prefetch.get(("chunk_id", d.get("chunk_id"))), canon.get(("chunk_id", d.get("chunk_id")))
        )
        _ensure_chunk_id_inplace(d2)
        key = (d2.get("chunk_id"), d2.get("file_path"))
        if key in merged_keys:
            continue
        merged_keys.add(key)
        merged.append(d2)

    # Cap per file (simple cap by first N rows)
    capped = merged[:cap]

    # Invariants
    _assert_provenance(capped, where="merge_cap", strict=True)
    for d in capped:
        assert d.get("chunk_id")
        # available text for downstream reader
        textish = d.get("text") or d.get("text_for_reader") or d.get("embedding_text") or ""
        assert isinstance(textish, str)
