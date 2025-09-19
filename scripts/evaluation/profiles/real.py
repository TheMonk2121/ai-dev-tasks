from __future__ import annotations

from typing import Any

from . import ProfileRunner


def _run_real(_argv: list[str]) -> int:  # Unused parameter
    try:
        from scripts.evaluation.clean_dspy_evaluator import CleanDSPyEvaluator  # type: ignore
    except Exception as exc:  # pragma: no cover
        print(f"❌ CRITICAL: Failed to load evaluator for real profile: {exc}")
        print("   This indicates a serious configuration or dependency issue.")
        print("   The real profile cannot run without the CleanDSPyEvaluator.")
        print("   Check that all dependencies are installed and paths are correct.")
        return 1

    try:
        evaluator: Any = CleanDSPyEvaluator(profile="real")
        _ = evaluator.run_evaluation(
            gold_file="evals/data/real/v1/real_cases.jsonl",
            limit=None,
        )
    except Exception as exc:
        print(f"❌ CRITICAL: Real evaluation failed: {exc}")
        print("   This indicates a serious runtime issue with the evaluation system.")
        print("   The real profile is required for full system validation.")
        print("   This failure indicates a fundamental problem with the RAG system.")
        return 1
    return 0


RUNNER = ProfileRunner(
    name="real",
    description="Full retrieval + reader on project data",
    run=_run_real,
)
