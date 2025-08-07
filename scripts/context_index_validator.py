#!/usr/bin/env python3
"""
Validate CONTEXT_INDEX blocks in documentation files.

Checks:
- JSON is parseable
- Each referenced file exists

Usage:
  python3 scripts/context_index_validator.py --root .
"""

import os
import sys
import json
from pathlib import Path

def extract_context_index(content: str):
    start = content.find("<!-- CONTEXT_INDEX")
    if start == -1:
        return None
    end = content.find("CONTEXT_INDEX -->", start)
    if end == -1:
        return None
    block = content[start:end]
    jstart = block.find("{")
    if jstart == -1:
        return None
    return json.loads(block[jstart:])

def validate_index(root: Path, index: dict) -> list:
    errors = []
    files = index.get("files", [])
    for f in files:
        path = f.get("path")
        if not path:
            errors.append("Missing path in files entry")
            continue
        target = root / path
        if not target.exists():
            errors.append(f"Missing file: {path}")
    return errors

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Validate CONTEXT_INDEX blocks")
    ap.add_argument("--root", default=".", help="Root path")
    args = ap.parse_args()

    root = Path(args.root)
    problems = []

    for p in root.rglob("*.md"):
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            continue
        idx = extract_context_index(content)
        if idx is None:
            continue
        try:
            errs = validate_index(root, idx)
            if errs:
                problems.append({"file": str(p), "errors": errs})
        except Exception as e:
            problems.append({"file": str(p), "errors": [f"Parse/validate error: {e}"]})

    if problems:
        print(json.dumps({"status": "fail", "problems": problems}, indent=2))
        sys.exit(1)
    else:
        print(json.dumps({"status": "ok"}, indent=2))

if __name__ == "__main__":
    main()


