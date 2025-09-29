from __future__ import annotations

import json
import time
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


def _run_gold(_argv: list[str]) -> int:
    try:
        # Use real LIMIT-inspired evaluator instead of basic DSPy evaluator
        evaluator_cls = _load_real_limit_evaluator()
    except Exception as exc:  # pragma: no cover - import failure
        print(f"❌ CRITICAL: Failed to load real LIMIT evaluator: {exc}")
        return 1

    evaluator = evaluator_cls()

    # Run real evaluation with LIMIT features
    try:
        cases = evaluator.load_test_cases()
        if not cases:
            print("⚠️ No test cases available; skipping evaluation")
            return 0

        report = evaluator.evaluate_with_limit_features(cases)
    except Exception as e:
        print(f"❌ CRITICAL: Real LIMIT evaluation failed: {e}")
        return 1

    output_dir = Path("metrics/baseline_evaluations")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"gold_profile_limit_eval_{int(time.time())}.json"
    # Ensure JSON serialization works with boolean values and numpy types
    def json_serializer(obj: Any) -> Any:
        if isinstance(obj, bool):
            return obj
        elif hasattr(obj, 'item'):  # numpy scalars
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy arrays
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    _ = output_path.write_text(json.dumps(report, indent=2, default=json_serializer), encoding="utf-8")
    print(f"📁 Gold profile results saved to: {output_path}")

    compliance = report.get("baseline_compliance", {})
    all_passed = all(compliance.values()) if compliance else True
    return 0 if all_passed else 2


RUNNER = ProfileRunner("gold", "Curated gold cases; baseline and PR gates", _run_gold)
