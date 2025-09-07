#!/usr/bin/env python3
"""
Production Evaluation Script
- One-command evaluation with locked configuration
- Shadow re-ingest and dual indexing
- Comprehensive health checks
- Performance monitoring
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dspy_rag_system.src.utils.config_lock import (
    ConfigLockManager,
    ShadowIndexManager,
    ProductionGuardrails,
    LockedConfig,
)


def run_command(cmd: str, cwd: Path = None) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd or project_root,
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"   Error: {result.stderr}")
        return result
    
    print(f"✅ Command succeeded: {cmd}")
    return result


def setup_environment(config: LockedConfig) -> Dict[str, str]:
    """Setup environment variables for locked configuration"""
    shadow_manager = ShadowIndexManager(config)
    ingest_run_id = shadow_manager.get_ingest_run_id()
    
    env_vars = {
        "INGEST_RUN_ID": ingest_run_id,
        "CHUNK_SIZE": str(config.chunk_size),
        "OVERLAP_RATIO": str(config.overlap_ratio),
        "JACCARD_THRESHOLD": str(config.jaccard_threshold),
        "PREFIX_POLICY": config.prefix_policy,
        "EVAL_DISABLE_CACHE": "1",
        "CHUNK_VERSION": config.chunk_version,
        "EMBEDDER_NAME": config.embedder_name,
    }
    
    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("🔧 Environment Variables Set:")
    for key, value in env_vars.items():
        print(f"   {key}={value}")
    
    return env_vars


def run_ingest(config: LockedConfig) -> Dict[str, Any]:
    """Run enhanced ingest with locked configuration"""
    print("\n📊 Running Enhanced Ingest")
    print("=" * 40)
    
    shadow_manager = ShadowIndexManager(config)
    ingest_run_id = shadow_manager.get_ingest_run_id()
    
    # Create shadow table
    shadow_table = shadow_manager.create_shadow_table()
    
    # Run ingest
    cmd = f"python dspy-rag-system/scripts/ingest_enhanced.py --run-id {ingest_run_id}"
    result = run_command(cmd)
    
    return {
        "ingest_run_id": ingest_run_id,
        "shadow_table": shadow_table,
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_evaluation(config: LockedConfig) -> Dict[str, Any]:
    """Run RAGChecker evaluation"""
    print("\n🧪 Running RAGChecker Evaluation")
    print("=" * 40)
    
    # Run evaluation
    cmd = (
        "python scripts/ragchecker_official_evaluation.py "
        "--cases eval/test_cases.json "
        "--outdir metrics/baseline_evaluations "
        "--use-bedrock "
        "--bypass-cli"
    )
    result = run_command(cmd)
    
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_sanity_checks() -> Dict[str, Any]:
    """Run sanity checks on evaluation results"""
    print("\n🔍 Running Sanity Checks")
    print("=" * 40)
    
    results_dir = Path("metrics/baseline_evaluations")
    if not results_dir.exists():
        return {"error": "Evaluation results directory not found"}
    
    # Find latest evaluation file
    eval_files = list(results_dir.glob("*.json"))
    if not eval_files:
        return {"error": "No evaluation results found"}
    
    latest_file = max(eval_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, "r") as f:
            eval_data = json.load(f)
        
        case_results = eval_data.get("case_results", [])
        
        # Check eval_path
        eval_path = eval_data.get("eval_path", "unknown")
        
        # Check schema version
        schema_version = eval_data.get("schema_version", "unknown")
        
        # Check retrieval snapshot sizes
        snapshot_sizes = [len(case.get("retrieval_snapshot", [])) for case in case_results]
        max_snapshot_size = max(snapshot_sizes) if snapshot_sizes else 0
        
        # Check oracle hit rates
        oracle_hits = [case.get("oracle_retrieval_hit_prefilter", 0) for case in case_results]
        total_oracle_hits = sum(oracle_hits)
        
        return {
            "eval_file": str(latest_file),
            "eval_path": eval_path,
            "schema_version": schema_version,
            "max_snapshot_size": max_snapshot_size,
            "total_oracle_hits": total_oracle_hits,
            "total_cases": len(case_results),
        }
        
    except Exception as e:
        return {"error": f"Error processing evaluation results: {e}"}


def run_health_checks(config: LockedConfig) -> Dict[str, Any]:
    """Run production health checks"""
    print("\n🏥 Running Health Checks")
    print("=" * 40)
    
    guardrails = ProductionGuardrails(config)
    
    # Validate configuration
    validation = guardrails.validate_config()
    
    # Check retrieval health
    results_dir = Path("metrics/baseline_evaluations")
    if results_dir.exists():
        eval_files = list(results_dir.glob("*.json"))
        if eval_files:
            latest_file = max(eval_files, key=lambda f: f.stat().st_mtime)
            with open(latest_file, "r") as f:
                eval_data = json.load(f)
            
            case_results = eval_data.get("case_results", [])
            retrieval_health = guardrails.check_retrieval_health(case_results)
        else:
            retrieval_health = {"error": "No evaluation results found"}
    else:
        retrieval_health = {"error": "Evaluation results directory not found"}
    
    return {
        "config_validation": validation,
        "retrieval_health": retrieval_health,
    }


def generate_report(
    config: LockedConfig,
    ingest_results: Dict[str, Any],
    eval_results: Dict[str, Any],
    sanity_results: Dict[str, Any],
    health_results: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate comprehensive evaluation report"""
    
    overall_success = (
        ingest_results.get("success", False) and
        eval_results.get("success", False) and
        not sanity_results.get("error") and
        health_results.get("config_validation", {}).get("valid", False)
    )
    
    return {
        "timestamp": datetime.now().isoformat(),
        "config_version": config.chunk_version,
        "config_hash": config.get_config_hash(),
        "overall_success": overall_success,
        "ingest_results": ingest_results,
        "eval_results": eval_results,
        "sanity_results": sanity_results,
        "health_results": health_results,
        "summary": {
            "ingest_success": ingest_results.get("success", False),
            "eval_success": eval_results.get("success", False),
            "config_valid": health_results.get("config_validation", {}).get("valid", False),
            "retrieval_healthy": health_results.get("retrieval_health", {}).get("healthy", False),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run production evaluation with locked configuration")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip ingest step")
    parser.add_argument("--skip-eval", action="store_true", help="Skip evaluation step")
    parser.add_argument("--output", help="Output file for evaluation report")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    # Load active configuration
    manager = ConfigLockManager()
    config = manager.get_active_config()
    
    if not config:
        print("❌ No active configuration found. Run lock_production_config.py first.")
        sys.exit(1)
    
    print("🚀 Production Evaluation")
    print("=" * 50)
    print(f"Config: {config.chunk_version}")
    print(f"Hash: {config.get_config_hash()}")
    print(f"Chunk size: {config.chunk_size}")
    print(f"Overlap ratio: {config.overlap_ratio}")
    print(f"Jaccard threshold: {config.jaccard_threshold}")
    print(f"Prefix policy: {config.prefix_policy}")
    print()
    
    # Setup environment
    env_vars = setup_environment(config)
    
    # Run ingest
    if not args.skip_ingest:
        ingest_results = run_ingest(config)
    else:
        ingest_results = {"skipped": True}
    
    # Run evaluation
    if not args.skip_eval:
        eval_results = run_evaluation(config)
    else:
        eval_results = {"skipped": True}
    
    # Run sanity checks
    sanity_results = run_sanity_checks()
    
    # Run health checks
    health_results = run_health_checks(config)
    
    # Generate report
    report = generate_report(config, ingest_results, eval_results, sanity_results, health_results)
    
    # Save report
    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
    
    # Console output
    if not args.quiet:
        print("\n📊 Evaluation Summary")
        print("=" * 40)
        print(f"Overall Success: {'✅' if report['overall_success'] else '❌'}")
        print(f"Ingest: {'✅' if report['summary']['ingest_success'] else '❌'}")
        print(f"Evaluation: {'✅' if report['summary']['eval_success'] else '❌'}")
        print(f"Config Valid: {'✅' if report['summary']['config_valid'] else '❌'}")
        print(f"Retrieval Healthy: {'✅' if report['summary']['retrieval_healthy'] else '❌'}")
        
        if sanity_results.get("eval_file"):
            print(f"\n📁 Latest Results: {sanity_results['eval_file']}")
            print(f"   Eval Path: {sanity_results.get('eval_path', 'unknown')}")
            print(f"   Schema Version: {sanity_results.get('schema_version', 'unknown')}")
            print(f"   Max Snapshot Size: {sanity_results.get('max_snapshot_size', 0)}")
            print(f"   Total Oracle Hits: {sanity_results.get('total_oracle_hits', 0)}")
        
        if health_results.get("retrieval_health", {}).get("bm25_prefix_leakage", 0) > 0:
            print(f"\n🚨 BM25 Prefix Leakage: {health_results['retrieval_health']['bm25_prefix_leakage']}")
        
        if health_results.get("retrieval_health", {}).get("over_budget_chunks", 0) > 0:
            print(f"🚨 Over Budget Chunks: {health_results['retrieval_health']['over_budget_chunks']}")
    
    # Exit with error code if evaluation failed
    if not report["overall_success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
