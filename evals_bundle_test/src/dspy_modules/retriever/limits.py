#!/usr/bin/env python3
import os
from functools import lru_cache

import yaml

# Environment-based defaults for increased candidate pool
DENSE_TOPK_DEFAULT = int(os.getenv("RETRIEVER_DENSE_TOPK", "120"))
BM25_TOPK_DEFAULT = int(os.getenv("RETRIEVER_BM25_TOPK", "120"))
RERANK_INPUT_TOPK = int(os.getenv("RERANK_INPUT_TOPK", "120"))
RERANK_KEEP = int(os.getenv("RERANK_KEEP", "24"))

DEFAULT_LIMITS: dict[str, int] = {
    "shortlist": max(DENSE_TOPK_DEFAULT, BM25_TOPK_DEFAULT),
    "topk": RERANK_KEEP,
    "dense_topk": DENSE_TOPK_DEFAULT,
    "bm25_topk": BM25_TOPK_DEFAULT,
    "rerank_input_topk": RERANK_INPUT_TOPK,
    "rerank_keep": RERANK_KEEP,
}


@lru_cache(maxsize=32)
def load_limits(tag: str = "", file_path: str | None = None) -> dict[str, int]:
    path = file_path or os.getenv("RETRIEVER_LIMITS_FILE", "configs/retriever_limits.yaml")
    limits: dict[str, int] = dict(DEFAULT_LIMITS)
    try:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            limits.update(data.get("default") or {})
            tag_map = data.get("tags") or {}
            if tag and tag_map.get(tag):
                limits.update(tag_map[tag])
    except Exception:
        pass

    # normalize + guard
    limits["shortlist"] = int(max(10, min(500, int(limits.get("shortlist", DEFAULT_LIMITS["shortlist"])))))
    limits["topk"] = int(max(5, min(limits["shortlist"], int(limits.get("topk", DEFAULT_LIMITS["topk"])))))

    # Ensure new limits are properly set
    limits["dense_topk"] = int(max(10, min(500, int(limits.get("dense_topk", DEFAULT_LIMITS["dense_topk"])))))
    limits["bm25_topk"] = int(max(10, min(500, int(limits.get("bm25_topk", DEFAULT_LIMITS["bm25_topk"])))))
    limits["rerank_input_topk"] = int(
        max(10, min(500, int(limits.get("rerank_input_topk", DEFAULT_LIMITS["rerank_input_topk"]))))
    )
    limits["rerank_keep"] = int(max(5, min(100, int(limits.get("rerank_keep", DEFAULT_LIMITS["rerank_keep"])))))

    return limits
