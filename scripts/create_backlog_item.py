#!/usr/bin/env python3
"""
Create Backlog Item (Auto-ID, Auto-Placement)

Usage:
  echo "Optimize database pooling for eval performance" | python3 scripts/create_backlog_item.py --section "New"
  python3 scripts/create_backlog_item.py --idea "Improve handoff bundles" --section "New" --dry-run

Behavior:
  - Reads idea text from --idea or stdin
  - Finds next available backlog ID (B-XXXX) by scanning 000_core/000_backlog.md
  - Inserts a concise backlog block after the most recent large item section (default: after B-1070 if present)
  - Avoids modifying B-1070 or other active items

Notes:
  - Minimal implementation with no external deps; Python 3.12 friendly
  - Keeps changes small and readable
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import List

BACKLOG_PATH = Path("000_core/000_backlog.md")


def _read_all_stdin() -> str:
    if sys.stdin is None or sys.stdin.closed:
        return ""
    data = sys.stdin.read()
    return data.strip()


def _load_backlog() -> str:
    try:
        return BACKLOG_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: {BACKLOG_PATH} not found", file=sys.stderr)
        sys.exit(1)


def _extract_all_backlog_ids(text: str) -> List[int]:
    # Robust: capture any B-#### occurrences anywhere in the file
    ids = re.findall(r"B-(\d{4})", text)
    return [int(x) for x in ids]


def _next_backlog_id(text: str) -> str:
    nums = _extract_all_backlog_ids(text)
    next_num = max(nums) + 1 if nums else 1
    return f"B-{next_num:04d}"


def _find_insert_position_after(text: str, anchor_backlog_id: str) -> int:
    # Insert after the block for the anchor backlog id; fallback to end of the B-1070 block or start of file
    m = re.search(rf"^### \*\*{re.escape(anchor_backlog_id)}:.*$", text, flags=re.MULTILINE)
    if not m:
        # fallback: append at end of file when anchor not found
        return len(text)

    # find next backlog heading after anchor
    next_heading = re.search(r"^### \*\*B-\d{4}:.*$", text[m.end() :], flags=re.MULTILINE)
    if next_heading:
        # insert before the next heading (end of the anchor block)
        return m.end() + next_heading.start()
    # else append at end
    return len(text)


def _render_block(backlog_id: str, idea: str) -> str:
    now = datetime.now(UTC).strftime("%Y-%m-%d")
    return (
        f"\n\n### **{backlog_id}: Context Handoff Seed** 🆕 **NEW**\n"
        f"- **Priority**: 🔥 **HIGH** - Handoff reliability and context capture\n"
        f"- **Points**: 2 - Minimal infra, high leverage\n"
        f"- **Status**: \ud83c\udd95 **NEW** - Seeded on {now}\n"
        f"- **Description**: {idea}\n"
        f"- **Essential Context**:\n"
        f"  - **Problem**: Manual handoffs cause context hunting and duplicate IDs\n"
        f"  - **Solution**: Standard capture + auto-ID + pickup bundle\n"
        f"  - **Scope**: Minimal scripts/conventions; no changes to active items\n"
        f"- **Context Bundle (seed)**:\n"
        f"  {{\n"
        f'    "backlog_id": "{backlog_id}",\n'
        f'    "title": "Context Handoff Seed",\n'
        f'    "problem": "Handoffs are unreliable; context is hard to pick up",\n'
        f'    "solution": "Capture script + handoff bundle extraction",\n'
        f'    "status": "new"\n'
        f"  }}\n"
        f"- **Next Steps**:\n"
        f"  - Extract pickup bundle via scripts/handoff_context.py {backlog_id}\n"
        f"  - Validate cross-chat pickup works\n"
        f"- **Exit Criteria**: Any chat can pick up with what/where/next in <10s\n"
    )


def insert_idea(idea: str, anchor_after: str = "B-1070", dry_run: bool = False) -> str:
    text = _load_backlog()
    new_id = _next_backlog_id(text)
    pos = _find_insert_position_after(text, anchor_after)
    block = _render_block(new_id, idea)
    new_text = text[:pos] + block + text[pos:]
    if dry_run:
        return new_text
    # Use surrogatepass to safely handle any legacy surrogate code points in the file
    BACKLOG_PATH.write_bytes(new_text.encode("utf-8", "surrogatepass"))
    return new_id


def main() -> None:
    ap = argparse.ArgumentParser(description="Capture idea and insert as backlog item with auto-ID")
    ap.add_argument("--idea", help="Idea text; if omitted, read from stdin")
    ap.add_argument("--anchor-after", default="B-1070", help="Insert after this backlog id (default: B-1070)")
    ap.add_argument("--dry-run", action="store_true", help="Print modified backlog content without writing")
    args = ap.parse_args()

    idea = (args.idea or _read_all_stdin()).strip()
    if not idea:
        print("Error: idea text is required via --idea or stdin", file=sys.stderr)
        sys.exit(2)

    result = insert_idea(idea, anchor_after=args.anchor_after, dry_run=args.dry_run)
    if args.dry_run:
        print(result)
    else:
        print(result)


if __name__ == "__main__":  # pragma: no cover
    main()
