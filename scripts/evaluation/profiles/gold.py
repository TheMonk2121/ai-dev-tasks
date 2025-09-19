from __future__ import annotations

from typing import Any

from . import ProfileRunner


def _run_gold(_argv: list[str]) -> int:  # Unused parameter
    # Defer heavy imports to runtime
    try:
        from scripts.evaluation.clean_dspy_evaluator import CleanDSPyEvaluator  # type: ignore
    except Exception as exc:  # pragma: no cover - import-time issues
        print(f"❌ CRITICAL: Failed to load evaluator for gold profile: {exc}")
        print("   This indicates a serious configuration or dependency issue.")
        print("   The gold profile cannot run without the CleanDSPyEvaluator.")
        print("   Check that all dependencies are installed and paths are correct.")
        return 1

    try:
        evaluator: Any = CleanDSPyEvaluator(profile="gold")
        _ = evaluator.run_evaluation(
            gold_file="evals/data/gold/v1/gold_cases_121.jsonl",
            limit=None,
        )
    except Exception as exc:
        print(f"❌ CRITICAL: Gold evaluation failed: {exc}")
        print("   This indicates a serious runtime issue with the evaluation system.")
        print("   The gold profile is required for baseline enforcement and PR gates.")
        print("   This failure will block CI/CD pipelines.")
        return 1
    return 0


RUNNER = ProfileRunner(
    name="gold",
    description="Curated gold cases; baseline and PR gates",
    run=_run_gold,
)
