#!/usr/bin/env python3
"""
RAGChecker Batch Evaluation with Performance Optimization
Combines RAGChecker evaluation with batch processing for improved performance
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bedrock_batch_processor import BatchRequest, BedrockBatchProcessor
from bedrock_cost_monitor import BedrockCostMonitor
from ragchecker_official_evaluation import OfficialRAGCheckerEvaluator


class BatchRAGCheckerEvaluator(OfficialRAGCheckerEvaluator):
    """
    Enhanced RAGChecker evaluator with batch processing capabilities.

    Features:
    - Parallel evaluation processing
    - Intelligent batch sizing
    - Cost optimization
    - Performance monitoring
    """

    def __init__(self, max_concurrent: int = 3, batch_size: int = 10):
        """
        Initialize batch evaluator.

        Args:
            max_concurrent: Maximum concurrent requests
            batch_size: Batch size for processing
        """
        super().__init__()
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.batch_processor = None
        self.cost_monitor = BedrockCostMonitor()

    def run_batch_evaluation(
        self, use_bedrock: bool = True, optimize_batch_size: bool = False, export_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run RAGChecker evaluation using batch processing.

        Args:
            use_bedrock: Use AWS Bedrock for evaluation
            optimize_batch_size: Automatically optimize batch size
            export_results: Export detailed results

        Returns:
            Evaluation results dictionary
        """
        print("🚀 RAGChecker Batch Evaluation")
        print("=" * 60)

        # Pre-evaluation cost check
        print("\n💰 Pre-Evaluation Cost Check:")
        pre_eval_summary = self.cost_monitor.get_usage_summary("today")
        alerts = self.cost_monitor.check_budget_alerts()

        if alerts:
            print("⚠️  Budget alerts:")
            for alert in alerts:
                print(f"   {alert['message']}")
        else:
            print("✅ Budget status: OK")

        # Initialize batch processor
        if use_bedrock:
            from bedrock_client import BedrockClient

            bedrock_client = BedrockClient()

            # Test connection
            if not bedrock_client.test_connection():
                print("❌ Bedrock connection failed, falling back to local evaluation")
                return self.run_official_evaluation(use_local_llm=True)

            self.batch_processor = BedrockBatchProcessor(
                bedrock_client=bedrock_client, max_concurrent=self.max_concurrent, batch_size=self.batch_size
            )
            print(f"☁️ Using AWS Bedrock with batch processing (concurrent: {self.max_concurrent})")
        else:
            print("🏠 Batch processing requires Bedrock, falling back to local evaluation")
            return self.run_official_evaluation(use_local_llm=True)

        # Prepare test cases
        print("\n📋 Preparing test cases...")
        input_data = self.prepare_official_input_data()
        print(f"✅ Created {len(input_data)} test cases")

        # Optimize batch size if requested
        if optimize_batch_size and len(input_data) >= 5:
            print("\n🔧 Optimizing batch size...")
            sample_requests = self._create_sample_requests(input_data[:5])
            optimal_size = self.batch_processor.optimize_batch_size(sample_requests)
            self.batch_processor.batch_size = optimal_size
            print(f"✅ Using optimized batch size: {optimal_size}")

        # Process evaluation in batches
        print(f"\n🔄 Processing {len(input_data)} evaluations in batches...")
        start_time = time.time()

        all_responses = []
        for i in range(0, len(input_data), self.batch_size):
            batch = input_data[i : i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(input_data) + self.batch_size - 1) // self.batch_size

            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} cases)")

            # Convert to batch requests
            batch_requests = []
            for j, case in enumerate(batch):
                # Generate response using memory system
                raw_response = self.get_memory_system_response(case["query"])

                # Apply word limit if enabled
                if os.getenv("RAGCHECKER_CONCISE", "1") == "1":
                    max_words = int(os.getenv("RAGCHECKER_MAX_WORDS", "1000"))
                    response = self._apply_word_limit(raw_response, max_words)
                else:
                    response = raw_response

                # Update case with response
                case["response"] = response

                # Create evaluation prompt
                eval_prompt = self._build_evaluation_prompt(case)

                request = BatchRequest(
                    request_id=f"batch_{batch_num}_case_{j+1}_{case.get('query_id', f'case_{j+1}')}",
                    prompt=eval_prompt,
                    max_tokens=150,
                    temperature=0.1,
                    use_json_prompt=True,
                )
                batch_requests.append(request)

            # Process batch
            batch_responses = self.batch_processor.process_batch_sync(batch_requests)
            all_responses.extend(batch_responses)

            # Show batch progress
            batch_success_rate = sum(1 for r in batch_responses if r.success) / len(batch_responses)
            batch_cost = sum(r.usage.total_cost for r in batch_responses)
            print(f"✅ Batch {batch_num} completed: {batch_success_rate:.1%} success, ${batch_cost:.6f}")

        total_time = time.time() - start_time

        # Process results
        print("\n📊 Processing evaluation results...")
        case_results = []
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        for i, (case, response) in enumerate(zip(input_data, all_responses)):
            if response.success:
                try:
                    # Parse evaluation scores from JSON response
                    scores = self._parse_evaluation_scores(response.response_text)
                    precision = scores.get("precision", 0.0)
                    recall = scores.get("recall", 0.0)
                    f1_score = scores.get("f1_score", 0.0)
                except Exception as e:
                    print(f"⚠️ Failed to parse scores for {case.get('query_id', f'case_{i+1}')}: {e}")
                    precision = recall = f1_score = 0.0
            else:
                precision = recall = f1_score = 0.0

            case_result = {
                "query_id": case.get("query_id", f"case_{i+1}"),
                "query": case["query"],
                "response": case["response"],
                "gt_answer": case["gt_answer"],
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "evaluation_cost": response.usage.total_cost,
                "processing_time": response.processing_time,
                "success": response.success,
            }

            case_results.append(case_result)
            total_precision += precision
            total_recall += recall
            total_f1 += f1_score

        # Calculate averages
        num_cases = len(input_data)
        avg_precision = total_precision / num_cases if num_cases > 0 else 0
        avg_recall = total_recall / num_cases if num_cases > 0 else 0
        avg_f1 = total_f1 / num_cases if num_cases > 0 else 0

        # Get performance metrics
        performance_metrics = self.batch_processor.get_performance_metrics()

        # Post-evaluation cost analysis
        post_eval_summary = self.cost_monitor.get_usage_summary("today")
        eval_cost = post_eval_summary.total_cost - pre_eval_summary.total_cost

        # Compile results
        results = {
            "evaluation_type": "batch_bedrock_evaluation",
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
            "total_cases": num_cases,
            "processing_time": total_time,
            "overall_metrics": {"precision": avg_precision, "recall": avg_recall, "f1_score": avg_f1},
            "performance_metrics": {
                "requests_per_second": num_cases / total_time,
                "avg_processing_time": total_time / num_cases,
                "total_cost": eval_cost,
                "cost_per_case": eval_cost / num_cases if num_cases > 0 else 0,
                "batch_efficiency": performance_metrics["success_rate"],
            },
            "batch_configuration": {
                "max_concurrent": self.max_concurrent,
                "batch_size": self.batch_size,
                "total_batches": (num_cases + self.batch_size - 1) // self.batch_size,
            },
            "case_results": case_results,
        }

        # Export results if requested
        if export_results:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            results_file = self.metrics_dir / f"batch_ragchecker_evaluation_{timestamp}.json"

            with open(results_file, "w") as f:
                import json

                json.dump(results, f, indent=2)

            print(f"\n💾 Results exported: {results_file}")

        # Print summary
        self._print_batch_summary(results)

        return results

    def _create_sample_requests(self, sample_cases: List[Dict[str, Any]]) -> List[BatchRequest]:
        """Create sample requests for batch optimization."""
        requests = []
        for i, case in enumerate(sample_cases):
            prompt = f"Evaluate this test case: {case['query'][:100]}..."
            request = BatchRequest(request_id=f"sample_{i}", prompt=prompt, max_tokens=100, use_json_prompt=True)
            requests.append(request)
        return requests

    def _build_evaluation_prompt(self, case: Dict[str, Any]) -> str:
        """Build evaluation prompt for a test case."""
        context_text = "\n".join(case.get("retrieved_context", []))

        prompt = f"""
Evaluate this RAG system response for precision and recall.

Query: {case['query']}

Context: {context_text}

Ground Truth: {case['gt_answer']}

Response: {case['response']}

Provide evaluation scores in JSON format:
{{
    "precision": 0.8,
    "recall": 0.7,
    "f1_score": 0.75,
    "reasoning": "Brief explanation of the scores"
}}

Score range: 0.0 to 1.0
"""
        return prompt

    def _parse_evaluation_scores(self, response_text: str) -> Dict[str, float]:
        """Parse evaluation scores from JSON response."""
        import json
        import re

        try:
            # Try direct JSON parsing
            scores = json.loads(response_text)
            return {
                "precision": float(scores.get("precision", 0.0)),
                "recall": float(scores.get("recall", 0.0)),
                "f1_score": float(scores.get("f1_score", 0.0)),
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            # Fallback to regex extraction
            precision_match = re.search(r'"precision":\s*([0-9.]+)', response_text)
            recall_match = re.search(r'"recall":\s*([0-9.]+)', response_text)
            f1_match = re.search(r'"f1_score":\s*([0-9.]+)', response_text)

            return {
                "precision": float(precision_match.group(1)) if precision_match else 0.0,
                "recall": float(recall_match.group(1)) if recall_match else 0.0,
                "f1_score": float(f1_match.group(1)) if f1_match else 0.0,
            }

    def _apply_word_limit(self, text: str, max_words: int) -> str:
        """Apply word limit to text."""
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]) + "..."

    def _print_batch_summary(self, results: Dict[str, Any]):
        """Print formatted batch evaluation summary."""
        print("\n🎯 Batch RAGChecker Evaluation Summary")
        print("=" * 60)

        metrics = results["overall_metrics"]
        perf = results["performance_metrics"]
        config = results["batch_configuration"]

        print("📊 Evaluation Metrics:")
        print(f"   Precision: {metrics['precision']:.3f}")
        print(f"   Recall: {metrics['recall']:.3f}")
        print(f"   F1 Score: {metrics['f1_score']:.3f}")

        print("\n⚡ Performance Metrics:")
        print(f"   Total Cases: {results['total_cases']}")
        print(f"   Processing Time: {results['processing_time']:.1f}s")
        print(f"   Requests/Second: {perf['requests_per_second']:.2f}")
        print(f"   Total Cost: ${perf['total_cost']:.6f}")
        print(f"   Cost/Case: ${perf['cost_per_case']:.6f}")
        print(f"   Batch Efficiency: {perf['batch_efficiency']:.1%}")

        print("\n🔧 Batch Configuration:")
        print(f"   Max Concurrent: {config['max_concurrent']}")
        print(f"   Batch Size: {config['batch_size']}")
        print(f"   Total Batches: {config['total_batches']}")


def main():
    """Main function for batch evaluation CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="RAGChecker Batch Evaluation with Performance Optimization")
    parser.add_argument("--concurrent", type=int, default=3, help="Maximum concurrent requests")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size for processing")
    parser.add_argument("--optimize", action="store_true", help="Optimize batch size automatically")
    parser.add_argument("--no-export", action="store_true", help="Skip exporting detailed results")
    parser.add_argument("--cost-summary", action="store_true", help="Show cost summary only")

    args = parser.parse_args()

    if args.cost_summary:
        monitor = BedrockCostMonitor()
        monitor.print_cost_summary("today")
        return 0

    # Initialize batch evaluator
    evaluator = BatchRAGCheckerEvaluator(max_concurrent=args.concurrent, batch_size=args.batch_size)

    # Run batch evaluation
    try:
        results = evaluator.run_batch_evaluation(
            use_bedrock=True, optimize_batch_size=args.optimize, export_results=not args.no_export
        )

        if results:
            print("\n✅ Batch evaluation completed successfully!")
            return 0
        else:
            print("\n❌ Batch evaluation failed!")
            return 1

    except Exception as e:
        print(f"\n❌ Batch evaluation error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
