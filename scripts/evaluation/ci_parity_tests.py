from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from src.utils.config_lock import ConfigLockManager, LockedConfig
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
CI Parity Tests Script
- Fail the build if key metrics regress
- Validate configuration consistency
- Check for data quality issues
- Ensure deterministic behavior
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(dspy_rag_path))

def check_eval_path(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Check that eval_path is correct"""
    eval_path = eval_data.get("eval_path", "")

    if eval_path != "dspy_rag":
        return {"valid": False, "error": f"Wrong eval_path: {eval_path} (expected 'dspy_rag')"}

    return {"valid": True}

def check_retrieval_snapshot_size(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Check retrieval snapshot size"""
    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    snapshot_sizes = [len(case.get("retrieval_snapshot", [])) for case in case_results]
    min_snapshot_size = min(snapshot_sizes) if snapshot_sizes else 0
    max_snapshot_size = max(snapshot_sizes) if snapshot_sizes else 0
    avg_snapshot_size = sum(snapshot_sizes) / len(snapshot_sizes) if snapshot_sizes else 0

    issues = []

    if min_snapshot_size < 20:
        issues.append(f"Min retrieval snapshot size too low: {min_snapshot_size} (expected ≥20)")

    if avg_snapshot_size < 15:
        issues.append(f"Avg retrieval snapshot size too low: {avg_snapshot_size:.1f} (expected ≥15)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "min_snapshot_size": min_snapshot_size,
        "max_snapshot_size": max_snapshot_size,
        "avg_snapshot_size": avg_snapshot_size,
    }

def check_oracle_metrics(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Check oracle metrics are present"""
    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    issues = []

    # Check top-level oracle metrics
    oracle_metrics = ["oracle_retrieval_hit_prefilter", "oracle_retrieval_hit_postfilter"]
    for metric in oracle_metrics:
        if metric not in eval_data:
            issues.append(f"Missing top-level oracle metric: {metric}")

    # Check case-level oracle metrics
    for i, case in enumerate(case_results):
        if "oracle_retrieval_hit_prefilter" not in case:
            issues.append(f"Case {i}: Missing oracle_retrieval_hit_prefilter")

        if "oracle_retrieval_hit_postfilter" not in case:
            issues.append(f"Case {i}: Missing oracle_retrieval_hit_postfilter")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }

def check_token_budget_compliance(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Check token budget compliance"""
    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    over_budget_chunks = 0
    total_chunks = 0
    max_embedding_tokens = 0

    for case in case_results:
        retrieval_snapshot = case.get("retrieval_snapshot", [])
        for chunk in retrieval_snapshot:
            total_chunks += 1
            embedding_tokens = chunk.get("embedding_token_count", 0)
            max_embedding_tokens = max(max_embedding_tokens, embedding_tokens)

            if embedding_tokens > 1024:
                over_budget_chunks += 1

    issues = []

    if over_budget_chunks > 0:
        issues.append(f"Token budget violations: {over_budget_chunks} chunks over 1024 tokens")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "over_budget_chunks": over_budget_chunks,
        "total_chunks": total_chunks,
        "max_embedding_tokens": max_embedding_tokens,
    }

def check_prefix_leakage(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Check for prefix leakage in BM25"""
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

    if bm25_with_prefix > 0:
        issues.append(f"Prefix leakage: {bm25_with_prefix} chunks with 'Document:' prefix in BM25 text")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "bm25_with_prefix": bm25_with_prefix,
        "total_chunks": total_chunks,
    }

def check_chunk_id_determinism(eval_data: dict[str, Any], config: LockedConfig) -> dict[str, Any]:
    """Check chunk ID determinism"""
    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    issues = []
    chunk_ids = set()
    duplicate_ids = 0

    for case in case_results:
        retrieval_snapshot = case.get("retrieval_snapshot", [])
        for chunk in retrieval_snapshot:
            chunk_id = chunk.get("id", "")

            # Check for duplicate IDs
            if chunk_id in chunk_ids:
                duplicate_ids += 1
            else:
                chunk_ids.add(chunk_id)

            # Check ID format (should include config hash)
            expected_config_hash = config.get_config_hash()[:8]
            if chunk_id and expected_config_hash not in str(chunk_id):
                issues.append(f"Chunk ID missing config hash: {chunk_id}")

    if duplicate_ids > 0:
        issues.append(f"Duplicate chunk IDs found: {duplicate_ids}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "unique_chunk_ids": len(chunk_ids),
        "duplicate_ids": duplicate_ids,
    }

def check_configuration_consistency(eval_data: dict[str, Any], config: LockedConfig) -> dict[str, Any]:
    """Check configuration consistency"""
    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {"valid": False, "error": "No case results found"}

    issues = []

    # Check first few chunks for configuration consistency
    for i, case in enumerate(case_results[:3]):
        retrieval_snapshot = case.get("retrieval_snapshot", [])
        for j, chunk in enumerate(retrieval_snapshot[:5]):
            # Check chunk version
            chunk_version = chunk.get("chunk_version", "")
            if chunk_version != config.chunk_version:
                issues.append(
                    f"Case {i}, chunk {j}: Wrong chunk_version. Expected {config.chunk_version}, got {chunk_version}"
                )

            # Check ingest run ID
            ingest_run_id = chunk.get("ingest_run_id", "")
            expected_run_id = f"{config.chunk_version}-{config.get_config_hash()[:8]}"
            if ingest_run_id != expected_run_id:
                issues.append(
                    f"Case {i}, chunk {j}: Wrong ingest_run_id. Expected {expected_run_id}, got {ingest_run_id}"
                )

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }

def run_parity_tests(eval_data: dict[str, Any], config: LockedConfig) -> dict[str, Any]:
    """Run all parity tests"""
    print("🧪 Running CI Parity Tests")
    print("=" * 40)

    tests = {
        "eval_path": check_eval_path(eval_data),
        "retrieval_snapshot_size": check_retrieval_snapshot_size(eval_data),
        "oracle_metrics": check_oracle_metrics(eval_data),
        "token_budget_compliance": check_token_budget_compliance(eval_data),
        "prefix_leakage": check_prefix_leakage(eval_data),
        "chunk_id_determinism": check_chunk_id_determinism(eval_data, config),
        "configuration_consistency": check_configuration_consistency(eval_data, config),
    }

    # Overall validation
    all_valid = all(test.get("valid", False) for test in tests.values())
    total_issues = sum(len(test.get("issues", [])) for test in tests.values())

    return {
        "valid": all_valid,
        "total_issues": total_issues,
        "tests": tests,
        "config_version": config.chunk_version,
        "config_hash": config.get_config_hash(),
    }

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

def main():
    parser = argparse.ArgumentParser(description="Run CI parity tests")
    parser.add_argument(
        "--results-dir", default="metrics/baseline_evaluations", help="Directory containing evaluation results"
    )
    parser.add_argument("--output", help="Output file for test results")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    # Load active configuration
    manager = ConfigLockManager()
    config = manager.get_active_config()

    if not config:
        print("❌ No active configuration found. Run lock_production_config.py first.")
        sys.exit(1)

    # Load evaluation results
    results_dir = Path(args.results_dir)
    eval_data = load_evaluation_results(results_dir)

    if not eval_data:
        print("❌ No evaluation results found. Run evaluation first.")
        sys.exit(1)

    # Run parity tests
    test_results = run_parity_tests(eval_data, config)

    # Save results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(test_results, f, indent=2)

    # Console output
    if not args.quiet:
        print("\n📊 CI Parity Test Results")
        print("=" * 40)
        print(f"Overall Valid: {'✅' if test_results['valid'] else '❌'}")
        print(f"Total Issues: {test_results['total_issues']}")
        print(f"Config Version: {test_results['config_version']}")
        print(f"Config Hash: {test_results['config_hash']}")

        print("\n🧪 Test Details:")
        for test_name, test_result in test_results["tests"].items():
            status = "✅" if test_result.get("valid", False) else "❌"
            print(f"  {test_name}: {status}")

            if test_result.get("issues"):
                for issue in test_result["issues"]:
                    print(f"    🚨 {issue}")

    # Exit with error code if tests failed
    if not test_results["valid"]:
        print("\n❌ CI Parity Tests Failed - Build should fail")
        sys.exit(1)

    print("\n✅ CI Parity Tests Passed - Build can proceed")

if __name__ == "__main__":
    main()
