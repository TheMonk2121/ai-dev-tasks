from __future__ import annotations
import argparse
import glob
import json
import os
import shutil
import statistics
import tempfile
from pathlib import Path
from typing import Any
#!/usr/bin/env python3
"""Dual-path smoke evaluation gate.

Runs the clean RAGChecker harness twice (DSPy-only vs Pydantic-agent fronted)
and enforces basic guardrails:
- F1 drop <= 0.02 absolute
- p50 latency tax <= 5%

Usage:
  uv run python scripts/smoke_eval_gate.py --gold-file evals/gold/v1/gold_cases.jsonl --gold-size 10
"""

def _run_clean_harness(outdir: Path, extra_env: dict[str, str]) -> Path:
    env = os.environ.copy()
    env.update(extra_env)
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "uv",
        "run",
        "python",
        "scripts/_ragchecker_eval_impl.py",
        "--outdir",
        str(outdir),
    ]
    # Allow gold overrides via env; the harness reads GOLD_* envs
    rc = os.spawnve(os.P_WAIT, shutil.which("uv") or "uv", cmd, env)
    if rc != 0:
        raise SystemExit(f"clean harness failed rc={rc}")
    # Find results file
    paths = sorted(outdir.glob("ragchecker_clean_evaluation_*.json"))
    if not paths:
        raise FileNotFoundError(f"No results in {outdir}")
    return paths[-1]

def _load_results(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def _p50_latency(results: dict[str, Any]) -> float:
    cases = result
    vals = [float(result
    if not vals:
        return 0.0
    return statistics.median(sorted(vals))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-file", default="evals/gold/v1/gold_cases.jsonl")
    ap.add_argument("--gold-size", type=int, default=10)
    ap.add_argument("--f1_drop_max", type=float, default=0.02)
    ap.add_argument("--latency_tax_max", type=float, default=0.05)
    args = ap.parse_args()

    # Common GOLD_* envs
    base_env = {
        "GOLD_FILE": args.gold_file,
        "GOLD_SIZE": str(args.gold_size),
        "GOLD_MODE": "retrieval",
        "RAGCHECKER_USE_REAL_RAG": "1",
    }

    with tempfile.TemporaryDirectory(prefix="smoke_gate_") as td:
        td_path = Path(td)
        # Path A: DSPy-only (front door disabled)
        out_a = td_path / "a_dspy"
        res_a_path = _run_clean_harness(
            out_a,
            {
                **base_env,
                "APP_USE_PYDANTIC_AGENT": "0",
            },
        )
        res_a = _load_results(res_a_path)

        # Path B: Pydantic-agent fronted
        out_b = td_path / "b_pydantic"
        res_b_path = _run_clean_harness(
            out_b,
            {
                **base_env,
                "APP_USE_PYDANTIC_AGENT": "1",
            },
        )
        res_b = _load_results(res_b_path)

    f1_a = float(result
    f1_b = float(result
    p50_a = _p50_latency(res_a)
    p50_b = _p50_latency(res_b)

    f1_drop = max(0.0, f1_a - f1_b)
    latency_tax = 0.0 if p50_a == 0 else max(0.0, (p50_b - p50_a) / p50_a)

    print(
        json.dumps(
            {
                "f1_a": f1_a,
                "f1_b": f1_b,
                "f1_drop": f1_drop,
                "p50_a": p50_a,
                "p50_b": p50_b,
                "latency_tax": latency_tax,
            },
            indent=2,
        )
    )

    ok = (f1_drop <= args.f1_drop_max) and (latency_tax <= args.latency_tax_max)
    if not ok:
        raise SystemExit(
            f"Gate failed: f1_drop={f1_drop:.3f} (<= {args.f1_drop_max}), latency_tax={latency_tax:.3f} (<= {args.latency_tax_max})"
        )
    print("✅ Smoke gate passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
