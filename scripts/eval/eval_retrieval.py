#!/usr/bin/env python3
"""
Production-grade retrieval evaluation runner.
Strictly typed with quality gates and exit codes.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import List

import yaml

# Add src to path for imports
sys.path.append("dspy-rag-system/src")

from eval.contracts import DatasetConfig, RunMetrics
from eval.ragchecker_adapter import RAGCheckerAdapter

# Production quality targets
TARGETS = {
    "R@20": 0.65,
    "MRR@10": 0.30,
    "nDCG@10": 0.40,
    "precision_at_k": 0.20,
    "latency_p50_ms": 2000.0,  # 2 seconds
    "latency_p95_ms": 4000.0,  # 4 seconds
}


def run(cfg_path: str) -> List[RunMetrics]:
    """Run retrieval evaluation with quality gates"""

    # Load configuration
    cfg_d = yaml.safe_load(pathlib.Path(cfg_path).read_text())
    ds = DatasetConfig(**cfg_d)

    # Initialize adapter
    rc = RAGCheckerAdapter()

    # Run evaluations for different modes
    runs: List[RunMetrics] = []

    # Dense retrieval
    dense = rc.evaluate_retrieval(dataset=ds, mode="dense")
    runs.append(dense)

    # Hybrid rerank (if available)
    hybrid = rc.evaluate_retrieval(dataset=ds, mode="hybrid_rerank")
    runs.append(hybrid)

    return runs


def main() -> None:
    """Main entry point with quality gate enforcement"""

    parser = argparse.ArgumentParser(description="Retrieval quality evaluation")
    parser.add_argument("--dataset_config", required=True, help="Path to dataset config YAML")
    parser.add_argument("--out_dir", default="artifacts/bench/retrieval", help="Output directory")
    parser.add_argument("--mode", choices=["dense", "hybrid_rerank"], default="hybrid_rerank", help="Evaluation mode")
    args = parser.parse_args()

    # Create output directory
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Run evaluation
        runs = run(args.dataset_config)

        # Find the target run
        target_run = next((r for r in runs if r.mode == args.mode), runs[0])

        # Save JSON artifact
        out = {
            "dataset": target_run.dataset,
            "mode": target_run.mode,
            "runs": {r.mode: r.metrics for r in runs},
            "samples": sum(r.samples_evaluated for r in runs),
            "timestamp": target_run.timestamp,
        }

        out_f = out_dir / f"{target_run.dataset.replace(':', '_')}_{args.mode}.json"
        out_f.write_text(json.dumps(out, indent=2))

        # Apply quality gates
        misses: list[str] = []
        for metric, target in TARGETS.items():
            if metric in target_run.metrics:
                value = float(target_run.metrics[metric])
                if value < target:
                    misses.append(f"{metric}: {value:.3f} < {target}")

        # Print results
        print(f"📊 Retrieval Evaluation Results ({target_run.mode})")
        print("=" * 60)
        print(f"Dataset: {target_run.dataset}")
        print(f"Samples: {target_run.samples_evaluated}")
        print(f"Timestamp: {target_run.timestamp}")
        print()

        print("Metrics:")
        for metric, value in target_run.metrics.items():
            target = TARGETS.get(metric, "N/A")
            status = "✅" if metric not in TARGETS or value >= TARGETS[metric] else "❌"
            print(f"  {status} {metric}: {value:.3f} (target: {target})")

        print()
        print(f"Results saved to: {out_f}")

        # Quality gate check
        if misses:
            print(f"\n🚨 QUALITY GATE FAILED: {len(misses)} metrics below targets")
            for miss in misses:
                print(f"  ❌ {miss}")
            print(f"\nDataset: {target_run.dataset}")
            print(f"Mode: {target_run.mode}")
            sys.exit(2)

        print("\n✅ QUALITY GATE PASSED")

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
