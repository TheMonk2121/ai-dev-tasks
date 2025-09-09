#!/usr/bin/env python3
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

sys.path.append(".")
from src.schemas.eval import KNOWN_TAGS, GoldCase

PATH = Path("evals/gold/v1/gold_cases.jsonl")


def main():
    raw = PATH.read_text(encoding="utf-8").splitlines()
    ids = set()
    n = 0
    for i, line in enumerate(raw, 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        case = GoldCase.model_validate(obj)  # validates + normalizes
        if case.id in ids:
            raise SystemExit(f"Duplicate id at line {i}: {case.id}")
        ids.add(case.id)
        n += 1

        # Gentle tag sanity (warn, don't fail)
        unknowns = [t for t in case.tags if t not in KNOWN_TAGS]
        if unknowns:
            print(f"⚠️  {case.id}: unknown tags {unknowns}")

        # When retrieval/decision specify globs/paths, check they resolve
        if case.mode.value == "retrieval":
            misses = []
            for p in case.expected_files or []:
                if not Path(p).exists():
                    misses.append(("file", p))
            for g in case.globs or []:
                if not glob.glob(g):
                    misses.append(("glob", g))
            if misses:
                print(f"⚠️  {case.id}: missing targets -> {misses[:5]}")

    print(f"✅ Validated {n} cases from {PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
