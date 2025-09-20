#!/usr/bin/env python3
"""
Performance Analysis Script for RAG System

This script analyzes RAG system performance, generates detailed reports,
and provides insights for optimization.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().result.get("key", "")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


class PerformanceAnalyzer:
    """Comprehensive performance analysis for RAG system."""

    def __init__(self, profile: str = "real"):
        self.profile = profile
        self.results_dir = Path("metrics/performance_analysis")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Analysis results
        self.analysis_results: dict[str, Any] = {}

    def load_evaluation_results(self, results_dir: str = "evals/metrics/dspy_evaluations") -> list[dict[str, Any]]:
        """Load recent evaluation results for analysis."""
        results_path = Path(results_dir)
        if not results_path.exists():
            print(f"❌ Results directory not found: {results_dir}")
            return []

        # Find most recent evaluation files
        eval_files = list(results_path.glob("dspy_evaluation_*.json"))
        if not eval_files:
            print(f"❌ No evaluation files found in {results_dir}")
            return []

        # Sort by modification time and take last 5
        eval_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        recent_files = eval_files[:5]

        results = []
        for file_path in recent_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    results.append(data)
            except Exception as e:
                print(f"⚠️  Failed to load {file_path}: {e}")
                continue

        print(f"📊 Loaded {len(results)} evaluation results")
        return results

    def analyze_metrics_trends(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze trends in evaluation metrics over time."""
        if not results:
            return {"error": "No results to analyze"}

        # Extract metrics over time
        timestamps = []
        precisions = []
        recalls = []
        f1_scores = []
        latencies = []

        for result in results:
            overall_metrics = result.get("overall_metrics", {})
            timestamps.append(result.get("timestamp", datetime.now()))
            precisions.append(overall_metrics.get("precision", 0.0))
            recalls.append(overall_metrics.get("recall", 0.0))
            f1_scores.append(overall_metrics.get("f1_score", 0.0))

            # Calculate average latency from case results
            case_results = result.get("case_results", [])
            if case_results:
                avg_latency = np.mean([case.get("latency_ms", 0.0) for case in case_results])
                latencies.append(avg_latency)
            else:
                latencies.append(0.0)

        # Calculate trends
        trends = {
            "precision_trend": self._calculate_trend(precisions),
            "recall_trend": self._calculate_trend(recalls),
            "f1_trend": self._calculate_trend(f1_scores),
            "latency_trend": self._calculate_trend(latencies),
            "latest_metrics": {
                "precision": precisions[-1] if precisions else 0.0,
                "recall": recalls[-1] if recalls else 0.0,
                "f1_score": f1_scores[-1] if f1_scores else 0.0,
                "latency": latencies[-1] if latencies else 0.0
            },
            "historical_data": {
                "timestamps": timestamps,
                "precisions": precisions,
                "recalls": recalls,
                "f1_scores": f1_scores,
                "latencies": latencies,
            },
        }

        return trends

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear trend calculation
        x = np.arange(len(values))
        y = np.array(values)

        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]

        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"

    def analyze_case_performance(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze performance by individual test cases."""
        if not results:
            return {"error": "No results to analyze"}

        # Use most recent result for case analysis
        latest_result = results[-1] if results else {}
        case_results = latest_result.get("case_results", [])

        if not case_results:
            return {"error": "No case results found"}

        # Analyze case performance
        case_analysis = []
        for case in case_results:
            case_analysis.append(
                {
                    "case_id": case.get("case_id", "unknown"),
                    "query": (
                        case.get("query", "")[:50] + "..."
                        if len(case.get("query", "")) > 50
                        else case.get("query", "")
                    ),
                    "precision": case.get("precision", 0.0),
                    "recall": case.get("recall", 0.0),
                    "f1_score": case.get("f1_score", 0.0),
                    "latency_sec": case.get("latency_ms", 0.0) / 1000.0,
                    "retrieved_context_count": case.get("retrieved_context_count", 0),
                    "oracle_retrieval_hit": case.get("oracle_retrieval_hit", False),
                    "oracle_reader_used_gold": case.get("oracle_reader_used_gold", False)
                }
            )

        # Calculate statistics
        precisions = [case["precision"] for case in case_analysis]
        recalls = [case["recall"] for case in case_analysis]
        f1_scores = [case["f1_score"] for case in case_analysis]
        latencies = [case["latency_sec"] for case in case_analysis]

        stats = {
            "total_cases": len(case_analysis),
            "precision_stats": {
                "mean": np.mean(precisions),
                "std": np.std(precisions),
                "min": np.min(precisions),
                "max": np.max(precisions),
            },
            "recall_stats": {
                "mean": np.mean(recalls),
                "std": np.std(recalls),
                "min": np.min(recalls),
                "max": np.max(recalls),
            },
            "f1_stats": {
                "mean": np.mean(f1_scores),
                "std": np.std(f1_scores),
                "min": np.min(f1_scores),
                "max": np.max(f1_scores),
            },
            "latency_stats": {
                "mean": np.mean(latencies),
                "std": np.std(latencies),
                "min": np.min(latencies),
                "max": np.max(latencies),
            },
            "oracle_stats": {
                "retrieval_hit_rate": np.mean([case["oracle_retrieval_hit"] for case in case_analysis]),
                "reader_used_gold_rate": np.mean([case["oracle_reader_used_gold"] for case in case_analysis])
            },
        }

        return {
            "case_analysis": case_analysis,
            "statistics": stats,
        }

    def analyze_retrieval_performance(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze retrieval system performance."""
        if not results:
            return {"error": "No results to analyze"}

        latest_result = results[-1] if results else {}
        case_results = latest_result.get("case_results", [])

        if not case_results:
            return {"error": "No case results found"}

        # Analyze retrieval metrics
        retrieval_metrics = []
        for case in case_results:
            retrieval_metrics.append(
                {
                    "case_id": case.get("case_id", "unknown"),
                    "retrieved_context_count": case.get("retrieved_context_count", 0),
                    "retrieval_candidates_count": case.get("retrieval_candidates_count", 0),
                    "oracle_retrieval_hit": case.get("oracle_retrieval_hit", False),
                    "file_retrieved": case.get("file_retrieved", ""),
                    "file_used": case.get("file_used", "")
                }
            )

        # Calculate retrieval statistics
        context_counts = [case["retrieved_context_count"] for case in retrieval_metrics]
        candidate_counts = [case["retrieval_candidates_count"] for case in retrieval_metrics]
        oracle_hits = [case["oracle_retrieval_hit"] for case in retrieval_metrics]
        file_retrievals = [case["file_retrieved"] for case in retrieval_metrics]

        stats = {
            "context_count_stats": {
                "mean": np.mean(context_counts),
                "std": np.std(context_counts),
                "min": np.min(context_counts),
                "max": np.max(context_counts),
            },
            "candidate_count_stats": {
                "mean": np.mean(candidate_counts),
                "std": np.std(candidate_counts),
                "min": np.min(candidate_counts),
                "max": np.max(candidate_counts),
            },
            "oracle_hit_rate": np.mean(oracle_hits),
            "file_retrieval_rate": np.mean(file_retrievals),
        }

        return {
            "retrieval_metrics": retrieval_metrics,
            "statistics": stats,
        }

    def generate_insights(self, analysis_results: dict[str, Any]) -> list[str]:
        """Generate actionable insights from analysis results."""
        insights = []

        # Metrics trend insights
        trends = analysis_results.get("trends", {})
        if trends and "error" not in trends:
            latest = trends.get("latest_metrics", {})
            f1_trend = trends.get("f1_trend", "stable")

            if f1_trend == "improving":
                insights.append("✅ F1 score is improving - keep current configuration")
            elif latest.get("f1_score", 0.0) < 0.1:
                insights.append(
                    "🚨 CRITICAL: F1 score is very low (< 0.1) - retrieval system may not be working properly"
                )
            elif latest.get("f1_score", 0.0) < 0.3:
                insights.append("⚠️  WARNING: F1 score is low (< 0.3) - consider tuning retrieval parameters")

            if f1_trend == "declining":
                insights.append("📉 TREND: Performance is declining - investigate recent changes")
            elif f1_trend == "improving":
                insights.append("📈 TREND: Performance is improving - continue current approach")

        # Case performance insights
        case_perf = analysis_results.get("case_performance", {})
        if case_perf and "error" not in case_perf:
            stats = case_perf.get("statistics", {})
            f1_stats = stats.get("f1_stats", {})

            if f1_stats.get("std", 0.0) > 0.2:
                insights.append(
                    "📊 VARIANCE: High variance in case performance - some queries work much better than others"
                )

            if f1_stats.get("max", 0.0) > 0.7:
                insights.append("🎯 OPPORTUNITY: Some cases perform well - analyze successful cases for patterns")

        # Retrieval performance insights
        retrieval_perf = analysis_results.get("retrieval_performance", {})
        if retrieval_perf and "error" not in retrieval_perf:
            stats = retrieval_perf.get("statistics", {})

            if stats.get("oracle_hit_rate", 0.0) < 0.3:
                insights.append(
                    "🔍 RETRIEVAL: Low oracle hit rate - retrieval system may not be finding relevant content"
                )

            if stats.get("file_retrieval_rate", 0.0) < 0.5:
                insights.append("📁 FILES: Low file retrieval rate - consider improving file-based search")

        # Latency insights
        trends = analysis_results.get("trends", {})
        if trends and "error" not in trends:
            latest = trends.get("latest_metrics", {})
            latency = latest.get("latency", 0.0)

            if latency > 5.0:
                insights.append(
                    "⏱️  LATENCY: High latency (>5s) - consider optimizing retrieval or reducing context size"
                )
            elif latency > 2.0:
                insights.append("⏱️  LATENCY: Moderate latency (>2s) - monitor for performance degradation")

        return insights

    def generate_recommendations(self, analysis_results: dict[str, Any]) -> list[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []

        # Get latest metrics
        trends = analysis_results.get("trends", {})
        latest = trends.get("latest_metrics", {}) if trends else {}

        f1_score = latest.get("f1_score", 0.0)
        precision = latest.get("precision", 0.0)
        recall = latest.get("recall", 0.0)
        latency = latest.get("latency", 0.0)

        # F1 score recommendations
        if f1_score < 0.1:
            recommendations.extend(
                [
                    "🔧 URGENT: Check if database has relevant content for test queries",
                    "🔧 URGENT: Verify embedding model is working correctly",
                    "🔧 URGENT: Check retrieval parameters (RETR_TOPK_VEC, RETR_TOPK_BM25)",
                ]
            )
        elif f1_score < 0.3:
            recommendations.extend(
                [
                    "🔧 TUNE: Increase retrieval top-k values (RETR_TOPK_VEC, RETR_TOPK_BM25)",
                    "🔧 TUNE: Enable reranking (RERANK_ENABLE=1)",
                    "🔧 TUNE: Adjust fusion weights for better retrieval",
                ]
            )

        # Precision vs Recall recommendations
        if precision < 0.1 and recall < 0.1:
            recommendations.append(
                "🔧 RETRIEVAL: Both precision and recall are low - check if retrieval is working at all"
            )
        elif precision < recall * 0.5:
            recommendations.append(
                "🔧 PRECISION: Precision much lower than recall - consider stricter filtering or better reranking"
            )
        elif recall < precision * 0.5:
            recommendations.append(
                "🔧 RECALL: Recall much lower than precision - consider increasing retrieval pool size"
            )

        # Latency recommendations
        if latency > 5.0:
            recommendations.extend(
                [
                    "⚡ LATENCY: Reduce EVAL_CONCURRENCY to decrease load",
                    "⚡ LATENCY: Lower BEDROCK_MAX_RPS to avoid throttling",
                    "⚡ LATENCY: Reduce RERANK_POOL size for faster processing",
                ]
            )

        # Retrieval-specific recommendations
        retrieval_perf = analysis_results.get("retrieval_performance", {})
        if retrieval_perf and "error" not in retrieval_perf:
            stats = retrieval_perf.get("stats", {})

            if stats.get("precision", 0) < 0.5:
                recommendations.extend(
                    [
                        "🔍 RETRIEVAL: Check if document chunks contain relevant information",
                        "🔍 RETRIEVAL: Verify embedding similarity search is working",
                        "🔍 RETRIEVAL: Consider adjusting query preprocessing",
                    ]
                )

        return recommendations

    def run_analysis(self) -> dict[str, Any]:
        """Run comprehensive performance analysis."""
        print("📊 Starting performance analysis...")

        # Load evaluation results
        results = self.load_evaluation_results()
        if not results:
            return {"error": "No evaluation results found"}

        # Run analyses
        print("📈 Analyzing metrics trends...")
        metrics_trends = self.analyze_metrics_trends(results)

        print("📋 Analyzing case performance...")
        case_performance = self.analyze_case_performance(results)

        print("🔍 Analyzing retrieval performance...")
        retrieval_performance = self.analyze_retrieval_performance(results)

        # Compile results
        analysis_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "profile": self.profile,
            "evaluations_analyzed": len(results),
            "metrics_trends": metrics_trends,
            "case_performance": case_performance,
            "retrieval_performance": retrieval_performance,
        }

        # Generate insights and recommendations
        print("💡 Generating insights...")
        insights = self.generate_insights(analysis_results)
        recommendations = self.generate_recommendations(analysis_results)

        self.analysis_results = analysis_results
        return analysis_results

    def save_results(self, results: dict[str, Any]) -> str:
        """Save analysis results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"performance_analysis_{timestamp}.json"

        # Convert numpy types to Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj

        # Convert numpy types in results
        converted_results = convert_numpy_types(results)

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(converted_results, f, indent=2, ensure_ascii=False)

        print(f"📁 Analysis results saved to: {results_file}")
        return str(results_file)

    def print_summary(self, results: dict[str, Any]) -> None:
        """Print analysis summary to console."""
        print("\n📊 PERFORMANCE ANALYSIS SUMMARY")
        print("=" * 60)

        if "error" in results:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return

        # Latest metrics
        trends = results.get("metrics_trends", {})
        if trends and "error" not in trends:
            latest = trends.get("latest", {})
            print("📈 Latest Performance:")
            print(f"   Precision: {latest.get('precision', 0.0):.3f}")
            print(f"   Recall: {latest.get('recall', 0.0):.3f}")
            print(f"   F1 Score: {latest.get('f1_score', 0.0):.3f}")
            print(f"   Latency: {latest.get('latency', 0.0):.3f}s")

        # Insights
        insights = results.get("insights", [])
        if insights:
            print("\n💡 Key Insights:")
            for insight in insights:
                print(f"   {insight}")

        # Recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            print("\n🔧 Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RAG System Performance Analysis")
    parser.add_argument("--profile", default="real", help="Evaluation profile")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    print("📊 RAG SYSTEM PERFORMANCE ANALYSIS")
    print("=" * 50)
    print(f"Profile: {args.profile}")
    print()

    # Initialize analyzer
    analyzer = PerformanceAnalyzer(profile=args.profile)

    # Run analysis
    results = analyzer.run_analysis()

    # Save results
    results_file = analyzer.save_results(results)

    # Print summary
    analyzer.print_summary(results)

    print(f"\n📁 Detailed analysis saved to: {results_file}")

    # Exit with error code if analysis failed
    if "error" in results:
        sys.exit(1)


if __name__ == "__main__":
    main()
