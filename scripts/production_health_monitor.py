#!/usr/bin/env python3
"""
Production Health Monitor
- Monitor chunking configuration health
- Check for prefix leakage, token budget violations
- Validate retrieval performance
- Generate daily health reports
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(dspy_rag_path))

from src.utils.config_lock import (
    ConfigLockManager,
    LockedConfig,
    ProductionGuardrails,
)


def check_config_health(config: LockedConfig) -> dict[str, Any]:
    """Check configuration health"""
    guardrails = ProductionGuardrails(config)
    validation = guardrails.validate_config()

    return {
        "config_version": config.chunk_version,
        "config_hash": config.get_config_hash(),
        "validation": validation,
        "timestamp": datetime.now().isoformat(),
    }


def check_retrieval_health(eval_results_dir: Path) -> dict[str, Any]:
    """Check retrieval health from evaluation results"""
    if not eval_results_dir.exists():
        return {"error": "Evaluation results directory not found"}

    # Find latest evaluation results
    eval_files = list(eval_results_dir.glob("*.json"))
    if not eval_files:
        return {"error": "No evaluation results found"}

    latest_file = max(eval_files, key=lambda f: f.stat().st_mtime)

    try:
        with open(latest_file) as f:
            eval_data = json.load(f)

        case_results = eval_data.get("case_results", [])
        if not case_results:
            return {"error": "No case results found"}

        # Check for prefix leakage in BM25
        bm25_with_prefix = 0
        over_budget_chunks = 0
        snapshot_sizes = []
        oracle_hits = []

        for case in case_results:
            retrieval_snapshot = case.get("retrieval_snapshot", [])
            snapshot_sizes.append(len(retrieval_snapshot))

            oracle_hit = case.get("oracle_retrieval_hit_prefilter", 0)
            oracle_hits.append(oracle_hit)

            for chunk in retrieval_snapshot:
                bm25_text = chunk.get("bm25_text", "")
                if bm25_text.startswith("Document:"):
                    bm25_with_prefix += 1

                embedding_tokens = chunk.get("embedding_token_count", 0)
                if embedding_tokens > 1024:  # Hard cap
                    over_budget_chunks += 1

        return {
            "eval_file": str(latest_file),
            "total_cases": len(case_results),
            "bm25_prefix_leakage": bm25_with_prefix,
            "over_budget_chunks": over_budget_chunks,
            "avg_snapshot_size": sum(snapshot_sizes) / len(snapshot_sizes) if snapshot_sizes else 0,
            "avg_oracle_hit": sum(oracle_hits) / len(oracle_hits) if oracle_hits else 0,
            "healthy": bm25_with_prefix == 0 and over_budget_chunks == 0,
        }

    except Exception as e:
        return {"error": f"Error processing evaluation results: {e}"}


def check_ingest_health(ingest_run_id: str) -> dict[str, Any]:
    """Check ingest health for a specific run"""
    # This would typically query your database
    # For now, we'll return a placeholder
    return {
        "ingest_run_id": ingest_run_id,
        "status": "placeholder",
        "chunk_count": 0,
        "dedup_rate": 0.0,
        "avg_tokens": 0,
        "max_tokens": 0,
    }


def generate_health_report(
    config_health: dict[str, Any],
    retrieval_health: dict[str, Any],
    ingest_health: dict[str, Any],
) -> dict[str, Any]:
    """Generate comprehensive health report"""

    overall_healthy = (
        config_health.get("validation", {}).get("valid", False)
        and retrieval_health.get("healthy", False)
        and not config_health.get("error")
        and not retrieval_health.get("error")
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "overall_healthy": overall_healthy,
        "config_health": config_health,
        "retrieval_health": retrieval_health,
        "ingest_health": ingest_health,
        "alerts": generate_alerts(config_health, retrieval_health, ingest_health),
    }


def generate_alerts(
    config_health: dict[str, Any],
    retrieval_health: dict[str, Any],
    ingest_health: dict[str, Any],
) -> list[str]:
    """Generate alerts for health issues"""
    alerts = []

    # Config validation alerts
    if not config_health.get("validation", {}).get("valid", True):
        alerts.append("🚨 Configuration validation failed")

    if config_health.get("validation", {}).get("issues"):
        alerts.extend([f"🚨 {issue}" for issue in config_health["validation"]["issues"]])

    if config_health.get("validation", {}).get("warnings"):
        alerts.extend([f"⚠️  {warning}" for warning in config_health["validation"]["warnings"]])

    # Retrieval health alerts
    if not retrieval_health.get("healthy", True):
        alerts.append("🚨 Retrieval health issues detected")

    if retrieval_health.get("bm25_prefix_leakage", 0) > 0:
        alerts.append(f"🚨 BM25 prefix leakage: {retrieval_health['bm25_prefix_leakage']} chunks")

    if retrieval_health.get("over_budget_chunks", 0) > 0:
        alerts.append(f"🚨 Over budget chunks: {retrieval_health['over_budget_chunks']}")

    # Performance alerts
    avg_snapshot_size = retrieval_health.get("avg_snapshot_size", 0)
    if avg_snapshot_size < 10:
        alerts.append(f"⚠️  Low retrieval snapshot size: {avg_snapshot_size}")

    avg_oracle_hit = retrieval_health.get("avg_oracle_hit", 0)
    if avg_oracle_hit < 0.3:
        alerts.append(f"⚠️  Low oracle hit rate: {avg_oracle_hit:.2f}")

    return alerts


def main():
    parser = argparse.ArgumentParser(description="Monitor production chunking health")
    parser.add_argument(
        "--eval-results-dir", default="metrics/baseline_evaluations", help="Directory containing evaluation results"
    )
    parser.add_argument("--ingest-run-id", help="Specific ingest run ID to check")
    parser.add_argument("--output", help="Output file for health report")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode (no console output)")

    args = parser.parse_args()

    # Load active configuration
    manager = ConfigLockManager()
    config = manager.get_active_config()

    if not config:
        print("❌ No active configuration found")
        sys.exit(1)

    # Check configuration health
    config_health = check_config_health(config)

    # Check retrieval health
    eval_results_dir = Path(args.eval_results_dir)
    retrieval_health = check_retrieval_health(eval_results_dir)

    # Check ingest health
    ingest_health = check_ingest_health(args.ingest_run_id or "latest")

    # Generate health report
    health_report = generate_health_report(config_health, retrieval_health, ingest_health)

    # Save report
    if args.output:
        output_file = Path(args.output)
        with open(output_file, "w") as f:
            json.dump(health_report, f, indent=2)

    # Console output
    if not args.quiet:
        print("🏥 Production Health Monitor")
        print("=" * 40)
        print(f"Config: {config.chunk_version}")
        print(f"Overall Health: {'✅ Healthy' if health_report['overall_healthy'] else '❌ Issues'}")
        print()

        if health_report["alerts"]:
            print("🚨 Alerts:")
            for alert in health_report["alerts"]:
                print(f"  {alert}")
            print()

        print("📊 Metrics:")
        print(f"  Config valid: {config_health.get('validation', {}).get('valid', 'unknown')}")
        print(f"  Retrieval healthy: {retrieval_health.get('healthy', 'unknown')}")
        print(f"  BM25 prefix leakage: {retrieval_health.get('bm25_prefix_leakage', 0)}")
        print(f"  Over budget chunks: {retrieval_health.get('over_budget_chunks', 0)}")
        print(f"  Avg snapshot size: {retrieval_health.get('avg_snapshot_size', 0):.1f}")
        print(f"  Avg oracle hit: {retrieval_health.get('avg_oracle_hit', 0):.2f}")

    # Exit with error code if unhealthy
    if not health_report["overall_healthy"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
