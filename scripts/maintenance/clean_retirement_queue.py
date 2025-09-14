from __future__ import annotations

import csv
import datetime as dt
import os
import pathlib
from pathlib import Path

#!/usr/bin/env python3
"""
Deduplicate metrics/retirement_queue.csv entries.

Rules:
- Keep exactly one row per (file, status=quarantined) with the earliest
  first_quarantined_at date.
- Preserve deleted rows as-is (historical record) and any non-quarantined statuses.
- For the kept quarantined row per file, prefer:
  - earliest first_quarantined_at
  - reason: first non-empty among grouped rows (fallback to "quarantine")
  - score: the maximum score string among grouped rows (informational only)
  - reinstated: "no" if any row says "no" (else keep original value)
  - deleted_at: empty for quarantined rows
"""

QUEUE = pathlib.Path("metrics/retirement_queue.csv")

def parse_date(s: str) -> dt.date:
    try:
        return dt.date.fromisoformat(s)
    except Exception:
        return dt.date.max

def main() -> int:
    assert QUEUE.exists(), f"Missing {QUEUE}"
    rows: list[dict[str, str]] = list(csv.DictReader(QUEUE.open()))

    # Preserve header order if present; else use canonical order
    header = (
        list(rows[0].keys())
        if rows
        else [
            "file",
            "status",
            "first_quarantined_at",
            "score",
            "reason",
            "reinstated",
            "deleted_at",
        ]
    )

    # Keep all non-quarantined rows as-is
    kept: list[dict[str, str]] = [r for r in rows if r.get("status") != "quarantined"]

    # Group quarantined rows by file
    by_file: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        if r.get("status") == "quarantined":
            by_file.setdefault(r.get("file", ""), []).append(r)

    for f, group in by_file.items():
        # Choose earliest quarantine date
        group_sorted = sorted(group, key=lambda r: parse_date(r.get("first_quarantined_at", "9999-12-31")))
        base = dict(group_sorted[0])
        # reason: first non-empty
        base["reason"] = (
            next((r.get("reason") for r in group_sorted if r.get("reason")), base.get("reason", "quarantine"))
            or "quarantine"
        )
        # score: max as string comparison won't work for decimals; coerce to float
        try:
            score_vals = []
            for r in group_sorted:
                try:
                    score_vals.append(float(r.get("score") or 0.0))
                except Exception:
                    pass
            base["score"] = f"{(max(score_vals) if score_vals else 0.0):.3f}"
        except Exception:
            base["score"] = base.get("score", "")
        # reinstated: if any row says "no", keep "no"; else keep the earliest row's value
        if any((r.get("reinstated", "no").lower() == "no") for r in group_sorted):
            base["reinstated"] = "no"
        # quarantined rows shouldn't have deleted_at
        base["deleted_at"] = ""
        kept.append(base)

    # Sort rows by file then status for stable output
    kept_sorted = sorted(kept, key=lambda r: (r.get("file", ""), r.get("status", "")))

    with QUEUE.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(kept_sorted)

    print(f"Deduplicated {len(rows)} -> {len(kept_sorted)} rows in {QUEUE}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
