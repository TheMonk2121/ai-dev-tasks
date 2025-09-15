from __future__ import annotations
import json
import sys
from pathlib import Path
#!/usr/bin/env python3
"""
RAGChecker Baseline Metrics Guard

This script enforces the RED LINE baseline requirements for RAGChecker performance.
It must be run after each evaluation to ensure compliance before development can proceed.

Usage:
    python3 scripts/metrics_guard.py metrics/baseline_evaluations/latest_evaluation.json
"""

def check_baseline_compliance(results_file: str) -> bool:
    """
    Check if evaluation results meet the RED LINE baseline requirements.

    Args:
        results_file: Path to the evaluation results JSON file

    Returns:
        True if all baseline requirements are met, False otherwise
    """
    try:
        with open(results_file) as f:
            results = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: Results file not found: {results_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in results file: {e}")
        return False

    # Extract overall metrics
    overall_metrics = results.get("overall_metrics", {})
    if not overall_metrics:
        print("❌ ERROR: No overall_metrics found in results file")
        return False

    print(f"🔍 Checking baseline compliance for: {results_file}")
    print(f"📊 Evaluation Type: {results.get('evaluation_type', 'unknown')}")
    print(f"📈 Total Cases: {results.get('total_cases', 'unknown')}")
    print()

    # Define baseline requirements based on judge mode
    judge_mode = results.get("judge_mode", "sonnet")
    if judge_mode == "haiku":
        # Interim Haiku floors (more conservative judge)
        baseline_requirements = {"precision": 0.135, "recall": 0.16, "f1_score": 0.145, "faithfulness": 0.60}
    else:
        # Legacy Sonnet floors
        baseline_requirements = {"precision": 0.20, "recall": 0.45, "f1_score": 0.22, "faithfulness": 0.60}

    # Check each metric
    all_passed = True
    for metric, target in baseline_requirements.items():
        current_value = overall_metrics.get(metric, 0.0)

        if current_value >= target:
            print(f"✅ PASS: {metric}={current_value:.3f} ≥ {target:.3f}")
        else:
            print(f"❌ RED LINE FAIL: {metric}={current_value:.3f} < {target:.3f}")
            all_passed = False

    # Additional comprehensive metrics (informational)
    print()
    print("📋 Additional Metrics (Informational):")
    comp_metrics = [
        "context_precision",
        "context_utilization",
        "noise_sensitivity",
        "hallucination_rate",
        "self_knowledge",
        "claim_recall",
    ]

    for metric in comp_metrics:
        if metric in overall_metrics:
            value = overall_metrics[metric]
            print(f"   {metric}: {value:.3f}")

    # Summary
    print()
    if all_passed:
        print("🎉 ALL BASELINE REQUIREMENTS MET!")
        print("✅ Development can proceed")
        return True
    else:
        print("🚨 BASELINE REQUIREMENTS NOT MET!")
        print("❌ Development is BLOCKED until all targets are achieved")
        print("📋 Focus areas:")

        # Identify specific areas needing improvement
        for metric, target in baseline_requirements.items():
            current_value = overall_metrics.get(metric, 0.0)
            if current_value < target:
                gap = target - current_value
                print(f"   • {metric}: Need +{gap:.3f} (current: {current_value:.3f}, target: {target:.3f})")

        return False

def main():
    """Main function to check baseline compliance."""
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/metrics_guard.py <results_file>")
        print("Example: python3 scripts/metrics_guard.py metrics/baseline_evaluations/latest_evaluation.json")
        sys.exit(1)

    results_file = sys.argv[1]

    # Check if file exists
    if not Path(results_file).exists():
        print(f"❌ ERROR: Results file not found: {results_file}")
        print("💡 Tip: Run RAGChecker evaluation first:")
        print("   export AWS_REGION=us-east-1")
        print("   python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli")
        sys.exit(1)

    # Check baseline compliance
    success = check_baseline_compliance(results_file)

    # Exit with appropriate code for CI
    if success:
        print("\n🎯 EXIT CODE: 0 (SUCCESS)")
        sys.exit(0)
    else:
        print("\n🚨 EXIT CODE: 2 (FAILURE)")
        sys.exit(2)

if __name__ == "__main__":
    main()