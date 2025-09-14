from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from src.utils.config_lock import ConfigLockManager, LockedConfig

#!/usr/bin/env python3
"""
KPI Monitor Script
- Monitor key performance indicators against baseline
- Check thresholds and generate alerts
- Support for canary rollout monitoring
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(dspy_rag_path))

def load_baseline_metrics(config: LockedConfig) -> dict[str, float]:
    """Load baseline metrics from configuration"""
    baseline = config.baseline_metrics or {}

    # Default baseline values if not set
    defaults = {
        "precision": 0.149,
        "recall": 0.099,
        "f1_score": 0.112,
        "faithfulness": 0.60,  # Target value
        "oracle_retrieval_hit_prefilter": 0.20,  # Target improvement
        "filter_hit_postfilter": 0.15,  # Target value
        "reader_used_gold": 0.10,  # Target value
        "latency_p95": 2.0,  # Target seconds
        "dedup_rate": 0.20,  # Target 20%
    }

    return {**defaults, **baseline}

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

def calculate_retrieval_metrics(eval_data: dict[str, Any]) -> dict[str, float]:
    """Calculate retrieval metrics from evaluation data"""
    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {}

    # Oracle retrieval hit prefilter
    oracle_hits = [case.get("oracle_retrieval_hit_prefilter", 0) for case in case_results]
    oracle_hit_rate = sum(oracle_hits) / len(oracle_hits) if oracle_hits else 0

    # Filter hit postfilter
    filter_hits = [case.get("filter_hit_postfilter", 0) for case in case_results]
    filter_hit_rate = sum(filter_hits) / len(filter_hits) if filter_hits else 0

    # Reader used gold
    reader_gold = [case.get("reader_used_gold", 0) for case in case_results]
    reader_gold_rate = sum(reader_gold) / len(reader_gold) if reader_gold else 0

    # Retrieval snapshot sizes
    snapshot_sizes = [len(case.get("retrieval_snapshot", [])) for case in case_results]
    avg_snapshot_size = sum(snapshot_sizes) / len(snapshot_sizes) if snapshot_sizes else 0
    max_snapshot_size = max(snapshot_sizes) if snapshot_sizes else 0

    return {
        "oracle_retrieval_hit_prefilter": oracle_hit_rate,
        "filter_hit_postfilter": filter_hit_rate,
        "reader_used_gold": reader_gold_rate,
        "avg_snapshot_size": avg_snapshot_size,
        "max_snapshot_size": max_snapshot_size,
    }

def calculate_end_metrics(eval_data: dict[str, Any]) -> dict[str, float]:
    """Calculate end-to-end metrics"""
    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {}

    # F1 score
    f1_scores = [case.get("f1_score", 0) for case in case_results]
    avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0

    # Precision
    precisions = [case.get("precision", 0) for case in case_results]
    avg_precision = sum(precisions) / len(precisions) if precisions else 0

    # Recall
    recalls = [case.get("recall", 0) for case in case_results]
    avg_recall = sum(recalls) / len(recalls) if recalls else 0

    # Faithfulness
    faithfulness_scores = [case.get("faithfulness", 0) for case in case_results]
    avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0

    return {
        "f1_score": avg_f1,
        "precision": avg_precision,
        "recall": avg_recall,
        "faithfulness": avg_faithfulness,
    }

def calculate_data_quality_metrics(eval_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate data quality metrics"""
    case_results = eval_data.get("case_results", [])
    if not case_results:
        return {}

    total_chunks = 0
    over_budget_chunks = 0
    bm25_with_prefix = 0
    max_embedding_tokens = 0
    max_bm25_tokens = 0

    for case in case_results:
        retrieval_snapshot = case.get("retrieval_snapshot", [])
        for chunk in retrieval_snapshot:
            total_chunks += 1

            # Token counts
            embedding_tokens = chunk.get("embedding_token_count", 0)
            bm25_tokens = chunk.get("bm25_token_count", 0)

            max_embedding_tokens = max(max_embedding_tokens, embedding_tokens)
            max_bm25_tokens = max(max_bm25_tokens, bm25_tokens)

            if embedding_tokens > 1024:
                over_budget_chunks += 1

            # Prefix leakage
            bm25_text = chunk.get("bm25_text", "")
            if bm25_text.startswith("Document:"):
                bm25_with_prefix += 1

    # Deduplication rate (placeholder - would need actual dedup data)
    dedup_rate = 0.20  # Placeholder

    return {
        "total_chunks": total_chunks,
        "over_budget_chunks": over_budget_chunks,
        "bm25_with_prefix": bm25_with_prefix,
        "max_embedding_tokens": max_embedding_tokens,
        "max_bm25_tokens": max_bm25_tokens,
        "dedup_rate": dedup_rate,
        "violation_rate": over_budget_chunks / total_chunks if total_chunks > 0 else 0,
        "prefix_leakage_rate": bm25_with_prefix / total_chunks if total_chunks > 0 else 0,
    }

def check_kpi_thresholds(current_metrics: dict[str, Any], baseline_metrics: dict[str, float]) -> dict[str, Any]:
    """Check KPI thresholds against baseline"""
    alerts = []
    warnings = []

    # Retrieval metrics (dev set)
    oracle_hit = current_metrics.get("oracle_retrieval_hit_prefilter", 0)
    baseline_oracle = baseline_metrics.get("oracle_retrieval_hit_prefilter", 0.20)

    if oracle_hit < baseline_oracle:
        alerts.append(f"Oracle retrieval hit rate below baseline: {oracle_hit:.3f} < {baseline_oracle:.3f}")
    elif oracle_hit >= baseline_oracle + 0.05:  # +5 points improvement
        print(f"✅ Oracle retrieval hit rate improved: {oracle_hit:.3f} (baseline: {baseline_oracle:.3f})")

    filter_hit = current_metrics.get("filter_hit_postfilter", 0)
    baseline_filter = baseline_metrics.get("filter_hit_postfilter", 0.15)

    if filter_hit < baseline_filter:
        alerts.append(f"Filter hit rate below baseline: {filter_hit:.3f} < {baseline_filter:.3f}")

    reader_gold = current_metrics.get("reader_used_gold", 0)
    baseline_reader = baseline_metrics.get("reader_used_gold", 0.10)

    if reader_gold < baseline_reader:
        alerts.append(f"Reader gold usage below baseline: {reader_gold:.3f} < {baseline_reader:.3f}")

    # End metrics
    f1_score = current_metrics.get("f1_score", 0)
    baseline_f1 = baseline_metrics.get("f1_score", 0.112)

    if f1_score < baseline_f1:
        alerts.append(f"F1 score below baseline: {f1_score:.3f} < {baseline_f1:.3f}")

    precision = current_metrics.get("precision", 0)
    baseline_precision = baseline_metrics.get("precision", 0.149)

    if precision < baseline_precision - 0.02:  # 2 point drift
        alerts.append(f"Precision drift too high: {precision:.3f} < {baseline_precision - 0.02:.3f}")

    # Data quality
    data_quality = current_metrics.get("data_quality", {})
    if not isinstance(data_quality, dict):
        data_quality = {}
    over_budget = data_quality.get("over_budget_chunks", 0)

    if over_budget > 0:
        alerts.append(f"Token budget violations: {over_budget} chunks over 1024 tokens")

    prefix_leakage = data_quality.get("bm25_with_prefix", 0)
    if prefix_leakage > 0:
        alerts.append(f"Prefix leakage: {prefix_leakage} chunks with 'Document:' prefix in BM25")

    dedup_rate = data_quality.get("dedup_rate", 0)
    if dedup_rate < 0.10 or dedup_rate > 0.35:
        warnings.append(f"Dedup rate outside target range: {dedup_rate:.2f} (expected 0.10-0.35)")

    return {
        "alerts": alerts,
        "warnings": warnings,
        "promote_ready": len(alerts) == 0,
    }

def generate_kpi_report(
    config: LockedConfig, eval_data: dict[str, Any], baseline_metrics: dict[str, float]
) -> dict[str, Any]:
    """Generate comprehensive KPI report"""

    # Calculate current metrics
    retrieval_metrics = calculate_retrieval_metrics(eval_data)
    end_metrics = calculate_end_metrics(eval_data)
    data_quality_metrics = calculate_data_quality_metrics(eval_data)

    # Combine all metrics
    current_metrics = {
        **retrieval_metrics,
        **end_metrics,
        "data_quality": data_quality_metrics,
    }

    # Check thresholds
    threshold_check = check_kpi_thresholds(current_metrics, baseline_metrics)

    return {
        "timestamp": datetime.now().isoformat(),
        "config_version": config.chunk_version,
        "config_hash": config.get_config_hash(),
        "baseline_metrics": baseline_metrics,
        "current_metrics": current_metrics,
        "threshold_check": threshold_check,
        "promote_ready": threshold_check["promote_ready"],
        "summary": {
            "oracle_hit_rate": retrieval_metrics.get("oracle_retrieval_hit_prefilter", 0),
            "f1_score": end_metrics.get("f1_score", 0),
            "precision": end_metrics.get("precision", 0),
            "over_budget_chunks": data_quality_metrics.get("over_budget_chunks", 0),
            "prefix_leakage": data_quality_metrics.get("bm25_with_prefix", 0),
        },
    }

def main():
    parser = argparse.ArgumentParser(description="Monitor KPIs and check thresholds")
    parser.add_argument(
        "--results-dir", default="metrics/baseline_evaluations", help="Directory containing evaluation results"
    )
    parser.add_argument("--output", help="Output file for KPI report")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("--promote-check", action="store_true", help="Check if ready for promotion")

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

    # Load baseline metrics
    baseline_metrics = load_baseline_metrics(config)

    # Generate KPI report
    kpi_report = generate_kpi_report(config, eval_data, baseline_metrics)

    # Save report
    if args.output:
        with open(args.output, "w") as f:
            json.dump(kpi_report, f, indent=2)

    # Console output
    if not args.quiet:
        print("📊 KPI Monitor Report")
        print("=" * 40)
        print(f"Config: {config.chunk_version}")
        print(f"Promote Ready: {'✅' if kpi_report['promote_ready'] else '❌'}")

        # Show key metrics
        summary = kpi_report["summary"]
        print("\n📈 Key Metrics:")
        print(f"  Oracle Hit Rate: {summary['oracle_hit_rate']:.3f}")
        print(f"  F1 Score: {summary['f1_score']:.3f}")
        print(f"  Precision: {summary['precision']:.3f}")
        print(f"  Over Budget Chunks: {summary['over_budget_chunks']}")
        print(f"  Prefix Leakage: {summary['prefix_leakage']}")

        # Show alerts
        threshold_check = kpi_report["threshold_check"]
        if threshold_check["alerts"]:
            print("\n🚨 Alerts:")
            for alert in threshold_check["alerts"]:
                print(f"  {alert}")

        if threshold_check["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in threshold_check["warnings"]:
                print(f"  {warning}")

    # Exit with error code if not ready for promotion
    if args.promote_check and not kpi_report["promote_ready"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
