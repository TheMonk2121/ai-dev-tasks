#!/usr/bin/env python3
import json
import os
import re
import shlex
import subprocess
import sys
from collections import defaultdict

# bootstrap
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from _bootstrap import ROOT, SRC  # noqa: F401
from dspy_modules.reader.entrypoint import build_reader_context
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import PHRASE_HINTS, build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap

from evals.load_cases import load_eval_cases

READER_GOLD = os.getenv("READER_GOLD_FILE", "evals/reader_gold.jsonl")
READER_CMD = os.getenv("READER_CMD")  # e.g., "python3 scripts/run_reader.py --model local"
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))
PER_FILE_CAP = int(os.getenv("PER_FILE_CAP", "5"))

MIN_F1_MICRO = float(os.getenv("READER_MIN_F1_MICRO", "0.35"))
MIN_F1_TAG = float(os.getenv("READER_MIN_F1_TAG", "0.25"))
MAX_REG_DROP = float(os.getenv("MAX_READER_REG_DROP", "0.05"))

BASELINE_FILE = os.getenv("READER_BASELINE_FILE", "evals/baseline_reader_metrics.json")
OUT_FILE = os.getenv("LATEST_READER_FILE", "evals/latest_reader_metrics.json")


def _norm(s):  # SQuAD-style normalization
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def f1_score(pred, golds):
    p = _norm(pred)
    best = 0.0
    for g in golds:
        g = _norm(g)
        p_toks = p.split()
        g_toks = g.split()
        if not p_toks and not g_toks:
            return 1.0
        if not p_toks or not g_toks:
            continue
        common = {}
        for t in p_toks:
            if t in g_toks:
                common[t] = min(p_toks.count(t), g_toks.count(t))
        num_same = sum(common.values())
        if num_same == 0:
            f1 = 0.0
        else:
            precision = num_same / len(p_toks)
            recall = num_same / len(g_toks)
            f1 = 2 * precision * recall / (precision + recall)
        best = max(best, f1)
    return best


def load_reader_gold(path):
    gold = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            gold[row["case_id"]] = row
    return gold


def run_reader_cmd(query, context, tag, case_id):
    if not READER_CMD:
        raise RuntimeError("READER_CMD not set (e.g., export READER_CMD='python3 scripts/run_reader.py --model local')")
    payload = json.dumps({"query": query, "context": context, "tag": tag, "case_id": case_id})
    proc = subprocess.run(
        shlex.split(READER_CMD), input=payload.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Reader failed: {proc.stderr.decode('utf-8', 'ignore')}")
    out = proc.stdout.decode("utf-8", "ignore").strip()
    try:
        obj = json.loads(out)
    except Exception:
        obj = {"answer": out}
    return obj.get("answer", "")


def eval_reader(cases, gold):
    tag_f1_sum, tag_cnt = defaultdict(float), defaultdict(int)
    f1_sum = 0.0
    for case in cases:
        g = gold.get(case.id)
        if not g:
            # Skip if no reader gold for this case
            continue
        lim = load_limits(case.tag)
        qs = build_channel_queries(case.query, case.tag)
        # shortlist → MMR → cap → topk
        rows = run_fused_query(
            qs["short"], qs["title"], qs["bm25"], case.qvec, tag=case.tag, k=lim["shortlist"], return_components=True
        )
        rows = mmr_rerank(rows, alpha=ALPHA, per_file_penalty=0.10, k=lim["shortlist"])
        rows = per_file_cap(rows, cap=PER_FILE_CAP)[: lim["topk"]]
        context, _meta = build_reader_context(
            rows, case.query, case.tag, compact=bool(int(os.getenv("READER_COMPACT", "1")))
        )
        pred = run_reader_cmd(case.query, context, case.tag, case.id)
        f1 = f1_score(pred, g["answers"])
        tag_f1_sum[case.tag] += f1
        tag_cnt[case.tag] += 1
        f1_sum += f1
    total = sum(tag_cnt.values()) or 1
    micro = f1_sum / total
    per_tag = {t: (tag_f1_sum[t] / max(1, tag_cnt[t])) for t in tag_cnt}
    macro = sum(per_tag.values()) / max(1, len(per_tag))
    return {"micro": micro, "macro": macro, "per_tag": per_tag, "total_cases": total}


def load_baseline(path):
    if not os.path.exists(path):
        return None
    return json.load(open(path, "r", encoding="utf-8"))


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=2)


if __name__ == "__main__":
    cases = load_eval_cases("gold")  # uses CASES_FILE env under the hood
    gold = load_reader_gold(READER_GOLD)
    metrics = eval_reader(cases, gold)
    print(f"[reader] micro={metrics['micro']:.3f} macro={metrics['macro']:.3f}")
    for t, v in sorted(metrics["per_tag"].items()):
        print(f"[reader][tag] {t}: {v:.3f}")

    # Floors
    if metrics["micro"] < MIN_F1_MICRO:
        print(f"FAIL: reader micro {metrics['micro']:.3f} < {MIN_F1_MICRO}")
        save_json(OUT_FILE, metrics)
        sys.exit(1)
    low = [t for t, v in metrics["per_tag"].items() if v < MIN_F1_TAG]
    if low:
        print(f"FAIL: reader per-tag floor {MIN_F1_TAG} violated: {low}")
        save_json(OUT_FILE, metrics)
        sys.exit(1)

    # Regression guard
    base = load_baseline(BASELINE_FILE)
    if base and base.get("micro") is not None:
        drop = base["micro"] - metrics["micro"]
        if drop > MAX_REG_DROP:
            print(f"FAIL: reader regression {drop:.3f} > {MAX_REG_DROP} (baseline {base['micro']:.3f})")
            save_json(OUT_FILE, metrics)
            sys.exit(1)

    print("PASS ✅")
    save_json(OUT_FILE, metrics)
