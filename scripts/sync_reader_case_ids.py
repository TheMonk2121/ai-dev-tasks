#!/usr/bin/env python3
"""
Sync reader gold case_ids to retrieval case_ids by matching normalized queries.

Inputs:
  - CASES_FILE (default: evals/gold_cases.json): retrieval cases (with case_id, query, tag)
  - READER_SRC (default: evals/reader_gold.jsonl): reader gold Q/A (case_id may be arbitrary)
Outputs:
  - READER_OUT (default: evals/reader_gold_comprehensive.jsonl): only matched rows,
    with case_id replaced by the retrieval case_id and tag set/normalized.
  - READER_LEFTOVER (default: evals/reader_gold_unmatched.jsonl): reader rows that did not match any retrieval query

Usage:
  export CASES_FILE=evals/gold_cases.json
  export READER_SRC=evals/reader_gold.jsonl
  python3 scripts/sync_reader_case_ids.py
"""

import json
import os
import pathlib
import re
import sys
from collections import defaultdict

CASES_FILE = os.getenv("CASES_FILE", "evals/gold_cases.json")
READER_SRC = os.getenv("READER_SRC", "evals/reader_gold.jsonl")
READER_OUT = os.getenv("READER_OUT", "evals/reader_gold_comprehensive.jsonl")
READER_LEFTOVER = os.getenv("READER_LEFTOVER", "evals/reader_gold_unmatched.jsonl")


def norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def load_cases(path):
    data = json.load(open(path, "r", encoding="utf-8"))
    # cases: list of {case_id, query, tag, ...}
    m = {}
    per_tag = defaultdict(int)
    for row in data:
        q = row.get("query") or row.get("question") or ""
        cid = row.get("case_id")
        tag = row.get("tag") or "rag_qa_single"
        if not cid or not q:
            continue
        key = norm(q)
        m[key] = {"case_id": cid, "tag": tag, "query": q}
        per_tag[tag] += 1
    return m, per_tag


def load_reader_gold(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            rows.append(r)
    return rows


def main():
    if not pathlib.Path(CASES_FILE).exists():
        print(f"ERROR: missing {CASES_FILE}", file=sys.stderr)
        sys.exit(1)
    if not pathlib.Path(READER_SRC).exists():
        print(f"ERROR: missing {READER_SRC}", file=sys.stderr)
        sys.exit(1)

    cases_map, per_tag_counts = load_cases(CASES_FILE)
    reader_rows = load_reader_gold(READER_SRC)

    matched, unmatched = [], []
    seen_ids = set()

    for r in reader_rows:
        q = r.get("query") or r.get("question") or ""
        key = norm(q)
        cm = cases_map.get(key)
        if cm:
            # rewrite case_id to match retrieval case_id; ensure tag consistency
            new = dict(r)
            new["case_id"] = cm["case_id"]
            new["tag"] = new.get("tag") or cm["tag"]
            # enforce uniqueness on case_id; last write wins (warn if duplicate)
            if new["case_id"] in seen_ids:
                # de-dup by appending a small suffix while printing a warning
                print(
                    f"[warn] duplicate case_id for query '{q[:60]}...'; keeping first, sending duplicate to unmatched",
                    file=sys.stderr,
                )
                unmatched.append(r)
                continue
            seen_ids.add(new["case_id"])
            matched.append(new)
        else:
            unmatched.append(r)

    # Write outputs
    outp = pathlib.Path(READER_OUT)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(READER_OUT, "w", encoding="utf-8") as f:
        for row in matched:
            f.write(json.dumps(row) + "\n")
    with open(READER_LEFTOVER, "w", encoding="utf-8") as f:
        for row in unmatched:
            f.write(json.dumps(row) + "\n")

    # Report
    print("=== Reader Case-ID Sync Report ===")
    print(f"Retrieval cases file: {CASES_FILE}")
    print(f"Reader gold source : {READER_SRC}")
    print(f"Matched written    : {READER_OUT}  ({len(matched)} rows)")
    print(f"Unmatched written  : {READER_LEFTOVER}  ({len(unmatched)} rows)")
    # Extra diagnostics: how many retrieval queries have a reader match?
    # Build reverse map to count coverage
    matched_keys = set(norm(r.get("query") or r.get("question") or "") for r in matched)
    total_retr = len(cases_map)
    covered = sum(1 for k in cases_map if k in matched_keys)
    print(f"Retrieval coverage : {covered}/{total_retr} queries covered by reader gold")

    # Per-tag summary from retrieval cases (not from reader)
    if per_tag_counts:
        print("Retrieval per-tag counts:")
        for t, c in sorted(per_tag_counts.items()):
            print(f"  - {t}: {c}")

    # Exit non-zero if zero matched (helps CI)
    if len(matched) == 0:
        print("FAIL: 0 matched reader gold items; fix queries or case_ids.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
