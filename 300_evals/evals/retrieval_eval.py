#!/usr/bin/env python3
"""
Pydantic Evals framework for retrieval evaluation.

This module demonstrates how to use the new Pydantic Evals framework
for comprehensive retrieval evaluation with custom evaluators.
"""

import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataclasses import dataclass

import logfire
from pydantic import BaseModel, ConfigDict
from pydantic_evals.dataset import Case, Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from scripts.migrate_to_pydantic_evals import create_pydantic_evals_dataset, load_eval_cases
from scripts.observability import init_observability

# Define input/output models for retrieval evaluation
class RetrievalInput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    query: str
    mode: str
    tags: list[str]
    category: str | None = None
    notes: str | None = None

class RetrievalOutput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    retrieved_docs: list[str] = []
    citations: list[str] = []
    confidence: float | None = None
    retrieval_time_ms: int | None = None

# Custom evaluators for retrieval
@dataclass
class FileHitEvaluator(Evaluator[RetrievalInput, RetrievalOutput, dict]):
    """Evaluator that checks if expected files are retrieved."""

    def evaluate(self, ctx: EvaluatorContext[RetrievalInput, RetrievalOutput, dict]) -> float:
        """Evaluate if expected files are in retrieved documents."""
        expected_files = ctx.expected_output.get("expected_files", []) if ctx.expected_output else []
        retrieved_docs = ctx.output.retrieved_docs if ctx.output else []

        if not expected_files:
            # No expected files to check
            increment_eval_metric("file_hit", 1.0)
            return 1.0

        # Check if any expected file is in retrieved docs
        hits = 0
        for expected_file in expected_files:
            for retrieved_doc in retrieved_docs:
                if expected_file in retrieved_doc or retrieved_doc in expected_file:
                    hits += 1
                    break

        hit_rate = hits / len(expected_files) if expected_files else 1.0
        increment_eval_metric("file_hit", hit_rate)

        # Set evaluation attributes
        set_eval_attribute("expected_files_count", len(expected_files))
        set_eval_attribute("retrieved_docs_count", len(retrieved_docs))
        set_eval_attribute("file_hits", hits)

        return hit_rate

@dataclass
class ResponseTimeEvaluator(Evaluator[RetrievalInput, RetrievalOutput, dict]):
    """Evaluator that checks response time is within acceptable limits."""

    max_time_ms: int = 5000  # 5 seconds default

    def evaluate(self, ctx: EvaluatorContext[RetrievalInput, RetrievalOutput, dict]) -> float:
        """Evaluate if response time is acceptable."""
        retrieval_time = ctx.output.retrieval_time_ms if ctx.output else None

        if retrieval_time is None:
            # No timing information
            increment_eval_metric("response_time_ok", 0.0)
            return 0.0

        is_acceptable = retrieval_time <= self.max_time_ms
        score = 1.0 if is_acceptable else 0.0

        increment_eval_metric("response_time_ok", score)
        set_eval_attribute("retrieval_time_ms", retrieval_time)
        set_eval_attribute("max_time_ms", self.max_time_ms)

        return score

@dataclass
class ConfidenceEvaluator(Evaluator[RetrievalInput, RetrievalOutput, dict]):
    """Evaluator that checks confidence scores are reasonable."""

    min_confidence: float = 0.5

    def evaluate(self, ctx: EvaluatorContext[RetrievalInput, RetrievalOutput, dict]) -> float:
        """Evaluate if confidence score is reasonable."""
        confidence = ctx.output.confidence if ctx.output else None

        if confidence is None:
            # No confidence information
            increment_eval_metric("confidence_ok", 0.0)
            return 0.0

        is_reasonable = confidence >= self.min_confidence
        score = 1.0 if is_reasonable else 0.0

        increment_eval_metric("confidence_ok", score)
        set_eval_attribute("confidence", confidence)
        set_eval_attribute("min_confidence", self.min_confidence)

        return score

# Mock retrieval function for demonstration
async def mock_retrieval_task(inputs: RetrievalInput) -> RetrievalOutput:
    """Mock retrieval task for demonstration purposes."""
    import random
    import time

    # Simulate retrieval process
    start_time = time.time()

    # Mock retrieved documents based on query
    mock_docs = [f"doc_{i}.md" for i in range(random.randint(1, 5))]

    # Mock citations
    mock_citations = [f"citation_{i}" for i in range(random.randint(1, 3))]

    # Simulate processing time
    await asyncio.sleep(random.uniform(0.1, 0.5))

    retrieval_time = int((time.time() - start_time) * 1000)
    confidence = random.uniform(0.6, 0.95)

    return RetrievalOutput(
        retrieved_docs=mock_docs, citations=mock_citations, confidence=confidence, retrieval_time_ms=retrieval_time
    )

async def run_retrieval_evaluation():
    """Run comprehensive retrieval evaluation using Pydantic Evals."""
    # Initialize observability
    init_observability(service="retrieval-eval", environment="dev")

    with logfire.span("retrieval_evaluation") as span:
        span.set_attribute("evaluation_type", "retrieval")

        # Load legacy gold cases and convert to Pydantic Evals dataset
        print("Loading gold cases...")
        gold_cases = load_eval_cases("gold")
        print(f"Loaded {len(gold_cases)} gold cases")

        # Convert to Pydantic Evals dataset
        dataset = create_pydantic_evals_dataset(gold_cases)
        print(f"Created Pydantic Evals dataset with {len(dataset.cases)} cases")

        # Add custom evaluators to dataset
        evaluators = [
            FileHitEvaluator(),
            ResponseTimeEvaluator(max_time_ms=3000),
            ConfidenceEvaluator(min_confidence=0.7),
        ]

        for evaluator in evaluators:
            dataset.add_evaluator(evaluator)

        # Run evaluation
        print("Running retrieval evaluation...")

        report = await dataset.evaluate(mock_retrieval_task)

        # Print results
        print("\n" + "=" * 60)
        print("RETRIEVAL EVALUATION RESULTS")
        print("=" * 60)
        print(f"Total cases: {len(dataset.cases)}")
        print(f"Evaluation report: {report.summary_json(indent=2)}")

        span.set_attribute("total_cases", len(dataset.cases))
        span.set_attribute("evaluation_complete", True)

        return report

if __name__ == "__main__":
    import asyncio

    print("🚀 Starting Pydantic Evals Retrieval Evaluation")
    print("=" * 60)

    try:
        report = asyncio.run(run_retrieval_evaluation())
        print("\n✅ Retrieval evaluation completed successfully!")
        print("📊 Results available in Logfire dashboard")

    except Exception as e:
        print(f"\n❌ Error running retrieval evaluation: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
