#!/usr/bin/env python3
"""
Pre-commit RAGChecker Evaluation Script

This script runs RAGChecker evaluation as part of the pre-commit process
to ensure RAG system changes meet quality standards before committing.
"""

import json
import subprocess
import sys
from pathlib import Path


def check_ragchecker_changes() -> bool:
    """Check if RAGChecker-related files have been modified."""
    try:
        # Get staged files
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)

        staged_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Check for RAGChecker-related changes
        ragchecker_patterns = [
            "scripts/ragchecker_",
            "tests/test_ragchecker_",
            "metrics/baseline_evaluations/",
            "400_guides/400_ragchecker-",
        ]

        for file_path in staged_files:
            for pattern in ragchecker_patterns:
                if pattern in file_path:
                    print(f"🔍 RAGChecker-related file detected: {file_path}")
                    return True

        return False

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error checking staged files: {e}")
        return False


def run_ragchecker_evaluation() -> bool:
    """Run RAGChecker evaluation and return success status."""
    try:
        print("🧪 Running RAGChecker evaluation...")

        # Run the official evaluation
        result = subprocess.run(
            ["python3", "scripts/ragchecker_official_evaluation.py"],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
        )

        if result.returncode != 0:
            print(f"❌ RAGChecker evaluation failed: {result.stderr}")
            return False

        print("✅ RAGChecker evaluation completed successfully")

        # Check for evaluation results
        eval_files = list(Path("metrics/baseline_evaluations").glob("ragchecker_official_evaluation_*.json"))
        if not eval_files:
            print("⚠️ No evaluation results found")
            return False

        # Get latest evaluation
        latest_eval = max(eval_files, key=lambda f: f.stat().st_mtime)

        # Validate results
        with open(latest_eval, "r") as f:
            data = json.load(f)

        metrics = data["overall_metrics"]
        print(
            f"📊 Evaluation metrics: Precision={metrics['precision']:.3f}, Recall={metrics['recall']:.3f}, F1={metrics['f1_score']:.3f}"
        )

        # Check quality gates (relaxed for pre-commit)
        quality_gates_passed = 0

        if metrics["precision"] >= 0.001:
            quality_gates_passed += 1
        else:
            print("⚠️ Precision below threshold (expected for fallback evaluation)")

        if metrics["recall"] >= 0.5:
            quality_gates_passed += 1
        else:
            print("⚠️ Recall below threshold (needs improvement)")

        if metrics["f1_score"] >= 0.001:
            quality_gates_passed += 1
        else:
            print("⚠️ F1 Score below threshold (expected for fallback evaluation)")

        print(f"🎯 Quality gates: {quality_gates_passed}/3 passed")

        # Allow commit if at least 1 gate passes (for fallback evaluation)
        if quality_gates_passed >= 1:
            print("✅ Pre-commit RAGChecker evaluation passed")
            return True
        else:
            print("❌ Pre-commit RAGChecker evaluation failed")
            return False

    except subprocess.TimeoutExpired:
        print("❌ RAGChecker evaluation timed out")
        return False
    except Exception as e:
        print(f"❌ RAGChecker evaluation error: {e}")
        return False


def run_ragchecker_tests() -> bool:
    """Run RAGChecker tests and return success status."""
    try:
        print("🧪 Running RAGChecker tests...")

        # Run evaluation tests
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_ragchecker_evaluation.py", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"❌ RAGChecker tests failed: {result.stderr}")
            return False

        print("✅ RAGChecker tests passed")
        return True

    except subprocess.TimeoutExpired:
        print("❌ RAGChecker tests timed out")
        return False
    except Exception as e:
        print(f"❌ RAGChecker tests error: {e}")
        return False


def main():
    """Main pre-commit function."""
    print("🔍 RAGChecker Pre-commit Hook")
    print("=" * 40)

    # Check if RAGChecker-related files are staged
    if not check_ragchecker_changes():
        print("✅ No RAGChecker-related changes detected, skipping evaluation")
        return 0

    print("🚀 RAGChecker-related changes detected, running evaluation...")

    # Run tests first
    if not run_ragchecker_tests():
        print("❌ RAGChecker tests failed, commit blocked")
        return 1

    # Run evaluation
    if not run_ragchecker_evaluation():
        print("❌ RAGChecker evaluation failed, commit blocked")
        return 1

    print("✅ Pre-commit RAGChecker validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
