#!/usr/bin/env python3
"""
Hard delete quarantined tests that have aged beyond the threshold.

Deletes tests that have been quarantined for >= N days without reinstatement.
"""

import argparse
import csv
import datetime
import pathlib
import subprocess
import sys

QUEUE = pathlib.Path("metrics/retirement_queue.csv")


def run(cmd):
    """Run command and return result"""
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser(description="Hard delete aged quarantined tests")
    ap.add_argument("--days", type=int, default=14, help="Days to wait before deletion")
    ap.add_argument("--apply", action="store_true", help="Actually perform deletions")
    args = ap.parse_args()

    assert QUEUE.exists(), f"Missing {QUEUE}"
    rows = list(csv.DictReader(QUEUE.open()))
    today = datetime.date.today()

    to_delete = []
    for r in rows:
        if r.get("status") != "quarantined" or r.get("reinstated", "no") == "yes":
            continue
        fq = datetime.date.fromisoformat(r["first_quarantined_at"])
        if (today - fq).days >= args.days:
            to_delete.append(r["file"])

    if not to_delete:
        print("Nothing to delete.")
        return

    print("Planned deletions:")
    for f in to_delete:
        print("  rm", f)

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to remove and stage.")
        return

    for f in to_delete:
        res = run(["git", "rm", "-f", f])
        if res.returncode != 0:
            pathlib.Path(f).unlink(missing_ok=True)

    # Mark deleted_at & status
    today_s = today.isoformat()
    for r in rows:
        if r["file"] in to_delete:
            r["status"] = "deleted"
            r["deleted_at"] = today_s

    with QUEUE.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\nStaged deletions. Commit and push.")


if __name__ == "__main__":
    main()
