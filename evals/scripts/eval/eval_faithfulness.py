#!/usr/bin/env python3
"""Production faithfulness evaluation runner with quality gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

# Ensure local ``src`` package is importable before pulling evaluation helpers.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:
    from src.evaluation.contracts import DatasetConfig
    from src.evaluation.adapters.ragchecker import RagCheckerAdapter
except ImportError:
    from eval.contracts import DatasetConfig  # type: ignore  # pragma: no cover
    from eval.ragchecker_adapter import RAGCheckerAdapter as RagCheckerAdapter  # type: ignore  # pragma: no cover

# Production quality targets; values are floats so we can cast metrics safely.
TARGETS: dict[str, float] = {
    "faithfulness": 0.60,
    "unsupported_rate": 0.15,  # lower is better
    "context_utilization": 0.60,
    "latency_p50_ms": 2000.0,  # milliseconds, lower is better
    "latency_p95_ms": 4000.0,
}
LOWER_IS_BETTER = {"unsupported_rate", "latency_p50_ms", "latency_p95_ms"}


def main() -> None:
    """Run the faithfulness evaluation and enforce quality gates."""

    parser = argparse.ArgumentParser(description="Faithfulness quality evaluation")
    parser.add_argument("--dataset_config", required=True, help="Path to dataset config YAML")
    parser.add_argument(
        "--out_dir",
        default="artifacts/bench/faithfulness",
        help="Directory for JSON artifacts",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        cfg_data = yaml.safe_load(Path(args.dataset_config).read_text())
        cfg = DatasetConfig(**cfg_data)

        adapter = RAGCheckerAdapter()
        result = adapter.evaluate_faithfulness(dataset=cfg)

        artifact = {
            "dataset": result.dataset,
            "mode": result.mode,
            "metrics": result.metrics,
            "samples": result.samples_evaluated,
            "timestamp": result.timestamp,
        }
        artifact_path = out_dir / f"{result.dataset.replace(':', '_')}_faithfulness.json"
        artifact_path.write_text(json.dumps(artifact, indent=2))

        failures: list[str] = []
        for metric, target in TARGETS.items():
            raw_value = result.metrics.get(metric)
            if raw_value is None:
                continue
            value = float(raw_value)
            if metric in LOWER_IS_BETTER:
                if value > target:
                    failures.append(f"{metric}: {value:.3f} > {target}")
            elif value < target:
                failures.append(f"{metric}: {value:.3f} < {target}")

        print("📝 Faithfulness Evaluation Results")
        print("=" * 60)
        print(f"Dataset: {result.dataset}")
        print(f"Mode: {result.mode}")
        print(f"Samples: {result.samples_evaluated}")
        print(f"Timestamp: {result.timestamp}")
        print()

        print("Metrics:")
        for metric, raw_value in result.metrics.items():
            value = float(raw_value)
            target = TARGETS.get(metric)
            if target is None:
                status = "⚠️"
            elif metric in LOWER_IS_BETTER:
                status = "✅" if value <= target else "❌"
            else:
                status = "✅" if value >= target else "❌"
            target_display = f"{target:.3f}" if isinstance(target, float) else "N/A"
            print(f"  {status} {metric}: {value:.3f} (target: {target_display})")

        print()
        print(f"Results saved to: {artifact_path}")

        if failures:
            print(f"\n🚨 QUALITY GATE FAILED: {len(failures)} metrics below targets")
            for failure in failures:
                print(f"  ❌ {failure}")
            print(f"\nDataset: {result.dataset}")
            sys.exit(2)

        print("\n✅ QUALITY GATE PASSED")
    except Exception as exc:  # pragma: no cover - defensive
        print(f"❌ Evaluation failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
