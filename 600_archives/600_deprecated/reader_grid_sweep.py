#!/usr/bin/env python3
"""
Sweep DSPy reader abstention/precision flags and report micro-F1 deltas.

Reuses the reader gate's evaluation path (retrieval→context→READER_CMD).
"""

import argparse
import json
import os
import sys
import time
from copy import deepcopy
from typing import Any

# Bootstrap path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _bootstrap import ROOT, SRC  # noqa: F401

sys.path.insert(0, str(SRC))

from scripts.migrate_to_pydantic_evals import load_eval_cases

# Import reader gate helpers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.ci_gate_reader import eval_reader, load_v1_reader_cases_and_gold  # type: ignore

Config = dict[str, Any]

def run_config(config: Config, cases, gold) -> dict[str, Any]:
    """Run reader eval for a single env config and return metrics + timing."""
    keys = [
        "READER_CMD",
        "READER_ABSTAIN",
        "READER_ENFORCE_SPAN",
        "READER_PRECHECK",
        "READER_PRECHECK_MIN_OVERLAP",
        "READER_COMPACT",
    ]
    old_env = {k: os.environ.get(k) for k in keys}
    try:
        for k, v in config.items():
            os.environ[str(k)] = str(v)
        t0 = time.time()
        metrics = eval_reader(cases, gold)
        metrics["duration_s"] = round(time.time() - t0, 2)
        return metrics
    finally:
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

def default_grid(cmd: str) -> list[Config]:
    base = {
        "READER_CMD": cmd,
        "READER_COMPACT": os.getenv("READER_COMPACT", "1"),
    }
    configs: list[Config] = []
    for abstain in (1, 0):
        for enforce in (1, 0):
            for precheck, overlap in ((1, 0.10), (1, 0.05), (0, 0.0)):
                cfg = deepcopy(base)
                cfg.update(
                    {
                        "READER_ABSTAIN": abstain,
                        "READER_ENFORCE_SPAN": enforce,
                        "READER_PRECHECK": precheck,
                        "READER_PRECHECK_MIN_OVERLAP": overlap,
                    }
                )
                configs.append(cfg)
    return configs

def main() -> None:
    ap = argparse.ArgumentParser(description="DSPy reader grid sweep for micro-F1")
    ap.add_argument("--gold-file", default=os.getenv("GOLD_FILE", "evals/gold/v1/gold_cases.jsonl"))
    ap.add_argument("--cmd", default=os.getenv("READER_CMD", "python3 scripts/run_dspy_reader.py"))
    ap.add_argument("--out", help="Write JSON summary to this path")
    args = ap.parse_args()

    # Load v1 reader cases once
    cases, gold = load_v1_reader_cases_and_gold(args.gold_file)

    # Build grid
    configs = default_grid(args.cmd)

    # Evaluate each config
    results: list[tuple[Config, dict[str, Any]]] = []
    for cfg in configs:
        metrics = run_config(cfg, cases, gold)
        results.append((cfg, metrics))

    baseline_micro = results[0][1].get("micro", 0.0)

    print("Config\tmicro\tΔmicro\tmacro\tmissing\tduration(s)")
    best = (None, -1.0)  # (index, micro)
    for i, (cfg, met) in enumerate(results):
        micro = met.get("micro", 0.0)
        macro = met.get("macro", 0.0)
        missing = met.get("missing", 0)
        dur = met.get("duration_s", 0.0)
        delta = micro - baseline_micro
        label = (
            f"A={cfg['READER_ABSTAIN']} S={cfg['READER_ENFORCE_SPAN']} "
            f"P={cfg['READER_PRECHECK']}@{cfg['READER_PRECHECK_MIN_OVERLAP']}"
        )
        print(f"{label}\t{micro:.3f}\t{delta:+.3f}\t{macro:.3f}\t{missing}\t{dur:.2f}")
        if micro > best[1]:
            best = (i, micro)

    if best[0] is not None:
        cfg, met = results[best[0]]
        print("\nBest config:")
        print(json.dumps({"config": cfg, "metrics": met}, indent=2))

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        payload = {
            "baseline_micro": baseline_micro,
            "results": [{"config": cfg, "metrics": met} for cfg, met in results],
        }
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

if __name__ == "__main__":
    main()
