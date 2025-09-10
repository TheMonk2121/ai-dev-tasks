#!/usr/bin/env python3
# ANCHOR_KEY: vector-store
# ANCHOR_PRIORITY: 30
# ROLE_PINS: ["implementer", "coder"]
"""
VectorStore DSPy Module (optimized)
- Unifies DB access via database_resilience manager
- Fixes dense result contract & hybrid merge
- Adds query-embed LRU cache and proper score fusion
- Includes spans in dense results
"""

# Standard library imports
import json
import logging
import os
import re
import uuid
from functools import lru_cache
from typing import Any

try:
    # DTO validation for retrieval candidates
    from pydantic import TypeAdapter

    from src.schemas.eval import RetrievalCandidate

    _RC_ADAPTER = TypeAdapter(list[RetrievalCandidate])
except Exception:
    _RC_ADAPTER = None  # type: ignore

import numpy as np

# Torch will be imported lazily when needed to avoid conflicts
# Third-party imports
from dspy import Module
from psycopg2 import errors
from psycopg2.extras import RealDictCursor, execute_values

# sentence_transformers will be imported lazily to avoid torch conflicts

# Local imports
try:
    from utils.database_resilience import get_database_manager
    from utils.db_pool import get_conn as get_stable_conn
    from utils.retry_wrapper import retry_database
except ImportError:
    # Fallback for when running from outside src directory
    from ..utils.database_resilience import get_database_manager
    from ..utils.retry_wrapper import retry_database

# Optional wrapper import kept at end of import section to satisfy linting rules
try:
    from .hybrid_wrapper import run_hybrid_search
except Exception:
    run_hybrid_search = None  # wrapper optional

# Set up logging
LOG = logging.getLogger(__name__)

# ---------------------------
# Model & embedding helpers
# ---------------------------


@lru_cache(maxsize=1)
def _get_model(name: str = "all-MiniLM-L6-v2"):
    """Singleton model loader to prevent repeated loads"""
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(name)
    except ImportError:
        raise ImportError("sentence_transformers not available")


@lru_cache(maxsize=1024)
def _cached_query_embedding_bytes(model_name: str, text: str) -> bytes:
    """Cache query embeddings by (model, text) as bytes to minimize memory overhead."""
    emb = _get_model(model_name).encode([text], convert_to_numpy=True)[0]
    # Lazy torch import to avoid conflicts
    try:
        import torch

        if isinstance(emb, torch.Tensor):
            emb = emb.detach().cpu().numpy()
    except ImportError:
        pass  # torch not available, continue with numpy
    emb = emb.astype(np.float32, copy=False)
    return emb.tobytes()


def _query_embedding(model_name: str, text: str) -> np.ndarray:
    return np.frombuffer(_cached_query_embedding_bytes(model_name, text), dtype=np.float32)


def _derive_section_title(file_path: str, chunk_text: str, prior_heading: str | None = None) -> str:
    """Heuristic section title extraction based on file type and content."""
    try:
        fp = (file_path or "").lower()
        # Markdown: use nearest heading if provided; else scan chunk
        if fp.endswith(".md"):
            if prior_heading:
                return prior_heading
            m = re.search(r"^(#{1,6})\s+(.*)$", chunk_text, re.MULTILINE)
            if m:
                return m.group(2).strip()
        # Python
        if fp.endswith(".py"):
            m = re.search(r"^(class|def)\s+([A-Za-z0-9_]+)", chunk_text, re.MULTILINE)
            if m:
                return f"{m.group(1).title()}: {m.group(2)}"
        # JS/TS
        if fp.endswith(".js") or fp.endswith(".ts") or fp.endswith(".tsx"):
            m = re.search(r"^(?:export\s+)?(class|function|const)\s+([A-Za-z0-9_]+)", chunk_text, re.MULTILINE)
            if m:
                return f"{m.group(1).title()}: {m.group(2)}"
        # SQL
        if fp.endswith(".sql"):
            m = re.search(
                r"^(CREATE|ALTER)\s+(INDEX|TABLE)\s+([A-Za-z0-9_\"]+)", chunk_text, re.MULTILINE | re.IGNORECASE
            )
            if m:
                return f"{m.group(2).title()}: {m.group(3)}"
        # YAML/TOML/JSON/ENV
        if fp.endswith((".yml", ".yaml", ".toml", ".json", ".env")):
            # crude: first two top-level keys as path
            keys = re.findall(r"^([A-Za-z0-9_.-]+):", chunk_text, re.MULTILINE)
            if keys:
                return " › ".join(keys[:2])
        # Fallback: filename
        return os.path.basename(file_path) if file_path else ""
    except Exception:
        return os.path.basename(file_path) if file_path else ""


# ---------------------------
# Intent extraction (namespace/filename)
# ---------------------------


def _extract_intent_namespace_and_filename(query: str) -> tuple[str, str, str]:
    """Extract optional namespace token and filename hints from a natural-language query.

    Returns (ns_token, file_exact, file_partial). Empty strings if not present.
    """
    ns_match = re.search(r"\b(000_core|100_memory|200_setup|400_guides)\b", query, re.IGNORECASE)
    ns_token = ns_match.group(1) if ns_match else ""

    file_match = re.search(r"([A-Za-z0-9_\-]+\.md)", query)
    file_exact = file_match.group(1) if file_match else ""
    file_partial = os.path.splitext(file_exact)[0] if file_exact else ""

    return ns_token, file_exact, file_partial


# ---------------------------
# Score normalization & fusion
# ---------------------------


def _zscore(scores: list[float]) -> list[float]:
    if not scores:
        return []
    mu = float(np.mean(scores))
    sigma = float(np.std(scores))
    if sigma == 0.0:
        # Avoid division by zero; all equal -> zeros
        return [0.0 for _ in scores]
    return [(s - mu) / sigma for s in scores]


def _rrf_ranks(scores: list[float]) -> dict[int, int]:
    # Higher score = better rank 1..N
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return {idx: rank + 1 for rank, idx in enumerate(order)}


def _fuse_dense_sparse(
    rows_dense: list[dict[str, Any]],
    rows_sparse: list[dict[str, Any]],
    limit: int,
    method: str = "zscore",  # or "rrf"
    w_dense: float = 0.6,
    w_sparse: float = 0.4,
) -> list[dict[str, Any]]:
    """
    Merge by key=(document_id, chunk_index) with either zscore fusion or RRF.
    Ensures comparable scales across modalities.
    """

    # Build maps
    def key(r):
        return (r["document_id"], r["chunk_index"])

    d_map = {key(r): r for r in rows_dense}
    s_map = {key(r): r for r in rows_sparse}

    # Union keys
    all_keys = list({*d_map.keys(), *s_map.keys()})

    # Prepare aligned score lists
    dense_scores = [d_map.get(k, {}).get("score_dense", 0.0) for k in all_keys]
    sparse_scores = [s_map.get(k, {}).get("score_sparse", 0.0) for k in all_keys]

    fused_scores: list[float] = []

    if method == "rrf":
        # Reciprocal Rank Fusion (stable when distributions are weird)
        k_dense = _rrf_ranks(dense_scores)
        k_sparse = _rrf_ranks(sparse_scores)
        # RRF: w/(60+rank) — 60 is conventional; tweak if needed
        fused_scores = [
            w_dense * (1.0 / (60.0 + k_dense.get(i, 60.0))) + w_sparse * (1.0 / (60.0 + k_sparse.get(i, 60.0)))
            for i in range(len(all_keys))
        ]
    else:
        # z-score normalize and weight
        zd = _zscore(dense_scores)
        zs = _zscore(sparse_scores)
        fused_scores = [w_dense * zd[i] + w_sparse * zs[i] for i in range(len(all_keys))]

    # Construct merged rows
    merged: list[dict[str, Any]] = []
    for i, k in enumerate(all_keys):
        d = d_map.get(k)
        s = s_map.get(k)
        base = d or s or {}
        row = {
            "document_id": base.get("document_id"),
            "chunk_index": base.get("chunk_index"),
            "content": base.get("content", ""),
            "score_dense": float(d.get("score_dense", 0.0)) if d else 0.0,
            "score_sparse": float(s.get("score_sparse", 0.0)) if s else 0.0,
            "hybrid_score": float(fused_scores[i]),
            "found_by": "both" if (d and s) else ("dense" if d else "sparse"),
            "start_offset": base.get("start_offset", 0),
            "end_offset": base.get("end_offset", len(base.get("content", ""))),
        }
        merged.append(row)

    merged.sort(key=lambda r: r["hybrid_score"], reverse=True)
    return merged[: max(1, int(limit))]


# ---------------------------
# Main module
# ---------------------------


class HybridVectorStore(Module):
    """DSPy module for hybrid vector storage and retrieval (dense + sparse)"""

    def __init__(
        self,
        db_connection_string: str,
        model_name: str = "all-MiniLM-L6-v2",
        metric: str = "cosine",  # "cosine", "l2", or "ip"
        fusion: str = "zscore",  # "zscore" or "rrf"
        w_dense: float = 0.6,
        w_sparse: float = 0.4,
        ivfflat_probes: int | None = None,  # e.g., 10, only if using IVF
        hnsw_ef_search: int | None = None,  # e.g., 80, only if using HNSW
        use_websearch_tsquery: bool = True,
    ):
        super().__init__()
        self.conn_str = db_connection_string
        self.model_name = model_name
        self.model = _get_model(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.metric = metric
        self.fusion = fusion
        self.w_dense = w_dense
        self.w_sparse = w_sparse
        self.ivfflat_probes = ivfflat_probes
        self.hnsw_ef_search = hnsw_ef_search
        self.use_websearch_tsquery = use_websearch_tsquery
        # Wrapper configuration (feature flag + ns reserved slots)
        self.use_wrapper: bool = os.getenv("HYBRID_USE_WRAPPER", "1") == "1"
        try:
            self.ns_reserved: int = int(os.getenv("NS_RESERVED", "2"))
        except Exception:
            self.ns_reserved = 2

    def forward(self, operation: str, **kwargs) -> dict[str, Any]:
        if operation == "store_chunks":
            return self._store_chunks_with_spans(**kwargs)
        elif operation == "search_vector":
            return self._search_vector(**kwargs)  # raw dense rows
        elif operation == "search_bm25":
            return self._search_bm25(**kwargs)  # raw sparse rows
        elif operation == "search":
            return self._hybrid_search(**kwargs)  # legacy merged path
        elif operation == "delete_document":
            return self._delete_document(**kwargs)
        elif operation == "get_document_chunks":
            return self._get_document_chunks(**kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    # ------------- Search -------------

    def _hybrid_search(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Hybrid search with guaranteed SQL aliasing and consistent column names."""
        q_emb = _query_embedding(self.model_name, query)
        ns_token, file_exact, file_partial = _extract_intent_namespace_and_filename(query)

        # Fast path: optionally delegate to wrapper (safer parameter building + ns slots)
        if self.use_wrapper and run_hybrid_search is not None:
            try:
                LOG.debug(
                    "wrapper hybrid: ns=%r file_exact=%r file_partial=%r ns_reserved=%s",
                    ns_token,
                    file_exact,
                    file_partial,
                    self.ns_reserved,
                )

                debug_flag = os.getenv("HYBRID_DEBUG_NS", "0") == "1"
                try:
                    pool_ns_env = int(os.getenv("POOL_NS", "0"))
                except Exception:
                    pool_ns_env = 0
                result = run_hybrid_search(
                    query=query,
                    q_emb=q_emb,
                    limit=limit,
                    ns_token=(ns_token or None),
                    filename_exact=(file_exact or None),
                    filename_partial=(file_partial or None),
                    ns_reserved=self.ns_reserved,
                    pool_ns=(pool_ns_env if pool_ns_env > 0 else 80),
                    debug=debug_flag,
                )
                rows = result.get("results", [])
                return {"status": "success", "search_type": "hybrid", "results": list(rows)}
            except Exception as e:
                LOG.error("Wrapper hybrid failed, falling back to inline: %s", e)

        try:
            # Use stable pool and explicit vector casts to avoid adapter issues
            LOG.debug("intent ns=%r file_exact=%r file_partial=%r", ns_token, file_exact, file_partial)
            with get_stable_conn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Per-query tunables (best-effort, ignore if unsupported)
                    if self.hnsw_ef_search is not None:
                        try:
                            cur.execute("SET LOCAL hnsw.ef_search = %s", (int(self.hnsw_ef_search),))
                        except Exception:
                            pass

                    # Base SQL using precomputed tsvector if available
                    sql = """
                        WITH vec AS (
                          SELECT
                            d.id         AS document_id,
                            d.filename   AS filename,
                            COALESCE(dc.file_path, d.file_path) AS file_path,
                            dc.content   AS content,
                            dc.embedding <=> %s::vector AS dist,
                            'vec'        AS src
                          FROM document_chunks dc
                          JOIN documents d ON dc.document_id = d.id
                          WHERE dc.embedding IS NOT NULL
                          ORDER BY dc.embedding <=> %s::vector
                          LIMIT 100
                        ),
                        vec_rank AS (
                          SELECT v.*, ROW_NUMBER() OVER (ORDER BY dist ASC) AS rnk_vec
                          FROM vec v
                        ),
                        bm AS (
                          SELECT
                            d.id         AS document_id,
                            d.filename   AS filename,
                            COALESCE(dc.file_path, d.file_path) AS file_path,
                            dc.content   AS content,
                            ts_rank_cd(dc.content_tsv, websearch_to_tsquery('english', %s)) AS bm25,
                            'bm25'       AS src
                          FROM document_chunks dc
                          JOIN documents d ON dc.document_id = d.id
                          WHERE dc.content_tsv @@ websearch_to_tsquery('english', %s)
                          ORDER BY bm25 DESC
                          LIMIT 100
                        ),
                        bm_rank AS (
                          SELECT b.*, ROW_NUMBER() OVER (ORDER BY bm25 DESC) AS rnk_bm
                          FROM bm b
                        ),
                        unioned AS (
                          SELECT document_id, filename, file_path, content, rnk_vec AS rnk, 'vec'  AS src FROM vec_rank
                          UNION ALL
                          SELECT document_id, filename, file_path, content, rnk_bm  AS rnk, 'bm25' AS src FROM bm_rank
                        ),
                        rrf AS (
                          SELECT
                            document_id, filename, file_path, content,
                            SUM(1.0 / (60 + rnk)) AS rrf_score
                          FROM unioned
                          GROUP BY document_id, filename, file_path, content
                        ),
                        ranked AS (
                          SELECT
                            r.*,
                            ROW_NUMBER() OVER (PARTITION BY r.document_id ORDER BY r.rrf_score DESC) AS dup_idx
                          FROM rrf r
                        ),
                        fused AS (
                          SELECT
                            document_id,
                            filename,
                            file_path,
                            content,
                            (rrf_score * (1.0 - 0.15 * GREATEST(dup_idx - 1, 0))) AS fused_score,
                            NULL::text AS src
                          FROM ranked
                        )
                        , boosted AS (
                          SELECT
                            r.document_id,
                            r.filename,
                            r.file_path,
                            r.content,
                            (
                              r.fused_score
                              + CASE WHEN %s <> '' AND r.file_path ILIKE '%%' || %s || '/%%' THEN 0.30 ELSE 0 END
                              + CASE
                                  WHEN %s <> '' AND LOWER(r.filename) = LOWER(%s) THEN 0.35
                                  WHEN %s <> '' AND r.filename ILIKE '%%' || %s || '%%' THEN 0.15
                                  ELSE 0
                                END
                            ) AS score,
                            r.src
                          FROM fused r
                        ),
                        u_ns AS (
                          SELECT b.*, CASE WHEN %s <> '' AND b.file_path ILIKE '%%' || %s || '/%%' THEN 1 ELSE 0 END AS ns_flag
                          FROM boosted b
                        ),
                        ns_subset AS (
                          SELECT * FROM u_ns WHERE ns_flag = 1 ORDER BY score DESC LIMIT 2
                        ),
                        ns_count AS (SELECT COUNT(*) AS c FROM ns_subset),
                        rest AS (
                          SELECT * FROM u_ns
                          WHERE document_id NOT IN (SELECT document_id FROM ns_subset)
                          ORDER BY score DESC
                          LIMIT GREATEST(%s - (SELECT c FROM ns_count), 0)
                        )
                        SELECT document_id, filename, file_path, content, score, src FROM (
                          SELECT * FROM ns_subset
                          UNION ALL
                          SELECT * FROM rest
                        ) final
                        ORDER BY score DESC
                        """
                    params = (
                        q_emb.tolist(),  # vec dist
                        q_emb.tolist(),  # vec order
                        query,  # bm tsquery
                        query,  # bm where
                        # boosts (6)
                        ns_token,
                        ns_token,
                        file_exact,
                        file_exact,
                        file_partial,
                        file_partial,
                        # ns gating (2)
                        ns_token,
                        ns_token,
                        # rest limit (1)
                        limit,
                    )
                    # Pre-execute guard on raw SQL (uses params)
                    expected = len(re.findall(r"(?<!%)%s", sql))
                    actual = len(params)
                    assert expected == actual, f"Placeholders={expected}, args={actual}"
                    try:
                        cur.execute(sql, params)
                    except Exception as e:
                        # Fallback if content_tsv is missing: compute tsvector on the fly
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
                    rows = cur.fetchall()

            payload = {
                "status": "success",
                "search_type": "hybrid",
                "results": list(rows),
            }

            # Optional: validate candidate rows into DTOs for downstream if requested
            try:
                if _RC_ADAPTER is not None and os.getenv("VALIDATE_CANDIDATES", "0") == "1":
                    raw = []
                    for idx, r in enumerate(payload["results"], start=1):
                        raw.append(
                            {
                                "query": str(query),
                                "chunk": {
                                    "id": f"{r.get('document_id')}:{r.get('chunk_index')}",
                                    "source": str(r.get("file_path") or r.get("filename") or ""),
                                    "text": str(r.get("content") or ""),
                                    "score": float(r.get("score", 0.0)),
                                    "metadata": {
                                        "document_id": r.get("document_id"),
                                        "chunk_index": r.get("chunk_index"),
                                    },
                                },
                                "rank": idx,
                                "score": float(r.get("score", 0.0)),
                                "route": "hybrid",
                            }
                        )
                    # Store validated snapshot for debugging/consumers
                    self._last_candidates_validated = _RC_ADAPTER.validate_python(raw)
            except Exception:
                self._last_candidates_validated = []

            return payload

        except Exception as e:
            LOG.error(f"Hybrid search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": [],
            }

    def _vector_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        """Dense vector search using pgvector with spans included."""
        return self._search_dense(query, limit)

    def _search_vector(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Raw vector search returning results with distance for canonicalization."""
        q_emb = _query_embedding(self.model_name, query)

        # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")
        where_clause = "WHERE dc.embedding IS NOT NULL"
        params: list[Any] = [q_emb]  # First q_emb for SELECT

        if run_id:
            where_clause += " AND dc.metadata->>'ingest_run_id' = %s"
            params.append(run_id)  # run_id for WHERE clause
        elif chunk_variant:
            where_clause += " AND dc.metadata->>'chunk_variant' = %s"
            params.append(chunk_variant)  # chunk_variant for WHERE clause
        else:
            # Use active configuration when no explicit run_id is set
            where_clause += " AND dc.metadata->>'ingest_run_id' = get_active_chunk_config()"

        params.append(q_emb)  # Second q_emb for ORDER BY
        params.append(limit)  # limit for LIMIT

        db_manager = get_database_manager()
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Per-query tunables (best-effort, ignore if unsupported)
                    if self.hnsw_ef_search is not None:
                        try:
                            cur.execute("SET LOCAL hnsw.ef_search = %s", (int(self.hnsw_ef_search),))
                        except Exception:
                            pass

                    cur.execute(
                        f"""
                        SELECT
                          dc.id AS id,
                          dc.document_id AS document_id,
                          dc.chunk_index AS chunk_index,
                          COALESCE(dc.file_path, d.file_path) AS file_path,
                          COALESCE(dc.file_path, d.file_path) AS filename,
                          dc.line_start AS line_start,
                          dc.line_end AS line_end,
                          dc.content AS content,
                          dc.bm25_text AS bm25_text,
                          dc.embedding_text AS embedding_text,
                          dc.embedding_token_count AS embedding_token_count,
                          dc.metadata->>'chunk_size' AS chunk_size,
                          dc.metadata->>'overlap_ratio' AS overlap_ratio,
                          dc.metadata->>'ingest_run_id' AS ingest_run_id,
                          dc.metadata->>'chunk_variant' AS chunk_variant,
                          dc.is_anchor AS is_anchor,
                          dc.anchor_key AS anchor_key,
                          dc.metadata AS metadata,
                          (dc.embedding <=> %s::vector) AS distance
                        FROM document_chunks dc
                        LEFT JOIN documents d ON d.id = dc.document_id
                        {where_clause}
                        ORDER BY dc.embedding <=> %s::vector ASC,
                                 COALESCE(dc.file_path, d.file_path) NULLS LAST,
                                 dc.chunk_index NULLS LAST,
                                 dc.id ASC
                        LIMIT %s
                        """,
                        params,
                    )
                    rows = cur.fetchall()

            return {"status": "success", "search_type": "vector", "results": list(rows)}

        except Exception:
            raise

    def _search_bm25(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Raw BM25 search returning results with ts_rank for canonicalization."""
        db_manager = get_database_manager()

        # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")

        where_clause = ""

        gating_param: Any | None = None
        if run_id:
            where_clause = "AND dc.metadata->>'ingest_run_id' = %s"
            gating_param = run_id
        elif chunk_variant:
            where_clause = "AND dc.metadata->>'chunk_variant' = %s"
            gating_param = chunk_variant
        else:
            # Use active configuration when no explicit run_id is set
            where_clause = "AND dc.metadata->>'ingest_run_id' = get_active_chunk_config()"

        # Build params in the exact order of placeholders in the SQL
        # 1) SELECT ts_rank(... %s)
        # 2) WHERE ... %s
        # 3) optional gating %s (if where_clause includes it)
        # 4) ORDER BY ts_rank(... %s)
        # 5) LIMIT %s
        ordered_params: list[Any] = [query, query]
        if gating_param is not None:
            ordered_params.append(gating_param)
        ordered_params.append(query)
        ordered_params.append(limit)

        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    try:
                        # Primary lexical path (websearch with generated tsvector)
                        cur.execute(
                            f"""
                            SELECT
                              dc.id AS id,
                              dc.document_id AS document_id,
                              dc.chunk_index AS chunk_index,
                              COALESCE(dc.file_path, d.file_path) AS file_path,
                              COALESCE(dc.file_path, d.file_path) AS filename,
                              dc.line_start AS line_start,
                              dc.line_end AS line_end,
                              dc.content AS content,
                              dc.bm25_text AS bm25_text,
                              dc.embedding_text AS embedding_text,
                              dc.embedding_token_count AS embedding_token_count,
                              dc.metadata->>'chunk_size' AS chunk_size,
                              dc.metadata->>'overlap_ratio' AS overlap_ratio,
                              dc.metadata->>'ingest_run_id' AS ingest_run_id,
                              dc.metadata->>'chunk_variant' AS chunk_variant,
                              dc.is_anchor AS is_anchor,
                              dc.anchor_key AS anchor_key,
                              dc.metadata AS metadata,
                              ts_rank(dc.ts, websearch_to_tsquery('english', %s)) AS bm25
                            FROM document_chunks dc
                            LEFT JOIN documents d ON d.id = dc.document_id
                            WHERE dc.ts @@ websearch_to_tsquery('english', %s)
                            {where_clause}
                            ORDER BY ts_rank(dc.ts, websearch_to_tsquery('english', %s)) DESC
                            LIMIT %s
                            """,
                            ordered_params,
                        )
                    except Exception as e:
                        if "content_tsv" in str(e).lower():
                            cur.execute(
                                """
                                SELECT
                                  dc.id AS id,
                                  dc.document_id AS document_id,
                                  dc.chunk_index AS chunk_index,
                                  COALESCE(dc.file_path, d.file_path) AS file_path,
                                  COALESCE(dc.file_path, d.file_path) AS filename,
                                  dc.line_start AS line_start,
                                  dc.line_end AS line_end,
                                  dc.content AS content,
                                  dc.is_anchor AS is_anchor,
                                  dc.anchor_key AS anchor_key,
                                  dc.metadata AS metadata,
                                  ts_rank_cd(to_tsvector('english', dc.content), websearch_to_tsquery('english', %s)) AS bm25
                                FROM document_chunks dc
                                LEFT JOIN documents d ON d.id = dc.document_id
                                WHERE to_tsvector('english', dc.content) @@ websearch_to_tsquery('english', %s)
                                ORDER BY bm25 DESC,
                                         COALESCE(dc.file_path, d.file_path) NULLS LAST,
                                         dc.chunk_index NULLS LAST,
                                         dc.id ASC
                                LIMIT %s
                                """,
                                (query, query, limit),
                            )
                        else:
                            raise
                    rows = cur.fetchall()

                    # Trigram fallback if results are thin
                    if len(rows) < limit and os.getenv("BM25_TRIGRAM_FALLBACK", "1") == "1":
                        try:
                            # Build fallback params explicitly to match placeholders:
                            # SELECT similarity(..., %s)
                            # WHERE dc.bm25_text % %s
                            # {where_clause}  # may introduce a gating %s
                            # ORDER BY similarity(..., %s)
                            # LIMIT %s
                            fb_params = [query, query]
                            if "%s" in where_clause:
                                # ordered_params layout: [query, query, (gating)?, query, limit]
                                # pick gating if present
                                try:
                                    gating = ordered_params[2]
                                    fb_params.append(gating)
                                except Exception:
                                    pass
                            fb_params.extend([query, ordered_params[-1]])
                            cur.execute(
                                f"""
                                SELECT
                                  dc.id AS id,
                                  dc.document_id AS document_id,
                                  dc.chunk_index AS chunk_index,
                                  COALESCE(dc.file_path, d.file_path) AS file_path,
                                  COALESCE(dc.file_path, d.file_path) AS filename,
                                  dc.line_start AS line_start,
                                  dc.line_end AS line_end,
                                  dc.content AS content,
                                  dc.bm25_text AS bm25_text,
                                  dc.embedding_text AS embedding_text,
                                  dc.embedding_token_count AS embedding_token_count,
                                  dc.metadata->>'chunk_size' AS chunk_size,
                                  dc.metadata->>'overlap_ratio' AS overlap_ratio,
                                  dc.metadata->>'ingest_run_id' AS ingest_run_id,
                                  dc.metadata->>'chunk_variant' AS chunk_variant,
                                  dc.is_anchor AS is_anchor,
                                  dc.anchor_key AS anchor_key,
                                  dc.metadata AS metadata,
                                  similarity(dc.bm25_text, %s) AS bm25
                                FROM document_chunks dc
                                LEFT JOIN documents d ON d.id = dc.document_id
                                WHERE dc.bm25_text % %s
                                {where_clause}
                                ORDER BY similarity(dc.bm25_text, %s) DESC
                                LIMIT %s
                                """,
                                fb_params,
                            )
                            fallback_rows = cur.fetchall()
                            # Merge results, avoiding duplicates
                            existing_ids = {row["id"] for row in rows}
                            for row in fallback_rows:
                                if row["id"] not in existing_ids and len(rows) < limit:
                                    rows.append(row)
                        except Exception as e:
                            LOG.warning(f"Trigram fallback failed: {e}")

            return {"status": "success", "search_type": "bm25", "results": list(rows)}

        except Exception:
            raise

    def _search_title(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Search using title/path full-text search with trigram fallback."""
        db_manager = get_database_manager()

        # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")

        where_clause = ""
        params: list[Any] = [query, query]

        gating_param: Any | None = None
        if run_id:
            where_clause = "AND dc.metadata->>'ingest_run_id' = %s"
            gating_param = run_id
        elif chunk_variant:
            where_clause = "AND dc.metadata->>'chunk_variant' = %s"
            gating_param = chunk_variant
        else:
            # Use active configuration when no explicit run_id is set
            where_clause = "AND dc.metadata->>'ingest_run_id' = get_active_chunk_config()"

        # Build params in the exact order of placeholders in the SQL
        ordered_params: list[Any] = [query, query]
        if gating_param is not None:
            ordered_params.append(gating_param)
        ordered_params.append(query)
        ordered_params.append(limit)

        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    try:
                        # Primary title search using websearch_to_tsquery
                        cur.execute(
                            f"""
                            SELECT
                              dc.id AS id,
                              dc.document_id AS document_id,
                              dc.chunk_index AS chunk_index,
                              COALESCE(dc.file_path, d.file_path) AS file_path,
                              COALESCE(dc.file_path, d.file_path) AS filename,
                              dc.line_start AS line_start,
                              dc.line_end AS line_end,
                              dc.content AS content,
                              dc.bm25_text AS bm25_text,
                              dc.embedding_text AS embedding_text,
                              dc.embedding_token_count AS embedding_token_count,
                              dc.metadata->>'chunk_size' AS chunk_size,
                              dc.metadata->>'overlap_ratio' AS overlap_ratio,
                              dc.metadata->>'ingest_run_id' AS ingest_run_id,
                              dc.metadata->>'chunk_variant' AS chunk_variant,
                              dc.is_anchor AS is_anchor,
                              dc.anchor_key AS anchor_key,
                              dc.metadata AS metadata,
                              ts_rank(dc.title_ts, websearch_to_tsquery('simple', %s)) AS score
                            FROM document_chunks dc
                            LEFT JOIN documents d ON d.id = dc.document_id
                            WHERE dc.title_ts @@ websearch_to_tsquery('simple', %s)
                            {where_clause}
                            ORDER BY ts_rank(dc.title_ts, websearch_to_tsquery('simple', %s)) DESC
                            LIMIT %s
                            """,
                            ordered_params,
                        )
                    except Exception as e:
                        if "title_ts" in str(e).lower():
                            # Fallback to trigram similarity if title_ts column doesn't exist
                            # Build fallback params explicitly (see note above)
                            fb_params = [query, query]
                            if "%s" in where_clause:
                                try:
                                    gating = ordered_params[2]
                                    fb_params.append(gating)
                                except Exception:
                                    pass
                            fb_params.extend([query, ordered_params[-1]])
                            cur.execute(
                                f"""
                                SELECT
                                  dc.id AS id,
                                  dc.document_id AS document_id,
                                  dc.chunk_index AS chunk_index,
                                  COALESCE(dc.file_path, d.file_path) AS file_path,
                                  COALESCE(dc.file_path, d.file_path) AS filename,
                                  dc.line_start AS line_start,
                                  dc.line_end AS line_end,
                                  dc.content AS content,
                                  dc.bm25_text AS bm25_text,
                                  dc.embedding_text AS embedding_text,
                                  dc.embedding_token_count AS embedding_token_count,
                                  dc.metadata->>'chunk_size' AS chunk_size,
                                  dc.metadata->>'overlap_ratio' AS overlap_ratio,
                                  dc.metadata->>'ingest_run_id' AS ingest_run_id,
                                  dc.metadata->>'chunk_variant' AS chunk_variant,
                                  dc.is_anchor AS is_anchor,
                                  dc.anchor_key AS anchor_key,
                                  dc.metadata AS metadata,
                                  similarity(dc.file_path, %s) AS score
                                FROM document_chunks dc
                                LEFT JOIN documents d ON d.id = dc.document_id
                                WHERE dc.file_path % %s
                                {where_clause}
                                ORDER BY similarity(dc.file_path, %s) DESC
                                LIMIT %s
                                """,
                                fb_params,
                            )
                        else:
                            raise
                    rows = cur.fetchall()

                    # Trigram fallback if results are thin
                    if len(rows) < limit and os.getenv("TITLE_TRIGRAM_FALLBACK", "1") == "1":
                        try:
                            cur.execute(
                                f"""
                                SELECT
                                  dc.id AS id,
                                  dc.document_id AS document_id,
                                  dc.chunk_index AS chunk_index,
                                  COALESCE(dc.file_path, d.file_path) AS file_path,
                                  COALESCE(dc.file_path, d.file_path) AS filename,
                                  dc.line_start AS line_start,
                                  dc.line_end AS line_end,
                                  dc.content AS content,
                                  dc.bm25_text AS bm25_text,
                                  dc.embedding_text AS embedding_text,
                                  dc.embedding_token_count AS embedding_token_count,
                                  dc.metadata->>'chunk_size' AS chunk_size,
                                  dc.metadata->>'overlap_ratio' AS overlap_ratio,
                                  dc.metadata->>'ingest_run_id' AS ingest_run_id,
                                  dc.metadata->>'chunk_variant' AS chunk_variant,
                                  dc.is_anchor AS is_anchor,
                                  dc.anchor_key AS anchor_key,
                                  dc.metadata AS metadata,
                                  similarity(dc.file_path, %s) AS score
                                FROM document_chunks dc
                                LEFT JOIN documents d ON d.id = dc.document_id
                                WHERE dc.file_path % %s
                                {where_clause}
                                ORDER BY similarity(dc.file_path, %s) DESC
                                LIMIT %s
                                """,
                                [query, query, query] + params[2:],
                            )
                            fallback_rows = cur.fetchall()
                            # Merge results, avoiding duplicates
                            existing_ids = {row["id"] for row in rows}
                            for row in fallback_rows:
                                if row["id"] not in existing_ids and len(rows) < limit:
                                    rows.append(row)
                        except Exception as e:
                            LOG.warning(f"Title trigram fallback failed: {e}")

            return {"status": "success", "search_type": "title", "results": list(rows)}

        except Exception:
            raise

    @retry_database
    def _search_dense(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        q_emb = _query_embedding(self.model_name, query)

        # Choose distance operator according to metric
        # pgvector operators: '<->' (L2), '<#>' (inner product), '<=>'(cosine)
        if self.metric == "l2":
            order_expr = "embedding <-> %s"
            sim_expr = "1.0 / (1.0 + (embedding <-> %s))"  # monotonic; avoids negatives
        elif self.metric == "ip":
            order_expr = "embedding <#> %s"  # lower is better for distance semantics
            sim_expr = "(- (embedding <#> %s))"  # convert to higher-is-better
        else:
            # cosine distance in [0..2]; convert to similarity in [1..-1] then clamp
            order_expr = "embedding <=> %s"
            sim_expr = "GREATEST(-1.0, LEAST(1.0, 1.0 - (embedding <=> %s)))"

        db_manager = get_database_manager()
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Per-query tunables (best-effort, ignore if unsupported)
                    if self.ivfflat_probes is not None:
                        try:
                            cur.execute("SET LOCAL ivfflat.probes = %s", (int(self.ivfflat_probes),))
                        except Exception:
                            pass
                    if self.hnsw_ef_search is not None:
                        try:
                            cur.execute("SET LOCAL hnsw.ef_search = %s", (int(self.hnsw_ef_search),))
                        except Exception:
                            pass

                    cur.execute(
                        f"""
                        SELECT document_id, chunk_index, content,
                               line_start, line_end,
                               {sim_expr} AS score_dense
                        FROM document_chunks
                        ORDER BY {order_expr}
                        LIMIT %s
                        """,
                        (q_emb, q_emb, limit),
                    )
                    rows = cur.fetchall()

            # Normalize shape
            out: list[dict[str, Any]] = []
            for r in rows:
                out.append(
                    {
                        "document_id": r["document_id"],
                        "chunk_index": r["chunk_index"],
                        "content": r["content"],
                        "start_offset": r.get("line_start", 0) or 0,
                        "end_offset": (
                            r.get("line_end", len(r["content"])) if r.get("content") else r.get("line_end", 0)
                        ),
                        "score_dense": float(r["score_dense"]),
                        "score_sparse": 0.0,
                    }
                )
            return out

        except Exception:
            raise

    def _text_search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Sparse text search using PostgreSQL full-text search (with spans)."""
        db_manager = get_database_manager()
        ts_fn = "websearch_to_tsquery" if self.use_websearch_tsquery else "plainto_tsquery"

        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        f"""
                        SELECT
                            document_id,
                            chunk_index,
                            content,
                            line_start,
                            line_end,
                            metadata->>'ingest_run_id' AS ingest_run_id,
                            metadata->>'chunk_variant' AS chunk_variant,
                            ts_rank(to_tsvector('english', content), {ts_fn}('english', %s)) AS score_sparse
                        FROM document_chunks
                        WHERE to_tsvector('english', content) @@ {ts_fn}('english', %s)
                        ORDER BY score_sparse DESC
                        LIMIT %s
                        """,
                        (query, query, limit),
                    )
                    rows = cur.fetchall()

            out: list[dict[str, Any]] = []
            for r in rows:
                out.append(
                    {
                        "document_id": r["document_id"],
                        "chunk_index": r["chunk_index"],
                        "content": r["content"],
                        "start_offset": r.get("line_start", 0) or 0,
                        "end_offset": (
                            r.get("line_end", len(r["content"])) if r.get("content") else r.get("line_end", 0)
                        ),
                        "score_dense": 0.0,
                        "score_sparse": float(r["score_sparse"]),
                        "ingest_run_id": r.get("ingest_run_id"),
                        "chunk_variant": r.get("chunk_variant"),
                    }
                )
            return out

        except Exception:
            raise

    def _search_section(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Search section titles using full-text and trigram similarity with gating."""
        db_manager = get_database_manager()

        # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")

        where_clause = ""
        params: list[Any] = [query, query]

        gating_param: Any | None = None
        if run_id:
            where_clause = "AND dc.metadata->>'ingest_run_id' = %s"
            gating_param = run_id
        elif chunk_variant:
            where_clause = "AND dc.metadata->>'chunk_variant' = %s"
            gating_param = chunk_variant
        else:
            # Use active configuration when no explicit run_id is set
            where_clause = "AND dc.metadata->>'ingest_run_id' = get_active_chunk_config()"

        ordered_params: list[Any] = [query, query]
        if gating_param is not None:
            ordered_params.append(gating_param)
        ordered_params.append(query)
        ordered_params.append(limit)

        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    try:
                        cur.execute(
                            f"""
                            SELECT
                              dc.id AS id,
                              dc.document_id AS document_id,
                              dc.chunk_index AS chunk_index,
                              COALESCE(dc.file_path, d.file_path) AS file_path,
                              COALESCE(dc.file_path, d.file_path) AS filename,
                              dc.section_title AS section_title,
                              dc.content AS content,
                              dc.metadata->>'ingest_run_id' AS ingest_run_id,
                              dc.metadata->>'chunk_variant' AS chunk_variant,
                              ts_rank(dc.section_ts, websearch_to_tsquery('simple', %s)) AS score
                            FROM document_chunks dc
                            LEFT JOIN documents d ON d.id = dc.document_id
                            WHERE dc.section_ts @@ websearch_to_tsquery('simple', %s)
                            {where_clause}
                            ORDER BY ts_rank(dc.section_ts, websearch_to_tsquery('simple', %s)) DESC
                            LIMIT %s
                            """,
                            ordered_params,
                        )
                    except Exception as e:
                        if "section_ts" in str(e).lower():
                            cur.execute(
                                f"""
                                SELECT
                                  dc.id AS id,
                                  dc.document_id AS document_id,
                                  dc.chunk_index AS chunk_index,
                                  COALESCE(dc.file_path, d.file_path) AS file_path,
                                  COALESCE(dc.file_path, d.file_path) AS filename,
                                  dc.section_title AS section_title,
                                  dc.content AS content,
                                  dc.metadata->>'ingest_run_id' AS ingest_run_id,
                                  dc.metadata->>'chunk_variant' AS chunk_variant,
                                  similarity(COALESCE(dc.section_title,''), %s) AS score
                                FROM document_chunks dc
                                LEFT JOIN documents d ON d.id = dc.document_id
                                WHERE COALESCE(dc.section_title,'') % %s
                                {where_clause}
                                ORDER BY similarity(COALESCE(dc.section_title,''), %s) DESC
                                LIMIT %s
                                """,
                                [query, query, query] + params[2:],
                            )
                        else:
                            raise
                    rows = cur.fetchall()

                    # Trigram fallback if results are thin
                    if len(rows) < limit:
                        try:
                            cur.execute(
                                f"""
                                SELECT
                                  dc.id AS id,
                                  dc.document_id AS document_id,
                                  dc.chunk_index AS chunk_index,
                                  COALESCE(dc.file_path, d.file_path) AS file_path,
                                  COALESCE(dc.file_path, d.file_path) AS filename,
                                  dc.section_title AS section_title,
                                  dc.content AS content,
                                  dc.metadata->>'ingest_run_id' AS ingest_run_id,
                                  dc.metadata->>'chunk_variant' AS chunk_variant,
                                  similarity(COALESCE(dc.section_title,''), %s) AS score
                                FROM document_chunks dc
                                LEFT JOIN documents d ON d.id = dc.document_id
                                WHERE COALESCE(dc.section_title,'') % %s
                                {where_clause}
                                ORDER BY similarity(COALESCE(dc.section_title,''), %s) DESC
                                LIMIT %s
                                """,
                                [query, query, query] + params[2:],
                            )
                            fallback_rows = cur.fetchall()
                            existing_ids = {row["id"] for row in rows}
                            for row in fallback_rows:
                                if row["id"] not in existing_ids and len(rows) < limit:
                                    rows.append(row)
                        except Exception as e:
                            LOG.warning(f"Section trigram fallback failed: {e}")

            return {"status": "success", "search_type": "section", "results": list(rows)}

        except Exception:
            raise

    def _search_short(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Short-field search over section_title + filename basename (weighted)."""
        db_manager = get_database_manager()

        # Add run ID gating for evaluations
        run_id = os.getenv("INGEST_RUN_ID")
        chunk_variant = os.getenv("CHUNK_VARIANT")

        where_clause = ""
        gating_param: Any | None = None
        if run_id:
            where_clause = "AND dc.metadata->>'ingest_run_id' = %s"
            gating_param = run_id
        elif chunk_variant:
            where_clause = "AND dc.metadata->>'chunk_variant' = %s"
            gating_param = chunk_variant
        else:
            where_clause = "AND dc.metadata->>'ingest_run_id' = get_active_chunk_config()"

        ordered_params: list[Any] = [query]
        if gating_param is not None:
            ordered_params.append(gating_param)
        ordered_params.append(query)
        ordered_params.append(limit)

        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Primary short_tsv query
                    cur.execute(
                        f"""
                        SELECT
                          dc.id AS id,
                          dc.document_id AS document_id,
                          dc.chunk_index AS chunk_index,
                          COALESCE(dc.file_path, d.file_path) AS file_path,
                          COALESCE(dc.filename, d.file_path) AS filename,
                          dc.section_title AS section_title,
                          dc.content AS content,
                          dc.metadata->>'ingest_run_id' AS ingest_run_id,
                          dc.metadata->>'chunk_variant' AS chunk_variant,
                          ts_rank_cd(dc.short_tsv, websearch_to_tsquery('simple', %s)) AS score
                        FROM document_chunks dc
                        LEFT JOIN documents d ON d.id = dc.document_id
                        WHERE dc.short_tsv @@ websearch_to_tsquery('simple', %s)
                        {where_clause}
                        ORDER BY score DESC
                        LIMIT %s
                        """,
                        ordered_params,
                    )
                    rows = cur.fetchall()

                    if len(rows) < limit:
                        # Trigram fallback on section_title or filename basename
                        fallback_params: list[Any] = [query, query]
                        if gating_param is not None:
                            fallback_params.append(gating_param)
                        fallback_params.extend([query, limit - len(rows)])

                        cur.execute(
                            f"""
                            SELECT
                              dc.id AS id,
                              dc.document_id AS document_id,
                              dc.chunk_index AS chunk_index,
                              COALESCE(dc.file_path, d.file_path) AS file_path,
                              COALESCE(dc.filename, d.file_path) AS filename,
                              dc.section_title AS section_title,
                              dc.content AS content,
                              dc.metadata->>'ingest_run_id' AS ingest_run_id,
                              dc.metadata->>'chunk_variant' AS chunk_variant,
                              GREATEST(
                                similarity(dc.section_title, %s),
                                similarity(regexp_replace(coalesce(dc.filename,''), '^.*/', ''), %s)
                              ) AS score
                            FROM document_chunks dc
                            LEFT JOIN documents d ON d.id = dc.document_id
                            WHERE dc.section_title % %s
                               OR regexp_replace(coalesce(dc.filename,''), '^.*/', '') % %s
                            {where_clause}
                            ORDER BY score DESC
                            LIMIT %s
                            """,
                            fallback_params,
                        )
                        frows = cur.fetchall()
                        # Merge without duplicates
                        seen = {r["id"] for r in rows}
                        for r in frows:
                            if r["id"] not in seen and len(rows) < limit:
                                rows.append(r)

            return {"status": "success", "search_type": "short", "results": list(rows)}

        except Exception:
            raise

    # ------------- Store -------------

    @retry_database
    def _store_chunks_with_spans(self, chunks: list[str], metadata: dict[str, Any]) -> dict[str, Any]:
        """Store document chunks with embeddings and span information."""
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        doc_id = metadata.get("document_id") or uuid.uuid4().hex

        chunk_rows: list[tuple] = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            # Lazy torch import to avoid conflicts
            try:
                import torch

                if isinstance(emb, torch.Tensor):
                    emb = emb.detach().cpu().numpy()
            except ImportError:
                pass  # torch not available, continue with numpy
            emb = emb.astype(np.float32, copy=False)

            # Calculate line numbers for the chunk
            # For now, use chunk index as line numbers (simplified approach)
            line_start = i * 10 + 1  # Approximate line numbers
            line_end = line_start + chunk.count("\n")

            # Derive section title
            section_title = _derive_section_title(
                metadata.get("file_path", metadata.get("filename", "")) or "", chunk, None
            )

            # Attach section_title into metadata copy for traceability
            md = dict(metadata)
            md["section_title"] = section_title

            chunk_rows.append((doc_id, i, chunk, emb, line_start, line_end, json.dumps(md), section_title))

        return self._insert_with_spans(chunk_rows, metadata, doc_id, len(chunks))

    def _insert_with_spans(
        self,
        chunk_rows: list[tuple],
        metadata: dict[str, Any],
        doc_id: str,
        chunk_count: int,
    ) -> dict[str, Any]:
        db_manager = get_database_manager()
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    # Insert document record and get the generated ID
                    cur.execute(
                        """
                        INSERT INTO documents
                               (filename, file_path, file_type, file_size,
                                chunk_count, status)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        RETURNING id
                        """,
                        (
                            metadata.get("filename"),
                            metadata.get(
                                "file_path", metadata.get("filename")
                            ),  # Fallback to filename if file_path is missing
                            metadata.get("file_type"),
                            metadata.get("file_size", 0),
                            chunk_count,
                            "completed",
                        ),
                    )
                    result = cur.fetchone()
                    if result is None:
                        raise Exception("Failed to insert document - no ID returned")
                    document_id = result[0]

                    # Update chunk rows with the correct document_id
                    updated_chunk_rows = []
                    for chunk_row in chunk_rows:
                        updated_chunk_rows.append(
                            (
                                chunk_row[0],  # document_id
                                chunk_row[1],  # chunk_index
                                chunk_row[2],  # content
                                chunk_row[3],  # embedding
                                chunk_row[4],  # line_start
                                chunk_row[5],  # line_end
                                chunk_row[6],  # metadata (with section_title)
                                chunk_row[7],  # section_title
                            )
                        )

                    # Re-insert chunks with correct document_id and new schema
                    updated_chunk_rows_with_schema = []
                    for chunk_row in updated_chunk_rows:
                        # Extract metadata to get anchor information
                        chunk_metadata = json.loads(chunk_row[6]) if chunk_row[6] else {}
                        is_anchor = chunk_metadata.get("is_anchor", False)
                        anchor_key = chunk_metadata.get("anchor_key")
                        file_path = chunk_metadata.get("file_path", metadata.get("file_path", metadata.get("filename")))
                        section_title = chunk_row[7]

                        updated_chunk_rows_with_schema.append(
                            (
                                chunk_row[0],  # document_id
                                chunk_row[1],  # chunk_index
                                file_path,  # file_path (first-class column)
                                chunk_row[4],  # line_start
                                chunk_row[5],  # line_end
                                chunk_row[2],  # content
                                chunk_row[3],  # embedding
                                is_anchor,  # is_anchor (first-class column)
                                anchor_key,  # anchor_key (first-class column)
                                chunk_row[6],  # metadata (JSONB)
                                section_title,  # section_title
                            )
                        )

                    # Insert with new schema including first-class columns
                    execute_values(
                        cur,
                        """
                        INSERT INTO document_chunks
                             (document_id, chunk_index, file_path, line_start, line_end,
                              content, embedding, is_anchor, anchor_key, metadata, section_title)
                        VALUES %s
                        """,
                        updated_chunk_rows_with_schema,
                        template="(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    )
            return {
                "status": "success",
                "document_id": document_id,
                "chunks_stored": chunk_count,
                "spans_tracked": True,
            }
        except Exception as e:
            LOG.error(f"Error in _insert_with_spans: {e}")
            raise

    # ------------- Admin -------------

    def _delete_document(self, document_id: str) -> dict[str, Any]:
        try:
            db_manager = get_database_manager()
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM document_chunks WHERE document_id = %s", (document_id,))
                    cur.execute("DELETE FROM documents WHERE document_id = %s", (document_id,))
            return {"status": "success", "document_id": document_id, "message": "Document and all chunks deleted"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_document_chunks(self, document_id: str) -> dict[str, Any]:
        try:
            db_manager = get_database_manager()
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT chunk_index, content, created_at
                        FROM document_chunks
                        WHERE document_id = %s
                        ORDER BY chunk_index
                        """,
                        (document_id,),
                    )
                    rows = cur.fetchall()
            chunks = [
                {
                    "chunk_index": r["chunk_index"],
                    "content": r["content"],
                    "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                }
                for r in rows
            ]
            return {"status": "success", "document_id": document_id, "chunks": chunks, "total_chunks": len(chunks)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_stats(self) -> dict[str, Any]:
        try:
            db_manager = get_database_manager()
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM document_chunks")
                    total_chunks = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM documents")
                    total_documents = cur.fetchone()[0]
                    try:
                        cur.execute("SELECT COUNT(*) FROM conversation_memory")
                        total_conversations = cur.fetchone()[0]
                    except errors.UndefinedTable:
                        total_conversations = 0
                    cur.execute("SELECT file_type, COUNT(*) FROM documents GROUP BY file_type")
                    document_types = dict(cur.fetchall())
            return {
                "status": "success",
                "total_chunks": total_chunks,
                "total_documents": total_documents,
                "total_conversations": total_conversations,
                "document_types": document_types,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_statistics(self) -> dict[str, Any]:
        """Alias for get_stats() to align with dashboard API"""
        return self.get_stats()


class VectorStorePipeline(Module):
    """DSPy module for complete vector store pipeline"""

    def __init__(self, db_connection_string: str):
        super().__init__()
        self.vector_store = HybridVectorStore(db_connection_string)

    def forward(self, operation: str, **kwargs) -> dict[str, Any]:
        result = self.vector_store(operation, **kwargs)
        if isinstance(result, dict):
            return result
        else:
            # Fallback for unexpected return types
            return {"status": "error", "error": f"Unexpected result type: {type(result)}"}


if __name__ == "__main__":
    # Quick smoke test (requires running DB with the expected schema)
    db_connection = "postgresql://danieljacobs@localhost:5432/ai_agency"
    vector_store = HybridVectorStore(db_connection)
    print(vector_store("search", query="What is DSPy?", limit=3))
    print(vector_store.get_stats())
