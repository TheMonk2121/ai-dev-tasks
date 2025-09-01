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
from typing import Any, Dict, List, Optional, Tuple

try:
    from .hybrid_wrapper import run_hybrid_search
except Exception:
    run_hybrid_search = None  # wrapper optional

# Third-party imports
import numpy as np
import torch
from dspy import Module
from psycopg2 import errors
from psycopg2.extras import RealDictCursor, execute_values
from sentence_transformers import SentenceTransformer

# Local imports
try:
    from utils.database_resilience import get_database_manager
    from utils.db_pool import get_conn as get_stable_conn
    from utils.retry_wrapper import retry_database
except ImportError:
    # Fallback for when running from outside src directory
    from ..utils.database_resilience import get_database_manager
    from ..utils.retry_wrapper import retry_database

# Set up logging
LOG = logging.getLogger(__name__)

# ---------------------------
# Model & embedding helpers
# ---------------------------


@lru_cache(maxsize=1)
def _get_model(name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Singleton model loader to prevent repeated loads"""
    return SentenceTransformer(name)


@lru_cache(maxsize=1024)
def _cached_query_embedding_bytes(model_name: str, text: str) -> bytes:
    """Cache query embeddings by (model, text) as bytes to minimize memory overhead."""
    emb = _get_model(model_name).encode([text], convert_to_numpy=True)[0]
    if isinstance(emb, torch.Tensor):
        emb = emb.detach().cpu().numpy()
    emb = emb.astype(np.float32, copy=False)
    return emb.tobytes()


def _query_embedding(model_name: str, text: str) -> np.ndarray:
    return np.frombuffer(_cached_query_embedding_bytes(model_name, text), dtype=np.float32)


# ---------------------------
# Intent extraction (namespace/filename)
# ---------------------------


def _extract_intent_namespace_and_filename(query: str) -> Tuple[str, str, str]:
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


def _zscore(scores: List[float]) -> List[float]:
    if not scores:
        return []
    mu = float(np.mean(scores))
    sigma = float(np.std(scores))
    if sigma == 0.0:
        # Avoid division by zero; all equal -> zeros
        return [0.0 for _ in scores]
    return [(s - mu) / sigma for s in scores]


def _rrf_ranks(scores: List[float]) -> Dict[int, int]:
    # Higher score = better rank 1..N
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return {idx: rank + 1 for rank, idx in enumerate(order)}


def _fuse_dense_sparse(
    rows_dense: List[Dict[str, Any]],
    rows_sparse: List[Dict[str, Any]],
    limit: int,
    method: str = "zscore",  # or "rrf"
    w_dense: float = 0.6,
    w_sparse: float = 0.4,
) -> List[Dict[str, Any]]:
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

    fused_scores: List[float] = []

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
    merged: List[Dict[str, Any]] = []
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
        ivfflat_probes: Optional[int] = None,  # e.g., 10, only if using IVF
        hnsw_ef_search: Optional[int] = None,  # e.g., 80, only if using HNSW
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

    def forward(self, operation: str, **kwargs) -> Dict[str, Any]:
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

    def _hybrid_search(self, query: str, limit: int = 5) -> Dict[str, Any]:
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

                    sql = """
                        WITH vec AS (
                          SELECT
                            d.id         AS document_id,
                            d.filename   AS filename,
                            dc.file_path AS file_path,
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
                            dc.file_path AS file_path,
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
                    # Pre-execute guard on raw SQL
                    expected = len(re.findall(r"(?<!%)%s", sql))
                    actual = len(params)
                    assert expected == actual, f"Placeholders={expected}, args={actual}"
                    cur.execute(sql, params)
                    rows = cur.fetchall()

            return {
                "status": "success",
                "search_type": "hybrid",
                "results": list(rows),
            }

        except Exception as e:
            LOG.error(f"Hybrid search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": [],
            }

    def _vector_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Dense vector search using pgvector with spans included."""
        return self._search_dense(query, limit)

    def _search_vector(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Raw vector search returning results with distance for canonicalization."""
        q_emb = _query_embedding(self.model_name, query)

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
                        """
                        SELECT
                          id, document_id, chunk_index, file_path, line_start, line_end,
                          content, is_anchor, anchor_key, metadata,
                          (embedding <=> %s::vector) AS distance
                        FROM document_chunks
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector ASC,
                                 file_path NULLS LAST,
                                 chunk_index NULLS LAST,
                                 id ASC
                        LIMIT %s
                        """,
                        (q_emb, q_emb, limit),
                    )
                    rows = cur.fetchall()

            return {"status": "success", "search_type": "vector", "results": list(rows)}

        except Exception:
            raise

    def _search_bm25(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Raw BM25 search returning results with ts_rank for canonicalization."""
        db_manager = get_database_manager()

        try:
            with db_manager.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT
                          id, document_id, chunk_index, file_path, line_start, line_end,
                          content, is_anchor, anchor_key, metadata,
                          ts_rank_cd(content_tsv, websearch_to_tsquery('english', %s)) AS bm25
                        FROM document_chunks
                        WHERE content_tsv @@ websearch_to_tsquery('english', %s)
                        ORDER BY bm25 DESC,
                                 file_path NULLS LAST,
                                 chunk_index NULLS LAST,
                                 id ASC
                        LIMIT %s
                        """,
                        (query, query, limit),
                    )
                    rows = cur.fetchall()

            return {"status": "success", "search_type": "bm25", "results": list(rows)}

        except Exception:
            raise

    @retry_database
    def _search_dense(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
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
            out: List[Dict[str, Any]] = []
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

    def _text_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
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
                            ts_rank(to_tsvector('english', content), {ts_fn}('english', %s)) AS score_sparse
                        FROM document_chunks
                        WHERE to_tsvector('english', content) @@ {ts_fn}('english', %s)
                        ORDER BY score_sparse DESC
                        LIMIT %s
                        """,
                        (query, query, limit),
                    )
                    rows = cur.fetchall()

            out: List[Dict[str, Any]] = []
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
                    }
                )
            return out

        except Exception:
            raise

    # ------------- Store -------------

    @retry_database
    def _store_chunks_with_spans(self, chunks: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store document chunks with embeddings and span information."""
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        doc_id = metadata.get("document_id") or uuid.uuid4().hex

        chunk_rows: List[Tuple] = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            if isinstance(emb, torch.Tensor):
                emb = emb.detach().cpu().numpy()
            emb = emb.astype(np.float32, copy=False)

            # Calculate line numbers for the chunk
            # For now, use chunk index as line numbers (simplified approach)
            line_start = i * 10 + 1  # Approximate line numbers
            line_end = line_start + chunk.count("\n")

            chunk_rows.append((doc_id, i, chunk, emb, line_start, line_end, json.dumps(metadata)))

        return self._insert_with_spans(chunk_rows, metadata, doc_id, len(chunks))

    def _insert_with_spans(
        self,
        chunk_rows: List[Tuple],
        metadata: Dict[str, Any],
        doc_id: str,
        chunk_count: int,
    ) -> Dict[str, Any]:
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
                                document_id,
                                chunk_row[1],
                                chunk_row[2],
                                chunk_row[3],
                                chunk_row[4],
                                chunk_row[5],
                                chunk_row[6],
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
                            )
                        )

                    # Insert with new schema including first-class columns
                    execute_values(
                        cur,
                        """
                        INSERT INTO document_chunks
                             (document_id, chunk_index, file_path, line_start, line_end,
                              content, embedding, is_anchor, anchor_key, metadata)
                        VALUES %s
                        """,
                        updated_chunk_rows_with_schema,
                        template="(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
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

    def _delete_document(self, document_id: str) -> Dict[str, Any]:
        try:
            db_manager = get_database_manager()
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM document_chunks WHERE document_id = %s", (document_id,))
                    cur.execute("DELETE FROM documents WHERE document_id = %s", (document_id,))
            return {"status": "success", "document_id": document_id, "message": "Document and all chunks deleted"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_document_chunks(self, document_id: str) -> Dict[str, Any]:
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

    def get_stats(self) -> Dict[str, Any]:
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

    def get_statistics(self) -> Dict[str, Any]:
        """Alias for get_stats() to align with dashboard API"""
        return self.get_stats()


class VectorStorePipeline(Module):
    """DSPy module for complete vector store pipeline"""

    def __init__(self, db_connection_string: str):
        super().__init__()
        self.vector_store = HybridVectorStore(db_connection_string)

    def forward(self, operation: str, **kwargs) -> Dict[str, Any]:
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
