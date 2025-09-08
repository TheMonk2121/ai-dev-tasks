#!/usr/bin/env python3
"""
Debug A/B test to ensure DSPy reader controls are wired the same way in every path.
Compares uncompiled vs compiled DSPy reader on the same context.
"""
import json
import os
import sys

sys.path.insert(0, "dspy-rag-system/src")
import dspy
from dspy_modules.dspy_reader_program import RAGAnswer, _lm
from dspy_modules.reader.entrypoint import build_reader_context
from dspy_modules.reader.span_picker import pick_span  # your rule-first
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap


def get_context(q, tag):
    lim = load_limits(tag)
    qs = build_channel_queries(q, tag)
    rows = run_fused_query(
        qs["short"], qs["title"], qs["bm25"], qvec=[], tag=tag, k=lim["shortlist"], return_components=True
    )
    rows = mmr_rerank(rows, alpha=float(os.getenv("MMR_ALPHA", "0.85")), per_file_penalty=0.10, k=lim["shortlist"])
    rows = per_file_cap(rows, cap=int(os.getenv("PER_FILE_CAP", "5")))[: lim["topk"]]
    ctx, meta = build_reader_context(rows, q, tag, compact=bool(int(os.getenv("READER_COMPACT", "1"))))
    return ctx, rows


def run_uncompiled(q, tag, ctx):
    dspy.settings.configure(lm=_lm())
    prog = RAGAnswer()
    # force same context: bypass internal retrieval by injecting rule-first → generator
    span = pick_span(ctx, q, tag)
    if span:
        return span
    out = prog.gen(context=ctx, question=q).answer
    return out


def run_compiled(q, tag, ctx):
    dspy.settings.configure(lm=_lm())
    try:
        prog = dspy.load("artifacts/dspy/rag_answer_compiled.json")
    except Exception:
        prog = RAGAnswer()
    # same forcing: use ctx directly if your compiled graph allows
    try:
        out = prog.gen(context=ctx, question=q).answer  # depends on how teleprompt compiled; adjust if needed
    except:
        # fallback: call prog(question, tag) and trust compiled retrieval (should match if limits equal)
        out = prog(question=q, tag=tag).answer
    return out


if __name__ == "__main__":
    q = os.getenv("Q") or "What is DSPy according to 400_07_ai-frameworks-dspy.md?"
    tag = os.getenv("TAG", "rag_qa_single")
    ctx, rows = get_context(q, tag)
    a = run_uncompiled(q, tag, ctx)
    b = run_compiled(q, tag, ctx)
    print(
        json.dumps(
            {"question": q, "tag": tag, "context_preview": ctx[:600], "A_rule_plus_gen": a, "B_compiled": b}, indent=2
        )
    )
