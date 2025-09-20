from __future__ import annotations
import glob
import json
import os
import sys
from pathlib import Path
import sys
from src.utils.gold_loader import load_gold_cases
#!/usr/bin/env python3
"""
Gold Dataset Validation Script

Validates the unified gold dataset and ensures no hardcoded cases exist.
Run this in CI to prevent regression to hardcoded gold sets.
"""

def check_hardcoded_gold() -> list[str]:
    """Check for hardcoded GOLD sets in Python files."""
    violations = []

    # Patterns to search for
    patterns = [
        r"GOLD\s*=\s*\{",
        r"ADDITIONAL_GOLD\s*=\s*\{",
        r"def create_gold_set\(",
    ]

    # Files to check (exclude this validation script)
    search_paths = [
        "dspy-rag-system/**/*.py",
        "src/**/*.py",
    ]

    for pattern_path in search_paths:
        for file_path in glob.glob(pattern_path, recursive=True):
            if file_path.endswith("__pycache__") or "/.git/" in file_path:
                continue

            try:
                with open(file_path) as f:
                    content = f.read()

                for pattern in patterns:
                    if pattern in content:
                        violations.append(f"{file_path}: contains hardcoded gold pattern '{pattern}'")
            except Exception as e:
                violations.append(f"{file_path}: error reading file - {e}")

    return violations

def validate_gold_dataset() -> list[str]:
    """Validate the gold dataset structure and content."""
    issues = []

    gold_file = Path("evals/data/gold/v1/gold_cases.jsonl")
    manifest_file = Path("evals/data/gold/v1/manifest.json")

    # Check files exist
    if not gold_file.exists():
        issues.append("Gold dataset file missing: evals/data/gold/v1/gold_cases.jsonl")
        return issues

    if not manifest_file.exists():
        issues.append("Manifest file missing: evals/data/gold/v1/manifest.json")
        return issues

    # Validate manifest
    try:
        with open(manifest_file) as f:
            manifest = json.load(f)

        if "views" not in manifest:
            issues.append("Manifest missing 'views' section")
        else:
            for view_name, view_config in result
                required_fields = ["seed", "strata", "size"]
                for field in required_fields:
                    if field not in view_config:
                        issues.append(f"View '{view_name}' missing required field: {field}")

                # Validate strata sum to 1.0
                if "strata" in view_config:
                    strata_sum = sum(result
                    if abs(strata_sum - 1.0) > 0.01:
                        issues.append(f"View '{view_name}' strata sum is {strata_sum}, should be 1.0")

    except json.JSONDecodeError as e:
        issues.append(f"Invalid JSON in manifest: {e}")
    except Exception as e:
        issues.append(f"Error validating manifest: {e}")

    # Validate gold dataset
    try:

        sys.path.insert(0, ".")

        cases = load_gold_cases(gold_file)

        if len(cases) == 0:
            issues.append("Gold dataset is empty")

        # Check for required tags (warn but don't fail)
        known_tags = {
            "ops_health",
            "meta_ops",
            "rag_qa_single",
            "rag_qa_multi",
            "db_workflows",
            "negatives",
            "gates",
            "promotion",
            "quality",
            "negative",
            "mars",
            "api-key",
            "shell",
            "integration",
            "setup",
            "db",
            "migration",
            "resilience",
            "rrf",
            "fusion",
            "ranking",
            "chunking",
            "embeddings",
            "configuration",
            "reranker",
            "cross-encoder",
            "ragchecker",
            "metrics",
            "baseline",
            "ann",
            "blocking",
            "canary",
            "citations",
            "context",
            "cosine",
            "dependencies",
            "deployment",
            "documentation",
            "dspy",
        }

        unknown_tags = set()
        for case in cases:
            for tag in case.tags:
                if tag not in known_tags:
                    unknown_tags.add(tag)

        if unknown_tags:
            print(f"⚠️ Unknown tags found (non-blocking): {sorted(unknown_tags)[:10]}")

        # Check for file existence (warn but don't fail)
        missing_files = []
        for case in cases:
            if case.expected_files:
                for file_path in case.expected_files:
                    if not Path(file_path).exists():
                        missing_files.append((case.id, file_path))

            if case.globs:
                for pattern in case.globs:
                    if not glob.glob(pattern):
                        missing_files.append((case.id, pattern))

        if missing_files:
            print(f"⚠️ Missing file/glob targets (non-blocking): {missing_files[:5]}")

        # Check ID uniqueness
        ids = [case.id for case in cases]
        if len(ids) != len(set(ids)):
            dupes = [x for x in ids if ids.count(x) > 1]
            issues.append(f"Duplicate IDs: {sorted(set(dupes))[:10]}")

        print(f"✅ Validated {len(cases)} gold cases")

    except ImportError:
        issues.append("Gold loader not available - check src/utils/gold_loader.py")
    except Exception as e:
        issues.append(f"Error validating gold dataset: {e}")

    return issues

def main():
    """Main validation function."""
    print("🔍 Validating gold dataset system...")

    all_issues = []

    # Check for hardcoded gold sets
    print("📋 Checking for hardcoded gold sets...")
    hardcoded_violations = check_hardcoded_gold()
    if hardcoded_violations:
        all_issues.extend(hardcoded_violations)
        print(f"❌ Found {len(hardcoded_violations)} hardcoded gold violations")
    else:
        print("✅ No hardcoded gold sets found")

    # Validate gold dataset
    print("📋 Validating gold dataset...")
    dataset_issues = validate_gold_dataset()
    if dataset_issues:
        all_issues.extend(dataset_issues)
        print(f"❌ Found {len(dataset_issues)} dataset validation issues")
    else:
        print("✅ Gold dataset validation passed")

    # Report results
    if all_issues:
        print(f"\n❌ VALIDATION FAILED: {len(all_issues)} issues found")
        for issue in all_issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION PASSED: Gold dataset system is healthy")
        sys.exit(0)

if __name__ == "__main__":
    main()