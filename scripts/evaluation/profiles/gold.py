from __future__ import annotations

from typing import Any

from . import ProfileRunner


def _run_gold(_argv: list[str]) -> int:  # Unused parameter
    # Defer heavy imports to runtime
    try:
        from scripts.evaluation.clean_dspy_evaluator import CleanDSPyEvaluator  # type: ignore
    except Exception as exc:  # pragma: no cover - import-time issues
        print(f"Failed to load evaluator for gold profile: {exc}")
        return 1

    evaluator: Any = CleanDSPyEvaluator()
    try:
        _ = evaluator.run_evaluation(
            gold_file="evals/data/gold/v1/gold_cases_121.jsonl",
            limit=None,
        )
    except Exception as exc:
        print(f"Gold evaluation failed: {exc}")
        return 1
    return 0


RUNNER = ProfileRunner(
    name="gold",
    description="Curated gold cases; baseline and PR gates",
    run=_run_gold,
)
