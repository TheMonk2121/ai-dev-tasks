from __future__ import annotations

import os
import sys

import psycopg

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config

#!/usr/bin/env python3

def _conn():
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    return psycopg.connect(dsn)

def _timescale_version(cur) -> tuple[int, int, int] | None:
    cur.execute("SELECT extversion FROM pg_extension WHERE extname='timescaledb'")
    row = cur.fetchone()
    if not row:
        return None
    parts = str(row[0]).split(".")
    try:
        return int(parts[0]), int(parts[1]), int(parts[2] if len(parts) > 2 else 0)
    except Exception:
        return None

def main() -> int:
    with _conn() as conn:
        with conn.cursor() as cur:
            # Extensions (best-effort)
            for ext in ("timescaledb", "vector", "pg_trgm"):
                try:
                    cur.execute(f"CREATE EXTENSION IF NOT EXISTS {ext}")
                except Exception as e:
                    print(f"⚠️  Skipping extension {ext}: {e}")

            # Tables
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluation_metrics (
                  ts              timestamptz NOT NULL DEFAULT now(),
                  run_id          uuid        NOT NULL,
                  profile         text        NOT NULL,
                  pass_id         text        NOT NULL,
                  f1              double precision,
                  precision       double precision,
                  recall          double precision,
                  faithfulness    double precision,
                  artifact_path   text,
                  git_sha         text,
                  tags            text[] DEFAULT '{}',
                  PRIMARY KEY (ts, run_id)
                )
                """
            )

            # Hypertable
            try:
                cur.execute("SELECT create_hypertable('evaluation_metrics', 'ts', if_not_exists => true)")
            except Exception as e:
                print(f"⚠️  create_hypertable: {e}")

            # Columnstore/compression + policies
            ver = _timescale_version(cur)
            try:
                if ver and (ver[0], ver[1]) >= (2, 18):
                    cur.execute(
                        """
                        ALTER TABLE evaluation_metrics SET (
                          timescaledb.enable_columnstore,
                          timescaledb.orderby  = 'ts DESC',
                          timescaledb.segmentby = 'profile'
                        )
                        """
                    )
                    cur.execute("CALL add_columnstore_policy('evaluation_metrics', after => INTERVAL '7 days')")
                    cur.execute("SELECT add_retention_policy('evaluation_metrics', INTERVAL '180 days')")
                else:
                    cur.execute(
                        """
                        ALTER TABLE evaluation_metrics SET (
                          timescaledb.compress,
                          timescaledb.compress_orderby   = 'ts DESC',
                          timescaledb.compress_segmentby = 'profile'
                        )
                        """
                    )
                    cur.execute("SELECT add_compression_policy('evaluation_metrics', INTERVAL '7 days')")
            except Exception as e:
                print(f"⚠️  Policy setup skipped: {e}")

        conn.commit()
    print("✅ Timeseries setup complete (evaluation_metrics)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
