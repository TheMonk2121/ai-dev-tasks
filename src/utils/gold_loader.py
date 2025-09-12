from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from src.schemas.eval import GoldCase, Mode
from typing import Any, Dict, List, Optional, Union


def load_gold_cases(path: str | Path) -> list[GoldCase]:
    p = Path(path)
    out: list[GoldCase] = []
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                out.append(GoldCase.model_validate_json(line))
            except Exception as e:
                raise ValueError(f"{p}:{i}: {e}")
    # uniqueness
    seen = set()
    for c in out:
        if c.id in seen:
            raise ValueError(f"Duplicate id detected: {c.id}")
        seen.add(c.id)
    return out


def write_gold_cases(path: str | Path, cases: list[GoldCase]) -> None:
    """Write gold cases to JSONL using stable Pydantic v2 serialization."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for c in cases:
            f.write(c.model_dump_json(exclude_none=True) + "\n")


def filter_cases(
    cases: list[GoldCase],
    include_tags: list[str] | None = None,
    mode: str | None = None,
    size: int | None = None,
    seed: int | None = None,
) -> list[GoldCase]:
    """Filter cases by tags, mode, and optionally sample."""
    pool = cases
    if include_tags:
        tagset = set(include_tags)
        pool = [c for c in pool if tagset & set(c.tags)]
    if mode:
        pool = [c for c in pool if c.mode == mode]
    if seed is not None:
        random.Random(seed).shuffle(pool)
    if size is not None:
        pool = pool[:size]
    return pool


def stratified_sample(
    cases: list[GoldCase],
    strata: dict[str, float],
    size: int,
    seed: int,
    mode: Mode | None = None,
) -> list[GoldCase]:
    rng = random.Random(seed)
    # bucket by first matching tag in strata
    buckets: dict[str, list[GoldCase]] = {t: [] for t in strata}
    for c in cases:
        if mode and c.mode != mode:
            continue
        for t in c.tags:
            if t in buckets:
                buckets[t].append(c)
                break
    out: list[GoldCase] = []

    # Calculate target samples per stratum, ensuring we don't exceed total size
    total_available = sum(len(bucket) for bucket in buckets.values())

    # If no cases match any strata, return random samples from all available cases
    if total_available == 0:
        all_cases = [c for c in cases if (not mode or c.mode == mode)]
        rng.shuffle(all_cases)
        return all_cases[:size]

    if total_available < size:
        # Not enough cases available, return all we have
        for bucket in buckets.values():
            rng.shuffle(bucket)
            out.extend(bucket)
        return out

    # Calculate proportional samples per stratum
    stratum_targets = {}
    remaining_size = size
    remaining_strata = list(strata.items())

    for t, frac in remaining_strata:
        bucket = buckets[t]
        if not bucket:
            continue
        target = max(1, int(round(frac * size)))
        # Don't exceed what's available in this stratum
        actual_target = min(target, len(bucket))
        stratum_targets[t] = actual_target
        remaining_size -= actual_target

    # If we're under the target, distribute remaining samples proportionally
    if remaining_size > 0:
        for t, frac in remaining_strata:
            if t in stratum_targets and remaining_size > 0:
                bucket = buckets[t]
                additional = min(remaining_size, len(bucket) - stratum_targets[t])
                stratum_targets[t] += additional
                remaining_size -= additional

    # Sample from each stratum
    for t, target in stratum_targets.items():
        bucket = buckets[t]
        rng.shuffle(bucket)
        out.extend(bucket[:target])

    # If we still need more samples, pad from remaining cases
    if len(out) < size:
        all_pool = [c for c in cases if (not mode or c.mode == mode) and c not in out]
        rng.shuffle(all_pool)
        out.extend(all_pool[: size - len(out)])

    return out[:size]


def load_manifest(path: str | Path = "300_evals/data/gold/v1/manifest.json") -> dict[str, Any]:
    """Load evaluation manifest with profiles."""
    with open(path) as f:
        return json.load(f)
