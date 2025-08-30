#!/usr/bin/env python3
"""
Hybrid RAGAS Evaluation System

This module implements a hybrid evaluation approach that runs both our custom
baseline evaluation and RAGAS evaluation side by side for comparison.

The goal is to:
1. Compare our custom evaluation against industry-standard RAGAS
2. Validate our evaluation methodology
3. Decide whether to migrate fully to RAGAS or keep hybrid approach
"""

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from baseline_ragus_evaluation import BaselineEvaluator
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness


@dataclass
class HybridEvaluationResult:
    """Result of hybrid evaluation comparing custom vs RAGAS."""

    test_case_name: str
    query: str
    custom_score: float
    ragas_scores: Dict[str, float]
    ragas_overall: float
    comparison: Dict[str, Any]
    recommendation: str


class HybridRagasEvaluator:
    """Hybrid evaluator that runs both custom and RAGAS evaluation."""

    def __init__(self):
        self.baseline_evaluator = BaselineEvaluator()
        # Use only metrics that work with our data format (no reference required)
        self.ragas_metrics = [faithfulness, answer_relevancy]

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

    def extract_ragas_data(self, response: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Extract data in RAGAS format from memory system response."""
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

            retrieved_documents = [" ".join(context_sources)] if context_sources else [""]

            return {
                "user_input": [query],
                "response": [generated_response],
                "retrieved_contexts": [retrieved_documents],
            }

        except Exception:
            # Fallback to basic extraction
            return {"user_input": [query], "response": [response.get("output", "")], "retrieved_contexts": [[""]]}

    def run_ragas_evaluation(self, ragas_data: Dict[str, Any]) -> Dict[str, float]:
        """Run RAGAS evaluation on the data."""
        try:
            # Convert to Hugging Face Dataset
            dataset = Dataset.from_dict(ragas_data)

            # Run RAGAS evaluation
            results = evaluate(dataset, self.ragas_metrics)

            # Convert to simple dict
            ragas_scores = {}
            for metric_name, score in results.items():
                ragas_scores[metric_name] = float(score)

            return ragas_scores

        except Exception as e:
            print(f"RAGAS evaluation failed: {e}")
            return {"faithfulness": 0.0, "answer_relevancy": 0.0, "context_precision": 0.0, "context_recall": 0.0}

    def calculate_ragas_overall(self, ragas_scores: Dict[str, float]) -> float:
        """Calculate overall RAGAS score (simple average)."""
        if not ragas_scores:
            return 0.0

        # Convert to 0-100 scale and average
        scores_100 = [score * 100 for score in ragas_scores.values()]
        return sum(scores_100) / len(scores_100)

    def compare_evaluations(self, custom_score: float, ragas_overall: float) -> Dict[str, Any]:
        """Compare custom vs RAGAS evaluation results."""
        difference = custom_score - ragas_overall
        percentage_diff = (difference / custom_score * 100) if custom_score > 0 else 0

        if abs(percentage_diff) < 10:
            agreement = "High Agreement"
            recommendation = "Both evaluations are well-aligned"
        elif percentage_diff > 20:
            agreement = "Custom Higher"
            recommendation = "Custom evaluation may be too lenient"
        elif percentage_diff < -20:
            agreement = "RAGAS Higher"
            recommendation = "RAGAS evaluation may be more appropriate"
        else:
            agreement = "Moderate Agreement"
            recommendation = "Consider using RAGAS as industry standard"

        return {
            "difference": difference,
            "percentage_diff": percentage_diff,
            "agreement": agreement,
            "recommendation": recommendation,
        }

    def evaluate_test_case(self, case_name: str, query: str, role: str = "planner") -> HybridEvaluationResult:
        """Evaluate a single test case using both custom and RAGAS evaluation."""

        # Run memory query
        response = self.run_memory_query(query, role)

        if not response["success"]:
            return HybridEvaluationResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                ragas_scores={},
                ragas_overall=0.0,
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
            return HybridEvaluationResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                ragas_scores={},
                ragas_overall=0.0,
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

        # Extract RAGAS data
        ragas_data = self.extract_ragas_data(response, query)

        # Run RAGAS evaluation
        ragas_scores = self.run_ragas_evaluation(ragas_data)
        ragas_overall = self.calculate_ragas_overall(ragas_scores)

        # Compare evaluations
        comparison = self.compare_evaluations(custom_score, ragas_overall)

        return HybridEvaluationResult(
            test_case_name=case_name,
            query=query,
            custom_score=custom_score,
            ragas_scores=ragas_scores,
            ragas_overall=ragas_overall,
            comparison=comparison,
            recommendation=comparison["recommendation"],
        )

    def run_hybrid_evaluation(self) -> Dict[str, Any]:
        """Run hybrid evaluation on all baseline test cases."""

        print("🧠 Starting Hybrid RAGAS Evaluation")
        print("📊 Comparing Custom vs Industry-Standard RAGAS")
        print("=" * 60)

        # Get baseline test cases
        baseline_cases = self.baseline_evaluator.create_baseline_evaluation_cases()

        results = []
        custom_total = 0
        ragas_total = 0

        for i, case in enumerate(baseline_cases, 1):
            print(f"\n🔍 Test {i}/{len(baseline_cases)}: {case.name}")
            print(f"   Query: {case.query}")

            # Run hybrid evaluation
            result = self.evaluate_test_case(case.name, case.query, case.role)

            results.append(result)
            custom_total += result.custom_score
            ragas_total += result.ragas_overall

            # Print results
            print(f"   Custom Score: {result.custom_score:.1f}/100")
            print(f"   RAGAS Score: {result.ragas_overall:.1f}/100")
            print(f"   Agreement: {result.comparison['agreement']}")
            print(f"   Recommendation: {result.recommendation}")

        # Calculate averages
        custom_avg = custom_total / len(baseline_cases)
        ragas_avg = ragas_total / len(baseline_cases)

        # Overall comparison
        overall_comparison = self.compare_evaluations(custom_avg, ragas_avg)

        print("\n" + "=" * 60)
        print("📊 HYBRID RAGAS EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Custom Average: {custom_avg:.1f}/100")
        print(f"🎯 RAGAS Average: {ragas_avg:.1f}/100")
        print(f"📈 Difference: {overall_comparison['difference']:.1f} points")
        print(f"📊 Agreement: {overall_comparison['agreement']}")
        print(f"💡 Recommendation: {overall_comparison['recommendation']}")

        # Detailed RAGAS metrics
        print("\n🔍 RAGAS Metrics Breakdown:")
        all_ragas_scores = {}
        for result in results:
            for metric, score in result.ragas_scores.items():
                if metric not in all_ragas_scores:
                    all_ragas_scores[metric] = []
                all_ragas_scores[metric].append(score)

        for metric, scores in all_ragas_scores.items():
            avg_score = sum(scores) / len(scores) * 100
            print(f"   {metric}: {avg_score:.1f}/100")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            "timestamp": timestamp,
            "custom_average": custom_avg,
            "ragas_average": ragas_avg,
            "overall_comparison": overall_comparison,
            "ragas_metrics_breakdown": {
                metric: sum(scores) / len(scores) * 100 for metric, scores in all_ragas_scores.items()
            },
            "detailed_results": [
                {
                    "test_case": r.test_case_name,
                    "query": r.query,
                    "custom_score": r.custom_score,
                    "ragas_scores": r.ragas_scores,
                    "ragas_overall": r.ragas_overall,
                    "comparison": r.comparison,
                    "recommendation": r.recommendation,
                }
                for r in results
            ],
        }

        output_file = f"metrics/baseline_ragus_evaluations/hybrid_ragas_evaluation_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        return results_data


def main():
    """Run hybrid RAGAS evaluation."""
    evaluator = HybridRagasEvaluator()
    results = evaluator.run_hybrid_evaluation()

    # Print final recommendation
    print("\n🎯 FINAL RECOMMENDATION:")
    print(f"Based on the comparison between custom evaluation ({results['custom_average']:.1f}/100)")
    print(f"and RAGAS evaluation ({results['ragas_average']:.1f}/100):")
    print(f"→ {results['overall_comparison']['recommendation']}")


if __name__ == "__main__":
    main()
