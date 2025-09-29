"""Shared state contract for PocketFlow-based orchestration."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

SCHEMA_VERSION = "2024-09-19"


class ConversationTurn(BaseModel):
    """Represents a single conversational turn."""

    turn_id: str
    thread_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationSummary(BaseModel):
    """Rolling summary for long-running sessions."""

    text: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    token_count: int = 0


class RetrievedHit(BaseModel):
    """A single retrieval hit from any source."""

    source: str
    score: float
    document_id: str | None = None
    file_path: str | None = None
    chunk_id: str | None = None
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalState(BaseModel):
    """Aggregated retrieval signals for the active query."""

    query: str = ""
    hits: dict[str, list[RetrievedHit]] = Field(default_factory=dict)
    merged: list[RetrievedHit] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)


class SharedState(BaseModel):
    """Shared store passed between PocketFlow nodes."""

    schema_version: Literal["2024-09-19"] = SCHEMA_VERSION
    session_id: str | None = None
    user_id: str | None = None
    idempotency_key: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    turns: list[ConversationTurn] = Field(default_factory=list)
    summary: ConversationSummary | None = None
    new_facts: list[dict[str, Any]] = Field(default_factory=list)
    entities: dict[str, dict[str, Any]] = Field(default_factory=dict)
    retrieval: RetrievalState = Field(default_factory=RetrievalState)
    answer: str | None = None
    caches: dict[str, dict[str, Any]] = Field(default_factory=dict)


__all__ = [
    "SCHEMA_VERSION",
    "ConversationTurn",
    "ConversationSummary",
    "RetrievedHit",
    "RetrievalState",
    "SharedState",
]
