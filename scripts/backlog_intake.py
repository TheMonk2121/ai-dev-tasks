from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scripts.doorway_utils import detect_duplicates

BACKLOG_FILE = Path("000_core/000_backlog.md")


def _load_live_backlog() -> list[tuple[str, str, str]]:
    """Return list of (id, title, status) for Live Backlog (todo/running).

    Try the canonical parser when available; otherwise fall back to a light
    section/table scan to support older interpreters.
    """
    # Attempt canonical parser
    try:
        from scripts.backlog_parser import BacklogParser  # type: ignore

        parser = BacklogParser()
        tasks = parser.parse_backlog(str(BACKLOG_FILE))
        live: list[tuple[str, str, str]] = []
        for t in tasks:
            status = getattr(t.status, "value", getattr(t, "status", ""))
            if status in {"todo", "running"}:
                live.append((t.id, t.title, status))
        return live
    except Exception:
        # Lightweight fallback: scan the Live Backlog section and pick rows
        text = BACKLOG_FILE.read_text(encoding="utf-8")
        lines = text.splitlines()
        start_idx = None
        for i, ln in enumerate(lines):
            if ln.strip() == "## Live Backlog":
                start_idx = i
                break
        if start_idx is None:
            return []
        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if lines[i].startswith("## "):
                end_idx = i
                break
        live: list[tuple[str, str, str]] = []
        for i in range(start_idx, end_idx):
            ln = lines[i]
            if ln.startswith("| B-") and "|" in ln:
                parts = [p.strip() for p in ln.split("|")]
                if len(parts) >= 7:
                    bid = parts[1]
                    title = parts[2]
                    status = parts[5]
                    if status in {"todo", "running"}:
                        live.append((bid, title, status))
        return live


def _next_backlog_id(existing_ids: list[str]) -> str:
    max_n = 0
    for bid in existing_ids:
        m = re.match(r"B-(\d+)$", bid)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"B-{max_n + 1:03d}"


def _insert_row(backlog_id: str, title: str) -> None:
    """Insert a minimal row into the Live Backlog table (appended at end of section)."""
    text = BACKLOG_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Find Live Backlog section bounds
    start_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## Live Backlog":
            start_idx = i
            break
    if start_idx is None:
        # Fallback: append at end of file as a minimal Live Backlog block
        block = [
            "",
            "## Live Backlog",
            "",
            "| ID  | Title | 🔥P | 🎯Points | Status | Problem/Outcome | Tech Footprint | Dependencies |",
            "|-----|-------|-----|----------|--------|-----------------|----------------|--------------|",
            f"| {backlog_id} | {title} | 🔧 | 3 | todo | {title} | None | None |",
            "",
        ]
        BACKLOG_FILE.write_text(text + "\n" + "\n".join(block), encoding="utf-8")
        return

    # Determine section end (next '## ' or EOF)
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            end_idx = i
            break

    # Find last table row in this section (line starting with '| B-')
    insert_at = None
    for i in range(end_idx - 1, start_idx, -1):
        if lines[i].startswith("| B-"):
            insert_at = i + 1
            break

    # If no existing rows, find the header divider line (---) and insert after
    if insert_at is None:
        for i in range(start_idx, end_idx):
            if lines[i].startswith("|---"):
                insert_at = i + 1
                break

    new_row = f"| {backlog_id} | {title} | 🔧 | 3 | todo | {title} | None | None |"
    if insert_at is None:
        # As a last resort, append at start_idx+1
        insert_at = start_idx + 1

    lines.insert(insert_at, new_row)
    BACKLOG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def intake(description: str, no_roadmap_advisory: bool = False) -> str:
    live = _load_live_backlog()
    existing_titles = [(bid, title) for bid, title, _ in live]

    exact, fuzzy = detect_duplicates(description, existing_titles)
    if exact:
        print(
            f"[INTAKE] Duplicate: {exact[0]} — proceeding with existing item",
            file=sys.stderr,
        )
        return exact[0]
    if fuzzy:
        print(f"[INTAKE] Similar to: {fuzzy[0]} — proceeding", file=sys.stderr)

    # Create new backlog ID and row
    new_id = _next_backlog_id([bid for bid, _, _ in live])
    _insert_row(new_id, description)

    if not no_roadmap_advisory:
        # Advisory only (fast path). We skip deep parsing to maintain speed.
        pass

    print(f"[INTAKE] Created {new_id}", file=sys.stderr)
    # Print B-ID to stdout for the doorway router
    print(new_id)
    return new_id


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("description")
    ap.add_argument("--no-roadmap-advisory", action="store_true")
    args = ap.parse_args()
    intake(args.description, args.no_roadmap_advisory)


if __name__ == "__main__":
    main()
