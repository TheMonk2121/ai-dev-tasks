from __future__ import annotations

import os
from typing import Any

from pydantic_ai import Agent, Tool

from src.config.settings import get_settings
from src.dspy_modules.dspy_reader_program import RAGAnswer
from src.memory.guards import build_answer, rows_to_dtos
from src.memory.models import Answer
from src.observability.logging import init_observability
import sys
from typing import Any, Dict, List, Optional, Union


def _retrieve_rows(question: str, tag: str) -> list[dict[str, Any]]:
    # Use existing DSPy program to execute retrieval-only path up to context build
    # We leverage the program to produce used_contexts after forward path
    prog = RAGAnswer()
    _ = prog(question=question, tag=tag)  # run to populate used_contexts
    rows = getattr(prog, "used_contexts", []) or []
    # Ensure dicts
    out: list[dict[str, Any]] = []
    for r in rows:
        if isinstance(r, dict):
            out.append(r)
        else:
            out.append({k: getattr(r, k, None) for k in ("chunk_id", "text", "score", "metadata")})
    return out


def make_agent() -> Agent[Any, Answer]:
    settings = get_settings()
    init_observability()

    @Tool
    def retrieve_context(question: str, tag: str = "rag_qa_single") -> list[dict[str, Any]]:
        """Retrieve context rows using the existing DSPy pipeline (prefetch→fusion→rerank)."""
        return _retrieve_rows(question, tag)

    @Tool
    def generate_answer(question: str, tag: str = "rag_qa_single") -> Answer:
        rows = _retrieve_rows(question, tag)
        chunks = rows_to_dtos(
            rows,
            run_id=os.getenv("RUN_ID", "dev"),
            producer="dspy_retriever",
            version="v1",
            strict=settings.strict_provenance,
        )
        # For now, defer to DSPy answer; integrate streaming later as needed
        prog = RAGAnswer()
        pred = prog(question=question, tag=tag)
        text = getattr(pred, "answer", "")
        citations = [c.provenance.source_path or c.provenance.document_id or c.chunk_id for c in chunks]
        return build_answer(text=text, citations=citations, chunks=chunks)

    agent = Agent(
        output_type=Answer,
        system_prompt="You orchestrate retrieval and answer generation.",
        tools=[retrieve_context, generate_answer],
    )
    return agent
