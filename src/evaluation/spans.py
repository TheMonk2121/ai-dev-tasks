"""Span helpers implementing the standard eval.run -> retrieval pipeline."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable, Mapping, Sequence

try:
    import logfire  # type: ignore
except Exception:  # pragma: no cover - logfire is optional for local dev
    logfire = None  # type: ignore[assignment]

from .contracts import SpanRecord


@dataclass(slots=True)
class CaseSpanContext:
    """Collects span records for a single case."""

    _parent_exit: Callable[[Any], None]
    _span: Any
    records: list[SpanRecord]

    @asynccontextmanager
    async def phase(self, name: str, attributes: Mapping[str, Any] | None = None):
        """Emit a child span for a retrieval/rerank/generate/judge phase."""

        start = perf_counter()
        lf_span = _enter_span(name, parent=self._span, attributes=attributes)
        try:
            yield lf_span
        finally:
            duration_ms = (perf_counter() - start) * 1000
            if lf_span is not None:
                _set_attributes(lf_span, duration_ms=duration_ms)
                _exit_span(lf_span)
            self.records.append(
                SpanRecord(
                    name=name,
                    start_ms=start * 1000,
                    duration_ms=duration_ms,
                    attributes=attributes or {},
                )
            )

    async def aclose(self) -> None:
        """Close the underlying case span."""

        if self._span is not None:
            self._parent_exit(self._span)
            self._span = None


@dataclass(slots=True)
class RunSpanContext:
    """Manages run-level span state and produces case contexts."""

    _exit: callable
    _span: Any

    @asynccontextmanager
    async def case(
        self,
        case_id: str,
        attributes: Mapping[str, Any] | None = None,
    ) -> CaseSpanContext:
        start = perf_counter()
        lf_span = _enter_span("eval.case", parent=self._span, attributes={"case_id": case_id, **(attributes or {})})
        context = CaseSpanContext(_exit_span, lf_span, [])
        try:
            yield context
        finally:
            duration_ms = (perf_counter() - start) * 1000
            if lf_span is not None:
                _set_attributes(lf_span, duration_ms=duration_ms, case_id=case_id)
                _exit_span(lf_span)

    async def aclose(self) -> None:
        if self._span is not None:
            self._exit(self._span)
            self._span = None


@asynccontextmanager
async def eval_run_span(
    run_id: str,
    profile: str,
    attributes: Mapping[str, Any] | None = None,
):
    """Context manager capturing run-level span information."""

    span = _enter_span("eval.run", attributes={"run_id": run_id, "profile": profile, **(attributes or {})})
    try:
        yield RunSpanContext(_exit_span, span)
    finally:
        if span is not None:
            _exit_span(span)


def _enter_span(name: str, parent: Any | None = None, attributes: Mapping[str, Any] | None = None) -> Any | None:
    if logfire is None:
        return None
    kwargs = attributes or {}
    if parent is not None:
        span_ctx = parent.span(name, **kwargs)
    else:
        span_ctx = logfire.span(name, **kwargs)
    return span_ctx.__enter__()


def _exit_span(span: Any) -> None:
    if span is None:
        return
    try:
        span.__exit__(None, None, None)
    except AttributeError:  # pragma: no cover - defensive guard
        pass


def _set_attributes(span: Any, **attributes: Any) -> None:
    if span is None:
        return
    setter = getattr(span, "set_attribute", None)
    if callable(setter):
        for key, value in attributes.items():
            setter(key, value)


__all__: Sequence[str] = ("eval_run_span", "RunSpanContext", "CaseSpanContext")
