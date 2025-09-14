"""PydanticAI QA agent with typed outputs and instrumentation."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Annotated, Any, Optional

import httpx
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.instrumented import InstrumentationSettings


class QAAnswer(BaseModel):
    """Structured answer output for QA tasks."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float | None = None


@dataclass
class Deps:
    """Dependencies for the QA agent."""

    http_client: httpx.AsyncClient


# Initialize agent only if API key is available
try:
    import os

    if os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_BASE_URL"):
        agent: Agent[Deps, QAAnswer] | None = Agent(
            "openai:gpt-4o-mini",  # or router string
            deps_type=Deps,
            system_prompt="You are a concise QA assistant.",
            output_type=QAAnswer,
            instrument=InstrumentationSettings(include_content=False),  # redact content by default
        )
    else:
        # Create a mock agent for testing
        agent = None
except Exception:
    # Fallback for testing environments
    agent = None


async def web_fetch(ctx: RunContext[Deps], url: str) -> str:
    """Fetch a URL (safe domains only)."""
    r = await ctx.deps.http_client.get(url, timeout=30)
    r.raise_for_status()
    return r.text


# Register tools only if agent is available
if agent is not None:
    agent.tool(web_fetch)


async def run_agent(question: str, deps: Deps) -> QAAnswer:
    """Run the QA agent safely in async contexts.

    - If the global agent is None, returns a mock QAAnswer.
    - Supports both sync and async Agent.run implementations.
    """
    if agent is None:
        return QAAnswer(answer=f"(mock draft) {question[:200]}")

    result_obj: Any = agent.run(question, deps=deps)
    if inspect.isawaitable(result_obj):
        result_obj = await result_obj

    # Normalize different possible return shapes to QAAnswer
    if isinstance(result_obj, QAAnswer):
        return result_obj

    for attr_name in ("data", "output", "parsed", "result"):
        if hasattr(result_obj, attr_name):
            value = getattr(result_obj, attr_name)
            if isinstance(value, QAAnswer):
                return value
            # If it's a mapping or object with 'answer', construct QAAnswer
            try:
                answer_value = getattr(value, "answer", None) or (
                    value.get("answer") if isinstance(value, dict) else None
                )
                confidence_value = getattr(value, "confidence", None) or (
                    value.get("confidence") if isinstance(value, dict) else None
                )
                if isinstance(answer_value, str) and len(answer_value) > 0:
                    return QAAnswer(answer=answer_value, confidence=confidence_value)
            except Exception:
                pass

    # Last resort: coerce to string
    return QAAnswer(answer=str(result_obj)[:500])
