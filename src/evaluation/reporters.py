"""Reporter implementations for the unified evaluation runner."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from src.evaluation.contracts import CaseResult, EvalSummary, Reporter, RunConfig


class ConsoleReporter(Reporter):
    """Human-friendly console reporter mirroring legacy output."""

    def __init__(self, verbose: bool = False) -> None:
        self._verbose = verbose

    async def begin(self, config: RunConfig) -> None:
        print(f"🚀 Starting evaluation run {config.run_id} (profile={config.profile})")
        print(f"   Dataset: {config.dataset}")
        print(f"   Limit: {config.limit or 'all'}; Concurrency: {config.concurrency}")

    async def emit_case(self, result: CaseResult) -> None:
        if not self._verbose:
            return
        metrics = ", ".join(f"{k}={v:.3f}" for k, v in sorted(result.metrics.items()))
        print(f"   • {result.case_id}: {result.verdict} ({metrics})")

    async def complete(self, summary: EvalSummary) -> None:
        print("✅ Evaluation complete")
        for key, value in sorted(summary.metrics.items()):
            try:
                print(f"   {key}: {float(value):.3f}")
            except (TypeError, ValueError):
                print(f"   {key}: {value}")
        print(f"   Cases: {len(summary.results)}")


class JsonReporter(Reporter):
    """Persists evaluation summaries to a JSON artifact."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def begin(self, config: RunConfig) -> None:  # noqa: D401
        self._config = config

    async def emit_case(self, result: CaseResult) -> None:  # noqa: D401
        # No-op; we persist only at completion to avoid partial files.
        return

    async def complete(self, summary: EvalSummary) -> None:
        payload = {
            "run_id": summary.run_id,
            "profile": summary.config.profile,
            "dataset": str(summary.config.dataset),
            "metrics": dict(summary.metrics),
            "cases": [case.case_id for case in summary.results],
            "started_at": summary.started_at.isoformat(),
            "finished_at": summary.finished_at.isoformat(),
        }
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"📁 Summary written to {self._path}")


def build_reporters(specs: Sequence[str], options: Mapping[str, str] | None = None) -> list[Reporter]:
    reporters: list[Reporter] = []
    options = options or {}
    for spec in specs:
        if spec.startswith("json:"):
            reporter = JsonReporter(Path(spec.split(":", 1)[1]))
        elif spec == "json" and "json_path" in options:
            reporter = JsonReporter(Path(options["json_path"]))
        elif spec == "console-verbose":
            reporter = ConsoleReporter(verbose=True)
        elif spec == "console":
            reporter = ConsoleReporter()
        else:
            raise ValueError(f"Unknown reporter spec: {spec}")
        reporters.append(reporter)
    return reporters


async def notify_begin(reporters: Iterable[Reporter], config: RunConfig) -> None:
    for reporter in reporters:
        await reporter.begin(config)


async def notify_case(reporters: Iterable[Reporter], result: CaseResult) -> None:
    for reporter in reporters:
        await reporter.emit_case(result)


async def notify_complete(reporters: Iterable[Reporter], summary: EvalSummary) -> None:
    for reporter in reporters:
        await reporter.complete(summary)


__all__ = [
    "ConsoleReporter",
    "JsonReporter",
    "build_reporters",
    "notify_begin",
    "notify_case",
    "notify_complete",
]
