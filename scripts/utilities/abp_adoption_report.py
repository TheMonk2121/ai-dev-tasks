from __future__ import annotations
import argparse
import glob
import json
import os
from typing import Any
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
ABP Adoption Report

Scans metrics/baseline_evaluations/*_context_meta.json and reports:
- Carry-over rate: fraction of runs with suggested/applied lessons > 0
- ABP presence rate: fraction of runs with an ABP emitted
- Basic counts of applied vs suggested lesson IDs

Usage:
  python3 scripts/abp_adoption_report.py --window 20
"""

def _load(path: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def main() -> int:
    parser = argparse.ArgumentParser(description="ABP Adoption Report")
    parser.add_argument("--dir", default="metrics/baseline_evaluations")
    parser.add_argument("--window", type=int, default=50)
    args = parser.parse_args()

    meta_files = sorted(glob.glob(os.path.join(args.dir, "*_context_meta.json")), key=os.path.getmtime, reverse=True)
    meta_files = meta_files[: args.window]
    if not meta_files:
        print("⚠️ No context meta files found. Run some evaluations first.")
        return 0

    total = len(meta_files)
    with_abp = 0
    carry_over = 0
    applied_count = 0
    suggested_count = 0

    for fp in meta_files:
        obj = _load(fp)
        if obj.get("abp_path") and os.path.exists(str(obj.get("abp_path"))):
            with_abp += 1
        if obj.get("carry_over"):
            carry_over += 1
        applied = obj.get("lessons_applied") or []
        suggested = obj.get("lessons_suggested") or []
        applied_count += len(applied)
        suggested_count += len(suggested)

    print("📊 ABP Adoption Report")
    print("======================")
    print(f"Window: last {total} runs")
    print(f"ABP presence rate: {with_abp}/{total} ({with_abp/total:.1%})")
    print(f"Carry-over rate:   {carry_over}/{total} ({carry_over/total:.1%})")
    print(f"Lessons applied (total):   {applied_count}")
    print(f"Lessons suggested (total): {suggested_count}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
