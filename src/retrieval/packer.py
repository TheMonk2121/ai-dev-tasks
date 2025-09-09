"""
Context Packing Utility

Packs selected candidate documents into a single context string with
per-document caps and overall character budget.
"""

from __future__ import annotations


DocId = str
Score = float
Document = str


def _first_two_sentences(s: str, max_chars: int = 600) -> str:
    import re

    parts = re.split(r"(?<=[.!?])\s+", s.strip())
    snippet = " ".join(parts[:2]) if parts else s.strip()
    return snippet[:max_chars]


def pack_candidates(
    candidates: list[tuple[DocId, Score]],
    documents: dict[DocId, Document],
    *,
    max_chars: int = 1600,
    max_per_document: int = 2,
) -> str:
    """Pack candidate snippets with headers.

    Each block:
        [doc:<doc_id>] <first two sentences>
    """
    blocks: list[str] = []
    used = 0
    per_doc_count: dict[str, int] = {}

    for doc_id, _score in candidates:
        cnt = per_doc_count.get(doc_id, 0)
        if cnt >= max_per_document:
            continue

        text = documents.get(doc_id, "").strip()
        if not text:
            continue

        header = f"[doc:{doc_id}]"
        body = _first_two_sentences(text)
        block = f"{header} {body}"
        n = len(block)

        if used + n > max_chars:
            break

        blocks.append(block)
        used += n + 2
        per_doc_count[doc_id] = cnt + 1

    return "\n\n".join(blocks)
