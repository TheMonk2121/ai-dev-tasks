#!/usr/bin/env python3
"""
Lightweight, post-fusion nudge to lift path/namespace/filename-aligned results.
Apply AFTER doc-diversity and BEFORE ns promotion. SQL remains unchanged.
"""

from __future__ import annotations

import re


FILE_TOKEN_RE = re.compile(r"[A-Za-z0-9_\-]+\.(md|mdx|pdf|txt)$", re.IGNORECASE)


def _filename_match_flags(query: str, filename: str) -> dict[str, bool]:
    q = (query or "").lower()
    f = (filename or "").lower()
    exact_tokens = set(q.split())
    quoted = set(re.findall(r'"([^"]+)"', q))
    exact = (f in exact_tokens) or (f in quoted)
    stem = f.split(".")[0] if "." in f else f
    partial = (not exact) and (stem in q or any(tok in f for tok in exact_tokens))
    return {"filename_exact": exact, "filename_partial": partial}


def apply_fusion_nudge(
    rows: list[dict],
    query: str,
    *,
    bonus_path: float = 0.12,
    bonus_ns: float = 0.06,
    bonus_exact: float = 0.08,
    bonus_partial: float = 0.04,
    score_key: str = "score",
) -> list[dict]:
    for r in rows:
        s = float(r.get(score_key, 0.0))
        if r.get("src") == "path":
            s += bonus_path
        if r.get("ns_match"):
            s += bonus_ns
        flags = _filename_match_flags(query, r.get("filename", "")) if r.get("filename") else {}
        if flags.get("filename_exact"):
            s += bonus_exact
            r["filename_exact"] = True
        elif flags.get("filename_partial"):
            s += bonus_partial
            r["filename_partial"] = True
        r[score_key] = s

    rows.sort(key=lambda x: (-float(x.get(score_key, 0.0)), x.get("rrf_rank", 10**9)))
    return rows
