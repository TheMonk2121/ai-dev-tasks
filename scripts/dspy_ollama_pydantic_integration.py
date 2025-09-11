#!/usr/bin/env python3
"""
DSPy + Ollama + Pydantic Ecosystem Integration

This script demonstrates how your existing DSPy system with Ollama models
integrates with the new Pydantic ecosystem:
- Uses your existing ModelSwitcher and RAGPipeline
- PydanticAI agents for structured outputs
- Pydantic Evals for evaluation
- Pydantic Logfire for observability
- Type-safe data flow with your local models
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add DSPy system to path
dspy_rag_path = Path("src")
sys.path.insert(0, str(dspy_rag_path))

import logfire
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.instrumented import InstrumentationSettings
from pydantic_evals.dataset import Case, Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from scripts.migrate_to_pydantic_evals import create_pydantic_evals_dataset, load_eval_cases
from scripts.observability import init_observability

# Import your existing DSPy system
try:
    from dspy_modules.model_switcher import LocalModel, ModelSwitcher
    from dspy_modules.rag_pipeline import RAGPipeline

    DSPY_AVAILABLE = True
    print("✅ DSPy system imported successfully")
except ImportError as e:
    print(f"⚠️  DSPy system not available: {e}")
    DSPY_AVAILABLE = False


# 1. Pydantic models for DSPy RAG integration
class DSPyRAGInput(BaseModel):
    """Input for DSPy RAG queries."""

    model_config = ConfigDict(strict=True, extra="forbid")
    query: str = Field(min_length=1)
    model_preference: str | None = None  # e.g., "llama3.1:8b", "mistral:7b", "phi3.5:3.8b"
    max_tokens: int = Field(default=512, ge=1, le=4096)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)


class DSPyRAGAnswer(BaseModel):
    """Structured answer from DSPy RAG system."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    model_used: str
    retrieval_metadata: dict[str, Any] = Field(default_factory=dict)
    response_time_ms: int


# 2. PydanticAI Agent that integrates with your DSPy system
class DSPyOllamaAgent:
    """PydanticAI agent that integrates with your existing DSPy + Ollama system."""

    def __init__(self, model_switcher: ModelSwitcher = None):
        self.model_switcher = model_switcher or ModelSwitcher()
        self.current_model = None

        # Create PydanticAI agent for structured outputs
        self.agent = Agent(
            "ollama:llama3.1:8b",  # Default to your Llama model
            system_prompt="You are a helpful AI assistant running locally via Ollama and DSPy.",
            output_type=DSPyRAGAnswer,
            instrument=InstrumentationSettings(include_content=False),
        )

    async def query_dspy_rag_system(self, inputs: DSPyRAGInput) -> DSPyRAGAnswer:
        """Query your DSPy RAG system and return structured output."""

        with logfire.span("dspy_ollama_query", query=inputs.query, model_preference=inputs.model_preference):
            set_eval_attribute("query_type", "dspy_rag")
            set_eval_attribute("model_preference", inputs.model_preference or "auto")
            increment_eval_metric("dspy_rag_queries", 1)

            try:
                # Switch to preferred model if specified
                if inputs.model_preference:
                    model_enum = self._get_model_enum(inputs.model_preference)
                    if model_enum:
                        success = self.model_switcher.switch_model(model_enum)
                        if success:
                            self.current_model = inputs.model_preference
                            set_eval_attribute("model_switched", True)
                        else:
                            set_eval_attribute("model_switch_failed", True)

                # Get RAG pipeline
                rag_pipeline = self.model_switcher.get_rag_pipeline()
                if not rag_pipeline:
                    raise Exception("RAG pipeline not available")

                # Query the DSPy RAG system
                start_time = asyncio.get_event_loop().time()
                result = rag_pipeline.answer(inputs.query, max_tokens=inputs.max_tokens, temperature=inputs.temperature)
                end_time = asyncio.get_event_loop().time()
                response_time_ms = int((end_time - start_time) * 1000)

                # Extract sources and metadata
                sources = result.get("sources", [])
                retrieval_metadata = result.get("retrieval_metadata", {})

                return DSPyRAGAnswer(
                    answer=result.get("answer", "No answer available"),
                    confidence=result.get("confidence", 0.8),
                    sources=sources,
                    model_used=self.current_model or "unknown",
                    retrieval_metadata=retrieval_metadata,
                    response_time_ms=response_time_ms,
                )

            except Exception as e:
                logfire.error("dspy_rag_query_failed", error=str(e), model=self.current_model)
                # Fallback response
                return DSPyRAGAnswer(
                    answer=f"Error querying DSPy RAG system: {str(e)}",
                    confidence=0.0,
                    sources=[],
                    model_used=self.current_model or "error",
                    retrieval_metadata={"error": str(e)},
                    response_time_ms=0,
                )

    def _get_model_enum(self, model_name: str) -> LocalModel | None:
        """Convert model name string to LocalModel enum."""
        model_mapping = {
            "llama3.1:8b": LocalModel.LLAMA_3_1_8B,
            "mistral:7b": LocalModel.MISTRAL_7B,
            "phi3.5:3.8b": LocalModel.PHI_3_5_3_8B,
        }
        return model_mapping.get(model_name)


# 3. Custom evaluators for DSPy RAG system
class DSPyRAGQualityEvaluator(Evaluator[DSPyRAGInput, DSPyRAGAnswer, dict]):
    """Evaluator for DSPy RAG system response quality."""

    def evaluate(self, ctx: EvaluatorContext[DSPyRAGInput, DSPyRAGAnswer, dict]) -> float:
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

        # Check model usage
        model_quality = 1.0 if ctx.output.model_used and ctx.output.model_used != "unknown" else 0.0

        # Overall quality score
        overall_quality = (answer_quality + confidence_quality + sources_quality + model_quality) / 4.0

        increment_eval_metric("dspy_rag_quality", overall_quality)
        set_eval_attribute("answer_length", len(ctx.output.answer) if ctx.output.answer else 0)
        set_eval_attribute("num_sources", len(ctx.output.sources))
        set_eval_attribute("model_used", ctx.output.model_used)
        set_eval_attribute("confidence", ctx.output.confidence)
        set_eval_attribute("response_time_ms", ctx.output.response_time_ms)

        return overall_quality


class DSPyModelPerformanceEvaluator(Evaluator[DSPyRAGInput, DSPyRAGAnswer, dict]):
    """Evaluator for DSPy model performance."""

    def evaluate(self, ctx: EvaluatorContext[DSPyRAGInput, DSPyRAGAnswer, dict]) -> float:
        """Evaluate DSPy model performance metrics."""

        if not ctx.output:
            increment_eval_metric("dspy_model_performance", 0.0)
            return 0.0

        # Response time score (faster is better, up to 10000ms)
        response_time = ctx.output.response_time_ms
        time_score = max(0.0, 1.0 - (response_time / 10000.0))

        # Model utilization score
        model_score = 1.0 if ctx.output.model_used and ctx.output.model_used != "unknown" else 0.0

        # Retrieval metadata quality
        metadata = ctx.output.retrieval_metadata
        metadata_score = 1.0 if metadata and not metadata.get("error") else 0.0

        # Overall performance score
        performance_score = (time_score + model_score + metadata_score) / 3.0

        increment_eval_metric("dspy_model_performance", performance_score)
        set_eval_attribute("response_time_ms", response_time)
        set_eval_attribute("model_used", ctx.output.model_used)
        set_eval_attribute("has_metadata", bool(metadata))

        return performance_score


# 4. Integration function that uses your DSPy system
async def evaluate_dspy_ollama_system():
    """Evaluate your DSPy + Ollama system using Pydantic Evals framework."""

    # Initialize observability
    init_observability(service="dspy-ollama-pydantic-integration", environment="dev")

    with logfire.span("dspy_ollama_pydantic_evaluation"):
        print("🚀 Starting DSPy + Ollama + Pydantic Ecosystem Integration Demo")
        print("=" * 70)

        if not DSPY_AVAILABLE:
            print("❌ DSPy system not available. Please ensure dspy-rag-system is properly set up.")
            return None

        # Check Ollama availability
        print("\n1. Checking Ollama availability...")
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    print(f"   ✅ Ollama is running with {len(models)} models available")
                    for model in models[:3]:  # Show first 3 models
                        print(f"      - {model.get('name', 'Unknown')}")
                else:
                    print("   ⚠️  Ollama is running but API returned unexpected status")
        except Exception as e:
            print(f"   ❌ Ollama not available: {e}")
            print("   💡 Make sure Ollama is running: ollama serve")
            return None

        # Initialize DSPy system
        print("\n2. Initializing DSPy system...")
        try:
            model_switcher = ModelSwitcher()
            print("   ✅ ModelSwitcher initialized")

            # Test model switching
            success = model_switcher.switch_model(LocalModel.LLAMA_3_1_8B)
            if success:
                print("   ✅ Successfully switched to Llama 3.1 8B")
            else:
                print("   ⚠️  Could not switch to Llama 3.1 8B")

            dspy_agent = DSPyOllamaAgent(model_switcher)
            print("   ✅ DSPy + Ollama agent initialized")

        except Exception as e:
            print(f"   ❌ Failed to initialize DSPy system: {e}")
            return None

        # Load evaluation cases
        print("\n3. Loading evaluation cases...")
        gold_cases = load_eval_cases("gold")
        print(f"   ✅ Loaded {len(gold_cases)} gold cases")

        # Create Pydantic Evals dataset
        dataset = create_pydantic_evals_dataset(gold_cases)
        print(f"   ✅ Created Pydantic Evals dataset with {len(dataset.cases)} cases")

        # Add evaluators
        print("\n4. Adding evaluators...")
        evaluators = [DSPyRAGQualityEvaluator(), DSPyModelPerformanceEvaluator()]

        for evaluator in evaluators:
            dataset.add_evaluator(evaluator)
        print(f"   ✅ Added {len(evaluators)} evaluators")

        # Define evaluation task
        async def dspy_evaluation_task(inputs):
            """Evaluation task that uses your DSPy RAG system."""
            return await dspy_agent.query_dspy_rag_system(inputs)

        # Run evaluation
        print("\n5. Running evaluation...")
        report = await dataset.evaluate(dspy_evaluation_task)

        # Print results
        print("\n" + "=" * 70)
        print("DSPY + OLLAMA + PYDANTIC ECOSYSTEM EVALUATION RESULTS")
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

        print("\n✅ DSPy + Ollama + Pydantic ecosystem integration successful!")
        print("📊 Results available in Logfire dashboard")
        print("🔄 Local models with type-safe evaluation")
        print("🚀 Ready for production use with your DSPy system")

        return report


def demonstrate_dspy_integration():
    """Show how to integrate with your existing DSPy system."""

    print("\n" + "=" * 70)
    print("DSPY + OLLAMA INTEGRATION GUIDE")
    print("=" * 70)

    integration_code = """
# Example: Using your existing DSPy system with Pydantic

from dspy_modules.model_switcher import ModelSwitcher, LocalModel
from dspy_modules.rag_pipeline import RAGPipeline

# Initialize your DSPy system
model_switcher = ModelSwitcher()

# Switch to your preferred model
model_switcher.switch_model(LocalModel.LLAMA_3_1_8B)  # or MISTRAL_7B, PHI_3_5_3_8B

# Get RAG pipeline
rag_pipeline = model_switcher.get_rag_pipeline()

# Query with your existing system
result = rag_pipeline.answer("What is the current project status?")

# Now integrate with Pydantic for type safety
from scripts.dspy_ollama_pydantic_integration import DSPyOllamaAgent, DSPyRAGInput

# Create PydanticAI agent with your DSPy system
dspy_agent = DSPyOllamaAgent(model_switcher)

# Use with structured inputs/outputs
inputs = DSPyRAGInput(
    query="Analyze the memory system architecture",
    model_preference="llama3.1:8b",
    max_tokens=512,
    temperature=0.2
)

# Get structured output
answer = await dspy_agent.query_dspy_rag_system(inputs)
print(f"Answer: {answer.answer}")
print(f"Model used: {answer.model_used}")
print(f"Sources: {answer.sources}")
"""

    print("Integration Code Example:")
    print(integration_code)

    print("\nYour Available Models:")
    print("  - llama3.1:8b (Planning, research, reasoning)")
    print("  - mistral:7b (Fast completions, rapid prototyping)")
    print("  - phi3.5:3.8b (Large context, documentation analysis)")

    print("\nKey Benefits of DSPy + Pydantic Integration:")
    print("✅ Your existing DSPy system works unchanged")
    print("✅ Type-safe data flow with Pydantic models")
    print("✅ Structured evaluation with Pydantic Evals")
    print("✅ Full observability with Logfire tracing")
    print("✅ Local models with no API keys needed")
    print("✅ Production-ready with your existing infrastructure")


if __name__ == "__main__":
    print("🔍 DSPy + Ollama + Pydantic Ecosystem Integration Demo")
    print("=" * 70)

    try:
        # Run the integration demo
        report = asyncio.run(evaluate_dspy_ollama_system())

        if report:
            # Show integration examples
            demonstrate_dspy_integration()

            print("\n🎉 Integration demo completed successfully!")
        else:
            print("\n⚠️  Demo skipped - DSPy or Ollama not available")
            print("💡 To run this demo:")
            print("   1. Ensure Ollama is running: ollama serve")
            print("   2. Pull models: ollama pull llama3.1:8b")
            print("   3. Ensure DSPy system is set up in dspy-rag-system/")
            print("   4. Run demo again")

    except Exception as e:
        print(f"\n❌ Error running integration demo: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
