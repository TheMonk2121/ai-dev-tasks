"""Logfire bootstrap and instrumentation setup.

This module centralizes Logfire configuration and provides small helper
wrappers used by evaluators to create spans and emit metrics. Keeping the
helpers here avoids optional import churn across scripts and makes static
type checkers happy where symbols are imported from this module.
"""

import os

import logfire


def init_observability(service="ai-dev-tasks", environment=os.getenv("ENV", "dev")) -> None:
    """Initialize Logfire observability with instrumentation.

    Args:
        service: Service name for telemetry
        environment: Environment name (dev, staging, prod)
    """
    # Configure Logfire with proper settings
    logfire.configure(
        service_name=service,
        environment=environment,
        send_to_logfire="if-token-present",  # Only send if token is present
        inspect_arguments=False,  # Disable argument inspection to avoid warnings
    )

    # Instrumentations (call each once after configure)
    try:
        logfire.instrument_httpx()  # LLM SDKs typically use httpx under the hood
    except Exception:
        pass
    try:
        logfire.instrument_psycopg()  # or instrument_asyncpg() if asyncpg
    except Exception:
        pass
    try:
        logfire.instrument_pydantic(record="all")  # Instrument all Pydantic models with full recording
    except Exception:
        pass
    # PydanticAI auto-instrumentation happens when you set Agent(..., instrument=...)


def get_logfire():
    """Return the configured logfire module.

    Kept as a function to match existing imports in scripts that do:
    `from scripts.observability import get_logfire`.
    """
    return logfire


def create_span(name: str, **attributes):
    """Create a manual span for custom instrumentation."""
    return logfire.span(name, attributes=attributes)


def log_metrics(**metrics):
    """Log custom metrics."""
    logfire.info("eval.metrics", **metrics)


# ----- Thin wrappers used by evaluation scripts -----------------------------
def log_eval_metrics(_logfire, metrics: dict) -> None:
    """Emit a consolidated metrics record.

    Args:
        _logfire: the logfire module (injected to keep call sites simple)
        metrics: mapping of metric name -> value
    """
    try:
        _logfire.info("eval.metrics", **metrics)
    except Exception:
        pass


def log_retrieval_span(_logfire, query: str, n_candidates: int, latency_ms: float) -> None:
    """Create a retrieval span with basic attributes."""
    try:
        with _logfire.span(
            "retrieval.hybrid",
            attributes={
                "query_len": len(query or ""),
                "candidates": int(n_candidates),
                "latency_ms": float(latency_ms),
            },
        ):
            pass
    except Exception:
        pass


def log_reader_span(_logfire, query: str, answer_len: int, ok: bool) -> None:
    """Create a reader span recording answer length and success state."""
    try:
        with _logfire.span(
            "reader.extractive",
            attributes={
                "query_len": len(query or ""),
                "answer_len": int(answer_len),
                "ok": bool(ok),
            },
        ):
            pass
    except Exception:
        pass


def log_scoring_span(_logfire, case_id: str, precision: float, recall: float, f1: float) -> None:
    """Create a scoring span for a single case."""
    try:
        with _logfire.span(
            "scoring",
            attributes={
                "case_id": str(case_id),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
            },
        ):
            pass
    except Exception:
        pass
