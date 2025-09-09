#!/usr/bin/env python3
"""
Sanity Probes Script
- Validate evaluation artifacts and fingerprints
- Check for prefix leakage and data quality issues
- Verify configuration consistency across the pipeline
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(dspy_rag_path))

from src.utils.config_lock import ConfigLockManager, LockedConfig


def load_evaluation_results(results_dir: Path) -> dict[str, Any] | None:
    """Load the latest evaluation results"""
    if not results_dir.exists():
        return None

    # Find latest evaluation file
    eval_files = list(results_dir.glob("*.json"))
    if not eval_files:
        return None

    latest_file = max(eval_files, key=lambda f: f.stat().st_mtime)

    try:
        with open(latest_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading evaluation results: {e}")
        return None


def check_run_variant_fingerprints(eval_data: dict[str, Any], expected_config: LockedConfig) -> dict[str, Any]:
    """Check that the right run/variant is in artifacts"""
    print("🔍 Checking run/variant fingerprints...")

    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    # Check first few retrieval snapshots for fingerprints
    issues = []
    warnings = []

    for i, case in enumerate(case_results[:3]):  # Check first 3 cases
        retrieval_snapshot = case.get("retrieval_snapshot", [])
        if not retrieval_snapshot:
            warnings.append(f"Case {i}: No retrieval snapshot")
            continue

        # Check first few chunks for fingerprints
        for j, chunk in enumerate(retrieval_snapshot[:8]):
            # Check for ingest_run_id in chunk metadata
            chunk_ingest_run_id = chunk.get("ingest_run_id")
            expected_run_id = f"{expected_config.chunk_version}-{expected_config.get_config_hash()[:8]}"

            if chunk_ingest_run_id != expected_run_id:
                issues.append(
                    f"Case {i}, chunk {j}: Wrong ingest_run_id. Expected {expected_run_id}, got {chunk_ingest_run_id}"
                )

            # Check for chunk_version
            chunk_version = chunk.get("chunk_version")
            if chunk_version != expected_config.chunk_version:
                issues.append(
                    f"Case {i}, chunk {j}: Wrong chunk_version. Expected {expected_config.chunk_version}, got {chunk_version}"
                )

            # Check for config hash in chunk ID
            chunk_id = chunk.get("id", "")
            expected_config_hash = expected_config.get_config_hash()[:8]
            if chunk_id and expected_config_hash not in str(chunk_id):
                warnings.append(f"Case {i}, chunk {j}: Config hash not found in chunk ID")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "checked_cases": min(3, len(case_results)),
        "checked_chunks": sum(len(case.get("retrieval_snapshot", [])) for case in case_results[:3]),
    }


def check_breadth_and_usage(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Check breadth and usage metrics"""
    print("🔍 Checking breadth and usage...")

    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    # Check retrieval snapshot sizes
    snapshot_sizes = [len(case.get("retrieval_snapshot", [])) for case in case_results]
    max_snapshot_size = max(snapshot_sizes) if snapshot_sizes else 0
    avg_snapshot_size = sum(snapshot_sizes) / len(snapshot_sizes) if snapshot_sizes else 0

    # Check retrieved context lengths
    context_lengths = [len(case.get("retrieved_context", [])) for case in case_results]
    max_context_length = max(context_lengths) if context_lengths else 0
    avg_context_length = sum(context_lengths) / len(context_lengths) if context_lengths else 0

    issues = []
    warnings = []

    # Check snapshot size bounds
    if max_snapshot_size < 20:
        issues.append(f"Max retrieval snapshot size too low: {max_snapshot_size} (expected ≥20)")
    elif max_snapshot_size < 30:
        warnings.append(f"Max retrieval snapshot size low: {max_snapshot_size} (expected 30-60+)")

    if avg_snapshot_size < 15:
        issues.append(f"Avg retrieval snapshot size too low: {avg_snapshot_size:.1f}")

    # Check context length bounds
    if max_context_length > 12:
        warnings.append(f"Max retrieved context length high: {max_context_length} (expected ≤12)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "max_snapshot_size": max_snapshot_size,
        "avg_snapshot_size": avg_snapshot_size,
        "max_context_length": max_context_length,
        "avg_context_length": avg_context_length,
    }


def check_oracle_path(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Check oracle path is alive"""
    print("🔍 Checking oracle path...")

    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    # Check oracle retrieval hit prefilter
    oracle_hits = [case.get("oracle_retrieval_hit_prefilter", 0) for case in case_results]
    total_oracle_hits = sum(oracle_hits)
    avg_oracle_hit = total_oracle_hits / len(oracle_hits) if oracle_hits else 0

    # Check reader used gold
    reader_gold = [case.get("reader_used_gold", 0) for case in case_results]
    total_reader_gold = sum(reader_gold)
    avg_reader_gold = total_reader_gold / len(reader_gold) if reader_gold else 0

    issues = []
    warnings = []

    # Check oracle hit rate
    if avg_oracle_hit < 0.1:
        issues.append(f"Oracle hit rate too low: {avg_oracle_hit:.3f} (expected ≥0.1)")
    elif avg_oracle_hit < 0.2:
        warnings.append(f"Oracle hit rate low: {avg_oracle_hit:.3f} (expected ≥0.2)")

    # Check reader gold usage
    if avg_reader_gold < 0.05:
        issues.append(f"Reader gold usage too low: {avg_reader_gold:.3f} (expected ≥0.05)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "total_oracle_hits": total_oracle_hits,
        "avg_oracle_hit": avg_oracle_hit,
        "total_reader_gold": total_reader_gold,
        "avg_reader_gold": avg_reader_gold,
    }


def check_prefix_leakage(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Check for prefix leakage in BM25"""
    print("🔍 Checking prefix leakage...")

    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    bm25_with_prefix = 0
    total_chunks = 0

    for case in case_results:
        retrieval_snapshot = case.get("retrieval_snapshot", [])
        for chunk in retrieval_snapshot:
            total_chunks += 1
            bm25_text = chunk.get("bm25_text", "")
            if bm25_text.startswith("Document:"):
                bm25_with_prefix += 1

    issues = []
    warnings = []

    if bm25_with_prefix > 0:
        issues.append(f"Prefix leakage detected: {bm25_with_prefix} chunks with 'Document:' prefix in BM25 text")

    return {
        "valid": bm25_with_prefix == 0,
        "issues": issues,
        "warnings": warnings,
        "bm25_with_prefix": bm25_with_prefix,
        "total_chunks": total_chunks,
        "leakage_rate": bm25_with_prefix / total_chunks if total_chunks > 0 else 0,
    }


def check_token_budget_compliance(eval_data: dict[str, Any], max_tokens: int = 1024) -> dict[str, Any]:
    """Check token budget compliance"""
    print("🔍 Checking token budget compliance...")

    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    over_budget_chunks = 0
    total_chunks = 0
    max_embedding_tokens = 0
    max_bm25_tokens = 0

    for case in case_results:
        retrieval_snapshot = case.get("retrieval_snapshot", [])
        for chunk in retrieval_snapshot:
            total_chunks += 1
            embedding_tokens = chunk.get("embedding_token_count", 0)
            bm25_tokens = chunk.get("bm25_token_count", 0)

            max_embedding_tokens = max(max_embedding_tokens, embedding_tokens)
            max_bm25_tokens = max(max_bm25_tokens, bm25_tokens)

            if embedding_tokens > max_tokens:
                over_budget_chunks += 1

    issues = []
    warnings = []

    if over_budget_chunks > 0:
        issues.append(f"Token budget violations: {over_budget_chunks} chunks over {max_tokens} tokens")

    if max_embedding_tokens > max_tokens * 1.1:
        warnings.append(f"High max embedding tokens: {max_embedding_tokens} (expected ≤{max_tokens})")

    return {
        "valid": over_budget_chunks == 0,
        "issues": issues,
        "warnings": warnings,
        "over_budget_chunks": over_budget_chunks,
        "total_chunks": total_chunks,
        "max_embedding_tokens": max_embedding_tokens,
        "max_bm25_tokens": max_bm25_tokens,
        "violation_rate": over_budget_chunks / total_chunks if total_chunks > 0 else 0,
    }


def run_sanity_probes(results_dir: Path, config: LockedConfig) -> dict[str, Any]:
    """Run all sanity probes"""
    print("🔍 Running Sanity Probes")
    print("=" * 40)

    # Load evaluation results
    eval_data = load_evaluation_results(results_dir)
    if not eval_data:
        return {"valid": False, "error": "No evaluation results found"}

    # Run all probes
    probes = {
        "run_variant_fingerprints": check_run_variant_fingerprints(eval_data, config),
        "breadth_and_usage": check_breadth_and_usage(eval_data),
        "oracle_path": check_oracle_path(eval_data),
        "prefix_leakage": check_prefix_leakage(eval_data),
        "token_budget_compliance": check_token_budget_compliance(eval_data, config.chunk_size),
    }

    # Overall validation
    all_valid = all(probe.get("valid", False) for probe in probes.values())
    total_issues = sum(len(probe.get("issues", [])) for probe in probes.values())
    total_warnings = sum(len(probe.get("warnings", [])) for probe in probes.values())

    return {
        "valid": all_valid,
        "total_issues": total_issues,
        "total_warnings": total_warnings,
        "probes": probes,
        "eval_file": (
            str(max(results_dir.glob("*.json"), key=lambda f: f.stat().st_mtime)) if results_dir.exists() else None
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Run sanity probes on evaluation results")
    parser.add_argument(
        "--results-dir", default="metrics/baseline_evaluations", help="Directory containing evaluation results"
    )
    parser.add_argument("--output", help="Output file for probe results")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    # Load active configuration
    manager = ConfigLockManager()
    config = manager.get_active_config()

    if not config:
        print("❌ No active configuration found. Run lock_production_config.py first.")
        sys.exit(1)

    # Run sanity probes
    results_dir = Path(args.results_dir)
    probe_results = run_sanity_probes(results_dir, config)

    # Save results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(probe_results, f, indent=2)

    # Console output
    if not args.quiet:
        print("\n📊 Sanity Probe Results")
        print("=" * 40)
        print(f"Overall Valid: {'✅' if probe_results['valid'] else '❌'}")
        print(f"Total Issues: {probe_results['total_issues']}")
        print(f"Total Warnings: {probe_results['total_warnings']}")

        if probe_results.get("eval_file"):
            print(f"Eval File: {probe_results['eval_file']}")

        print("\n🔍 Probe Details:")
        for probe_name, probe_result in probe_results["probes"].items():
            status = "✅" if probe_result.get("valid", False) else "❌"
            print(f"  {probe_name}: {status}")

            if probe_result.get("issues"):
                for issue in probe_result["issues"]:
                    print(f"    🚨 {issue}")

            if probe_result.get("warnings"):
                for warning in probe_result["warnings"]:
                    print(f"    ⚠️  {warning}")

    # Exit with error code if probes failed
    if not probe_results["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
