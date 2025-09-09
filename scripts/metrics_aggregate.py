#!/usr/bin/env python3
from __future__ import annotations
import json
import csv
from pathlib import Path


def find_summaries(root: str = "metrics"):
    return sorted(Path(root).rglob("summary.json"))


def row_from_summary(p: Path):
    data = json.loads(p.read_text())
    met = data.get("metrics", {}) or data.get("overall_metrics", {})
    cfg = data.get("reranker_config", {})
    return {
        "path": str(p),
        "suite": data.get("suite_name"),
        "profile": data.get("profile"),
        "seed": data.get("seed"),
        "ts": data.get("timestamp", ""),
        "micro_f1": met.get("micro_f1") or met.get("f1_score") or met.get("f1"),
        "micro_p": met.get("micro_precision") or met.get("precision"),
        "micro_r": met.get("micro_recall") or met.get("recall"),
        "macro_f1": met.get("macro_f1") or met.get("f1_score"),
        "rerank": cfg.get("enable"),
        "r_model": cfg.get("model"),
        "r_topk": cfg.get("input_topk"),
        "r_keep": cfg.get("keep"),
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
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows → {out}")


if __name__ == "__main__":
    main()

