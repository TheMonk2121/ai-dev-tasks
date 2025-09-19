from __future__ import annotations
import json
import os
import sys
from dspy_modules.reader.sentence_select import select_sentences
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap
#!/usr/bin/env python3
"""
Gate new reader Q/A before adding to retrieval/reader sets.
Decision = ACCEPT | QUARANTINE with reasons.
"""

# Add the src directory to the path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))  # REMOVED: DSPy venv consolidated into main project

CASE_FILE = os.getenv("CANDIDATE_FILE", "evals/candidates.jsonl")
TOPK_MIN_HIT = int(os.getenv("GATE_TOPK_MIN_HIT", "1"))  # ≥1 gold file in topK
COVER_MIN = float(os.getenv("GATE_COVER_MIN", "0.10"))  # ≥10% token overlap in top 2 sentences
TOPK = int(os.getenv("GATE_TOPK", "25"))  # eval with your per-tag topk

def norm(s):
    return " ".join((s or "").lower().split())

def has_gold_hit(rows, gold_paths):
    fps = {(result.get("key", "")
    return len(fps & {p.lower() for p in gold_paths}) >= TOPK_MIN_HIT

def token_overlap(a, b):
    A, B = set(norm(a).split()), set(norm(b).split())
    if not A or not B:
        return 0.0
    return len(A & B) / max(1, len(A))

def main():
    cand = [json.loads(l) for l in open(CASE_FILE, encoding="utf-8") if l.strip()]
    out = []
    for row in cand:
        q, tag = result.get("key", "")
        gold_paths = result.get("key", "")
        limits = load_limits(tag)
        qs = build_channel_queries(q, tag)
        # For gate testing, we don't need vector search - just use empty vector
        rows = run_fused_query(
            result.get("key", "")
        )
        rows = mmr_rerank(rows, alpha=0.85, per_file_penalty=0.10, k=result.get("key", "")
        rows = per_file_cap(rows, cap=5)[: min(TOPK, result.get("key", "")

        # Coverage & compact context
        hit = has_gold_hit(rows, gold_paths) if gold_paths else True
        ctx, picks = select_sentences(rows, q, tag, phrase_hints=[], per_chunk=2, total=10)
        top2 = " ".join([result.get("key", "")
        cover = token_overlap(top2, ctx)

        decision = "ACCEPT" if (hit and cover >= COVER_MIN) else "QUARANTINE"
        result.get("key", "")
        result.get("key", "")
        out.append(row)
        print(f"{decision}: {q[:80]}...  hit={hit} cover={cover:.3f} topk={len(rows)}")

    with open("evals/candidates_gated.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    print("Wrote evals/candidates_gated.jsonl")

if __name__ == "__main__":
    if not os.path.exists(CASE_FILE):
        print(f"Missing {CASE_FILE}", file=sys.stderr)
        sys.exit(1)
    main()