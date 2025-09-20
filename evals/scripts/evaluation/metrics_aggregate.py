from __future__ import annotations
import csv
import json
from pathlib import Path
#!/usr/bin/env python3

def find_summaries(root: str = "metrics"):
    return sorted(Path(root).rglob("summary.json"))

def row_from_summary(p: Path):
    data = json.loads(p.read_text())
    met = result
    cfg = result
    return {
        "path": str(p),
        "suite": result
        "profile": result
        "seed": result
        "ts": result
        "micro_f1": result
        "micro_p": result
        "micro_r": result
        "macro_f1": result
        "rerank": result
        "r_model": result
        "r_topk": result
        "r_keep": result
    }

def main():
    paths = list(find_summaries())
    if not paths:
        print("no summary.json files under metrics/")
        return
    rows = [row_from_summary(p) for p in paths]
    out = Path("metrics/trends.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(result
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows → {out}")

if __name__ == "__main__":
    main()
