#!/usr/bin/env python3
"""
Intelligently select existing tests based on context.

This script analyzes the context and automatically selects
the most appropriate existing tests to run.
"""

import subprocess
import sys
from typing import Dict, List


def analyze_context(context: str) -> Dict[str, float]:
    """Analyze context and return relevance scores for different test types."""

    # Define keywords and their relevance to test types
    test_keywords = {
        "performance": [
            "performance",
            "speed",
            "fast",
            "slow",
            "benchmark",
            "optimization",
            "efficiency",
            "response time",
            "throughput",
            "memory usage",
        ],
        "security": [
            "security",
            "vulnerability",
            "attack",
            "injection",
            "validation",
            "authentication",
            "authorization",
            "encryption",
            "safety",
        ],
        "workflow": [
            "workflow",
            "process",
            "automation",
            "pipeline",
            "orchestration",
            "integration",
            "end-to-end",
            "e2e",
            "system test",
        ],
        "unit": [
            "unit",
            "function",
            "method",
            "class",
            "component",
            "module",
            "individual",
            "isolated",
            "single",
            "basic",
        ],
        "code_quality": [
            "quality",
            "style",
            "linting",
            "formatting",
            "standards",
            "documentation",
            "coherence",
            "validation",
        ],
        "system_health": [
            "health",
            "status",
            "monitoring",
            "diagnostics",
            "check",
            "system",
            "infrastructure",
            "operational",
        ],
        "conflict_check": [
            "conflict",
            "merge",
            "duplicate",
            "consistency",
            "coherence",
            "validation",
            "check",
            "audit",
        ],
    }

    # Calculate relevance scores
    scores = {}
    context_lower = context.lower()

    for test_type, keywords in test_keywords.items():
        score = 0.0
        for keyword in keywords:
            if keyword in context_lower:
                score += 1.0
        scores[test_type] = score

    return scores

def select_tests_for_context(context: str, min_score: float = 0.5) -> List[str]:
    """Select appropriate existing tests based on context."""

    scores = analyze_context(context)

    # Filter tests above minimum score
    selected_tests = [test_type for test_type, score in scores.items() if score >= min_score]

    # Always include basic tests if no specific tests selected
    if not selected_tests:
        selected_tests = ["smoke", "code_quality"]

    # Sort by relevance score (highest first)
    selected_tests.sort(key=lambda x: scores.get(x, 0), reverse=True)

    return selected_tests

def get_test_command(test_type: str) -> List[str]:
    """Get the command for a specific test type."""

    test_mapping = {
        "smoke": ["./dspy-rag-system/run_tests.sh", "--tiers", "1", "--kinds", "smoke"],
        "unit": ["./dspy-rag-system/run_tests.sh", "--tiers", "1", "--kinds", "unit"],
        "integration": ["./dspy-rag-system/run_tests.sh", "--tiers", "1", "2", "--kinds", "integration"],
        "performance": [sys.executable, "scripts/performance_benchmark.py"],
        "security": [sys.executable, "scripts/security_enhancement.py"],
        "system_health": [sys.executable, "scripts/system_health_check.py"],
        "code_quality": [sys.executable, "-m", "ruff", "check", "."],
        "conflict_check": [sys.executable, "scripts/quick_conflict_check.py"],
        "doc_validation": [sys.executable, "scripts/doc_coherence_validator.py", "--check-all"],
    }

    return test_mapping.get(test_type, [])

def run_selected_tests(context: str, dry_run: bool = False) -> Dict[str, bool]:
    """Run tests selected for the given context."""

    selected_tests = select_tests_for_context(context)

    print(f"🧪 CONTEXT ANALYSIS: {context}")
    print(f"📋 SELECTED TESTS: {', '.join(selected_tests)}")

    if dry_run:
        print("\n🔍 DRY RUN - Commands that would be executed:")
        for test_type in selected_tests:
            command = get_test_command(test_type)
            print(f"  {test_type}: {' '.join(command)}")
        return {}

    results = {}

    for test_type in selected_tests:
        print(f"\n{'='*50}")
        print(f"🧪 Running: {test_type.upper()}")

        command = get_test_command(test_type)
        if not command:
            print(f"❌ No command found for test type: {test_type}")
            results[test_type] = False
            continue

        print(f"  Command: {' '.join(command)}")

        try:
            if test_type in ["smoke", "unit", "integration"]:
                # These need to run from dspy-rag-system directory
                result = subprocess.run(command, cwd="dspy-rag-system")
            else:
                result = subprocess.run(command)

            success = result.returncode == 0
            results[test_type] = success

            if success:
                print(f"  ✅ {test_type.upper()} passed")
            else:
                print(f"  ❌ {test_type.upper()} failed")

        except Exception as e:
            print(f"  ❌ {test_type.upper()} error: {e}")
            results[test_type] = False

    return results

def suggest_test_improvements(context: str) -> List[str]:
    """Suggest improvements based on context analysis."""

    scores = analyze_context(context)
    suggestions = []

    # Check for missing test coverage
    low_score_tests = [test_type for test_type, score in scores.items() if score < 0.5]

    if low_score_tests:
        suggestions.append(f"Consider adding tests for: {', '.join(low_score_tests)}")

    # Check for high-priority tests
    high_score_tests = [test_type for test_type, score in scores.items() if score >= 2.0]

    if high_score_tests:
        suggestions.append(f"High relevance detected for: {', '.join(high_score_tests)}")

    # Check for comprehensive testing
    if len(select_tests_for_context(context)) < 3:
        suggestions.append("Consider running comprehensive test suite for thorough validation")

    return suggestions

def main():
    """Main function for intelligent test selection."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/select_existing_tests.py <context> [--dry-run]")
        print("\nExamples:")
        print("  python scripts/select_existing_tests.py 'performance optimization'")
        print("  python scripts/select_existing_tests.py 'security validation' --dry-run")
        sys.exit(1)

    context = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    print("🧠 INTELLIGENT TEST SELECTION")
    print("=" * 50)

    # Run selected tests
    results = run_selected_tests(context, dry_run)

    if not dry_run and results:
        # Summary
        print(f"\n{'='*50}")
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 50)

        passed = sum(1 for success in results.values() if success)
        total = len(results)

        for test_type, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {test_type.upper()}: {status}")

        print(f"\n  Results: {passed}/{total} tests passed")

        # Suggestions
        suggestions = suggest_test_improvements(context)
        if suggestions:
            print("\n💡 SUGGESTIONS:")
            for suggestion in suggestions:
                print(f"  - {suggestion}")

    # Exit with appropriate code
    if dry_run:
        sys.exit(0)
    elif results and all(results.values()):
        print("🎉 All selected tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed - review required")
        sys.exit(1)

if __name__ == "__main__":
    main()
