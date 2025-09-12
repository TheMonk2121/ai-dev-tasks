from __future__ import annotations
import os
from functools import lru_cache
from typing import Any
import yaml
    from src.rag import reranker_env as RENV
import sys
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Configuration loader for reranker settings.
Integrates with the existing retriever configuration system.
"""



try:
except Exception:
    RENV = None

DEFAULT_RERANKER_CONFIG = {
    "enabled": False,
    "model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "input_topk": 50,
    "keep": 12,
    "batch_size": 8,
    "device": "auto",  # auto, cpu, mps, cuda
    "cache_enabled": True,
    "cache_dir": "cache",
}


@lru_cache(maxsize=32)
def load_reranker_config(tag: str = "", file_path: str | None = None) -> dict[str, Any]:
    """
    Load reranker configuration from YAML file with tag-specific overrides.

    Args:
        tag: Tag for tag-specific configuration
        file_path: Path to config file (defaults to retriever_weights.yaml)

    Returns:
        Dictionary with reranker configuration
    """
    path = file_path or os.getenv("RETRIEVER_WEIGHTS_FILE", "configs/retriever_weights.yaml")
    config = dict(DEFAULT_RERANKER_CONFIG)

    try:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Load default reranker config
            default_config = data.get("default", {})
            reranker_config = default_config.get("reranker", {})
            if isinstance(reranker_config, dict):
                config.update({k: v for k, v in reranker_config.items()})

            # Load tag-specific overrides
            tags = data.get("tags", {})
            tag_config = tags.get(tag, {})
            tag_reranker_config = tag_config.get("reranker", {})
            if isinstance(tag_reranker_config, dict):
                config.update({k: v for k, v in tag_reranker_config.items()})

    except Exception:
        # Fall back silently to DEFAULT_RERANKER_CONFIG if file missing or invalid
        pass

    # Override with environment variables
    if RENV:
        env_overrides = {
            "enabled": str(int(RENV.RERANK_ENABLE)),
            "model": RENV.RERANKER_MODEL,
            "input_topk": str(RENV.RERANK_INPUT_TOPK),
            "keep": str(RENV.RERANK_KEEP),
            "batch_size": str(RENV.RERANK_BATCH),
            "device": RENV.TORCH_DEVICE,
            "cache_enabled": "1",
            "cache_dir": os.getenv("RERANKER_CACHE_DIR", "cache"),
        }
    else:
        env_overrides = {
            "enabled": os.getenv("RERANKER_ENABLED"),
            "model": os.getenv("RERANKER_MODEL"),
            "input_topk": os.getenv("RERANK_INPUT_TOPK"),
            "keep": os.getenv("RERANK_KEEP"),
            "batch_size": os.getenv("RERANK_BATCH"),
            "device": os.getenv("TORCH_DEVICE"),
            "cache_enabled": os.getenv("RERANKER_CACHE_ENABLED"),
            "cache_dir": os.getenv("RERANKER_CACHE_DIR"),
        }

    for key, value in env_overrides.items():
        if value is not None:
            if key in ["enabled", "cache_enabled"]:
                config[key] = value.lower() in ("true", "1", "yes", "on")
            elif key in ["input_topk", "keep", "batch_size"]:
                try:
                    config[key] = int(value)
                except ValueError:
                    pass
            else:
                config[key] = value

    return config


def get_reranker_env_vars(config: dict[str, Any]) -> dict[str, str]:
    """
    Convert reranker config to environment variables for the reranker module.

    Args:
        config: Reranker configuration dictionary

    Returns:
        Dictionary of environment variables
    """
    env_vars = {}

    if config.get("model"):
        env_vars["RERANKER_MODEL"] = config["model"]
    if config.get("input_topk"):
        env_vars["RERANK_INPUT_TOPK"] = str(config["input_topk"])
    if config.get("keep"):
        env_vars["RERANK_KEEP"] = str(config["keep"])
    if config.get("batch_size"):
        env_vars["RERANK_BATCH"] = str(config["batch_size"])
    if config.get("device"):
        env_vars["TORCH_DEVICE"] = config["device"]
    if config.get("cache_dir"):
        env_vars["RERANKER_CACHE_DIR"] = config["cache_dir"]

    return env_vars


def apply_reranker_config(config: dict[str, Any]):
    """
    Apply reranker configuration by setting environment variables.

    Args:
        config: Reranker configuration dictionary
    """
    env_vars = get_reranker_env_vars(config)
    for key, value in env_vars.items():
        os.environ[key] = value
