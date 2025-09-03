#!/usr/bin/env python3
"""
Context Bundle Extractor

Usage:
  python3 scripts/extract_context.py B-1071
  python3 scripts/extract_context.py B-1071 --format json

Reads 000_core/000_backlog.md, extracts the section for the given backlog ID,
and prints a compact context bundle with: what, where, next, and context.

Goals:
- Zero external dependencies
- Friendly to Python 3.12, Ruff, and Pyright
- Minimal, readable implementation
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add validation support
try:
    from src.schemas.models import ContextBundle

    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

BACKLOG_PATH = Path("000_core/000_backlog.md")


def _read_backlog_text() -> str:
    try:
        return BACKLOG_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: {BACKLOG_PATH} not found", file=sys.stderr)
        sys.exit(1)


def _find_section(text: str, backlog_id: str) -> Optional[str]:
    # Headings look like: ### **B-1071: Title** ...
    # We capture from this heading to the next backlog heading or EOF
    heading_pattern = re.compile(rf"^### \*\*{re.escape(backlog_id)}:.*$", re.MULTILINE)
    match = heading_pattern.search(text)
    if not match:
        return None

    start = match.start()
    # Find the next heading for another backlog item
    next_heading = re.compile(r"^### \*\*B-\d{4}:.*$", re.MULTILINE)
    next_match = next_heading.search(text, match.end())
    end = next_match.start() if next_match else len(text)
    return text[start:end].strip()


def _extract_field_lines(section: str, prefix: str) -> List[str]:
    lines = []
    for line in section.splitlines():
        if line.strip().startswith(prefix):
            lines.append(line.strip())
    return lines


def _extract_value_after_prefix(section: str, prefix: str) -> Optional[str]:
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            # Split at ":" and take the remainder
            parts = stripped.split(":", 1)
            if len(parts) == 2:
                return parts[1].strip()
    return None


def _extract_context_bundle_json(section: str) -> Optional[Dict[str, object]]:
    # Heuristically find a JSON-like block after a "Context Bundle" label
    if "Context Bundle" not in section:
        return None
    lines = section.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if "Context Bundle" in line:
            # Look ahead for a line starting with "{" within the next few lines
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip().startswith("{"):
                    start_idx = j
                    break
            break
    if start_idx is None:
        return None

    # Collect until the matching closing brace on its own line or section end
    buf: List[str] = []
    brace_depth = 0
    started = False
    for k in range(start_idx, len(lines)):
        line = lines[k]
        buf.append(line)
        brace_depth += line.count("{")
        brace_depth -= line.count("}")
        if not started and "{" in line:
            started = True
        if started and brace_depth <= 0:
            break

    raw = "\n".join(buf)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _extract_next_steps(section: str) -> List[str]:
    steps: List[str] = []
    in_next = False
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- **Next Steps**") or stripped.startswith("- **Next steps**"):
            in_next = True
            continue
        if in_next:
            if stripped.startswith("- **") and not stripped.startswith("- **Exit"):
                # Another field begins; stop collecting
                break
            if stripped.startswith("- "):
                # Bullet line under next steps list
                steps.append(stripped[2:].strip())
            # End collection at blank line separating sections
            if stripped == "":
                break
    return steps


def build_handoff_bundle(section: str, backlog_id: str) -> Dict[str, object]:
    title_match = re.search(rf"^### \*\*{re.escape(backlog_id)}: (.+?)\*\*", section, re.MULTILINE)
    title = title_match.group(1) if title_match else backlog_id

    status = _extract_value_after_prefix(section, "- **Status**") or ""
    description = _extract_value_after_prefix(section, "- **Description**") or ""
    priority = _extract_value_after_prefix(section, "- **Priority**") or ""

    # Pull first next step if available
    next_steps = _extract_next_steps(section)
    next_action = next_steps[0] if next_steps else ""

    context_json = _extract_context_bundle_json(section) or {}

    bundle: Dict[str, object] = {
        "backlog_id": backlog_id,
        "title": title,
        "what": description,
        "where": status,
        "priority": priority,
        "next": next_action,
        "context": context_json,
    }
    return bundle


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract compact handoff context for a backlog ID")
    ap.add_argument("backlog_id", help="Backlog ID, e.g., B-1071")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--validate", action="store_true", help="Validate output with Pydantic (requires schemas)")
    args = ap.parse_args()

    text = _read_backlog_text()
    section = _find_section(text, args.backlog_id)
    if not section:
        print(f"Error: Section for {args.backlog_id} not found", file=sys.stderr)
        sys.exit(2)

    bundle = build_handoff_bundle(section, args.backlog_id)

    # Validate if requested
    if args.validate:
        if not VALIDATION_AVAILABLE:
            print("Error: Validation requested but Pydantic schemas not available", file=sys.stderr)
            sys.exit(3)
        try:
            ContextBundle(**bundle)
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            sys.exit(4)

    if args.format == "json":
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
        return

    # text format
    what = bundle.get("what", "") or ""
    where = bundle.get("where", "") or ""
    nxt = bundle.get("next", "") or ""
    title = bundle.get("title", "") or ""
    print(f"{args.backlog_id} — {title}\nWhat: {what}\nWhere: {where}\nNext: {nxt}")


if __name__ == "__main__":  # pragma: no cover
    main()
