#!/usr/bin/env python3
"""
PostgreSQL query execution for fused retrieval with multiplicative prior.
Implements the surgical patch SQL query.
"""

import os
from typing import Any, Dict, List, Optional

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
    qvec: List[float],
    k: int = 25,
    use_mmr: bool = True,
    tag: str = "",
    weights: Optional[Dict[str, float]] = None,
    weights_file: Optional[str] = None,
    return_components: bool = True,
    fname_regex: Optional[str] = None,
    adjacency_db: bool = False,
    cold_start: bool = False,
) -> List[Dict[str, Any]]:
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

    Returns:
        List of result dictionaries
    """

    VEC = _vec_expr()
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
        d.file_path,
        d.path_tsv
      FROM document_chunks dc
      LEFT JOIN documents d ON d.id = dc.document_id
    )
    SELECT
      b.chunk_id,
      b.filename,
      b.file_path,
      b.embedding,

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
    has_vec = bool(qvec)
    if not qvec:
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

    # Apply MMR reranking if requested
    if use_mmr and len(rows) > k:
        return mmr_rerank(rows, k=k)

    return rows[:k]


def gold_hit(case_id: str, retrieved_rows: List[Dict[str, Any]]) -> bool:
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
