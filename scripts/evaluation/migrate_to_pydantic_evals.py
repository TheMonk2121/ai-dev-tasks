from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
Migration helper to convert legacy load_eval_cases usage to Pydantic Evals framework.

This script provides compatibility functions to help migrate existing scripts
from the deprecated evals.load_cases to the new Pydantic Evals framework.
"""

import json
import os
import sys
import warnings
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydantic_evals.dataset import Case, Dataset

from src.schemas.eval import GoldCase

def load_eval_cases_pydantic(profile: str | Path = "gold") -> list[GoldCase]:
    """
    Replacement for evals.load_cases.load_eval_cases using Pydantic Evals framework.

    This function provides the same interface as the deprecated load_eval_cases
    but uses the new Pydantic Evals framework internally.

    Args:
        profile: Profile name or path to evaluation cases file

    Returns:
        List of GoldCase objects (same as legacy load_eval_cases)
    """
    # Issue deprecation warning for the old function
    warnings.warn(
        "Using legacy load_eval_cases interface. Consider migrating to pydantic_evals.dataset.Dataset directly.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Resolve path: prefer unified v1 JSONL via GOLD_FILE
    if isinstance(profile, (str, Path)) and str(profile).startswith("gold"):
        path = os.getenv("GOLD_FILE", os.getenv("CASES_FILE", "evals/gold/v1/gold_cases.jsonl"))
    else:
        path = str(profile)

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Cases file not found: {path}")

    # Load via canonical loader for JSONL; fallback to legacy JSON parser
    if p.suffix.lower() == ".jsonl":
        try:
            from src.utils.gold_loader import load_gold_cases as _load_v1

            return _load_v1(str(p))
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Failed to load v1 gold cases from {p}: {e}")
    else:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Normalize iterable to list
        if isinstance(data, dict):
            data = [data]

        # Convert to GoldCase objects using Pydantic validation
        cases: list[GoldCase] = []
        for obj in data:
            try:
                legacy_obj = obj.copy()

                if "mode" not in legacy_obj:
                    legacy_obj["mode"] = "retrieval"
                if "tags" not in legacy_obj:
                    legacy_obj["tags"] = []
                elif isinstance(legacy_obj["tags"], str):
                    legacy_obj["tags"] = [legacy_obj["tags"]]

                case = GoldCase.model_validate(legacy_obj)
                cases.append(case)
            except Exception as e:  # pragma: no cover
                warnings.warn(
                    f"Failed to validate case {obj.get('id', 'unknown')}: {e}. Skipping.", UserWarning, stacklevel=2
                )
                continue

        return cases

def create_pydantic_evals_dataset(cases: list[GoldCase]) -> Dataset:
    """
    Convert GoldCase objects to Pydantic Evals Dataset.

    This is the recommended way to work with evaluation cases in the new framework.

    Args:
        cases: List of GoldCase objects

    Returns:
        Pydantic Evals Dataset
    """
    # Define Pydantic models for inputs and outputs
    from pydantic import BaseModel, ConfigDict

    class EvalInput(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        query: str
        mode: str
        tags: list[str]
        category: str | None = None
        notes: str | None = None

    class EvalOutput(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        gt_answer: str | None = None
        expected_files: list[str] | None = None
        globs: list[str] | None = None
        expected_decisions: list[str] | None = None

    # Convert GoldCase objects to Pydantic Evals Case objects
    eval_cases = []
    for case in cases:
        try:
            # Create Pydantic model instances for inputs and outputs
            eval_input = EvalInput(
                query=case.query,
                mode=case.mode.value if hasattr(case.mode, "value") else str(case.mode),
                tags=case.tags,
                category=case.category,
                notes=case.notes,
            )

            eval_output = EvalOutput(
                gt_answer=case.gt_answer,
                expected_files=case.expected_files,
                globs=case.globs,
                expected_decisions=case.expected_decisions,
            )

            # Create a comprehensive input/output structure for Pydantic Evals
            eval_case = Case(
                name=case.id,
                inputs=eval_input,
                expected_output=eval_output,
                metadata={
                    "case_id": case.id,
                    "mode": case.mode.value if hasattr(case.mode, "value") else str(case.mode),
                    "tags": case.tags,
                    "category": case.category,
                    "notes": case.notes,
                    "has_gt_answer": bool(case.gt_answer),
                    "has_expected_files": bool(case.expected_files),
                    "has_globs": bool(case.globs),
                    "has_expected_decisions": bool(case.expected_decisions),
                },
            )
            eval_cases.append(eval_case)
        except Exception as e:
            warnings.warn(
                f"Failed to convert case {case.id} to Pydantic Evals format: {e}. Skipping.", UserWarning, stacklevel=2
            )
            continue

    return Dataset[EvalInput, EvalOutput](cases=eval_cases)

# Backward compatibility: provide the same interface as the old function
def load_eval_cases(profile: str | Path = "gold") -> list[GoldCase]:
    """
    Backward compatibility function that mimics the old load_eval_cases interface.

    This function provides a drop-in replacement for the deprecated load_eval_cases
    function, allowing existing scripts to work with minimal changes.
    """
    return load_eval_cases_pydantic(profile)

if __name__ == "__main__":
    # Test the migration helper
    print("Testing Pydantic Evals migration helper...")

    try:
        # Test loading cases
        cases = load_eval_cases("gold")
        print(f"✅ Loaded {len(cases)} cases using new Pydantic framework")

        # Test creating dataset
        if cases:
            dataset = create_pydantic_evals_dataset(cases)
            print(f"✅ Created Pydantic Evals dataset with {len(dataset.cases)} cases")

        print("✅ Migration helper working correctly!")

    except Exception as e:
        print(f"❌ Error testing migration helper: {e}")
        sys.exit(1)
