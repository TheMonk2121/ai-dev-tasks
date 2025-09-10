#!/usr/bin/env python3
"""
Ingest Observability Script
- Comprehensive logging and metrics
- Performance monitoring
- Quality validation
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def log_ingest_metrics(file_path: str, metrics: dict[str, Any], config: dict[str, Any]) -> None:
    """Log comprehensive ingest metrics"""
    log_entry = {
        "timestamp": time.time(),
        "file_path": file_path,
        "config": config,
        "metrics": metrics,
        "quality_checks": {
            "budget_compliance": metrics.get("chunks_over_budget", 0) == 0,
            "token_efficiency": metrics.get("post_split_tokens_mean", 0) / metrics.get("pre_split_tokens", 1),
            "processing_speed": metrics.get("time_per_1k_tokens", 0),
        },
    }

    # Log to file for analysis
    log_file = Path("logs/ingest_observability.jsonl")
    log_file.parent.mkdir(exist_ok=True)

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def validate_chunking_quality() -> dict[str, Any]:
    """Validate overall chunking quality"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get chunk statistics
            cur.execute(
                """
                SELECT
                    COUNT(*) as total_chunks,
                    AVG(embedding_token_count) as avg_embedding_tokens,
                    AVG(bm25_token_count) as avg_bm25_tokens,
                    MAX(embedding_token_count) as max_embedding_tokens,
                    MIN(embedding_token_count) as min_embedding_tokens,
                    COUNT(CASE WHEN embedding_token_count > 512 THEN 1 END) as chunks_over_budget,
                    COUNT(CASE WHEN chunk_id IS NOT NULL THEN 1 END) as chunks_with_id
                FROM document_chunks
                WHERE embedding_token_count IS NOT NULL
            """
            )

            stats = cur.fetchone()

            # Get content type distribution
            cur.execute(
                """
                SELECT
                    (metadata->>'content_type') as content_type,
                    COUNT(*) as count,
                    AVG(embedding_token_count) as avg_tokens
                FROM document_chunks
                WHERE embedding_token_count IS NOT NULL
                GROUP BY (metadata->>'content_type')
            """
            )

            content_types = cur.fetchall()

            # Get deduplication stats
            cur.execute(
                """
                SELECT
                    COUNT(DISTINCT chunk_id) as unique_chunks,
                    COUNT(*) as total_chunks,
                    (COUNT(*) - COUNT(DISTINCT chunk_id)) as duplicates
                FROM document_chunks
                WHERE chunk_id IS NOT NULL
            """
            )

            dedup_stats = cur.fetchone()

    return {
        "chunk_statistics": {
            "total_chunks": stats[0] if stats and len(stats) > 0 else 0,
            "avg_embedding_tokens": float(stats[1]) if stats and len(stats) > 1 and stats[1] else 0,
            "avg_bm25_tokens": float(stats[2]) if stats and len(stats) > 2 and stats[2] else 0,
            "max_embedding_tokens": stats[3] if stats and len(stats) > 3 else 0,
            "min_embedding_tokens": stats[4] if stats and len(stats) > 4 else 0,
            "chunks_over_budget": stats[5] if stats and len(stats) > 5 else 0,
            "chunks_with_id": stats[6] if stats and len(stats) > 6 else 0,
            "budget_compliance_rate": 1 - (stats[5] / stats[0]) if stats and len(stats) > 5 and stats[0] > 0 else 1,
        },
        "content_type_distribution": [
            {"type": row[0], "count": row[1], "avg_tokens": float(row[2]) if row[2] else 0} for row in content_types
        ],
        "deduplication_stats": {
            "unique_chunks": dedup_stats[0] if dedup_stats and len(dedup_stats) > 0 else 0,
            "total_chunks": dedup_stats[1] if dedup_stats and len(dedup_stats) > 1 else 0,
            "duplicates": dedup_stats[2] if dedup_stats and len(dedup_stats) > 2 else 0,
            "dedup_rate": (
                dedup_stats[2] / dedup_stats[1] if dedup_stats and len(dedup_stats) > 2 and dedup_stats[1] > 0 else 0
            ),
        },
    }


def monitor_ingest_performance() -> dict[str, Any]:
    """Monitor ingest performance metrics"""
    log_file = Path("logs/ingest_observability.jsonl")

    if not log_file.exists():
        return {"error": "No ingest logs found"}

    # Read recent logs
    recent_logs = []
    with open(log_file) as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                # Only include logs from last 24 hours
                if time.time() - log_entry["timestamp"] < 86400:
                    recent_logs.append(log_entry)
            except json.JSONDecodeError:
                continue

    if not recent_logs:
        return {"error": "No recent logs found"}

    # Calculate performance metrics
    processing_times = [log["metrics"]["processing_time"] for log in recent_logs]
    token_counts = [log["metrics"]["pre_split_tokens"] for log in recent_logs]
    chunk_counts = [log["metrics"]["chunk_count"] for log in recent_logs]

    return {
        "recent_ingests": len(recent_logs),
        "avg_processing_time": sum(processing_times) / len(processing_times),
        "avg_tokens_per_second": sum(token_counts) / sum(processing_times) if sum(processing_times) > 0 else 0,
        "avg_chunks_per_second": sum(chunk_counts) / sum(processing_times) if sum(processing_times) > 0 else 0,
        "total_tokens_processed": sum(token_counts),
        "total_chunks_created": sum(chunk_counts),
        "quality_compliance": sum(1 for log in recent_logs if log["quality_checks"]["budget_compliance"])
        / len(recent_logs),
    }


def generate_health_report() -> dict[str, Any]:
    """Generate comprehensive health report"""
    print("Generating ingest health report...")

    quality_metrics = validate_chunking_quality()
    performance_metrics = monitor_ingest_performance()

    report = {
        "timestamp": time.time(),
        "quality_metrics": quality_metrics,
        "performance_metrics": performance_metrics,
        "health_status": (
            "healthy" if quality_metrics["chunk_statistics"]["budget_compliance_rate"] > 0.95 else "warning"
        ),
    }

    # Save report
    report_file = Path("logs/ingest_health_report.json")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    return report


def print_health_summary(report: dict[str, Any]) -> None:
    """Print human-readable health summary"""
    print("\n" + "=" * 60)
    print("INGEST HEALTH REPORT")
    print("=" * 60)

    quality = report["quality_metrics"]
    performance = report["performance_metrics"]

    print(f"Health Status: {report['health_status'].upper()}")
    print()

    print("CHUNK QUALITY:")
    stats = quality["chunk_statistics"]
    print(f"  Total chunks: {stats['total_chunks']:,}")
    print(f"  Avg embedding tokens: {stats['avg_embedding_tokens']:.1f}")
    print(f"  Avg BM25 tokens: {stats['avg_bm25_tokens']:.1f}")
    print(f"  Max embedding tokens: {stats['max_embedding_tokens']}")
    print(f"  Chunks over budget: {stats['chunks_over_budget']}")
    print(f"  Budget compliance: {stats['budget_compliance_rate']:.1%}")
    print(f"  Chunks with stable IDs: {stats['chunks_with_id']:,}")

    print("\nCONTENT TYPE DISTRIBUTION:")
    for ct in quality["content_type_distribution"]:
        print(f"  {ct['type']}: {ct['count']:,} chunks, {ct['avg_tokens']:.1f} avg tokens")

    print("\nDEDUPLICATION:")
    dedup = quality["deduplication_stats"]
    print(f"  Unique chunks: {dedup['unique_chunks']:,}")
    print(f"  Duplicates: {dedup['duplicates']:,}")
    print(f"  Dedup rate: {dedup['dedup_rate']:.1%}")

    if "error" not in performance:
        print("\nPERFORMANCE (Last 24h):")
        print(f"  Recent ingests: {performance['recent_ingests']}")
        print(f"  Avg processing time: {performance['avg_processing_time']:.2f}s")
        print(f"  Tokens per second: {performance['avg_tokens_per_second']:.0f}")
        print(f"  Chunks per second: {performance['avg_chunks_per_second']:.1f}")
        print(f"  Total tokens processed: {performance['total_tokens_processed']:,}")
        print(f"  Quality compliance: {performance['quality_compliance']:.1%}")

    print("\nRECOMMENDATIONS:")
    if stats["budget_compliance_rate"] < 0.95:
        print("  ⚠️  Budget compliance below 95% - review chunk size settings")
    if dedup["dedup_rate"] > 0.1:
        print("  ⚠️  High dedup rate - may be too aggressive")
    if performance.get("avg_tokens_per_second", 0) < 1000:
        print("  ⚠️  Low processing speed - consider optimization")

    if stats["budget_compliance_rate"] >= 0.95 and dedup["dedup_rate"] <= 0.1:
        print("  ✅ All quality metrics look good!")


def main():
    """Main observability function"""
    load_dotenv()

    parser = argparse.ArgumentParser("Ingest Observability")
    parser.add_argument("--report", action="store_true", help="Generate health report")
    parser.add_argument("--monitor", action="store_true", help="Monitor performance")
    parser.add_argument("--validate", action="store_true", help="Validate chunking quality")
    args = parser.parse_args()

    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL not set")
        sys.exit(1)

    if args.report or (not args.monitor and not args.validate):
        report = generate_health_report()
        print_health_summary(report)

    if args.monitor:
        metrics = monitor_ingest_performance()
        print("Performance Metrics:")
        print(json.dumps(metrics, indent=2))

    if args.validate:
        quality = validate_chunking_quality()
        print("Quality Metrics:")
        print(json.dumps(quality, indent=2))


if __name__ == "__main__":
    main()
