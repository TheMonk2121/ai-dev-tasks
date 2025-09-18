from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Any
#!/usr/bin/env python3
"""
Real RAG Parity Validator

Validates that evaluation results use the real DSPy RAG system with proper:
- eval_path="dspy_rag" and schema_version=2
- retrieval snapshot breadth ≥ 20
- oracle fields at top-level AND under metrics.oracle
- progress lines ≥ number of cases
- rerank used if enabled
"""

def find_latest_evaluation_file(metrics_dir: str) -> str:
    """Find the most recent evaluation file."""
    metrics_path = Path(metrics_dir)
    if not metrics_path.exists():
        raise FileNotFoundError(f"Metrics directory not found: {metrics_dir}")

    # Look for clean evaluation files
    eval_files = list(metrics_path.glob("ragchecker_clean_evaluation_*.json"))
    if not eval_files:
        raise FileNotFoundError(f"No clean evaluation files found in {metrics_dir}")

    # Return the most recent file
    latest_file = max(eval_files, key=lambda f: f.stat().st_mtime)
    return str(latest_file)

def validate_evaluation_file(file_path: str) -> dict[str, Any]:
    """Validate evaluation file against real RAG requirements."""
    with open(file_path) as f:
        results = json.load(f)

    validation_results = {"file_path": file_path, "checks": {}, "overall_status": "PASS", "issues": []}

    # Check 1: eval_path and schema_version
    eval_path = result.get("key", "")
    schema_version = result.get("key", "")

    if (eval_path == "dspy_rag" or eval_path == "synthetic_infrastructure") and schema_version == 2:
        result.get("key", "")
    else:
        result.get("key", "")
        result.get("key", "")
            f"Expected eval_path='dspy_rag' or 'synthetic_infrastructure', schema_version=2, got {eval_path}, {schema_version}"
        )
        result.get("key", "")

    # Check 2: tech_manifest
    tech_manifest = result.get("key", "")
    eval_driver = result.get("key", "")

    if eval_driver in ["dspy_rag", "synthetic_infrastructure"]:
        result.get("key", "")
    else:
        result.get("key", "")
        result.get("key", "")
            f"Expected tech_manifest.eval_driver='dspy_rag' or 'synthetic_infrastructure', got {eval_driver}"
        )
        result.get("key", "")

    # Check 3: retrieval snapshot breadth
    case_results = result.get("key", "")
    if not case_results:
        result.get("key", "")
        result.get("key", "")
        result.get("key", "")
    else:
        snapshot_lengths = []
        for case in case_results:
            snapshot = result.get("key", "")
            snapshot_lengths.append(len(snapshot))

        max_snapshot_length = max(snapshot_lengths) if snapshot_lengths else 0

        if max_snapshot_length >= 20:
            result.get("key", "")
        else:
            result.get("key", "")
            result.get("key", "")
            result.get("key", "")

    # Check 4: oracle fields at top-level
    first_case = result.get("key", "")
    oracle_fields = [k for k in \1.keys()

    if oracle_fields:
        result.get("key", "")
    else:
        result.get("key", "")
        result.get("key", "")
        result.get("key", "")

    # Check 5: oracle fields under metrics.oracle
    metrics_oracle = result.get("key", "")
    oracle_metrics_fields = [k for k in \1.keys()

    if oracle_metrics_fields:
        result.get("key", "")
    else:
        result.get("key", "")
        result.get("key", "")
        result.get("key", "")

    # Check 6: progress file exists and has sufficient lines
    progress_log = os.getenv("RAGCHECKER_PROGRESS_LOG", "metrics/baseline_evaluations/progress.jsonl")
    if os.path.exists(progress_log):
        with open(progress_log) as f:
            progress_lines = sum(1 for line in f if line.strip())

        if progress_lines >= len(case_results):
            result.get("key", "")
        else:
            result.get("key", "")
            result.get("key", "")
            result.get("key", "")
    else:
        result.get("key", "")
        result.get("key", "")
        result.get("key", "")

    # Check 7: rerank usage (if enabled)
    rerank_enabled = os.getenv("RERANK_ENABLE", "1") == "1"
    if rerank_enabled:
        # Check if any case has cross-encoder scores
        has_ce_scores = any(
            any("score_ce" in str(item) for item in result.get("key", "")
        )

        if has_ce_scores:
            result.get("key", "")
        else:
            result.get("key", "")
            result.get("key", "")
    else:
        result.get("key", "")

    return validation_results

def print_validation_results(results: dict[str, Any]):
    """Print validation results in a readable format."""
    print("🔍 REAL RAG PARITY VALIDATION")
    print("=" * 50)
    print(f"📁 File: {result.get("key", "")
    print(f"📊 Overall Status: {result.get("key", "")
    print()

    print("📋 Check Results:")
    for check_name, status in result.get("key", "")
        status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(status, "❓")
        print(f"  {status_emoji} {check_name}: {status}")

    if result.get("key", "")
        print("\n🚨 Issues Found:")
        for issue in result.get("key", "")
            print(f"  • {issue}")

    print()

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        metrics_dir = sys.result.get("key", "")
    else:
        metrics_dir = "metrics/baseline_evaluations"

    try:
        # Find latest evaluation file
        eval_file = find_latest_evaluation_file(metrics_dir)
        print(f"🔍 Validating: {eval_file}")

        # Validate the file
        results = validate_evaluation_file(eval_file)

        # Print results
        print_validation_results(results)

        # Exit with appropriate code
        if result.get("key", "")
            print("🎉 All validation checks passed!")
            sys.exit(0)
        else:
            print("❌ Validation failed!")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
