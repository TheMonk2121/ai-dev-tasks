from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from src.evaluation.contracts import (  # type: ignore[import-untyped]
    CaseInput,
    CaseResult,
    RunConfig,
)
from src.evaluation.errors import ProviderError  # type: ignore[import-untyped]

try:
    from scripts.evaluation.ragchecker_official_evaluation import (  # type: ignore[import-untyped]
        OfficialRAGCheckerEvaluator,
    )
except Exception as exc:  # pragma: no cover - import errors should surface during prepare
    OfficialRAGCheckerEvaluator = exc  # type: ignore[assignment]


class RagCheckerAdapter:
    """Adapter that wraps the legacy OfficialRAGCheckerEvaluator."""

    def __init__(self, outdir: Path | None = None) -> None:
        self._base_outdir: Path = Path(outdir or "metrics/baseline_evaluations")
        self._run_dir: Path | None = None
        self._case_inputs: list[CaseInput] = []
        self._results: list[CaseResult] = []
        self._metrics: Mapping[str, float] = {}
        self._prepared: bool = False
        self._artifact_path: Path | None = None

    async def prepare(self, config: RunConfig) -> None:  # type: ignore[arg-type]
        if isinstance(OfficialRAGCheckerEvaluator, Exception):  # pragma: no cover - surfaced at runtime
            raise ProviderError(f"Unable to import RAGChecker evaluator: {OfficialRAGCheckerEvaluator}")

        self._run_dir = self._base_outdir / config.run_id
        _ = self._run_dir.mkdir(parents=True, exist_ok=True)

        for key, value in config.environment.items():
            _ = os.environ.setdefault(key, value)

        raw_cases = _load_raw_cases(config.dataset)
        if config.limit is not None and config.limit < len(raw_cases):
            raw_cases = raw_cases[: config.limit]
            if self._run_dir is None:
                raise ProviderError("Run directory not initialized")
            dataset_path = self._run_dir / "cases.limited.jsonl"
            _write_jsonl(dataset_path, raw_cases)
            dataset_for_eval = dataset_path
        else:
            dataset_for_eval = config.dataset

        self._case_inputs = _to_case_inputs(raw_cases)

        evaluator = OfficialRAGCheckerEvaluator()
        results = await asyncio.to_thread(
            evaluator.run_official_evaluation,
            str(dataset_for_eval),
            str(self._run_dir),
        )

        self._metrics = _overall_metrics(results.get("overall_metrics", {}))
        self._results = _results_to_cases(results.get("case_results", []), self._case_inputs)
        self._artifact_path = _discover_artifact(self._run_dir)
        self._prepared = True

    async def run_case(self, case: CaseInput) -> CaseResult:  # type: ignore[arg-type,return-type]
        if not self._prepared:
            raise ProviderError("RagCheckerAdapter used before prepare() completes")
        if not self._results:
            raise ProviderError("No remaining case results to emit")

        # Align results by original order; adjust ID to match requested case
        result = self._results.pop(0)
        if result.case_id != case.case_id:
            result = CaseResult(
                case_id=case.case_id,
                metrics=result.metrics,
                latency_ms=result.latency_ms,
                verdict=result.verdict,
                artifacts=result.artifacts,
                spans=result.spans,
            )
        return result

    async def finalize(self, results: Sequence[CaseResult]) -> Mapping[str, float]:  # noqa: D401  # type: ignore[arg-type]
        _ = results  # Parameter required by protocol but not used in this implementation
        if not self._prepared:
            raise ProviderError("RagCheckerAdapter used before prepare() completes")
        return self._metrics

    def case_inputs(self) -> Sequence[CaseInput]:  # type: ignore[return-type]
        return tuple(self._case_inputs)

    def artifact_path(self) -> Path | None:
        return self._artifact_path


def _load_raw_cases(path: Path) -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = []
    if path.suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                data.append(json.loads(line))
        return data

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return [dict(item) for item in payload]
    if isinstance(payload, dict):
        cases = payload.get("cases") or payload.get("data") or []
        return [dict(item) for item in cases]

    raise ValueError(f"Unsupported dataset format from {path}")


def _write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            _ = handle.write(json.dumps(record, ensure_ascii=False))
            _ = handle.write("\n")


def _to_case_inputs(raw_cases: Sequence[Mapping[str, Any]]) -> list[CaseInput]:  # type: ignore[return-type]
    cases: list[CaseInput] = []
    for idx, record in enumerate(raw_cases):
        case_id = str(record.get("id") or record.get("query_id") or record.get("case_id") or idx)
        query = str(record.get("query", ""))
        gt_answer = str(record.get("gt_answer", ""))
        tags_data = record.get("tags")
        if isinstance(tags_data, (list, tuple)):
            tags = tuple(str(tag) for tag in tags_data)
        else:
            tags = ()
        metadata = {
            key: value
            for key, value in record.items()
            if key not in {"id", "query_id", "case_id", "query", "gt_answer", "tags"}
        }
        cases.append(CaseInput(case_id=case_id, query=query, ground_truth=gt_answer, tags=tags, metadata=metadata))
    return cases


def _results_to_cases(raw_results: Sequence[Mapping[str, Any]], expected_cases: Sequence[CaseInput]) -> list[CaseResult]:  # type: ignore[arg-type,return-type]
    results: list[CaseResult] = []
    for idx, record in enumerate(raw_results):
        case_id = str(
            record.get("case_id")
            or record.get("query_id")
            or (expected_cases[idx].case_id if idx < len(expected_cases) else idx)
        )
        metrics = _case_metrics(record)
        latency_ms = float(record.get("latency_sec", 0.0)) * 1000.0
        verdict = _verdict(record)
        results.append(
            CaseResult(
                case_id=case_id,
                metrics=metrics,
                latency_ms=latency_ms,
                verdict=verdict,
                artifacts={"raw": dict(record)},
                spans=(),
            )
        )
    return results


def _case_metrics(record: Mapping[str, Any]) -> Mapping[str, float]:
    metrics: dict[str, float] = {}
    for key in ("precision", "recall", "f1", "f1_score", "faithfulness"):
        value = record.get(key)
        if isinstance(value, (int, float)):
            metrics[key] = float(value)
    # fold nested metrics
    nested = record.get("metrics")
    if isinstance(nested, Mapping):
        for key, value in nested.items():
            if isinstance(value, (int, float)):
                metrics[f"metrics.{key}"] = float(value)
    return metrics


def _overall_metrics(record: Mapping[str, Any]) -> Mapping[str, float]:
    metrics: dict[str, float] = {}
    for key, value in record.items():
        if isinstance(value, (int, float)):
            metrics[key] = float(value)
    return metrics


def _verdict(record: Mapping[str, Any]) -> str:
    status = record.get("status")
    if isinstance(status, str) and status:
        return status
    precision = record.get("precision") or record.get("f1") or record.get("f1_score")
    try:
        if precision is not None and float(precision) > 0:
            return "success"
    except (TypeError, ValueError):
        pass
    return "unknown"


def _discover_artifact(run_dir: Path | None) -> Path | None:
    if run_dir is None:
        return None
    try:
        candidates = sorted(
            run_dir.glob("ragchecker_clean_evaluation_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except FileNotFoundError:
        return None
    return candidates[0] if candidates else None


__all__ = ["RagCheckerAdapter"]
