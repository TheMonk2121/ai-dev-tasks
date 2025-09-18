"""
Advanced Retrieval System Integration

Integrates the sophisticated retrieval components (fusion, prefilter, reranker)
with the existing DSPy RAG system while maintaining compatibility.
"""

#!/usr/bin/env python3

import logging
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
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
from src.retrieval.fusion import weighted_rrf
from src.retrieval.prefilter import RecallFriendlyPrefilter
from src.retrieval.quality_gates import QualityGateValidator
from src.retrieval.reranker import heuristic_rerank

logger = logging.getLogger(__name__)

# Query embedding model singleton
_query_embedder: SentenceTransformer | None = None


def _as_mapping(value: object) -> Mapping[str, Any] | None:
    """Return a mapping view if ``value`` is mapping-like."""
    if isinstance(value, Mapping):
        return cast(Mapping[str, Any], value)
    return None


def _coerce_int(value: object, default: int) -> int:
    """Best-effort conversion of config values to integers."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


def _coerce_float(value: object, default: float) -> float:
    """Best-effort conversion of config values to floats."""
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def _coerce_bool(value: object, default: bool) -> bool:
    """Best-effort conversion of config values to booleans."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return default


@dataclass(frozen=True)
class CandidateLimits:
    """Typed view of candidate selection limits."""

    bm25_limit: int = 100
    vector_limit: int = 100
    final_limit: int = 50
    min_candidates: int = 10

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "CandidateLimits":
        if data is None:
            return cls()
        return cls(
            bm25_limit=_coerce_int(data.get("bm25_limit", 100), 100),
            vector_limit=_coerce_int(data.get("vector_limit", 100), 100),
            final_limit=_coerce_int(data.get("final_limit", 50), 50),
            min_candidates=_coerce_int(data.get("min_candidates", 10), 10),
        )


@dataclass(frozen=True)
class FusionSettings:
    """Typed settings for weighted fusion."""

    k: int = 60
    lambda_lex: float = 0.6
    lambda_sem: float = 0.4

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "FusionSettings":
        if data is None:
            return cls()
        return cls(
            k=_coerce_int(data.get("k", 60), 60),
            lambda_lex=_coerce_float(data.get("lambda_lex", 0.6), 0.6),
            lambda_sem=_coerce_float(data.get("lambda_sem", 0.4), 0.4),
        )


@dataclass(frozen=True)
class RerankSettings:
    """Typed settings for heuristic reranking."""

    enabled: bool = True
    alpha: float = 0.7
    top_m: int = 25

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "RerankSettings":
        if data is None:
            return cls()
        return cls(
            enabled=_coerce_bool(data.get("enabled", True), True),
            alpha=_coerce_float(data.get("alpha", 0.7), 0.7),
            top_m=_coerce_int(data.get("top_m", 25), 25),
        )


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
        self.config_path: str = config_path or "evals/stable_build/config/retrieval.yaml"
        # Local typed alias to avoid Unknown on imported function type
        _creator = cast(
            Callable[[dict[str, Any]], RecallFriendlyPrefilter],
            _prefilter_module.create_prefilter_from_config,
        )
        self.prefilter: RecallFriendlyPrefilter = _creator(self._load_config())
        self.quality_gates: QualityGateValidator | None = None  # Will be initialized when needed

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml

            with open(self.config_path) as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ValueError("Config file did not contain a mapping")
                return cast(dict[str, Any], data)
        except Exception as e:
            logger.warning(f"Failed to load config from {self.config_path}: {e}")
            # Return default config
            return {
                "candidates": {
                    "bm25_limit": 100,
                    "vector_limit": 100,
                    "final_limit": 50,
                    "min_candidates": 10,
                },
                "fusion": {"k": 60, "lambda_lex": 0.6, "lambda_sem": 0.4},
                "prefilter": {
                    "min_bm25_score": 0.1,
                    "min_vector_score": 0.7,
                    "min_doc_length": 50,
                    "max_doc_length": 8000,
                    "enable_diversity": True,
                    "diversity_threshold": 0.9,
                },
                "rerank": {"enabled": True, "alpha": 0.7, "top_m": 25},
            }

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
        fusion_settings = FusionSettings.from_mapping(_as_mapping(config.get("fusion")))
        rerank_settings = RerankSettings.from_mapping(_as_mapping(config.get("rerank")))

        # Load weights
        if weights is None:
            weights = load_weights(tag, weights_file)

        # Get candidate limits
        candidates_limits = CandidateLimits.from_mapping(_as_mapping(config.get("candidates")))
        bm25_limit = candidates_limits.bm25_limit
        vector_limit = candidates_limits.vector_limit

        try:
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
                    bm25_scores: list[tuple[str, float]] = [(row[0], float(row[5])) for row in bm25_results]
                    vector_scores: list[tuple[str, float]] = [(row[0], float(row[5])) for row in vector_results]

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
                            top_m=rerank_settings.top_m,
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
                                        cur.execute(
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
                                    "chunk_index": row[0],
                                    "filename": row[1],
                                    "content": row[2],
                                    "metadata": row[3],
                                    "score": score,
                                    "file_path": row[4],
                                    "path_tsv": row[5],
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
    ) -> list[tuple[str, str, str, dict[str, Any], str, Any]]:
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
    ) -> list[tuple[str, str, str, dict[str, Any], str, Any]]:
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
