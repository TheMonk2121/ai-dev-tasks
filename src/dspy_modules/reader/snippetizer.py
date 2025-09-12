from __future__ import annotations

import re
import os

ID = r"[A-Za-z_][A-Za-z0-9_]*"
PATH = r"(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+(?:\.py)?"
FUNC = rf"(?:def|class)\s+({ID})\s*\("
SYMS = re.compile(rf"{PATH}|{FUNC}")


def split_sentences(text: str) -> list[str]:
    # Code-friendly sentence splitter
    parts = re.split(r"(?<=[.!?])\s+(?!\w+::)", text)
    return [p.strip() for p in parts if len(p.strip()) > 0]


def select_snippets(chunk: str, q: str, k: int = 6) -> list[str]:
    sents = split_sentences(chunk)
    # Soft boost for sentences that carry paths/functions
    scored = []
    ql = q.lower()
    for s in sents:
        score = 0.0
        if SYMS.search(s):
            score += 0.5
        if any(t in s.lower() for t in ql.split()[:4]):
            score += 0.3
        score += min(len(s), 300) / 1000.0
        scored.append((score, s))
    return [s for _, s in sorted(scored, reverse=True)[:k]]
