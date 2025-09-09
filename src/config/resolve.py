from __future__ import annotations
import os
import json
from pathlib import Path

from src.rag import reranker_env as RENV


def load_layer_file(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def compose_layers(layer_paths: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for p in layer_paths:
        env.update(load_layer_file(p))
    # CLI / os.environ wins over layers; explicit precedence for known prefixes
    for k, v in os.environ.items():
        if k.startswith(("RAG_", "RERANK", "BM25", "VEC", "RETR")):
            env[k] = v
    return env


def effective_rerank_config() -> dict[str, object]:
    # Always read through shim so legacy/canonical names are normalized
    return {
        "enable": int(getattr(RENV, "RERANK_ENABLE", False)),
        "model": getattr(RENV, "RERANKER_MODEL", None),
        "input_topk": getattr(RENV, "RERANK_INPUT_TOPK", None),
        "keep": getattr(RENV, "RERANK_KEEP", None),
        "batch": getattr(RENV, "RERANK_BATCH", None),
        "device": getattr(RENV, "TORCH_DEVICE", None),
        "cache": getattr(RENV, "RERANK_CACHE_BACKEND", None),
    }
