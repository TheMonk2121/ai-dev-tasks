"""Typed evaluation errors shared by adapters and the unified runner."""

from __future__ import annotations


class EvalError(Exception):
    """Base exception for unified evaluation runner failures."""


class ConfigError(EvalError):
    """Raised when configuration validation fails."""


class DataInvariantError(EvalError):
    """Raised when dataset or case payloads violate expected invariants."""


class ProviderError(EvalError):
    """Raised when an upstream provider (LLM, retriever, etc.) fails deterministically."""


class TransientRetryableError(ProviderError):
    """Raised when a transient provider issue allows for retry semantics."""


__all__ = [
    "EvalError",
    "ConfigError",
    "DataInvariantError",
    "ProviderError",
    "TransientRetryableError",
]
