#!/usr/bin/env python3
import math
import re
from typing import Dict, List, Tuple

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

SQL_TOKENS = {
    "create",
    "alter",
    "drop",
    "index",
    "table",
    "materialized",
    "view",
    "foreign",
    "primary",
    "using",
    "gin",
    "gist",
    "ivfflat",
    "to_tsvector",
    "tsquery",
    "websearch_to_tsquery",
}


def _is_sql_line(s):
    return "```" in s.lower() or any(t in s.lower() for t in SQL_TOKENS)


def _norm_tokens(s: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_./-]+", (s or "").lower())


def _filename_tokens(fp: str) -> List[str]:
    name = (fp or "").split("/")[-1].lower()
    return [t for t in re.findall(r"[A-Za-z0-9_.-]{3,}", name) if not t.isdigit()]


def _score_sentence(sent: str, q_uni: set, phrase_list: List[str], fname_toks: set) -> float:
    if not sent:
        return 0.0
    s_uni = set(_norm_tokens(sent))
    overlap = len(s_uni & q_uni) / max(1.0, math.sqrt(len(s_uni)))
    phrases = 0.0
    for p in phrase_list:
        inner = p.strip('"').lower()
        if inner and inner in sent.lower():
            phrases = 0.4
            break
    fname_bonus = 0.2 if (s_uni & fname_toks) else 0.0
    sql_bonus = 0.35 if _is_sql_line(sent) else 0.0
    return overlap + phrases + fname_bonus + sql_bonus


def select_sentences(
    rows: List[Dict],
    query: str,
    tag: str,
    phrase_hints: List[str],
    per_chunk: int = 2,
    total: int = 10,
) -> Tuple[str, List[Dict]]:
    """
    rows: retrieved items with keys: file_path/filename, embedding_text (chunk text), score,...
    returns (compact_context, selections_meta)
    """
    q_uni = set(_norm_tokens(query))
    picks: List[Tuple[float, Dict]] = []
    for r in rows:
        text = r.get("embedding_text") or ""
        if not text:
            continue
        sents = _SENT_SPLIT.split(text) if len(text) < 4000 else text.split("\n")
        fname_set = set(_filename_tokens(r.get("file_path") or r.get("filename") or ""))
        scored: List[Tuple[float, str]] = []
        for s in sents:
            scored.append((_score_sentence(s, q_uni, phrase_hints, fname_set), s.strip()))
        scored.sort(key=lambda t: t[0], reverse=True)
        for score, sent in scored[:per_chunk]:
            if not sent:
                continue
            picks.append(
                (
                    score + 1e-6 * float(r.get("score", 0.0) or 0.0),
                    {
                        "file_path": r.get("file_path") or r.get("filename") or "",
                        "chunk_id": r.get("chunk_id"),
                        "sentence": sent,
                        "s_score": float(score),
                        "r_score": float(r.get("score", 0.0) or 0.0),
                    },
                )
            )

    picks.sort(key=lambda t: t[0], reverse=True)
    chosen = [m for _, m in picks[:total]]

    lines: List[str] = []
    for m in chosen:
        anchor = f"{m['file_path']}#chunk:{m['chunk_id']}"
        lines.append(f"[{anchor}] {m['sentence']}")
    compact = "\n".join(lines)
    return compact, chosen
