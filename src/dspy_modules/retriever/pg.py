#!/usr/bin/env python3
"""
PostgreSQL query execution for fused retrieval with multiplicative prior.
Implements the surgical patch SQL query.
"""

import logging
import os
from typing import Any

import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

from .rerank import mmr_rerank
from .weights import load_weights


def get_db_connection():
    """Get database connection from environment or default."""
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    # Handle mock DSN for testing
    if dsn.startswith("mock://"):
        dsn = "postgresql://danieljacobs@localhost:5432/ai_agency"
    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)


def fetch_doc_chunks_by_slug(doc_slug: str, limit: int = 12) -> list[dict[str, Any]]:
    """Prefetch top chunks from a specific document identified by slug.

    The slug should be like '400_12_advanced-configurations'.
    Returns rows compatible with fused results (including text_for_reader, score).
    """
    if not doc_slug:
        return []
    sql = """
    SELECT
      dc.chunk_id,
      dc.filename,
      d.file_path,
      dc.embedding,
      dc.embedding_text,
      COALESCE(dc.embedding_text, dc.bm25_text, dc.content) AS text_for_reader,
      dc.metadata AS metadata,
      dc.metadata->>'ingest_run_id' AS ingest_run_id,
      dc.metadata->>'chunk_variant' AS chunk_variant,
      100.0::float AS score
    FROM document_chunks dc
    LEFT JOIN documents d ON d.id = dc.document_id
    WHERE lower(replace(coalesce(dc.filename,''), '.md','')) = %(slug)s
       OR d.file_path ILIKE '%%' || %(slug)s || '%%'
    ORDER BY dc.chunk_id
    LIMIT %(limit)s
    """
    params = {"slug": doc_slug.lower(), "limit": int(limit)}
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]
            # Normalize metadata to ensure provenance presence
            for r in rows:
                md = dict(r.get("metadata") or {})
                if r.get("ingest_run_id") and not md.get("ingest_run_id"):
                    md["ingest_run_id"] = r["ingest_run_id"]
                if r.get("chunk_variant") and not md.get("chunk_variant"):
                    md["chunk_variant"] = r["chunk_variant"]
                md.setdefault("ingest_run_id", "legacy")
                md.setdefault("chunk_variant", "legacy")
                r["metadata"] = md
            return rows


def _vec_expr() -> str:
    ops = (os.getenv("PGVECTOR_OPS", "cosine") or "cosine").lower()
    if ops == "l2":
        return "1.0 / (1.0 + (b.embedding <=> %(qvec)s::vector))"
    if ops == "ip":
        return "- (b.embedding <=> %(qvec)s::vector)"
    return "1.0 - (b.embedding <=> %(qvec)s::vector)"


def run_fused_query(
    q_short: str,
    q_title: str,
    q_bm25: str,
    qvec: list[float],
    k: int = 25,
    use_mmr: bool = True,
    tag: str = "",
    weights: dict[str, float] | None = None,
    weights_file: str | None = None,
    return_components: bool = True,  # noqa: ARG001
    fname_regex: str | None = None,
    adjacency_db: bool = False,
    cold_start: bool = False,
) -> list[dict[str, Any]]:
    """
    Run the fused SQL query with multiplicative prior weight.

    Args:
        q_short: Query for short channel (with hints)
        q_title: Query for title channel (with hints)
        q_bm25: Query for BM25 channel (raw, no hints)
        qvec: Vector embedding for similarity search
        k: Number of results to return
        use_mmr: Whether to apply MMR reranking
        weights: Optional weight dictionary for channels
        return_components: Reserved for future use (API compatibility)

    Returns:
        List of result dictionaries
    """

    VEC = _vec_expr()

    # Acknowledge return_components parameter for API compatibility
    _ = return_components

    # Sanitize inputs to avoid postgres/driver issues (e.g., NUL 0x00)
    def _clean(s: str) -> str:
        # Replace NULs and collapse excessive whitespace
        s = s.replace("\x00", " ")
        return s

    q_short = _clean(q_short)
    q_title = _clean(q_title)
    q_bm25 = _clean(q_bm25)
    short_tsq = (
        "(websearch_to_tsquery('simple', %(q_short)s) || to_tsquery('simple', 'create <-> index') || to_tsquery('simple', 'alter <-> table'))"
        if (tag == "db_workflows" and adjacency_db)
        else "websearch_to_tsquery('simple', %(q_short)s)"
    )
    sql = f"""
    WITH
    q AS (
      SELECT
        CASE WHEN %(q_short)s <> '' THEN {short_tsq} END  AS tsq_short,
        CASE WHEN %(q_title)s <> '' THEN websearch_to_tsquery('simple', %(q_title)s) END  AS tsq_title,
        CASE WHEN %(q_bm25)s <> '' THEN websearch_to_tsquery('simple', %(q_bm25)s) END  AS tsq_bm25
    ),
    base AS (
      SELECT
        dc.chunk_id,
        dc.filename,
        dc.short_tsv,
        dc.title_tsv,
        dc.content_tsv,
        dc.embedding,
        dc.embedding_text,
        dc.bm25_text,
        dc.metadata AS metadata,
        dc.metadata->>'ingest_run_id' AS ingest_run_id,
        dc.metadata->>'chunk_variant' AS chunk_variant,
        d.file_path,
        d.path_tsv
      FROM document_chunks dc
      LEFT JOIN documents d ON d.id = dc.document_id
    )
    SELECT
      b.chunk_id,
      b.filename,
      b.metadata,
      b.ingest_run_id,
      b.chunk_variant,
      b.file_path,
      b.embedding,
      b.embedding_text,
      COALESCE(b.embedding_text, b.bm25_text) AS text_for_reader,

      -- Switch to ts_rank with normalization=32 to penalize long docs.
      COALESCE(%(w_path)s * ts_rank(b.path_tsv,  q.tsq_short, 32), 0.0)   AS s_path,
      COALESCE(%(w_short)s * ts_rank(b.short_tsv, q.tsq_short, 32), 0.0)  AS s_short,
      COALESCE(%(w_title)s * ts_rank(b.title_tsv, q.tsq_title, 32), 0.0)  AS s_title,
      COALESCE(%(w_bm25)s * ts_rank(b.content_tsv, q.tsq_bm25, 32), 0.0)  AS s_bm25,
      COALESCE(%(w_vec)s * (CASE WHEN %(has_vec)s THEN {VEC} ELSE 0.0 END), 0.0) AS s_vec,

      (
        (CASE
           WHEN b.filename ~* '\\.(sql|sh|bash|zsh|py|ipynb|yaml|yml|toml|ini|env|dockerfile)$' THEN 0.25
           WHEN b.embedding_text ~ '```' THEN 0.15
           WHEN b.embedding_text ~ '(?i)\\b(CREATE|ALTER)\\s+(INDEX|TABLE)\\b' THEN 0.20
           ELSE 0.0
         END
         - CASE
            WHEN lower(b.filename) ~ '(readme|notes|journal|diary|thoughts)' THEN 0.20
            ELSE 0.0
          END
         + CASE WHEN %(fname_regex)s <> '^$' AND lower(b.filename) ~ %(fname_regex)s THEN 0.05 ELSE 0.0 END
         + CASE WHEN %(tag)s = 'db_workflows' AND lower(b.file_path) ~ '(^|/)(db|database|migrations?|sql)(/|$)' THEN 0.03 ELSE 0.0 END
         + CASE WHEN %(tag)s = 'ops_health' AND lower(b.file_path) ~ '(^|/)(ops|scripts|shell|setup)(/|$)' THEN 0.03 ELSE 0.0 END
         + CASE
            WHEN lower(b.file_path) ~ '(^|/)(docs?|designs?)(/|$)' THEN 0.05
            ELSE 0.0
          END
         + CASE
            WHEN lower(b.file_path) ~ 'dspy_modules/retriever/' THEN 0.03
            ELSE 0.0
          END
        ) / 10.0
      ) AS prior_scaled,

      (
        COALESCE(%(w_path)s * ts_rank(b.path_tsv,  q.tsq_short, 32), 0.0)
      + COALESCE(%(w_short)s * ts_rank(b.short_tsv, q.tsq_short, 32), 0.0)
      + COALESCE(%(w_title)s * ts_rank(b.title_tsv, q.tsq_title, 32), 0.0)
      + COALESCE(%(w_bm25)s * ts_rank(b.content_tsv, q.tsq_bm25, 32), 0.0)
      + (CASE WHEN %(has_vec)s THEN %(w_vec)s * ({VEC}) ELSE 0.0 END)
      )
      * LEAST(GREATEST(1.0 + (
          (CASE
             WHEN b.filename ~* '\\.(sql|sh|bash|zsh|py|ipynb|yaml|yml|toml|ini|env|dockerfile)$' THEN 0.25
             WHEN b.embedding_text ~ '```' THEN 0.15
             WHEN b.embedding_text ~ '(?i)\\b(CREATE|ALTER)\\s+(INDEX|TABLE)\\b' THEN 0.20
             ELSE 0.0
           END
           - CASE
               WHEN lower(b.filename) ~ '(readme|notes|journal|diary|thoughts)' THEN 0.20
               ELSE 0.0
             END
        ) / 10.0), 0.95), 1.05)     -- clamp: ±5 percent max
      AS score

    FROM base b, q
    ORDER BY score DESC NULLS LAST
    LIMIT %(limit)s;
    """

    # Use larger pool for MMR reranking
    pool_size = 60 if use_mmr else k

    # Default or YAML-derived weights if not provided
    if weights is None:
        weights = load_weights(tag=tag, file_path=weights_file)

    # Cold-start boost: increase w_vec when query is lexically sparse
    if cold_start:
        boost = float(os.getenv("COLD_START_WVEC_BOOST", "0.10"))
        weights["w_vec"] = weights["w_vec"] * (1.0 + boost)

    # Format query vector as pgvector literal to avoid adapter issues
    if isinstance(qvec, np.ndarray):
        has_vec = qvec.size > 0
    else:
        has_vec = bool(qvec) and len(qvec) > 0
    if not has_vec:
        try:
            dim = int(os.getenv("EMBED_DIM", "384"))
        except Exception:
            dim = 384
        qvec = [0.0] * dim
    qvec_literal = "[" + ",".join(f"{float(x):.6f}" for x in qvec) + "]"

    # Named parameters for stability
    params = {
        "q_short": q_short,
        "q_title": q_title,
        "q_bm25": q_bm25,
        "w_path": weights["w_path"],
        "w_short": weights["w_short"],
        "w_title": weights["w_title"],
        "w_bm25": weights["w_bm25"],
        "w_vec": weights["w_vec"],
        "qvec": qvec_literal,
        "has_vec": has_vec,
        "fname_regex": fname_regex or "^$",
        "tag": tag or "",
        "limit": pool_size,
    }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql, params)
                rows = [dict(row) for row in cur.fetchall()]
            except Exception as e:
                if "path_tsv" in str(e).lower():
                    # Fallback: compute path_tsv on the fly
                    fallback_sql = f"""
                    WITH
                    q AS (
                      SELECT
                        CASE WHEN %(q_short)s <> '' THEN {short_tsq} END  AS tsq_short,
                        CASE WHEN %(q_title)s <> '' THEN websearch_to_tsquery('simple', %(q_title)s) END  AS tsq_title,
                        CASE WHEN %(q_bm25)s <> '' THEN websearch_to_tsquery('simple', %(q_bm25)s) END  AS tsq_bm25
                    ),
                    base AS (
                      SELECT
                        dc.chunk_id,
                        dc.filename,
                        dc.short_tsv,
                        dc.title_tsv,
                        dc.content_tsv,
                        dc.embedding,
                        dc.embedding_text,
                        dc.bm25_text,
                        d.file_path,
                        to_tsvector('simple', replace(replace(coalesce(d.file_path,''), '/', ' '), '_', ' ')) AS path_tsv
                      FROM document_chunks dc
                      LEFT JOIN documents d ON d.id = dc.document_id
                    )
                    SELECT
                      b.chunk_id,
                      b.filename,
                      b.file_path,
                      b.embedding,
                      b.embedding_text,
                      COALESCE(b.embedding_text, b.bm25_text) AS text_for_reader,

                      COALESCE(%(w_path)s * ts_rank(b.path_tsv,  q.tsq_short, 32), 0.0)   AS s_path,
                      COALESCE(%(w_short)s * ts_rank(b.short_tsv, q.tsq_short, 32), 0.0)  AS s_short,
                      COALESCE(%(w_title)s * ts_rank(b.title_tsv, q.tsq_title, 32), 0.0)  AS s_title,
                      COALESCE(%(w_bm25)s * ts_rank(b.content_tsv, q.tsq_bm25, 32), 0.0)  AS s_bm25,
                      COALESCE(%(w_vec)s * (CASE WHEN %(has_vec)s THEN {VEC} ELSE 0.0 END), 0.0) AS s_vec,

                      (
                        (CASE
                           WHEN b.filename ~* '\\.(sql|sh|bash|zsh|py|ipynb|yaml|yml|toml|ini|env|dockerfile)$' THEN 0.25
                           WHEN b.embedding_text ~ '```' THEN 0.15
                           WHEN b.embedding_text ~ '(?i)\\b(CREATE|ALTER)\\s+(INDEX|TABLE)\\b' THEN 0.20
                           ELSE 0.0
                         END
                         - CASE
                             WHEN lower(b.filename) ~ '(readme|notes|journal|diary|thoughts)' THEN 0.20
                             ELSE 0.0
                           END
                         + CASE WHEN %(fname_regex)s <> '^$' AND lower(b.filename) ~ %(fname_regex)s THEN 0.05 ELSE 0.0 END
                         + CASE WHEN %(tag)s = 'db_workflows' AND lower(b.file_path) ~ '(^|/)(db|database|migrations?|sql)(/|$)' THEN 0.03 ELSE 0.0 END
                         + CASE WHEN %(tag)s = 'ops_health' AND lower(b.file_path) ~ '(^|/)(ops|scripts|shell|setup)(/|$)' THEN 0.03 ELSE 0.0 END
                         + CASE
                             WHEN lower(b.file_path) ~ '(^|/)(docs?|designs?)(/|$)' THEN 0.05
                             ELSE 0.0
                           END
                         + CASE
                             WHEN lower(b.file_path) ~ 'dspy_modules/retriever/' THEN 0.03
                             ELSE 0.0
                           END
                        ) / 10.0
                      ) AS prior_scaled,

                      (
                        COALESCE(%(w_path)s * ts_rank(b.path_tsv,  q.tsq_short, 32), 0.0)
                      + COALESCE(%(w_short)s * ts_rank(b.short_tsv, q.tsq_short, 32), 0.0)
                      + COALESCE(%(w_title)s * ts_rank(b.title_tsv, q.tsq_title, 32), 0.0)
                      + COALESCE(%(w_bm25)s * ts_rank(b.content_tsv, q.tsq_bm25, 32), 0.0)
                      + (CASE WHEN %(has_vec)s THEN %(w_vec)s * ({VEC}) ELSE 0.0 END)
                      )
                      * LEAST(GREATEST(1.0 + (
                          (CASE
                             WHEN b.filename ~* '\\.(sql|sh|bash|zsh|py|ipynb|yaml|yml|toml|ini|env|dockerfile)$' THEN 0.25
                             WHEN b.embedding_text ~ '```' THEN 0.15
                             WHEN b.embedding_text ~ '(?i)\\b(CREATE|ALTER)\\s+(INDEX|TABLE)\\b' THEN 0.20
                             ELSE 0.0
                           END
                           - CASE
                               WHEN lower(b.filename) ~ '(readme|notes|journal|diary|thoughts)' THEN 0.20
                               ELSE 0.0
                             END
                        ) / 10.0), 0.95), 1.05)
                      AS score

                    FROM base b, q
                    ORDER BY score DESC NULLS LAST
                    LIMIT %(limit)s;
                    """
                    # Open a fresh transaction for fallback
                    cur.close()
                    conn.rollback()
                    with get_db_connection() as conn2:
                        with conn2.cursor() as cur2:
                            cur2.execute(fallback_sql, params)
                            rows = [dict(row) for row in cur2.fetchall()]
                else:
                    raise

    # Apply learned fusion head if enabled
    enabled = os.getenv("FUSION_HEAD_ENABLE", "0") == "1"
    ckpt = os.getenv("FUSION_HEAD_PATH", "")
    spec_path = os.getenv("FUSION_FEATURE_SPEC", "configs/feature_spec_v1.json")
    hidden = int(os.getenv("FUSION_HIDDEN", "0"))
    device = os.getenv("FUSION_DEVICE", "cpu")

    if enabled and ckpt and os.path.exists(ckpt):
        try:
            from .fusion_head import load_feature_spec, load_head, score_rows

            feature_names = load_feature_spec(spec_path)
            head = load_head(ckpt, in_dim=len(feature_names), hidden=hidden, device=device)
            rows = score_rows(rows, feature_names, head, device=device)

            # Replace fusion score with learned score
            for row in rows:
                row["score"] = row.get("score_learned", row.get("score", 0.0))

            # Sort by learned score and truncate to k
            rows = sorted(rows, key=lambda x: x["score"], reverse=True)[:k]

        except Exception as e:
            # Log error but continue with original behavior
            logger = logging.getLogger(__name__)
            logger.warning(f"Fusion head failed, falling back to original scoring: {e}")

    # Apply MMR reranking if requested (only if fusion head not used)
    if use_mmr and len(rows) > k and not (enabled and ckpt and os.path.exists(ckpt)):
        return mmr_rerank(rows, k=k)

    return rows[:k]


def gold_hit(case_id: str, retrieved_rows: list[dict[str, Any]]) -> bool:
    """
    Check if any of the retrieved chunks match the gold standard for a case.

    Args:
        case_id: Evaluation case ID
        retrieved_rows: List of retrieved result dictionaries

    Returns:
        True if any chunk matches gold standard
    """
    from ..evals.gold import gold_hit as real_gold_hit

    return real_gold_hit(case_id, retrieved_rows)
