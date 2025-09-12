from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import AnyUrl, BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, Union
"""Typed DTOs for agent boundaries and evaluation interoperability.

These models are intentionally strict (extra='forbid') to prevent silent schema
creep. They align with our provenance requirements and evaluation harness
contracts (retrieved_context, citations).
"""





class Provenance(BaseModel):
    """Provenance envelope required on all retrieved chunks."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: str = Field(description="Execution/run identifier for traceability")
    ingest_run_id: str = Field(description="Ingest run identifier (required)")
    chunk_variant: str = Field(description="Stable variant id for the chunk (required)")
    source_uri: AnyUrl | str | None = Field(
        default=None, description="Canonical URI for source; may be None if using file_path/doc_id"
    )
    source_path: str | None = Field(default=None, description="Local path when applicable")
    document_id: str | None = Field(default=None, description="Upstream document id if available")
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    tool: str = Field(description="Producing tool/component name")
    version: str = Field(description="Version of producer or schema")
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    meta: dict[str, Any] | None = Field(default=None, description="Optional extra, not for new schema fields")


class RetrievedChunk(BaseModel):
    """Chunk returned from retrieval/fusion/rerank stages."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    chunk_id: str
    text: str
    score: float = 0.0
    start_char: int | None = None
    end_char: int | None = None
    provenance: Provenance


class Answer(BaseModel):
    """Final structured answer returned by the orchestrator."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    text: str
    citations: list[str] = Field(default_factory=list)
    retrieved_context: list[RetrievedChunk] = Field(default_factory=list)
    timings_ms: dict[str, float] | None = None
    metadata: dict[str, Any] | None = None
