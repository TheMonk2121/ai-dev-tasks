from __future__ import annotations
import json
import os
import sys
from pathlib import Path
#!/usr/bin/env python3
"""
Analyze Gold Cases for File Reference Accuracy

This script analyzes the gold test cases to identify:
1. Missing files referenced in expected_files
2. Incorrect file paths
3. Files that have been moved or renamed
4. Directory structure changes
"""

def load_gold_cases(file_path: str) -> list[dict]:
    """Load gold cases from JSONL file."""
    cases = []
    with open(file_path) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line.strip()))
    return cases

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return os.path.exists(file_path)

def find_actual_files(directory: str, pattern: str = "*.md") -> set[str]:
    """Find all files matching pattern in directory."""
    files = set()
    if os.path.exists(directory):
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(".md"):
                    rel_path = os.path.relpath(os.path.join(root, filename), ".")
                    files.add(rel_path)
    return files

def analyze_gold_cases():
    """Analyze gold cases for accuracy issues."""
    print("🔍 Analyzing Gold Cases for File Reference Accuracy")
    print("=" * 80)

    # Load gold cases
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")
    print(f"📊 Loaded {len(cases)} gold cases")

    # Track issues
    issues: dict[str, list] = {"missing_files": [], "incorrect_paths": [], "moved_files": [], "directory_changes": []}

    # Get all actual files in the project
    all_files = set()
    for directory in [
        "400_guides",
        "000_core",
        "100_memory",
        "200_setup",
        "500_research",
        "300_experiments",
        "templates",
        "scripts",
        "src",
    ]:
        all_files.update(find_actual_files(directory))

    # Also check root directory
    for root, dirs, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".md") and not any(
                skip in root for skip in ["node_modules", ".git", "__pycache__", "600_archives"]
            ):
                rel_path = os.path.relpath(os.path.join(root, filename), ".")
                all_files.add(rel_path)

    print(f"📁 Found {len(all_files)} actual files in project")

    # Analyze each case
    for i, case in enumerate(cases, 1):
        case_id = case.get("id", f"Case_{i}")
        expected_files = case.get("expected_files", [])
        globs = case.get("globs", [])

        print(f"\n🔍 Analyzing Case {i}: {case_id}")

        # Check expected_files
        if expected_files:
            for file_path in expected_files:
                if not check_file_exists(file_path):
                    issues["missing_files"].append(
                        {
                            "case_id": case_id,
                            "file_path": file_path,
                            "query": case.get("query", ""),
                            "mode": case.get("mode", ""),
                        }
                    )
                    print(f"  ❌ Missing file: {file_path}")

                    # Try to find similar files
                    filename = os.path.basename(file_path)
                    similar_files = [f for f in all_files if filename in f]
                    if similar_files:
                        print(f"     💡 Similar files found: {similar_files[:3]}")
                else:
                    print(f"  ✅ File exists: {file_path}")

        # Check globs (simplified check)
        if globs:
            for glob_pattern in globs:
                print(f"  🔍 Glob pattern: {glob_pattern}")

    # Summary
    print("\n" + "=" * 80)
    print("📋 SUMMARY OF ISSUES")
    print("=" * 80)

    print(f"\n❌ Missing Files: {len(issues['missing_files'])}")
    for issue in issues["missing_files"]:
        print(f"  - {issue['case_id']}: {issue['file_path']}")
        print(f"    Query: {issue['query'][:60]}...")

    # Specific known issues from our consolidation
    print("\n🔧 KNOWN ISSUES FROM CONSOLIDATION:")
    print("  - 400_guides/400_guide-index.md → Merged into 400_00_memory-system-overview.md")
    print("  - 400_ai-constitution.md → Exists in root directory")
    print("  - Some files may have been moved to 600_archives/")

    return issues

if __name__ == "__main__":
    issues = analyze_gold_cases()

    # Save results
    with open("gold_cases_analysis_results.json", "w") as f:
        json.dump(issues, f, indent=2)

    print("\n💾 Results saved to gold_cases_analysis_results.json")