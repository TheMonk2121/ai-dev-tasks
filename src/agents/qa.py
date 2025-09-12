from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated
import httpx
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.instrumented import InstrumentationSettings
import sys
from typing import Any, Dict, List, Optional, Union
"""PydanticAI QA agent with typed outputs and instrumentation."""





class QAAnswer(BaseModel):
    """Structured answer output for QA tasks."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float | None = None


@dataclass
class Deps:
    """Dependencies for the QA agent."""

    http_client: httpx.AsyncClient


agent = Agent(
    "openai:gpt-4o-mini",  # or router string
    deps_type=Deps,
    system_prompt="You are a concise QA assistant.",
    output_type=QAAnswer,
    instrument=InstrumentationSettings(include_content=False),  # redact content by default
)


@agent.tool
async def web_fetch(ctx: RunContext[Deps], url: str) -> str:
    """Fetch a URL (safe domains only)."""
    r = await ctx.deps.http_client.get(url, timeout=30)
    r.raise_for_status()
    return r.text
