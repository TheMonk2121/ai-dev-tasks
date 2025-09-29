from __future__ import annotations

import contextlib
import os
from datetime import UTC, datetime
from typing import Any

try:
    # Optional dependency; file guards runtime if missing
    from pydantic_graph.persistence import BaseStatePersistence
except Exception:  # pragma: no cover - import-safe in environments without pydantic-graph
    # Create a proper base class when pydantic-graph is not available
    class BaseStatePersistence:
        def __init__(self) -> None:
            pass


# Add project paths
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from psycopg.rows import dict_row
from psycopg.types.json import Json

from src.common.psycopg3_config import Psycopg3Config


def _connect_dsn() -> Any:
    # Use Psycopg3Config for database connections
    return Psycopg3Config.get_cursor("default")


_DDL = """
CREATE TABLE IF NOT EXISTS graph_run_snapshots (
  run_id TEXT NOT NULL,
  snapshot_id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('node','end')),
  status TEXT NOT NULL,
  state_json JSONB,
  node_json JSONB,
  result_json JSONB,
  start_ts TIMESTAMPTZ,
  duration_sec DOUBLE PRECISION,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


class PgStatePersistence(BaseStatePersistence):  # type: ignore[misc]
    def __init__(self, run_id: str) -> None:
        super().__init__()
        self.run_id: str = run_id
        # Best-effort table creation
        with contextlib.suppress(Exception):
            with _connect_dsn() as conn:
                with conn.cursor() as cur:
                    cur.execute(_DDL)
                conn.commit()

    def snapshot_node(self, state: Any, next_node: Any) -> str:
        sid = f"{self.run_id}:{int(datetime.now(UTC).timestamp()*1000)}"
        with _connect_dsn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO graph_run_snapshots
                      (run_id, snapshot_id, kind, status, state_json, node_json, start_ts)
                    VALUES (%s,%s,'node','created',%s,%s,now())
                    """,
                    (
                        self.run_id,
                        sid,
                        Json(state) if Json else None,
                        Json(getattr(next_node, "__dict__", {})) if Json else None,
                    ),
                )
            conn.commit()
        return sid

    def snapshot_node_if_new(self, snapshot_id: str, state: Any, next_node: Any) -> str:
        with _connect_dsn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM graph_run_snapshots WHERE snapshot_id=%s", (snapshot_id,))
                exists = cur.fetchone() is not None
                if not exists:
                    cur.execute(
                        """
                        INSERT INTO graph_run_snapshots
                          (run_id, snapshot_id, kind, status, state_json, node_json, start_ts)
                        VALUES (%s,%s,'node','created',%s,%s,now())
                        """,
                        (
                            self.run_id,
                            snapshot_id,
                            Json(state) if Json else None,
                            Json(getattr(next_node, "__dict__", {})) if Json else None,
                        ),
                    )
            conn.commit()
        return snapshot_id

    def snapshot_end(self, state: Any, end: Any) -> str:
        sid = f"{self.run_id}:end:{int(datetime.now(UTC).timestamp()*1000)}"
        with _connect_dsn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO graph_run_snapshots
                      (run_id, snapshot_id, kind, status, state_json, result_json, start_ts)
                    VALUES (%s,%s,'end','success',%s,%s,now())
                    """,
                    (
                        self.run_id,
                        sid,
                        Json(state) if Json else None,
                        Json(getattr(end, "__dict__", end)) if Json else None,
                    ),
                )
            conn.commit()
        return sid

    @contextlib.contextmanager
    def record_run(self, snapshot_id: str):  # type: ignore[override]
        start = datetime.now(UTC)
        try:
            yield
            status = "success"
        except Exception:
            status = "error"
            raise
        finally:
            duration = (datetime.now(UTC) - start).total_seconds()
            with contextlib.suppress(Exception):
                with _connect_dsn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE graph_run_snapshots
                               SET status=%s, duration_sec=%s
                             WHERE snapshot_id=%s
                            """,
                            (status, duration, snapshot_id),
                        )
                    conn.commit()

    def load_all(self) -> list[dict[str, Any]]:  # type: ignore[override]
        with _connect_dsn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT * FROM graph_run_snapshots WHERE run_id=%s ORDER BY created_at ASC",
                    (self.run_id,),
                )
                rows = cur.fetchall()
        return list(rows)
