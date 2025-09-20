#!/usr/bin/env python3
"""Tail Codex CLI/IDE chat history from JSONL logs into Postgres."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

import psycopg
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.psycopg3_config import Psycopg3Config

LOGGER = logging.getLogger("codex_history_tailer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_EMBEDDER: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBEDDER


@dataclass
class CodexMessage:
    session_file: Path
    conversation_id: str
    index: int
    role: str
    content: str
    timestamp: datetime

    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


def find_session_logs(root: Path | None = None) -> Iterable[Path]:
    if root:
        base = root
    else:
        base = Path.home() / ".codex/sessions"
    if not base.exists():
        return []
    return sorted(base.glob("**/*.jsonl"))


def parse_jsonl(file_path: Path) -> Iterator[CodexMessage]:
    conversation_id = file_path.stem
    with file_path.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:  # pragma: no cover - corrupt line
                LOGGER.warning("Skipping malformed JSON in %s: %s", file_path, exc)
                continue

            role = payload.get("role") or payload.get("speaker") or "assistant"
            role = role.lower()
            if role not in {"user", "assistant", "system"}:
                role = "assistant"

            raw_content = payload.get("content") or payload.get("text") or ""
            if isinstance(raw_content, list):
                content = "\n".join(map(str, raw_content))
            elif isinstance(raw_content, dict):
                content = json.dumps(raw_content)
            else:
                content = str(raw_content)

            if not content or not isinstance(content, str) or not content.strip():
                continue

            ts = payload.get("timestamp") or payload.get("time")
            if ts:
                try:
                    timestamp = datetime.fromisoformat(ts)
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=UTC)
                except ValueError:
                    try:
                        timestamp = datetime.fromtimestamp(float(ts), tz=UTC)
                    except Exception:
                        timestamp = datetime.now(UTC)
            else:
                timestamp = datetime.now(UTC)

            yield CodexMessage(
                session_file=file_path,
                conversation_id=conversation_id,
                index=idx,
                role="human" if role == "user" else "ai",
                content=content.strip(),
                timestamp=timestamp,
            )


def ensure_session(cur: psycopg.Cursor, conversation_id: str) -> tuple[str, str]:
    session_id = f"codex_session_{conversation_id}"
    thread_id = f"codex:{conversation_id}"
    now = datetime.now(UTC)
    metadata = json.dumps({"capture_type": "codex_history"})

    cur.execute(
        """
        INSERT INTO conversation_sessions
            (session_id, user_id, session_name, session_type, status, created_at, last_activity, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (session_id) DO UPDATE SET
            last_activity = EXCLUDED.last_activity,
            metadata = EXCLUDED.metadata
        """,
        (session_id, "codex_user", f"Codex Session {conversation_id[:8]}", "codex_ai", "active", now, now, metadata),
    )

    embedder = get_embedder()
    empty_embedding = embedder.encode([""])[0].tolist()

    cur.execute(
        """
        INSERT INTO atlas_thread
            (thread_id, session_id, tab_id, title, status, embedding, metadata, created_at, last_activity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (thread_id) DO UPDATE SET
            last_activity = EXCLUDED.last_activity,
            metadata = EXCLUDED.metadata
        """,
        (
            thread_id,
            session_id,
            "codex_tab",
            f"Codex Conversation {conversation_id[:8]}",
            "active",
            empty_embedding,
            metadata,
            now,
            now,
        ),
    )

    return session_id, thread_id


def insert_message(cur: psycopg.Cursor, session_id: str, thread_id: str, message: CodexMessage) -> None:
    embedder = get_embedder()
    embedding = embedder.encode([message.content])[0].tolist()
    metadata = json.dumps(
        {
            "capture_type": "codex_history",
            "session_file": str(message.session_file),
            "message_index": message.index,
            "timestamp": message.timestamp.isoformat(),
        }
    )

    cur.execute(
        """
        INSERT INTO conversation_messages
            (session_id, message_type, role, content, content_hash, message_index, metadata, embedding, created_at)
        SELECT %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM conversation_messages WHERE session_id = %s AND content_hash = %s
        )
        """,
        (
            session_id,
            "message",
            message.role,
            message.content,
            message.content_hash(),
            message.index,
            metadata,
            embedding,
            message.timestamp,
            session_id,
            message.content_hash(),
        ),
    )

    cur.execute(
        """
        INSERT INTO atlas_conversation_turn
            (turn_id, thread_id, role, content, timestamp, embedding, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (turn_id) DO UPDATE SET
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding,
            metadata = EXCLUDED.metadata
        """,
        (
            f"turn_{thread_id}_{message.index}",
            thread_id,
            "user" if message.role == "human" else "assistant",
            message.content,
            message.timestamp,
            embedding,
            metadata,
        ),
    )

    cur.execute(
        "UPDATE atlas_thread SET last_activity = %s WHERE thread_id = %s",
        (message.timestamp, thread_id),
    )
    cur.execute(
        "UPDATE conversation_sessions SET last_activity = %s WHERE session_id = %s",
        (message.timestamp, session_id),
    )


def process_logs(base_path: Path) -> None:
    files = list(find_session_logs(base_path))
    if not files:
        LOGGER.info("No Codex session logs found in %s", base_path)
        return

    with Psycopg3Config.get_connection("memory") as conn:
        with conn.cursor() as cur:
            for file_path in files:
                LOGGER.info("Processing Codex log %s", file_path)
                messages = list(parse_jsonl(file_path))
                if not messages:
                    continue
                session_id, thread_id = ensure_session(cur, messages[0].conversation_id)
                for msg in messages:
                    insert_message(cur, session_id, thread_id, msg)
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Tail Codex chat history into Postgres")
    parser.add_argument("--sessions", type=Path, default=None, help="Path to Codex sessions directory")
    parser.add_argument("--interval", type=float, default=0.0, help="Polling interval seconds (0 for one-shot)")
    args = parser.parse_args()

    base_path = args.sessions or Path.home() / ".codex/sessions"

    def _run_once() -> None:
        try:
            process_logs(base_path)
        except Exception as exc:
            LOGGER.error("Failed processing Codex logs: %s", exc, exc_info=True)

    if args.interval <= 0:
        _run_once()
        return

    LOGGER.info("Starting Codex tailer with %.2f second interval", args.interval)
    while True:
        _run_once()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
