"""Utility helpers for loading retrieval configuration with environment overrides.

The tuning pipeline writes per-trial copies of ``retrieval.yaml`` and sets the
``RETRIEVAL_CONFIG_PATH`` environment variable before launching evaluations.
This module provides a single point of truth for resolving that override and
producing typed views over commonly used configuration sections.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, MutableMapping

import yaml  # type: ignore[import-untyped]

LOGGER = logging.getLogger(__name__)
DEFAULT_CONFIG_PATH = Path("evals/stable_build/config/retrieval.yaml")


def resolve_config_path(explicit: str | os.PathLike[str] | None = None) -> Path:
    """Resolve the retrieval configuration path honoring environment overrides."""
    candidates: list[Path] = []

    if explicit is not None:
        candidates.append(Path(explicit).expanduser())

    env_override = os.getenv("RETRIEVAL_CONFIG_PATH")
    if env_override:
        candidates.append(Path(env_override).expanduser())

    candidates.append(DEFAULT_CONFIG_PATH)

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    # Fall back to the first candidate (prefer explicit override even if missing)
    return candidates[0]


def load_retrieval_config(config_path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load the retrieval configuration as a dictionary."""
    resolved = resolve_config_path(config_path)
    return _load_config_for_path(str(resolved))


@lru_cache(maxsize=8)
def _load_config_for_path(resolved_path: str) -> dict[str, Any]:
    path = Path(resolved_path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        LOGGER.warning("Retrieval config not found at %s: %s", path, exc)
        if path.resolve() != DEFAULT_CONFIG_PATH.resolve():
            return _load_config_for_path(str(DEFAULT_CONFIG_PATH))
        return {}
    except Exception as exc:
        LOGGER.warning("Failed to load retrieval config from %s: %s", path, exc)
        if path.resolve() != DEFAULT_CONFIG_PATH.resolve():
            return _load_config_for_path(str(DEFAULT_CONFIG_PATH))
        return {}

    if not isinstance(data, MutableMapping):
        LOGGER.warning("Retrieval config %s did not contain a mapping", path)
        return {}

    # Normalize to plain dict to detach from YAML structures
    return dict(data)


def _as_mapping(value: object) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    return None


def _coerce_int(value: object, default: int) -> int:
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
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def _coerce_bool(value: object, default: bool) -> bool:
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
class PrefilterSettings:
    min_bm25_score: float = 0.1
    min_vector_score: float = 0.7
    min_doc_length: int = 50
    max_doc_length: int = 8000
    enable_diversity: bool = True
    diversity_threshold: float = 0.9

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "PrefilterSettings":
        if data is None:
            return cls()
        return cls(
            min_bm25_score=_coerce_float(data.get("min_bm25_score", 0.1), 0.1),
            min_vector_score=_coerce_float(data.get("min_vector_score", 0.7), 0.7),
            min_doc_length=_coerce_int(data.get("min_doc_length", 50), 50),
            max_doc_length=_coerce_int(data.get("max_doc_length", 8000), 8000),
            enable_diversity=_coerce_bool(data.get("enable_diversity", True), True),
            diversity_threshold=_coerce_float(data.get("diversity_threshold", 0.9), 0.9),
        )


@dataclass(frozen=True)
class CrossEncoderSettings:
    model_name: str = "BAAI/bge-reranker-base"
    onnx_path: str = "models/reranker.onnx"
    micro_batch_size: int = 32
    timeout_ms: int = 400
    max_timeout_ms: int = 600
    fallback_to_heuristic: bool = True
    workers: int = 3

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "CrossEncoderSettings":
        if data is None:
            return cls()
        return cls(
            model_name=str(data.get("model_name", cls.model_name)),
            onnx_path=str(data.get("onnx_path", cls.onnx_path)),
            micro_batch_size=_coerce_int(data.get("micro_batch_size", cls.micro_batch_size), cls.micro_batch_size),
            timeout_ms=_coerce_int(data.get("timeout_ms", cls.timeout_ms), cls.timeout_ms),
            max_timeout_ms=_coerce_int(data.get("max_timeout_ms", cls.max_timeout_ms), cls.max_timeout_ms),
            fallback_to_heuristic=_coerce_bool(
                data.get("fallback_to_heuristic", cls.fallback_to_heuristic), cls.fallback_to_heuristic
            ),
            workers=_coerce_int(data.get("workers", cls.workers), cls.workers),
        )


@dataclass(frozen=True)
class WindowingSettings:
    enabled: bool = True
    window_size_tokens: int = 150
    overlap_pct: int = 33
    preserve_doc_boundaries: bool = True

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "WindowingSettings":
        if data is None:
            return cls()
        return cls(
            enabled=_coerce_bool(data.get("enabled", True), True),
            window_size_tokens=_coerce_int(data.get("window_size_tokens", 150), 150),
            overlap_pct=_coerce_int(data.get("overlap_pct", 33), 33),
            preserve_doc_boundaries=_coerce_bool(data.get("preserve_doc_boundaries", True), True),
        )


@dataclass(frozen=True)
class DedupSettings:
    enabled: bool = True
    method: str = "cosine"
    threshold: float = 0.9
    before_rerank: bool = True

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "DedupSettings":
        if data is None:
            return cls()
        return cls(
            enabled=_coerce_bool(data.get("enabled", True), True),
            method=str(data.get("method", cls.method)),
            threshold=_coerce_float(data.get("threshold", 0.9), 0.9),
            before_rerank=_coerce_bool(data.get("before_rerank", True), True),
        )


@dataclass(frozen=True)
class RerankSettings:
    enabled: bool = True
    alpha: float = 0.7
    final_top_n: int = 8
    method: str = "cross_encoder"
    min_score: float = 0.30
    per_file_penalty: float = 0.10
    cross_encoder: CrossEncoderSettings = CrossEncoderSettings()
    windowing: WindowingSettings = WindowingSettings()
    dedup: DedupSettings = DedupSettings()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> "RerankSettings":
        if data is None:
            return cls()
        return cls(
            enabled=_coerce_bool(data.get("enabled", True), True),
            alpha=_coerce_float(data.get("alpha", 0.7), 0.7),
            final_top_n=_coerce_int(data.get("final_top_n", 8), 8),
            method=str(data.get("method", "cross_encoder")),
            min_score=_coerce_float(data.get("min_score", 0.30), 0.30),
            per_file_penalty=_coerce_float(data.get("per_file_penalty", 0.10), 0.10),
            cross_encoder=CrossEncoderSettings.from_mapping(_as_mapping(data.get("cross_encoder"))),
            windowing=WindowingSettings.from_mapping(_as_mapping(data.get("windowing"))),
            dedup=DedupSettings.from_mapping(_as_mapping(data.get("dedup"))),
        )

    def recommended_input_pool(self, baseline: int) -> int:
        """Return the recommended rerank input pool size."""
        if not self.enabled:
            return baseline
        multiplier = 3
        suggested = max(self.final_top_n * multiplier, self.final_top_n)
        return max(baseline, suggested)


def get_candidate_limits(config: Mapping[str, Any] | None = None) -> CandidateLimits:
    source = config if config is not None else load_retrieval_config()
    return CandidateLimits.from_mapping(_as_mapping(source.get("candidates")))


def get_fusion_settings(config: Mapping[str, Any] | None = None) -> FusionSettings:
    source = config if config is not None else load_retrieval_config()
    return FusionSettings.from_mapping(_as_mapping(source.get("fusion")))


def get_prefilter_settings(config: Mapping[str, Any] | None = None) -> PrefilterSettings:
    source = config if config is not None else load_retrieval_config()
    return PrefilterSettings.from_mapping(_as_mapping(source.get("prefilter")))


def get_rerank_settings(config: Mapping[str, Any] | None = None) -> RerankSettings:
    source = config if config is not None else load_retrieval_config()
    return RerankSettings.from_mapping(_as_mapping(source.get("rerank")))
