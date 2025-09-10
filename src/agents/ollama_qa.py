"""PydanticAI QA agent with Ollama local models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import httpx
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.instrumented import InstrumentationSettings


class OllamaQAAnswer(BaseModel):
    """Structured answer output for Ollama QA tasks."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float | None = None
    model_used: str
    response_time_ms: int


@dataclass
class OllamaDeps:
    """Dependencies for the Ollama QA agent."""

    http_client: httpx.AsyncClient
    ollama_base_url: str = "http://localhost:11434"


# Create Ollama agent with llama3.1:8b model
ollama_agent = Agent(
    "ollama:llama3.1:8b",  # Use local Ollama model
    deps_type=OllamaDeps,
    system_prompt="You are a concise QA assistant running locally via Ollama.",
    output_type=OllamaQAAnswer,
    instrument=InstrumentationSettings(include_content=False),  # redact content by default
)


@ollama_agent.tool
async def web_fetch(ctx: RunContext[OllamaDeps], url: str) -> str:
    """Fetch a URL (safe domains only)."""
    r = await ctx.deps.http_client.get(url, timeout=30)
    r.raise_for_status()
    return r.text


@ollama_agent.tool
async def check_ollama_status(ctx: RunContext[OllamaDeps]) -> str:
    """Check if Ollama is running and list available models."""
    try:
        r = await ctx.deps.http_client.get(f"{ctx.deps.ollama_base_url}/api/tags", timeout=5)
        r.raise_for_status()
        models = r.json().get("models", [])
        model_names = [model.get("name", "Unknown") for model in models]
        return f"Ollama is running with {len(models)} models: {', '.join(model_names[:5])}"
    except Exception as e:
        return f"Ollama status check failed: {str(e)}"


# Alternative agent configurations for different models
def create_ollama_agent(model_name: str, system_prompt: str = None) -> Agent:
    """Create an Ollama agent with a specific model."""

    if system_prompt is None:
        system_prompt = f"You are a helpful AI assistant running locally via Ollama ({model_name})."

    return Agent(
        f"ollama:{model_name}",
        deps_type=OllamaDeps,
        system_prompt=system_prompt,
        output_type=OllamaQAAnswer,
        instrument=InstrumentationSettings(include_content=False),
    )


# Pre-configured agents for different use cases
mistral_agent = create_ollama_agent("mistral:7b", "You are a coding-focused assistant running locally via Mistral 7B.")

phi_agent = create_ollama_agent(
    "phi3.5:3.8b", "You are a lightweight, efficient assistant running locally via Phi-3.5."
)

codellama_agent = create_ollama_agent(
    "codellama:7b", "You are a specialized coding assistant running locally via CodeLlama."
)
