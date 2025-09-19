#!/usr/bin/env python3
"""
Thin wrapper that delegates to the canonical evaluator at
`evals/scripts/evaluation/dspy_evaluator.py` while preserving
the historic import path `scripts.evaluation.clean_dspy_evaluator`.

The actual evaluator implementation lives in evals/scripts/evaluation/dspy_evaluator.py.
This wrapper exists only for backward compatibility.
"""

from __future__ import annotations

from typing import cast

# Prefer absolute import from the vendored evals package
try:
    from evals.scripts.evaluation.dspy_evaluator import (  # type: ignore[import]
        CleanDSPyEvaluator as _CleanDSPyEvaluator,
    )
    from evals.scripts.evaluation.dspy_evaluator import (
        main as _impl_main,
    )
except Exception as _e:  # Fallback: re-raise with clearer context
    raise ImportError(
        "Failed to import evals.scripts.evaluation.dspy_evaluator. "
        + "Ensure the 'evals' package directory exists and is on sys.path."
    ) from _e


# Re-export primary symbols used by tests and callers with explicit typing
CleanDSPyEvaluator = _CleanDSPyEvaluator


def main() -> None:
    _impl_main()
    return None


__all__ = ["CleanDSPyEvaluator", "main"]


if __name__ == "__main__":
    main()
