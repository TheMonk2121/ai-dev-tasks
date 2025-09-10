#!/usr/bin/env python3
import math
import re

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

OPS_TOKENS = {"health", "check", "shell", "zshrc", "zprofile", "env", "setup"}
META_TOKENS = {"canary", "percentage", "rollout", "deploy", "flag", "check"}


def _is_sql_line(s):
    return "```" in s.lower() or any(t in s.lower() for t in SQL_TOKENS)


def _is_sql_command(s):
    """Check if line starts with SQL command keywords."""
    sql_commands = ["create", "alter", "drop", "insert", "update", "delete", "select"]
    s_lower = s.lower().strip()
    return any(s_lower.startswith(cmd) for cmd in sql_commands)


def _has_sql_index_hint(s):
    """Check if line contains SQL index hints."""
    index_hints = ["using gin", "using gist", "using ivfflat", "using hnsw"]
    s_lower = s.lower()
    return any(hint in s_lower for hint in index_hints)


def _tag_bonus(sent: str, tag: str) -> float:
    """Add tag-specific bonuses for ops_health and meta_ops."""
    s = sent.lower()
    if tag == "ops_health":
        return 0.20 if any(t in s for t in OPS_TOKENS) else 0.0
    if tag == "meta_ops":
        return 0.20 if any(t in s for t in META_TOKENS) else 0.0
    return 0.0


def _norm_tokens(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_./-]+", (s or "").lower())


def _filename_tokens(fp: str) -> list[str]:
    name = (fp or "").split("/")[-1].lower()
    return [t for t in re.findall(r"[A-Za-z0-9_.-]{3,}", name) if not t.isdigit()]


def _score_sentence(sent: str, q_uni: set, phrase_list: list[str], fname_toks: set, tag: str = "") -> float:
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
    sql_command_bonus = 0.10 if _is_sql_command(sent) else 0.0
    sql_index_bonus = 0.05 if _has_sql_index_hint(sent) else 0.0

    # First-line bias for SQL commands (helps pick true DDL when two are close)
    first_line_bias = 1.15 if _is_sql_command(sent) and sent.strip().split("\n")[0].strip() == sent.strip() else 1.0

    tag_bonus = _tag_bonus(sent, tag)
    base_score = overlap + phrases + fname_bonus + sql_bonus + sql_command_bonus + sql_index_bonus + tag_bonus
    return base_score * first_line_bias


def select_sentences(
    rows: list[dict],
    query: str,
    tag: str,
    phrase_hints: list[str],
    per_chunk: int = 2,
    total: int = 10,
) -> tuple[str, list[dict]]:
    """
    rows: retrieved items with keys: file_path/filename, embedding_text (chunk text), score,...
    returns (compact_context, selections_meta)
    """
    q_uni = set(_norm_tokens(query))
    picks: list[tuple[float, dict]] = []
    for r in rows:
        text = r.get("text_for_reader") or r.get("embedding_text") or r.get("bm25_text") or r.get("content") or ""
        if not text:
            continue
        sents = _SENT_SPLIT.split(text) if len(text) < 4000 else text.split("\n")
        fname_set = set(_filename_tokens(r.get("file_path") or r.get("filename") or ""))
        scored: list[tuple[float, str]] = []
        for s in sents:
            scored.append((_score_sentence(s, q_uni, phrase_hints, fname_set, tag), s.strip()))
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

    lines: list[str] = []
    for m in chosen:
        anchor = f"{m['file_path']}#chunk:{m['chunk_id']}"
        lines.append(f"[{anchor}] {m['sentence']}")
    compact = "\n".join(lines)
    return compact, chosen
