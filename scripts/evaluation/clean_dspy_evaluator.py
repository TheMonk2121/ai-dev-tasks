#!/usr/bin/env python3
"""
Wrapper that delegates to the canonical evaluator at
`evals/scripts/evaluation/clean_dspy_evaluator.py` while preserving
the historic import path `scripts.evaluation.clean_dspy_evaluator`.
"""

from __future__ import annotations

from typing import Any, cast

# Prefer absolute import from the vendored evals package
try:
    from evals.scripts.evaluation.clean_dspy_evaluator import (  # type: ignore[import]
        CleanDSPyEvaluator as _CleanDSPyEvaluator,
    )
    from evals.scripts.evaluation.clean_dspy_evaluator import (
        main as _impl_main,
    )
except Exception as _e:  # Fallback: re-raise with clearer context
    raise ImportError(
        "Failed to import evals.scripts.evaluation.clean_dspy_evaluator. "
        "Ensure the 'evals' package directory exists and is on sys.path."
    ) from _e


# Re-export primary symbols used by tests and callers with explicit typing
CleanDSPyEvaluator: type[object] = cast(type[object], _CleanDSPyEvaluator)


def main() -> None:
    _impl_main()
    return None


__all__ = ["CleanDSPyEvaluator", "main"]


if __name__ == "__main__":
    main()
