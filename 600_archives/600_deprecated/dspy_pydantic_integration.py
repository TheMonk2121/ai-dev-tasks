#!/usr/bin/env python3
"""
DEPRECATED: DSPy + Pydantic ecosystem integration demo.

Superseded by unified evaluation flow and v1 gold dataset. Keep only as
reference. Set ALLOW_DEPRECATED_SCRIPTS=1 to run anyway.
"""
import os, sys
if os.getenv("ALLOW_DEPRECATED_SCRIPTS") != "1":
    sys.stderr.write(
        "This demo is deprecated. Use scripts/smoke_eval_gate.py with evals/gold/v1/gold_cases.jsonl,\n"
        "or set ALLOW_DEPRECATED_SCRIPTS=1 to override.\n"
    )
    sys.exit(2)

import asyncio
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logfire
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.instrumented import InstrumentationSettings
from pydantic_ai.models.test import TestModel
from pydantic_evals.dataset import Case, Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from scripts.migrate_to_pydantic_evals import create_pydantic_evals_dataset, load_eval_cases
from scripts.observability import init_observability

# 1. PydanticAI Agent that can work with DSPy RAG system
class DSPyRAGAnswer(BaseModel):
    """Structured answer from DSPy RAG system."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    retrieval_metadata: dict[str, Any] = Field(default_factory=dict)

class DSPyRAGAgent:
    """PydanticAI agent that integrates with DSPy RAG system."""

    def __init__(self, dspy_rag_system=None):
        self.dspy_rag = dspy_rag_system
        self.agent = Agent(
            TestModel(),  # Use test model for demo
            system_prompt="You are a RAG assistant that provides structured answers with sources.",
            output_type=DSPyRAGAnswer,
            instrument=InstrumentationSettings(include_content=False),
        )

    async def query_rag_system(self, question: str) -> DSPyRAGAnswer:
        """Query the DSPy RAG system and return structured output."""

        with logfire.span("dspy_rag_query", question=question):
            set_eval_attribute("query_type", "rag")
            increment_eval_metric("rag_queries", 1)

            if self.dspy_rag:
                # Use real DSPy RAG system
                result = self.dspy_rag.forward(question)

                return DSPyRAGAnswer(
                    answer=result.get("answer", "No answer available"),
                    confidence=result.get("confidence", 0.5),
                    sources=result.get("sources", []),
                    retrieval_metadata=result.get("metadata", {}),
                )
            else:
                # Mock response for demonstration
                return DSPyRAGAnswer(
                    answer=f"Mock answer for: {question}",
                    confidence=0.85,
                    sources=["doc1.md", "doc2.md"],
                    retrieval_metadata={"retrieval_time_ms": 150, "num_docs": 2},
                )

# 2. Pydantic Evals evaluators for DSPy RAG system
class DSPyRAGEvaluator(Evaluator[DSPyRAGAnswer, DSPyRAGAnswer, dict]):
    """Evaluator for DSPy RAG system responses."""

    def evaluate(self, ctx: EvaluatorContext[DSPyRAGAnswer, DSPyRAGAnswer, dict]) -> float:
        """Evaluate DSPy RAG response quality."""

        if not ctx.output:
            increment_eval_metric("dspy_rag_quality", 0.0)
            return 0.0

        # Check if answer is present and non-empty
        answer_quality = 1.0 if ctx.output.answer and len(ctx.output.answer.strip()) > 0 else 0.0

        # Check confidence score
        confidence_quality = ctx.output.confidence if ctx.output.confidence else 0.0

        # Check if sources are provided
        sources_quality = 1.0 if ctx.output.sources else 0.0

        # Overall quality score
        overall_quality = (answer_quality + confidence_quality + sources_quality) / 3.0

        increment_eval_metric("dspy_rag_quality", overall_quality)
        set_eval_attribute("answer_length", len(ctx.output.answer) if ctx.output.answer else 0)
        set_eval_attribute("num_sources", len(ctx.output.sources))
        set_eval_attribute("confidence", ctx.output.confidence)

        return overall_quality

class DSPyRetrievalEvaluator(Evaluator[DSPyRAGAnswer, DSPyRAGAnswer, dict]):
    """Evaluator for DSPy retrieval performance."""

    def evaluate(self, ctx: EvaluatorContext[DSPyRAGAnswer, DSPyRAGAnswer, dict]) -> float:
        """Evaluate retrieval performance."""

        if not ctx.output:
            increment_eval_metric("dspy_retrieval_quality", 0.0)
            return 0.0

        # Check retrieval metadata
        metadata = ctx.output.retrieval_metadata
        retrieval_time = metadata.get("retrieval_time_ms", 0)
        num_docs = metadata.get("num_docs", 0)

        # Time-based score (faster is better, up to 1000ms)
        time_score = max(0.0, 1.0 - (retrieval_time / 1000.0))

        # Document count score (more docs is better, up to 10)
        docs_score = min(1.0, num_docs / 10.0)

        # Overall retrieval score
        retrieval_score = (time_score + docs_score) / 2.0

        increment_eval_metric("dspy_retrieval_quality", retrieval_score)
        set_eval_attribute("retrieval_time_ms", retrieval_time)
        set_eval_attribute("num_retrieved_docs", num_docs)

        return retrieval_score

async def evaluate_dspy_rag_system():
    """Evaluate DSPy RAG system using Pydantic Evals framework."""

    # Initialize observability
    init_observability(service="dspy-pydantic-integration", environment="dev")

    with logfire.span("dspy_pydantic_evaluation"):
        print("🚀 Starting DSPy + Pydantic Ecosystem Integration Demo")
        print("=" * 70)

        # Load evaluation cases
        print("\n1. Loading evaluation cases...")
        gold_cases = load_eval_cases("gold")
        print(f"   ✅ Loaded {len(gold_cases)} gold cases")

        # Create Pydantic Evals dataset
        dataset = create_pydantic_evals_dataset(gold_cases)
        print(f"   ✅ Created Pydantic Evals dataset with {len(dataset.cases)} cases")

        # Initialize DSPy RAG agent
        print("\n2. Initializing DSPy RAG agent...")
        dspy_agent = DSPyRAGAgent()  # No real DSPy system for demo
        print("   ✅ DSPy RAG agent initialized")

        # Add evaluators
        print("\n3. Adding evaluators...")
        evaluators = [DSPyRAGEvaluator(), DSPyRetrievalEvaluator()]

        for evaluator in evaluators:
            dataset.add_evaluator(evaluator)
        print(f"   ✅ Added {len(evaluators)} evaluators")

        # Define evaluation task
        async def dspy_evaluation_task(inputs: Any) -> DSPyRAGAnswer:
            """Evaluation task that uses DSPy RAG system."""
            return await dspy_agent.query_rag_system(inputs.query)

        # Run evaluation
        print("\n4. Running evaluation...")
        report = await dataset.evaluate(dspy_evaluation_task)

        # Print results
        print("\n" + "=" * 70)
        print("DSPY + PYDANTIC ECOSYSTEM EVALUATION RESULTS")
        print("=" * 70)
        report.print()

        # Print averages
        print("\nEvaluation Averages:")
        averages = report.averages()
        if averages:
            # Try different ways to access the averages data
            if hasattr(averages, "__dict__"):
                # If it's a Pydantic model, access its attributes
                for key, value in averages.__dict__.items():
                    if not key.startswith("_"):  # Skip private attributes
                        print(f"  {key}: {value}")
            else:
                # Fallback: just print the averages object
                print(f"  {averages}")
        else:
            print("  Averages displayed in the report table above")

        print("\n✅ DSPy + Pydantic ecosystem integration successful!")
        print("📊 Results available in Logfire dashboard")
        print("🔄 Type-safe evaluation with structured outputs")
        print("🚀 Ready for production use with real DSPy RAG system")

        return report

if __name__ == "__main__":
    print("🚀 Starting DSPy + Pydantic Ecosystem Integration Demo")
    print("=" * 70)

    try:
        report = asyncio.run(evaluate_dspy_rag_system())
        print("\n✅ Integration demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Error running integration demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
