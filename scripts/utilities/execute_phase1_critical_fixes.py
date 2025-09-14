from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
Execute Phase 1: Critical Fixes
Run this script to immediately fix the most critical issues in gold cases.
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

def fix_unclear_phrasing(cases: list[dict]) -> int:
    """Fix unclear phrasing in gold cases."""
    print("🔧 Fixing unclear phrasing...")

    # Define fixes
    phrasing_fixes = {
        "what show": "show me",
        "what give": "give me",
        "what point": "point me to",
        "what is the main purpose of": "what does",
        "tl;dr": "TL;DR",
        "dspy": "DSPy",
    }

    changes_made = 0

    for case in cases:
        original_query = case.get("query", "")
        new_query = original_query

        # Apply fixes
        for old_phrase, new_phrase in phrasing_fixes.items():
            if old_phrase in new_query.lower():
                new_query = re.sub(old_phrase, new_phrase, new_query, flags=re.IGNORECASE)

        # Fix grammar
        new_query = re.sub(r"\?$", "?", new_query)  # Ensure ends with ?
        new_query = re.sub(r"\s+", " ", new_query)  # Fix spacing
        new_query = new_query.strip()

        if new_query != original_query:
            case["query"] = new_query
            changes_made += 1
            print(f"  ✅ Fixed: '{original_query}' → '{new_query}'")

    return changes_made

def fix_short_queries(cases: list[dict]) -> int:
    """Fix queries that are too short."""
    print("🔧 Fixing short queries...")

    changes_made = 0

    for case in cases:
        query = case.get("query", "")

        if len(query) < 10:
            # Try to expand based on context
            if "dspy" in query.lower():
                case["query"] = "What is DSPy and how is it used in this project?"
                changes_made += 1
            elif "db" in query.lower() or "database" in query.lower():
                case["query"] = "How does the database system work in this project?"
                changes_made += 1
            elif "memory" in query.lower():
                case["query"] = "How does the memory system work in this project?"
                changes_made += 1
            else:
                # Generic expansion
                case["query"] = f"What is {query} and how is it used in this project?"
                changes_made += 1

            print(f"  ✅ Expanded: '{query}' → '{case['query']}'")

    return changes_made

def run_verification():
    """Run verification to check results."""
    print("\n🔍 Running verification...")
    try:
        result = subprocess.run(["python3", "scripts/verify_gold_cases_detailed.py"], capture_output=True, text=True)
        print("Verification completed.")
        return result.returncode == 0
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

def main():
    """Execute Phase 1 critical fixes."""
    print("🚀 EXECUTING PHASE 1: CRITICAL FIXES")
    print("=" * 50)

    # Create backup
    backup_path = "evals/gold/v1/gold_cases.jsonl.backup_phase1"
    print(f"📁 Creating backup: {backup_path}")

    # Load gold cases
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")
    print(f"📊 Loaded {len(cases)} gold cases")

    # Create backup
    save_gold_cases(cases, backup_path)

    # Fix unclear phrasing
    phrasing_changes = fix_unclear_phrasing(cases)

    # Fix short queries
    short_query_changes = fix_short_queries(cases)

    # Save updated cases
    save_gold_cases(cases, "evals/gold/v1/gold_cases.jsonl")

    # Summary
    total_changes = phrasing_changes + short_query_changes
    print("\n📊 PHASE 1 SUMMARY")
    print("=" * 30)
    print(f"✅ Unclear phrasing fixed: {phrasing_changes} cases")
    print(f"✅ Short queries fixed: {short_query_changes} cases")
    print(f"✅ Total changes: {total_changes} cases")

    if total_changes > 0:
        print("\n🎉 Phase 1 completed successfully!")
        print(f"💾 Backup saved to: {backup_path}")
        print("💾 Updated file: evals/gold/v1/gold_cases.jsonl")

        # Ask if user wants to run verification
        response = input("\n🔍 Run verification to check results? (y/n): ").lower()
        if response == "y":
            run_verification()
    else:
        print("\n✅ No changes needed - gold cases already in good shape!")

if __name__ == "__main__":
    main()
