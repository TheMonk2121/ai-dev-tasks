#!/usr/bin/env python3
"""
Evaluation Harness for Decision Retrieval

Computes Failure@20, Recall@10, Precision@10 metrics for decision retrieval
using the unified API and stores results as JSON/CSV artifacts.
"""

import csv
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.unified_retrieval_api import search_decisions

logger = logging.getLogger(__name__)


class DecisionRetrievalEvaluator:
    """Evaluator for decision retrieval performance"""

    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.logger = logging.getLogger("decision_retrieval_evaluator")

    def create_gold_set(self) -> list[dict[str, Any]]:
        """
        DEPRECATED: Load gold set from unified dataset instead of hardcoded values.

        This method now loads decision cases from evals/gold/v1/gold_cases.jsonl
        to ensure consistent evaluation across all systems.

        Returns:
            List of query-gold pairs for evaluation
        """
        try:
            from src.utils.gold_loader import filter_cases, load_gold_cases

            # Load decision cases from unified dataset
            cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")
            decision_cases = filter_cases(cases, mode="decision")

            # Convert to legacy format for compatibility
            gold_set = []
            for case in decision_cases:
                gold_set.append(
                    {
                        "query": case.query,
                        "expected_decisions": case.expected_decisions or [],
                        "description": case.notes or f"Decision case: {case.query}",
                    }
                )

            self.logger.info(f"Loaded {len(gold_set)} decision cases from unified dataset")
            return gold_set

        except ImportError:
            self.logger.warning("New gold loader not available, returning empty set")
            return []
        except Exception as e:
            self.logger.error(f"Failed to load gold cases: {e}")
            return []

    def compute_recall_at_k(self, retrieved_decisions: list[str], expected_decisions: list[str], k: int) -> float:
        """
        Compute Recall@K metric

        Args:
            retrieved_decisions: List of retrieved decision keys
            expected_decisions: List of expected decision keys
            k: Number of top results to consider

        Returns:
            Recall@K score (0.0 to 1.0)
        """
        if not expected_decisions:
            return 1.0  # If no expected decisions, perfect recall

        # Get top K retrieved decisions
        top_k_retrieved = retrieved_decisions[:k]

        # Count how many expected decisions are in top K
        relevant_retrieved = set(top_k_retrieved) & set(expected_decisions)

        return len(relevant_retrieved) / len(expected_decisions)

    def compute_precision_at_k(self, retrieved_decisions: list[str], expected_decisions: list[str], k: int) -> float:
        """
        Compute Precision@K metric

        Args:
            retrieved_decisions: List of retrieved decision keys
            expected_decisions: List of expected decision keys
            k: Number of top results to consider

        Returns:
            Precision@K score (0.0 to 1.0)
        """
        if k == 0:
            return 0.0

        # Get top K retrieved decisions
        top_k_retrieved = retrieved_decisions[:k]

        # If no decisions retrieved, precision is 0
        if not top_k_retrieved:
            return 0.0

        # Count how many of top K are relevant
        relevant_retrieved = set(top_k_retrieved) & set(expected_decisions)

        return len(relevant_retrieved) / len(top_k_retrieved)

    def compute_failure_at_k(self, retrieved_decisions: list[str], expected_decisions: list[str], k: int) -> float:
        """
        Compute Failure@K metric (fraction of queries with no relevant results in top K)

        Args:
            retrieved_decisions: List of retrieved decision keys
            expected_decisions: List of expected decision keys
            k: Number of top results to consider

        Returns:
            Failure@K score (0.0 to 1.0)
        """
        if not expected_decisions:
            return 0.0  # If no expected decisions, no failure

        # Get top K retrieved decisions
        top_k_retrieved = retrieved_decisions[:k]

        # Check if any expected decisions are in top K
        relevant_retrieved = set(top_k_retrieved) & set(expected_decisions)

        return 1.0 if len(relevant_retrieved) == 0 else 0.0

    def evaluate_query(self, query: str, expected_decisions: list[str]) -> dict[str, Any]:
        """
        Evaluate a single query

        Args:
            query: Search query
            expected_decisions: List of expected decision keys

        Returns:
            Dictionary with evaluation results
        """
        try:
            # Use unified API to search decisions
            result = search_decisions(query=query, limit=20, debug=True)  # Get top 20 for Failure@20 calculation

            retrieved_decisions = [d["decision_key"] for d in result["decisions"]]

            # Compute metrics
            recall_at_10 = self.compute_recall_at_k(retrieved_decisions, expected_decisions, 10)
            precision_at_10 = self.compute_precision_at_k(retrieved_decisions, expected_decisions, 10)
            failure_at_20 = self.compute_failure_at_k(retrieved_decisions, expected_decisions, 20)

            return {
                "query": query,
                "expected_decisions": expected_decisions,
                "retrieved_decisions": retrieved_decisions,
                "recall_at_10": recall_at_10,
                "precision_at_10": precision_at_10,
                "failure_at_20": failure_at_20,
                "total_retrieved": len(retrieved_decisions),
                "total_expected": len(expected_decisions),
                "debug_info": result.get("debug", {}),
            }

        except Exception as e:
            self.logger.error(f"Error evaluating query '{query}': {e}")
            return {
                "query": query,
                "expected_decisions": expected_decisions,
                "retrieved_decisions": [],
                "recall_at_10": 0.0,
                "precision_at_10": 0.0,
                "failure_at_20": 1.0,
                "total_retrieved": 0,
                "total_expected": len(expected_decisions),
                "error": str(e),
            }

    def run_evaluation(self) -> dict[str, Any]:
        """
        Run the complete evaluation

        Returns:
            Dictionary with evaluation results and metrics
        """
        self.logger.info("Starting decision retrieval evaluation...")

        # Create gold set
        gold_set = self.create_gold_set()

        # Evaluate each query
        query_results = []
        for gold_item in gold_set:
            result = self.evaluate_query(gold_item["query"], gold_item["expected_decisions"])
            result["description"] = gold_item["description"]
            query_results.append(result)

            # Print per-query debug row
            print(f"Query: {result['query']}")
            print(f"  Expected: {result['expected_decisions']}")
            print(f"  Retrieved: {result['retrieved_decisions'][:5]}...")  # Show first 5
            print(
                f"  R@10: {result['recall_at_10']:.3f}, P@10: {result['precision_at_10']:.3f}, F@20: {result['failure_at_20']:.3f}"
            )
            print()

        # Compute aggregate metrics
        total_queries = len(query_results)
        avg_recall_at_10 = sum(r["recall_at_10"] for r in query_results) / total_queries
        avg_precision_at_10 = sum(r["precision_at_10"] for r in query_results) / total_queries
        avg_failure_at_20 = sum(r["failure_at_20"] for r in query_results) / total_queries

        # Check if targets are met
        targets_met = {
            "recall_at_10": avg_recall_at_10 >= 0.7,
            "precision_at_10": avg_precision_at_10 >= 0.8,
            "failure_at_20": avg_failure_at_20 <= 0.2,
        }

        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": total_queries,
            "metrics": {
                "recall_at_10": avg_recall_at_10,
                "precision_at_10": avg_precision_at_10,
                "failure_at_20": avg_failure_at_20,
            },
            "targets": {"recall_at_10_target": 0.7, "precision_at_10_target": 0.8, "failure_at_20_target": 0.2},
            "targets_met": targets_met,
            "all_targets_met": all(targets_met.values()),
            "query_results": query_results,
        }

        self.logger.info(
            f"Evaluation completed. R@10: {avg_recall_at_10:.3f}, P@10: {avg_precision_at_10:.3f}, F@20: {avg_failure_at_20:.3f}"
        )

        return evaluation_results

    def save_artifacts(self, results: dict[str, Any], output_dir: str = "evaluation_artifacts") -> None:
        """
        Save evaluation artifacts as JSON and CSV

        Args:
            results: Evaluation results
            output_dir: Directory to save artifacts
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON results
        json_file = os.path.join(output_dir, f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_file, "w") as f:
            json.dump(results, f, indent=2)

        # Save CSV results
        csv_file = os.path.join(output_dir, f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "query",
                    "description",
                    "expected_decisions",
                    "retrieved_decisions",
                    "recall_at_10",
                    "precision_at_10",
                    "failure_at_20",
                    "total_retrieved",
                    "total_expected",
                ]
            )

            for result in results["query_results"]:
                writer.writerow(
                    [
                        result["query"],
                        result.get("description", ""),
                        ";".join(result["expected_decisions"]),
                        ";".join(result["retrieved_decisions"]),
                        result["recall_at_10"],
                        result["precision_at_10"],
                        result["failure_at_20"],
                        result["total_retrieved"],
                        result["total_expected"],
                    ]
                )

        self.logger.info(f"Artifacts saved to {output_dir}")
        print("📊 Evaluation artifacts saved:")
        print(f"  JSON: {json_file}")
        print(f"  CSV: {csv_file}")


def run_evaluation(db_connection_string: str | None = None) -> dict[str, Any]:
    """
    Convenience function to run evaluation

    Args:
        db_connection_string: Database connection string (optional)

    Returns:
        Evaluation results
    """
    if db_connection_string is None:
        db_connection_string = "postgresql://danieljacobs@localhost:5432/ai_agency"

    evaluator = DecisionRetrievalEvaluator(db_connection_string)
    results = evaluator.run_evaluation()
    evaluator.save_artifacts(results)

    return results


if __name__ == "__main__":
    # Run evaluation
    print("🎯 Running Decision Retrieval Evaluation...")
    results = run_evaluation()

    # Print summary
    print("\n📊 Evaluation Summary:")
    print(f"  Total Queries: {results['total_queries']}")
    print(f"  Recall@10: {results['metrics']['recall_at_10']:.3f} (target: ≥0.7)")
    print(f"  Precision@10: {results['metrics']['precision_at_10']:.3f} (target: ≥0.8)")
    print(f"  Failure@20: {results['metrics']['failure_at_20']:.3f} (target: ≤0.2)")
    print(f"  All Targets Met: {'✅' if results['all_targets_met'] else '❌'}")
