"""
Advanced Retrieval System Integration

Integrates the sophisticated retrieval components (fusion, prefilter, reranker)
with the existing DSPy RAG system while maintaining compatibility.
"""

#!/usr/bin/env python3

import logging
import os
from collections.abc import Callable
from typing import Any, cast

import numpy as np
import psycopg
from numpy.typing import NDArray
from psycopg import Connection, Cursor
from psycopg.rows import DictRow, TupleRow, dict_row
from sentence_transformers import SentenceTransformer

# Import existing components for compatibility
from common.embedding_validation import assert_embedding_dim
from dspy_modules.retriever.weights import load_weights
from src.retrieval import prefilter as _prefilter_module
from src.retrieval.config_loader import (
    CandidateLimits,
    FusionSettings,
    RerankSettings,
    get_candidate_limits,
    get_fusion_settings,
    get_rerank_settings,
    load_retrieval_config,
    resolve_config_path,
)
from src.retrieval.fusion import weighted_rrf
from src.retrieval.prefilter import RecallFriendlyPrefilter
from src.retrieval.quality_gates import QualityGateValidator
from src.retrieval.reranker import heuristic_rerank

logger = logging.getLogger(__name__)

# Query embedding model singleton
_query_embedder: SentenceTransformer | None = None


def _get_query_embedder() -> SentenceTransformer:
    """Get or create the query embedding model."""
    global _query_embedder
    if _query_embedder is None:
        _query_embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
        _query_embedder.max_seq_length = 512
    return _query_embedder


def _generate_query_embedding(query: str) -> list[float]:
    """Generate embedding for a query string with BGE query prefix."""
    if not query or not query.strip():
        return []

    # Add BGE query prefix for better retrieval
    prefixed_query = f"Represent this sentence for searching relevant passages: {query}"

    try:
        embedder = _get_query_embedder()
        # Force numpy return to ensure stable typing for .tolist()
        embedding_obj = embedder.encode(
            prefixed_query,
            normalize_embeddings=True,
            convert_to_numpy=True,
            convert_to_tensor=False,
            output_value="sentence_embedding",
        )
        embedding = cast(NDArray[np.float32], embedding_obj)
        return cast(list[float], embedding.tolist())
    except Exception as e:
        logger.warning(f"Failed to generate query embedding: {e}")
        return []


def get_db_connection() -> Connection[TupleRow]:
    """Get database connection from environment or default."""
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

    # Strictly fail if DSN is a mock or empty
    if not dsn or dsn.startswith("mock://"):
        raise RuntimeError(
            f"Invalid DSN detected: {dsn}. MUST use a real PostgreSQL connection string. Set POSTGRES_DSN to a valid connection string. Recommended: Use evals/configs/profiles/real.env for real database connection."
        )

    conn: Connection[TupleRow] = psycopg.connect(dsn)
    return conn


class AdvancedRetriever:
    """Advanced retrieval system with sophisticated fusion, prefiltering, and reranking."""

    def __init__(self, config_path: str | None = None):
        """Initialize the advanced retriever with configuration."""
        resolved = resolve_config_path(config_path)
        self.config_path: str = str(resolved)
        self._config_cache: dict[str, Any] | None = None
        # Local typed alias to avoid Unknown on imported function type
        _creator = cast(
            Callable[[dict[str, Any]], RecallFriendlyPrefilter],
            _prefilter_module.create_prefilter_from_config,
        )
        self.prefilter: RecallFriendlyPrefilter = _creator(self._load_config())
        self.quality_gates: QualityGateValidator | None = None  # Will be initialized when needed

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if self._config_cache is None:
            self._config_cache = load_retrieval_config(self.config_path)
        return dict(self._config_cache)

    def fetch_doc_chunks_by_slug(self, doc_slug: str, limit: int = 12) -> list[dict[str, object]]:
        """Prefetch top chunks from a specific document identified by slug."""
        if not doc_slug:
            return []

        sql = """
        SELECT
          dc.chunk_index,
          d.file_name AS filename,
          d.file_path,
          dc.embedding,
          dc.content,
          dc.metadata,
          dc.metadata->>'ingest_run_id' AS ingest_run_id,
          dc.metadata->>'chunk_variant' AS chunk_variant,
          d.path_tsv
        FROM document_chunks dc
        LEFT JOIN documents d ON d.id = dc.document_id
        WHERE d.file_name ILIKE %s
        ORDER BY dc.chunk_index
        LIMIT %s
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    _ = cur.execute(sql, (f"%{doc_slug}%", limit))
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch chunks by slug {doc_slug}: {e}")
            return []

    def run_advanced_query(
        self,
        q_short: str,
        q_title: str,
        q_bm25: str,
        qvec: list[float],
        k: int = 25,
        tag: str = "",
        weights: dict[str, float] | None = None,
        weights_file: str | None = None,
        return_components: bool = False,
    ) -> list[dict[str, object]]:
        """Run advanced retrieval query with fusion, prefiltering, and reranking."""

        # Load configuration
        config = self._load_config()
        fusion_settings = get_fusion_settings(config)
        rerank_settings = get_rerank_settings(config)

        # Mark intentionally unused params to satisfy linters without changing behavior
        _ = (k, return_components)

        # Load weights
        if weights is None:
            weights = load_weights(tag, weights_file)

        # Get candidate limits
        candidates_limits = get_candidate_limits(config)
        bm25_limit = candidates_limits.bm25_limit
        vector_limit = candidates_limits.vector_limit

        try:
            # If no embedding provided, generate one from available query text
            if not qvec:
                seed_query = q_short or q_title or q_bm25 or ""
                qvec = _generate_query_embedding(seed_query)

            with get_db_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    # Run BM25 query
                    bm25_results = self._run_bm25_query(cur, q_bm25, bm25_limit)

                    # Run vector query
                    vector_results = self._run_vector_query(cur, qvec, vector_limit)

                    # Extract documents for prefiltering
                    all_docs: dict[str, str] = {}
                    for row in bm25_results + vector_results:
                        doc_id = row[0]
                        content = row[2]
                        all_docs[doc_id] = content

                    # Convert results to (doc_id, score) format for fusion
                    # row[6] is the score (rank/similarity), row[5] is path_tsv
                    bm25_scores: list[tuple[str, float]] = [(row[0], float(row[6])) for row in bm25_results]
                    vector_scores: list[tuple[str, float]] = [(row[0], float(row[6])) for row in vector_results]

                    # Apply prefiltering
                    filtered_bm25, filtered_vector = self.prefilter.prefilter_all(bm25_scores, vector_scores, all_docs)

                    # Apply fusion
                    fused_results = weighted_rrf(
                        filtered_bm25,
                        filtered_vector,
                        k=fusion_settings.k,
                        lambda_lex=fusion_settings.lambda_lex,
                        lambda_sem=fusion_settings.lambda_sem,
                        limit=candidates_limits.final_limit,
                    )

                    # Apply reranking if enabled
                    if rerank_settings.enabled:
                        query_text = q_short or q_title or q_bm25 or ""
                        fused_results = heuristic_rerank(
                            query_text,
                            fused_results,
                            all_docs,
                            alpha=rerank_settings.alpha,
                            top_m=rerank_settings.final_top_n if rerank_settings.final_top_n > 0 else None,
                        )

                    # Convert to expected format
                    results: list[dict[str, object]] = []
                    for doc_id, score in fused_results:
                        # Find the original row data
                        original_row = None
                        for row in bm25_results + vector_results:
                            if row[0] == doc_id:
                                original_row = row
                                break

                        if original_row:
                            # Get embedding from database for this chunk
                            embedding: list[float] | None = None
                            try:
                                with get_db_connection() as conn:
                                    with conn.cursor(row_factory=dict_row) as cur:
                                        _ = cur.execute(
                                            "SELECT embedding FROM document_chunks WHERE chunk_index = %s",
                                            (doc_id,),
                                        )
                                        result_row = cur.fetchone()
                                        if result_row and "embedding" in result_row:
                                            embedding = cast(list[float], result_row["embedding"])  # type: ignore[assignment]
                            except Exception:
                                pass  # Continue without embedding if query fails

                            results.append(
                                {
                                    "chunk_index": original_row[0],
                                    "filename": original_row[1],
                                    "content": original_row[2],
                                    "metadata": original_row[3],
                                    "score": score,
                                    "file_path": original_row[4],
                                    "path_tsv": original_row[5],
                                    "embedding": embedding,
                                }
                            )

                    return results

        except Exception as e:
            logger.error(f"Advanced query failed: {e}")
            return []

    def _run_bm25_query(
        self,
        cur: Cursor[DictRow],
        q_bm25: str,
        limit: int,
    ) -> list[tuple[str, str, str, dict[str, Any], str, Any, float]]:
        """Run BM25 query and return results."""
        if not q_bm25:
            return []

        # Use plainto_tsquery for more flexible matching
        sql = """
        SELECT
          dc.chunk_index::text,
          d.file_name,
          dc.content,
          dc.metadata,
          d.file_path,
          d.path_tsv,
          ts_rank(dc.content_tsv, plainto_tsquery('simple', %s)) AS rank
        FROM document_chunks dc
        LEFT JOIN documents d ON d.id = dc.document_id
        WHERE dc.content_tsv @@ plainto_tsquery('simple', %s)
        ORDER BY ts_rank(dc.content_tsv, plainto_tsquery('simple', %s)) DESC
        LIMIT %s
        """

        _ = cur.execute(sql, (q_bm25, q_bm25, q_bm25, limit))
        rows = cur.fetchall()
        return [
            (
                str(row["chunk_index"]),
                row["file_name"],
                row["content"],
                row["metadata"],
                row["file_path"],
                row["path_tsv"],
                row["rank"],
            )
            for row in rows
        ]

    def _run_vector_query(
        self,
        cur: Cursor[DictRow],
        qvec: list[float],
        limit: int,
    ) -> list[tuple[str, str, str, dict[str, Any], str, Any, float]]:
        """Run vector similarity query and return results."""
        if not qvec:
            return []

        # Validate embedding dimension
        try:
            dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
            assert_embedding_dim(dsn, expected_dim=384)
        except Exception as e:
            logger.warning(f"Embedding dimension issue: {e}")
            return []

        # Convert list to string representation for PostgreSQL vector
        qvec_str = "[" + ",".join(map(str, qvec)) + "]"

        sql = """
        SELECT
          dc.chunk_index::text,
          d.file_name,
          dc.content,
          dc.metadata,
          d.file_path,
          d.path_tsv,
          1 - (dc.embedding <=> %s::vector) AS similarity
        FROM document_chunks dc
        LEFT JOIN documents d ON d.id = dc.document_id
        WHERE dc.embedding IS NOT NULL
        ORDER BY dc.embedding <=> %s::vector
        LIMIT %s
        """

        _ = cur.execute(sql, (qvec_str, qvec_str, limit))
        rows = cur.fetchall()
        return [
            (
                str(row["chunk_index"]),
                row["file_name"],
                row["content"],
                row["metadata"],
                row["file_path"],
                row["path_tsv"],
                row["similarity"],
            )
            for row in rows
        ]


# Compatibility functions for existing DSPy integration
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
    return_components: bool = False,
) -> list[dict[str, Any]]:
    """
    Compatibility function that maintains the same interface as the old run_fused_query.
    This allows the DSPy system to use the new advanced retrieval without changes.
    """
    # preserve signature; mark parameter as intentionally unused
    _ = use_mmr
    retriever = AdvancedRetriever()
    return retriever.run_advanced_query(
        q_short=q_short,
        q_title=q_title,
        q_bm25=q_bm25,
        qvec=qvec,
        k=k,
        tag=tag,
        weights=weights,
        weights_file=weights_file,
        return_components=return_components,
    )


def fetch_doc_chunks_by_slug(doc_slug: str, limit: int = 12) -> list[dict[str, Any]]:
    """
    Compatibility function for slug-based document fetching.
    """
    retriever = AdvancedRetriever()
    return retriever.fetch_doc_chunks_by_slug(doc_slug, limit)
