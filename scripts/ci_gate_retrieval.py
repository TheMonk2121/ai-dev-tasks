#!/usr/bin/env python3
import json
import os
import sys
from collections import defaultdict

# bootstrap
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
dspy_src = os.path.join(repo_root, "dspy-rag-system", "src")
sys.path.insert(0, repo_root)
sys.path.insert(0, dspy_src)
from _bootstrap import ROOT, SRC  # noqa: F401
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap

from evals.gold import gold_hit
from scripts.migrate_to_pydantic_evals import load_eval_cases

PREFILTER_MIN_MICRO = float(os.getenv("PREFILTER_MIN_MICRO", "0.85"))
PREFILTER_MIN_TAG = float(os.getenv("PREFILTER_MIN_TAG", "0.75"))
MAX_REG_DROP = float(os.getenv("MAX_REG_DROP", "0.05"))
K_CAP = int(os.getenv("PER_FILE_CAP", "5"))
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))

BASELINE_FILE = os.getenv("BASELINE_METRICS_FILE", "evals/baseline_metrics.json")
OUT_FILE = os.getenv("LATEST_METRICS_FILE", "evals/latest_retrieval_metrics.json")


def eval_once(cases):
    tag_hits, tag_total = defaultdict(int), defaultdict(int)
    hits_total = 0
    for case in cases:
        lim = load_limits(case.tag)
        qs = build_channel_queries(case.query, case.tag)
        rows = run_fused_query(
            qs["short"], qs["title"], qs["bm25"], case.qvec, tag=case.tag, k=lim["shortlist"], return_components=True
        )
        rows = mmr_rerank(rows, alpha=ALPHA, per_file_penalty=0.10, k=lim["shortlist"])
        rows = per_file_cap(rows, cap=K_CAP)[: lim["topk"]]
        hit = gold_hit(case.id, rows)
        tag_total[case.tag] += 1
        tag_hits[case.tag] += int(hit)
        hits_total += int(hit)
    micro = hits_total / max(1, sum(tag_total.values()))
    tag_rates = {t: tag_hits[t] / max(1, tag_total[t]) for t in tag_total}
    macro = sum(tag_rates.values()) / max(1, len(tag_rates))
    return {"micro": micro, "macro": macro, "per_tag": tag_rates, "total_cases": int(sum(tag_total.values()))}


def load_baseline(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


if __name__ == "__main__":
    cases_file = os.getenv("CASES_FILE", "evals/gold_cases.json")
    dataset = os.path.splitext(os.path.basename(cases_file))[0].replace("_cases", "")
    cases = load_eval_cases(dataset)
    metrics = eval_once(cases)

    print(f"[prefilter] micro={metrics['micro']:.3f} macro={metrics['macro']:.3f}")
    for t, v in sorted(metrics["per_tag"].items()):
        print(f"[tag] {t}: {v:.3f}")

    # Floors
    if metrics["micro"] < PREFILTER_MIN_MICRO:
        print(f"FAIL: micro {metrics['micro']:.3f} < {PREFILTER_MIN_MICRO}")
        save_json(OUT_FILE, metrics)
        sys.exit(1)
    low_tags = [t for t, v in metrics["per_tag"].items() if v < PREFILTER_MIN_TAG]
    if low_tags:
        print(f"FAIL: per-tag floor {PREFILTER_MIN_TAG} violated: {low_tags}")
        save_json(OUT_FILE, metrics)
        sys.exit(1)

    # Regression guard vs baseline
    baseline = load_baseline(BASELINE_FILE)
    if baseline and baseline.get("micro") is not None:
        drop = baseline["micro"] - metrics["micro"]
        if drop > MAX_REG_DROP:
            print(f"FAIL: regression {drop:.3f} > {MAX_REG_DROP} (baseline {baseline['micro']:.3f})")
            save_json(OUT_FILE, metrics)
            sys.exit(1)

    print("PASS ✅")
    save_json(OUT_FILE, metrics)
    # tip: copy latest → baseline in CI after main merges
