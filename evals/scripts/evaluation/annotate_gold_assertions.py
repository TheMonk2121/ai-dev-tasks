from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                # Keep malformed lines as-is to avoid data loss; mark unscored
                try:
                    items.append({"raw": line, "scored": False})
                except Exception:
                    pass
    return items


def dump_jsonl(path: Path, items: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def to_list(val: Any) -> list[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def to_dict(val: Any) -> dict[str, Any]:
    if isinstance(val, dict):
        return val
    return {}


def annotate_item(item: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(item)
    mode = item.get("mode", "")

    # Ensure assertions container
    assertions: dict[str, Any] = to_dict(item.get("assertions", {}))

    def mark_scored(flag: bool) -> None:
        updated["scored"] = flag

    # Decision mode
    if mode == "decision":
        expected = to_list(item.get("expected"))
        if expected:
            assertions.setdefault("decision", {})["any_of"] = expected
            mark_scored(True)
        else:
            mark_scored(False)

    # Retrieval mode
    elif mode == "retrieval":
        expected_files = to_list(item.get("expected_files"))
        globs = to_list(item.get("globs"))
        if expected_files:
            k = 5
            min_recall = 1.0 if len(expected_files) <= k else 0.6
            r = assertions.setdefault("retrieval", {})
            r.setdefault("k", k)
            r.setdefault("min_recall_at_5", min_recall)
            r.setdefault("must_include", expected_files)
            mark_scored(True)
        else:
            # Namespace-only targets are advisory without concrete ground truth
            mark_scored(False)

    # Reader mode
    elif mode == "reader":
        gt_answer = item.get("gt_answer")
        expected_answers = to_list(item.get("expected_answers"))

        # Normalize answers
        if gt_answer and not expected_answers:
            expected_answers = [gt_answer]
            updated["expected_answers"] = expected_answers

        r = assertions.setdefault("reader", {})

        if expected_answers:
            # Special-case unanswerables marked with "Not in context."
            if all(isinstance(a, str) and a.strip().lower() == "not in context." for a in expected_answers):
                updated["expected_answers"] = expected_answers
                r.setdefault("must_abstain", True)
            else:
                r.setdefault("match", "normalized")
            mark_scored(True)
        else:
            mark_scored(False)

    else:
        # Unknown modes are advisory
        mark_scored(False)

    # Optional faithfulness for reader items with sources
    if mode == "reader" and item.get("sources"):
        assertions.setdefault("faithfulness", {}).setdefault("min_score", 0.6)

    updated["assertions"] = assertions
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate gold JSONL with assertions and scored flags")
    parser.add_argument("--path",
        default="evals/evals/data/gold/v1/gold_cases.jsonl",
        help="Path to gold JSONL")
    parser.add_argument("--backup", action="store_true", help="Write a timestamped backup next to the file")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"❌ File not found: {target}")
        sys.exit(1)

    items = load_jsonl(target)
    updated_items: list[dict[str, Any]] = []

    counts = {"total": 0, "scored": 0, "advisory": 0}
    for it in items:
        counts["total"] += 1
        upd = annotate_item(it)
        updated_items.append(upd)
        if upd.get("scored", False):
            counts["scored"] += 1
        else:
            counts["advisory"] += 1

    if args.backup:
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = target.with_suffix(target.suffix + f".backup_{ts}")
        shutil.copyfile(target, backup_path)
        print(f"🗄️  Backup written: {backup_path}")

    dump_jsonl(target, updated_items)

    print(json.dumps({
        "path": str(target),
        "summary": counts,
    }, indent=2))


if __name__ == "__main__":
    main()
