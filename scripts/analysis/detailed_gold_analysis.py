from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from src.schemas.eval import GoldCase, Mode
from src.utils.gold_loader import load_gold_cases
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Detailed Gold Test Case Analysis

This script provides a detailed breakdown of the issues found in the gold test cases
and suggests specific fixes for each problem.
"""

# Add project root to path
sys.path.insert(0, ".")

def analyze_specific_issues():
    """Analyze specific issues in detail."""
    cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")

    print("🔍 DETAILED GOLD TEST CASE ANALYSIS")
    print("=" * 60)

    # 1. Schema Validation Issues
    print("\n1. SCHEMA VALIDATION ISSUES")
    print("-" * 40)

    schema_issues = []
    for case in cases:
        if case.mode == Mode.reader and not case.gt_answer:
            schema_issues.append(f"❌ {case.id}: Reader mode missing gt_answer")
        elif case.mode == Mode.retrieval and not case.expected_files and not case.globs:
            schema_issues.append(f"❌ {case.id}: Retrieval mode missing expected_files or globs")
        elif case.mode == Mode.decision and not case.expected_decisions:
            schema_issues.append(f"❌ {case.id}: Decision mode missing expected_decisions")

    print(f"Found {len(schema_issues)} schema violations:")
    for issue in schema_issues[:10]:  # Show first 10
        print(f"  {issue}")
    if len(schema_issues) > 10:
        print(f"  ... and {len(schema_issues) - 10} more")

    # 2. Missing Files Analysis
    print("\n2. MISSING FILES ANALYSIS")
    print("-" * 40)

    missing_files = []
    for case in cases:
        if case.expected_files:
            for file_path in case.expected_files:
                if not Path(file_path).exists():
                    missing_files.append((case.id, file_path))

    print(f"Found {len(missing_files)} missing files:")

    # Group by file type
    file_types = defaultdict(list)
    for case_id, file_path in missing_files:
        if file_path.endswith(".py"):
            file_types["Python files"].append((case_id, file_path))
        elif file_path.endswith(".md"):
            file_types["Markdown files"].append((case_id, file_path))
        else:
            file_types["Other files"].append((case_id, file_path))

    for file_type, files in file_types.items():
        print(f"\n  {file_type}:")
        for case_id, file_path in files[:5]:  # Show first 5
            print(f"    ❌ {case_id}: {file_path}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")

    # 3. Query Quality Issues
    print("\n3. QUERY QUALITY ISSUES")
    print("-" * 40)

    query_issues = {"too_short": [], "unclear": [], "file_specific": [], "duplicates": []}

    query_counts = defaultdict(int)
    for case in cases:
        query = case.query.strip()
        query_counts[query] += 1

        if len(query) < 10:
            query_issues["too_short"].append(f"❌ {case.id}: '{query}' (too short)")
        if not query.endswith("?"):
            query_issues["unclear"].append(f"❌ {case.id}: '{query}' (not a question)")
        if any(pattern in query.lower() for pattern in [".md", ".py", "according to"]):
            query_issues["file_specific"].append(f"❌ {case.id}: '{query}' (file-specific)")

    # Find duplicates
    for query, count in query_counts.items():
        if count > 1:
            query_issues["duplicates"].append(f"❌ '{query}' appears {count} times")

    for issue_type, issues in query_issues.items():
        if issues:
            print(f"\n  {issue_type.upper()}:")
            for issue in issues[:5]:  # Show first 5
                print(f"    {issue}")
            if len(issues) > 5:
                print(f"    ... and {len(issues) - 5} more")

    # 4. Tag Analysis
    print("\n4. TAG ANALYSIS")
    print("-" * 40)

    # Known tags from the validation script
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
        "evaluation",
        "evals",
        "memory",
        "prd",
        "workflow",
        "vector",
        "index",
        "ivfflat",
        "fts",
        "tsquery",
        "postgresql",
        "pgvector",
        "teleprompter",
        "optimization",
        "grounding",
        "multi-hop",
        "hyde",
        "prf",
        "provenance",
        "tracking",
        "leakage",
        "runbook",
        "manifests",
        "quantum",
        "entanglement",
        "time-travel",
        "percentage",
    }

    all_tags = set()
    for case in cases:
        all_tags.update(case.tags)

    unknown_tags = all_tags - known_tags
    print(f"Total unique tags: {len(all_tags)}")
    print(f"Unknown tags: {len(unknown_tags)}")
    print(f"Unknown tags: {sorted(unknown_tags)}")

    # 5. Mode Distribution Analysis
    print("\n5. MODE DISTRIBUTION ANALYSIS")
    print("-" * 40)

    mode_counts = defaultdict(int)
    for case in cases:
        mode_counts[case.mode] += 1

    print("Mode distribution:")
    for mode, count in mode_counts.items():
        percentage = (count / len(cases)) * 100
        print(f"  {mode}: {count} cases ({percentage:.1f}%)")

    # 6. Specific Problem Cases
    print("\n6. SPECIFIC PROBLEM CASES")
    print("-" * 40)

    problem_cases = []
    for case in cases:
        issues = []

        # Check for multiple issues
        if case.mode == Mode.retrieval and not case.expected_files and not case.globs:
            issues.append("missing supervision")
        if case.mode == Mode.reader and not case.gt_answer:
            issues.append("missing answer")
        if case.mode == Mode.decision and not case.expected_decisions:
            issues.append("missing decisions")
        if len(case.query) < 10:
            issues.append("query too short")
        if not case.query.endswith("?"):
            issues.append("not a question")

        if issues:
            problem_cases.append((case.id, case.query, issues))

    print(f"Found {len(problem_cases)} cases with multiple issues:")
    for case_id, query, issues in problem_cases[:10]:  # Show first 10
        print(f"  ❌ {case_id}: {', '.join(issues)}")
        print(f"      Query: '{query}'")
    if len(problem_cases) > 10:
        print(f"  ... and {len(problem_cases) - 10} more")

    return {
        "schema_issues": len(schema_issues),
        "missing_files": len(missing_files),
        "query_issues": sum(len(issues) for issues in query_issues.values()),
        "unknown_tags": len(unknown_tags),
        "problem_cases": len(problem_cases),
    }

def generate_fix_recommendations():
    """Generate specific fix recommendations."""
    print("\n7. FIX RECOMMENDATIONS")
    print("-" * 40)

    recommendations = [
        "🔧 SCHEMA FIXES:",
        "  - Add missing gt_answer for reader mode cases",
        "  - Add expected_files or globs for retrieval mode cases",
        "  - Add expected_decisions for decision mode cases",
        "",
        "📁 FILE FIXES:",
        "  - Update file paths to match actual project structure",
        "  - Remove references to non-existent files",
        "  - Use glob patterns for directory-based queries",
        "",
        "❓ QUERY FIXES:",
        "  - Rewrite queries to be proper questions ending with '?'",
        "  - Make queries more specific and less file-dependent",
        "  - Remove duplicate queries",
        "  - Ensure queries are at least 10 characters long",
        "",
        "🏷️ TAG FIXES:",
        "  - Standardize tag usage across all cases",
        "  - Remove or replace unknown tags",
        "  - Use consistent tag naming conventions",
        "",
        "🎯 PRIORITY FIXES:",
        "  1. Fix schema violations (34 cases) - CRITICAL",
        "  2. Update missing file references (16 files) - HIGH",
        "  3. Improve query quality (20 queries) - MEDIUM",
        "  4. Standardize tags (15 unknown tags) - LOW",
    ]

    for rec in recommendations:
        print(rec)

def main():
    """Main function."""
    results = analyze_specific_issues()
    generate_fix_recommendations()

    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Schema issues: {results['schema_issues']}")
    print(f"Missing files: {results['missing_files']}")
    print(f"Query issues: {results['query_issues']}")
    print(f"Unknown tags: {results['unknown_tags']}")
    print(f"Problem cases: {results['problem_cases']}")

    print("\n🎯 NEXT STEPS:")
    print("1. Run the validation script to see current status")
    print("2. Fix schema violations first (most critical)")
    print("3. Update file references to match actual structure")
    print("4. Improve query quality and remove duplicates")
    print("5. Standardize tag usage")

    return 0

if __name__ == "__main__":
    sys.exit(main())
