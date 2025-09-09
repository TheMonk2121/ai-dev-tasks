#!/usr/bin/env python3
"""
ABP and Baseline Manifest Validation

Checks:
- Baseline Manifest exists for profile and is fresh (mtime <= max_age_days)
- Latest ABP exists and references (optional) decision docket

Usage:
  python3 scripts/abp_validation.py --profile precision_elevated --max-age-days 2 [--ci-mode] [--strict]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import time
from typing import Any


def _fresh(path: str, max_age_days: int) -> bool:
    try:
        mtime = os.path.getmtime(path)
        age_days = (time.time() - mtime) / 86400.0
        return age_days <= max_age_days
    except Exception:
        return False


def _load(path: str) -> dict[str, Any] | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ABP and Baseline Manifest")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--max-age-days", type=int, default=2)
    parser.add_argument("--ci-mode", action="store_true", help="Print GitHub Actions warnings instead of failing")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors (fail on stale/missing)")
    args = parser.parse_args()

    # Check baseline manifest
    manifest = os.path.join("config", "baselines", f"{args.profile}.json")
    issues = []  # collected human-readable issues
    if not os.path.exists(manifest):
        issues.append(f"Missing Baseline Manifest: {manifest}")
    elif not _fresh(manifest, args.max_age_days):
        issues.append(f"Stale Baseline Manifest (> {args.max_age_days} days): {manifest}")
    if not os.path.exists(manifest):
        print(f"❌ Missing Baseline Manifest: {manifest}")
        print("   Run: python3 scripts/update_baseline_manifest.py --profile", args.profile)
        if args.ci_mode:
            print(f"::warning ::ABP validation: Missing Baseline Manifest for profile {args.profile}")
        if args.strict:
            return 1
        else:
            return 1
    elif not _fresh(manifest, args.max_age_days):
        msg = f"⚠️ Stale Baseline Manifest (> {args.max_age_days} days): {manifest}"
        print(msg)
        if args.ci_mode:
            print(f"::warning ::ABP validation: {msg}")
        if args.strict:
            return 1
    else:
        print(f"✅ Baseline Manifest OK: {manifest}")

    # Find most recent ABP
    abps = sorted(
        glob.glob(os.path.join("metrics", "briefings", f"*_ {args.profile}_ABP.md").replace(" _", "_")),
        key=os.path.getmtime,
        reverse=True,
    )
    if not abps:
        msg = "No ABP files found. They are generated during evaluation runs."
        print(f"⚠️ {msg}")
        if args.ci_mode:
            print(f"::warning ::ABP validation: {msg}")
        if args.strict:
            return 1
        return 0
    latest_abp = abps[0]
    print(f"✅ Latest ABP: {latest_abp}")

    # Optionally check that context meta sidecar exists for latest results
    metas = sorted(
        glob.glob(os.path.join("metrics", "baseline_evaluations", "*_context_meta.json")),
        key=os.path.getmtime,
        reverse=True,
    )
    if metas:
        meta = _load(metas[0]) or {}
        if meta.get("abp_path") and os.path.exists(str(meta.get("abp_path"))):
            print("✅ Context meta references ABP")
        else:
            msg = "Latest context meta does not reference an ABP"
            print(f"⚠️ {msg}")
            if args.ci_mode:
                print(f"::warning ::ABP validation: {msg}")
            if args.strict:
                return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
