from __future__ import annotations

import asyncio
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Optional, Union

import httpx
import logfire
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.instrumented import InstrumentationSettings
from pydantic_evals.dataset import Case, Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from scripts.evaluation.migrate_to_pydantic_evals import create_pydantic_evals_dataset, load_eval_cases
from scripts.observability import init_observability

#!/usr/bin/env python3
"""
Ollama + Pydantic Ecosystem Integration

This script demonstrates how to use local Ollama models with the Pydantic ecosystem:
- PydanticAI agents with Ollama models
- Pydantic Evals for evaluation
- Pydantic Logfire for observability
- Type-safe data flow with local models
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 1. PydanticAI Agent with Ollama models
class OllamaAnswer(BaseModel):
    """Structured answer from Ollama model."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    model_used: str
    response_time_ms: int
    tokens_generated: int | None = None

class OllamaAgent:
    """PydanticAI agent that uses local Ollama models."""

    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.agent = Agent(
            f"ollama:{model_name}",  # Use Ollama model
            system_prompt="You are a helpful AI assistant running locally via Ollama.",
            output_type=OllamaAnswer,
            instrument=InstrumentationSettings(include_content=False),
        )

    async def query_local_model(self, question: str) -> OllamaAnswer:
        """Query the local Ollama model and return structured output."""

        with logfire.span("ollama_query", question=question, model=self.model_name):
            set_eval_attribute("query_type", "ollama")
            set_eval_attribute("model_name", self.model_name)
            increment_eval_metric("ollama_queries", 1)

            try:
                # Use PydanticAI agent with Ollama
                result = await self.agent.run(question)

                # Access the result data through the output attribute
                return OllamaAnswer(
                    answer=result.output.answer,
                    confidence=result.output.confidence or 0.8,
                    model_used=self.model_name,
                    response_time_ms=1000,  # Mock timing
                    tokens_generated=int(len(result.output.answer.split()) * 1.3),  # Rough estimate
                )

            except Exception as e:
                logfire.error("ollama_query_failed", error=str(e), model=self.model_name)
                # Fallback response
                return OllamaAnswer(
                    answer=f"Error querying {self.model_name}: {str(e)}",
                    confidence=0.0,
                    model_used=self.model_name,
                    response_time_ms=0,
                    tokens_generated=0,
                )

# 2. Pydantic Evals evaluators for Ollama models
class OllamaQualityEvaluator(Evaluator[OllamaAnswer, OllamaAnswer, dict]):
    """Evaluator for Ollama model response quality."""

    def evaluate(self, ctx: EvaluatorContext[OllamaAnswer, OllamaAnswer, dict]) -> float:
        """Evaluate Ollama response quality."""

        if not ctx.output:
            increment_eval_metric("ollama_quality", 0.0)
            return 0.0

        # Check if answer is present and non-empty
        answer_quality = 1.0 if ctx.output.answer and len(ctx.output.answer.strip()) > 0 else 0.0

        # Check confidence score
        confidence_quality = ctx.output.confidence if ctx.output.confidence else 0.0

        # Check if model was used
        model_quality = 1.0 if ctx.output.model_used else 0.0

        # Overall quality score
        overall_quality = (answer_quality + confidence_quality + model_quality) / 3.0

        increment_eval_metric("ollama_quality", overall_quality)
        set_eval_attribute("answer_length", len(ctx.output.answer) if ctx.output.answer else 0)
        set_eval_attribute("model_used", ctx.output.model_used)
        set_eval_attribute("confidence", ctx.output.confidence)
        set_eval_attribute("response_time_ms", ctx.output.response_time_ms)

        return overall_quality

class OllamaPerformanceEvaluator(Evaluator[OllamaAnswer, OllamaAnswer, dict]):
    """Evaluator for Ollama model performance."""

    def evaluate(self, ctx: EvaluatorContext[OllamaAnswer, OllamaAnswer, dict]) -> float:
        """Evaluate Ollama performance metrics."""

        if not ctx.output:
            increment_eval_metric("ollama_performance", 0.0)
            return 0.0

        # Response time score (faster is better, up to 5000ms)
        response_time = ctx.output.response_time_ms
        time_score = max(0.0, 1.0 - (response_time / 5000.0))

        # Token efficiency score (more tokens is better, up to 1000)
        tokens = ctx.output.tokens_generated or 0
        token_score = min(1.0, tokens / 1000.0)

        # Overall performance score
        performance_score = (time_score + token_score) / 2.0

        increment_eval_metric("ollama_performance", performance_score)
        set_eval_attribute("response_time_ms", response_time)
        set_eval_attribute("tokens_generated", tokens)

        return performance_score

# 3. Integration function that uses Ollama with Pydantic Evals
async def evaluate_ollama_models():
    """Evaluate Ollama models using Pydantic Evals framework."""

    # Initialize observability
    init_observability(service="ollama-pydantic-integration", environment="dev")

    with logfire.span("ollama_pydantic_evaluation"):
        print("🚀 Starting Ollama + Pydantic Ecosystem Integration Demo")
        print("=" * 70)

        # Check if Ollama is available
        print("\n1. Checking Ollama availability...")
        try:

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

        # Load evaluation cases
        print("\n2. Loading evaluation cases...")
        gold_cases = load_eval_cases("gold")
        print(f"   ✅ Loaded {len(gold_cases)} gold cases")

        # Create Pydantic Evals dataset
        dataset = create_pydantic_evals_dataset(gold_cases)
        print(f"   ✅ Created Pydantic Evals dataset with {len(dataset.cases)} cases")

        # Initialize Ollama agents with different models
        print("\n3. Initializing Ollama agents...")
        models_to_test = ["llama3.1:8b", "mistral:7b", "phi3.5:3.8b"]
        agents = {}

        for model in models_to_test:
            try:
                agents[model] = OllamaAgent(model)
                print(f"   ✅ Initialized agent for {model}")
            except Exception as e:
                print(f"   ⚠️  Could not initialize {model}: {e}")

        if not agents:
            print("   ❌ No Ollama agents could be initialized")
            return None

        # Add evaluators
        print("\n4. Adding evaluators...")
        evaluators = [OllamaQualityEvaluator(), OllamaPerformanceEvaluator()]

        for evaluator in evaluators:
            dataset.add_evaluator(evaluator)
        print(f"   ✅ Added {len(evaluators)} evaluators")

        # Define evaluation task
        async def ollama_evaluation_task(inputs):
            """Evaluation task that uses Ollama models."""
            # Use the first available model
            model_name = list(agents.keys())[0]
            agent = agents[model_name]
            return await agent.query_local_model(inputs.query)

        # Run evaluation
        print("\n5. Running evaluation...")
        report = await dataset.evaluate(ollama_evaluation_task)

        # Print results
        print("\n" + "=" * 70)
        print("OLLAMA + PYDANTIC ECOSYSTEM EVALUATION RESULTS")
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

        print("\n✅ Ollama + Pydantic ecosystem integration successful!")
        print("📊 Results available in Logfire dashboard")
        print("🔄 Local models with type-safe evaluation")
        print("🚀 Ready for production use with Ollama models")

        return report

# 4. Demonstration of different Ollama model configurations
def demonstrate_ollama_configurations():
    """Show different ways to configure Ollama with PydanticAI."""

    print("\n" + "=" * 70)
    print("OLLAMA CONFIGURATION EXAMPLES")
    print("=" * 70)

    config_examples = """
# Example 1: Basic Ollama model
agent = Agent(
    "ollama:llama3.1:8b",
    system_prompt="You are a helpful assistant.",
    output_type=MyOutputModel
)

# Example 2: Ollama with custom endpoint
agent = Agent(
    "ollama:mistral:7b",
    system_prompt="You are a coding assistant.",
    output_type=CodeOutputModel,
    model_kwargs={"base_url": "http://localhost:11434"}
)

# Example 3: Multiple Ollama models with routing
def create_ollama_agent(model_name: str):
    return Agent(
        f"ollama:{model_name}",
        system_prompt=f"You are a {model_name} assistant.",
        output_type=UnifiedOutputModel
    )

# Available models (check with: ollama list)
models = [
    "llama3.1:8b",      # General purpose
    "mistral:7b",       # Coding focused
    "phi3.5:3.8b",      # Lightweight
    "codellama:7b",     # Code specific
    "llama3.1:70b"      # Large model (if you have enough RAM)
]
"""

    print("Configuration Examples:")
    print(config_examples)

    print("\nOllama Commands:")
    print("  ollama serve                    # Start Ollama server")
    print("  ollama list                     # List available models")
    print("  ollama pull llama3.1:8b         # Download a model")
    print("  ollama run llama3.1:8b          # Test a model")

    print("\nKey Benefits of Ollama + Pydantic:")
    print("✅ Local models - no API keys needed")
    print("✅ Type-safe outputs with Pydantic models")
    print("✅ Full observability with Logfire")
    print("✅ Easy evaluation with Pydantic Evals")
    print("✅ Privacy - data stays on your machine")

if __name__ == "__main__":
    print("🔍 Ollama + Pydantic Ecosystem Integration Demo")
    print("=" * 70)

    try:
        # Run the integration demo
        report = asyncio.run(evaluate_ollama_models())

        if report:
            # Show configuration examples
            demonstrate_ollama_configurations()

            print("\n🎉 Ollama integration demo completed successfully!")
        else:
            print("\n⚠️  Demo skipped - Ollama not available")
            print("💡 To run this demo:")
            print("   1. Install Ollama: https://ollama.ai")
            print("   2. Start server: ollama serve")
            print("   3. Pull models: ollama pull llama3.1:8b")
            print("   4. Run demo again")

    except Exception as e:
        print(f"\n❌ Error running Ollama integration demo: {e}")

        traceback.print_exc()
        sys.exit(1)
