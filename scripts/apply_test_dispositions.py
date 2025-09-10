#!/usr/bin/env python3
"""
Apply test dispositions based on test signal analysis.

Moves low-signal tests to tests/legacy/ and manages retirement queue.
"""
import argparse
import csv
import datetime
import os
import pathlib
import subprocess
import sys

import yaml

CSV_IN = pathlib.Path("metrics/tests_signal.csv")
LEG_DIR = pathlib.Path("tests/legacy")
QUEUE = pathlib.Path("metrics/retirement_queue.csv")
SENTINELS = pathlib.Path("tests/sentinels.yml")


def run(cmd):
    """Run command and return result"""
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def load_sentinels():
    """Load sentinel tests that must never be quarantined"""
    if not SENTINELS.exists():
        return set()
    data = yaml.safe_load(SENTINELS.read_text()) or {}
    # May list file paths or nodeids; we normalize to file paths here
    keep = set()
    for item in data.get("keep", []):
        keep.add(item.split("::")[0])
    return keep


def main():
    ap = argparse.ArgumentParser(description="Apply test dispositions from signal analysis")
    ap.add_argument("--apply", action="store_true", help="perform git mv operations")
    ap.add_argument("--prune-clusters", action="store_true", help="also move non-representatives")
    ap.add_argument("--retire-threshold", type=float, default=0.3)
    args = ap.parse_args()

    assert CSV_IN.exists(), f"Missing {CSV_IN}"
    LEG_DIR.mkdir(parents=True, exist_ok=True)
    sentinels = load_sentinels()

    rows = list(csv.DictReader(CSV_IN.open()))
    moves = []
    today = datetime.date.today().isoformat()

    # Track files we've already planned to move to avoid duplicates
    planned_moves = set()

    for r in rows:
        tid = r["test_id"]
        decision = r.get("decision", "").lower()
        cluster_rep = r.get("cluster_rep", "0") in ("1", "true", "True")
        score = float(r.get("score", "0") or 0.0)
        fpath = tid.split("::")[0]

        # sentinel protection
        if fpath in sentinels:
            print(f"🛡️  Sentinel protected: {fpath}")
            continue

        # Skip if we've already planned to move this file
        if fpath in planned_moves:
            continue

        # Quarantine rule
        should_quarantine = (decision == "quarantine") or (args.prune_clusters and not cluster_rep)

        if should_quarantine:
            src = pathlib.Path(fpath)
            if not src.exists():
                continue
            dest = LEG_DIR / src.name
            if src.resolve() == dest.resolve():
                continue
            moves.append((str(src), str(dest), "quarantine", score))
            planned_moves.add(fpath)

        # Immediate retire (rare; only if decision says retire and below threshold)
        if decision == "retire" and score < args.retire_threshold:
            # We still quarantine first; hard delete handled by the queue cleaner.
            pass

    # Plan output
    if not moves:
        print("No moves planned.")
        return

    print("Planned moves:")
    for src, dest, reason, score in moves:
        print(f"  {src} -> {dest}  ({reason}, score={score:.3f})")

    # Update retirement queue
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    new_queue = []
    if QUEUE.exists():
        new_queue.extend(list(csv.DictReader(QUEUE.open())))
    existing = {(r["file"], r.get("status", "")) for r in new_queue}

    for src, dest, reason, score in moves:
        if (dest, "quarantined") in existing:
            continue
        new_queue.append(
            {
                "file": dest,
                "status": "quarantined",
                "first_quarantined_at": today,
                "score": f"{score:.3f}",
                "reason": reason,
                "reinstated": "no",
                "deleted_at": "",
            }
        )

    with QUEUE.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(new_queue[0].keys()))
        w.writeheader()
        w.writerows(new_queue)

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to move files.")
        return

    # Apply moves with git mv (fallback to os.rename)
    for src, dest, _, _ in moves:
        pathlib.Path(dest).parent.mkdir(parents=True, exist_ok=True)
        res = run(["git", "mv", src, dest])
        if res.returncode != 0:
            os.rename(src, dest)
    print("\nApplied quarantine moves. Commit these changes.")
    print("  git add -A && git commit -m 'Quarantine low-signal tests'")
    print("  git push")


if __name__ == "__main__":
    main()
