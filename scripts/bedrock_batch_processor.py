#!/usr/bin/env python3
"""
AWS Bedrock Batch Processing System
Implements batch processing and parallel evaluation for improved performance and cost efficiency
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from bedrock_client import BedrockClient, BedrockUsage


@dataclass
class BatchRequest:
    """Individual request in a batch."""

    request_id: str
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.1
    system_prompt: str | None = None
    use_json_prompt: bool = False


@dataclass
class BatchResponse:
    """Response from batch processing."""

    request_id: str
    response_text: str
    usage: BedrockUsage
    processing_time: float
    success: bool = True
    error: str | None = None


class BedrockBatchProcessor:
    """
    Batch processing system for AWS Bedrock requests.

    Features:
    - Parallel request processing with configurable concurrency
    - Intelligent batching with size optimization
    - Rate limiting and retry logic
    - Cost optimization through request grouping
    - Progress tracking and monitoring
    """

    def __init__(
        self,
        bedrock_client: BedrockClient | None = None,
        max_concurrent: int = 5,
        batch_size: int = 10,
        rate_limit_delay: float = 0.1,
    ):
        """
        Initialize batch processor.

        Args:
            bedrock_client: BedrockClient instance (creates new if None)
            max_concurrent: Maximum concurrent requests
            batch_size: Optimal batch size for processing
            rate_limit_delay: Delay between requests to avoid rate limiting
        """
        self.bedrock_client = bedrock_client or BedrockClient()
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.rate_limit_delay = rate_limit_delay

        # Tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_usage = BedrockUsage()

    def process_batch_sync(self, requests: list[BatchRequest]) -> list[BatchResponse]:
        """
        Process batch of requests synchronously with threading.

        Args:
            requests: List of BatchRequest objects

        Returns:
            List of BatchResponse objects
        """
        print(f"🔄 Processing batch of {len(requests)} requests (max concurrent: {self.max_concurrent})")

        responses = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit all requests
            future_to_request = {executor.submit(self._process_single_request, req): req for req in requests}

            # Collect results as they complete
            for future in as_completed(future_to_request):
                request = future_to_request[future]
                try:
                    response = future.result()
                    responses.append(response)

                    if response.success:
                        self.successful_requests += 1
                        self._update_total_usage(response.usage)
                    else:
                        self.failed_requests += 1

                    # Progress update
                    completed = len(responses)
                    progress = (completed / len(requests)) * 100
                    print(
                        f"📊 Progress: {completed}/{len(requests)} ({progress:.1f}%) - "
                        f"Latest: {response.request_id} ({'✅' if response.success else '❌'})"
                    )

                except Exception as e:
                    print(f"⚠️ Request {request.request_id} failed with exception: {e}")
                    responses.append(
                        BatchResponse(
                            request_id=request.request_id,
                            response_text="",
                            usage=BedrockUsage(),
                            processing_time=0.0,
                            success=False,
                            error=str(e),
                        )
                    )
                    self.failed_requests += 1

        total_time = time.time() - start_time
        self.total_requests += len(requests)

        print(f"✅ Batch completed in {total_time:.2f}s")
        print(
            f"📊 Success rate: {self.successful_requests}/{self.total_requests} "
            f"({(self.successful_requests/self.total_requests*100):.1f}%)"
        )

        return responses

    def _process_single_request(self, request: BatchRequest) -> BatchResponse:
        """Process a single request with timing and error handling."""
        start_time = time.time()

        try:
            # Add rate limiting delay
            time.sleep(self.rate_limit_delay)

            if request.use_json_prompt:
                response_text, usage = self.bedrock_client.invoke_with_json_prompt(
                    prompt=request.prompt, max_tokens=request.max_tokens, temperature=request.temperature
                )
            else:
                response_text, usage = self.bedrock_client.invoke_model(
                    prompt=request.prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system_prompt=request.system_prompt,
                )

            processing_time = time.time() - start_time

            return BatchResponse(
                request_id=request.request_id,
                response_text=response_text,
                usage=usage,
                processing_time=processing_time,
                success=True,
            )

        except Exception as e:
            processing_time = time.time() - start_time

            return BatchResponse(
                request_id=request.request_id,
                response_text="",
                usage=BedrockUsage(),
                processing_time=processing_time,
                success=False,
                error=str(e),
            )

    def _update_total_usage(self, usage: BedrockUsage):
        """Update total usage statistics."""
        self.total_usage.input_tokens += usage.input_tokens
        self.total_usage.output_tokens += usage.output_tokens
        self.total_usage.request_count += usage.request_count
        self.total_usage.total_cost += usage.total_cost

    def process_ragchecker_batch(self, test_cases: list[dict[str, Any]]) -> list[BatchResponse]:
        """
        Process RAGChecker test cases in batch.

        Args:
            test_cases: List of RAGChecker test case dictionaries

        Returns:
            List of BatchResponse objects
        """
        print(f"🧠 Processing RAGChecker batch: {len(test_cases)} test cases")

        # Convert test cases to batch requests
        batch_requests = []
        for i, case in enumerate(test_cases):
            # Build RAGChecker evaluation prompt
            prompt = self._build_ragchecker_prompt(case)

            request = BatchRequest(
                request_id=f"ragchecker_{i+1}",
                prompt=prompt,
                max_tokens=1000,
                temperature=0.1,
                use_json_prompt=True,  # Use JSON for better parsing
            )
            batch_requests.append(request)

        return self.process_batch_sync(batch_requests)

    def _build_ragchecker_prompt(self, test_case: dict[str, Any]) -> str:
        """Build RAGChecker evaluation prompt from test case."""
        query = test_case.get("query", "")
        context = test_case.get("retrieved_context", [])
        gt_answer = test_case.get("gt_answer", "")

        context_text = "\n".join(context) if isinstance(context, list) else str(context)

        prompt = f"""
Evaluate this RAG system response for precision and recall.

Query: {query}

Context: {context_text}

Ground Truth: {gt_answer}

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

    def optimize_batch_size(self, sample_requests: list[BatchRequest], target_time: float = 60.0) -> int:
        """
        Optimize batch size based on performance testing.

        Args:
            sample_requests: Sample requests for testing
            target_time: Target processing time in seconds

        Returns:
            Optimal batch size
        """
        print(f"🔧 Optimizing batch size (target: {target_time}s)")

        if len(sample_requests) < 3:
            print("⚠️ Not enough sample requests for optimization")
            return self.batch_size

        # Test different batch sizes
        test_sizes = [1, 3, 5, 10]
        results = {}

        for size in test_sizes:
            if size > len(sample_requests):
                continue

            print(f"📊 Testing batch size: {size}")
            test_batch = sample_requests[:size]

            start_time = time.time()
            responses = self.process_batch_sync(test_batch)
            elapsed_time = time.time() - start_time

            # Calculate throughput (requests per second)
            throughput = len(responses) / elapsed_time if elapsed_time > 0 else 0

            # Calculate projected time for full batch
            projected_time = len(sample_requests) / throughput if throughput > 0 else float("inf")

            results[size] = {
                "throughput": throughput,
                "projected_time": projected_time,
                "success_rate": sum(1 for r in responses if r.success) / len(responses),
            }

            print(f"   Throughput: {throughput:.2f} req/s, Projected: {projected_time:.1f}s")

        # Find optimal batch size closest to target time
        optimal_size = self.batch_size
        best_score = float("inf")

        for size, metrics in results.items():
            # Score based on how close to target time and success rate
            time_score = abs(metrics["projected_time"] - target_time)
            success_penalty = (1.0 - metrics["success_rate"]) * 100  # Penalty for failures
            total_score = time_score + success_penalty

            if total_score < best_score:
                best_score = total_score
                optimal_size = size

        print(f"✅ Optimal batch size: {optimal_size}")
        return optimal_size

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "total_usage": {
                "input_tokens": self.total_usage.input_tokens,
                "output_tokens": self.total_usage.output_tokens,
                "total_cost": self.total_usage.total_cost,
                "request_count": self.total_usage.request_count,
            },
            "avg_cost_per_request": (
                self.total_usage.total_cost / self.successful_requests if self.successful_requests > 0 else 0
            ),
            "configuration": {
                "max_concurrent": self.max_concurrent,
                "batch_size": self.batch_size,
                "rate_limit_delay": self.rate_limit_delay,
            },
        }

    def export_results(self, responses: list[BatchResponse], output_file: str):
        """Export batch processing results to file."""
        results = {
            "batch_summary": {
                "total_requests": len(responses),
                "successful_requests": sum(1 for r in responses if r.success),
                "failed_requests": sum(1 for r in responses if not r.success),
                "total_cost": sum(r.usage.total_cost for r in responses),
                "total_processing_time": sum(r.processing_time for r in responses),
            },
            "responses": [
                {
                    "request_id": r.request_id,
                    "success": r.success,
                    "response_text": r.response_text[:200] + "..." if len(r.response_text) > 200 else r.response_text,
                    "usage": r.usage.to_dict(),
                    "processing_time": r.processing_time,
                    "error": r.error,
                }
                for r in responses
            ],
            "performance_metrics": self.get_performance_metrics(),
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📄 Results exported to: {output_path}")


def main():
    """Main function for batch processing CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="AWS Bedrock Batch Processing System")
    parser.add_argument("--test-batch", type=int, default=5, help="Number of test requests to process")
    parser.add_argument("--concurrent", type=int, default=3, help="Maximum concurrent requests")
    parser.add_argument("--optimize", action="store_true", help="Run batch size optimization")
    parser.add_argument("--export", type=str, help="Export results to file")

    args = parser.parse_args()

    # Initialize batch processor
    processor = BedrockBatchProcessor(max_concurrent=args.concurrent)

    if args.optimize:
        # Create sample requests for optimization
        sample_requests = [
            BatchRequest(
                request_id=f"test_{i}", prompt=f"Test prompt {i}: What is 2+{i}? Respond briefly.", max_tokens=50
            )
            for i in range(1, 6)
        ]

        optimal_size = processor.optimize_batch_size(sample_requests)
        print(f"🎯 Recommended batch size: {optimal_size}")

    else:
        # Create test batch
        test_requests = [
            BatchRequest(
                request_id=f"test_{i}",
                prompt=f"Test request {i}: Calculate {i} * 2 and explain briefly.",
                max_tokens=100,
                use_json_prompt=True,
            )
            for i in range(1, args.test_batch + 1)
        ]

        print(f"🚀 Processing test batch of {len(test_requests)} requests...")
        responses = processor.process_batch_sync(test_requests)

        # Show results
        print("\n📊 Batch Processing Results:")
        for response in responses:
            status = "✅" if response.success else "❌"
            print(
                f"   {status} {response.request_id}: {response.processing_time:.2f}s, ${response.usage.total_cost:.6f}"
            )

        # Show performance metrics
        metrics = processor.get_performance_metrics()
        print("\n🎯 Performance Summary:")
        print(f"   Success Rate: {metrics['success_rate']:.1%}")
        print(f"   Total Cost: ${metrics['total_usage']['total_cost']:.6f}")
        print(f"   Avg Cost/Request: ${metrics['avg_cost_per_request']:.6f}")

        # Export if requested
        if args.export:
            processor.export_results(responses, args.export)


if __name__ == "__main__":
    main()
