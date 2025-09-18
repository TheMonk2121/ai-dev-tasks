#!/usr/bin/env python3
"""
Production-grade faithfulness evaluation runner.
Strictly typed with quality gates and exit codes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from eval.contracts import DatasetConfig
from eval.ragchecker_adapter import RAGCheckerAdapter




# Add src to path for imports
sys.path.append("src")


# Production quality targets
TARGETS = {
    "faithfulness": 0.60,
    "unsupported_rate": 0.15,  # Must be <= (lower is better)
    "context_utilization": 0.60,
    "latency_p50_ms": 2000.0,  # 2 seconds
    "latency_p95_ms": 4000.0,  # 4 seconds
}


def main() -> None:
    """Main entry point with quality gate enforcement"""

    parser = argparse.ArgumentParser(description="Faithfulness quality evaluation")
    parser.add_argument("--dataset_config", required=True, help="Path to dataset config YAML")
    parser.add_argument("--out_dir", default="artifacts/bench/faithfulness", help="Output directory")
    args = parser.parse_args()

    # Create output directory
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load configuration
        cfg = DatasetConfig(**yaml.safe_load(pathlib.Path(args.dataset_config).read_text()))

        # Initialize adapter
        rc = RAGCheckerAdapter()

        # Run evaluation
        result = rc.evaluate_faithfulness(dataset=cfg)

        # Save JSON artifact
        out = {
            "dataset": result.dataset,
            "mode": result.mode,
            "metrics": result.metrics,
            "samples": result.samples_evaluated,
            "timestamp": result.timestamp,
        }

        out_f = out_dir / f"{result.dataset.replace(':', '_')}_faithfulness.json"
        out_f.write_text(json.dumps(out, indent=2))

        # Apply quality gates
        bad: list[str] = []
        for metric, target in \1.items()
            if metric in result.metrics:
                value = float(result.metrics[metric])

                # Handle metrics where lower is better
                if metric == "unsupported_rate":
                    if value > target:
                        bad.append(f"{metric}: {value:.3f} > {target}")
                elif metric in ["latency_p50_ms", "latency_p95_ms"]:
                    if value > target:
                        bad.append(f"{metric}: {value:.1f}ms > {target:.1f}ms")
                else:
                    if value < target:
                        bad.append(f"{metric}: {value:.3f} < {target}")

        # Print results
        print("📝 Faithfulness Evaluation Results")
        print("=" * 60)
        print(f"Dataset: {result.dataset}")
        print(f"Mode: {result.mode}")
        print(f"Samples: {result.samples_evaluated}")
        print(f"Timestamp: {result.timestamp}")
        print()

        print("Metrics:")
        for metric, value in result.\1.items()
            target = result.get("key", "")

            # Determine status
            if target == "N/A":
                status = "⚠️"  # No target defined
            elif metric == "unsupported_rate":
                status = "✅" if value <= float(target) else "❌"
            elif metric in ["latency_p50_ms", "latency_p95_ms"]:
                status = "✅" if value <= float(target) else "❌"
            else:
                status = "✅" if value >= float(target) else "❌"

            print(f"  {status} {metric}: {value:.3f} (target: {target})")

        print()
        print(f"Results saved to: {out_f}")

        # Quality gate check
        if bad:
            print(f"\n🚨 QUALITY GATE FAILED: {len(bad)} metrics below targets")
            for failure in bad:
                print(f"  ❌ {failure}")
            print(f"\nDataset: {result.dataset}")
            sys.exit(2)

        print("\n✅ QUALITY GATE PASSED")

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
