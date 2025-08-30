#!/usr/bin/env python3
"""
Local RAG Evaluation System

This module implements local RAG evaluation using RAG-Evaluation package
with Ollama support for completely local evaluation without API keys.

Features:
- Query relevance evaluation
- Factual accuracy assessment
- Coverage analysis
- Coherence scoring
- Fluency evaluation
- Local model support via Ollama
- No API keys required
"""

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from baseline_ragus_evaluation import BaselineEvaluator
from rag_evaluation import (
    COHERENCE_SCORE_CRITERIA,
    COHERENCE_SCORE_STEPS,
    COVERAGE_CRITERIA,
    COVERAGE_STEPS,
    FACTUAL_ACCURACY_CRITERIA,
    FACTUAL_ACCURACY_STEPS,
    FLUENCY_SCORE_CRITERIA,
    FLUENCY_SCORE_STEPS,
    QUERY_RELEVANCE_CRITERIA,
    QUERY_RELEVANCE_STEPS,
    evaluate_response,
    normalize_score,
)


@dataclass
class LocalRAGEvaluationResult:
    """Result of local RAG evaluation."""

    test_case_name: str
    query: str
    custom_score: float
    local_rag_scores: Dict[str, float]
    local_rag_overall: float
    comparison: Dict[str, Any]
    recommendation: str


class LocalRAGEvaluator:
    """Local RAG evaluator using RAG-Evaluation with Ollama support."""

    def __init__(self, ollama_model: str = "llama3.2:1b"):
        self.baseline_evaluator = BaselineEvaluator()
        self.ollama_model = ollama_model

        # Define evaluation metrics and weights
        self.evaluation_metrics = {
            "query_relevance": (QUERY_RELEVANCE_CRITERIA, QUERY_RELEVANCE_STEPS),
            "factual_accuracy": (FACTUAL_ACCURACY_CRITERIA, FACTUAL_ACCURACY_STEPS),
            "coverage": (COVERAGE_CRITERIA, COVERAGE_STEPS),
            "coherence": (COHERENCE_SCORE_CRITERIA, COHERENCE_SCORE_STEPS),
            "fluency": (FLUENCY_SCORE_CRITERIA, FLUENCY_SCORE_STEPS),
        }

        # Weights for different metrics
        self.metric_weights = {
            "query_relevance": 0.25,
            "factual_accuracy": 0.30,
            "coverage": 0.20,
            "coherence": 0.15,
            "fluency": 0.10,
        }

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

    def extract_evaluation_data(self, response: Dict[str, Any], query: str) -> Dict[str, str]:
        """Extract data for RAG evaluation from memory system response."""
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

            return {"query": query, "response": generated_response, "document": retrieved_context}

        except json.JSONDecodeError:
            # Handle case where output is not valid JSON
            return {"query": query, "response": response.get("output", ""), "document": ""}
        except Exception as e:
            print(f"Error extracting evaluation data: {e}")
            # Fallback to basic extraction
            return {"query": query, "response": response.get("output", ""), "document": ""}

    def run_local_rag_evaluation(self, eval_data: Dict[str, str]) -> Dict[str, float]:
        """Run local RAG evaluation using RAG-Evaluation with Ollama."""
        try:
            # Use RAG-Evaluation with Ollama model
            # Note: RAG-Evaluation supports local models via model_type parameter
            results_df = evaluate_response(
                query=eval_data["query"],
                response=eval_data["response"],
                document=eval_data["document"],
                model_type="ollama",  # Use Ollama for local evaluation
                model_name=self.ollama_model,
                evaluation_metrics=self.evaluation_metrics,
                weights=list(self.metric_weights.values()),
            )

            # Extract scores from DataFrame
            local_rag_scores = {}
            for metric in self.evaluation_metrics.keys():
                if metric in results_df.columns:
                    # Get the score and normalize to 0-100 scale
                    score = results_df[metric].iloc[0] if len(results_df) > 0 else 0
                    local_rag_scores[metric] = normalize_score(score, max_score=5) * 100
                else:
                    local_rag_scores[metric] = 0.0

            return local_rag_scores

        except Exception as e:
            print(f"Local RAG evaluation failed: {e}")
            # Fallback to basic metrics calculation
            return self._calculate_basic_metrics(eval_data)

    def _calculate_basic_metrics(self, eval_data: Dict[str, str]) -> Dict[str, float]:
        """Calculate basic metrics that don't require LLM evaluation."""
        metrics = {}

        # Response length (normalized)
        response_length = len(eval_data["response"])
        metrics["response_length"] = min(response_length / 1000, 1.0) * 100

        # Document utilization (if we have retrieved context)
        document_length = len(eval_data["document"])
        metrics["document_utilization"] = min(document_length / 1000, 1.0) * 100

        # Query-response overlap (simple keyword matching)
        query_words = set(eval_data["query"].lower().split())
        response_words = set(eval_data["response"].lower().split())
        if query_words:
            overlap = len(query_words.intersection(response_words)) / len(query_words)
            metrics["query_response_overlap"] = overlap * 100
        else:
            metrics["query_response_overlap"] = 0.0

        # Query-document overlap (context relevance)
        if eval_data["document"]:
            document_words = set(eval_data["document"].lower().split())
            if query_words:
                doc_overlap = len(query_words.intersection(document_words)) / len(query_words)
                metrics["query_document_overlap"] = doc_overlap * 100
            else:
                metrics["query_document_overlap"] = 0.0
        else:
            metrics["query_document_overlap"] = 0.0

        return metrics

    def calculate_local_rag_overall(self, local_rag_scores: Dict[str, float]) -> float:
        """Calculate overall local RAG score (weighted average)."""
        if not local_rag_scores:
            return 0.0

        # Use the predefined weights for evaluation metrics
        total_score = 0.0
        total_weight = 0.0

        for metric, score in local_rag_scores.items():
            weight = self.metric_weights.get(metric, 0.1)  # Default weight
            total_score += score * weight
            total_weight += weight

        # Return weighted average
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.0

    def compare_evaluations(self, custom_score: float, local_rag_overall: float) -> Dict[str, Any]:
        """Compare custom vs local RAG evaluation results."""
        difference = custom_score - local_rag_overall
        percentage_diff = (difference / custom_score * 100) if custom_score > 0 else 0

        if abs(percentage_diff) < 10:
            agreement = "High Agreement"
            recommendation = "Both evaluations are well-aligned"
        elif percentage_diff > 20:
            agreement = "Custom Higher"
            recommendation = "Custom evaluation may be too lenient"
        elif percentage_diff < -20:
            agreement = "Local RAG Higher"
            recommendation = "Local RAG evaluation may be more appropriate"
        else:
            agreement = "Moderate Agreement"
            recommendation = "Consider using local RAG as industry standard"

        return {
            "difference": difference,
            "percentage_diff": percentage_diff,
            "agreement": agreement,
            "recommendation": recommendation,
        }

    def evaluate_test_case(self, case_name: str, query: str, role: str = "planner") -> LocalRAGEvaluationResult:
        """Evaluate a single test case using both custom and local RAG evaluation."""

        # Run memory query
        response = self.run_memory_query(query, role)

        if not response["success"]:
            return LocalRAGEvaluationResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                local_rag_scores={},
                local_rag_overall=0.0,
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
            return LocalRAGEvaluationResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                local_rag_scores={},
                local_rag_overall=0.0,
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

        # Extract evaluation data
        eval_data = self.extract_evaluation_data(response, query)

        # Run local RAG evaluation
        local_rag_scores = self.run_local_rag_evaluation(eval_data)
        local_rag_overall = self.calculate_local_rag_overall(local_rag_scores)

        # Compare evaluations
        comparison = self.compare_evaluations(custom_score, local_rag_overall)

        return LocalRAGEvaluationResult(
            test_case_name=case_name,
            query=query,
            custom_score=custom_score,
            local_rag_scores=local_rag_scores,
            local_rag_overall=local_rag_overall,
            comparison=comparison,
            recommendation=comparison["recommendation"],
        )

    def run_local_rag_evaluation_suite(self) -> Dict[str, Any]:
        """Run local RAG evaluation on all baseline test cases."""

        print("🧠 Starting Local RAG Evaluation")
        print("📊 Local RAG Evaluation (No API Keys Required)")
        print("🦙 Using Ollama for Local Model Evaluation")
        print("=" * 60)

        # Get baseline test cases
        baseline_cases = self.baseline_evaluator.create_baseline_evaluation_cases()

        results = []
        custom_total = 0
        local_rag_total = 0

        for i, case in enumerate(baseline_cases, 1):
            print(f"\n🔍 Test {i}/{len(baseline_cases)}: {case.name}")
            print(f"   Query: {case.query}")

            # Run local RAG evaluation
            result = self.evaluate_test_case(case.name, case.query, case.role)

            results.append(result)
            custom_total += result.custom_score
            local_rag_total += result.local_rag_overall

            # Print results
            print(f"   Custom Score: {result.custom_score:.1f}/100")
            print(f"   Local RAG Score: {result.local_rag_overall:.1f}/100")
            print(f"   Agreement: {result.comparison['agreement']}")
            print(f"   Recommendation: {result.recommendation}")

        # Calculate averages
        custom_avg = custom_total / len(baseline_cases)
        local_rag_avg = local_rag_total / len(baseline_cases)

        # Overall comparison
        overall_comparison = self.compare_evaluations(custom_avg, local_rag_avg)

        print("\n" + "=" * 60)
        print("📊 LOCAL RAG EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Custom Average: {custom_avg:.1f}/100")
        print(f"🎯 Local RAG Average: {local_rag_avg:.1f}/100")
        print(f"📈 Difference: {overall_comparison['difference']:.1f} points")
        print(f"📊 Agreement: {overall_comparison['agreement']}")
        print(f"💡 Recommendation: {overall_comparison['recommendation']}")

        # Detailed local RAG metrics
        print("\n🔍 Local RAG Metrics Breakdown:")
        all_local_rag_scores = {}
        for result in results:
            for metric, score in result.local_rag_scores.items():
                if metric not in all_local_rag_scores:
                    all_local_rag_scores[metric] = []
                all_local_rag_scores[metric].append(score)

        for metric, scores in all_local_rag_scores.items():
            avg_score = sum(scores) / len(scores)
            print(f"   {metric}: {avg_score:.1f}/100")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            "timestamp": timestamp,
            "custom_average": custom_avg,
            "local_rag_average": local_rag_avg,
            "overall_comparison": overall_comparison,
            "local_rag_metrics_breakdown": {
                metric: sum(scores) / len(scores) for metric, scores in all_local_rag_scores.items()
            },
            "detailed_results": [
                {
                    "test_case": r.test_case_name,
                    "query": r.query,
                    "custom_score": r.custom_score,
                    "local_rag_scores": r.local_rag_scores,
                    "local_rag_overall": r.local_rag_overall,
                    "comparison": r.comparison,
                    "recommendation": r.recommendation,
                }
                for r in results
            ],
        }

        output_file = f"metrics/baseline_ragus_evaluations/local_rag_evaluation_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        return results_data


def main():
    """Run local RAG evaluation."""
    evaluator = LocalRAGEvaluator()
    results = evaluator.run_local_rag_evaluation_suite()

    # Print final recommendation
    print("\n🎯 FINAL RECOMMENDATION:")
    print(f"Based on the comparison between custom evaluation ({results['custom_average']:.1f}/100)")
    print(f"and local RAG evaluation ({results['local_rag_average']:.1f}/100):")
    print(f"→ {results['overall_comparison']['recommendation']}")

    print("\n📚 Local RAG Evaluation Reference:")
    print("Package: rag-evaluation")
    print("Features: Local evaluation, no API keys, Ollama support")
    print("Metrics: Query relevance, factual accuracy, coverage, coherence, fluency")


if __name__ == "__main__":
    main()
