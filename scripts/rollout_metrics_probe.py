#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def load_latest(results_dir: Path) -> dict[str, Any]:
    files = sorted(results_dir.glob("ragchecker_clean_evaluation_*.json"))
    if not files:
        raise FileNotFoundError(f"No results found in {results_dir}")
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def p50_p95_latency(results: dict[str, Any]) -> tuple[float, float]:
    cases = results.get("case_results", [])
    vals = [float(c.get("timing_sec", 0.0)) for c in cases if c.get("timing_sec") is not None]
    if not vals:
        return 0.0, 0.0
    vals_sorted = sorted(vals)
    p50 = statistics.median(vals_sorted)
    idx95 = max(0, int(round(0.95 * (len(vals_sorted) - 1))))
    p95 = vals_sorted[idx95]
    return p50, p95


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="metrics/runs", help="Directory with profile run outputs")
    args = ap.parse_args()

    runs = sorted(Path(args.dir).glob("*/ragchecker_clean_evaluation_*.json"))
    if not runs:
        raise SystemExit("No evaluation result artifacts found")

    # Print summary for latest run under each profile dir
    for run_file in runs[-3:]:
        results = json.loads(Path(run_file).read_text())
        overall = results.get("overall_metrics", {})
        p50, p95 = p50_p95_latency(results)
        print(
            json.dumps(
                {
                    "file": str(run_file),
                    "precision": overall.get("precision", 0.0),
                    "recall": overall.get("recall", 0.0),
                    "f1": overall.get("f1_score", 0.0),
                    "p50": p50,
                    "p95": p95,
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
