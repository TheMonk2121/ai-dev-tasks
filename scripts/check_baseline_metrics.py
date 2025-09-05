#!/usr/bin/env python3
"""
Baseline Metrics Pre-commit Check

This script validates that your RAG system is meeting baseline performance metrics.
It warns if metrics are below targets but doesn't block commits (yet).
Once you reach the baseline, this will become a hard gate.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Baseline targets (from NEW_BASELINE_MILESTONE_2025.md)
BASELINE_TARGETS = {
    "recall_at_20": 0.65,
    "precision_at_k": 0.20,
    "faithfulness": 0.60,
    "p50_e2e": 2.0,
    "p95_e2e": 4.0,
}

# Current status (will be updated when you reach baseline)
CURRENT_STATUS = "DEVELOPMENT_PHASE"  # Will become "PRODUCTION_READY" when baseline is hit


def find_latest_evaluation() -> Optional[Path]:
    """Find the latest RAGChecker evaluation file."""
    metrics_dir = Path("metrics/baseline_evaluations")
    if not metrics_dir.exists():
        return None

    # Look for the most recent evaluation file
    eval_files = list(metrics_dir.glob("ragchecker_official_evaluation_*.json"))
    if not eval_files:
        return None

    # Sort by modification time and get the latest
    latest_file = max(eval_files, key=lambda f: f.stat().st_mtime)
    return latest_file


def parse_evaluation_file(file_path: Path) -> Dict:
    """Parse the evaluation file and extract metrics."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"⚠️  Warning: Could not parse evaluation file {file_path}: {e}")
        return {}


def extract_metrics(data: Dict) -> Dict[str, float]:
    """Extract relevant metrics from evaluation data."""
    metrics = {}

    # Extract overall metrics
    if "overall_metrics" in data:
        overall = data["overall_metrics"]
        metrics["precision_at_k"] = overall.get("precision", 0.0)
        metrics["recall_at_20"] = overall.get("recall", 0.0)

        # If we have case results, calculate faithfulness from comprehensive metrics
        if "case_results" in data and data["case_results"]:
            faithfulness_scores = []
            for case in data["case_results"]:
                if "comprehensive_metrics" in case:
                    comp_metrics = case["comprehensive_metrics"]
                    if "faithfulness" in comp_metrics:
                        faithfulness_scores.append(comp_metrics["faithfulness"])

            if faithfulness_scores:
                metrics["faithfulness"] = sum(faithfulness_scores) / len(faithfulness_scores)

    # For now, we don't have latency metrics, so we'll use placeholders
    metrics["p50_e2e"] = None  # Not measured yet
    metrics["p95_e2e"] = None  # Not measured yet

    return metrics


def find_latest_baseline_metrics() -> Optional[Path]:
    """Find the latest baseline metrics file."""
    metrics_dir = Path("metrics/baseline_evaluations")
    if not metrics_dir.exists():
        return None

    # Look for baseline metrics files
    metrics_files = list(metrics_dir.glob("baseline_metrics_*.json"))
    if not metrics_files:
        return None

    # Sort by modification time and get the latest
    latest_file = max(metrics_files, key=lambda f: f.stat().st_mtime)
    return latest_file


def extract_baseline_metrics(data: Dict) -> Dict[str, float]:
    """Extract metrics from baseline metrics file."""
    metrics = {}

    # Extract latency metrics
    if "latency" in data:
        latency = data["latency"]
        metrics["p50_e2e"] = latency.get("p50_ms", 0.0) / 1000.0  # Convert to seconds
        metrics["p95_e2e"] = latency.get("p95_ms", 0.0) / 1000.0  # Convert to seconds

    # Extract reranker metrics
    if "reranker" in data:
        reranker = data["reranker"]
        metrics["reranker_lift"] = reranker.get("reranker_lift", 0.0)

    # Extract health metrics
    if "health" in data:
        health = data["health"]
        metrics["system_health"] = 1.0 if health.get("database_connection", False) else 0.0

    return metrics


def check_baseline_compliance(metrics: Dict[str, float]) -> Tuple[bool, List[str]]:
    """Check if metrics meet baseline targets."""
    violations = []

    for metric_name, target in BASELINE_TARGETS.items():
        current_value = metrics.get(metric_name)

        if current_value is None:
            continue

        # Check if metric meets target
        if metric_name.startswith("p") and metric_name.endswith("_e2e"):
            # Latency metrics: lower is better
            if current_value > target:
                violations.append(f"{metric_name}: {current_value:.3f} > {target:.3f}")
        else:
            # Quality metrics: higher is better
            if current_value < target:
                violations.append(f"{metric_name}: {current_value:.3f} < {target:.3f}")

    return len(violations) == 0, violations


def print_status(metrics: Dict[str, float], violations: List[str], file_path: Optional[Path]):
    """Print the current status and any violations."""
    print("🔍 Baseline Metrics Pre-commit Check")
    print("=" * 50)

    if file_path:
        print(f"📊 Latest Evaluation: {file_path.name}")
    else:
        print("⚠️  No evaluation files found")

    print(f"🎯 Current Status: {CURRENT_STATUS}")
    print()

    # Print current metrics vs targets
    print("📈 Current Metrics vs Targets:")
    for metric_name, target in BASELINE_TARGETS.items():
        current_value = metrics.get(metric_name)
        if current_value is not None:
            status = "✅" if current_value >= target else "❌"
            print(f"   {status} {metric_name}: {current_value:.3f} (target: {target:.3f})")
        else:
            print(f"   ❓ {metric_name}: Not measured (target: {target:.3f})")

    print()

    if violations:
        print("🚨 Baseline Violations Detected:")
        for violation in violations:
            print(f"   ❌ {violation}")
        print()
        print("⚠️  WARNING: Your system is below baseline targets!")
        print("   This will become a hard gate once you reach production-ready status.")
        print("   Focus on improving these metrics before adding new features.")
        print()
        print("💡 Recommendation: Run baseline evaluation and focus on performance improvements.")
        return False
    else:
        if CURRENT_STATUS == "DEVELOPMENT_PHASE":
            print("✅ All measured metrics are above baseline targets!")
            print("🎯 You're on track to reach production-ready status.")
            print("💡 Continue improving until you hit all baseline targets.")
        else:
            print("🎉 CONGRATULATIONS! All baseline metrics are met!")
            print("🚨 This is now a HARD GATE - no commits below baseline allowed!")
        return True


def main():
    """Main function for the baseline check."""
    # Find latest evaluation and baseline metrics
    latest_eval = find_latest_evaluation()
    latest_baseline = find_latest_baseline_metrics()

    # Combine metrics from both sources
    metrics = {}

    # Extract RAGChecker metrics
    if latest_eval:
        eval_data = parse_evaluation_file(latest_eval)
        if eval_data:
            metrics.update(extract_metrics(eval_data))

    # Extract baseline metrics (latency, reranker, health)
    if latest_baseline:
        baseline_data = parse_evaluation_file(latest_baseline)
        if baseline_data:
            metrics.update(extract_baseline_metrics(baseline_data))

    if not metrics:
        print("⚠️  Warning: No baseline metrics found")
        print("   Run: python3 scripts/baseline_metrics_collector.py")
        print("   This check will become mandatory once you reach baseline.")
        return 0  # Don't block commits yet

    # Check compliance
    compliant, violations = check_baseline_compliance(metrics)

    # Print status
    is_ok = print_status(metrics, violations, latest_eval or latest_baseline)

    # For now, always return 0 (don't block commits)
    # Once you reach baseline, this will become a hard gate
    if CURRENT_STATUS == "DEVELOPMENT_PHASE":
        if not is_ok:
            print("🚨 NOTE: This will become a HARD GATE once you reach production-ready status!")
            print("   For now, commits are allowed but you're warned about performance issues.")
        return 0
    else:
        # Production ready mode - hard gate
        return 0 if is_ok else 1


if __name__ == "__main__":
    sys.exit(main())
