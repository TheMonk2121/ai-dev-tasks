#!/usr/bin/env python3
"""
Memory Rehydrator
-----------------
Builds a role-aware, task-scoped hydration bundle from Postgres using:
- Pinned anchors (stable + role-based) from document_chunks.metadata
- Hybrid retrieval via your HybridVectorStore public API
- Span-grounded snippets with a strict token budget

Design constraints (per consensus):
- Reuse existing infra (DB resilience + vector store + fusion knobs)
- Configurable defaults via env; log what was used for traceability
- No migrations; JSONB metadata drives pinning

Docs this implements (source of truth):
- Stable anchors & reading order: 100_memory/100_cursor-memory-context.md
- Critical Path + role mapping: 400_guides/400_system-overview.md, 000_core/000_backlog.md
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from psycopg2.extras import RealDictCursor

from ..dspy_modules.vector_store import HybridVectorStore  # public Module interface

# Repo-local imports: reuse your infra (no ad-hoc pooling)
from .database_resilience import get_database_manager

# ---------- Policy knobs (env-configurable) ----------

DEFAULT_FUSION_METHOD = os.getenv("REHYDRATE_FUSION_METHOD", "").strip() or None  # e.g., "zscore" | "rrf"
DEFAULT_W_DENSE = float(os.getenv("REHYDRATE_W_DENSE", "0.7"))
DEFAULT_W_SPARSE = float(os.getenv("REHYDRATE_W_SPARSE", "0.3"))

DEFAULT_LIMIT = int(os.getenv("REHYDRATE_TOPK", "8"))
DEFAULT_BUDGET = int(os.getenv("REHYDRATE_TOKEN_BUDGET", "1200"))

# Vector store DSN (HybridVectorStore will use it internally as designed)
DEFAULT_PG_DSN = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

# Stable anchors from memory scaffold (reading order guaranteed)
STABLE_ANCHORS = ("tldr", "quick-start", "quick-links", "commands")

# Role → files map (kept small/deterministic; can be extended)
ROLE_FILES = {
    "planner": (
        "400_guides/400_system-overview.md",
        "000_core/000_backlog.md",
    ),
    "implementer": ("100_memory/104_dspy-development-context.md",),
    "researcher": (
        # extend later if needed (e.g., 500_research/*)
    ),
}


# ---------- Utility helpers ----------


def token_estimate(text: str) -> int:
    # Approx ~4 chars/token; safe budgeter for mix of prose/code.
    return max(1, len(text) // 4)


def trim(text: str, limit: int = 220) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def cite(document_id: str, start: int, end: int) -> str:
    # Span-grounded citation string; aligns with your prior convention.
    return f"Doc {document_id}, chars {start}-{end}"


@dataclass
class Section:
    kind: str  # "pin" | "anchor" | "span"
    title: str  # e.g., anchor_key or label
    content: str
    citation: str
    document_id: str
    chunk_index: int
    start_offset: int
    end_offset: int


@dataclass
class Bundle:
    text: str
    sections: List[Section]
    meta: Dict[str, Any]


# ---------- Data access (pinned anchors) ----------


def fetch_pins(role: str, *, db_dsn: str = DEFAULT_PG_DSN, cap: int = 30) -> List[Dict[str, Any]]:
    """
    Fetches stable anchors (always) + role-based pins (by file) from JSONB metadata.
    Prioritizes 'anchor_priority' ascending, then stable order.
    """
    db = get_database_manager()
    pins: List[Dict[str, Any]] = []

    role_files = ROLE_FILES.get(role.lower(), ())

    # Query selects: document_id, chunk_index, content, offsets, anchor_key, prio
    sql = """
        SELECT d.file_path,
               dc.document_id,
               dc.chunk_index,
               dc.content,
               dc.start_offset,
               dc.end_offset,
               dc.metadata->>'anchor_key' AS anchor_key,
               COALESCE((dc.metadata->>'anchor_priority')::int, 999) AS prio
        FROM document_chunks dc
        JOIN documents d ON d.document_id = dc.document_id
        WHERE dc.metadata ? 'anchor_key'
          AND (
               (dc.metadata->>'anchor_key') = ANY (%s)             -- stable anchors
               OR (d.file_path = ANY (%s))                         -- role → files
               OR ((dc.metadata ? 'role_pins') AND                 -- exact JSONB membership
                   (dc.metadata->'role_pins') @> %s::jsonb)
          )
        ORDER BY
          CASE dc.metadata->>'anchor_key'
            WHEN 'tldr' THEN 0
            WHEN 'quick-start' THEN 1
            WHEN 'quick-links' THEN 2
            WHEN 'commands' THEN 3
            ELSE COALESCE((dc.metadata->>'anchor_priority')::int, 999)
          END,
          d.file_path,
          dc.chunk_index
        LIMIT %s
    """

    with db.get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (list(STABLE_ANCHORS), list(role_files), json.dumps([role.lower()]), cap))
        rows = cur.fetchall()
        pins.extend(rows)

    return pins


def anchor_key_for(conn, document_id: str, chunk_index: int) -> Optional[str]:
    """
    Check whether a retrieved chunk is an anchor-ish chunk (has metadata.anchor_key).
    Kept simple since retrieval topK is small.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT metadata->>'anchor_key'
            FROM document_chunks
            WHERE document_id = %s AND chunk_index = %s
            """,
            (document_id, chunk_index),
        )
        row = cur.fetchone()
        if row is None:
            return None
        try:
            return row[0]
        except (KeyError, IndexError, TypeError):
            return None


# ---------- Assembly policy ----------


def assemble_bundle(
    pins: List[Dict[str, Any]],
    retrieval: List[Dict[str, Any]],
    *,
    token_budget: int,
    db_dsn: str = DEFAULT_PG_DSN,
) -> Bundle:
    """
    Pins first (stable+role), then anchor-like retrievals, then general spans.
    Enforces token budget; returns both rendered text and machine-readable sections.
    """
    db = get_database_manager()

    used = 0
    out_sections: List[Section] = []
    seen: set[Tuple[str, int]] = set()

    def try_add(kind: str, title: str, row: Dict[str, Any]) -> bool:
        nonlocal used
        key = (str(row["document_id"]), int(row["chunk_index"]))
        if key in seen:
            return False
        content = trim(row["content"])
        cost = token_estimate(content)
        if used + cost > token_budget:
            return False
        out_sections.append(
            Section(
                kind=kind,
                title=title,
                content=content,
                citation=cite(
                    str(row["document_id"]), int(row.get("start_offset", 0)), int(row.get("end_offset", len(content)))
                ),
                document_id=str(row["document_id"]),
                chunk_index=int(row["chunk_index"]),
                start_offset=int(row.get("start_offset", 0)),
                end_offset=int(row.get("end_offset", len(content))),
            )
        )
        used += cost
        seen.add(key)
        return True

    # 1) PINS (stable anchors in documented reading order, then role pins)
    #    We display stable anchors with friendly titles matching memory scaffold anchors.
    for row in pins:
        title = (row.get("anchor_key") or "pin").upper()
        try_add("pin", title, row)

    # 2) RETRIEVAL (anchor-like first)
    with db.get_connection() as conn:
        anchorish: List[Dict[str, Any]] = []
        spans: List[Dict[str, Any]] = []

        for r in retrieval:
            # normalize expected fields across implementations
            row = {
                "document_id": r.get("document_id") or r.get("doc_id") or r.get("id"),
                "chunk_index": r.get("chunk_index") or r.get("idx") or 0,
                "content": r.get("content") or r.get("text") or "",
                "start_offset": r.get("span_start") or r.get("start_offset") or 0,
                "end_offset": r.get("span_end") or r.get("end_offset") or len(r.get("content") or ""),
            }
            if not row["document_id"]:
                continue

            ak = anchor_key_for(conn, row["document_id"], int(row["chunk_index"]))
            if ak:
                row["anchor_key"] = ak
                anchorish.append(row)
            else:
                spans.append(row)

    for row in anchorish:
        title = (row.get("anchor_key") or "ANCHOR").upper()
        if not try_add("anchor", title, row):
            break

    for row in spans:
        if not try_add("span", "SPAN", row):
            break

    # 3) Render
    lines: List[str] = []
    for s in out_sections:
        # Lightweight headings; pins get their anchor_key as a section header
        if s.kind == "pin":
            lines.append(f"[{s.title}]")
        elif s.kind == "anchor":
            lines.append(f"[FOCUSED CONTEXT — {s.title}]")
        else:
            lines.append("[SPAN SOURCE]")

        lines.append(s.content.strip())
        lines.append(f"— {s.citation}")
        lines.append("")  # blank line

    text = "\n".join(lines).strip()

    meta = {
        "sections": len(out_sections),
        "tokens_est": used,
        "stable_anchors": STABLE_ANCHORS,
        "role_files": ROLE_FILES,
    }

    return Bundle(text=text, sections=out_sections, meta=meta)


# ---------- Public API ----------


def build_hydration_bundle(
    role: str,
    task: str,
    *,
    token_budget: int = DEFAULT_BUDGET,
    limit: int = DEFAULT_LIMIT,
    fusion_method: Optional[str] = DEFAULT_FUSION_METHOD,
    w_dense: Optional[float] = DEFAULT_W_DENSE,
    w_sparse: Optional[float] = DEFAULT_W_SPARSE,
    db_dsn: str = DEFAULT_PG_DSN,
) -> Bundle:
    """
    Entry point used by agents.

    - Pinned layer: stable anchors (TL;DR → quick-start → quick-links → commands) +
      role-based pins (planner/system-overview & backlog; implementer/DSPy context).
    - Task-scoped layer: Hybrid retrieval via HybridVectorStore public interface.
    - Budgeting: 1,200 tokens default, pins first, then anchor-like, then spans.

    Defaults and fusion knobs are passed through; the vector store decides how to use them.
    """
    t0 = time.time()

    # 1) Fetch pins
    pins = fetch_pins(role=role, db_dsn=db_dsn)

    # 2) Hybrid retrieval via your module interface (no private methods)
    vs = HybridVectorStore(db_connection_string=db_dsn)
    search_kwargs = {
        "query": task,
        "limit": limit,
    }

    vs_resp = vs("search", **search_kwargs)
    retrieval = vs_resp.get("results", []) if isinstance(vs_resp, dict) else []

    # 3) Assemble bundle under budget
    bundle = assemble_bundle(pins, retrieval, token_budget=token_budget, db_dsn=db_dsn)

    # 4) Metadata logging for reproducibility
    bundle.meta.update(
        {
            "role": role,
            "task": task,
            "limit": limit,
            "fusion_method_used": fusion_method,
            "w_dense_used": w_dense,
            "w_sparse_used": w_sparse,
            "dense_count": vs_resp.get("dense_count") if isinstance(vs_resp, dict) else None,
            "sparse_count": vs_resp.get("sparse_count") if isinstance(vs_resp, dict) else None,
            "merged_count": vs_resp.get("merged_count") if isinstance(vs_resp, dict) else None,
            "elapsed_s": round(time.time() - t0, 3),
        }
    )
    return bundle


# ---------- CLI for quick testing ----------


def _main():
    p = argparse.ArgumentParser(description="Build a role-aware hydration bundle from Postgres.")
    p.add_argument("--role", required=True, help="planner | implementer | researcher")
    p.add_argument("--task", required=True, help="Current task/title to focus retrieval")
    p.add_argument("--budget", type=int, default=DEFAULT_BUDGET, help="Token budget (default 1200)")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="TopK for retrieval (default 8)")
    p.add_argument("--fusion", dest="fusion_method", default=DEFAULT_FUSION_METHOD, help="zscore | rrf (optional)")
    p.add_argument("--w-dense", dest="w_dense", type=float, default=DEFAULT_W_DENSE, help="Dense weight (optional)")
    p.add_argument("--w-sparse", dest="w_sparse", type=float, default=DEFAULT_W_SPARSE, help="Sparse weight (optional)")
    p.add_argument("--json", action="store_true", help="Emit JSON (sections + meta) instead of formatted text")
    args = p.parse_args()

    bundle = build_hydration_bundle(
        role=args.role,
        task=args.task,
        token_budget=args.budget,
        limit=args.limit,
        fusion_method=args.fusion_method if args.fusion_method else None,
        w_dense=args.w_dense,
        w_sparse=args.w_sparse,
    )

    if args.json:
        payload = {
            "text": bundle.text,
            "sections": [asdict(s) for s in bundle.sections],
            "meta": bundle.meta,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(bundle.text)
        print("\n# meta")
        print(json.dumps(bundle.meta, indent=2))


if __name__ == "__main__":
    _main()
