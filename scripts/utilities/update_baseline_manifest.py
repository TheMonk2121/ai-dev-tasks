from __future__ import annotations

import argparse
import json
import os
from glob import glob
from statistics import median
from typing import Any, Optional, Union

#!/usr/bin/env python3
"""
Update Baseline Manifest per profile.

Reads recent evaluation results and produces config/baselines/<profile>.json with:
- targets: derived from gates (min → target for min-constrained metrics; max for latency)
- ema: exponential moving average of observed metrics (precision, recall, f1, latency_ms) over a window
- gates: copied from config/ragchecker_quality_gates.json

This lightweight manifest is consumed by the ABP and CI to surface current position vs thresholds.
"""

def _safe_load(path: str) -> dict[str, Any] | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _collect_results(results_dir: str, window: int) -> list[dict[str, Any]]:
    files = sorted(glob(os.path.join(results_dir, "*.json")), key=os.path.getmtime, reverse=True)
    out: list[dict[str, Any]] = []
    for fp in files[: max(window, 1)]:
        data = _safe_load(fp)
        if data:
            out.append(data)
    return out

def _get_overall(metrics_obj: dict[str, Any]) -> dict[str, float]:
    overall = metrics_obj.get("overall_metrics", {})
    # Normalize keys
    return {
        "precision": float(overall.get("precision", 0.0) or 0.0),
        "recall": float(overall.get("recall", 0.0) or 0.0),
        "f1": float(overall.get("f1_score", overall.get("f1", 0.0)) or 0.0),
        # Latency best-effort: allow either ms or s fields if available
        "latency_ms": float(overall.get("latency_ms", 0.0) or 0.0),
    }

def _ema(values: list[float], alpha: float = 0.3) -> float:
    if not values:
        return 0.0
    acc = values[0]
    for v in values[1:]:
        acc = alpha * v + (1 - alpha) * acc
    return acc

def main() -> int:
    parser = argparse.ArgumentParser(description="Update Baseline Manifest for a profile")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--results-dir", default="metrics/baseline_evaluations")
    parser.add_argument("--gates", default="config/ragchecker_quality_gates.json")
    parser.add_argument("--window", type=int, default=10)
    parser.add_argument("--out-dir", default="config/baselines")

    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, f"{args.profile}.json")

    gates = _safe_load(args.gates) or {}
    recent = _collect_results(args.results_dir, args.window)

    # Gather series
    prec = [_get_overall(r).get("precision", 0.0) for r in recent if isinstance(r, dict)]
    rec = [_get_overall(r).get("recall", 0.0) for r in recent if isinstance(r, dict)]
    f1 = [_get_overall(r).get("f1", 0.0) for r in recent if isinstance(r, dict)]
    lat_ms = [
        _get_overall(r).get("latency_ms", 0.0)
        for r in recent
        if isinstance(r, dict) and _get_overall(r).get("latency_ms", 0.0) > 0
    ]

    manifest: dict[str, Any] = {
        "targets": {},
        "ema": {},
        "gates": gates,
        "window": args.window,
    }

    # Targets from gates (single source of truth)
    for k, v in gates.items():
        if not isinstance(v, dict):
            continue
        if "min" in v:
            manifest["targets"][k] = v["min"]
        elif "max" in v:
            manifest["targets"][k] = v["max"]

    # EMA values for trend awareness
    if prec:
        manifest["ema"]["precision"] = round(_ema(list(reversed(prec))), 6)
    if rec:
        manifest["ema"]["recall"] = round(_ema(list(reversed(rec))), 6)
    if f1:
        manifest["ema"]["f1"] = round(_ema(list(reversed(f1))), 6)
    if lat_ms:
        manifest["ema"]["latency_ms"] = round(_ema(list(reversed(lat_ms))), 3)

    # Store medians as a side-car for reference
    if prec:
        manifest["median_precision"] = round(median(prec), 6)
    if rec:
        manifest["median_recall"] = round(median(rec), 6)
    if f1:
        manifest["median_f1"] = round(median(f1), 6)
    if lat_ms:
        manifest["median_latency_ms"] = round(median(lat_ms), 3)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(out_path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
