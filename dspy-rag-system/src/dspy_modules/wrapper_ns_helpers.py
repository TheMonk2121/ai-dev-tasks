#!/usr/bin/env python3
"""
Robust namespace helpers: extraction, validation, ns-seed fetch, and debug logging.
"""

from __future__ import annotations

import re
from typing import Any
from collections.abc import Sequence

import psycopg2.extras

NS_ALIASES = {
    "core": "000_core",
    # route ops/setup terms to 400_guides (only namespace present alongside core/memory)
    "ops": "400_guides",
    "operations": "400_guides",
    "runbook": "400_guides",
    "playbook": "400_guides",
    "setup": "400_guides",
    "install": "400_guides",
    "bootstrap": "400_guides",
    "workflow": "400_guides",
    # additional synonyms to route to guides for scoped path intent
    "setup docs": "400_guides",
    "naming": "400_guides",
    "conventions": "400_guides",
    "naming conventions": "400_guides",
    "model": "400_guides",
    "configuration": "400_guides",
    "model configuration": "400_guides",
    "memory": "100_memory",
    "research": "400_guides",
    "guides": "400_guides",
}

SEGMENT_RE = re.compile(r"^\d{3}_[A-Za-z0-9\-]+$")
FIND_RE = re.compile(r"(^|/)(\d{3}_[A-Za-z0-9\-]+)(/|$)")


def normalize_ns_token(s: str) -> str | None:
    s = s.strip().replace("\\", "/").lower().replace(" ", "_")
    s = NS_ALIASES.get(s, s)
    return s if SEGMENT_RE.match(s) else None


def path_to_ns(path: str) -> str | None:
    p = (path or "").replace("\\", "/")
    for seg in p.split("/"):
        if SEGMENT_RE.match(seg):
            return seg
    m = FIND_RE.search(p)
    return m.group(2) if m else None


def extract_ns_tokens(query: str) -> list[str]:
    q = (query or "").lower()
    tokens: list[str] = []
    # exact and loose forms
    for m in re.finditer(r"\b(\d{3})[_\- ]([a-z0-9\-]+)\b", q):
        candidate = f"{m.group(1)}_{m.group(2)}"
        n = normalize_ns_token(candidate)
        if n:
            tokens.append(n)
    # alias words
    for kw, mapped in NS_ALIASES.items():
        if re.search(rf"\b{re.escape(kw)}\b", q):
            tokens.append(mapped)
    # dedupe preserve order
    seen = set()
    out: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def validate_ns_tokens(conn, tokens: Sequence[str]) -> list[str]:
    if not tokens:
        return []
    sql = """
        SELECT DISTINCT namespace
        FROM documents
        WHERE namespace = ANY(%s)
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, (list(tokens),))
        return [r["namespace"] for r in cur.fetchall()]


def fetch_ns_seed(conn, ns_tokens: Sequence[str], top_n: int = 80, fuzzy_fallback: bool = True) -> list[dict[str, Any]]:
    if not ns_tokens:
        return []
    strict = [t for t in (normalize_ns_token(t) for t in ns_tokens) if t]
    if not strict:
        return []
    regex = list(strict)
    fuzzy = [f"%/{t}/%" for t in strict]

    sql = """
    SELECT d.id AS document_id, d.filename, d.file_path, dc.content,
           1.0::float AS score, 'ns'::text AS src
    FROM documents d
    JOIN document_chunks dc ON dc.document_id = d.id
    WHERE d.namespace = ANY(%s)
    LIMIT %s

    UNION ALL
    SELECT d.id, d.filename, d.file_path, dc.content,
           0.9::float AS score, 'ns_regex'
    FROM documents d
    JOIN document_chunks dc ON dc.document_id = d.id
    WHERE substring(replace(d.file_path, '\\', '/') from '(^|/)(\d{3}_[[:alnum:]_-]+)(/|$)') = ANY(%s)
    LIMIT %s

    UNION ALL
    SELECT d.id, d.filename, d.file_path, dc.content,
           0.5::float AS score, 'ns_fuzzy'
    FROM documents d
    JOIN document_chunks dc ON dc.document_id = d.id
    WHERE d.file_path ILIKE ANY(%s)
    LIMIT %s
    """
    params = (strict, int(top_n), regex, int(top_n), fuzzy, int(top_n))
    _assert_params_match(sql, params)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def log_debug_ns(query: str, ns_tokens: Sequence[str], vec_rows, bm_rows, ns_rows, fused, ranked) -> None:
    ns_total_in_pool = len(ns_rows)
    print(
        f"[NS DEBUG] q='{query}' ns_tokens={list(ns_tokens)} ns_total_in_pool={ns_total_in_pool} "
        f"vec_pool={len(vec_rows)} bm_pool={len(bm_rows)} fused={len(fused)} ranked={len(ranked)}"
    )
    if ns_total_in_pool == 0:
        print("[NS DEBUG] ⚠️ No namespace candidates found. Check extraction & DB namespaces.")


def _assert_params_match(sql: str, params: Sequence[Any]) -> None:
    placeholders = 0
    i = 0
    while i < len(sql):
        if sql[i] == "%":
            if i + 1 < len(sql) and sql[i + 1] == "s":
                placeholders += 1
                i += 2
                continue
            if i + 1 < len(sql) and sql[i + 1] == "%":
                i += 2
                continue
        i += 1
    assert placeholders == len(params), f"placeholders={placeholders} != params={len(params)}"
