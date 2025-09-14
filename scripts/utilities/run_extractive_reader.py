from __future__ import annotations

import json
import os
import sys

import dspy  # type: ignore[import-untyped]

from dspy_modules.dspy_reader_program import _lm  # reuse shared LM configuration
from dspy_modules.reader import READER  # pre-configured ExtractiveReader instance

#!/usr/bin/env python3
"""
CLI shim to run the new ExtractiveReader on a provided context.

Reads a JSON payload from stdin with keys: {query, context, tag, case_id}
and prints a JSON object: {answer}.

This enables CI and tools that rely on READER_CMD to use the
new extractive reader without changing their call pattern.
"""

# Ensure module imports work when called from repo root
sys.path.insert(0, "src")

def _context_to_passages(context: str) -> list[str]:
    """Convert context text into a list of short passages/sentences.

    Works for both compact (sentence-selected) and fallback (concatenated files) contexts.
    Keeps lines short and non-empty; trims headers like "=== file ===".
    """
    if not context:
        return []
    lines = []
    for line in context.splitlines():
        s = (line or "").strip()
        if not s:
            continue
        # Drop simple headers inserted by context builder
        if s.startswith("=== ") and s.endswith(" ==="):
            continue
        lines.append(s)
    # Keep a modest number; the module will internally join the top few
    return lines[:24]

def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        query = payload.get("query", "")
        context = payload.get("context", "")
        tag = payload.get("tag", "general")

        # Configure LM for DSPy predictions (shared config/util)
        dspy.settings.configure(lm=_lm())

        passages = _context_to_passages(context)
        pred = READER(question=query, passages=passages, tag=tag)  # type: ignore[arg-type]
        # ExtractiveReader returns a dict-like prediction {"answer": str}
        answer = (pred or {}).get("answer", "") if isinstance(pred, dict) else getattr(pred, "answer", "")

        print(json.dumps({"answer": answer}))
        return 0
    except Exception as e:
        print(json.dumps({"answer": "", "error": str(e)}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
