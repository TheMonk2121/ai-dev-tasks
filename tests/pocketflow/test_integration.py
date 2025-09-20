from __future__ import annotations

from datetime import UTC, datetime, timezone
from typing import Any

import pytest

from pocketflow import integration
from pocketflow.shared_state import ConversationSummary, ConversationTurn, RetrievedHit, SharedState


class FakeCursor:
    def __init__(self, statements: list[tuple[str, tuple[Any, ...]]]) -> None:
        self._statements = statements

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - no-op
        return None

    def execute(self, sql: str, params: tuple[Any, ...]) -> None:
        self._statements.append((sql, params))


class FakeConnection:
    def __init__(self, statements: list[tuple[str, tuple[Any, ...]]], commits: list[bool]) -> None:
        self._statements = statements
        self._commits = commits

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._statements)

    def commit(self) -> None:
        self._commits.append(True)

    def __enter__(self) -> FakeConnection:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - no-op
        return None


def test_persist_turn_inserts(monkeypatch: pytest.MonkeyPatch) -> None:
    statements: list[tuple[str, tuple[Any, ...]]] = []
    commits: list[bool] = []
    monkeypatch.setattr(
        integration,
        "connect",
        lambda role="memory": FakeConnection(statements, commits),
    )

    state = SharedState(session_id="session-1")
    turn = ConversationTurn(
        turn_id="turn-1",
        thread_id="thread-1",
        role="user",
        content="hello world",
        created_at=datetime.now(UTC),
    )

    saved = integration._persist_turn(state, turn)

    assert statements, "expected an insert statement"
    sql, params = statements[0]
    assert "INSERT INTO conversation_messages" in sql
    assert params[1] == "user"
    assert commits and commits[0] is True
    assert saved.metadata.get("content_hash")


def test_hybrid_retriever_returns_hits(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_build_channel_queries(question: str, tag: str) -> dict[str, str]:
        return {"short": "s", "title": "t", "bm25": "bm"}

    sample_rows = [
        {
            "retrieval_stage": "hybrid",
            "rerank_score": 0.9,
            "filename": "file.md",
            "file_path": "docs/file.md",
            "chunk_id": "chunk-1",
            "text_for_reader": "content text",
            "metadata": {"ingest_run_id": "demo"},
        }
    ]

    monkeypatch.setattr(integration, "build_channel_queries", fake_build_channel_queries)
    monkeypatch.setattr(integration, "run_fused_query", lambda *args, **kwargs: sample_rows)

    state = SharedState()
    state.retrieval.query = "What is PocketFlow?"

    hits = integration._hybrid_retriever(state)

    assert len(hits) == 1
    hit = hits[0]
    assert hit.content == "content text"
    assert hit.file_path == "docs/file.md"
    assert state.retrieval.params["queries"]["short"] == "s"


def test_default_composer_uses_rag_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    # Prepare fake program
    class FakePrediction:
        def __init__(self, answer: str) -> None:
            self.answer = answer

    class FakeRAG:
        precheck_enabled = False
        abstain_enabled = False
        enforce_span = False
        precheck_min_overlap = 0.1
        _lm = object()

        def __init__(self) -> None:
            self.used_contexts = []

        def _likely_answerable(self, context: str, question: str, min_overlap: float) -> bool:  # noqa: D401
            return True

        def cls(self, *args, **kwargs):  # noqa: D401
            return FakePrediction("yes")

        def gen(self, *args, **kwargs):  # noqa: D401
            return FakePrediction("Generated answer")

    fake_prog = FakeRAG()
    monkeypatch.setattr(integration, "_get_rag_program", lambda: fake_prog)
    integration._RAG_PROGRAM = fake_prog

    monkeypatch.setattr(
        integration,
        "build_reader_context",
        lambda rows, question, tag, compact=True: ("\n".join(r["text_for_reader"] for r in rows), {}),
    )
    monkeypatch.setattr(integration, "pick_span", lambda *args, **kwargs: None)
    monkeypatch.setattr(integration, "normalize_answer", lambda text, tag: f"norm:{text}")
    monkeypatch.setattr(integration, "_answer_in_context", lambda *args, **kwargs: True)
    monkeypatch.setattr(integration, "_best_sentence_from_context", lambda *args, **kwargs: "fallback")

    state = SharedState()
    state.retrieval.query = "What is PocketFlow?"
    state.retrieval.params["tag"] = "rag_qa_single"
    state.retrieval.merged = [
        RetrievedHit(
            source="hybrid",
            score=0.9,
            document_id="file.md",
            file_path="docs/file.md",
            chunk_id="chunk-1",
            content="context text",
            metadata={},
        )
    ]
    state.summary = ConversationSummary(text="Summary text", token_count=2)

    answer = integration._default_composer(state)

    assert answer.startswith("norm:Generated answer")
    assert "Summary text" in answer
