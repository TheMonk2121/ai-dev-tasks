from __future__ import annotations

import os
import re
import sys

#!/usr/bin/env python3
"""
Normalize markdown formatting for markdownlint basics:
- Ensure blank line before and after headings
- Ensure blank line before and after list blocks
- Collapse multiple blank lines to a single blank line
- Ensure code fences have a language (add 'text' if missing)

Usage:
  python3 scripts/fix_markdown_blanks.py 100_cursor-memory-context.md
"""

def ensure_code_fence_language(lines):
    out = []
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            ticks = line.strip()
            if not in_fence:
                # opening fence
                lang = ticks[3:].strip()
                if not lang:
                    line = "```text\n"
                in_fence = True
            else:
                in_fence = False
        out.append(line)
    return out

def normalize_markdown(content: str) -> str:
    lines = content.splitlines(True)

    # First pass: ensure code fences have language
    lines = ensure_code_fence_language(lines)

    # Second pass: insert blank lines around headings and list blocks
    result = []
    i = 0
    n = len(lines)

    def is_heading(l):
        return l.lstrip().startswith("#")

    def is_list(l):
        s = l.lstrip()
        return bool(re.match(r"(- |\* |\d+\. )", s))

    while i < n:
        line = lines[i]
        prev = result[-1] if result else "\n"
        next_line = lines[i + 1] if i + 1 < n else "\n"

        # Ensure blank line before headings
        if is_heading(line):
            if result and prev.strip() != "":
                result.append("\n")
            result.append(line)
            # Ensure blank after heading if next is not blank or fence
            if next_line.strip() != "" and not next_line.strip().startswith("```"):
                result.append("\n")
            i += 1
            continue

        # Handle list blocks: ensure blank line before and after contiguous list
        if is_list(line):
            # blank before list
            if result and prev.strip() != "":
                result.append("\n")
            # add list lines
            while i < n and (is_list(lines[i]) or lines[i].strip() == ""):
                result.append(lines[i])
                i += 1
            # blank after list if next non-blank isn't a code fence close
            if i < n and lines[i].strip() != "":
                result.append("\n")
            continue

        result.append(line)
        i += 1

    # Collapse 3+ blank lines to max 2 and then to 1 where needed
    text = "".join(result)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not text.endswith("\n"):
        text += "\n"
    return text

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/fix_markdown_blanks.py <file.md>")
        sys.exit(1)
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        original = f.read()
    fixed = normalize_markdown(original)
    with open(path, "w", encoding="utf-8") as f:
        f.write(fixed)
    print(f"Formatted {path}")

if __name__ == "__main__":
    main()
