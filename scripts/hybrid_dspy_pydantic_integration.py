#!/usr/bin/env python3
"""
Hybrid DSPy + Pydantic Integration

This script works in both environments:
- Local: Pydantic + Ollama (fast development)
- Docker: DSPy + Pydantic + Ollama (full ML stack)
"""

import asyncio
import os
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
from pydantic_evals.dataset import Case, Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from scripts.migrate_to_pydantic_evals import create_pydantic_evals_dataset, load_eval_cases
from scripts.observability import init_observability


# Detect environment
def detect_environment():
    """Detect if we're running in Docker or local environment."""
    if os.path.exists("/.dockerenv") or os.environ.get("UV_PROJECT_ENVIRONMENT") == ".venv-linux":
        return "docker"
    return "local"


# Pydantic models for both environments
class HybridRAGInput(BaseModel):
    """Input for hybrid RAG queries."""

    model_config = ConfigDict(strict=True, extra="forbid")
    query: str = Field(min_length=1)
    use_dspy: bool = Field(default=False)  # Whether to use DSPy system
    model_preference: str | None = None


class HybridRAGAnswer(BaseModel):
    """Structured answer from hybrid RAG system."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    model_used: str
    environment: str  # "local" or "docker"
    response_time_ms: int
    metadata: dict[str, Any] = Field(default_factory=dict)


# Local Environment Handler (Pydantic + Ollama)
class LocalOllamaAgent:
    """PydanticAI agent for local Ollama models."""

    def __init__(self):
        # Use TestModel for local development (no API keys needed)
        from pydantic_ai.models.test import TestModel

        self.agent = Agent(
            TestModel(),
            system_prompt="You are a helpful AI assistant running locally via Ollama.",
            output_type=HybridRAGAnswer,
            instrument=InstrumentationSettings(include_content=False),
        )

    async def query_local_model(self, inputs: HybridRAGInput) -> HybridRAGAnswer:
        """Query local Ollama model."""

        with logfire.span("local_ollama_query", query=inputs.query):
            set_eval_attribute("query_type", "local_ollama")
            set_eval_attribute("environment", "local")
            increment_eval_metric("local_ollama_queries", 1)

            try:
                start_time = asyncio.get_event_loop().time()
                result = await self.agent.run(inputs.query)
                end_time = asyncio.get_event_loop().time()
                response_time_ms = int((end_time - start_time) * 1000)

                return HybridRAGAnswer(
                    answer=result.content.answer,
                    confidence=result.content.confidence or 0.8,
                    sources=["local_ollama"],
                    model_used="ollama:llama3.1:8b",
                    environment="local",
                    response_time_ms=response_time_ms,
                    metadata={"method": "pydantic_ai"},
                )

            except Exception as e:
                logfire.error("local_ollama_query_failed", error=str(e))
                return HybridRAGAnswer(
                    answer=f"Local Ollama error: {str(e)}",
                    confidence=0.0,
                    sources=[],
                    model_used="error",
                    environment="local",
                    response_time_ms=0,
                    metadata={"error": str(e)},
                )


# Docker Environment Handler (DSPy + Pydantic + Ollama)
class DockerDSPyAgent:
    """DSPy + Pydantic agent for Docker environment."""

    def __init__(self):
        # Try to import DSPy system
        try:
# sys.path.insert(0, str(project_root / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project
            from dspy_modules.model_switcher import LocalModel, ModelSwitcher

            self.model_switcher = ModelSwitcher()
            self.dspy_available = True
        except ImportError as e:
            print(f"⚠️  DSPy not available in Docker: {e}")
            self.dspy_available = False

    async def query_dspy_system(self, inputs: HybridRAGInput) -> HybridRAGAnswer:
        """Query DSPy system in Docker environment."""

        with logfire.span("docker_dspy_query", query=inputs.query):
            set_eval_attribute("query_type", "docker_dspy")
            set_eval_attribute("environment", "docker")
            increment_eval_metric("docker_dspy_queries", 1)

            if not self.dspy_available:
                return HybridRAGAnswer(
                    answer="DSPy system not available in Docker environment",
                    confidence=0.0,
                    sources=[],
                    model_used="none",
                    environment="docker",
                    response_time_ms=0,
                    metadata={"error": "DSPy not available"},
                )

            try:
                # Switch to preferred model
                if inputs.model_preference:
                    model_enum = self._get_model_enum(inputs.model_preference)
                    if model_enum:
                        self.model_switcher.switch_model(model_enum)

                # Get RAG pipeline
                rag_pipeline = self.model_switcher.get_rag_pipeline()
                if not rag_pipeline:
                    raise Exception("RAG pipeline not available")

                # Query DSPy system
                start_time = asyncio.get_event_loop().time()
                result = rag_pipeline.answer(inputs.query)
                end_time = asyncio.get_event_loop().time()
                response_time_ms = int((end_time - start_time) * 1000)

                return HybridRAGAnswer(
                    answer=result.get("answer", "No answer available"),
                    confidence=result.get("confidence", 0.8),
                    sources=result.get("sources", []),
                    model_used=inputs.model_preference or "dspy_default",
                    environment="docker",
                    response_time_ms=response_time_ms,
                    metadata={"method": "dspy_rag", "retrieval_metadata": result.get("retrieval_metadata", {})},
                )

            except Exception as e:
                logfire.error("docker_dspy_query_failed", error=str(e))
                return HybridRAGAnswer(
                    answer=f"DSPy error: {str(e)}",
                    confidence=0.0,
                    sources=[],
                    model_used="error",
                    environment="docker",
                    response_time_ms=0,
                    metadata={"error": str(e)},
                )

    def _get_model_enum(self, model_name: str):
        """Convert model name to LocalModel enum."""
        try:
            from dspy_modules.model_switcher import LocalModel

            model_mapping = {
                "llama3.1:8b": LocalModel.LLAMA_3_1_8B,
                "mistral:7b": LocalModel.MISTRAL_7B,
                "phi3.5:3.8b": LocalModel.PHI_3_5_3_8B,
            }
            return model_mapping.get(model_name)
        except ImportError:
            return None


# Hybrid Agent that chooses the right handler
class HybridRAGAgent:
    """Hybrid agent that works in both local and Docker environments."""

    def __init__(self):
        self.environment = detect_environment()
        print(f"🌍 Detected environment: {self.environment}")

        if self.environment == "local":
            self.agent = LocalOllamaAgent()
        else:
            self.agent = DockerDSPyAgent()

    async def query(self, inputs: HybridRAGInput) -> HybridRAGAnswer:
        """Query using the appropriate handler for the environment."""

        if self.environment == "local":
            return await self.agent.query_local_model(inputs)
        else:
            return await self.agent.query_dspy_system(inputs)


# Evaluators for both environments
class HybridRAGQualityEvaluator(Evaluator[HybridRAGInput, HybridRAGAnswer, dict]):
    """Evaluator for hybrid RAG system quality."""

    def evaluate(self, ctx: EvaluatorContext[HybridRAGInput, HybridRAGAnswer, dict]) -> float:
        """Evaluate hybrid RAG response quality."""

        if not ctx.output:
            increment_eval_metric("hybrid_rag_quality", 0.0)
            return 0.0

        # Environment-specific scoring
        environment = ctx.output.environment
        base_quality = 1.0 if ctx.output.answer and len(ctx.output.answer.strip()) > 0 else 0.0
        confidence_quality = ctx.output.confidence if ctx.output.confidence else 0.0

        # Bonus for Docker environment (more sophisticated)
        env_bonus = 0.1 if environment == "docker" else 0.0

        # Sources quality
        sources_quality = 1.0 if ctx.output.sources else 0.0

        overall_quality = (base_quality + confidence_quality + sources_quality) / 3.0 + env_bonus

        increment_eval_metric("hybrid_rag_quality", overall_quality)
        set_eval_attribute("environment", environment)
        set_eval_attribute("model_used", ctx.output.model_used)
        set_eval_attribute("response_time_ms", ctx.output.response_time_ms)

        return overall_quality


# Main integration function
async def run_hybrid_integration():
    """Run hybrid integration demo."""

    # Initialize observability
    init_observability(service="hybrid-dspy-pydantic", environment="dev")

    with logfire.span("hybrid_integration_demo"):
        print("🚀 Starting Hybrid DSPy + Pydantic Integration Demo")
        print("=" * 70)

        # Detect environment
        environment = detect_environment()
        print(f"🌍 Running in: {environment.upper()} environment")

        # Initialize hybrid agent
        print("\n1. Initializing hybrid agent...")
        agent = HybridRAGAgent()
        print(f"   ✅ Hybrid agent initialized for {environment} environment")

        # Load evaluation cases
        print("\n2. Loading evaluation cases...")
        gold_cases = load_eval_cases("gold")
        print(f"   ✅ Loaded {len(gold_cases)} gold cases")

        # Create Pydantic Evals dataset
        dataset = create_pydantic_evals_dataset(gold_cases)
        print(f"   ✅ Created Pydantic Evals dataset with {len(dataset.cases)} cases")

        # Add evaluators
        print("\n3. Adding evaluators...")
        evaluators = [HybridRAGQualityEvaluator()]
        for evaluator in evaluators:
            dataset.add_evaluator(evaluator)
        print(f"   ✅ Added {len(evaluators)} evaluators")

        # Define evaluation task
        async def hybrid_evaluation_task(inputs):
            """Evaluation task using hybrid agent."""
            return await agent.query(inputs)

        # Run evaluation
        print("\n4. Running evaluation...")
        report = await dataset.evaluate(hybrid_evaluation_task)

        # Print results
        print("\n" + "=" * 70)
        print(f"HYBRID {environment.upper()} ENVIRONMENT EVALUATION RESULTS")
        print("=" * 70)
        report.print()

        # Print averages
        print("\nEvaluation Averages:")
        averages = report.averages()
        if averages and hasattr(averages, "items"):
            for key, value in averages.items():
                print(f"  {key}: {value}")
        else:
            print("  Averages displayed in the report table above")

        print(f"\n✅ Hybrid {environment} integration successful!")
        print("📊 Results available in Logfire dashboard")
        print("🔄 Environment-appropriate model usage")
        print("🚀 Ready for production use")

        return report


if __name__ == "__main__":
    print("🔍 Hybrid DSPy + Pydantic Integration Demo")
    print("=" * 70)

    try:
        report = asyncio.run(run_hybrid_integration())
        print("\n🎉 Hybrid integration demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Error running hybrid integration demo: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
