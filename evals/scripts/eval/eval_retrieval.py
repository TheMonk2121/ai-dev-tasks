#!/usr/bin/env python3
"""Production retrieval evaluation runner with quality gates."""

from __future__ import annotations

import argparse
import json
import sys
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

if TYPE_CHECKING:  # pragma: no cover - assist static typing
    from src.evaluation.adapters.ragchecker import RagCheckerAdapter
    from src.evaluation.contracts import DatasetConfig

    class RunMetrics(Protocol):
        mode: str
        dataset: str
        metrics: dict[str, float]
        samples_evaluated: int
        timestamp: str
else:
    try:
        from src.evaluation.contracts import DatasetConfig
        from src.evaluation.adapters.ragchecker import RagCheckerAdapter
    except ImportError:  # pragma: no cover - legacy fallback
        contracts_module = import_module("eval.contracts")
        DatasetConfig = getattr(contracts_module, "DatasetConfig")
        RunMetrics = getattr(contracts_module, "RunMetrics")
        RagCheckerAdapter = getattr(import_module("eval.ragchecker_adapter"), "RAGCheckerAdapter")
    else:
        RunMetrics = Any

TARGETS: dict[str, float] = {
    "R@20": 0.65,
    "MRR@10": 0.30,
    "nDCG@10": 0.40,
    "precision_at_k": 0.20,
    "latency_p50_ms": 2000.0,
    "latency_p95_ms": 4000.0,
}


def run(cfg_path: str) -> list[RunMetrics]:
    """Execute retrieval evaluations for available modes."""

    cfg_data = yaml.safe_load(Path(cfg_path).read_text())
    dataset_cfg = DatasetConfig(**cfg_data)

    adapter = RagCheckerAdapter()
    runs: list[RunMetrics] = []
    runs.append(adapter.evaluate_retrieval(dataset=dataset_cfg, mode="dense"))
    runs.append(adapter.evaluate_retrieval(dataset=dataset_cfg, mode="hybrid_rerank"))
    return runs


def main() -> None:
    """Run retrieval evaluation and enforce quality targets."""

    parser = argparse.ArgumentParser(description="Retrieval quality evaluation")
    parser.add_argument("--dataset_config", required=True, help="Path to dataset config YAML")
    parser.add_argument(
        "--out_dir",
        default="artifacts/bench/retrieval",
        help="Directory for JSON artifacts",
    )
    parser.add_argument(
        "--mode",
        choices=["dense", "hybrid_rerank"],
        default="hybrid_rerank",
        help="Which mode to inspect for gating",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        runs = run(args.dataset_config)
        target_run = next((run for run in runs if run.mode == args.mode), runs[0])

        artifact = {
            "dataset": target_run.dataset,
            "mode": target_run.mode,
            "runs": {run.mode: run.metrics for run in runs},
            "samples": sum(run.samples_evaluated for run in runs),
            "timestamp": target_run.timestamp,
        }
        artifact_path = out_dir / f"{target_run.dataset.replace(':', '_')}_{args.mode}.json"
        artifact_path.write_text(json.dumps(artifact, indent=2))

        misses: list[str] = []
        for metric, target in TARGETS.items():
            raw_value = target_run.metrics.get(metric)
            if raw_value is None:
                continue
            value = float(raw_value)
            if value < target:
                misses.append(f"{metric}: {value:.3f} < {target}")

        print(f"📊 Retrieval Evaluation Results ({target_run.mode})")
        print("=" * 60)
        print(f"Dataset: {target_run.dataset}")
        print(f"Samples: {target_run.samples_evaluated}")
        print(f"Timestamp: {target_run.timestamp}")
        print()

        print("Metrics:")
        for metric, raw_value in target_run.metrics.items():
            value = float(raw_value)
            target = TARGETS.get(metric)
            status = "✅" if target is None or value >= target else "❌"
            target_display = f"{target:.3f}" if isinstance(target, float) else "N/A"
            print(f"  {status} {metric}: {value:.3f} (target: {target_display})")

        print()
        print(f"Results saved to: {artifact_path}")

        if misses:
            print(f"\n🚨 QUALITY GATE FAILED: {len(misses)} metrics below targets")
            for miss in misses:
                print(f"  ❌ {miss}")
            print(f"\nDataset: {target_run.dataset}")
            print(f"Mode: {target_run.mode}")
            sys.exit(2)

        print("\n✅ QUALITY GATE PASSED")
    except Exception as exc:  # pragma: no cover - defensive
        print(f"❌ Evaluation failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
