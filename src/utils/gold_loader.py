from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class GoldCase:
    id: str
    mode: str  # "retrieval" | "reader" | "decision"
    query: str
    tags: List[str]
    category: Optional[str] = None
    gt_answer: Optional[str] = None
    expected_files: Optional[List[str]] = None
    globs: Optional[List[str]] = None
    expected_decisions: Optional[List[str]] = None
    notes: Optional[str] = None


ALLOWED_MODES = {"retrieval", "reader", "decision"}


def load_gold_cases(path: str | Path) -> List[GoldCase]:
    """Load gold cases from JSONL file with validation."""
    p = Path(path)
    cases: List[GoldCase] = []
    with p.open() as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            # basic validation
            if obj.get("mode") not in ALLOWED_MODES:
                raise ValueError(f"case {obj.get('id')} invalid mode")
            if not obj.get("id") or not obj.get("query") or not obj.get("tags"):
                raise ValueError(f"line {i}: missing required fields")
            # For decision mode, allow empty expected_decisions (means no decisions yet)
            if obj.get("mode") == "decision":
                # Decision mode is valid even with empty expected_decisions
                pass
            # For retrieval mode, allow cases without explicit targets (they test general retrieval)
            elif obj.get("mode") == "retrieval":
                # Retrieval mode is valid even without explicit expected_files/globs
                pass
            elif (
                sum(
                    [
                        bool(obj.get("gt_answer")),
                        bool(obj.get("expected_files")) or bool(obj.get("globs")),
                        bool(obj.get("expected_decisions")),
                    ]
                )
                == 0
            ):
                raise ValueError(f"{obj.get('id')}: no supervision target")
            cases.append(GoldCase(**obj))
    # uniqueness
    ids = [c.id for c in cases]
    if len(ids) != len(set(ids)):
        dupes = [x for x in ids if ids.count(x) > 1]
        raise ValueError(f"Duplicate IDs: {sorted(set(dupes))[:10]}")
    return cases


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
    mode: Optional[str] = None,
) -> List[GoldCase]:
    """Sample cases maintaining tag proportions."""
    rng = random.Random(seed)
    buckets: Dict[str, List[GoldCase]] = {t: [] for t in strata}
    for c in cases:
        for t in c.tags:
            if t in buckets and (mode is None or c.mode == mode):
                buckets[t].append(c)
                break
    out: List[GoldCase] = []
    for t, frac in strata.items():
        take = max(1, int(round(frac * size)))
        rng.shuffle(buckets[t])
        out.extend(buckets[t][:take])
    # pad if rounding error
    if len(out) < size:
        rest = [c for c in cases if c not in out and (mode is None or c.mode == mode)]
        rng.shuffle(rest)
        out.extend(rest[: size - len(out)])
    return out[:size]


def load_manifest(path: str | Path = "evals/gold/v1/manifest.json") -> Dict[str, Any]:
    """Load evaluation manifest with profiles."""
    with open(path) as f:
        return json.load(f)
