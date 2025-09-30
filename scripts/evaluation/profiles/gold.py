from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import ProfileRunner

if TYPE_CHECKING:
    pass


def _load_real_limit_evaluator() -> type[Any]:
    """Load the real LIMIT-inspired evaluator."""
    from evals.scripts.evaluation.ragchecker_limit_inspired_evaluation import (
        LimitInspiredEvaluator,
    )
    return LimitInspiredEvaluator


def _run_gold(argv: list[str]) -> int:
    # Minimal argv parsing for --limit and --outdir
    limit: int | None = None
    outdir: Path | None = None
    if "--limit" in argv:
        try:
            i = argv.index("--limit")
            limit = int(argv[i + 1])
        except Exception:
            limit = None
    if "--outdir" in argv:
        try:
            i = argv.index("--outdir")
            outdir = Path(argv[i + 1]) if i + 1 < len(argv) else None
        except Exception:
            outdir = None

    use_limit = os.getenv("USE_LIMIT", os.getenv("RAGCHECKER_USE_LIMIT", "0"))
    report: dict[str, Any]
    if use_limit == "1":
        try:
            evaluator_cls = _load_real_limit_evaluator()
            evaluator = evaluator_cls()
            # LIMIT path requires a concrete loader; if missing, fall back
            if not hasattr(evaluator, "load_test_cases"):
                raise AttributeError("load_test_cases not implemented in LIMIT evaluator")
            cases = evaluator.load_test_cases()
            if not cases:
                raise RuntimeError("LIMIT evaluator returned no test cases")
            report = evaluator.evaluate_with_limit_features(cases)
        except Exception as e:
            print(f"❌ LIMIT path unavailable: {e}. Falling back to DSPy evaluator.")
            use_limit = "0"

    if use_limit != "1":
        # Fallback: DSPy evaluator with gold profile
        from scripts.evaluation.dspy_evaluator import (  # type: ignore[import-untyped]
            CleanDSPyEvaluator,
        )

        evaluator: Any = CleanDSPyEvaluator()
        gold_file = os.getenv("GOLD_CASES_PATH", "evals/data/gold/v1/gold_cases_121.jsonl")
        report = evaluator.run_evaluation(gold_file=gold_file, limit=limit)

    # Write results
    if outdir is None:
        outdir = Path("metrics/baseline_evaluations")
    outdir.mkdir(parents=True, exist_ok=True)
    output_path = outdir / "results.json"

    def json_serializer(obj: Any) -> Any:
        if isinstance(obj, bool):
            return obj
        if hasattr(obj, "item"):
            return obj.item()
        if hasattr(obj, "tolist"):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    output_path.write_text(json.dumps(report, indent=2, default=json_serializer), encoding="utf-8")
    print(f"📁 Gold profile results saved to: {output_path}")

    compliance = report.get("baseline_compliance", {})
    all_passed = all(compliance.values()) if compliance else True
    return 0 if all_passed else 2


RUNNER = ProfileRunner("gold", "Curated gold cases; baseline and PR gates", _run_gold)
