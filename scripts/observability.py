#!/usr/bin/env python3
from __future__ import annotations

"""
Lightweight observability helpers.

- get_logfire(): optional Logfire init with sensible defaults
- span helpers for retrieval/reader/scoring and a metrics logger

Safe to import when Logfire/Pydantic AI are not installed; functions become no-ops.
"""

from typing import Any

_logfire = None


def _lazy_configure() -> Any | None:
    global _logfire
    if _logfire is not None:
        return _logfire
    try:
        import logfire  # type: ignore

        # Configure with defaults; allow env/rc to control backend
        # Set send_to_logfire=False via env/rc if you want to route to another OTEL collector
        logfire.configure()

        # Optional instrumentations (kept minimal by default)
        try:
            logfire.instrument_pydantic_ai()  # emits GenAI OTel spans where available
        except Exception:
            pass
        try:
            logfire.instrument_httpx(capture_all=False)
        except Exception:
            pass
        try:
            logfire.instrument_psycopg()  # SQL timings; parameters are redacted by default
        except Exception:
            pass

        _logfire = logfire
        return _logfire
    except Exception:
        _logfire = None
        return None


def get_logfire():
    """Return configured logfire client or None (no-op mode)."""
    return _lazy_configure()


def _with_span(name: str, attributes: dict | None = None):
    lf = _lazy_configure()
    if not lf:
        # context manager shim doing nothing
        class _Noop:
            def __enter__(self):
                return None

            def __exit__(self, *_):
                return False

        return _Noop()
    return lf.span(name, attributes=attributes or {})


def log_retrieval_span(logfire_obj, query: str, candidate_count: int, duration_ms: float) -> None:
    try:
        if not logfire_obj:
            return
        with logfire_obj.span(
            "retrieval.hybrid", attributes={"query_len": len(query or ""), "candidates": candidate_count}
        ):
            # attach duration as event
            try:
                logfire_obj.info("retrieval.done", duration_ms=duration_ms)
            except Exception:
                pass
    except Exception:
        pass


def log_reader_span(logfire_obj, query: str, answer_len: int, success: bool) -> None:
    try:
        if not logfire_obj:
            return
        with logfire_obj.span(
            "reader.answer",
            attributes={"query_len": len(query or ""), "answer_len": int(answer_len), "ok": bool(success)},
        ):
            pass
    except Exception:
        pass


def log_scoring_span(logfire_obj, case_id: str, precision: float, recall: float, f1: float) -> None:
    try:
        if not logfire_obj:
            return
        with logfire_obj.span("scoring.oracle", attributes={"case_id": case_id}):
            logfire_obj.info("eval.case_scores", precision=precision, recall=recall, f1=f1)
    except Exception:
        pass


def log_eval_metrics(logfire_obj, metrics: dict) -> None:
    try:
        if not logfire_obj:
            return
        logfire_obj.info(
            "eval.metrics", **{k: metrics.get(k) for k in ("precision", "recall", "f1", "faithfulness", "total_cases")}
        )
    except Exception:
        pass
