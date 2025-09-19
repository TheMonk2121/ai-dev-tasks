from __future__ import annotations

from typing import Any

from . import ProfileRunner


def _run_real(_argv: list[str]) -> int:  # Unused parameter
    try:
        from scripts.evaluation.clean_dspy_evaluator import CleanDSPyEvaluator  # type: ignore
    except Exception as exc:  # pragma: no cover
        print(f"Failed to load evaluator for real profile: {exc}")
        return 1

    evaluator: Any = CleanDSPyEvaluator()
    try:
        _ = evaluator.run_evaluation(
            gold_file="evals/data/real/v1/real_cases.jsonl",
            limit=None,
        )
    except Exception as exc:
        print(f"Real evaluation failed: {exc}")
        return 1
    return 0


RUNNER = ProfileRunner(
    name="real",
    description="Full retrieval + reader on project data",
    run=_run_real,
)
