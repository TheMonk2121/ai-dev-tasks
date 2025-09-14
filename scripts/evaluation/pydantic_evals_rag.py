from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
import importlib
from os.path import basename
from src.common.db_dsn import resolve_dsn
from src.utils.gold_loader import load_gold_cases as _load_v1
from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
Pydantic Evals integration demo for the RAG pipeline.

This script does not change core code; it adapts existing eval assets into
Pydantic Evals Datasets and evaluates the RAG task with lightweight, local
evaluators (no LLM judge required).

Usage examples:
  - Evaluate unit-style cases (expected answer substrings):
      python scripts/pydantic_evals_rag.py --suite unit

  - Evaluate gold cases (expected citations by file path):
      python scripts/pydantic_evals_rag.py --suite gold

  - Both suites:
      python scripts/pydantic_evals_rag.py --suite both

Notes:
  - Requires `pydantic-evals` (>=0.0.47). Install:
      pip install pydantic-evals
    Optional OpenTelemetry/Logfire:
      pip install 'pydantic-evals[logfire]'
  - Respects DATABASE_URL/POSTGRES_DSN via src/common/db_dsn.resolve_dsn.
  - Sets EVAL_DISABLE_CACHE=1 to minimize retrieval caching during evals.
"""

# Bootstrap sys.path for local imports regardless of CWD
try:
    _ROOT = Path(__file__).resolve().parents[1]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    _DSPY_SRC = _ROOT / "dspy-rag-system" / "src"
    if _DSPY_SRC.exists() and str(_DSPY_SRC) not in sys.path:
        sys.path.insert(0, str(_DSPY_SRC))
except Exception:
    pass

def _require_pydantic_evals():
    try:
        # Imports are scoped so the script still loads to print helpful errors if missing
        global Case, Dataset, Evaluator, EvaluatorContext, IsInstance
        from pydantic_evals import Case, Dataset
        from pydantic_evals.evaluators import Evaluator, EvaluatorContext, IsInstance
        return Case, Dataset, Evaluator, EvaluatorContext, IsInstance
    except Exception as e:  # pragma: no cover
        print(
            "\n❌ pydantic-evals is not installed.\n"
            "Install with: pip install pydantic-evals\n"
            f"Import error: {e}\n",
            file=sys.stderr,
        )
        sys.exit(2)

def _resolve_dsn() -> str | None:
    """Resolve a database DSN via canonical helper with safe fallback."""
    try:
        return resolve_dsn(strict=False)  # type: ignore[no-any-return]
    except Exception:
        # Conservative local default
        return os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN") or "postgresql://localhost:5432/ai_agency"

def _rag_task_factory():
    """Return a callable(question:str)->Dict compatible with RAG pipeline."""
    dsn = _resolve_dsn()
    # Disable caches for deterministic-ish runs
    os.environ.setdefault("EVAL_DISABLE_CACHE", "1")

    # Late import to avoid heavy deps if user only wants help text

    rp = importlib.import_module("dspy_modules.rag_pipeline")
    pipe = rp.RAGPipeline(dsn)

    def task(question: str) -> dict[str, Any]:
        # Preferred: full RAG answer (requires DSPy LM configured)
        try:
            return pipe.answer(question)
        except Exception as e:
            # Fallback: retrieval-only mode using debug_retrieval
            try:
                dbg = pipe.debug_retrieval(question, k=8)
                hits = list(dbg.get("hits") or []) if isinstance(dbg, dict) else []
                cites = [str(h.get("title") or "") for h in hits if h]
                return {"answer": "", "citations": cites, "context_used": False, "_fallback": f"retrieval_only: {e}"}
            except Exception:
                raise

    return task

def _load_unit_cases() -> list[dict[str, Any]]:
    """Load unit-style cases from eval/test_cases.json.

    Schema example:
      {"query": str, "answer": str, "context": [str, ...]}
    """
    p = Path("eval/test_cases.json")
    if not p.exists():
        return []
    return json.loads(p.read_text())

def _load_gold_cases() -> list[dict[str, Any]]:
    """Load gold cases from unified v1 JSONL.

    Source of truth: evals/gold/v1/gold_cases.jsonl
    We project retrieval-mode cases with explicit expected_files into
    the {id, query, file_paths, globs, tags} shape used by this script.
    """
    p = Path("evals/gold/v1/gold_cases.jsonl")
    if not p.exists():
        return []

    # Use the canonical loader
    try:
        cases = _load_v1(str(p))
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for c in cases:
        # Keep only cases that supervise retrieval with concrete targets
        fps = list(c.expected_files or [])
        if not fps:
            continue
        out.append(
            {
                "id": c.id,
                "query": c.query,
                "file_paths": fps,
                "globs": list(c.globs or []),
                "tags": list(c.tags or []),
                "mode": str(c.mode),
            }
        )
    return out

def build_unit_dataset():

    unit = _load_unit_cases()
    cases: list[Case[str, dict[str, Any], dict[str, Any]]] = []

    for i, row in enumerate(unit):
        q = str(row.get("query", "")).strip()
        expected = str(row.get("answer", "")).strip()
        meta = {"context": row.get("context") or []}
        cases.append(Case(name=f"unit_{i+1}", inputs=q, expected_output=expected, metadata=meta))

    # Custom evaluator: answer equals/contains expected
    class AnswerMatches(Evaluator[dict[str, Any], str]):
        def evaluate(self, ctx: EvaluatorContext[dict[str, Any], str]) -> float:
            out = ctx.output or {}
            ans = str(out.get("answer", ""))
            exp = str(ctx.expected_output or "")
            if not exp:
                return 0.0
            if ans == exp:
                return 1.0
            if exp.lower() in ans.lower():
                return 0.8
            return 0.0

    # Custom evaluator: mentions any provided context spans
    class MentionsContext(Evaluator[dict[str, Any], str]):
        def evaluate(self, ctx: EvaluatorContext[dict[str, Any], str]) -> float:
            out = ctx.output or {}
            ans = str(out.get("answer", ""))
            ctx_list = list((ctx.metadata or {}).get("context") or [])
            if not ctx_list:
                return 0.0
            hits = sum(1 for s in ctx_list if isinstance(s, str) and s and s.lower() in ans.lower())
            return 1.0 if hits >= max(1, len(ctx_list) // 2) else (0.5 if hits else 0.0)

    dataset = Dataset(
        cases=cases,
        evaluators=[IsInstance(type_name="dict"), AnswerMatches(), MentionsContext()],
    )
    return dataset

def build_gold_dataset():

    gold = _load_gold_cases()
    cases: list[Case[str, list[str], dict[str, Any]]] = []

    for row in gold:
        q = str(row.get("query", "")).strip()
        exp_files = list(row.get("file_paths") or [])
        name = str(row.get("id") or row.get("name") or q[:40] or "gold_case")
        meta = {k: row.get(k) for k in ("globs", "tags") if k in row}
        # expected_output carries list[str] of target file paths
        cases.append(Case(name=name, inputs=q, expected_output=exp_files, metadata=meta))

    # Custom evaluator: any expected file appears in citations
    class CitationsHit(Evaluator[dict[str, Any], list[str]]):
        def evaluate(self, ctx: EvaluatorContext[dict[str, Any], list[str]]) -> float:
            out = ctx.output or {}
            cites = [str(x) for x in (out.get("citations") or [])]
            expected = [str(x) for x in (ctx.expected_output or [])]
            if not expected:
                return 0.0

            # Match on full path or basename containment
            def match(one: str, two: str) -> bool:

                return one == two or basename(one) in two or basename(two) in one

            ok = any(match(e, c) for e in expected for c in cites)
            return 1.0 if ok else 0.0

    dataset = Dataset(
        cases=cases,
        evaluators=[IsInstance(type_name="dict"), CitationsHit()],
    )
    return dataset

def main():
    _require_pydantic_evals()
    parser = argparse.ArgumentParser(description="Evaluate RAG with Pydantic Evals")
    parser.add_argument(
        "--suite",
        choices=["unit", "gold", "both"],
        default="both",
        help="Which dataset suite to run",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=int(os.getenv("EVAL_MAX_CONCURRENCY", "4")),
        help="Concurrency during evaluation",
    )
    args = parser.parse_args()

    task = _rag_task_factory()

    ran_any = False
    if args.suite in ("unit", "both"):
        unit_ds = build_unit_dataset()
        if unit_ds.cases:
            print("\n=== Pydantic Evals: Unit Cases ===\n")
            report = unit_ds.evaluate_sync(task, max_concurrency=args.max_concurrency)
            report.print(include_input=True, include_output=False, include_durations=False)
            ran_any = True
        else:
            print("(No unit cases found at eval/test_cases.json)")

    if args.suite in ("gold", "both"):
        gold_ds = build_gold_dataset()
        if gold_ds.cases:
            print("\n=== Pydantic Evals: Gold Cases (Citations) ===\n")
            report = gold_ds.evaluate_sync(task, max_concurrency=args.max_concurrency)
            report.print(include_input=True, include_output=False, include_durations=False)
            ran_any = True
        else:
            print("(No gold cases found at evals/gold_cases.json)")

    if not ran_any:
        print(
            "\nNo cases to run. Ensure eval/test_cases.json or evals/gold_cases.json exist.\n"
            "See this script’s header for details.",
            file=sys.stderr,
        )

if __name__ == "__main__":
    main()
