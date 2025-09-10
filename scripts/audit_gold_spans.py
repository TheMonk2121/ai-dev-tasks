#!/usr/bin/env python3
"""
Gold–Context Span Audit: catch silent F1 leaks from coverage mismatches.
Every gold answer must be an exact substring of the compact context for its case.
"""
import json
import os
import re
import sys

# Add the src directory to the path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))  # REMOVED: DSPy venv consolidated into main project
from dspy_modules.reader.sentence_select import select_sentences
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap

CASES = os.getenv("CASES_FILE", "evals/gold_cases.json")
GOLD = os.getenv("READER_GOLD_FILE", "evals/reader_gold_comprehensive.jsonl")


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def main():
    gold = {r["case_id"]: r for r in load_jsonl(GOLD)}
    cases = json.load(open(CASES, encoding="utf-8"))
    misses = []
    for c in cases:
        cid, q, tag = c["case_id"], c["query"], c.get("tag", "rag_qa_single")
        if cid not in gold:
            continue
        answers = gold[cid].get("answers", [])
        lim = load_limits(tag)
        qs = build_channel_queries(q, tag)
        rows = run_fused_query(
            qs["short"], qs["title"], qs["bm25"], qvec=[], tag=tag, k=lim["shortlist"], return_components=True
        )
        rows = mmr_rerank(rows, alpha=0.85, per_file_penalty=0.10, k=lim["shortlist"])
        rows = per_file_cap(rows, cap=5)[: lim["topk"]]
        context, picks = select_sentences(rows, q, tag, phrase_hints=[], per_chunk=2, total=10)
        ctxn = norm(context)
        ok = any(norm(a) in ctxn for a in answers if a)
        if not ok:
            misses.append(
                {"case_id": cid, "tag": tag, "query": q, "answers": answers[:5], "context_preview": context[:800]}
            )
    fp = "evals/audit_reader_span_misses.json"
    os.makedirs("evals", exist_ok=True)
    json.dump(misses, open(fp, "w", encoding="utf-8"), indent=2)
    print(f"Span misses: {len(misses)}  → {fp}")


if __name__ == "__main__":
    main()
