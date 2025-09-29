#!/usr/bin/env python3
"""Unified evaluation runner shim (beta)."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import Iterable
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add scripts to path for imports
scripts_path = Path(__file__).parent.parent.resolve()
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# Import after path setup
try:
    from scripts.evaluation.dspy_evaluator import CleanDSPyEvaluator
    from src.evaluation.adapters import RagCheckerAdapter
    from src.evaluation.contracts import CaseResult, EvalSummary, Reporter, RunConfig
    from src.evaluation.errors import ProviderError
    from src.evaluation.reporters import (
        build_reporters,
        notify_begin,
        notify_case,
        notify_complete,
    )
    from src.evaluation.spans import eval_run_span
except ImportError as e:
    # Fallback for when modules are not available
    print(f"Warning: Import error - {e}")
    # Define minimal fallback classes with proper type annotations
    class CleanDSPyEvaluator:
        def __init__(self, profile: str) -> None:
            self.profile: str = profile
        
        def run_evaluation(self, dataset: str, limit: int, *args: Any, **kwargs: Any) -> dict[str, Any]:
            return {"case_results": [], "overall_metrics": {}}
    
    class RagCheckerAdapter:
        async def prepare(self, config: Any) -> None:
            pass
        
        def case_inputs(self) -> list[Any]:
            return []
        
        async def run_case(self, case_input: Any) -> Any:
            return type('Result', (), {
                'case_id': 'fallback',
                'metrics': {},
                'latency_ms': 0.0,
                'verdict': 'unknown',
                'artifacts': {}
            })()
        
        async def finalize(self, results: list[Any]) -> dict[str, Any]:
            return {}
        
        def artifact_path(self) -> str | None:
            return None
    
    class CaseResult:
        def __init__(self, case_id: str, metrics: dict[str, Any], latency_ms: float, verdict: str, artifacts: dict[str, Any], spans: tuple[Any, ...]) -> None:
            self.case_id: str = case_id
            self.metrics: dict[str, Any] = metrics
            self.latency_ms: float = latency_ms
            self.verdict: str = verdict
            self.artifacts: dict[str, Any] = artifacts
            self.spans: tuple[Any, ...] = spans
    
    class EvalSummary:
        def __init__(self, run_id: str, started_at: datetime, finished_at: datetime, config: Any, results: tuple[Any, ...], metrics: dict[str, Any], artifacts: dict[str, Any]) -> None:
            self.run_id: str = run_id
            self.started_at: datetime = started_at
            self.finished_at: datetime = finished_at
            self.config: Any = config
            self.results: tuple[Any, ...] = results
            self.metrics: dict[str, Any] = metrics
            self.artifacts: dict[str, Any] = artifacts
    
    class Reporter:
        pass
    
    class RunConfig:
        def __init__(self, run_id: str, profile: str, dataset: Path, adapters: tuple[str, ...], limit: int, seed: int, concurrency: int, reporter_names: tuple[str, ...], environment: dict[str, Any]) -> None:
            self.run_id: str = run_id
            self.profile: str = profile
            self.dataset: Path = dataset
            self.adapters: tuple[str, ...] = adapters
            self.limit: int = limit
            self.seed: int = seed
            self.concurrency: int = concurrency
            self.reporter_names: tuple[str, ...] = reporter_names
            self.environment: dict[str, Any] = environment
    
    class ProviderError(Exception):
        pass
    
    def build_reporters(names: list[str] | tuple[str, ...]) -> list[Reporter]:
        return []
    
    async def notify_begin(reporters: list[Reporter], config: Any) -> None:
        pass
    
    async def notify_case(reporters: list[Reporter], result: Any) -> None:
        pass
    
    async def notify_complete(reporters: list[Reporter], summary: Any) -> None:
        pass
    
    class eval_run_span:
        def __init__(self, run_id: str, profile: str, metadata: dict[str, Any]) -> None:
            self.run_id: str = run_id
            self.profile: str = profile
            self.metadata: dict[str, Any] = metadata
        
        async def __aenter__(self) -> eval_run_span:
            return self
        
        async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
            pass
        
        def case(self, case_id: str, metadata: dict[str, Any] | None = None) -> eval_run_span:
            return self
        
        def phase(self, name: str) -> eval_run_span:
            return self
        
        @property
        def records(self) -> list[Any]:
            return []


def _build_config(args: argparse.Namespace, reporter_specs: list[str]) -> RunConfig:
    env_overrides = {k: v for k, v in os.environ.items() if k.startswith("EVAL_") or k.startswith("DSPY_")}
    return RunConfig(
        run_id=args.run_id,
        profile=args.profile,
        dataset=Path(args.dataset).resolve(),
        adapters=(args.adapter,),
        limit=args.limit,
        seed=args.seed,
        concurrency=args.concurrency,
        reporter_names=tuple(reporter_specs),
        environment=env_overrides,
    )


def _case_metrics(raw: dict[str, Any]) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for key in ("precision", "recall", "f1", "f1_score", "faithfulness"):
        value = raw.get(key)
        if isinstance(value, int | float):
            metrics[key] = float(value)
    nested = raw.get("metrics")
    if isinstance(nested, dict):
        for key, value in nested.items():
            if isinstance(value, int | float):
                metrics[f"metrics.{key}"] = float(value)
    return metrics


def _overall_metrics(raw: dict[str, Any]) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for key, value in raw.items():
        if isinstance(value, int | float):
            metrics[key] = float(value)
    return metrics


def _verdict(raw: dict[str, Any]) -> str:
    status = raw.get("status")
    if isinstance(status, str) and status:
        return status
    precision = raw.get("precision") or raw.get("f1") or raw.get("f1_score")
    try:
        if precision is not None and float(precision) > 0:
            return "success"
    except (TypeError, ValueError):
        pass
    return "unknown"


async def _run_dspy(config: RunConfig, reporters: list[Reporter]) -> EvalSummary:
    start = datetime.now(UTC)
    evaluator = CleanDSPyEvaluator(profile=config.profile)

    await notify_begin(reporters, config)

    raw_results = await asyncio.to_thread(
        evaluator.run_evaluation,
        str(config.dataset),
        config.limit,
        None,
        None,
        config.concurrency,
    )

    case_results: list[CaseResult] = []
    async with eval_run_span(config.run_id, config.profile, {"adapters": config.adapters}) as run_span:
        for raw_case in raw_results.get("case_results", []):
            case_id = str(raw_case.get("case_id", raw_case.get("id", "unknown")))
            async with run_span.case(case_id) as case_span:
                async with case_span.phase("legacy.adapter"):
                    pass
                latency = float(raw_case.get("latency_sec", 0.0)) * 1000
                metrics = _case_metrics(raw_case)
                result = CaseResult(
                    case_id=case_id,
                    metrics=metrics,
                    latency_ms=latency,
                    verdict=_verdict(raw_case),
                    artifacts={"raw": raw_case},
                    spans=tuple(case_span.records),
                )
            case_results.append(result)
            await notify_case(reporters, result)

    overall = _overall_metrics(raw_results.get("overall_metrics", {}))
    summary = EvalSummary(
        run_id=config.run_id,
        started_at=start,
        finished_at=datetime.now(UTC),
        config=config,
        results=tuple(case_results),
        metrics=overall,
        artifacts={"raw": raw_results},
    )

    await notify_complete(reporters, summary)
    return summary


async def _run_ragchecker(config: RunConfig, reporters: list[Reporter]) -> EvalSummary:
    start = datetime.now(UTC)
    await notify_begin(reporters, config)

    adapter = RagCheckerAdapter()
    results: list[CaseResult] = []

    async with eval_run_span(config.run_id, config.profile, {"adapter": "ragchecker"}) as run_span:
        await adapter.prepare(config)
        case_inputs = list(adapter.case_inputs())

        for case_input in case_inputs:
            async with run_span.case(case_input.case_id, {"query": case_input.query[:80]}) as case_span:
                async with case_span.phase("legacy.adapter"):
                    raw_result = await adapter.run_case(case_input)
                result = CaseResult(
                    case_id=raw_result.case_id,
                    metrics=raw_result.metrics,
                    latency_ms=raw_result.latency_ms,
                    verdict=raw_result.verdict,
                    artifacts=raw_result.artifacts,
                    spans=tuple(case_span.records),
                )
            results.append(result)
            await notify_case(reporters, result)

        metrics_mapping = await adapter.finalize(results)

    summary = EvalSummary(
        run_id=config.run_id,
        started_at=start,
        finished_at=datetime.now(UTC),
        config=config,
        results=tuple(results),
        metrics=dict(metrics_mapping),
        artifacts={
            "adapter": "ragchecker",
            "ragchecker_results_path": str(adapter.artifact_path()) if adapter.artifact_path() else None,
        },
    )

    await notify_complete(reporters, summary)
    return summary


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified evaluation runner (beta)")
    _ = parser.add_argument("--dataset", default="evals/data/gold/v1/gold_cases_121.jsonl", help="Path to dataset JSONL")
    _ = parser.add_argument("--profile", default="gold", choices=["gold", "real", "mock"], help="Evaluation profile")
    _ = parser.add_argument("--run-id", default=datetime.now(UTC).strftime("run_%Y%m%d_%H%M%S"), help="Run identifier")
    _ = parser.add_argument("--adapter", default="dspy", choices=["dspy", "ragchecker"], help="Evaluation adapter to use")
    _ = parser.add_argument("--limit", type=int, default=None, help="Limit number of cases")
    _ = parser.add_argument("--seed", type=int, default=42, help="Random seed")
    _ = parser.add_argument("--concurrency", type=int, default=3, help="Maximum concurrent cases")
    _ = parser.add_argument("--reporter", action="append", default=None, help="Reporter spec (console, console-verbose, json:/path)")
    _ = parser.add_argument("--out", type=Path, default=None, help="Shortcut for json reporter output path")
    _ = parser.add_argument("--verbose", action="store_true", help="Use verbose console reporter")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    reporter_specs = args.reporter or []
    if args.verbose and "console-verbose" not in reporter_specs:
        _ = reporter_specs.append("console-verbose")
    if not reporter_specs:
        _ = reporter_specs.append("console")
    if args.out:
        reporter_specs = [spec for spec in reporter_specs if not spec.startswith("json")]
        _ = reporter_specs.append(f"json:{args.out}")

    config = _build_config(args, reporter_specs)
    reporters = build_reporters(config.reporter_names)

    try:
        if args.adapter == "ragchecker":
            _ = asyncio.run(_run_ragchecker(config, reporters))
        else:
            _ = asyncio.run(_run_dspy(config, reporters))
    except ProviderError as exc:
        print(f"❌ Provider error: {exc}")
        return 2
    except Exception as exc:
        print(f"❌ Unexpected error: {exc}")
        return 1

    return 0


class CodexEvaluator:
    """Unified evaluation runner for codex evaluations."""
    
    def __init__(self) -> None:
        """Initialize the codex evaluator."""
        pass
    
    async def _run_ragchecker(self, config: RunConfig, reporters: tuple[Reporter, ...] = ()) -> EvalSummary:
        """Run ragchecker evaluation."""
        return await _run_ragchecker(config, list(reporters))
    
    async def _run_dspy(self, config: RunConfig, reporters: tuple[Reporter, ...] = ()) -> EvalSummary:
        """Run DSPy evaluation."""
        return await _run_dspy(config, list(reporters))


if __name__ == "__main__":
    raise SystemExit(main())
