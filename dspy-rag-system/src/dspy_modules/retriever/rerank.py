#!/usr/bin/env python3
"""
Lightweight MMR rerank with per-file diversity for reader lift.
"""

import math
from collections import defaultdict
from typing import Any
from collections.abc import Sequence


def mmr_rerank(
    rows: list[dict[str, Any]], alpha: float = 0.85, per_file_penalty: float = 0.10, k: int = 25, tag: str = ""
) -> list[dict[str, Any]]:
    """
    MMR rerank to avoid README clusters and reward novelty.

    Args:
        rows: List of dicts with keys: chunk_id, file_path (or filename), score, embedding (vector)
        alpha: MMR balance (0.85 = 85% relevance, 15% diversity)
        per_file_penalty: Penalty for multiple chunks from same file
        k: Number of results to return
        tag: Tag for tag-specific penalties (ops tags get higher penalty)

    Returns:
        Reranked list of results
    """
    out, seen_by_file = [], defaultdict(int)

    # Tag-specific penalty adjustment
    if tag in {"meta_ops", "ops_health"}:
        per_file_penalty = 0.12  # Higher penalty for ops tags

    def _to_vec(v: Any) -> Sequence[float]:
        return v if isinstance(v, list | tuple) else ()

    def cos(v1: Any, v2: Any) -> float:
        """Cosine similarity between two vectors; 0.0 if invalid."""
        v1 = _to_vec(v1)
        v2 = _to_vec(v2)
        if not v1 or not v2:
            return 0.0
        num = sum(a * b for a, b in zip(v1, v2))
        den = math.sqrt(sum(a * a for a in v1)) * math.sqrt(sum(b * b for b in v2))
        return 0.0 if den == 0 else num / den

    selected = []
    candidates = rows[:]  # already scored desc
    while candidates and len(selected) < k:
        best, best_row = -1e9, None
        for r in candidates:
            sim_to_sel = max((cos(r["embedding"], s["embedding"]) for s in selected), default=0.0)
            mmr = alpha * r["score"] - (1 - alpha) * sim_to_sel
            file_pen = per_file_penalty * seen_by_file.get(r.get("file_path") or r.get("filename"), 0)
            mmr -= file_pen
            if mmr > best:
                best, best_row = mmr, r
        selected.append(best_row)
        out.append(best_row)
        key = best_row.get("file_path") or best_row.get("filename")
        seen_by_file[key] += 1
        candidates.remove(best_row)
    return out


def per_file_cap(rows: list[dict[str, Any]], cap: int = 5) -> list[dict[str, Any]]:
    """Limit the number of chunks per file to `cap`, preserving order."""
    out: list[dict[str, Any]] = []
    seen: dict[str, int] = defaultdict(int)
    for r in rows:
        key = (r.get("file_path") or r.get("filename") or "").lower()
        seen[key] += 1
        if seen[key] <= cap:
            out.append(r)
    return out
