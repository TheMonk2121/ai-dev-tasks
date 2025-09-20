from __future__ import annotations

import glob
import json
import sys
from pathlib import Path
from typing import Any

from src.schemas.eval import GoldCase
from src.schemas.settings import settings
from src.schemas.validation import ValidationConfig, ValidationResult

#!/usr/bin/env python3

sys.path.append(".")


def main() -> Any:
    """Main validation function with configurable settings."""
    # Get path from settings
    path: Any = settings.get_gold_cases_path()

    # Create validation config from settings
    config = ValidationConfig(
        strict_mode=settings.validation_strict,
        allow_missing_files=settings.allow_missing_files,
        unknown_tag_warning=settings.unknown_tag_warning,
        check_file_existence=settings.check_file_existence,
        known_tags=set(settings.known_tags),
    )

    # Load and validate cases
    result = validate_gold_cases_file(path, config)

    # Print results
    print(result.get_summary())

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  ❌ {error}")

    return 0 if result.is_valid else 1


def validate_gold_cases_file(path: Path, config: ValidationConfig) -> ValidationResult:
    """Validate all cases in a gold cases file."""
    result = ValidationResult(is_valid=True)

    if not path.exists():
        result.add_error(f"Gold cases file not found: {path}")
        return result

    raw = path.read_text(encoding="utf-8").splitlines()
    ids = set()

    for i, line in enumerate(raw, 1):
        if not line.strip():
            continue

        try:
            obj: Any = json.loads(line)
            case = GoldCase.model_validate(obj)  # validates + normalizes

            # Check for duplicate IDs
            if case.id in ids:
                result.duplicate_ids.append(case.id)
                result.add_error(f"Duplicate id at line {i}: {case.id}")
            ids.add(case.id)

            # Validate individual case
            case_result: Any = case.validate_case(config)
            result.cases_processed += 1

            if not case_result.is_valid:
                result.cases_failed += 1
                result.errors.extend(case_result.errors)

            result.warnings.extend(case_result.warnings)
            result.missing_files.extend(case_result.missing_files)
            result.unknown_tags.update(case_result.unknown_tags)

        except Exception as e:
            result.cases_failed += 1
            result.add_error(f"Line {i}: {e}")

    return result


if __name__ == "__main__":
    sys.exit(main())
