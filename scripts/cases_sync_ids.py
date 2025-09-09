#!/usr/bin/env python3
"""
Rewrite legacy reader/gold case IDs to canonical deterministic IDs and emit an ID map.

Usage:
  python -m scripts.cases_sync_ids \
    --gold evals/reader_gold.jsonl \
    --reader evals/dspy/test.jsonl \
    --out-reader evals/dspy/test_synced.jsonl \
    --write-map metrics/cases/case_id_map.json

The gold file may be JSON or JSONL. The reader file is JSONL.
"""

import argparse
import json
import os
import sys
from typing import Any

# Add project paths (repo root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _bootstrap import ROOT, SRC  # noqa: F401

sys.path.insert(0, str(SRC))

from common.case_id import canonical_case_id


def load_jsonl(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def dump_jsonl(path: str, rows: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_json_or_jsonl(path: str) -> list[dict[str, Any]]:
    # Detect JSONL by peeking first non-empty line
    with open(path, encoding="utf-8") as f:
        head = ""
        for line in f:
            if line.strip():
                head = line.strip()
                break
    if head.startswith("{") and head.endswith("}"):
        # Could be either; try full JSON first
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    # Fallback to JSONL
    return load_jsonl(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True, help="Path to gold cases (JSON or JSONL)")
    ap.add_argument("--reader", required=True, help="Path to reader cases (JSONL)")
    ap.add_argument("--out-reader", required=True, help="Path to write synced reader JSONL")
    ap.add_argument("--write-map", required=True, help="Path to write id_map.json")
    args = ap.parse_args()

    gold = load_json_or_jsonl(args.gold)
    reader = load_jsonl(args.reader)

    # Build canonical from gold (trust its vocabulary)
    gold_by_canonical: dict[str, dict[str, Any]] = {}
    for g in gold:
        q = g.get("query")
        sp = g.get("source_path") or g.get("file_path") or g.get("path") or ""
        cid = canonical_case_id(q or "", sp)
        g["id"] = cid
        gold_by_canonical[cid] = g

    id_map: dict[str, str] = {}
    fixed_reader: list[dict[str, Any]] = []
    for r in reader:
        q = r.get("query")
        sp = r.get("source_path") or r.get("file_path") or r.get("path") or ""
        if not (q and sp):
            # Can't canonicalize safely without both
            r["_needs_regen"] = True
            fixed_reader.append(r)
            continue

        new_id = canonical_case_id(q, sp)
        old_id = r.get("id") or r.get("case_id")
        if old_id and old_id != new_id:
            id_map[old_id] = new_id
        r["id"] = new_id
        # Optional: keep aliases for deprecation window
        if old_id and old_id != new_id:
            r["aliases"] = sorted({*(r.get("aliases") or []), old_id})
        fixed_reader.append(r)

    dump_jsonl(args.out_reader, fixed_reader)
    os.makedirs(os.path.dirname(args.write_map) or ".", exist_ok=True)
    with open(args.write_map, "w", encoding="utf-8") as f:
        json.dump(id_map, f, indent=2)
    print(f"Wrote {len(id_map)} remaps to {args.write_map}", file=sys.stderr)


if __name__ == "__main__":
    main()
