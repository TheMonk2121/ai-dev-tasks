#!/usr/bin/env python3
"""
Simple Local RAG Evaluation System

This module implements a simplified local RAG evaluation using basic metrics
that don't require LLM evaluation, avoiding safety issues with local models.

Features:
- Query-response overlap analysis
- Document utilization metrics
- Response length analysis
- Context relevance scoring
- No LLM dependencies
- No API keys required
"""

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from baseline_ragus_evaluation import BaselineEvaluator


@dataclass
class SimpleLocalRAGEvaluationResult:
    """Result of simple local RAG evaluation."""

    test_case_name: str
    query: str
    custom_score: float
    simple_rag_scores: Dict[str, float]
    simple_rag_overall: float
    comparison: Dict[str, Any]
    recommendation: str


class SimpleLocalRAGEvaluator:
    """Simple local RAG evaluator using basic metrics without LLM evaluation."""

    def __init__(self):
        self.baseline_evaluator = BaselineEvaluator()

        # Define metric weights for simple evaluation
        self.metric_weights = {
            "query_response_overlap": 0.30,  # How well response matches query
            "document_utilization": 0.25,  # How much context was used
            "response_completeness": 0.20,  # Response length and detail
            "context_relevance": 0.15,  # How relevant context is to query
            "response_coherence": 0.10,  # Basic coherence indicators
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
        """Extract data for simple RAG evaluation from memory system response."""
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

    def calculate_query_response_overlap(self, query: str, response: str) -> float:
        """Calculate how well the response matches the query."""
        # Normalize text
        query_words = set(re.findall(r"\b\w+\b", query.lower()))
        response_words = set(re.findall(r"\b\w+\b", response.lower()))

        if not query_words:
            return 0.0

        # Calculate overlap
        overlap = len(query_words.intersection(response_words))
        overlap_ratio = overlap / len(query_words)

        # Boost score for longer responses that contain query terms
        response_length_boost = min(len(response_words) / 50, 0.3)  # Max 30% boost

        return min((overlap_ratio + response_length_boost) * 100, 100.0)

    def calculate_document_utilization(self, document: str, response: str) -> float:
        """Calculate how much of the retrieved context was utilized."""
        if not document:
            return 0.0

        # Normalize text
        doc_words = set(re.findall(r"\b\w+\b", document.lower()))
        response_words = set(re.findall(r"\b\w+\b", response.lower()))

        if not doc_words:
            return 0.0

        # Calculate utilization
        utilized_words = len(doc_words.intersection(response_words))
        utilization_ratio = utilized_words / len(doc_words)

        return utilization_ratio * 100

    def calculate_response_completeness(self, response: str) -> float:
        """Calculate response completeness based on length and structure."""
        if not response:
            return 0.0

        # Length score (0-50 points)
        length_score = min(len(response) / 200, 1.0) * 50

        # Structure score (0-50 points)
        structure_indicators = 0
        if len(response.split(".")) > 2:  # Multiple sentences
            structure_indicators += 10
        if len(response.split("\n")) > 1:  # Multiple lines
            structure_indicators += 10
        if any(word in response.lower() for word in ["because", "therefore", "however", "additionally"]):
            structure_indicators += 15  # Logical connectors
        if re.search(r"\d+", response):  # Contains numbers
            structure_indicators += 5
        if re.search(r"[A-Z][a-z]+", response):  # Proper nouns
            structure_indicators += 10

        structure_score = min(structure_indicators, 50)

        return length_score + structure_score

    def calculate_context_relevance(self, query: str, document: str) -> float:
        """Calculate how relevant the retrieved context is to the query."""
        if not document:
            return 0.0

        # Normalize text
        query_words = set(re.findall(r"\b\w+\b", query.lower()))
        doc_words = set(re.findall(r"\b\w+\b", document.lower()))

        if not query_words:
            return 0.0

        # Calculate relevance
        relevant_words = len(query_words.intersection(doc_words))
        relevance_ratio = relevant_words / len(query_words)

        return relevance_ratio * 100

    def calculate_response_coherence(self, response: str) -> float:
        """Calculate basic response coherence indicators."""
        if not response:
            return 0.0

        coherence_score = 0

        # Sentence structure
        sentences = response.split(".")
        if len(sentences) > 1:
            coherence_score += 20

        # Paragraph structure
        paragraphs = response.split("\n\n")
        if len(paragraphs) > 1:
            coherence_score += 15

        # Logical flow indicators
        flow_words = ["first", "second", "then", "next", "finally", "therefore", "because", "however"]
        flow_count = sum(1 for word in flow_words if word in response.lower())
        coherence_score += min(flow_count * 5, 25)

        # Consistency (no obvious contradictions)
        contradiction_indicators = ["but", "however", "nevertheless", "on the other hand"]
        contradiction_count = sum(1 for word in contradiction_indicators if word in response.lower())
        coherence_score += min(contradiction_count * 3, 15)

        # Grammar and readability
        if len(response) > 50 and response.count(".") > 0:
            coherence_score += 25

        return min(coherence_score, 100.0)

    def run_simple_rag_evaluation(self, eval_data: Dict[str, str]) -> Dict[str, float]:
        """Run simple RAG evaluation using basic metrics."""
        try:
            query = eval_data["query"]
            response = eval_data["response"]
            document = eval_data["document"]

            # Calculate all metrics
            simple_rag_scores = {
                "query_response_overlap": self.calculate_query_response_overlap(query, response),
                "document_utilization": self.calculate_document_utilization(document, response),
                "response_completeness": self.calculate_response_completeness(response),
                "context_relevance": self.calculate_context_relevance(query, document),
                "response_coherence": self.calculate_response_coherence(response),
            }

            return simple_rag_scores

        except Exception as e:
            print(f"Simple RAG evaluation failed: {e}")
            return {
                "query_response_overlap": 0.0,
                "document_utilization": 0.0,
                "response_completeness": 0.0,
                "context_relevance": 0.0,
                "response_coherence": 0.0,
            }

    def calculate_simple_rag_overall(self, simple_rag_scores: Dict[str, float]) -> float:
        """Calculate overall simple RAG score (weighted average)."""
        if not simple_rag_scores:
            return 0.0

        # Calculate weighted average
        total_score = 0.0
        total_weight = 0.0

        for metric, score in simple_rag_scores.items():
            weight = self.metric_weights.get(metric, 0.1)  # Default weight
            total_score += score * weight
            total_weight += weight

        # Return weighted average
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.0

    def compare_evaluations(self, custom_score: float, simple_rag_overall: float) -> Dict[str, Any]:
        """Compare custom vs simple RAG evaluation results."""
        difference = custom_score - simple_rag_overall
        percentage_diff = (difference / custom_score * 100) if custom_score > 0 else 0

        if abs(percentage_diff) < 10:
            agreement = "High Agreement"
            recommendation = "Both evaluations are well-aligned"
        elif percentage_diff > 20:
            agreement = "Custom Higher"
            recommendation = "Custom evaluation may be too lenient"
        elif percentage_diff < -20:
            agreement = "Simple RAG Higher"
            recommendation = "Simple RAG evaluation may be more appropriate"
        else:
            agreement = "Moderate Agreement"
            recommendation = "Consider using simple RAG as baseline standard"

        return {
            "difference": difference,
            "percentage_diff": percentage_diff,
            "agreement": agreement,
            "recommendation": recommendation,
        }

    def evaluate_test_case(self, case_name: str, query: str, role: str = "planner") -> SimpleLocalRAGEvaluationResult:
        """Evaluate a single test case using both custom and simple RAG evaluation."""

        # Run memory query
        response = self.run_memory_query(query, role)

        if not response["success"]:
            return SimpleLocalRAGEvaluationResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                simple_rag_scores={},
                simple_rag_overall=0.0,
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
            return SimpleLocalRAGEvaluationResult(
                test_case_name=case_name,
                query=query,
                custom_score=0.0,
                simple_rag_scores={},
                simple_rag_overall=0.0,
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

        # Run simple RAG evaluation
        simple_rag_scores = self.run_simple_rag_evaluation(eval_data)
        simple_rag_overall = self.calculate_simple_rag_overall(simple_rag_scores)

        # Compare evaluations
        comparison = self.compare_evaluations(custom_score, simple_rag_overall)

        return SimpleLocalRAGEvaluationResult(
            test_case_name=case_name,
            query=query,
            custom_score=custom_score,
            simple_rag_scores=simple_rag_scores,
            simple_rag_overall=simple_rag_overall,
            comparison=comparison,
            recommendation=comparison["recommendation"],
        )

    def run_simple_rag_evaluation_suite(self) -> Dict[str, Any]:
        """Run simple RAG evaluation on all baseline test cases."""

        print("🧠 Starting Simple Local RAG Evaluation")
        print("📊 Simple RAG Evaluation (No LLM Required)")
        print("🔍 Using Basic Metrics Only")
        print("=" * 60)

        # Get baseline test cases
        baseline_cases = self.baseline_evaluator.create_baseline_evaluation_cases()

        results = []
        custom_total = 0
        simple_rag_total = 0

        for i, case in enumerate(baseline_cases, 1):
            print(f"\n🔍 Test {i}/{len(baseline_cases)}: {case.name}")
            print(f"   Query: {case.query}")

            # Run simple RAG evaluation
            result = self.evaluate_test_case(case.name, case.query, case.role)

            results.append(result)
            custom_total += result.custom_score
            simple_rag_total += result.simple_rag_overall

            # Print results
            print(f"   Custom Score: {result.custom_score:.1f}/100")
            print(f"   Simple RAG Score: {result.simple_rag_overall:.1f}/100")
            print(f"   Agreement: {result.comparison['agreement']}")
            print(f"   Recommendation: {result.recommendation}")

        # Calculate averages
        custom_avg = custom_total / len(baseline_cases)
        simple_rag_avg = simple_rag_total / len(baseline_cases)

        # Overall comparison
        overall_comparison = self.compare_evaluations(custom_avg, simple_rag_avg)

        print("\n" + "=" * 60)
        print("📊 SIMPLE RAG EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Custom Average: {custom_avg:.1f}/100")
        print(f"🎯 Simple RAG Average: {simple_rag_avg:.1f}/100")
        print(f"📈 Difference: {overall_comparison['difference']:.1f} points")
        print(f"📊 Agreement: {overall_comparison['agreement']}")
        print(f"💡 Recommendation: {overall_comparison['recommendation']}")

        # Detailed simple RAG metrics
        print("\n🔍 Simple RAG Metrics Breakdown:")
        all_simple_rag_scores = {}
        for result in results:
            for metric, score in result.simple_rag_scores.items():
                if metric not in all_simple_rag_scores:
                    all_simple_rag_scores[metric] = []
                all_simple_rag_scores[metric].append(score)

        for metric, scores in all_simple_rag_scores.items():
            avg_score = sum(scores) / len(scores)
            print(f"   {metric}: {avg_score:.1f}/100")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            "timestamp": timestamp,
            "custom_average": custom_avg,
            "simple_rag_average": simple_rag_avg,
            "overall_comparison": overall_comparison,
            "simple_rag_metrics_breakdown": {
                metric: sum(scores) / len(scores) for metric, scores in all_simple_rag_scores.items()
            },
            "detailed_results": [
                {
                    "test_case": r.test_case_name,
                    "query": r.query,
                    "custom_score": r.custom_score,
                    "simple_rag_scores": r.simple_rag_scores,
                    "simple_rag_overall": r.simple_rag_overall,
                    "comparison": r.comparison,
                    "recommendation": r.recommendation,
                }
                for r in results
            ],
        }

        output_file = f"metrics/baseline_ragus_evaluations/simple_rag_evaluation_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        return results_data


def main():
    """Run simple local RAG evaluation."""
    evaluator = SimpleLocalRAGEvaluator()
    results = evaluator.run_simple_rag_evaluation_suite()

    # Print final recommendation
    print("\n🎯 FINAL RECOMMENDATION:")
    print(f"Based on the comparison between custom evaluation ({results['custom_average']:.1f}/100)")
    print(f"and simple RAG evaluation ({results['simple_rag_average']:.1f}/100):")
    print(f"→ {results['overall_comparison']['recommendation']}")

    print("\n📚 Simple RAG Evaluation Reference:")
    print("Features: No LLM required, no API keys, basic metrics only")
    print("Metrics: Query overlap, document utilization, completeness, relevance, coherence")


if __name__ == "__main__":
    main()
