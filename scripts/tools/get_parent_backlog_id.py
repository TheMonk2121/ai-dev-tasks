#!/usr/bin/env python3
"""
Resolve a file's parent backlog ID.

Order of precedence:
1) Markdown header comment <!-- parent_backlog: B-#### --> (first 50 lines)
2) Introducing commit message containing B-#### (git log --diff-filter=A --follow)

Usage:
  python scripts/tools/get_parent_backlog_id.py /absolute/or/relative/path.md
"""

from __future__ import annotations

import os
import re
import subprocess  # nosec B404
import sys
from typing import Optional

HEADER_PATTERN = re.compile(r"<!--\s*parent_backlog:\s*(B-\d{4,})\s*-->")
ID_PATTERN = re.compile(r"\b(B-\d{4,})\b")


def read_header_for_id(file_path: str) -> Optional[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for _ in range(50):
                line = f.readline()
                if not line:
                    break
                m = HEADER_PATTERN.search(line)
                if m:
                    return m.group(1)
    except Exception:
        return None
    return None


def git_introducing_commit_id(file_path: str) -> Optional[str]:
    try:
        cmd = [
            "git",
            "log",
            "--diff-filter=A",
            "--follow",
            "--format=%s",
            "--",
            file_path,
        ]
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)  # nosec B603
        lines = [line.strip() for line in out.splitlines() if line.strip()]
        if not lines:
            return None
        introducing_subject = lines[-1]
        m = ID_PATTERN.search(introducing_subject)
        if m:
            return m.group(1)
    except Exception:
        return None
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/tools/get_parent_backlog_id.py <path>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Error: path not found: {path}", file=sys.stderr)
        return 2

    header = read_header_for_id(path)
    if header:
        print(header)
        return 0

    gid = git_introducing_commit_id(path)
    if gid:
        print(gid)
        return 0

    print("UNKNOWN", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
