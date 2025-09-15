from __future__ import annotations
import json
import os
import re
import shlex
import subprocess
import sys
from collections import defaultdict
from _bootstrap import ROOT, SRC  # noqa: F401
from sentence_transformers import SentenceTransformer
from dspy_modules.reader.entrypoint import build_reader_context
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import PHRASE_HINTS, build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap
from src.utils.gold_loader import load_gold_cases as _load_v1
from src.schemas.eval import Mode
from src.dspy_modules.dspy_reader_program import _apply_cross_encoder_rerank
#!/usr/bin/env python3

# bootstrap
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
src_dir = os.path.join(repo_root, "src")
sys.path.insert(0, repo_root)
sys.path.insert(0, src_dir)

# Unified v1 gold dataset (reader-mode)
GOLD_FILE = os.getenv("GOLD_FILE", "evals/gold/v1/gold_cases.jsonl")
READER_ID_MAP = os.getenv("READER_ID_MAP")  # optional mapping; rarely needed with v1
# Default to the new extractive reader CLI if not provided
# You can still override via: export READER_CMD="uv run python scripts/run_dspy_reader.py" (or custom)
READER_CMD = os.getenv("READER_CMD", "uv run python scripts/run_extractive_reader.py")
ALPHA = float(os.getenv("MMR_ALPHA", "0.85"))
PER_FILE_CAP = int(os.getenv("PER_FILE_CAP", "5"))

MIN_F1_MICRO = float(os.getenv("READER_MIN_F1_MICRO", "0.35"))
MIN_F1_TAG = float(os.getenv("READER_MIN_F1_TAG", "0.25"))
MAX_REG_DROP = float(os.getenv("MAX_READER_REG_DROP", "0.05"))
FAIL_ON_MISSING = bool(int(os.getenv("READER_FAIL_ON_MISSING_ID", "1")))

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

def load_v1_reader_cases_and_gold(path: str):
    """Load v1 gold cases and build a simple reader gold mapping.

    Returns a tuple (cases, gold_map) where cases are reader-mode GoldCase
    objects and gold_map maps case_id -> {"answers": [gt_answer]}.
    """
    all_cases = _load_v1(path)
    cases = [c for c in all_cases if getattr(c, "mode", None) == Mode.reader and (c.gt_answer or "").strip()]

    # Optional ID remapping support (rarely needed in v1)
    id_map = {}
    if READER_ID_MAP and os.path.exists(READER_ID_MAP):
        try:
            id_map = json.load(open(READER_ID_MAP, encoding="utf-8"))
        except Exception:
            id_map = {}

    gold = {}
    for c in cases:
        key = c.id
        row = {"answers": [c.gt_answer]}
        gold[key] = row
        # Add remap entries if provided
        for old, new in id_map.items():
            if new == key:
                gold.setdefault(old, row)

    return cases, gold

def run_reader_cmd(query, context, tag, case_id):
    if not READER_CMD:
        raise RuntimeError(
            "READER_CMD not set (e.g., export READER_CMD='uv run python scripts/run_reader.py --model local')"
        )
    payload = json.dumps({"query": query, "context": context, "tag": tag, "case_id": case_id})
    proc = subprocess.run(shlex.split(READER_CMD), input=payload.encode("utf-8"), capture_output=True)
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
    missing = 0

    # Initialize sentence transformer for query vector generation
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")

    for case in cases:
        g = gold.get(case.id)
        if not g:
            missing += 1
            continue  # conservatively skip; handle after loop
        tag = case.tags[0] if case.tags else "general"
        lim = load_limits(tag)
        qs = build_channel_queries(case.query, tag)

        # Generate query vector if empty
        qvec = getattr(case, "qvec", None)
        if not qvec:
            qvec = model.encode(case.query, normalize_embeddings=True)

        # shortlist → Cross-encoder rerank (if enabled) → MMR → cap → topk
        rows = run_fused_query(
            qs["short"], qs["title"], qs["bm25"], qvec, tag=tag, k=lim["shortlist"], return_components=True
        )

        # Apply cross-encoder reranking if enabled
        rerank_enable = bool(int(os.getenv("RERANK_ENABLE", "0")))
        if rerank_enable:
            try:

                input_topk = int(os.getenv("RERANK_INPUT_TOPK", "40"))
                rerank_keep = int(os.getenv("RERANK_KEEP", "10"))
                print(
                    f"[reranker] Applying cross-encoder reranking: input_topk={input_topk}, rerank_keep={rerank_keep}"
                )
                rows, rerank_method = _apply_cross_encoder_rerank(case.query, rows, input_topk, rerank_keep)
                print(f"[reranker] Cross-encoder method: {rerank_method}")
            except Exception as e:
                print(f"[reranker] Cross-encoder failed, falling back to MMR: {e}")

        rows = mmr_rerank(rows, alpha=ALPHA, per_file_penalty=0.10, k=lim["shortlist"])
        rows = per_file_cap(rows, cap=PER_FILE_CAP)[: lim["topk"]]
        context, _meta = build_reader_context(
            rows, case.query, tag, compact=bool(int(os.getenv("READER_COMPACT", "1")))
        )
        pred = run_reader_cmd(case.query, context, tag, case.id)
        f1 = f1_score(pred, g["answers"])
        tag_f1_sum[tag] += f1
        tag_cnt[tag] += 1
        f1_sum += f1
    total = sum(tag_cnt.values()) or 1
    micro = f1_sum / total
    per_tag = {t: (tag_f1_sum[t] / max(1, tag_cnt[t])) for t in tag_cnt}
    macro = sum(per_tag.values()) / max(1, len(per_tag))
    return {"micro": micro, "macro": macro, "per_tag": per_tag, "total_cases": total, "missing": missing}

def load_baseline(path):
    if not os.path.exists(path):
        return None
    return json.load(open(path, encoding="utf-8"))

def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=2)

if __name__ == "__main__":
    # Load reader-mode cases and gold answers from v1 dataset
    cases, gold = load_v1_reader_cases_and_gold(GOLD_FILE)
    metrics = eval_reader(cases, gold)
    if metrics.get("missing", 0):
        print(f"[reader] missing gold cases for {metrics['missing']} retrieval ids")
        if FAIL_ON_MISSING:
            print("FAIL: missing reader gold entries; set READER_FAIL_ON_MISSING_ID=0 to bypass during migration")
            save_json(OUT_FILE, metrics)
            sys.exit(1)
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
