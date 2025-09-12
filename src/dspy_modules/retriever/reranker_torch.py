from __future__ import annotations
import hashlib
import logging
import os
import sqlite3
from typing import Any
    from src.rag import reranker_env as RENV  # SSOT env shim
            import sentence_transformers
            import torch
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Minimal cross-encoder reranker for inference-only PyTorch integration.
Implements the surgical approach: pre-trained models, cached scores, deterministic results.
"""


try:
except Exception:
    RENV = None  # Fallback if path not available; direct envs will be used

logger = logging.getLogger(__name__)

# Lazy imports to avoid dependency issues
_sentence_transformers = None
_torch = None


def _get_sentence_transformers():
    """Lazy import of sentence_transformers"""
    global _sentence_transformers
    if _sentence_transformers is None:
        try:

            _sentence_transformers = sentence_transformers
        except ImportError:
            logger.warning("sentence_transformers not available, reranker disabled")
            return None
    return _sentence_transformers


def _get_torch():
    """Lazy import of torch"""
    global _torch
    if _torch is None:
        try:

            _torch = torch
        except ImportError:
            logger.warning("torch not available, reranker disabled")
            return None
    return _torch


def _device():
    """Determine the best available device for inference"""
    device = RENV.TORCH_DEVICE if RENV else os.getenv("TORCH_DEVICE", "cpu")

    if device == "mps":  # Apple Silicon
        torch = _get_torch()
        if torch and torch.backends.mps.is_available():
            return "mps"
        logger.warning("MPS requested but not available, falling back to CPU")
        return "cpu"
    elif device == "cuda":
        torch = _get_torch()
        if torch and torch.cuda.is_available():
            return "cuda"
        logger.warning("CUDA requested but not available, falling back to CPU")
        return "cpu"

    return device


# Global model cache
_MODEL = None
_MODEL_NAME = None


def _model():
    """Get or create the cross-encoder model"""
    global _MODEL, _MODEL_NAME

    model_name = RENV.RERANKER_MODEL if RENV else os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

    # Return cached model if name hasn't changed
    if _MODEL is not None and _MODEL_NAME == model_name:
        return _MODEL

    # Clean up old model if name changed
    if _MODEL is not None and _MODEL_NAME != model_name:
        del _MODEL
        _MODEL = None

    sentence_transformers = _get_sentence_transformers()
    if sentence_transformers is None:
        return None

    try:
        device = _device()
        logger.info(f"Loading reranker model '{model_name}' on device '{device}'")
        _MODEL = sentence_transformers.CrossEncoder(model_name, device=device)
        _MODEL_NAME = model_name
        return _MODEL
    except Exception as e:
        logger.error(f"Failed to load reranker model '{model_name}': {e}")
        return None


def _get_cache_db():
    """Get or create the SQLite cache database"""
    cache_dir = (
        RENV.RERANK_CACHE_PATH
        if (RENV and RENV.RERANK_CACHE_BACKEND == "sqlite")
        else os.getenv("RERANKER_CACHE_DIR", "cache")
    )
    # Backwards-compat for existing layout: RERANKER_CACHE_DIR expects a directory
    if cache_dir and cache_dir.endswith(".sqlite"):
        # user provided a full sqlite path; derive directory
        cache_dir_parent = os.path.dirname(cache_dir)
        os.makedirs(cache_dir_parent or ".", exist_ok=True)
        db_path = cache_dir
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reranker_scores (
                model_name TEXT,
                query_hash TEXT,
                chunk_id TEXT,
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (model_name, query_hash, chunk_id)
            )
            """
        )
        return conn
    os.makedirs(cache_dir, exist_ok=True)

    db_path = os.path.join(cache_dir, "reranker_scores.db")
    conn = sqlite3.connect(db_path)

    # Create table if it doesn't exist
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reranker_scores (
            model_name TEXT,
            query_hash TEXT,
            chunk_id TEXT,
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (model_name, query_hash, chunk_id)
        )
    """
    )

    return conn


def _query_hash(query: str) -> str:
    """Create a deterministic hash for the query"""
    return hashlib.md5(query.encode("utf-8")).hexdigest()


def _get_cached_scores(model_name: str, query_hash: str, chunk_ids: list[str]) -> dict[str, float]:
    """Get cached scores for the given query and chunks"""
    conn = _get_cache_db()
    try:
        placeholders = ",".join(["?" for _ in chunk_ids])
        cursor = conn.execute(
            f"SELECT chunk_id, score FROM reranker_scores WHERE model_name = ? AND query_hash = ? AND chunk_id IN ({placeholders})",
            [model_name, query_hash] + chunk_ids,
        )
        return {row[0]: row[1] for row in cursor.fetchall()}
    finally:
        conn.close()


def _cache_scores(model_name: str, query_hash: str, scores: dict[str, float]):
    """Cache scores for the given query and chunks"""
    conn = _get_cache_db()
    try:
        data = [(model_name, query_hash, chunk_id, score) for chunk_id, score in scores.items()]
        conn.executemany(
            "INSERT OR REPLACE INTO reranker_scores (model_name, query_hash, chunk_id, score) VALUES (?, ?, ?, ?)", data
        )
        conn.commit()
    finally:
        conn.close()


def rerank(
    query: str, candidates: list[tuple[str, str]], topk_keep: int = 12, batch_size: int = 8
) -> list[tuple[str, str, float]]:
    """
    Rerank candidates using a cross-encoder model.

    Args:
        query: The search query
        candidates: List of (chunk_id, text) tuples
        topk_keep: Number of top results to return
        batch_size: Batch size for model inference

    Returns:
        List of (chunk_id, text, score) tuples sorted by score descending
    """
    if not candidates:
        return []

    model = _model()
    if model is None:
        logger.warning("Reranker model not available, returning candidates unchanged")
        return [(cid, txt, 0.0) for cid, txt in candidates[:topk_keep]]

    model_name = RENV.RERANKER_MODEL if RENV else os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    query_hash = _query_hash(query)
    chunk_ids = [cid for cid, _ in candidates]

    # Check cache first
    cached_scores = _get_cached_scores(model_name, query_hash, chunk_ids)

    # Find candidates that need scoring
    uncached_candidates = []
    uncached_indices = []
    for i, (chunk_id, text) in enumerate(candidates):
        if chunk_id not in cached_scores:
            uncached_candidates.append((chunk_id, text))
            uncached_indices.append(i)

    # Score uncached candidates
    new_scores = {}
    if uncached_candidates:
        try:
            pairs = [(query, text) for _, text in uncached_candidates]
            scores = model.predict(pairs, batch_size=batch_size)

            if hasattr(scores, "tolist"):
                scores = scores.tolist()

            for (chunk_id, _), score in zip(uncached_candidates, scores):
                new_scores[chunk_id] = float(score)

            # Cache the new scores
            if new_scores:
                _cache_scores(model_name, query_hash, new_scores)

        except Exception as e:
            logger.error(f"Reranker inference failed: {e}")
            # Fallback: assign neutral scores
            for chunk_id, _ in uncached_candidates:
                new_scores[chunk_id] = 0.0

    # Combine cached and new scores
    all_scores = {**cached_scores, **new_scores}

    # Create scored results
    scored = []
    for chunk_id, text in candidates:
        score = all_scores.get(chunk_id, 0.0)
        scored.append((chunk_id, text, score))

    # Sort by score descending and return top k
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:topk_keep]


def is_available() -> bool:
    """Check if the reranker is available (dependencies installed)"""
    return _get_sentence_transformers() is not None and _get_torch() is not None


def get_model_info() -> dict[str, Any]:
    """Get information about the current reranker configuration"""
    model = _model()
    if model is None:
        return {"available": False, "error": "Model not loaded"}

    return {
        "available": True,
        "model_name": (
            RENV.RERANKER_MODEL if RENV else os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        ),
        "device": _device(),
        "batch_size": (RENV.RERANK_BATCH if RENV else int(os.getenv("RERANK_BATCH", "8"))),
        "input_topk": (RENV.RERANK_INPUT_TOPK if RENV else int(os.getenv("RERANK_INPUT_TOPK", "50"))),
        "output_topk": (RENV.RERANK_KEEP if RENV else int(os.getenv("RERANK_KEEP", "12"))),
        "cache_enabled": True,
    }
