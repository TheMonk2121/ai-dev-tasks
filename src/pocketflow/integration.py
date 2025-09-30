"""Convenience builders that connect PocketFlow nodes with real repo behaviors."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime, timezone
from typing import Any

from dspy_modules.dspy_reader_program import (
    RAGAnswer,
    _answer_in_context,
    _best_sentence_from_context,
    _generate_query_embedding,
    build_reader_context,
)
from dspy_modules.reader.span_picker import normalize_answer, pick_span
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from graphs.memory_graphs.consolidate import Turn as MemoryTurn
from graphs.memory_graphs.consolidate import extract_facts as memory_extract_facts
from graphs.memory_graphs.consolidate import summarize as memory_summarize
from pocketflow.flows import Flow, Parallel, build_answer_flow, build_capture_flow
from pocketflow.nodes import (
    AppendTurnNode,
    ComposeAnswerNode,
    ExtractFactsNode,
    IndexFactsNode,
    MaybeSummarizeNode,
    MergeResultsNode,
    RetrieveNode,
)
from pocketflow.shared_state import ConversationSummary, ConversationTurn, RetrievedHit, SharedState
from src.common.db_sync import connect

logger = logging.getLogger(__name__)
_rag_program_cache: RAGAnswer | None = None


def _get_rag_program() -> RAGAnswer:
    global _rag_program_cache
    if _rag_program_cache is None:
        _rag_program_cache = RAGAnswer()
    return _rag_program_cache


def _session_id_from_state(state: SharedState, turn: ConversationTurn | None = None) -> str:
    if state.session_id:
        return state.session_id
    if turn and turn.thread_id:
        return turn.thread_id
    if state.turns:
        return state.turns[0].thread_id
    return "default_session"


def _persist_turn(state: SharedState, turn: ConversationTurn) -> ConversationTurn:
    """Write the turn into the conversation_messages table and mirror into state."""

    session_id = _session_id_from_state(state, turn)
    created_at = turn.created_at or datetime.now(UTC)
    content_hash = uuid.uuid5(uuid.NAMESPACE_URL, f"{session_id}:{turn.role}:{turn.content}").hex
    metadata_json = json.dumps(turn.metadata or {})

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            with connect("memory") as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO conversation_messages (session_id, role, content, content_hash, metadata, created_at)
                        SELECT %s, %s, %s, %s, %s::jsonb, %s
                        WHERE NOT EXISTS (
                            SELECT 1 FROM conversation_messages
                            WHERE session_id = %s AND content_hash = %s
                        )
                        """,
                        (
                            session_id,
                            turn.role,
                            turn.content,
                            content_hash,
                            metadata_json,
                            created_at,
                            session_id,
                            content_hash,
                        ),
                    )
                conn.commit()
            break
        except Exception as exc:  # pragma: no cover - network/db outage path
            logger.warning("Persist turn attempt %s failed: %s", attempt, exc, exc_info=True)
            if attempt == max_attempts:
                logger.error("Failed to persist turn after %s attempts", max_attempts)
            else:
                time.sleep(0.2 * attempt)

    if not turn.turn_id:
        turn.turn_id = f"turn_{uuid.uuid4().hex}"
    turn.metadata.setdefault("content_hash", content_hash)
    return turn


def _memory_summarizer(turns: Sequence[ConversationTurn]) -> ConversationSummary:
    memory_turns = [
        MemoryTurn(role=t.role, content=t.content, timestamp=(t.created_at.timestamp() if t.created_at else None))
        for t in turns
    ]
    summary_text = memory_summarize(memory_turns)
    token_count = len(summary_text.split()) if summary_text else 0
    return ConversationSummary(text=summary_text, token_count=token_count)


def _extract_structured_facts(turns: Sequence[ConversationTurn], summary_text: str) -> list[dict[str, Any]]:
    memory_turns = [
        MemoryTurn(role=t.role, content=t.content, timestamp=(t.created_at.timestamp() if t.created_at else None))
        for t in turns
    ]
    facts = memory_extract_facts(memory_turns, summary_text)
    return [asdict(fact) for fact in facts]


def _index_facts(facts: list[dict[str, Any]], state: SharedState) -> None:
    if not facts:
        return

    session_id = _session_id_from_state(state)
    now = datetime.now(UTC)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            with connect("memory") as conn:
                with conn.cursor() as cur:
                    for fact in facts:
                        content = fact.get("text") or fact.get("summary") or ""
                        metadata_json = json.dumps(fact)
                        cur.execute(
                            """
                            INSERT INTO conversation_memory (session_id, content, metadata, created_at)
                            SELECT %s, %s, %s::jsonb, %s
                            WHERE NOT EXISTS (
                                SELECT 1 FROM conversation_memory
                                WHERE session_id = %s AND metadata ->> 'text' = %s
                            )
                            """,
                            (
                                session_id,
                                content,
                                metadata_json,
                                now,
                                session_id,
                                fact.get("text") or fact.get("summary") or "",
                            ),
                        )
                conn.commit()
            break
        except Exception as exc:  # pragma: no cover
            logger.warning("Index facts attempt %s failed: %s", attempt, exc, exc_info=True)
            if attempt == max_attempts:
                logger.error("Failed to index facts after %s attempts", max_attempts)
            else:
                time.sleep(0.2 * attempt)


def _hybrid_retriever(state: SharedState) -> list[RetrievedHit]:
    question = state.retrieval.query or (state.turns[-1].content if state.turns else "")
    if not question:
        return []

    tag = state.retrieval.params.get("tag", "")
    queries = state.retrieval.params.get("queries")
    if not queries:
        queries = build_channel_queries(question, tag)
        state.retrieval.params["queries"] = queries

    query_text = queries["short"] or queries["title"] or queries["bm25"] or question
    qvec = _generate_query_embedding(query_text)
    k = int(state.retrieval.params.get("k", 25))

    rows: list[dict[str, object]] = []
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            rows = run_fused_query(
                queries["short"],
                queries["title"],
                queries["bm25"],
                qvec=qvec,
                tag=tag,
                k=k,
                return_components=True,
            )
            break
        except Exception as exc:
            logger.warning("Hybrid retrieval attempt %s failed: %s", attempt, exc, exc_info=True)
            if attempt == max_attempts:
                logger.error("Hybrid retrieval failed for question '%s'", question)
                return []
            time.sleep(0.2 * attempt)

    hits: list[RetrievedHit] = []
    for row in rows:
        raw_metadata = row.get("metadata") or {}
        metadata = {str(k): v for k, v in raw_metadata.items()} if isinstance(raw_metadata, dict) else {}
        hits.append(
            RetrievedHit(
                source=str(row.get("retrieval_stage") or "hybrid"),
                score=float(str(row.get("rerank_score") or row.get("score") or 0.0)),
                document_id=str(row.get("filename") or row.get("file_path")) if row.get("filename") or row.get("file_path") else None,
                file_path=str(row.get("file_path")) if row.get("file_path") else None,
                chunk_id=str(row.get("chunk_id")) if row.get("chunk_id") is not None else None,
                content=str(row.get("text_for_reader") or row.get("content") or ""),
                metadata=metadata,
            )
        )
    return hits


def _flat_merger(hits: dict[str, list[RetrievedHit]]) -> list[RetrievedHit]:
    merged: list[RetrievedHit] = []
    for source_hits in hits.values():
        merged.extend(source_hits)
    merged.sort(key=lambda hit: hit.score, reverse=True)
    return merged


def _default_composer(state: SharedState) -> str:
    question = state.retrieval.query
    if not question:
        return "No question supplied."

    merged_hits = state.retrieval.merged or []
    if not merged_hits:
        return f"Question: {question}\nNo supporting context found."

    tag = state.retrieval.params.get("tag", "rag_qa_single")
    prog = _get_rag_program()

    rows: list[dict[str, object]] = []
    for hit in merged_hits:
        rows.append(
            {
                "chunk_id": hit.chunk_id,
                "file_path": hit.file_path,
                "filename": hit.document_id,
                "text_for_reader": hit.content,
                "text": hit.content,
                "score": hit.score,
                "metadata": hit.metadata,
            }
        )

    try:
        compact = bool(int(os.getenv("READER_COMPACT", "1")))
    except Exception:  # pragma: no cover - env parsing fallback
        compact = True

    context_str, _ = build_reader_context(rows, question, tag, compact=compact)
    prog.used_contexts = rows

    span = pick_span(context_str, question, tag)
    if span:
        answer = normalize_answer(span, tag)
    else:
        if prog.precheck_enabled and not prog._likely_answerable(context_str, question, prog.precheck_min_overlap):
            answer = "I don't know"
        else:
            if prog.abstain_enabled:
                cls_pred = prog.cls(context=context_str, question=question)
                label = str(getattr(cls_pred, "label", "")).strip().lower()
                if label != "yes":
                    answer = "I don't know"
                else:
                    answer = None
            else:
                answer = None

            if answer is None:
                import dspy

                if prog._lm is None:
                    prog_local = RAGAnswer()
                    globals()["_rag_program_cache"] = prog_local
                    prog = prog_local

                if dspy.settings.lm is None and prog._lm is not None:
                    dspy.settings.configure(lm=prog._lm)
                if os.getenv("DSPY_DISABLE_JSON_ADAPTER", "1") == "1":
                    try:
                        dspy.settings.configure(adapter=None)
                    except Exception:  # pragma: no cover - adapter already cleared
                        pass

                gen_pred = prog.gen(context=context_str, question=question)
                answer_text = str(getattr(gen_pred, "answer", "")).strip()
                if prog.enforce_span and answer_text:
                    if not _answer_in_context(answer_text, context_str):
                        fallback = _best_sentence_from_context(context_str, question)
                        if fallback and _answer_in_context(fallback, context_str, min_overlap=0.5):
                            answer_text = fallback
                        else:
                            answer_text = "I don't know"
                answer = normalize_answer(answer_text or "", tag)

    summary = state.summary.text if state.summary else ""
    if summary and answer not in {"I don't know", ""}:
        return f"{answer}\n\nSummary:\n{summary}".strip()
    return answer


def default_capture_flow() -> Flow:
    return build_capture_flow(
        AppendTurnNode(persist_turn=_persist_turn),
        MaybeSummarizeNode(summarizer=_memory_summarizer),
        ExtractFactsNode(extractor=_extract_structured_facts),
        IndexFactsNode(indexer=_index_facts),
    )


def default_answer_flow() -> Flow:
    retrieval_nodes = Parallel(
        nodes=[
            RetrieveNode(source="hybrid", retriever=_hybrid_retriever),
        ]
    )
    return build_answer_flow(
        retrieval_nodes,
        MergeResultsNode(merger=_flat_merger),
        ComposeAnswerNode(composer=_default_composer),
    )


__all__ = ["default_capture_flow", "default_answer_flow"]
