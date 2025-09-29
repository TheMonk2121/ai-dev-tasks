#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_micro_f1(path: Path) -> float:
    data = json.loads(path.read_text())
    # Prefer our overall_metrics->f1_score; fallback to metrics.micro_f1
    if isinstance(data, dict):
        if "overall_metrics" in data:
            return float(data["overall_metrics"]["f1_score"])
        if "metrics" in data and isinstance(data["metrics"], dict):
            if "micro_f1" in data["metrics"]:
                return float(data["metrics"]["micro_f1"])
    raise KeyError("No F1 metric found in summary JSON")
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("off_summary")
    ap.add_argument("on_summary")
    ap.add_argument("--threshold", type=float, default=0.01)
    args = ap.parse_args()

    off = Path(args.off_summary)
    on = Path(args.on_summary)
    f1_off = read_micro_f1(off)
    f1_on = read_micro_f1(on)
    delta = f1_on - f1_off
    print(f"[reranker-uplift] OFF={f1_off:.3f} ON={f1_on:.3f} Δ={delta:.3f} (threshold={args.threshold:.3f})")
    if delta < args.threshold:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())