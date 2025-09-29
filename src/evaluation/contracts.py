"""Shared evaluation contracts for unified runner adapters.

These dataclasses provide typed configurations and payloads that the new
`codex_evaluator` runner will use to orchestrate evaluation adapters. Keeping
these contracts lightweight and dependency-free makes it safe to import them
from both legacy wrappers and upcoming unified implementations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class RunConfig:
    """Canonical configuration resolved from CLI, env, and profile inputs."""

    run_id: str
    profile: str
    dataset: Path
    adapters: tuple[str, ...] = ("ragchecker",)
    limit: int | None = None
    seed: int = 42
    concurrency: int = 3
    reporter_names: tuple[str, ...] = ("console",)
    environment: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CaseInput:
    """Normalized case payload fed into adapters regardless of source format."""

    case_id: str
    query: str
    ground_truth: str
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SpanRecord:
    """Structured span output for downstream observability and ledgers."""

    name: str
    start_ms: float
    duration_ms: float
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CaseResult:
    """Adapter-agnostic result produced for each evaluated case."""

    case_id: str
    metrics: Mapping[str, float]
    latency_ms: float
    verdict: str
    artifacts: Mapping[str, Any] = field(default_factory=dict)
    spans: Sequence[SpanRecord] = ()


@dataclass(frozen=True, slots=True)
class EvalSummary:
    """Aggregate outcome for an evaluation run."""

    run_id: str
    started_at: datetime
    finished_at: datetime
    config: RunConfig
    results: Sequence[CaseResult]
    metrics: Mapping[str, float]
    artifacts: Mapping[str, Any] = field(default_factory=dict)


class Evaluator(Protocol):
    """Adapter protocol implemented by RAGChecker/DSPy/AB-test integrations."""

    async def prepare(self, config: RunConfig) -> None:
        """Perform any one-time setup prior to case execution."""
        ...

    async def run_case(self, case: CaseInput) -> CaseResult:
        """Execute the adapter against an individual case."""
        ...

    async def finalize(self, results: Sequence[CaseResult]) -> Mapping[str, float]:
        """Return aggregated metrics after all cases complete."""
        ...


class Reporter(Protocol):
    """Reporter protocol for emitting run/case level telemetry."""

    async def begin(self, config: RunConfig) -> None:
        """Called once at the start of an evaluation run."""

    async def emit_case(self, result: CaseResult) -> None:
        """Called for every produced case result."""

    async def complete(self, summary: EvalSummary) -> None:
        """Called once after aggregation with the final summary."""


__all__ = [
    "RunConfig",
    "CaseInput",
    "CaseResult",
    "SpanRecord",
    "EvalSummary",
    "Evaluator",
    "Reporter",
]
