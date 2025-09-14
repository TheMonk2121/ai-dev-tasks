from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from utils.hybrid_retriever import HybridRetriever, create_hybrid_retriever

from evaluation.enhanced_metrics import EnhancedEvaluator, QueryResult, load_golden_queries
from retrieval.cross_encoder_client import create_cross_encoder_client
from retrieval.deduplication import create_deduplicator
from retrieval.windowing import create_windower
from telemetry.request_logger import CanaryTagger, RequestLogger, log_rag_request

#!/usr/bin/env python3
"""
Phase 0/1 Integration Script

Demonstrates the complete Phase 0/1 RAG enhancement pipeline:
- Golden set evaluation with slices
- Per-request telemetry logging
- RRF fusion with windowing
- Near-duplicate suppression
- Cross-encoder reranking with fallback
- Singleflight caching and concurrency control
- Enhanced metrics (nDCG, Coverage, F1, ECE)

Usage:
    python scripts/phase01_integration.py --config config/retrieval.yaml --golden configs/eval/golden/
"""

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent))
# sys.path.insert(0, str(Path(__file__).parent.parent / "src"))  # DSPy modules now in main src directory
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import our Phase 0/1 components

# Import existing components
try:
    from utils.hybrid_retriever import create_hybrid_retriever
except ImportError:

    def create_hybrid_retriever(**kwargs):
        return HybridRetriever(**kwargs)


class Phase01Pipeline:
    """Complete Phase 0/1 RAG pipeline with all enhancements."""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)

        # Initialize telemetry
        telemetry_config = self.config.get("telemetry", {})
        self.request_logger = RequestLogger(
            log_path=telemetry_config.get("log_path", "metrics/logs/requests.jsonl"),
            enabled=telemetry_config.get("enabled", True),
        )

        canary_config = self.config.get("canary", {})
        self.canary_tagger = CanaryTagger(
            enabled=canary_config.get("enabled", False), sample_pct=canary_config.get("sample_pct", 10)
        )

        # Initialize Phase 1 components
        rerank_config = self.config.get("rerank", {})
        windowing_config = rerank_config.get("windowing", {})
        dedup_config = rerank_config.get("dedup", {})
        cross_encoder_config = rerank_config.get("cross_encoder", {})

        self.windower = create_windower(windowing_config) if windowing_config.get("enabled") else None
        self.deduplicator = create_deduplicator(dedup_config) if dedup_config.get("enabled") else None
        self.cross_encoder_client = None  # Will be created async if ONNX model exists

        # Initialize retriever
        self.retriever = self._create_retriever()

        # Initialize evaluator
        self.evaluator = EnhancedEvaluator()

        print("Phase 0/1 Pipeline initialized")
        print(f"  Telemetry: {self.request_logger.enabled}")
        print(f"  Canary: {self.canary_tagger.enabled}")
        print(f"  Windowing: {self.windower is not None}")
        print(f"  Deduplication: {self.deduplicator is not None}")
        print(f"  Cross-encoder: {cross_encoder_config.get('enabled', False)}")

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _create_retriever(self) -> HybridRetriever:
        """Create hybrid retriever with Phase 0/1 enhancements."""

        # Base configuration
        retriever_config = {
            "bm25_weight": self.config.get("fusion", {}).get("lambda_lex", 0.6),
            "dense_weight": self.config.get("fusion", {}).get("lambda_sem", 0.4),
            "stage1_top_k": self.config.get("candidates", {}).get("final_limit", 50),
            "stage2_top_k": self.config.get("rerank", {}).get("final_top_n", 8),
            # Phase 0/1 features
            "enable_windowing": self.config.get("rerank", {}).get("windowing", {}).get("enabled", True),
            "enable_dedup": self.config.get("rerank", {}).get("dedup", {}).get("enabled", True),
            "enable_cross_encoder": self.config.get("rerank", {}).get("cross_encoder", {}).get("model_name")
            is not None,
            "enable_singleflight": self.config.get("resilience", {}).get("singleflight", {}).get("enabled", True),
            "singleflight_ttl": self.config.get("resilience", {}).get("singleflight", {}).get("ttl_seconds", 30),
        }

        retriever = create_hybrid_retriever(**retriever_config)

        # Set Phase 0/1 components
        retriever.set_phase01_components(
            windower=self.windower, deduplicator=self.deduplicator, cross_encoder_client=self.cross_encoder_client
        )

        return retriever

    async def start(self):
        """Start background services."""
        await self.request_logger.start()

        # Initialize cross-encoder if configured
        cross_encoder_config = self.config.get("rerank", {}).get("cross_encoder", {})
        if cross_encoder_config.get("onnx_path"):
            try:
                self.cross_encoder_client = await create_cross_encoder_client(cross_encoder_config)
                self.retriever.set_phase01_components(cross_encoder_client=self.cross_encoder_client)
                print(f"Cross-encoder client initialized: {cross_encoder_config.get('model_name')}")
            except Exception as e:
                print(f"Failed to initialize cross-encoder: {e}")

    async def stop(self):
        """Stop background services."""
        await self.request_logger.stop()
        if self.cross_encoder_client:
            self.cross_encoder_client.close()

    async def process_query(self, query: str, expected_result: QueryResult | None = None) -> QueryResult:
        """
        Process a single query through the complete Phase 0/1 pipeline.

        Returns QueryResult with telemetry logged.
        """
        start_time = time.time()
        request_id = None

        try:
            # Generate canary tag
            canary_tag = None
            if self.canary_tagger.enabled:
                canary_tag = self.canary_tagger.get_tag(query)

            # Stage timing
            stage_timings = {}

            # Mock retrieval (replace with actual retrieval)
            stage_start = time.time()
            # retrieved_results = self.retriever.retrieve(query)

            # For demo, simulate retrieval results
            retrieved_results = [
                {"document_id": "doc1", "text": "Sample retrieved text about the query", "score": 0.8},
                {"document_id": "doc2", "text": "Another relevant passage", "score": 0.6},
            ]
            stage_timings["retrieval"] = (time.time() - stage_start) * 1000

            # Mock answer generation
            stage_start = time.time()
            predicted_answer = f"Generated answer for: {query}"
            confidence = 0.75
            stage_timings["generation"] = (time.time() - stage_start) * 1000

            # Create query result
            result = QueryResult(
                query=query,
                expected_answer=expected_result.expected_answer if expected_result else "",
                predicted_answer=predicted_answer,
                expected_spans=expected_result.expected_spans if expected_result else [],
                retrieved_spans=[doc["text"] for doc in retrieved_results],
                sub_claims=expected_result.sub_claims if expected_result else [],
                supported_claims=[],  # Would be computed by coverage calculator
                confidence=confidence,
                slice_tags=expected_result.slice_tags if expected_result else [],
            )

            # Log request with telemetry
            total_latency = (time.time() - start_time) * 1000
            request_id = await log_rag_request(
                query=query,
                answer=predicted_answer,
                canary_tag=canary_tag,
                confidence=confidence,
                stage_timings=stage_timings,
                vector_candidates=[{"doc": doc["document_id"], "score": doc["score"]} for doc in retrieved_results],
                total_latency_ms=total_latency,
            )

            print(f"✓ Processed query in {total_latency:.1f}ms (request_id: {request_id[:8]})")
            return result

        except Exception as e:
            error_latency = (time.time() - start_time) * 1000
            print(f"✗ Query failed after {error_latency:.1f}ms: {e}")

            # Log failed request
            if request_id:
                await log_rag_request(
                    query=query, answer=f"ERROR: {str(e)}", confidence=0.0, stage_timings={"error": error_latency}
                )

            # Return error result
            return QueryResult(
                query=query,
                expected_answer=expected_result.expected_answer if expected_result else "",
                predicted_answer=f"ERROR: {str(e)}",
                expected_spans=[],
                retrieved_spans=[],
                sub_claims=[],
                supported_claims=[],
                confidence=0.0,
                slice_tags=[],
            )

    async def evaluate_golden_set(self, golden_dir: str) -> dict[str, Any]:
        """
        Evaluate against golden query sets with comprehensive metrics.

        Returns evaluation results with slice breakdown.
        """
        print(f"Loading golden queries from {golden_dir}")

        golden_path = Path(golden_dir)
        all_results = []

        # Process each golden slice
        for slice_file in golden_path.glob("*.jsonl"):
            print(f"Processing slice: {slice_file.name}")

            golden_queries = load_golden_queries(str(slice_file))
            slice_results = []

            for golden_query in golden_queries:
                result = await self.process_query(query=golden_query.query, expected_result=golden_query)
                slice_results.append(result)
                all_results.append(result)

            print(f"  Completed {len(slice_results)} queries")

        # Compute comprehensive evaluation metrics
        print("Computing evaluation metrics...")
        metrics = self.evaluator.evaluate_batch(all_results, slice_breakdown=True)

        # Save results
        timestamp = int(time.time())
        results_file = f"metrics/phase01_evaluation_{timestamp}.json"
        self.evaluator.save_results(metrics, results_file)

        print(f"Evaluation complete! Results saved to {results_file}")
        return {"metrics": metrics, "results_file": results_file, "query_count": len(all_results)}


async def main():
    parser = argparse.ArgumentParser(description="Phase 0/1 RAG Pipeline Demo")
    parser.add_argument("--config", default="config/retrieval.yaml", help="Config file path")
    parser.add_argument("--golden", default="configs/eval/golden/", help="Golden queries directory")
    parser.add_argument("--single-query", help="Run single query for testing")

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = Phase01Pipeline(args.config)

    try:
        await pipeline.start()

        if args.single_query:
            # Single query demo
            print(f"Processing single query: {args.single_query}")
            result = await pipeline.process_query(args.single_query)
            print(f"Answer: {result.predicted_answer}")
            print(f"Confidence: {result.confidence}")

        else:
            # Full golden set evaluation
            evaluation = await pipeline.evaluate_golden_set(args.golden)

            # Print summary
            metrics = evaluation["metrics"]
            print("\n" + "=" * 50)
            print("PHASE 0/1 EVALUATION SUMMARY")
            print("=" * 50)
            print(f"Queries processed: {evaluation['query_count']}")
            print(f"nDCG@10: {metrics.ndcg_10:.3f}")
            print(f"Coverage: {metrics.coverage:.3f}")
            print(f"Exact Match: {metrics.exact_match:.3f}")
            print(f"Span Support: {metrics.span_support:.3f}")
            print(f"F1 Score: {metrics.f1_score:.3f}")
            print(f"ECE: {metrics.ece:.3f}")

            if metrics.temperature_param:
                print(f"Temperature: {metrics.temperature_param:.3f}")

            if metrics.slice_metrics:
                print("\nSlice Breakdown:")
                for slice_name, slice_metrics in metrics.slice_metrics.items():
                    print(
                        f"  {slice_name}: F1={slice_metrics['f1_score']:.3f}, Coverage={slice_metrics['coverage']:.3f}"
                    )

    finally:
        await pipeline.stop()


if __name__ == "__main__":
    asyncio.run(main())
