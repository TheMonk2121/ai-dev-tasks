#!/usr/bin/env python3
"""Compatibility bridge that re-exports the canonical DSPy evaluator."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import from the actual dspy_evaluator in evals directory
from evals.scripts.evaluation.dspy_evaluator import (
    CleanDSPyEvaluator as _RealCleanDSPyEvaluator,
)

if TYPE_CHECKING:
    from evals.scripts.evaluation.dspy_evaluator import (
        CleanDSPyEvaluator as CleanDSPyEvaluatorType,
    )


CleanDSPyEvaluator: type[CleanDSPyEvaluatorType] = _RealCleanDSPyEvaluator

__all__ = ["CleanDSPyEvaluator"]
