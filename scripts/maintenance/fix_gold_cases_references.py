from __future__ import annotations
import json
import os
import sys
from pathlib import Path
#!/usr/bin/env python3
"""
Fix Gold Cases File References

This script fixes the file references in gold cases based on our analysis:
1. Updates references to consolidated files
2. Fixes missing file references
3. Ensures all references point to existing files
"""

def load_gold_cases(file_path: str) -> list[dict]:
    """Load gold cases from JSONL file."""
    cases = []
    with open(file_path) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line.strip()))
    return cases

def save_gold_cases(cases: list[dict], file_path: str):
    """Save gold cases to JSONL file."""
    with open(file_path, "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")

def fix_gold_cases():
    """Fix file references in gold cases."""
    print("🔧 Fixing Gold Cases File References")
    print("=" * 80)

    # Load gold cases
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")
    print(f"📊 Loaded {len(cases)} gold cases")

    # Define fixes
    fixes = {
        # Consolidated files
        "400_guides/400_guide-index.md": "400_guides/400_00_memory-system-overview.md",
        # File path corrections
        "400_ai-constitution.md": "400_ai-constitution.md",  # Already correct
        # Update queries that reference old filenames
        "400_06_memory-and-context-systems.md": "400_02_memory-rehydration-context-management.md",
        "400_07_ai-frameworks-dspy.md": "400_09_ai-frameworks-dspy.md",
    }

    # Track changes
    changes_made = 0

    for i, case in enumerate(cases):
        case_id = case.get("id", f"Case_{i+1}")
        original_case = case.copy()

        # Fix expected_files
        if case.get("expected_files"):
            for j, file_path in enumerate(case["expected_files"]):
                if file_path in fixes:
                    old_path = file_path
                    new_path = fixes[file_path]
                    case["expected_files"][j] = new_path
                    print(f"  ✅ {case_id}: {old_path} → {new_path}")
                    changes_made += 1

        # Fix globs that reference old patterns
        if case.get("globs"):
            for j, glob_pattern in enumerate(case["globs"]):
                if "400_*dspy*.md" in glob_pattern:
                    # This is actually correct - it's a glob pattern
                    pass
                elif "400_*memory*.md" in glob_pattern:
                    # This is actually correct - it's a glob pattern
                    pass

        # Fix queries that reference old filenames
        query = case.get("query", "")
        if "400_06_memory-and-context-systems.md" in query:
            case["query"] = query.replace(
                "400_06_memory-and-context-systems.md", "400_02_memory-rehydration-context-management.md"
            )
            print(f"  ✅ {case_id}: Updated query reference")
            changes_made += 1
        elif "400_07_ai-frameworks-dspy.md" in query:
            case["query"] = query.replace("400_07_ai-frameworks-dspy.md", "400_09_ai-frameworks-dspy.md")
            print(f"  ✅ {case_id}: Updated query reference")
            changes_made += 1

        # Special case: Update the specific cases that reference the deleted guide-index
        if case_id in ["EVAL_GOLD_ADD_0009", "Give the high-level getting started index."]:
            if case.get("expected_files") and "400_guides/400_guide-index.md" in case["expected_files"]:
                case["expected_files"] = ["400_guides/400_00_memory-system-overview.md"]
                print(f"  ✅ {case_id}: Updated to reference consolidated file")
                changes_made += 1

    print(f"\n📊 Made {changes_made} changes")

    # Save updated cases
    backup_path = "evals/gold/v1/gold_cases.jsonl.backup"
    save_gold_cases(cases, backup_path)
    print(f"💾 Created backup: {backup_path}")

    save_gold_cases(cases, "evals/gold/v1/gold_cases.jsonl")
    print("💾 Updated: evals/gold/v1/gold_cases.jsonl")

    return cases

def validate_fixes(cases: list[dict]):
    """Validate that all fixes are correct."""
    print("\n🔍 Validating Fixes")
    print("=" * 40)

    missing_files = []

    for i, case in enumerate(cases):
        case_id = case.get("id", f"Case_{i+1}")
        expected_files = case.get("expected_files", [])

        if expected_files:
            for file_path in expected_files:
                if not os.path.exists(file_path):
                    missing_files.append(
                        {"case_id": case_id, "file_path": file_path, "query": case.get("query", "")[:60] + "..."}
                    )

    if missing_files:
        print(f"❌ Still missing {len(missing_files)} files:")
        for issue in missing_files:
            print(f"  - {issue['case_id']}: {issue['file_path']}")
    else:
        print("✅ All file references are now valid!")

    return len(missing_files) == 0

if __name__ == "__main__":
    # Fix the cases
    cases = fix_gold_cases()

    # Validate the fixes
    is_valid = validate_fixes(cases)

    if is_valid:
        print("\n🎉 All gold case file references have been fixed!")
    else:
        print("\n⚠️  Some issues remain - please review the missing files above")
        sys.exit(1)