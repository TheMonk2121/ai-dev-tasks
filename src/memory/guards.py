from __future__ import annotations
from collections.abc import Iterable
from typing import Any
from pydantic import ValidationError
from .models import Answer, Provenance, RetrievedChunk
import os
from typing import Any, Dict, List, Optional, Union
"""Boundary guards to enforce strict provenance on retrieval outputs.

These helpers convert raw retrieval rows (dicts/objects) into strict DTOs and
apply repository provenance policies. Use at the agent/tool boundary.
"""





REQUIRED_META_KEYS = ("ingest_run_id", "chunk_variant")


def _get_meta(row: dict[str, Any]) -> dict[str, Any]:
    return (row.get("metadata") or row.get("meta") or {}) if isinstance(row, dict) else {}


def _require_provenance(row: dict[str, Any], strict: bool = True) -> None:
    md = _get_meta(row)
    missing = [k for k in REQUIRED_META_KEYS if not md.get(k)]
    if missing and strict:
        raise ValueError(f"missing required provenance keys: {missing}")


def normalize_row(row_any: Any) -> dict[str, Any]:
    """Normalize diverse row shapes into a dict with expected keys."""
    if isinstance(row_any, dict):
        d = dict(row_any)
        d.setdefault("metadata", d.get("metadata") or d.get("meta") or {})
        return d
    # Fallback object adapter
    return {
        "chunk_id": getattr(row_any, "chunk_id", None),
        "text": getattr(row_any, "text", None) or getattr(row_any, "content", None) or "",
        "score": float(getattr(row_any, "score", 0.0)),
        "start_char": getattr(row_any, "start_char", None),
        "end_char": getattr(row_any, "end_char", None),
        "metadata": dict(getattr(row_any, "metadata", {}) or {}),
    }


def rows_to_dtos(
    rows: Iterable[Any], *, run_id: str, producer: str, version: str, strict: bool = True
) -> list[RetrievedChunk]:
    """Convert raw rows to strict RetrievedChunk DTOs, enforcing provenance.

    - Requires ingest_run_id and chunk_variant in metadata when strict=True
    - Fills producer/run/version and wraps as Provenance
    """
    out: list[RetrievedChunk] = []
    for r in rows or []:
        d = normalize_row(r)
        _require_provenance(d, strict=strict)
        md = _get_meta(d)
        prov = Provenance(
            run_id=run_id,
            ingest_run_id=str(md.get("ingest_run_id")),
            chunk_variant=str(md.get("chunk_variant")),
            source_uri=md.get("source_uri"),
            source_path=md.get("source_path"),
            document_id=str(md.get("document_id")) if md.get("document_id") is not None else None,
            tool=producer,
            version=version,
            confidence=float(md.get("confidence", 1.0)),
            meta={k: v for k, v in md.items() if k not in {"ingest_run_id", "chunk_variant"}},
        )
        try:
            out.append(
                RetrievedChunk(
                    chunk_id=str(d.get("chunk_id") or md.get("chunk_id") or ""),
                    text=str(d.get("text") or d.get("text_for_reader") or ""),
                    score=float(d.get("final_score") or d.get("rerank_score") or d.get("score") or 0.0),
                    start_char=d.get("start_char") or md.get("start_char"),
                    end_char=d.get("end_char") or md.get("end_char"),
                    provenance=prov,
                )
            )
        except ValidationError as ve:
            raise ValueError(f"row validation failed: {ve}")
    return out


def build_answer(
    text: str, citations: list[str], chunks: list[RetrievedChunk], timings_ms: dict[str, float] | None = None
) -> Answer:
    return Answer(text=text, citations=citations, retrieved_context=chunks, timings_ms=timings_ms)
