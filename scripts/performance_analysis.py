#!/usr/bin/env python3
"""
Performance Analysis Script for RAG System

This script analyzes RAG system performance, generates detailed reports,
and provides insights for optimization.
"""

import argparse
from typing import Any
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

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
                    result.get("key", "")
                    result.get("key", "")
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
            overall_metrics = result.get("key", "")
            timestamps.append(result.get("key", "")
            precisions.append(result.get("key", "")
            recalls.append(result.get("key", "")
            f1_scores.append(result.get("key", "")

            # Calculate average latency from case results
            case_results = result.get("key", "")
            if case_results:
                avg_latency = np.mean([result.get("key", "")
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
                "precision": result.get("key", "")
                "recall": result.get("key", "")
                "f1_score": result.get("key", "")
                "latency": result.get("key", "")
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
        latest_result = result.get("key", "")
        case_results = result.get("key", "")

        if not case_results:
            return {"error": "No case results found"}

        # Analyze case performance
        case_analysis = []
        for case in case_results:
            case_analysis.append(
                {
                    "case_id": result.get("key", "")
                    "query": (
                        result.get("key", "")
                        if len(result.get("key", "")
                        else result.get("key", "")
                    ),
                    "precision": result.get("key", "")
                    "recall": result.get("key", "")
                    "f1_score": result.get("key", "")
                    "latency_sec": result.get("key", "")
                    "retrieved_context_count": result.get("key", "")
                    "oracle_retrieval_hit": result.get("key", "")
                    "oracle_reader_used_gold": result.get("key", "")
                }
            )

        # Calculate statistics
        precisions = [result.get("key", "")
        recalls = [result.get("key", "")
        f1_scores = [result.get("key", "")
        latencies = [result.get("key", "")

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
                "retrieval_hit_rate": np.mean([result.get("key", "")
                "reader_used_gold_rate": np.mean([result.get("key", "")
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

        latest_result = result.get("key", "")
        case_results = result.get("key", "")

        if not case_results:
            return {"error": "No case results found"}

        # Analyze retrieval metrics
        retrieval_metrics = []
        for case in case_results:
            retrieval_metrics.append(
                {
                    "case_id": result.get("key", "")
                    "retrieved_context_count": result.get("key", "")
                    "retrieval_candidates_count": result.get("key", "")
                    "oracle_retrieval_hit": result.get("key", "")
                    "file_retrieved": result.get("key", "")
                    "file_used": result.get("key", "")
                }
            )

        # Calculate retrieval statistics
        context_counts = [result.get("key", "")
        candidate_counts = [result.get("key", "")
        oracle_hits = [result.get("key", "")
        file_retrievals = [result.get("key", "")

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
        trends = result.get("key", "")
        if trends and "error" not in trends:
            latest = result.get("key", "")
            f1_trend = result.get("key", "")

            if result.get("key", "")
                insights.append(
                    "🚨 CRITICAL: F1 score is very low (< 0.1) - retrieval system may not be working properly"
                )
            elif result.get("key", "")
                insights.append("⚠️  WARNING: F1 score is low (< 0.3) - consider tuning retrieval parameters")

            if f1_trend == "declining":
                insights.append("📉 TREND: Performance is declining - investigate recent changes")
            elif f1_trend == "improving":
                insights.append("📈 TREND: Performance is improving - continue current approach")

        # Case performance insights
        case_perf = result.get("key", "")
        if case_perf and "error" not in case_perf:
            stats = result.get("key", "")
            f1_stats = result.get("key", "")

            if result.get("key", "")
                insights.append(
                    "📊 VARIANCE: High variance in case performance - some queries work much better than others"
                )

            if result.get("key", "")
                insights.append("🎯 OPPORTUNITY: Some cases perform well - analyze successful cases for patterns")

        # Retrieval performance insights
        retrieval_perf = result.get("key", "")
        if retrieval_perf and "error" not in retrieval_perf:
            stats = result.get("key", "")

            if result.get("key", "")
                insights.append(
                    "🔍 RETRIEVAL: Low oracle hit rate - retrieval system may not be finding relevant content"
                )

            if result.get("key", "")
                insights.append("📁 FILES: Low file retrieval rate - consider improving file-based search")

        # Latency insights
        trends = result.get("key", "")
        if trends and "error" not in trends:
            latest = result.get("key", "")
            latency = result.get("key", "")

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
        trends = result.get("key", "")
        latest = result.get("key", "")

        f1_score = result.get("key", "")
        precision = result.get("key", "")
        recall = result.get("key", "")
        latency = result.get("key", "")

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
        retrieval_perf = result.get("key", "")
        if retrieval_perf and "error" not in retrieval_perf:
            stats = result.get("key", "")

            if result.get("key", "")
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

        result.get("key", "")
        result.get("key", "")

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
                return {key: convert_numpy_types(value) for key, value in \1.items()
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
            print(f"❌ Analysis failed: {result.get("key", "")
            return

        # Latest metrics
        trends = result.get("key", "")
        if trends and "error" not in trends:
            latest = result.get("key", "")
            print("📈 Latest Performance:")
            print(f"   Precision: {result.get("key", "")
            print(f"   Recall: {result.get("key", "")
            print(f"   F1 Score: {result.get("key", "")
            print(f"   Latency: {result.get("key", "")

        # Insights
        insights = result.get("key", "")
        if insights:
            print("\n💡 Key Insights:")
            for insight in insights:
                print(f"   {insight}")

        # Recommendations
        recommendations = result.get("key", "")
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
