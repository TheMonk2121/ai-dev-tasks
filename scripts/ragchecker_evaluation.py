#!/usr/bin/env python3
"""
RAGChecker Evaluation System

This module implements RAGChecker evaluation as a replacement for RAGAS.
RAGChecker is a peer-reviewed, industry-tested framework that provides
fine-grained diagnostic metrics for RAG systems with strong correlation
to human judgments.

Reference: https://arxiv.org/abs/2408.08067
"""

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from baseline_ragus_evaluation import BaselineEvaluator
from ragchecker.container import RetrievedDoc
from ragchecker.evaluator import RAGChecker, RAGResult, RAGResults


@dataclass
class RAGCheckerResult:
    """Result of RAGChecker evaluation."""

    test_case_name: str
    query: str
    custom_score: float
    ragchecker_scores: Dict[str, float]
    ragchecker_overall: float
    comparison: Dict[str, Any]
    recommendation: str


class RAGCheckerEvaluator:
    """RAGChecker evaluator that provides industry-standard RAG evaluation."""

    def __init__(self):
        self.baseline_evaluator = BaselineEvaluator()

        # Initialize RAGChecker with default settings
        # Note: RAGChecker requires LLM access for claim extraction and checking
        # We'll use it in a limited capacity for metrics that don't require LLM
        self.ragchecker = RAGChecker()

    def run_memory_query(self, query: str, role: str = "planner") -> Dict[str, Any]:
        """Run memory query using our existing orchestrator."""
        try:
            result = subprocess.run(
                [
                    "python3",
                    "scripts/unified_memory_orchestrator.py",
                    "--systems",
                    "ltst",
                    "cursor",
                    "go_cli",
                    "prime",
                    "--role",
                    role,
                    query,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {"success": True, "output": result.stdout, "error": None}
            else:
                return {"success": False, "output": result.stdout, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Query timed out after 60 seconds"}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

    def extract_ragchecker_data(self, response: Dict[str, Any], query: str) -> RAGResult:
        """Extract data in RAGChecker format from memory system response."""
        try:
            # Parse the response
            response_data = json.loads(response["output"])
            generated_response = response_data.get("formatted_output", "")

            # Extract retrieved context
            context_sources = []
            if "ltst_memory" in response_data:
                context_sources.append(response_data["ltst_memory"])
            if "cursor_memory" in response_data:
                context_sources.append(response_data["cursor_memory"])
            if "go_cli_memory" in response_data:
                context_sources.append(response_data["go_cli_memory"])
            if "prime_memory" in response_data:
                context_sources.append(response_data["prime_memory"])

            retrieved_context = " ".join(context_sources) if context_sources else ""

            # Create RetrievedDoc objects
            retrieved_docs = []
            if retrieved_context:
                retrieved_docs.append(RetrievedDoc(doc_id="memory_context", text=retrieved_context))

            # Create RAGResult
            # Note: We don't have ground truth answers, so we'll use a placeholder
            rag_result = RAGResult(
                query_id=f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                query=query,
                gt_answer="",  # We don't have ground truth
                response=generated_response,
                retrieved_context=retrieved_docs,
            )

            return rag_result

        except Exception as e:
            print(f"Error extracting RAGChecker data: {e}")
            # Fallback to basic extraction
            return RAGResult(
                query_id=f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                query=query,
                gt_answer="",
                response=response.get("output", ""),
                retrieved_context=[],
            )

    def run_ragchecker_evaluation(self, rag_result: RAGResult) -> Dict[str, float]:
        """Run RAGChecker evaluation on the data."""
        try:
            # Create RAGResults object
            rag_results = RAGResults([rag_result])

            # Run RAGChecker evaluation with limited metrics
            # Note: Many RAGChecker metrics require LLM access and ground truth
            # We'll focus on metrics that can work with our data
            results = self.ragchecker.evaluate(rag_results, metrics="faithfulness")

            # Extract scores
            ragchecker_scores = {}
            for metric_name, score in results.items():
                try:
                    if isinstance(score, (int, float)):
                        ragchecker_scores[metric_name] = float(score)
                    else:
                        ragchecker_scores[metric_name] = 0.0
                except (ValueError, TypeError):
                    ragchecker_scores[metric_name] = 0.0

            return ragchecker_scores

        except Exception as e:
            print(f"RAGChecker evaluation failed: {e}")
            # Return basic metrics that we can calculate manually
            return self._calculate_basic_metrics(rag_result)

    def _calculate_basic_metrics(self, rag_result: RAGResult) -> Dict[str, float]:
        """Calculate basic metrics that don't require LLM or ground truth."""
        metrics = {}

        # Response length (normalized)
        response_length = len(rag_result.response)
        metrics["response_length"] = min(response_length / 1000, 1.0)  # Normalize to 0-1

        # Context utilization (if we have retrieved context)
        if rag_result.retrieved_context:
            context_length = sum(len(doc.text) for doc in rag_result.retrieved_context)
            metrics["context_utilization"] = min(context_length / 1000, 1.0)
        else:
            metrics["context_utilization"] = 0.0

        # Query-response overlap (simple keyword matching)
        query_words = set(rag_result.query.lower().split())
        response_words = set(rag_result.response.lower().split())
        if query_words:
            overlap = len(query_words.intersection(response_words)) / len(query_words)
            metrics["query_response_overlap"] = overlap
        else:
            metrics["query_response_overlap"] = 0.0

        return metrics

    def calculate_ragchecker_overall(self, ragchecker_scores: Dict[str, float]) -> float:
        """Calculate overall RAGChecker score (weighted average)."""
        if not ragchecker_scores:
            return 0.0

        # Define weights for different metrics (based on importance)
        weights = {
            "faithfulness": 0.40,  # Most important - factual consistency
            "query_response_overlap": 0.30,  # Query relevance
            "context_utilization": 0.20,  # Context usage
            "response_length": 0.10,  # Response completeness
        }

        # Calculate weighted average
        total_score = 0.0
        total_weight = 0.0

        for metric, score in ragchecker_scores.items():
            weight = weights.get(metric, 0.1)  # Default weight
            total_score += score * weight
            total_weight += weight

        # Convert to 0-100 scale
        if total_weight > 0:
            return (total_score / total_weight) * 100
        else:
            return 0.0

    def compare_evaluations(self, custom_score: float, ragchecker_overall: float) -> Dict[str, Any]:
        """Compare custom vs RAGChecker evaluation results."""
        difference = custom_score - ragchecker_overall
        percentage_diff = (difference / custom_score * 100) if custom_score > 0 else 0

        if abs(percentage_diff) < 10:
            agreement = "High Agreement"
            recommendation = "Both evaluations are well-aligned"
        elif percentage_diff > 20:
            agreement = "Custom Higher"
            recommendation = "Custom evaluation may be too lenient"
        elif percentage_diff < -20:
            agreement = "RAGChecker Higher"
            recommendation = "RAGChecker evaluation may be more appropriate"
        else:
            agreement = "Moderate Agreement"
            recommendation = "Consider using RAGChecker as industry standard"

        return {
            "difference": difference,
            "percentage_diff": percentage_diff,
            "agreement": agreement,
            "recommendation": recommendation,
        }

    def evaluate_test_case(self, case_name: str, query: str, role: str = "planner") -> RAGCheckerResult:
        """Evaluate a single test case using both custom and RAGChecker evaluation."""

        # Run memory query
        response = self.run_memory_query(query, role)

        if not response["success"]:
            return RAGCheckerResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                ragchecker_scores={},
                ragchecker_overall=0.0,
                comparison={"error": response["error"], "agreement": "Query Failed", "recommendation": "Query failed"},
                recommendation="Query failed",
            )

        # Find the case by name
        baseline_cases = self.baseline_evaluator.create_baseline_evaluation_cases()
        case = None
        for c in baseline_cases:
            if c.name == case_name:
                case = c
                break

        if case is None:
            return RAGCheckerResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                ragchecker_scores={},
                ragchecker_overall=0.0,
                comparison={
                    "error": "Case not found",
                    "agreement": "Case Not Found",
                    "recommendation": "Case not found",
                },
                recommendation="Case not found",
            )

        # Run custom evaluation
        try:
            custom_result = self.baseline_evaluator.evaluate_response(case, response)
            custom_score = custom_result["score"]
        except Exception as e:
            print(f"Custom evaluation failed: {e}")
            custom_score = 0.0

        # Extract RAGChecker data
        rag_result = self.extract_ragchecker_data(response, query)

        # Run RAGChecker evaluation
        ragchecker_scores = self.run_ragchecker_evaluation(rag_result)
        ragchecker_overall = self.calculate_ragchecker_overall(ragchecker_scores)

        # Compare evaluations
        comparison = self.compare_evaluations(custom_score, ragchecker_overall)

        return RAGCheckerResult(
            test_case_name=case_name,
            query=query,
            custom_score=custom_score,
            ragchecker_scores=ragchecker_scores,
            ragchecker_overall=ragchecker_overall,
            comparison=comparison,
            recommendation=comparison["recommendation"],
        )

    def run_ragchecker_evaluation_suite(self) -> Dict[str, Any]:
        """Run RAGChecker evaluation on all baseline test cases."""

        print("🧠 Starting RAGChecker Evaluation")
        print("📊 Industry-Standard RAG Evaluation (Peer-Reviewed)")
        print("=" * 60)

        # Get baseline test cases
        baseline_cases = self.baseline_evaluator.create_baseline_evaluation_cases()

        results = []
        custom_total = 0
        ragchecker_total = 0

        for i, case in enumerate(baseline_cases, 1):
            print(f"\n🔍 Test {i}/{len(baseline_cases)}: {case.name}")
            print(f"   Query: {case.query}")

            # Run RAGChecker evaluation
            result = self.evaluate_test_case(case.name, case.query, case.role)

            results.append(result)
            custom_total += result.custom_score
            ragchecker_total += result.ragchecker_overall

            # Print results
            print(f"   Custom Score: {result.custom_score:.1f}/100")
            print(f"   RAGChecker Score: {result.ragchecker_overall:.1f}/100")
            print(f"   Agreement: {result.comparison['agreement']}")
            print(f"   Recommendation: {result.recommendation}")

        # Calculate averages
        custom_avg = custom_total / len(baseline_cases)
        ragchecker_avg = ragchecker_total / len(baseline_cases)

        # Overall comparison
        overall_comparison = self.compare_evaluations(custom_avg, ragchecker_avg)

        print("\n" + "=" * 60)
        print("📊 RAGCHECKER EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Custom Average: {custom_avg:.1f}/100")
        print(f"🎯 RAGChecker Average: {ragchecker_avg:.1f}/100")
        print(f"📈 Difference: {overall_comparison['difference']:.1f} points")
        print(f"📊 Agreement: {overall_comparison['agreement']}")
        print(f"💡 Recommendation: {overall_comparison['recommendation']}")

        # Detailed RAGChecker metrics
        print("\n🔍 RAGChecker Metrics Breakdown:")
        all_ragchecker_scores = {}
        for result in results:
            for metric, score in result.ragchecker_scores.items():
                if metric not in all_ragchecker_scores:
                    all_ragchecker_scores[metric] = []
                all_ragchecker_scores[metric].append(score)

        for metric, scores in all_ragchecker_scores.items():
            avg_score = sum(scores) / len(scores) * 100
            print(f"   {metric}: {avg_score:.1f}/100")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            "timestamp": timestamp,
            "custom_average": custom_avg,
            "ragchecker_average": ragchecker_avg,
            "overall_comparison": overall_comparison,
            "ragchecker_metrics_breakdown": {
                metric: sum(scores) / len(scores) * 100 for metric, scores in all_ragchecker_scores.items()
            },
            "detailed_results": [
                {
                    "test_case": r.test_case_name,
                    "query": r.query,
                    "custom_score": r.custom_score,
                    "ragchecker_scores": r.ragchecker_scores,
                    "ragchecker_overall": r.ragchecker_overall,
                    "comparison": r.comparison,
                    "recommendation": r.recommendation,
                }
                for r in results
            ],
        }

        output_file = f"metrics/baseline_ragus_evaluations/ragchecker_evaluation_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        return results_data


def main():
    """Run RAGChecker evaluation."""
    evaluator = RAGCheckerEvaluator()
    results = evaluator.run_ragchecker_evaluation_suite()

    # Print final recommendation
    print("\n🎯 FINAL RECOMMENDATION:")
    print(f"Based on the comparison between custom evaluation ({results['custom_average']:.1f}/100)")
    print(f"and RAGChecker evaluation ({results['ragchecker_average']:.1f}/100):")
    print(f"→ {results['overall_comparison']['recommendation']}")

    print("\n📚 RAGChecker Reference:")
    print("Paper: https://arxiv.org/abs/2408.08067")
    print("Features: Peer-reviewed, industry-tested, correlates with human judgments")
    print("\n⚠️  Note: This evaluation uses basic metrics due to LLM access requirements.")
    print("   For full RAGChecker capabilities, configure LLM access (OpenAI, Bedrock, etc.)")


if __name__ == "__main__":
    main()
