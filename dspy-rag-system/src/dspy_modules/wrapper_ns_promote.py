#!/usr/bin/env python3
"""
Namespace promotion helpers: extract ns tokens from query and hard-promote
up to ns_reserved items into the top-k after ranking.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Set, Tuple

NS_REGEX = re.compile(r"\b\d{3}_[A-Za-z0-9\-]+\b")


def extract_ns_tokens(query: str) -> Set[str]:
    return {m.group(0) for m in NS_REGEX.finditer(query or "")}


def is_ns_match(row: Dict[str, Any], ns_tokens: Set[str]) -> bool:
    if not ns_tokens:
        return False
    fp = (row.get("file_path") or "").lower()
    fn = (row.get("filename") or "").lower()
    for ns in ns_tokens:
        ns_l = ns.lower()
        if fp.startswith(ns_l + "/") or ("/" + ns_l + "/") in fp or fn.startswith(ns_l):
            return True
    return False


def dedupe_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Set[Tuple[Any, str]] = set()
    out: List[Dict[str, Any]] = []
    for r in rows:
        key = (r.get("document_id"), (r.get("content") or "")[:64])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def promote_ns_reserved(
    rows: List[Dict[str, Any]], ns_tokens: Set[str], k: int, ns_reserved: int = 2
) -> List[Dict[str, Any]]:
    if not ns_tokens or ns_reserved <= 0:
        return rows[:k]
    ns_rows = [r for r in rows if is_ns_match(r, ns_tokens)]
    non_ns = [r for r in rows if not is_ns_match(r, ns_tokens)]
    promoted = ns_rows[:ns_reserved] + non_ns
    promoted = dedupe_rows(promoted)
    return promoted[:k]


def debug_print(query: str, rows: List[Dict[str, Any]], ns_tokens: Set[str], k: int = 10) -> None:
    ns_total = sum(1 for r in rows if is_ns_match(r, ns_tokens))
    print(f"\n[NS DEBUG] query={query!r} ns_tokens={sorted(ns_tokens)} ns_total_in_pool={ns_total}")
    for i, r in enumerate(rows[:k], 1):
        tag = "NS" if is_ns_match(r, ns_tokens) else "  "
        print(f"{i:2d} {tag} score={str(r.get('score')):>8}  {r.get('filename')}  [{r.get('file_path')}]")
