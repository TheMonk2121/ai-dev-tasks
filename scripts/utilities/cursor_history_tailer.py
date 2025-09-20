#!/usr/bin/env python3
"""Tail Cursor chat history from SQLite into Postgres in near real-time."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import logging
import os
import sqlite3
import sys
import time
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

import psycopg
from sentence_transformers import SentenceTransformer

# Ensure project root available for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.psycopg3_config import Psycopg3Config

LOGGER = logging.getLogger("cursor_history_tailer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_EMBEDDER: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBEDDER


@dataclass
class CursorMessage:
    workspace_id: str
    conversation_id: str
    index: int
    role: str
    content: str
    timestamp: datetime

    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


def find_state_dbs(explicit_path: Path | None = None) -> Iterator[Path]:
    if explicit_path:
        if explicit_path.is_file():
            yield explicit_path
        return

    candidates: Iterable[Path] = []
    base_paths = []

    mac_root = Path.home() / "Library/Application Support/Cursor/User/workspaceStorage"
    if mac_root.exists():
        base_paths.append(mac_root)

    win_root = os.environ.get("APPDATA")
    if win_root:
        win_root_path = Path(win_root) / "Cursor/User/workspaceStorage"
        if win_root_path.exists():
            base_paths.append(win_root_path)

    for root in base_paths:
        for sub in root.iterdir():
            db_path = sub / "state.vscdb"
            if db_path.exists():
                yield db_path


def decode_conversation_blob(value: str) -> dict:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        try:
            decoded = base64.b64decode(value)
            return json.loads(decoded)
        except Exception as exc:  # pragma: no cover - conservative fallback
            LOGGER.warning("Failed to decode conversation blob: %s", exc)
            return {}


def cursor_messages_from_db(db_path: Path) -> Iterator[CursorMessage]:
    workspace_id = db_path.parent.name
    LOGGER.debug("Reading conversations from %s", db_path)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE 'composerData:%'")
        rows = cur.fetchall()
    finally:
        conn.close()

    embedder = get_embedder()
    empty_embedding = embedder.encode([""])[0].tolist()
    _ = empty_embedding  # ensure model is initialized even if no rows

    for key, raw_value in rows:
        payload = decode_conversation_blob(raw_value)
        messages = payload.get("conversation") or payload.get("messages") or []
        if not messages:
            continue

        convo_id = key.split(":", 1)[-1]
        for idx, message in enumerate(messages):
            role = "human" if message.get("type") == 1 else "ai"
            content = format_message(message)
            ts_ms = message.get("timingInfo", {}).get("clientStartTime", 0)
            if ts_ms:
                timestamp = datetime.fromtimestamp(ts_ms / 1000.0, tz=UTC)
            else:
                timestamp = datetime.now(UTC)
            yield CursorMessage(
                workspace_id=workspace_id,
                conversation_id=convo_id,
                index=idx,
                role=role,
                content=content,
                timestamp=timestamp,
            )


def format_message(message: dict) -> str:
    parts: list[str] = []
    role = "User" if message.get("type") == 1 else "Assistant"
    header = f"**{role}**"
    ts_ms = message.get("timingInfo", {}).get("clientStartTime")
    if ts_ms:
        ts = datetime.fromtimestamp(ts_ms / 1000.0, tz=UTC).strftime("%Y-%m-%d %H:%M:%S %Z")
        header += f" ({ts})"
    parts.append(header + ":")

    text = (message.get("text") or "").strip()
    if text:
        parts.append(text)

    for block in message.get("codeBlocks", []) or []:
        code = block.get("code", "")
        language = block.get("language", "")
        if code:
            parts.append(f"```{language}\n{code}\n```")

    file_actions = message.get("fileActions") or []
    if file_actions:
        parts.append("\n**File Actions:**")
        for action in file_actions:
            action_type = action.get("type", "unknown")
            path = action.get("path", "unknown path")
            parts.append(f"- {action_type}: {path}")
            content = action.get("content")
            if content:
                parts.append(f"```\n{content}\n```")

    return "\n\n".join(parts).strip()


def ensure_session_and_thread(
    cur: psycopg.Cursor, workspace_id: str, conversation_id: str, title: str
) -> tuple[str, str]:
    session_id = f"cursor_session_{workspace_id}_{conversation_id}"
    thread_id = f"cursor:{workspace_id}:{conversation_id}"
    now = datetime.now(UTC)
    metadata = json.dumps({"workspace": workspace_id, "capture_type": "history"})

    cur.execute(
        """
        INSERT INTO conversation_sessions
        (session_id, user_id, session_name, session_type, status, created_at, last_activity, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (session_id) DO UPDATE SET
            last_activity = EXCLUDED.last_activity,
            metadata = EXCLUDED.metadata
        """,
        (session_id, "cursor_user", title, "cursor_ai", "active", now, now, metadata),
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
        (thread_id, session_id, "cursor_tab", title, "active", empty_embedding, metadata, now, now),
    )

    return session_id, thread_id


def insert_message(cur: psycopg.Cursor, session_id: str, thread_id: str, message: CursorMessage) -> None:
    embedder = get_embedder()
    embedding = embedder.encode([message.content])[0].tolist()
    metadata = json.dumps(
        {
            "workspace": message.workspace_id,
            "conversation_id": message.conversation_id,
            "capture_type": "history",
            "content_length": len(message.content),
            "word_count": len(message.content.split()),
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


def process_database(db_path: Path) -> None:
    LOGGER.info("Processing Cursor database: %s", db_path)
    messages = list(cursor_messages_from_db(db_path))
    if not messages:
        LOGGER.info("No messages found in %s", db_path)
        return

    with Psycopg3Config.get_connection("memory") as conn:
        with conn.cursor() as cur:
            conversations: dict[tuple[str, str], list[CursorMessage]] = {}
            for msg in messages:
                key = (msg.workspace_id, msg.conversation_id)
                conversations.setdefault(key, []).append(msg)

            for (workspace_id, convo_id), convo_messages in conversations.items():
                convo_messages.sort(key=lambda m: m.index)
                title = next(
                    (m.content.split("\n", 1)[0] for m in convo_messages if m.role == "human" and m.content), None
                )
                if not title:
                    title = f"Cursor Chat {convo_id[:8]}"
                session_id, thread_id = ensure_session_and_thread(cur, workspace_id, convo_id, title)
                for message in convo_messages:
                    insert_message(cur, session_id, thread_id, message)
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Tail Cursor chat history into Postgres")
    parser.add_argument("--db", type=Path, default=None, help="Optional path to a specific state.vscdb file")
    parser.add_argument("--interval", type=float, default=0.0, help="Polling interval in seconds (0 for one-shot)")
    args = parser.parse_args()

    def _run_once() -> None:
        db_paths = list(find_state_dbs(args.db))
        if not db_paths:
            LOGGER.warning("No Cursor chat databases found")
            return
        for db_path in db_paths:
            try:
                process_database(db_path)
            except Exception as exc:
                LOGGER.error("Failed processing %s: %s", db_path, exc, exc_info=True)

    if args.interval <= 0:
        _run_once()
        return

    LOGGER.info("Starting tailer with interval %.2f seconds", args.interval)
    while True:
        _run_once()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
