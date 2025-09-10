#!/usr/bin/env python3
"""
Hybrid search SQL wrapper with optional namespace/filename reserved slots.
Builds params in exact placeholder order and guards placeholder/arg count.
"""

from __future__ import annotations

import re
from typing import Any

import psycopg2.extras

try:
    from utils.database_resilience import get_database_manager
except ImportError:
    from ..utils.database_resilience import get_database_manager
try:
    from .wrapper_ns_promote import debug_print, extract_ns_tokens, promote_ns_reserved
except Exception:
    extract_ns_tokens = None
    promote_ns_reserved = None
    debug_print = None
try:
    from .wrapper_fusion_nudge import apply_fusion_nudge
except Exception:
    apply_fusion_nudge = None

# Namespace seed SQL (pull candidates by first path segment)
NS_SEED_SQL = """
SELECT
    d.id        AS document_id,
    d.filename  AS filename,
    d.file_path AS file_path,
    dc.content  AS content,
    ts_rank_cd(dc.content_tsv, plainto_tsquery('english', %s)) AS score,
    'ns'        AS src
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.id
WHERE split_part(d.file_path, '/', 1) = ANY(%s::text[])
ORDER BY score DESC
LIMIT %s;
"""


PS_PLACEHOLDER_RE = re.compile(r"(?<!%)%s")


def _count_placeholders(sql: str) -> int:
    return len(PS_PLACEHOLDER_RE.findall(sql))


def _mk_patterns(
    ns_token: str | None, filename_exact: str | None, filename_partial: str | None
) -> tuple[str | None, str | None, str | None]:
    ns_like = f"%/{ns_token.strip('/')}/%" if ns_token else None
    file_eq = filename_exact or None
    file_like = f"%{filename_partial}%" if filename_partial else None
    return ns_like, file_eq, file_like


def _infer_ns_from_query(query: str) -> list[str]:
    """Infer namespace from 3-digit prefix tokens in the query (e.g., 000_, 100_, 400_)."""
    q = (query or "").lower()
    inferred: list[str] = []
    for pref, ns in (("000", "000_core"), ("100", "100_memory"), ("400", "400_guides")):
        if f"{pref}_" in q:
            inferred.append(ns)
    # dedupe preserve order
    seen = set()
    out: list[str] = []
    for t in inferred:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def run_hybrid_search(
    query: str,
    q_emb,  # numpy array or list
    limit: int = 8,
    ns_token: str | None = None,
    filename_exact: str | None = None,
    filename_partial: str | None = None,
    ns_reserved: int = 2,
    pool_ns: int = 80,
    debug: bool = False,
) -> dict[str, Any]:
    qv = q_emb.tolist() if hasattr(q_emb, "tolist") else q_emb
    ns_like, file_eq, file_like = _mk_patterns(ns_token, filename_exact, filename_partial)
    use_ns_union = any([ns_like, file_eq, file_like])

    merged_sql = """
    WITH vec AS (
        SELECT d.id AS document_id, d.filename, d.file_path, dc.content,
               dc.embedding <=> %s::vector AS dist,
               1.0 / (1.0 + (dc.embedding <=> %s::vector)) AS vec_score
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE dc.embedding IS NOT NULL
        ORDER BY dc.embedding <=> %s::vector
        LIMIT 50
    ),
    bm AS (
        SELECT d.id AS document_id, d.filename, d.file_path, dc.content,
               ts_rank_cd(dc.content_tsv, websearch_to_tsquery('english', %s)) AS bm_score
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE dc.content_tsv @@ websearch_to_tsquery('english', %s)
        ORDER BY bm_score DESC
        LIMIT 50
    ),
    unioned AS (
        SELECT document_id, filename, file_path, content, vec_score AS base_score FROM vec
        UNION ALL
        SELECT document_id, filename, file_path, content, bm_score  AS base_score FROM bm
    ),
    scored AS (
        SELECT u.document_id, u.filename, u.file_path, u.content,
               (
                   CASE WHEN %s IS NOT NULL AND u.file_path ILIKE %s THEN 0.30 ELSE 0 END
                 + CASE WHEN %s IS NOT NULL AND u.filename = %s THEN 0.35 ELSE 0 END
                 + CASE WHEN %s IS NOT NULL AND u.filename ILIKE %s THEN 0.15 ELSE 0 END
               ) AS boost,
               COALESCE(u.base_score, 0) AS rrf_base
        FROM unioned u
    ),
    ranked AS (
        SELECT document_id, filename, file_path, content,
               (rrf_base + boost) AS score,
               ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY (rrf_base + boost) DESC) AS doc_rank
        FROM scored
    ),
    merged AS (
        SELECT document_id, filename, file_path, content,
               (score - 0.15 * GREATEST(doc_rank - 1, 0)) AS score
        FROM ranked
    )
    """

    tail_plain = """
    SELECT document_id, filename, file_path, content, score
    FROM merged
    ORDER BY score DESC
    LIMIT %s
    """

    tail_ns = """
    , unioned_ns AS (
        SELECT m.*,
               CASE WHEN (%s IS NOT NULL AND file_path ILIKE %s)
                      OR (%s IS NOT NULL AND filename = %s)
                      OR (%s IS NOT NULL AND filename ILIKE %s)
                    THEN 1 ELSE 0 END AS ns_flag
        FROM merged m
    ),
    ns_subset AS (
        SELECT * FROM unioned_ns WHERE ns_flag = 1
        ORDER BY score DESC
        LIMIT %s
    ),
    ns_count AS (SELECT COUNT(*) AS c FROM ns_subset),
    rest AS (
        SELECT * FROM unioned_ns
        WHERE document_id NOT IN (SELECT document_id FROM ns_subset)
        ORDER BY score DESC
        LIMIT GREATEST(%s - (SELECT c FROM ns_count), 0)
    )
    SELECT document_id, filename, file_path, content, score
    FROM (
        SELECT * FROM ns_subset
        UNION ALL
        SELECT * FROM rest
    ) final
    ORDER BY score DESC
    """

    sql = merged_sql + (tail_ns if use_ns_union else tail_plain)

    params: list[Any] = []
    # vec (3)
    params += [qv, qv, qv]
    # bm (2)
    params += [query, query]
    # boosts (6)
    params += [ns_like, ns_like, file_eq, file_eq, file_like, file_like]

    # Use a slightly larger internal pool to avoid starvation before promotion
    pool_limit = max(limit, 80)

    if use_ns_union:
        # ns gating (patterns + limit)
        params += [ns_like, ns_like, file_eq, file_eq, file_like, file_like, ns_reserved, pool_limit]
    else:
        params += [pool_limit]

    expected = _count_placeholders(sql)
    actual = len(params)
    if expected != actual:
        raise ValueError(f"Placeholder/param mismatch: expected {expected}, got {actual}")

    db = get_database_manager()
    with db.get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            try:
                cur.execute(sql, params)
            except Exception as e:
                # Fallback if content_tsv is missing: substitute computed tsvector
                if "content_tsv" in str(e).lower():
                    alt_sql = sql.replace(
                        "ts_rank_cd(dc.content_tsv, websearch_to_tsquery('english', %s))",
                        "ts_rank_cd(to_tsvector('english', dc.content), websearch_to_tsquery('english', %s))",
                    ).replace(
                        "dc.content_tsv @@ websearch_to_tsquery('english', %s)",
                        "to_tsvector('english', dc.content) @@ websearch_to_tsquery('english', %s)",
                    )
                    cur.execute(alt_sql, params)
                else:
                    raise
            rows = [dict(r) for r in cur.fetchall()]

            # Namespace seed fetch (independent query)
            ns_tokens: list[str] = []
            if extract_ns_tokens is not None:
                auto_tokens = list(extract_ns_tokens(query))
                if ns_token:
                    auto_tokens.append(ns_token)
                ns_tokens = [t for t in auto_tokens if t]
            # Also infer from simple prefix mapping
            for t in _infer_ns_from_query(query):
                if t not in ns_tokens:
                    ns_tokens.append(t)

            if ns_tokens and pool_ns > 0:
                ns_params = (query, ns_tokens, pool_ns)
                # pre-exec assert on raw SQL
                expected = NS_SEED_SQL.count("%s")
                actual = len(ns_params)
                if expected == actual:
                    cur.execute(NS_SEED_SQL, ns_params)
                    ns_rows = [dict(r) for r in cur.fetchall()]
                    rows.extend(ns_rows)

    # Small fusion nudge (after diversity) before promotion
    if apply_fusion_nudge is not None:
        try:
            rows = apply_fusion_nudge(rows, query)
        except Exception:
            pass

    # Post-ranked promotion (hard ns reserved) if tokens present
    ns_tokens = set()
    if extract_ns_tokens is not None:
        # merge explicit ns_token with regex-detected tokens in the query
        ns_tokens = extract_ns_tokens(query)
        if ns_token:
            ns_tokens.add(ns_token)
    # union inferred prefixes as well
    for t in _infer_ns_from_query(query):
        ns_tokens.add(t)

    if promote_ns_reserved is not None and ns_tokens:
        promoted_rows: list[dict[str, Any]] = promote_ns_reserved(rows, ns_tokens, k=limit, ns_reserved=ns_reserved)
        # optional debug print
        # if debug_print:
        #     debug_print(query, promoted_rows, ns_tokens, k=min(10, limit))
        rows = promoted_rows

    # Concise NS debug
    if debug:
        try:
            ns_total_in_pool = len(ns_rows) if "ns_rows" in locals() and isinstance(ns_rows, list) else 0
            top3 = [r.get("filename") for r in rows[:3]]
            print(f"[NS] q={query!r} ns={sorted(ns_tokens)} pool(ns={ns_total_in_pool}) top3={top3}")
        except Exception:
            pass

    return {
        "status": "success",
        "results": rows,
        "query": query,
        "limit": limit,
        "ns_union": use_ns_union,
        "ns_tokens": sorted(ns_tokens),
        "ns_reserved": ns_reserved,
    }
