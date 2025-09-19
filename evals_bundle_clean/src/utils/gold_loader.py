from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from src.schemas.eval import GoldCase, Mode


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
    for t, frac in strata.items():
        bucket = buckets[t]
        rng.shuffle(bucket)
        take = max(1, int(round(frac * size)))
        out.extend(bucket[:take])
    # pad if we're short
    all_pool = [c for c in cases if (not mode or c.mode == mode) and c not in out]
    rng.shuffle(all_pool)
    out.extend(all_pool[: max(0, size - len(out))])
    return out[:size]


def load_manifest(path: str | Path = "evals/gold/v1/manifest.json") -> dict[str, Any]:
    """Load evaluation manifest with profiles."""
    with open(path) as f:
        return json.load(f)
