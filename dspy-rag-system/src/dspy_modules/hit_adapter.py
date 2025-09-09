#!/usr/bin/env python3
"""
Hit adapter for guaranteed score, filename, and document_id.
Fixes the "Score=None / Title=None → reranker/packer drop everything" cascade.
"""

import logging
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class Hit:
    """Guaranteed hit with required fields."""

    text: str
    score: float
    metadata: dict[str, Any]


def _row_to_hit(row: dict[str, Any]) -> Hit:
    """Convert database row to Hit with guaranteed fields."""
    # Required fields (fail early if SQL aliasing broke)
    doc_id = row.get("document_id") or row.get("id")
    if doc_id is None:
        raise ValueError(f"hybrid query missing document_id: {row}")

    filename = row.get("filename") or f"doc:{doc_id}"
    text = (row.get("content") or "").strip()

    # Score must be a float; default to 0.0 (but log it)
    raw_score = row.get("score", 0.0)
    try:
        score = float(raw_score)
    except Exception:
        log.warning(f"Invalid score {raw_score} for doc {doc_id}, using 0.0")
        score = 0.0

    return Hit(
        text=text,
        score=score,
        metadata={
            "document_id": doc_id,
            "filename": filename,
            "file_path": row.get("file_path"),
            "src": row.get("src"),  # 'vec' | 'bm25'
        },
    )


def adapt_rows(rows: list[dict[str, Any]]) -> list[Hit]:
    """Adapt database rows to Hits with guaranteed fields."""
    hits = []
    for r in rows:
        if not r.get("content"):
            continue  # Skip empty content
        try:
            hit = _row_to_hit(r)
            hits.append(hit)
        except Exception as e:
            log.warning(f"Failed to adapt row: {e}")
            continue

    # Keep score ordering from SQL
    return hits


def pack_hits(hits: list[Hit], max_chars: int = 8000, max_per_document: int = 2) -> str:
    """Pack hits into context with guaranteed headers and per-document cap."""
    import re

    def _first_two_sentences(s: str, max_chars: int = 600) -> str:
        # crude but robust sentence split
        parts = re.split(r"(?<=[.!?])\s+", s.strip())
        snippet = " ".join(parts[:2]) if parts else s.strip()
        return snippet[:max_chars]

    blocks = []
    used = 0
    per_doc_count: dict[str, int] = {}

    for h in hits:
        doc_id = str(h.metadata.get("document_id"))
        cnt = per_doc_count.get(doc_id, 0)
        if cnt >= max_per_document:
            continue
        fname = h.metadata.get("filename") or f"doc:{h.metadata.get('document_id')}"
        header = f"[{fname}]"
        body = _first_two_sentences(h.text)
        block = f"{header} {body}"
        n = len(block)

        if used + n > max_chars:
            break

        blocks.append(block)
        used += n + 2
        per_doc_count[doc_id] = cnt + 1

    return "\n\n".join(blocks)


def _rescale(hits: list[Hit]) -> list[Hit]:
    """Simple per-source min-max normalization to balance vector vs BM25 scores."""
    # Group by source
    by_src = {}
    for h in hits:
        src = h.metadata.get("src", "?")
        by_src.setdefault(src, []).append(h)

    # Rescale each source independently
    for src, group in by_src.items():
        if len(group) < 2:
            continue  # Need at least 2 values to rescale

        vals = [x.score for x in group]
        lo, hi = min(vals), max(vals)
        rng = (hi - lo) or 1.0

        for x in group:
            x.score = (x.score - lo) / rng

    return hits


def smoke_test(retriever) -> bool:
    """Quick sanity test to verify adapter invariants."""
    try:
        q = "What is DSPy according to 400_07_ai-frameworks-dspy.md?"
        result = retriever.forward("search", query=q, limit=12)

        if result["status"] != "success":
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
            return False

        rows = result["results"]
        hits = adapt_rows(rows)

        assert hits, "No hits returned"
        assert all(isinstance(h.score, float) for h in hits), "Non-float score"
        assert all(h.metadata.get("filename") for h in hits), "Missing filename"
        assert all(h.text for h in hits), "Empty text"

        print("✅ Adapter smoke test passed")
        print("Top 3 hits:")
        for h in hits[:3]:
            print(f"  {round(h.score, 4)} {h.metadata['filename']}")
            print(f"  {h.text[:150]}...\n")

        ctx = pack_hits(hits[:6])
        print(f"Packed context preview:\n{ctx[:500]}...\n")

        return True

    except Exception as e:
        print(f"❌ Adapter smoke test failed: {e}")
        return False
