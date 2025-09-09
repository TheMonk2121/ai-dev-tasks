#!/usr/bin/env python3
import json
from pathlib import Path


def normalize_case(obj):
    """Normalize a gold case to standard format"""
    # Handle both "id" and "case_id" fields
    case_id = obj.get("id") or obj.get("case_id")
    if not case_id:
        return None

    # Normalize to standard format
    normalized = {
        "id": case_id,
        "mode": obj.get("mode", "retrieval"),  # default to retrieval
        "query": obj.get("query", ""),
        "tags": obj.get("tags", [obj.get("tag", "")]) if isinstance(obj.get("tags"), list) else [obj.get("tag", "")],
        "category": obj.get("category"),
        "gt_answer": obj.get("gt_answer") or obj.get("answers"),
        "expected_files": obj.get("expected_files")
        or obj.get("file_paths")
        or ([obj.get("file_path")] if obj.get("file_path") else None),
        "globs": obj.get("globs"),
        "expected_decisions": obj.get("expected_decisions"),
        "notes": obj.get("notes"),
    }

    # Clean up empty tags
    normalized["tags"] = [t for t in normalized["tags"] if t]

    return normalized


def main():
    p = Path("evals/gold/v1/gold_cases.jsonl")
    seen = set()
    out = []

    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        normalized = normalize_case(obj)
        if not normalized:
            print(f"Warning: Skipping case with no ID: {obj}")
            continue

        case_id = normalized["id"]
        if case_id in seen:
            continue
        seen.add(case_id)
        out.append(normalized)

    # Write normalized cases
    p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n")
    print(f"Kept {len(out)} unique normalized cases.")


if __name__ == "__main__":
    main()
