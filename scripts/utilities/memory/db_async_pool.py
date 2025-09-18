#!/usr/bin/env python3
from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional, Tuple

import psycopg
from psycopg_pool import AsyncConnectionPool

# Prefer DATABASE_URL, fallback to POSTGRES_DSN
DB_DSN = (os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN") or "").strip()
if not DB_DSN:
    raise RuntimeError("Set DATABASE_URL or POSTGRES_DSN")

pool: AsyncConnectionPool = AsyncConnectionPool(
    DB_DSN,
    min_size=1,
    max_size=10,
    max_idle=300,
)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


async def advisory_lock(conn: psycopg.AsyncConnection[Any], thread_id: str) -> None:
    async with conn.cursor() as cur:
        await cur.execute("SELECT pg_advisory_xact_lock(hashtext($1))", (thread_id,))


async def ensure_thread_exists(conn: psycopg.AsyncConnection[Any], thread_id: str | None) -> str:
    tid = thread_id or _new_id("thread")
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO atlas_thread(thread_id, last_activity)
            VALUES ($1, NOW())
            ON CONFLICT (thread_id) DO UPDATE
              SET last_activity = GREATEST(atlas_thread.last_activity, EXCLUDED.last_activity)
            """,
            (tid,),
        )
    return tid


async def next_seq(conn: psycopg.AsyncConnection[Any], thread_id: str) -> int:
    async with conn.cursor() as cur:
        await cur.execute(
            """
            UPDATE atlas_thread
               SET next_seq = next_seq + 1
             WHERE thread_id = $1
         RETURNING next_seq
            """,
            (thread_id,),
        )
        row = await cur.fetchone()
        return int(row[0]) if row and row[0] is not None else 0


async def get_parent_turn(conn: psycopg.AsyncConnection[Any], turn_id: str) -> dict[str, Any] | None:
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT turn_id, thread_id, role
              FROM atlas_conversation_turn
             WHERE turn_id = $1
            """,
            (turn_id,),
        )
        row = await cur.fetchone()
        if not row:
            return None
        return {"turn_id": row[0], "thread_id": row[1], "role": row[2]}


async def insert_user_turn(
    conn: psycopg.AsyncConnection[Any], *, thread_id: str, content: str, metadata: dict[str, Any]
) -> tuple[str, int]:
    async with conn.transaction():
        await advisory_lock(conn, thread_id)
        await ensure_thread_exists(conn, thread_id)
        seq = await next_seq(conn, thread_id)
        turn_id = _new_id("turn")
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO atlas_conversation_turn
                    (turn_id, thread_id, seq, role, content, metadata)
                VALUES
                    ($1, $2, $3, 'user', $4, CAST($5 AS JSONB))
                ON CONFLICT (turn_id) DO NOTHING
                """,
                (turn_id, thread_id, seq, content, metadata),
            )
        return turn_id, seq


async def insert_ai_turn(
    conn: psycopg.AsyncConnection[Any],
    *,
    parent_turn_id: str,
    content: str,
    metadata: dict[str, Any],
    status: str = "final",
    explicit_thread_id: str | None = None,
    allow_supersede: bool = False,
) -> tuple[str, str, int]:
    parent = await get_parent_turn(conn, parent_turn_id)
    if not parent:
        raise ValueError("unknown_query_turn_id")
    if parent["role"] != "user":
        raise ValueError("query_turn_not_user_role")
    parent_tid = str(parent["thread_id"])  # ensure str
    if explicit_thread_id and explicit_thread_id != parent_tid:
        raise LookupError(f"thread_id_mismatch:{parent_tid}:{explicit_thread_id}")

    async with conn.transaction():
        await advisory_lock(conn, parent_tid)
        await ensure_thread_exists(conn, parent_tid)
        seq = await next_seq(conn, parent_tid)

        if allow_supersede and status == "final":
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE atlas_conversation_turn
                       SET status = 'superseded'
                     WHERE query_turn_id = $1 AND role='ai' AND status='final'
                    """,
                    (parent_turn_id,),
                )

        turn_id = _new_id("turn")
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO atlas_conversation_turn
                        (turn_id, thread_id, seq, role, content, metadata, query_turn_id, status)
                    VALUES
                        ($1, $2, $3, 'ai', $4, CAST($5 AS JSONB), $6, $7)
                    ON CONFLICT (turn_id) DO NOTHING
                    """,
                    (turn_id, parent_tid, seq, content, metadata, parent_turn_id, status),
                )
        except psycopg.errors.UniqueViolation as e:  # type: ignore[attr-defined]
            raise FileExistsError("parent_already_answered") from e

    return turn_id, parent_tid, seq
