from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Optional

from src.schemas.eval import GoldCase, Mode


def load_gold_cases(path: str | Path) -> List[GoldCase]:
    p = Path(path)
    out: List[GoldCase] = []
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                out.append(GoldCase.parse_obj(obj))
            except Exception as e:
                raise ValueError(f"{p}:{i}: {e}")
    # uniqueness
    seen = set()
    for c in out:
        if c.id in seen:
            raise ValueError(f"Duplicate id detected: {c.id}")
        seen.add(c.id)
    return out


def filter_cases(
    cases: List[GoldCase],
    include_tags: Optional[List[str]] = None,
    mode: Optional[str] = None,
    size: Optional[int] = None,
    seed: Optional[int] = None,
) -> List[GoldCase]:
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
    cases: List[GoldCase],
    strata: Dict[str, float],
    size: int,
    seed: int,
    mode: Optional[Mode] = None,
) -> List[GoldCase]:
    rng = random.Random(seed)
    # bucket by first matching tag in strata
    buckets: Dict[str, List[GoldCase]] = {t: [] for t in strata}
    for c in cases:
        if mode and c.mode != mode:
            continue
        for t in c.tags:
            if t in buckets:
                buckets[t].append(c)
                break
    out: List[GoldCase] = []
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


def load_manifest(path: str | Path = "evals/gold/v1/manifest.json") -> Dict[str, Any]:
    """Load evaluation manifest with profiles."""
    with open(path) as f:
        return json.load(f)
