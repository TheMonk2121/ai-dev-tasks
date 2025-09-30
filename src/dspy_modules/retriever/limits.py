#!/usr/bin/env python3
import os
from functools import lru_cache
from typing import Any

from src.retrieval.config_loader import (
    CandidateLimits,
    RerankSettings,
    get_candidate_limits,
    get_rerank_settings,
    load_retrieval_config,
)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _clamp(value: int, *, low: int, high: int) -> int:
    return max(low, min(high, value))


def _resolve_config(file_path: str | None) -> dict[str, Any]:
    if file_path is not None:
        return load_retrieval_config(file_path)
    return load_retrieval_config()


@lru_cache(maxsize=32)
def load_limits(tag: str = "", file_path: str | None = None) -> dict[str, int]:
    config = _resolve_config(file_path)
    candidate_limits: CandidateLimits = get_candidate_limits(config)
    rerank_settings: RerankSettings = get_rerank_settings(config)

    _ = tag  # Reserved for tag-specific overrides in future tuning passes

    shortlist_default = max(candidate_limits.final_limit, candidate_limits.min_candidates)
    shortlist = _env_int("RETRIEVER_SHORTLIST", shortlist_default)
    shortlist = _clamp(shortlist, low=candidate_limits.min_candidates, high=500)

    dense_topk = _env_int("RETRIEVER_DENSE_TOPK", candidate_limits.vector_limit)
    dense_topk = _clamp(dense_topk, low=10, high=500)

    bm25_topk = _env_int("RETRIEVER_BM25_TOPK", candidate_limits.bm25_limit)
    bm25_topk = _clamp(bm25_topk, low=10, high=500)

    rerank_keep_default = max(rerank_settings.final_top_n, 1)
    rerank_keep = _env_int("RERANK_KEEP", rerank_keep_default)
    rerank_keep = _clamp(rerank_keep, low=1, high=100)

    pool_baseline = max(shortlist, rerank_keep)
    rerank_input_default = rerank_settings.recommended_input_pool(pool_baseline)
    rerank_input_topk = _env_int("RERANK_INPUT_TOPK", rerank_input_default)
    rerank_input_topk = _clamp(rerank_input_topk, low=pool_baseline, high=500)

    topk_default = min(shortlist, rerank_keep)
    topk = _env_int("RETRIEVER_TOPK", topk_default)
    topk = _clamp(topk, low=1, high=shortlist)

    limits = {
        "shortlist": shortlist,
        "topk": topk,
        "dense_topk": dense_topk,
        "bm25_topk": bm25_topk,
        "rerank_input_topk": rerank_input_topk,
        "rerank_keep": rerank_keep,
    }

    return limits
