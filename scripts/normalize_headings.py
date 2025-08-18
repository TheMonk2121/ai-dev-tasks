#!/usr/bin/env python3.12.123.11
"""
Normalize markdown headings in 400_guides: enforce a single H1 per file.

Rules:
- Preserve the first top-level heading (`# `) as-is.
- Demote any subsequent `# ` headings to `## `.
- Do not modify content inside fenced code blocks (``` ... ```).

Usage:
  python scripts/normalize_headings.py --write

Dry run by default; use --write to apply changes.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def normalize_file(path: Path) -> tuple[bool, str]:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    in_code_fence = False
    saw_first_h1 = False
    changed = False
    out_lines: list[str] = []

    # Match exactly one '#', with optional space after, capturing title text
    h1_pattern = re.compile(r"^(\s*)#(?!#)\s*(.*)$")

    for line in lines:
        stripped = line.lstrip()

        # Toggle code-fence state on lines that start a fence
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            out_lines.append(line)
            continue

        if in_code_fence:
            out_lines.append(line)
            continue

        # Demote additional H1s to H2s, preserving leading whitespace
        m = h1_pattern.match(line)
        if m:
            indent, title = m.groups()
            if not saw_first_h1:
                saw_first_h1 = True
                out_lines.append(f"{indent}# {title}")
            else:
                out_lines.append(f"{indent}## {title}")
                changed = True
        else:
            out_lines.append(line)

    new_content = "\n".join(out_lines) + ("\n" if content.endswith("\n") else "")
    return changed, new_content


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="apply changes in-place")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    guides_dir = root / "400_guides"

    md_files = sorted(p for p in guides_dir.glob("*.md"))
    any_changed = False
    for f in md_files:
        changed, new_content = normalize_file(f)
        if changed:
            any_changed = True
            if args.write:
                f.write_text(new_content, encoding="utf-8")
            else:
                print(f"Would update: {f}")

    if not any_changed:
        print("No changes needed.")
    else:
        if args.write:
            print("Applied heading normalization.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
