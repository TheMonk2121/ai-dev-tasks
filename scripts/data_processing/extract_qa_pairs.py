from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional, Union

from src.schemas.eval import GoldCase, Mode
from src.utils.gold_loader import load_gold_cases

#!/usr/bin/env python3
"""
Extract Q&A pairs from gold test cases with file locations
"""

# Add project root to path
sys.path.insert(0, ".")

def extract_qa_pairs():
    """Extract all Q&A pairs with file locations."""
    print("🔍 Extracting Q&A pairs from gold test cases...")
    print("=" * 80)

    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")

    # Group by mode
    retrieval_cases = []
    reader_cases = []
    decision_cases = []

    for case in cases:
        if case.mode == Mode.retrieval:
            retrieval_cases.append(case)
        elif case.mode == Mode.reader:
            reader_cases.append(case)
        elif case.mode == Mode.decision:
            decision_cases.append(case)

    print(f"📊 Found {len(cases)} total cases:")
    print(f"  - Retrieval: {len(retrieval_cases)}")
    print(f"  - Reader: {len(reader_cases)}")
    print(f"  - Decision: {len(decision_cases)}")
    print()

    # Extract retrieval cases (questions with expected files)
    print("🔍 RETRIEVAL MODE CASES")
    print("=" * 80)
    for i, case in enumerate(retrieval_cases, 1):
        print(f"{i:3d}. ID: {case.id}")
        print(f"     Question: {case.query}")

        if case.expected_files:
            print(f"     Expected Files: {', '.join(case.expected_files)}")
        if case.globs:
            print(f"     Glob Patterns: {', '.join(case.globs)}")
        if case.tags:
            print(f"     Tags: {', '.join(case.tags)}")
        print()

    # Extract reader cases (questions with ground truth answers)
    print("💬 READER MODE CASES")
    print("=" * 80)
    for i, case in enumerate(reader_cases, 1):
        print(f"{i:3d}. ID: {case.id}")
        print(f"     Question: {case.query}")
        print(f"     Answer: {case.gt_answer}")

        if case.expected_files:
            print(f"     Expected Files: {', '.join(case.expected_files)}")
        if case.globs:
            print(f"     Glob Patterns: {', '.join(case.globs)}")
        if case.tags:
            print(f"     Tags: {', '.join(case.tags)}")
        print()

    # Extract decision cases (questions with expected decisions)
    print("🎯 DECISION MODE CASES")
    print("=" * 80)
    for i, case in enumerate(decision_cases, 1):
        print(f"{i:3d}. ID: {case.id}")
        print(f"     Question: {case.query}")
        print(f"     Expected Decisions: {', '.join(case.expected_decisions) if case.expected_decisions else 'None'}")

        if case.expected_files:
            print(f"     Expected Files: {', '.join(case.expected_files)}")
        if case.globs:
            print(f"     Glob Patterns: {', '.join(case.globs)}")
        if case.tags:
            print(f"     Tags: {', '.join(case.tags)}")
        print()

    # Summary statistics
    print("📊 SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total Questions: {len(cases)}")
    print(f"Questions with Answers: {len(reader_cases)}")
    print(f"Questions with Expected Files: {len([c for c in cases if c.expected_files])}")
    print(f"Questions with Glob Patterns: {len([c for c in cases if c.globs])}")
    print(f"Questions with Expected Decisions: {len(decision_cases)}")

    # File coverage analysis
    all_files = set()
    for case in cases:
        if case.expected_files:
            all_files.update(case.expected_files)

    print("\n📁 FILE COVERAGE")
    print("=" * 80)
    print(f"Total Unique Files Referenced: {len(all_files)}")
    print("Files by directory:")

    dir_counts = {}
    for file_path in all_files:
        dir_name = file_path.split("/")[0] if "/" in file_path else "root"
        dir_counts[dir_name] = dir_counts.get(dir_name, 0) + 1

    for dir_name, count in sorted(dir_counts.items()):
        print(f"  {dir_name}: {count} files")

    return cases

def main():
    """Main function."""
    cases = extract_qa_pairs()
    print(f"\n✅ Extraction complete! Processed {len(cases)} cases.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
