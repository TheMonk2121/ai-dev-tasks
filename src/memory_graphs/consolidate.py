from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any
from src.config.settings import get_settings
from typing import Any, Dict, List, Optional, Union
"""Memory consolidation graph (stubbed, off hot path).

This module provides a lightweight, typed orchestration for consolidating
conversation turns into durable memory artifacts. It is gated by
`Settings.use_memory_graph` and is safe to import when disabled.
"""





@dataclass
class Turn:
    role: str
    content: str


@dataclass
class ConsolidationResult:
    summary: str
    facts: list[dict[str, Any]]
    links: list[dict[str, Any]]
    upserts: dict[str, int]


def collect_turns(raw: Iterable[dict[str, Any]]) -> list[Turn]:
    """Collect turns from raw records (minimal adapter)."""
    out: list[Turn] = []
    for r in raw or []:
        role = str(r.get("role", "user"))
        content = str(r.get("content") or r.get("text") or "")
        if not content:
            continue
        out.append(Turn(role=role, content=content))
    return out


def summarize(turns: list[Turn]) -> str:
    """Very small heuristic summary (placeholder)."""
    if not turns:
        return ""
    head = turns[-1].content[:240]
    return head.strip()


def extract_facts(summary: str) -> list[dict[str, Any]]:
    """Extract coarse facts (placeholder, deterministic)."""
    if not summary:
        return []
    return [{"type": "note", "text": summary}]


def link_entities(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create trivial links for downstream upserts (placeholder)."""
    links: list[dict[str, Any]] = []
    for f in facts:
        links.append({"from": "summary", "to": f.get("type", "fact"), "rel": "describes"})
    return links


def upsert_vector(facts: list[dict[str, Any]]) -> int:
    """Stub: return count of vector upserts."""
    return len(facts)


def upsert_fts(facts: list[dict[str, Any]]) -> int:
    """Stub: return count of FTS upserts."""
    return len(facts)


def run(raw_turns: Iterable[dict[str, Any]]) -> ConsolidationResult:
    """Execute the consolidation graph if enabled; otherwise no-op safely."""
    settings = get_settings()
    if not settings.use_memory_graph:
        return ConsolidationResult(summary="", facts=[], links=[], upserts={"vector": 0, "fts": 0})

    turns = collect_turns(raw_turns)
    summary = summarize(turns)
    facts = extract_facts(summary)
    links = link_entities(facts)
    up_vector = upsert_vector(facts)
    up_fts = upsert_fts(facts)
    return ConsolidationResult(summary=summary, facts=facts, links=links, upserts={"vector": up_vector, "fts": up_fts})
