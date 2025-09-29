from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# FIXME: Update this import path after reorganization
# from scripts.doorway_utils import detect_duplicates

BACKLOG_FILE = Path("000_core/000_backlog.md")

def _load_all_backlog_ids() -> list[tuple[str, str, str]]:
    """Return list of (id, title, status) for ALL backlog items across all sections.

    This enhanced function scans the entire backlog file to find all existing IDs,
    preventing conflicts between different sections (P0, P1, P2, Live Backlog, etc.).
    """
    text = BACKLOG_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()

    all_items: list[tuple[str, str, str]] = []

    # Scan for all table rows that start with | B-
    for i, line in enumerate(lines):
        if line.startswith("| B-") and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 7:
                bid = parts[1]
                title = parts[2]
                status = parts[5] if len(parts) > 5 else "unknown"
                all_items.append((bid, title, status))

    # Also scan for P0/P1/P2 lane items (different format)
    for i, line in enumerate(lines):
        if line.startswith("- B‑") and "—" in line:
            # Format: "- B‑077 — Code Review Process Upgrade with Performance Reporting (score 7.5)"
            match = re.match(r"- (B‑\d+) — (.+?)(?: \(score \d+\.\d+\))?$", line)
            if match:
                bid = match.group(1)
                title = match.group(2)
                # P0/P1/P2 items are typically todo status
                status = "todo"
                all_items.append((bid, title, status))

    return all_items

def _load_live_backlog() -> list[tuple[str, str, str]]:
    """Return list of (id, title, status) for Live Backlog (todo/running).

    Use lightweight scan as default for performance; fall back to canonical parser
    only if lightweight scan completely fails.
    """
    # Fast path: lightweight scan of Live Backlog section
    text = BACKLOG_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()
    start_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## Live Backlog":
            start_idx = i
            break
    if start_idx is None:
        return []

    # Find section end (next '## ' or EOF)
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            end_idx = i
            break

    # Parse table rows in Live Backlog section
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

    # If lightweight scan found items, return them (fast path)
    if live:
        return live

    # Last resort: only if lightweight scan completely failed, try canonical parser
    try:
        from scripts.backlog_parser import BacklogParser  # type: ignore[import-untyped]

        parser = BacklogParser()
        tasks = parser.parse_backlog(str(BACKLOG_FILE))
        live_items: list[tuple[str, str, str]] = []
        for t in tasks:
            status = getattr(t.status, "value", getattr(t, "status", ""))
            if status in {"todo", "running"}:
                live_items.append((t.id, t.title, status))
        return live_items
    except Exception:
        return []

def _next_backlog_id(existing_ids: list[str]) -> str:
    """Generate the next available backlog ID, checking against ALL existing IDs."""
    max_n = 0
    for bid in existing_ids:
        # Handle both B-001 and B‑001 formats (different dash types)
        m = re.match(r"B[‑-](\d+)$", bid)
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

def detect_duplicates(description: str, existing_titles: list[tuple[str, str]]) -> tuple[list[str], list[str]]:
    """Detect exact and fuzzy duplicates in backlog items."""
    exact_duplicates = []
    fuzzy_duplicates = []

    # Check for exact matches
    for bid, title in existing_titles:
        if description.lower().strip() == title.lower().strip():
            exact_duplicates.append(bid)

    # Check for fuzzy matches (simple similarity)
    for bid, title in existing_titles:
        if description.lower().strip() in title.lower().strip() or title.lower().strip() in description.lower().strip():
            if bid not in exact_duplicates:  # Don't double-count exact matches
                fuzzy_duplicates.append(bid)

    return exact_duplicates, fuzzy_duplicates

def intake(description: str, no_roadmap_advisory: bool = False) -> str:
    # Enhanced: Load ALL backlog items to check for duplicates and ID conflicts
    all_items = _load_all_backlog_ids()
    existing_titles = [(bid, title) for bid, title, _ in all_items]
    existing_ids = [bid for bid, _, _ in all_items]

    # Check for exact and fuzzy duplicates across ALL sections
    exact, fuzzy = detect_duplicates(description, existing_titles)
    if exact:
        print(
            f"[INTAKE] Duplicate: {exact[0]} — proceeding with existing item",
            file=sys.stderr,
        )
        return exact[0]
    if fuzzy:
        print(f"[INTAKE] Similar to: {fuzzy[0]} — proceeding", file=sys.stderr)

    # Create new backlog ID, checking against ALL existing IDs
    new_id = _next_backlog_id(existing_ids)

    # Double-check that the new ID doesn't conflict
    if new_id in existing_ids:
        print(f"[INTAKE] ERROR: Generated ID {new_id} already exists!", file=sys.stderr)
        print(f"[INTAKE] Existing IDs: {sorted(existing_ids)}", file=sys.stderr)
        sys.exit(1)

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
