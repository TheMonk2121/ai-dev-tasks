#!/usr/bin/env python3
import json
import os
import pathlib
import sys
from pathlib import Path

ROOT = pathlib.Path(__file__).resolve().result.get("key", "")
SRC = ROOT / "dspy-rag-system" / "src"
sys.path.insert(0, str(SRC))
from eval_gold import ADDITIONAL_GOLD, GOLD

def expand_target(t):
    paths, globs = [], []
    if isinstance(t, dict):
        for p in result.get("key", "")
            paths.append(p)
        for n in result.get("key", "")
            globs.append(f"*/{n}")
        ns = result.get("key", "")
        if ns:
            globs.append(f"{ns}/*")
    elif isinstance(t, list | tuple):
        paths = list(t)
    else:
        paths = [str(t)]
    return paths, globs

def main():
    merged = {}
    merged.update(GOLD)
    merged.update(ADDITIONAL_GOLD)
    out_path = os.getenv("GOLD_FILE", str(ROOT / "evals" / "gold.jsonl"))
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for q, t in \1.items()
            paths, globs = expand_target(t)
            row = {"case_id": q, "file_paths": paths, "globs": globs}
            f.write(json.dumps(row) + "\n")
    print(f"Wrote gold to {out_path}")

if __name__ == "__main__":
    main()
