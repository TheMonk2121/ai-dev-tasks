#!/usr/bin/env python3
"""
Memory Rehydrator - Lean Hybrid with Kill-Switches
--------------------------------------------------
Semantic-first memory rehydration with configurable complexity.

Design: Pins as guardrails (tiny, always present) + semantic evidence (bulk of context)
with kill-switches for simplicity when needed.

Defaults (robust):
- RRF fusion (vector + BM25)
- File round-robin + overlap deduplication
- Auto query expansion on low confidence
- Stability = 0.6

Kill-switches (simple):
- --no-rrf: Pure vector similarity only
- --dedupe file: File-level deduplication only
- --expand-query off: No query expansion
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor

# Repo-local imports: reuse your infra (no ad-hoc pooling)
from .database_resilience import get_database_manager
from .entity_overlay import (
    calculate_adaptive_k_related,
    extract_entities_from_query,
    populate_related_entities,
)

# Import HybridVectorStore for potential future integration
# Note: This module currently uses direct database queries for specialized
# memory rehydration logic, but HybridVectorStore is available for DSPy integration
try:
    from ..dspy_modules.vector_store import HybridVectorStore
except ImportError:
    # Fallback for when running from outside src directory
    HybridVectorStore = None

# ---- Kill-switch defaults (can be overridden by CLI or env) ----
DEFAULT_STABILITY = float(os.getenv("REHYDRATE_STABILITY", "0.6"))
USE_RRF = os.getenv("REHYDRATE_USE_RRF", "1") != "0"
DEDUPE_MODE = os.getenv("REHYDRATE_DEDUPE", "file+overlap")  # "file" | "file+overlap"
EXPAND_QUERY = os.getenv("REHYDRATE_EXPAND_QUERY", "auto")  # "off" | "auto"

PINS_CAP_TOKENS = 200
K_VEC = 32
K_LEX = 32
RRF_K0 = 60
OVERLAP_THRESH = 0.60
PER_FILE_ROUND_ROBIN = 2
LOW_CONF_SIM = 0.30  # top-1 vector similarity threshold

# Vector store DSN (used for direct database connections and HybridVectorStore)
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


# ---------- Core pipeline functions ----------


def rrf_fuse(vec: List[Dict[str, Any]], lex: List[Dict[str, Any]], k0: int = RRF_K0) -> List[Dict[str, Any]]:
    """Reciprocal Rank Fusion with deterministic tie-breaking."""

    def rank_map(items, key):
        # rank starts at 1; stable by (score desc, file, path)
        sorted_items = sorted(items, key=lambda d: (-float(d.get(key, 0.0)), d.get("file", ""), d.get("path", "")))
        return {d["id"]: (i + 1) for i, d in enumerate(sorted_items)}

    r_vec = rank_map(vec, "sim")
    r_lex = rank_map(lex, "bm25")

    id_index: Dict[str, Dict[str, Any]] = {}
    for d in vec:
        id_index[d["id"]] = {**d, "rrf": 0.0}
    for d in lex:
        id_index.setdefault(d["id"], {**d, "rrf": 0.0})

    for _id, d in id_index.items():
        if _id in r_vec:
            d["rrf"] += 1.0 / (k0 + r_vec[_id])
        if _id in r_lex:
            d["rrf"] += 1.0 / (k0 + r_lex[_id])
        # canonical score field for downstream sorting:
        d["score"] = d["rrf"]

    fused = list(id_index.values())
    fused.sort(key=lambda d: (-d["score"], d.get("file", ""), d.get("path", "")))
    return fused


def round_robin_by_file(items: List[Dict[str, Any]], per_file: int = PER_FILE_ROUND_ROBIN) -> List[Dict[str, Any]]:
    """Cheap diversity: interleave by file, cap per-file on first pass."""
    from collections import defaultdict, deque

    buckets = defaultdict(list)
    for d in items:
        buckets[d.get("file", "")].append(d)

    # buckets already sorted by 'score' due to prior sort
    queues = {f: deque(lst[:]) for f, lst in buckets.items()}
    taken = []
    per_file_count = {f: 0 for f in queues.keys()}

    # pass 1: up to per_file each
    progressed = True
    while progressed:
        progressed = False
        for f, q in queues.items():
            if q and per_file_count[f] < per_file:
                taken.append(q.popleft())
                per_file_count[f] += 1
                progressed = True

    # pass 2: if budget remains later, caller will truncate by tokens;
    # we keep remaining order stable:
    leftovers = []
    for f, q in queues.items():
        leftovers.extend(list(q))
    return taken + leftovers


def _shingles(text: str, n: int = 5) -> set:
    toks = re.findall(r"\w+", text.lower())
    return set(tuple(toks[i : i + n]) for i in range(0, max(0, len(toks) - n + 1)))


def drop_near_duplicates(items: List[Dict[str, Any]], overlap_thresh: float = OVERLAP_THRESH) -> List[Dict[str, Any]]:
    """O(k^2) worst-case with small k; adequate for k<=64."""
    kept = []
    shingle_cache = {}
    for d in items:
        t = d.get("text", "")
        if not t:
            kept.append(d)
            continue
        s = shingle_cache.get(d["id"]) or _shingles(t)
        dup = False
        for prev in kept:
            pt = prev.get("text", "")
            ps = shingle_cache.get(prev["id"]) or _shingles(pt)
            # Jaccard similarity:
            inter = len(s & ps)
            union = max(1, len(s | ps))
            j = inter / union
            if j >= overlap_thresh:
                dup = True
                break
        if not dup:
            kept.append(d)
        shingle_cache[d["id"]] = s
    return kept


def overlaps_scope(d: Dict[str, Any], query: str) -> bool:
    """Cheap scope heuristic: file or anchor_key token appears in query."""
    q = query.lower()
    f = (d.get("file") or "").lower()
    ak = (d.get("anchor_key") or "").lower()
    return bool((f and f.split("/")[-1] in q) or (ak and ak in q))


def augment_query(q: str, terms: List[str]) -> str:
    """Include terms once; keep lexical variety."""
    if not terms:
        return q
    extra = " ".join(sorted(set(terms)))
    return f"{q} {extra}"


# ---------- Data access (pinned anchors) ----------


def fetch_pins(role: str, *, db_dsn: str = DEFAULT_PG_DSN, cap: int = 30) -> List[Dict[str, Any]]:
    """
    Fetches stable anchors (always) + role-based pins (by file) from JSONB metadata.
    Prioritizes 'anchor_priority' ascending, then stable order.
    """
    db = get_database_manager()
    pins: List[Dict[str, Any]] = []

    role_files = ROLE_FILES.get(role.lower(), ())

    # Query selects: document_id, chunk_index, content, line spans, anchor_key, prio
    sql = """
        SELECT d.file_path,
               dc.document_id,
               dc.chunk_index,
               dc.content,
               dc.line_start,
               dc.line_end,
               dc.anchor_key,
               COALESCE((dc.metadata->>'anchor_priority')::int, 999) AS prio
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE dc.is_anchor = TRUE
          AND (
               (dc.anchor_key = ANY (%s))                          -- stable anchors
               OR (d.file_path = ANY (%s))                         -- role → files
               OR ((dc.metadata ? 'role_pins') AND                 -- exact JSONB membership
                   (dc.metadata->'role_pins') @> %s::jsonb)
          )
        ORDER BY
          CASE dc.anchor_key
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


# ---------- Vector store interface functions ----------


def vector_search(query: str, k: int, db_dsn: str = DEFAULT_PG_DSN) -> List[Dict[str, Any]]:
    """
    Vector search via HybridVectorStore.
    Returns: List[{
        "id": str,
        "file": str,          # e.g., "src/dspy_modules/vector_store.py"
        "path": str,          # e.g., "src/dspy_modules/vector_store.py#L45-92"
        "text": str,          # raw chunk text
        "sim": float,         # cosine or IP normalized 0..1
        "is_anchor": bool,    # True if chunk has anchor metadata
        "anchor_key": str | None
    }]
    """
    try:
        # Function-level import to avoid circular dependency
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from dspy_modules.vector_store import HybridVectorStore

        vs = HybridVectorStore(db_connection_string=db_dsn)
        results = vs("search_vector", query=query, limit=k)
        return _normalize_to_canonical(results.get("results", []), "vector")
    except Exception as e:
        print(f"Vector search error: {e}")
        return []


def bm25_search(query: str, k: int, db_dsn: str = DEFAULT_PG_DSN) -> List[Dict[str, Any]]:
    """
    BM25 search via HybridVectorStore.
    Returns: List[{
        "id": str,
        "file": str,          # e.g., "src/dspy_modules/vector_store.py"
        "path": str,          # e.g., "src/dspy_modules/vector_store.py#L45-92"
        "text": str,          # raw chunk text
        "bm25": float,        # ts_rank_cd score
        "is_anchor": bool,    # True if chunk has anchor metadata
        "anchor_key": str | None
    }]
    """
    try:
        # Function-level import to avoid circular dependency
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from dspy_modules.vector_store import HybridVectorStore

        vs = HybridVectorStore(db_connection_string=db_dsn)
        results = vs("search_bm25", query=query, limit=k)
        return _normalize_to_canonical(results.get("results", []), "bm25")
    except Exception as e:
        print(f"BM25 search error: {e}")
        return []


def _normalize_to_canonical(results, search_type="vector"):
    """
    Canonicalizer with soft-fail by default and strict mode toggle.
    Enforces real PK id from store and deterministic path generation.
    """
    import os

    STRICT_IDS = os.getenv("REHYDRATE_STRICT_IDS", "0") == "1"

    canon = []
    for r in results or []:
        # Enforce real PK id from store
        rid = r.get("id")
        if rid is None:
            msg = f"[rehydrate] row missing id; skipping (file_path={r.get('file_path','unknown')})"
            if STRICT_IDS:
                raise ValueError(msg)
            else:
                print(msg)
                continue

        meta = r.get("metadata") or {}
        file_path = r.get("file_path") or meta.get("file_path") or "unknown"

        # Path: spans -> chunk -> file (simple & deterministic)
        ls, le = r.get("line_start"), r.get("line_end")
        if isinstance(ls, int) and isinstance(le, int) and le >= ls and ls > 0:
            path = f"{file_path}#L{ls}-{le}"
        elif r.get("chunk_index") is not None:
            path = f"{file_path}#chunk{r['chunk_index']}"
        else:
            path = file_path

        if search_type == "vector":
            sim = r.get("similarity", 0.0)
            if r.get("distance") is not None:
                sim = max(0.0, min(1.0, 1.0 - float(r["distance"])))
            bm25 = 0.0
        else:
            sim, bm25 = 0.0, float(r.get("bm25", 0.0))

        is_anchor = bool(r.get("is_anchor")) or bool(meta.get("is_anchor")) or bool(meta.get("anchor_key"))
        anchor_key = r.get("anchor_key") or meta.get("anchor_key")

        canon.append(
            {
                "id": str(rid),
                "file": file_path,
                "path": path,
                "text": r.get("content", ""),
                "sim": float(sim),
                "bm25": bm25,
                "is_anchor": is_anchor,
                "anchor_key": anchor_key,
            }
        )
    return canon


def mine_anchor_terms(query: str, top_n: int = 6) -> List[str]:
    """Mine discriminative terms from anchor documents for query expansion."""
    try:
        db = get_database_manager()

        # Get anchor documents and extract terms
        sql = """
            SELECT DISTINCT dc.content
            FROM document_chunks dc
            WHERE dc.metadata ? 'anchor_key'
            LIMIT 10
        """

        with db.get_connection() as conn, conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

            # Extract terms (simple heuristic)
            all_terms = set()
            for row in rows:
                content = row[0] if row else ""
                # Extract potential discriminative terms
                terms = re.findall(r"\b[A-Z][a-zA-Z0-9_]*\b", content)  # CamelCase/PascalCase
                terms.extend(re.findall(r"\b[a-z_][a-z0-9_]*\b", content))  # snake_case
                all_terms.update(terms)

            # Filter and return top terms
            filtered_terms = [t for t in all_terms if len(t) > 2 and t.lower() not in query.lower()]
            return filtered_terms[:top_n]
    except Exception as e:
        print(f"Anchor term mining error: {e}")
        return []


def load_guardrail_pins(cap_tokens: int = PINS_CAP_TOKENS) -> str:
    """Load pre-compressed guardrail pins."""
    # Pre-compressed micro-summaries
    pins = [
        "Style TL;DR: Follow project conventions, use descriptive names, add type hints, keep functions focused.",
        "Repo map (micro): 000_core/ (backlog, workflows), 100_memory/ (context), 400_guides/ (documentation), dspy-rag-system/ (implementation)",
        "Response conventions: Be concise, show code examples, reference specific files, explain trade-offs.",
    ]

    combined = " ".join(pins)
    if token_estimate(combined) > cap_tokens:
        # Truncate if needed
        combined = trim(combined, cap_tokens * 4)  # Rough char estimate

    return combined


def compress_chunk(d: Dict[str, Any]) -> Dict[str, Any]:
    """Answer-aware compression: path, why, gist."""
    text = d.get("text", "")
    path = d.get("path", "")

    # Simple compression heuristic
    lines = text.split("\n")
    if len(lines) > 3:
        gist = "\n".join(lines[:3]) + "..."
    else:
        gist = text

    # Truncate to ~160 tokens
    if token_estimate(gist) > 160:
        gist = trim(gist, 160 * 4)

    return {
        "path": path,
        "why": f"Relevant to query: {path.split('/')[-1] if path else 'unknown'}",
        "gist": gist,
        "tokens": token_estimate(gist),
    }


def token_len(obj) -> int:
    """Count tokens in object."""
    if isinstance(obj, str):
        return token_estimate(obj)
    elif isinstance(obj, list):
        return sum(token_len(item) for item in obj)
    elif isinstance(obj, dict):
        return sum(token_len(v) for v in obj.values())
    else:
        return token_estimate(str(obj))


def package_bundle(
    pins: str, query_expansion_terms: List[str], evidence: List[Dict[str, Any]], debug: Dict[str, Any]
) -> Bundle:
    """Package final bundle for Cursor."""
    # Format evidence for display
    evidence_text = []
    for e in evidence:
        evidence_text.append(f"[{e['path']}]")
        evidence_text.append(e["gist"])
        evidence_text.append(f"— {e['why']}")
        evidence_text.append("")

    # Combine all content
    bundle_text = f"[TLDR]\n{pins}\n\n"
    if query_expansion_terms:
        bundle_text += f"[QUERY EXPANSION]\nTerms: {', '.join(query_expansion_terms)}\n\n"
    bundle_text += "[EVIDENCE]\n" + "\n".join(evidence_text)

    # Create sections for metadata
    sections = []
    sections.append(
        Section(
            kind="pin",
            title="TLDR",
            content=pins,
            citation="guardrail_pins",
            document_id="pins",
            chunk_index=0,
            start_offset=0,
            end_offset=len(pins),
        )
    )

    for i, e in enumerate(evidence):
        sections.append(
            Section(
                kind="evidence",
                title=f"EVIDENCE_{i}",
                content=e["gist"],
                citation=e["path"],
                document_id=e.get("document_id", "unknown"),
                chunk_index=i,
                start_offset=0,
                end_offset=len(e["gist"]),
            )
        )

    return Bundle(text=bundle_text, sections=sections, meta=debug)


# ---------- Entity expansion integration ----------


def semantic_evidence_with_entity_expansion(
    query: str,
    base_chunks: List[Dict[str, Any]],
    use_entity_expansion: bool = True,
    stability_threshold: float = 0.7,
    db_dsn: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Enhance semantic evidence with entity expansion.

    Args:
        query: Input query
        base_chunks: Base chunks from semantic search
        use_entity_expansion: Whether to enable entity expansion
        stability_threshold: Minimum similarity threshold for entity chunks
        db_dsn: Database connection string

    Returns:
        Tuple of (expanded_chunks, expansion_metrics)
    """
    if not use_entity_expansion:
        return base_chunks, {
            "expansion_used": False,
            "entities_found": 0,
            "expansion_latency_ms": 0.0,
            "chunks_added": 0,
        }

    # Extract entities from query
    entities = extract_entities_from_query(query)

    if not entities:
        return base_chunks, {
            "expansion_used": True,
            "entities_found": 0,
            "expansion_latency_ms": 0.0,
            "chunks_added": 0,
        }

    # Calculate adaptive k_related based on entity count
    k_related = calculate_adaptive_k_related(base_k=2, entity_count=len(entities))

    # Populate with entity-related chunks
    expanded_chunks = populate_related_entities(
        base_chunks=base_chunks,
        entities=entities,
        k_related=k_related,
        stability_threshold=stability_threshold,
        db_dsn=db_dsn,
    )

    # Calculate metrics
    chunks_added = len(expanded_chunks) - len(base_chunks)

    # Get expansion latency from first entity-related chunk
    expansion_latency_ms = 0.0
    for chunk in expanded_chunks:
        if chunk.get("entity_related"):
            expansion_latency_ms = chunk.get("expansion_metadata", {}).get("expansion_latency_ms", 0.0)
            break

    expansion_metrics = {
        "expansion_used": True,
        "entities_found": len(entities),
        "entity_types": [entity.entity_type for entity in entities],
        "k_related": k_related,
        "expansion_latency_ms": expansion_latency_ms,
        "chunks_added": chunks_added,
        "stability_threshold": stability_threshold,
    }

    return expanded_chunks, expansion_metrics


# ---------- Main rehydration function ----------


def rehydrate(
    query: str,
    stability: float = DEFAULT_STABILITY,
    max_tokens: int = 6000,
    use_rrf: bool = USE_RRF,
    dedupe: str = DEDUPE_MODE,
    expand_query: str = EXPAND_QUERY,
    use_entity_expansion: bool = True,
    role: str = "planner",
    db_dsn: str = DEFAULT_PG_DSN,
) -> Bundle:

    # 0) Pins (always tiny, pre-compressed)
    pins = load_guardrail_pins(PINS_CAP_TOKENS)

    # 1) Initial vector probe for confidence
    vec_probe = vector_search(query, k=K_VEC, db_dsn=db_dsn)
    sim_top = max((d.get("sim", 0.0) for d in vec_probe), default=0.0)

    # 2) Optional auto query expansion on low confidence
    if expand_query == "auto" and sim_top < LOW_CONF_SIM:
        anchor_terms = mine_anchor_terms(query, top_n=6)
        expanded_q = augment_query(query, anchor_terms)
    else:
        anchor_terms = []
        expanded_q = query

    # 3) Full searches with canonicalization
    vec = vector_search(expanded_q, k=K_VEC, db_dsn=db_dsn)
    lex = bm25_search(expanded_q, k=K_LEX, db_dsn=db_dsn) if use_rrf else []

    # Canonicalize results to consistent format
    vec_canon = _normalize_to_canonical(vec, search_type="vector")
    lex_canon = _normalize_to_canonical(lex, search_type="bm25") if lex else []

    # 4) Fusion (RRF or pure vector)
    if use_rrf and lex_canon:
        fused = rrf_fuse(vec_canon, lex_canon, k0=RRF_K0)
    else:
        # Pure vector path with canonical 'score' field
        fused = sorted(vec_canon, key=lambda d: (-d.get("sim", 0.0), d.get("file", ""), d.get("path", "")))
        for d in fused:
            d["score"] = d.get("sim", 0.0)

    # 5) Low‑confidence anchor uplift (tiny, deterministic epsilon)
    if sim_top < LOW_CONF_SIM and expand_query != "off":
        eps = 0.02 + 0.05 * max(0.0, min(1.0, stability))
        for d in fused:
            if d.get("is_anchor") and overlaps_scope(d, query):
                d["score"] += eps
        fused.sort(key=lambda d: (-d["score"], d.get("file", ""), d.get("path", "")))

    # 6) Entity expansion (if enabled)
    if use_entity_expansion:
        ranked, expansion_metrics = semantic_evidence_with_entity_expansion(
            query=query, base_chunks=fused, use_entity_expansion=True, stability_threshold=stability, db_dsn=db_dsn
        )
    else:
        ranked = fused
        expansion_metrics = {
            "expansion_used": False,
            "entities_found": 0,
            "expansion_latency_ms": 0.0,
            "chunks_added": 0,
        }

    # 7) Cheap diversity / dedupe
    if dedupe.startswith("file"):
        ranked = round_robin_by_file(ranked, per_file=PER_FILE_ROUND_ROBIN)
    if dedupe.endswith("overlap"):
        ranked = drop_near_duplicates(ranked, overlap_thresh=OVERLAP_THRESH)

    # 7) Compression & budgeting
    budget_for_evidence = max(0, max_tokens - token_len(pins))
    evidence = []
    used = 0
    for d in ranked:
        comp = compress_chunk(d)  # => {path, why, gist, tokens:int(optional)}
        c_tokens = comp.get("tokens", token_len(comp))
        if used + c_tokens > budget_for_evidence:
            break
        evidence.append(comp)
        used += c_tokens

    # 8) Package
    bundle = package_bundle(
        pins=pins,
        query_expansion_terms=anchor_terms,
        evidence=evidence,
        debug={
            "stability": stability,
            "sim_top": sim_top,
            "use_rrf": bool(use_rrf),
            "dedupe": dedupe,
            "expand_query": expand_query,
            "use_entity_expansion": use_entity_expansion,
            "k_vec": K_VEC,
            "k_lex": K_LEX if use_rrf else 0,
            "rrf_k0": RRF_K0,
            "overlap_thresh": OVERLAP_THRESH,
            "per_file": PER_FILE_ROUND_ROBIN,
            "pins_tokens": token_len(pins),
            "evidence_tokens": used,
            **expansion_metrics,  # Include entity expansion metrics
        },
    )
    return bundle


# ---------- Legacy compatibility function ----------


def build_hydration_bundle(
    role: str,
    task: str,
    *,
    token_budget: int = 1200,
    limit: int = 8,
    fusion_method: Optional[str] = None,
    w_dense: Optional[float] = None,
    w_sparse: Optional[float] = None,
    db_dsn: str = DEFAULT_PG_DSN,
) -> Bundle:
    """
    Legacy compatibility function for existing code.
    Maps to the new rehydrate function with appropriate defaults.
    """
    t0 = time.time()

    # Map legacy parameters to new ones
    use_rrf = fusion_method is not None or (w_dense is not None and w_sparse is not None)
    dedupe = "file+overlap"  # Default to robust mode
    expand_query = "auto"  # Default to auto expansion

    bundle = rehydrate(
        query=task,
        stability=DEFAULT_STABILITY,
        max_tokens=token_budget,
        use_rrf=use_rrf,
        dedupe=dedupe,
        expand_query=expand_query,
        role=role,
        db_dsn=db_dsn,
    )

    # Add legacy metadata
    bundle.meta.update(
        {
            "role": role,
            "task": task,
            "limit": limit,
            "fusion_method_used": fusion_method,
            "w_dense_used": w_dense,
            "w_sparse_used": w_sparse,
            "elapsed_s": round(time.time() - t0, 3),
        }
    )

    return bundle


# ---------- CLI for testing ----------


def _main():
    p = argparse.ArgumentParser(description="Build a role-aware hydration bundle from Postgres.")
    p.add_argument("--role", required=True, help="planner | implementer | researcher")
    p.add_argument("--task", required=True, help="Current task/title to focus retrieval")
    p.add_argument("--stability", type=float, default=DEFAULT_STABILITY, help="Stability knob (0.0-1.0)")
    p.add_argument("--no-rrf", action="store_true", help="Disable BM25+RRF fusion")
    p.add_argument("--dedupe", choices=["file", "file+overlap"], default=DEDUPE_MODE, help="Deduplication mode")
    p.add_argument("--expand-query", choices=["off", "auto"], default=EXPAND_QUERY, help="Query expansion mode")
    p.add_argument("--no-entity-expansion", action="store_true", help="Disable entity expansion")
    p.add_argument("--max-tokens", type=int, default=6000, help="Maximum tokens")
    p.add_argument("--json", action="store_true", help="Emit JSON (sections + meta) instead of formatted text")
    args = p.parse_args()

    bundle = rehydrate(
        query=args.task,
        stability=args.stability,
        max_tokens=args.max_tokens,
        use_rrf=(not args.no_rrf),
        dedupe=args.dedupe,
        expand_query=args.expand_query,
        use_entity_expansion=(not args.no_entity_expansion),
        role=args.role,
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
