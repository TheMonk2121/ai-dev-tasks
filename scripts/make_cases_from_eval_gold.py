#!/usr/bin/env python3
import json, os, sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "dspy-rag-system" / "src"
sys.path.insert(0, str(SRC))
# import the existing gold
from eval_gold import GOLD, ADDITIONAL_GOLD  # existing dicts


def guess_tag(paths):
    p = " ".join(paths).lower()
    if any(x in p for x in ["/db/", ".sql", "migrations", "ivfflat", "index.sql"]):
        return "db_workflows"
    if any(x in p for x in ["/ops/", "zsh", "shell", "health", "canary", "deploy"]):
        return "meta_ops" if "canary" in p or "deploy" in p else "ops_health"
    return "rag_qa_single"


def to_case(q, target):
    # q is the question string key in GOLD; target may be dict/tuple based on your eval_gold structure
    # Normalize to a list of file path-like strings if available
    paths = []
    if isinstance(target, dict):
        for k in ("paths", "filenames", "namespace"):
            v = target.get(k)
            if not v:
                continue
            if k == "filenames":
                paths += [f"*/{name}" for name in v]
            elif k == "namespace":
                paths += [f"{v}/*"]
            else:
                paths += v
    elif isinstance(target, (list, tuple)):
        paths = list(target)
    else:
        paths = [str(target)]

    return {
        "case_id": q,
        "query": q,
        "tag": guess_tag(paths),
        # leave qvec empty; your runner will embed it
        "qvec": [],
    }


def main():
    out = []
    merged = {}
    merged.update(GOLD)
    merged.update(ADDITIONAL_GOLD)
    for q, target in merged.items():
        out.append(to_case(q, target))
    path = os.getenv("CASES_FILE", str(ROOT / "evals" / "gold_cases.json"))
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {len(out)} cases to {path}")


if __name__ == "__main__":
    main()
