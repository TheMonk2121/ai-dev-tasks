#!/usr/bin/env python3
import json
import os
import sys

# sys.path.insert(0, "src")  # DSPy modules now in main src directory
import dspy

from dspy_modules.dspy_reader_program import RAGAnswer, _lm

if __name__ == "__main__":
    payload = json.loads(sys.stdin.read())
    query = payload["query"]
    tag = payload.get("tag", "rag_qa_single")

    # Load compiled if present; else run vanilla program
    dspy.settings.configure(lm=_lm())
    try:
        prog = dspy.load("artifacts/dspy/rag_answer_compiled.json")
    except Exception:
        prog = RAGAnswer()

    pred = prog(question=query, tag=tag)
    # Handle both compiled and uncompiled program outputs
    if hasattr(pred, "answer"):
        answer = getattr(pred, "answer", "")
    else:
        # For compiled programs, the output might be different
        answer = str(pred) if pred else "I don't know"
    print(json.dumps({"answer": answer}))
