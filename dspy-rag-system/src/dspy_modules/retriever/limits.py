#!/usr/bin/env python3
import os
from functools import lru_cache


import yaml

DEFAULT_LIMITS: dict[str, int] = {"shortlist": 60, "topk": 25}


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
    limits["shortlist"] = int(max(10, min(200, int(limits.get("shortlist", 60)))))
    limits["topk"] = int(max(5, min(limits["shortlist"], int(limits.get("topk", 25)))))
    return limits
