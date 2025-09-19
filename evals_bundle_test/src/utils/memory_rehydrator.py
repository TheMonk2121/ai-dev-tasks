#!/usr/bin/env python3
"""
Thin adapter exposing a stable memory rehydration interface for the orchestrator.

Provides:
- RehydrationRequest: input payload used by the orchestrator
- MemoryRehydrator.rehydrate_memory(): returns a RehydrationResult with the
  fields expected by the unified orchestrator for formatting into a bundle.

Implementation detail:
- Wraps LTSTMemoryIntegration to obtain a context and similar contexts.
"""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RehydrationRequest:
    session_id: str
    user_id: str
    current_message: str
    context_types: list[str] = field(default_factory=list)
    max_context_length: int = 8192
    include_conversation_history: bool = True
    history_limit: int = 20
    relevance_threshold: float = 0.7
    similarity_threshold: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: float


@dataclass
class RelevantContext:
    context_id: str
    content: str
    metadata: dict[str, Any]
    similarity_score: float | None = None


@dataclass
class RehydrationResult:
    rehydrated_context: str
    conversation_history: list[ConversationMessage]
    user_preferences: dict[str, Any]
    project_context: dict[str, Any]
    relevant_contexts: list[RelevantContext]
    session_continuity_score: float
    context_relevance_scores: dict[str, float]
    rehydration_time_ms: float
    cache_hit: bool
    metadata: dict[str, Any]


@dataclass
class MemoryBundle:
    """Simple container for Cursor-friendly bundles."""

    text: str
    meta: dict[str, Any]


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Run in a new loop to avoid interfering with existing one
        return asyncio.run(coro)
    return asyncio.run(coro)


class MemoryRehydrator:
    """
    Adapter around LTSTMemoryIntegration providing a stable rehydrate_memory API.
    """

    def rehydrate_memory(self, request: RehydrationRequest) -> RehydrationResult:
        start = time.time()

        # If forced degraded mode, skip external deps
        if os.getenv("REHYDRATE_FORCE_DEGRADED", "0") == "1":
            return self._degraded_fallback(request, start)

        # Lazy import to keep adapter lightweight and avoid import cycles at module import time
        try:
            from scripts.ltst_memory_integration import LTSTContext, LTSTMemoryIntegration  # type: ignore
        except Exception:
            # Import not available; use degraded fallback
            return self._degraded_fallback(request, start)

        async def _do_rehydrate() -> RehydrationResult:
            try:
                async with LTSTMemoryIntegration() as integration:
                    # Retrieve primary context
                    ctx: LTSTContext | None = await integration.retrieve_context(
                        request.current_message, user_id=request.user_id
                    )

                    # Retrieve similar contexts for supporting evidence
                    similar = await integration.search_similar_contexts(
                        request.current_message, limit=5, threshold=request.similarity_threshold
                    )

                    rehydrated_context = ctx.content if ctx else ""
                    cache_hit = bool(getattr(ctx, "cache_hit", False)) if ctx else False

                    # Build relevant contexts model
                    relevant_contexts: list[RelevantContext] = []
                    relevance_scores: dict[str, float] = {}
                    for sc in similar:
                        rc = RelevantContext(
                            context_id=getattr(sc, "context_id", ""),
                            content=getattr(sc, "content", ""),
                            metadata=getattr(sc, "metadata", {}),
                            similarity_score=getattr(sc, "similarity_score", None),
                        )
                        relevant_contexts.append(rc)
                        if rc.similarity_score is not None and rc.context_id:
                            relevance_scores[rc.context_id] = float(rc.similarity_score)

                    # Minimal viable conversation history and preferences for now
                    conversation_history: list[ConversationMessage] = []
                    user_preferences: dict[str, Any] = {}
                    project_context: dict[str, Any] = {}

                    # Simple continuity heuristic: cache hit preferred
                    session_continuity_score = 0.9 if cache_hit else 0.6

                    elapsed_ms = (time.time() - start) * 1000.0

                    return RehydrationResult(
                        rehydrated_context=rehydrated_context,
                        conversation_history=conversation_history,
                        user_preferences=user_preferences,
                        project_context=project_context,
                        relevant_contexts=relevant_contexts,
                        session_continuity_score=session_continuity_score,
                        context_relevance_scores=relevance_scores,
                        rehydration_time_ms=elapsed_ms,
                        cache_hit=cache_hit,
                        metadata={
                            "adapter": "ltst_memory_integration",
                            "session_id": request.session_id,
                            "user_id": request.user_id,
                            "role": request.metadata.get("role"),
                            "mode": "normal",
                        },
                    )
            except Exception:
                # On any runtime error (e.g., DB unavailable), fall back gracefully
                return self._degraded_fallback(request, start)

        return _run_async(_do_rehydrate())

    def _degraded_fallback(self, request: RehydrationRequest, start_time: float) -> RehydrationResult:
        """Return a safe, local-file-based context when external systems are unavailable."""
        # Try to read a lightweight local memory file as a stopgap
        candidates = [
            os.path.join(os.getcwd(), "100_memory", "100_cursor-memory-context.md"),
            os.path.join(os.getcwd(), "400_guides", "400_system-overview.md"),
        ]
        content = ""
        source = None
        for p in candidates:
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    content = f.read(4000)
                    source = p
                    break
            except Exception:
                continue

        elapsed_ms = (time.time() - start_time) * 1000.0
        return RehydrationResult(
            rehydrated_context=content or "",
            conversation_history=[],
            user_preferences={},
            project_context={},
            relevant_contexts=[],
            session_continuity_score=0.5,
            context_relevance_scores={},
            rehydration_time_ms=elapsed_ms,
            cache_hit=False,
            metadata={
                "adapter": "ltst_memory_integration",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "role": request.metadata.get("role"),
                "mode": "degraded",
                "fallback_source": source,
            },
        )


def rehydrate(
    *,
    query: str,
    role: str = "planner",
    stability: float | None = None,
    use_rrf: bool | None = None,
    dedupe: str | None = None,
    expand_query: str | None = None,
    use_entity_expansion: bool | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
) -> MemoryBundle:
    """Cursor-friendly wrapper that returns a MemoryBundle with text+meta.

    Parameters mirror scripts/cursor_memory_rehydrate.py and are recorded in meta.
    """
    # Build request
    req = RehydrationRequest(
        session_id=session_id or f"rehydrate_{int(time.time())}",
        user_id=user_id or os.getenv("USER", "rehydrator"),
        current_message=query,
        context_types=["conversation", "preference", "project", "user_info"],
        max_context_length=10000,
        include_conversation_history=True,
        history_limit=20,
        relevance_threshold=0.7,
        similarity_threshold=0.8,
        metadata={"role": role},
    )

    rehydrator = MemoryRehydrator()
    result = rehydrator.rehydrate_memory(req)

    # Compose human-friendly text bundle
    header = [
        f"[ROLE] {role}",
        f"[TASK] {query}",
        "",
    ]
    body = result.rehydrated_context or ""

    # Optionally append a compact section of similar contexts if present
    similar_lines: list[str] = []
    if result.relevant_contexts:
        similar_lines.append("")
        similar_lines.append("[SIMILAR CONTEXTS]")
        for i, rc in enumerate(result.relevant_contexts[:5], 1):
            snippet = (rc.content or "").strip().replace("\n", " ")
            if len(snippet) > 300:
                snippet = snippet[:300] + "..."
            similar_lines.append(f"— {i}. {snippet}")

    text = "\n".join(header) + body + ("\n" + "\n".join(similar_lines) if similar_lines else "")

    meta = {
        "total_chunks": (1 if body else 0) + len(result.relevant_contexts or []),
        "processing_time": round(result.rehydration_time_ms / 1000.0, 3),
        "cache_hit": result.cache_hit,
        "mode": result.metadata.get("mode"),
        "flags": {
            "stability": stability,
            "use_rrf": use_rrf,
            "dedupe": dedupe,
            "expand_query": expand_query,
            "use_entity_expansion": use_entity_expansion,
        },
    }

    return MemoryBundle(text=text, meta=meta)
