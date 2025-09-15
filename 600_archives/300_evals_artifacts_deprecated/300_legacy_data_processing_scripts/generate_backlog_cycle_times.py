from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

#!/usr/bin/env python3

BACKLOG_PATH = Path("000_core/000_backlog.md")
OUT_DIR = Path("metrics")
OUT_FILE = OUT_DIR / "backlog_cycle_times.csv"

def parse_timestamp(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    # Try common ISO formats
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

def main() -> None:
    text = BACKLOG_PATH.read_text(encoding="utf-8", errors="ignore")

    # Match backlog rows like: | B-1008 | Title | ... | status |
    # Capture generic status cell without fragile alternation (emojis/markdown can appear)
    row_re = re.compile(r"^\|\s*(B-\d{3,4})\s*\|\s*(.*?)\|.*?\|\s*([^|]+)\|", re.IGNORECASE | re.MULTILINE)

    # Nearby HTML comment timestamps under/around rows
    started_re = re.compile(r"started_at:\s*([0-9T:_.\-]+)")
    updated_re = re.compile(r"last_updated:\s*([0-9T:_.\-]+)")
    completed_re = re.compile(r"(completion_date|completed|completion):\s*([0-9T:_.\-]+)")

    records: list[dict[str, str]] = []

    for m in row_re.finditer(text):
        bid = m.group(1)
        title = m.group(2).strip()
        raw_status = m.group(3).strip()
        ls = raw_status.lower()
        if any(x in ls for x in ("✅", "complete", "done")):
            status = "done"
        elif "in_progress" in ls or "in-progress" in ls or "in progress" in ls or "🔄" in ls:
            status = "in-progress"
        elif "blocked" in ls:
            status = "blocked"
        else:
            status = "todo"

        # Capture a window of text around the row for metadata
        start = max(0, m.start() - 800)
        end = min(len(text), m.end() + 800)
        window = text[start:end]

        started = parse_timestamp(next(iter(started_re.findall(window)), ""))
        # completed_re returns tuples; pick first group's second value
        comp_match = completed_re.search(window)
        completed = parse_timestamp(comp_match.group(2)) if comp_match else None
        last_updated = parse_timestamp(next(iter(updated_re.findall(window)), ""))

        lead_hours: float | None = None
        if started and completed:
            lead_hours = (completed - started).total_seconds() / 3600.0

        rec = {
            "id": bid,
            "title": title,
            "status": status,
            "started_at": started.isoformat() if started else "",
            "last_updated": last_updated.isoformat() if last_updated else "",
            "completed_at": completed.isoformat() if completed else "",
            "lead_time_hours": f"{lead_hours:.2f}" if lead_hours is not None else "",
        }
        records.append(rec)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "title",
                "status",
                "started_at",
                "last_updated",
                "completed_at",
                "lead_time_hours",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} records to {OUT_FILE}")

if __name__ == "__main__":
    main()
