#!/usr/bin/env python3
"""
Evaluation Analytics Dashboard

This script provides comprehensive analytics and insights from our TimescaleDB
evaluation data, leveraging the enhanced continuous aggregates and views.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.common.db_dsn import resolve_dsn


class EvaluationAnalytics:
    """Analytics engine for evaluation data."""

    def __init__(self):
        self.dsn = resolve_dsn(strict=False)
        if not self.dsn or self.dsn.startswith("mock://"):
            raise ValueError("No real database connection available")

        self.conn = psycopg.connect(self.dsn)
        try:
            self.conn.row_factory = dict_row  # type: ignore[attr-defined]
        except Exception:
            pass
        self.cursor = self.conn.cursor()

    def get_performance_trends(self, days: int = 7):
        """Get performance trends over time."""
        query = f"""
        SELECT
            day,
            tag,
            model,
            ok_cases,
            f1_avg,
            p50_latency_ms,
            f1_change,
            latency_change
        FROM evaluation_performance_trends
        WHERE day >= CURRENT_DATE - INTERVAL '{days} days'
        ORDER BY day DESC, tag, model;
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_quality_metrics(self, limit: int = 10):
        """Get quality metrics for recent evaluations."""
        query = f"""
        SELECT
            run_id,
            tag,
            model,
            started_at,
            duration_seconds,
            total_cases,
            successful_cases,
            avg_f1,
            avg_precision,
            avg_recall,
            avg_latency_ms
        FROM evaluation_quality_metrics
        ORDER BY started_at DESC
        LIMIT {limit};
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_performance_alerts(self, days: int = 7):
        """Get performance degradation alerts."""
        query = f"""
        SELECT
            tag,
            model,
            day,
            f1_avg,
            prev_f1_avg,
            f1_delta,
            alert_type
        FROM performance_degradation_alerts
        WHERE day >= CURRENT_DATE - INTERVAL '{days} days'
        AND alert_type IS NOT NULL
        ORDER BY day DESC, tag, model;
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_hourly_metrics(self, hours: int = 24):
        """Get hourly metrics for detailed analysis."""
        query = f"""
        SELECT
            hour,
            tag,
            model,
            stage,
            ok_cases,
            f1_avg,
            f1_min,
            f1_max,
            p50_latency_ms,
            min_latency_ms,
            max_latency_ms,
            precision_avg,
            recall_avg,
            faithfulness_avg
        FROM eval_hourly
        WHERE hour >= NOW() - INTERVAL '{hours} hours'
        ORDER BY hour DESC, tag, model, stage;
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_weekly_summary(self, weeks: int = 4):
        """Get weekly summary statistics."""
        query = f"""
        SELECT
            week,
            tag,
            model,
            ok_cases,
            f1_avg,
            f1_stddev,
            p50_latency_ms,
            p95_latency_ms,
            total_cases,
            precision_avg,
            recall_avg,
            faithfulness_avg
        FROM eval_weekly
        WHERE week >= NOW() - INTERVAL '{weeks} weeks'
        ORDER BY week DESC, tag, model;
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_model_comparison(self, days: int = 7):
        """Compare performance across different models."""
        query = f"""
        SELECT
            model,
            tag,
            COUNT(*) as total_runs,
            AVG(f1_avg) as avg_f1,
            STDDEV(f1_avg) as f1_stddev,
            AVG(p50_latency_ms) as avg_latency,
            AVG(precision_avg) as avg_precision,
            AVG(recall_avg) as avg_recall,
            AVG(faithfulness_avg) as avg_faithfulness
        FROM eval_daily
        WHERE day >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY model, tag
        ORDER BY avg_f1 DESC;
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_profile_analysis(self, days: int = 7):
        """Analyze performance by evaluation profile."""
        query = f"""
        SELECT
            tag as profile,
            COUNT(*) as total_runs,
            AVG(f1_avg) as avg_f1,
            MIN(f1_avg) as min_f1,
            MAX(f1_avg) as max_f1,
            AVG(p50_latency_ms) as avg_latency,
            AVG(ok_cases) as avg_successful_cases
        FROM eval_daily
        WHERE day >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY tag
        ORDER BY avg_f1 DESC;
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def print_performance_trends(analytics: EvaluationAnalytics, days: int = 7):
    """Print performance trends."""
    print(f"\n📈 Performance Trends (Last {days} days)")
    print("=" * 60)

    trends = analytics.get_performance_trends(days)

    if not trends:
        print("No data available")
        return

    for trend in trends[:10]:  # Show last 10
        print(f"📅 {result.get("key", "")
        print(
            f"   F1: {result.get("key", "")
        )
        print(f"   Cases: {result.get("key", "")
        print()


def print_quality_metrics(analytics: EvaluationAnalytics, limit: int = 5):
    """Print quality metrics."""
    print(f"\n🎯 Quality Metrics (Last {limit} evaluations)")
    print("=" * 80)

    metrics = analytics.get_quality_metrics(limit)

    if not metrics:
        print("No data available")
        return

    for metric in metrics:
        print(f"🔍 {result.get("key", "")
        print(
            f"   Duration: {result.get("key", "")
        )
        print(
            f"   F1: {result.get("key", "")
        )
        print(f"   Latency: {result.get("key", "")
        print()


def print_performance_alerts(analytics: EvaluationAnalytics, days: int = 7):
    """Print performance alerts."""
    print(f"\n🚨 Performance Alerts (Last {days} days)")
    print("=" * 60)

    alerts = analytics.get_performance_alerts(days)

    if not alerts:
        print("✅ No performance alerts")
        return

    for alert in alerts:
        print(f"⚠️  {result.get("key", "")
        print(f"   Alert: {result.get("key", "")
        print(f"   F1: {result.get("key", "")
        print()


def print_model_comparison(analytics: EvaluationAnalytics, days: int = 7):
    """Print model comparison."""
    print(f"\n🤖 Model Comparison (Last {days} days)")
    print("=" * 80)

    comparison = analytics.get_model_comparison(days)

    if not comparison:
        print("No data available")
        return

    for model in comparison:
        print(f"🔧 {result.get("key", "")
        print(f"   Runs: {result.get("key", "")
        print(
            f"   Latency: {result.get("key", "")
        )
        print(f"   Faithfulness: {result.get("key", "")
        print()


def print_profile_analysis(analytics: EvaluationAnalytics, days: int = 7):
    """Print profile analysis."""
    print(f"\n📊 Profile Analysis (Last {days} days)")
    print("=" * 60)

    analysis = analytics.get_profile_analysis(days)

    if not analysis:
        print("No data available")
        return

    for profile in analysis:
        print(f"🎯 {result.get("key", "")
        print(
            f"   Runs: {result.get("key", "")
        )
        print(f"   Latency: {result.get("key", "")
        print()


def main():
    """Main entry point."""
    print("📊 Evaluation Analytics Dashboard")
    print("=" * 50)

    try:
        analytics = EvaluationAnalytics()

        # Print various analytics
        print_performance_trends(analytics, days=7)
        print_quality_metrics(analytics, limit=5)
        print_performance_alerts(analytics, days=7)
        print_model_comparison(analytics, days=7)
        print_profile_analysis(analytics, days=7)

        print("\n✅ Analytics dashboard completed!")
        print("\n💡 Tips:")
        print("  - Use Logfire dashboard for real-time monitoring")
        print("  - Set up alerts for performance degradation")
        print("  - Monitor trends over time for optimization opportunities")

    except Exception as e:
        print(f"❌ Analytics dashboard failed: {e}")
        sys.exit(1)
    finally:
        if "analytics" in locals():
            analytics.close()


if __name__ == "__main__":
    main()
