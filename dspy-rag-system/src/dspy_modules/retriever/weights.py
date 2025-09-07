#!/usr/bin/env python3
import os
from functools import lru_cache
from typing import Dict, Optional

import yaml

DEFAULT: Dict[str, float] = {"w_path": 2.0, "w_short": 1.8, "w_title": 1.4, "w_bm25": 1.0, "w_vec": 1.1}


@lru_cache(maxsize=32)
def load_weights(tag: str = "", file_path: Optional[str] = None) -> Dict[str, float]:
    path = file_path or os.getenv("RETRIEVER_WEIGHTS_FILE", "configs/retriever_weights.yaml")
    cfg: Dict[str, float] = dict(DEFAULT)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if isinstance(data.get("default"), dict):
                cfg.update({k: float(v) for k, v in data["default"].items()})
            tags = data.get("tags") or {}
            tag_cfg = tags.get(tag or "") or {}
            if isinstance(tag_cfg, dict):
                cfg.update({k: float(v) for k, v in tag_cfg.items()})
    except Exception:
        # Fall back silently to DEFAULT if file missing or invalid
        pass
    return cfg

