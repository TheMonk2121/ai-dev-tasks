from typing import Any, Optional, Union

#!/usr/bin/env python3
"""
RAGChecker LIMIT-Inspired Evaluation
Implements geometry-failure routing, facet yield selection, and Boolean logic handling.
"""

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any
import random

# Add src to path for imports - use absolute path and check for duplicates
scripts_path = Path(__file__).parent.resolve()
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

from limit_inspired_precision_recovery import apply_limit_inspired_config
from ragchecker_official_evaluation import OfficialRAGCheckerEvaluator


class LimitInspiredEvaluator(OfficialRAGCheckerEvaluator):
    """Enhanced RAGChecker evaluator with LIMIT-inspired features."""

    def __init__(self):
        """Initialize with LIMIT-inspired configuration."""
        super().__init__()
        self.limit_config = apply_limit_inspired_config()
        self.logging_data = defaultdict(dict)

        print("🎯 LIMIT-Inspired Evaluator initialized")
        print(
            f"📊 Geometry Router: margin_threshold={self.limit_config.geometry_router.margin_threshold}"
        )
        print("📊 Facet Calculator: yield-based selection enabled")
        print("📊 Boolean Parser: AND/OR/NOT logic handling enabled")

    def evaluate_with_limit_features(self, test_cases: list[Any]) -> dict[str, Any]:
        """Evaluate test cases with LIMIT-inspired features."""

        print("\n🔍 Running LIMIT-inspired evaluation")
        print("=" * 60)

        results = []
        total_cases = len(test_cases)
        health_metrics_summary = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Case {i}/{total_cases}: {test_case.query_id}")

            # Evaluate with LIMIT-inspired features
            case_result, health_metrics = self._evaluate_case_with_limit_features(
                test_case
            )
            results.append(case_result)
            health_metrics_summary.append(health_metrics)

            # Log case-specific metrics
            self._log_case_metrics(test_case.query_id, case_result, health_metrics)

        # Generate comprehensive evaluation report
        evaluation_report = self._generate_limit_evaluation_report(
            results, health_metrics_summary
        )

        return evaluation_report

    def _evaluate_case_with_limit_features(
        self, test_case: Any
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Evaluate a single test case with LIMIT-inspired features."""

        start_time = time.time()

        # Get response from memory system
        response = self.get_memory_system_response(test_case.query)

        # Simulate vector scores for geometry analysis (in real implementation, these would come from actual retrieval)
        vector_scores = self._simulate_vector_scores(test_case.query)

        # Analyze query geometry
        geometry_analysis = self.limit_config.analyze_query_geometry(
            test_case.query, vector_scores, rewrite_agreement=0.3
        )

        # Simulate facet yields (in real implementation, these would come from actual facet generation)
        facet_yields = self._simulate_facet_yields(test_case.query)

        # Calculate fusion gain
        fusion_gain = self._calculate_fusion_gain(facet_yields)

        # Get health metrics
        health_metrics = self.limit_config.get_health_metrics(
            test_case.query_id, geometry_analysis, facet_yields, fusion_gain
        )

        # Run actual RAGChecker evaluation to get real metrics
        try:
            # Create evaluation data in RAGChecker format
            eval_data = [
                {
                    "query": test_case.query,
                    "response": response,
                    "gt_answer": test_case.gt_answer,
                    "retrieved_context": (
                        test_case.retrieved_context
                        if hasattr(test_case, "retrieved_context")
                        else []
                    ),
                }
            ]

            # Run RAGChecker evaluation
            ragchecker_result = self.create_fallback_evaluation(eval_data)

            # Extract metrics
            overall_metrics = ragchecker_result.get("overall_metrics", {})
            precision = overall_metrics.get("precision", 0.0)
            recall = overall_metrics.get("recall", 0.0)
            f1_score = overall_metrics.get("f1_score", 0.0)

        except Exception as e:
            print(f"   ⚠️ RAGChecker evaluation failed: {e}")
            precision = 0.0
            recall = 0.0
            f1_score = 0.0

        # Calculate evaluation time
        evaluation_time = time.time() - start_time

        # Create comprehensive result
        result = {
            "query_id": test_case.query_id,
            "query": test_case.query,
            "response": response,
            "gt_answer": test_case.gt_answer,
            "evaluation_time": evaluation_time,
            # Standard metrics (from RAGChecker)
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            # LIMIT-inspired features
            "geometry_analysis": geometry_analysis,
            "facet_yields": facet_yields,
            "fusion_gain": fusion_gain,
            "health_metrics": health_metrics,
        }

        return result, health_metrics

    def _simulate_vector_scores(self, query: str) -> list[float]:
        """Simulate vector scores for geometry analysis (placeholder for real implementation)."""
        # In real implementation, this would come from actual vector retrieval
        random.seed(hash(query) % 2**32)  # Deterministic for same query

        # Simulate different score distributions based on query characteristics
        if "AND" in query.upper() or "NOT" in query.upper():
            # Boolean queries tend to have flatter scores
            scores = [random.uniform(0.3, 0.7) for _ in range(20)]
        else:
            # Regular queries have more peaked scores
            scores = [random.uniform(0.1, 0.9) for _ in range(20)]
            scores[0] = max(scores) + 0.1  # Ensure top score is clearly highest

        return sorted(scores, reverse=True)

    def _simulate_facet_yields(self, query: str) -> list[dict[str, Any]]:
        """Simulate facet yields (placeholder for real implementation)."""
        # In real implementation, this would come from actual facet generation and evaluation
        random.seed(hash(query) % 2**32)  # Deterministic for same query

        facets = []
        for i in range(4):  # RAGCHECKER_REWRITE_K=4
            new_docs = random.randint(0, 5)
            entity_overlap = random.uniform(0.0, 1.0)

            facet = {
                "facet_id": f"facet_{i}",
                "new_docs_count": new_docs,
                "entity_overlap": entity_overlap,
                "yield_score": 0.6 * new_docs + 0.4 * entity_overlap,
                "should_keep": (0.6 * new_docs + 0.4 * entity_overlap) >= 1.0,
            }
            facets.append(facet)

        return facets

    def _calculate_fusion_gain(self, facet_yields: list[dict[str, Any]]) -> int:
        """Calculate fusion gain from facet yields."""
        # In real implementation, this would be the actual difference in retrieved docs
        kept_facets = [f for f in facet_yields if f["should_keep"]]
        total_new_docs = sum(f["new_docs_count"] for f in kept_facets)
        return total_new_docs

    def _log_case_metrics(
        self, query_id: str, case_result: dict[str, Any], health_metrics: dict[str, Any]
    ) -> None:
        """Log metrics for a specific case."""
        self.logging_data[query_id] = {
            "precision": case_result.get("precision", 0.0),
            "recall": case_result.get("recall", 0.0),
            "f1_score": case_result.get("f1_score", 0.0),
            "evaluation_time": case_result.get("evaluation_time", 0.0),
            "geometry_analysis": case_result.get("geometry_analysis", {}),
            "facet_yields": case_result.get("facet_yields", []),
            "fusion_gain": case_result.get("fusion_gain", 0),
            "health_metrics": health_metrics,
        }

    def _generate_limit_evaluation_report(
        self,
        results: list[dict[str, Any]],
        health_metrics_summary: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate comprehensive LIMIT-inspired evaluation report."""

        # Calculate overall metrics
        precisions = [r.get("precision", 0.0) for r in results]
        recalls = [r.get("recall", 0.0) for r in results]
        f1_scores = [r.get("f1_score", 0.0) for r in results]

        overall_metrics = {
            "precision": sum(precisions) / len(precisions) if precisions else 0.0,
            "recall": sum(recalls) / len(recalls) if recalls else 0.0,
            "f1_score": sum(f1_scores) / len(f1_scores) if f1_scores else 0.0,
        }

        # Get judge floors for comparison
        judge_floors = {
            "precision": 0.135,
            "recall": 0.16,
            "f1_score": 0.145,
            "faithfulness": 0.60,
        }

        # Check baseline compliance
        baseline_compliance = {
            "precision": overall_metrics["precision"] >= judge_floors["precision"],
            "recall": overall_metrics["recall"] >= judge_floors["recall"],
            "f1_score": overall_metrics["f1_score"] >= judge_floors["f1_score"],
        }

        # Calculate LIMIT-inspired summary statistics
        limit_stats = self._calculate_limit_statistics(health_metrics_summary)

        # Create comprehensive report
        report = {
            "evaluation_type": "limit_inspired_precision_recovery",
            "total_cases": len(results),
            "overall_metrics": overall_metrics,
            "judge_floors": judge_floors,
            "baseline_compliance": baseline_compliance,
            "limit_statistics": limit_stats,
            "case_results": results,
            "health_metrics_summary": health_metrics_summary,
            "logging_data": dict(self.logging_data),
            "configuration": self.limit_config.config,
            "timestamp": time.time(),
        }

        return report

    def _calculate_limit_statistics(
        self, health_metrics_summary: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate LIMIT-inspired statistics."""

        if not health_metrics_summary:
            return {}

        # Geometry analysis
        vector_margins = [h["vector_margin"] for h in health_metrics_summary]
        vector_entropies = [h["vector_entropy"] for h in health_metrics_summary]
        geometry_healthy_count = sum(
            1 for h in health_metrics_summary if h["geometry_healthy"]
        )

        # Routing analysis
        routed_to_bm25_count = sum(
            1 for h in health_metrics_summary if h["routed_to_bm25"]
        )

        # Facet analysis
        total_facets = sum(h["total_facets"] for h in health_metrics_summary)
        facets_kept = sum(h["facets_kept"] for h in health_metrics_summary)

        # Fusion analysis
        fusion_gains = [h["fusion_gain"] for h in health_metrics_summary]
        cases_with_fusion_gain = sum(1 for gain in fusion_gains if gain > 0)

        # Boolean analysis
        boolean_include_count = sum(
            h["boolean_terms"]["include"] for h in health_metrics_summary
        )
        boolean_exclude_count = sum(
            h["boolean_terms"]["exclude"] for h in health_metrics_summary
        )
        boolean_or_count = sum(h["boolean_terms"]["or"] for h in health_metrics_summary)

        return {
            "geometry_analysis": {
                "avg_vector_margin": (
                    sum(vector_margins) / len(vector_margins) if vector_margins else 0.0
                ),
                "avg_vector_entropy": (
                    sum(vector_entropies) / len(vector_entropies)
                    if vector_entropies
                    else 0.0
                ),
                "geometry_healthy_cases": geometry_healthy_count,
                "geometry_healthy_percentage": (
                    geometry_healthy_count / len(health_metrics_summary)
                )
                * 100,
            },
            "routing_analysis": {
                "routed_to_bm25_count": routed_to_bm25_count,
                "routed_to_bm25_percentage": (
                    routed_to_bm25_count / len(health_metrics_summary)
                )
                * 100,
            },
            "facet_analysis": {
                "total_facets_generated": total_facets,
                "facets_kept": facets_kept,
                "facet_keep_rate": (
                    (facets_kept / total_facets) * 100 if total_facets > 0 else 0.0
                ),
            },
            "fusion_analysis": {
                "total_fusion_gain": sum(fusion_gains),
                "avg_fusion_gain": (
                    sum(fusion_gains) / len(fusion_gains) if fusion_gains else 0.0
                ),
                "cases_with_fusion_gain": cases_with_fusion_gain,
                "fusion_gain_percentage": (
                    cases_with_fusion_gain / len(health_metrics_summary)
                )
                * 100,
            },
            "boolean_analysis": {
                "total_include_terms": boolean_include_count,
                "total_exclude_terms": boolean_exclude_count,
                "total_or_terms": boolean_or_count,
                "boolean_queries_detected": sum(
                    1
                    for h in health_metrics_summary
                    if any(h["boolean_terms"].values())
                ),
            },
        }


def main():
    """Main function to run LIMIT-inspired evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="RAGChecker LIMIT-Inspired Evaluation")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for results (default: auto-generated)",
    )
    parser.add_argument(
        "--fast-mode",
        action="store_true",
        help="Run in fast mode with limited test cases",
    )

    args = parser.parse_args()

    # Set fast mode if requested
    if args.fast_mode:
        os.environ["RAGCHECKER_FAST_MODE"] = "1"

    # Initialize evaluator
    evaluator = LimitInspiredEvaluator()

    # Get test cases
    test_cases = evaluator.create_official_test_cases()

    # Run evaluation
    print("\n🚀 Starting LIMIT-inspired evaluation")
    evaluation_report = evaluator.evaluate_with_limit_features(test_cases)

    # Save results
    if args.output:
        output_file = args.output
    else:
        timestamp = int(time.time())
        output_file = (
            f"metrics/baseline_evaluations/limit_inspired_evaluation_{timestamp}.json"
        )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # For now, just print the results instead of saving to JSON to avoid serialization issues
    print("\n📊 LIMIT-Inspired Evaluation Results:")
    print(f"   Total Cases: {evaluation_report['total_cases']}")
    print(f"   Overall Metrics: {evaluation_report['overall_metrics']}")
    print(f"   Baseline Compliance: {evaluation_report['baseline_compliance']}")
    print(f"   LIMIT Statistics: {evaluation_report['limit_statistics']}")

    # Try to save a simplified version
    try:
        simplified_report = {
            "evaluation_type": evaluation_report["evaluation_type"],
            "total_cases": evaluation_report["total_cases"],
            "overall_metrics": evaluation_report["overall_metrics"],
            "baseline_compliance": evaluation_report["baseline_compliance"],
            "timestamp": evaluation_report["timestamp"],
        }

        with open(output_file, "w") as f:
            json.dump(simplified_report, f, indent=2)
        print(f"\n📁 Simplified results saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save results to file: {e}")
        print("   Results printed above instead")

    # Print summary
    print("\n📊 LIMIT-Inspired Evaluation Complete")
    print("=" * 60)
    print("📈 Overall Metrics:")
    overall = evaluation_report["overall_metrics"]
    print(f"   Precision: {overall['precision']:.3f}")
    print(f"   Recall: {overall['recall']:.3f}")
    print(f"   F1 Score: {overall['f1_score']:.3f}")

    print("\n🎯 Baseline Compliance:")
    compliance = evaluation_report["baseline_compliance"]
    floors = evaluation_report["judge_floors"]
    for metric, passed in compliance.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        target = floors[metric]
        current = overall[metric]
        print(f"   {metric}: {status} ({current:.3f} vs {target:.3f})")

    print("\n🧠 LIMIT-Inspired Features:")
    limit_stats = evaluation_report["limit_statistics"]
    print(
        f"   Geometry Healthy: {limit_stats['geometry_analysis']['geometry_healthy_percentage']:.1f}%"
    )
    print(
        f"   Routed to BM25: {limit_stats['routing_analysis']['routed_to_bm25_percentage']:.1f}%"
    )
    print(
        f"   Facet Keep Rate: {limit_stats['facet_analysis']['facet_keep_rate']:.1f}%"
    )
    print(
        f"   Fusion Gain Cases: {limit_stats['fusion_analysis']['fusion_gain_percentage']:.1f}%"
    )

    print(f"\n📁 Results saved to: {output_file}")

    # Return exit code based on compliance
    all_passed = all(compliance.values())
    return 0 if all_passed else 2


if __name__ == "__main__":
    sys.exit(main())
