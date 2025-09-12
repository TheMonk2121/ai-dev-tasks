from __future__ import annotations

import re
import sys
from typing import Any, Dict, List, Optional, Union

# Match repo slugs like 400_12_advanced-configurations (with optional .md)
SLUG_RE = re.compile(r"\b(?P<slug>\d{3}_\d{2}_[a-z0-9\-]+)(?:\.md)?\b", re.I)


def parse_doc_hint(q: str) -> str | None:
    m = SLUG_RE.search(q or "")
    return m.group("slug").lower() if m else None


#!/usr/bin/env python3
"""
Query rewriting and channel-specific query building for RAG system.
Implements the surgical patch to fix BM25 hinting issues.
"""

import re
from typing import Any

TAG_HINTS = {
    "ops_health": ["setup", "shell", "zshrc", "zprofile", "integration"],
    "db_workflows": ["ddl", "sql", "index", "ivfflat", "create", "alter", "script", "idx"],
    "meta_ops": ["canary", "percentage", "check", "deploy", "rollout"],
    "rag_qa_single": ["vector_store", "tsquery", "websearch", "dspy", "bm25"],
}

PHRASE_HINTS = {
    "db_workflows": [
        '"create index"',
        '"create unique index"',
        '"create <-> index"',
        '"alter <-> table"',
        '"alter table"',
        '"create table"',
        '"create materialized view"',
        '"drop index"',
        '"foreign key"',
        '"primary key"',
        '"on conflict"',
        '"generated always as"',
        '"stored"',
        '"using gin"',
        '"create index concurrently"',
        '"drop table"',
        '"rename table"',
        '"add column"',
        '"alter column type"',
        '"create extension"',
        '"explain analyze"',
        '"vacuum analyze"',
        '"grant"',
        '"revoke"',
        '"using gist"',
        '"using ivfflat"',
        '"using hnsw"',
        '"to_tsvector"',
        '"tsquery"',
        '"websearch_to_tsquery"',
    ],
    "ops_health": [
        '"health check"',
        '"shell init"',
        '"zsh profile"',
        '"env setup"',
        '"startup script"',
    ],
    "meta_ops": [
        '"canary deploy"',
        '"percentage rollout"',
        '"deployment check"',
        '"feature flag"',
    ],
    "rag_qa_single": [
        '"vector store"',
        '"tsquery"',
        '"websearch_to_tsquery"',
        '"integration patterns"',
        '"collaboration patterns"',
        '"communication patterns"',
        '"role-specific"',
        '"multi-role"',
        '"context patterns"',
    ],
}


def _nz(s: str) -> str:
    return s if s is not None else ""


def filename_regex_from_query(q: str) -> str:
    """Extract a compact OR-regex from query tokens for filename matching."""
    toks = re.findall(r"[A-Za-z0-9_.-]{3,}", q or "")
    toks = [t.lower() for t in toks if not t.isdigit()]
    if not toks:
        return "^$"
    toks = toks[:6]
    return rf"(?:{'|'.join(re.escape(t) for t in toks)})"


def _lex_sparse(q: str) -> bool:
    """Detect if query is lexically sparse (cold-start condition)."""
    toks = re.findall(r"[A-Za-z0-9_]{3,}", (q or ""))
    return len(toks) < 3


def build_channel_queries(user_q: str, tag: str) -> dict[str, Any]:
    """
    Build channel-specific queries with hints only for short/title channels.

    Args:
        user_q: Raw user query
        tag: Query tag for hint selection

    Returns:
        Dictionary with channel-specific queries
    """
    user_q = _nz(user_q).strip()
    hints = TAG_HINTS.get(tag, [])
    hint_str = " ".join(dict.fromkeys(hints)) if hints else ""
    phrases = " ".join(PHRASE_HINTS.get(tag, [])) if tag in PHRASE_HINTS else ""
    prefix = " ".join([p for p in (phrases, hint_str) if p]).strip()

    # Hints and phrases only for short/title; BM25 stays pure to preserve tf-idf shape
    q_short = f"{prefix} {user_q}".strip() if prefix else user_q
    q_title = q_short
    q_bm25 = user_q  # ← revert: no hint append
    q_vec = user_q or " "  # keep non-empty

    cold_start = _lex_sparse(user_q)
    return {
        "short": q_short,
        "title": q_title,
        "bm25": q_bm25,
        "vec": q_vec,
        "fname_regex": filename_regex_from_query(user_q),
        "cold_start": cold_start,
    }
