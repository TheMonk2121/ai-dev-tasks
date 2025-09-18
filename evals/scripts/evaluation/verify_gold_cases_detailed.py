from __future__ import annotations
import json
import os
import sys
from pathlib import Path
#!/usr/bin/env python3
"""
Detailed Gold Cases Verification - Question by Question

This script verifies each gold case question in groups of 10 to ensure:
1. Questions are clear and accurate
2. Expected files actually exist and are relevant
3. Queries match the expected files
4. File references are appropriate for the question
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

def read_file_preview(file_path: str, lines: int = 10) -> str:
    """Read first few lines of a file for context."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines_content = content.split("\n")[:lines]
            return "\n".join(lines_content)
    except Exception as e:
        return f"Error reading file: {e}"

def verify_case_group(cases: list[dict], start_idx: int, end_idx: int) -> list[dict]:
    """Verify a group of cases (10 at a time)."""
    print(f"\n{'='*80}")
    print(f"🔍 VERIFYING CASES {start_idx+1}-{end_idx} ({end_idx-start_idx} cases)")
    print(f"{'='*80}")

    issues = []

    for i in range(start_idx, min(end_idx, len(cases))):
        case = cases[i]
        case_id = result.get("key", "")
        mode = result.get("key", "")
        query = result.get("key", "")
        expected_files = result.get("key", "")
        globs = result.get("key", "")
        tags = result.get("key", "")

        print(f"\n📋 Case {i+1}: {case_id}")
        print(f"   Mode: {mode}")
        print(f"   Query: {query}")
        print(f"   Tags: {tags}")

        # Check expected files
        if expected_files:
            print(f"   Expected Files: {expected_files}")
            for file_path in expected_files:
                if check_file_exists(file_path):
                    print(f"   ✅ {file_path} - EXISTS")
                    # Read preview to check relevance
                    preview = read_file_preview(file_path, 5)
                    if any(keyword in preview.lower() for keyword in query.lower().split()):
                        print("      📄 Content appears relevant to query")
                    else:
                        print("      ⚠️  Content may not be directly relevant to query")
                else:
                    print(f"   ❌ {file_path} - MISSING")
                    issues.append({"case_id": case_id, "issue": "missing_file", "file_path": file_path, "query": query})

        # Check globs
        if globs:
            print(f"   Glob Patterns: {globs}")
            for glob_pattern in globs:
                print(f"   🔍 {glob_pattern} - Pattern (not validated)")

        # Check query quality
        if len(query) < 10:
            print(f"   ⚠️  Query seems too short: '{query}'")
            issues.append({"case_id": case_id, "issue": "short_query", "query": query})

        # Check for typos or unclear language
        unclear_indicators = ["what give", "what show", "what point", "what is the main purpose of"]
        if any(indicator in query.lower() for indicator in unclear_indicators):
            print(f"   ⚠️  Query may have unclear phrasing: '{query}'")
            issues.append({"case_id": case_id, "issue": "unclear_phrasing", "query": query})

    return issues

def verify_all_cases():
    """Verify all gold cases in groups of 10."""
    print("🔍 Detailed Gold Cases Verification")
    print("=" * 80)

    # Load gold cases
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")
    print(f"📊 Loaded {len(cases)} gold cases")

    all_issues = []

    # Process in groups of 10
    group_size = 10
    for start_idx in range(0, len(cases), group_size):
        end_idx = min(start_idx + group_size, len(cases))
        group_issues = verify_case_group(cases, start_idx, end_idx)
        all_issues.extend(group_issues)

        # Pause between groups for review
        if end_idx < len(cases):
            input(f"\n⏸️  Press Enter to continue to next group ({end_idx+1}-{min(end_idx+group_size, len(cases))})...")

    # Summary
    print(f"\n{'='*80}")
    print("📋 VERIFICATION SUMMARY")
    print(f"{'='*80}")

    if all_issues:
        print(f"❌ Found {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"  - {result.get("key", "")
            if result.get("key", "")
                print(f"    Missing: {result.get("key", "")
            elif result.get("key", "")
                print(f"    Query: {result.get("key", "")
    else:
        print("✅ No issues found!")

    return all_issues

if __name__ == "__main__":
    issues = verify_all_cases()

    # Save results
    with open("gold_cases_detailed_verification.json", "w") as f:
        json.dump(issues, f, indent=2)

    print("\n💾 Detailed verification results saved to gold_cases_detailed_verification.json")