#!/usr/bin/env python3
"""
Enhanced RAGChecker Evaluation with Coach's Strategy
Integrates enhanced retrieval pipeline and answer generator
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add src to path for enhanced components
# sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project

from dspy_modules.enhanced_answer_generator import create_enhanced_generator
from dspy_modules.retrieval_pipeline import create_enhanced_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRAGCheckerEvaluator:
    """
    Enhanced RAGChecker evaluator implementing the coach's strategy
    """

    def __init__(self):
        # Initialize enhanced pipeline
        self.pipeline = create_enhanced_pipeline(
            max_tokens=300,
            overlap_tokens=64,
            bm25_weight=0.55,
            dense_weight=0.35,
            metadata_weight=0.10,
            stage1_top_k=24,
            stage2_top_k=8,
        )

        # Initialize enhanced answer generator
        self.generator = create_enhanced_generator(
            min_citations=2, max_answer_length=500, enable_abstention=True, code_formatting=True
        )

        logger.info("Enhanced RAGChecker evaluator initialized")

    def evaluate_query(
        self, query: str, query_type: str | None = None, enable_enhanced_features: bool = True
    ) -> dict[str, Any]:
        """
        Evaluate a single query with enhanced features
        """
        start_time = time.time()

        try:
            if enable_enhanced_features:
                # Use enhanced retrieval pipeline
                retrieved_chunks = self.pipeline.retrieve_with_context(query, query_type)

                # Generate enhanced answer
                result = self.generator.generate_enhanced_answer(query, retrieved_chunks, query_type)

                # Extract metrics
                answer = result
                validation = result
                metadata = result

                # Calculate enhanced metrics
                enhanced_metrics = {
                    "citations_count": result
                    "has_sufficient_context": result
                    "meets_citation_requirement": result
                    "chunk_diversity": result
                    "abstention": result
                    "query_type": result
                }

            else:
                # Fallback to basic evaluation (mock)
                answer = f"Basic answer for: {query}"
                enhanced_metrics = {
                    "citations_count": 0,
                    "has_sufficient_context": False,
                    "meets_citation_requirement": False,
                    "chunk_diversity": 1,
                    "abstention": False,
                    "query_type": "basic",
                }

            evaluation_time = time.time() - start_time

            return {
                "query": query,
                "answer": answer,
                "evaluation_time": evaluation_time,
                "enhanced_metrics": enhanced_metrics,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Evaluation failed for query '{query}': {e}")
            return {
                "query": query,
                "answer": f"Error: {str(e)}",
                "evaluation_time": time.time() - start_time,
                "enhanced_metrics": {
                    "citations_count": 0,
                    "has_sufficient_context": False,
                    "meets_citation_requirement": False,
                    "chunk_diversity": 0,
                    "abstention": False,
                    "query_type": "error",
                },
                "success": False,
                "error": str(e),
            }

    def run_enhanced_evaluation(self, test_cases: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Run enhanced evaluation on test cases
        """
        logger.info(f"Starting enhanced evaluation with {len(test_cases)} test cases")

        results = []
        total_time = 0

        for i, test_case in enumerate(test_cases):
            logger.info(f"Evaluating case {i+1}/{len(test_cases)}: {result

            query = result
            query_type = result

            # Run evaluation
            result = self.evaluate_query(query, query_type, enable_enhanced_features=True)
            results.append(result)

            total_time += result

            # Log progress
            logger.info(f"  ✅ Completed in {result
            if result:
                logger.info(f"  ⚠️  Abstention: {result
            else:
                logger.info(f"  📊 Citations: {result

        # Calculate enhanced metrics
        enhanced_summary = self._calculate_enhanced_summary(results)

        return {
            "results": results,
            "summary": enhanced_summary,
            "total_time": total_time,
            "avg_time_per_case": total_time / len(test_cases) if test_cases else 0,
        }

    def _calculate_enhanced_summary(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Calculate enhanced evaluation summary
        """
        total_cases = len(results)
        successful_cases = len([r for r in results if result:

        # Enhanced metrics
        total_citations = sum(result
        avg_citations = total_citations / total_cases if total_cases > 0 else 0

        context_sufficient = sum(1 for r in results if result:
        context_sufficiency_rate = context_sufficient / total_cases if total_cases > 0 else 0

        citation_requirement_met = sum(1 for r in results if result:
        citation_success_rate = citation_requirement_met / total_cases if total_cases > 0 else 0

        abstentions = sum(1 for r in results if result:
        abstention_rate = abstentions / total_cases if total_cases > 0 else 0

        # Query type distribution
        query_types = {}
        for result in results:
            query_type = result
            query_types[query_type] = result

        return {
            "total_cases": total_cases,
            "successful_cases": successful_cases,
            "success_rate": successful_cases / total_cases if total_cases > 0 else 0,
            "enhanced_metrics": {
                "avg_citations": avg_citations,
                "context_sufficiency_rate": context_sufficiency_rate,
                "citation_success_rate": citation_success_rate,
                "abstention_rate": abstention_rate,
                "total_citations": total_citations,
                "context_sufficient_cases": context_sufficient,
                "citation_requirement_met_cases": citation_requirement_met,
                "abstention_cases": abstentions,
            },
            "query_type_distribution": query_types,
            "pipeline_stats": self.pipeline.get_pipeline_stats(),
            "generator_stats": self.generator.get_generator_stats(),
        }

    def save_evaluation_results(self, results: dict[str, Any], filepath: str | None = None) -> str:
        """
        Save evaluation results to file
        """
        if not filepath:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filepath = f"metrics/enhanced_evaluations/enhanced_ragchecker_evaluation_{timestamp}.json"

        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Save results
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Enhanced evaluation results saved to: {filepath}")
        return filepath

def main():
    """Main function for enhanced evaluation"""

    # Sample test cases (replace with actual RAGChecker test cases)
    test_cases = [
        {
            "name": "dspy_implementation_001",
            "query": "How do I implement a DSPy module with custom optimization?",
            "type": "implementation",
        },
        {"name": "memory_system_001", "query": "Explain the LTST memory system architecture", "type": "explanatory"},
        {
            "name": "performance_001",
            "query": "How do I optimize RAG performance for large datasets?",
            "type": "optimization",
        },
        {
            "name": "error_handling_001",
            "query": "What are the best practices for error handling in DSPy?",
            "type": "troubleshooting",
        },
    ]

    print("🚀 Enhanced RAGChecker Evaluation")
    print("=" * 50)
    print("Implementing coach's strategy:")
    print("✅ Code-aware chunking + stitching")
    print("✅ Hybrid retrieval + reranking")
    print("✅ Answer discipline + citations")
    print("✅ Abstention for poor context")
    print()

    # Initialize evaluator
    evaluator = EnhancedRAGCheckerEvaluator()

    # Run evaluation
    print("🔍 Running enhanced evaluation...")
    results = evaluator.run_enhanced_evaluation(test_cases)

    # Display results
    print("\n📊 Enhanced Evaluation Results")
    print("=" * 40)

    summary = result
    enhanced_metrics = result

    print(f"📋 Total Cases: {result
    print(f"✅ Success Rate: {result
    print(f"⏱️  Total Time: {result
    print(f"⏱️  Avg Per Case: {result

    print("\n🎯 Enhanced Metrics:")
    print(f"  📚 Avg Citations: {result
    print(f"  🔍 Context Sufficiency: {result
    print(f"  ✅ Citation Success: {result
    print(f"  ⚠️  Abstention Rate: {result

    print("\n📊 Query Type Distribution:")
    for query_type, count in result
        print(f"  {query_type}: {count}")

    # Save results
    filepath = evaluator.save_evaluation_results(results)
    print(f"\n💾 Results saved to: {filepath}")

    print("\n🎯 Expected Impact:")
    print("  Current F1: 17.1%")
    print("  Target F1: 20.0%+")
    print("  Key improvements:")
    print("    - Code-aware chunking preserves function boundaries")
    print("    - Hybrid retrieval improves recall")
    print("    - Answer discipline improves precision")
    print("    - Abstention prevents hallucination")

    return results

if __name__ == "__main__":
    main()
