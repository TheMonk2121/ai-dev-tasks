from __future__ import annotations
import os
import sys
from utils.db_pool import get_conn  # type: ignore[import-untyped]
from utils.decision_extractor import create_decisions_table  # type: ignore[import-untyped]
from utils.supersedence_retrieval import create_supersedence_tables  # type: ignore[import-untyped]
#!/usr/bin/env python3
"""
Minimal DB smoke check for pool + schema changes.

What it does (read-only except for idempotent setup calls):
- Verifies per-role GUCs/timeouts are applied on checkout
- Runs decisions/supersedence setup (idempotent DDL)
- Checks for expected indexes, FKs, and helper functions

Usage:
  export DATABASE_URL=postgresql://user@host:5432/db
  python scripts/db_smoke_check.py
"""

# DSPy modules moved to main src directory
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DSRC = os.path.join(ROOT, "src")
if DSRC not in sys.path:
    sys.path.insert(0, DSRC)

def show_gucs(role: str) -> None:
    print(f"\n[GUCs] role={role}")
    with get_conn(role=role) as conn:
        with conn.cursor() as cur:
            cur.execute("SHOW application_name;")
            app = cur.fetchone()[0]
            cur.execute("SHOW statement_timeout;")
            st = cur.fetchone()[0]
            cur.execute("SHOW idle_in_transaction_session_timeout;")
            it = cur.fetchone()[0]
            # Optional: show plan cache mode if supported
            try:
                cur.execute("SHOW plan_cache_mode;")
                pcm = cur.fetchone()[0]
            except Exception:
                pcm = "(n/a)"
            print(f"application_name={app}, statement_timeout={st}, idle_in_xact_timeout={it}, plan_cache_mode={pcm}")

def ensure_setup() -> None:
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("[WARN] DATABASE_URL not set; using pool env. Make sure db_pool can resolve.")

    # Idempotent setup for decisions + supersedence
    ok1 = create_decisions_table(dsn or "")
    ok2 = create_supersedence_tables(dsn or "")
    print(f"\n[Setup] decisions_table={ok1}, supersedence_tables={ok2}")

def check_decisions_indexes() -> None:
    print("\n[Checks] decisions indexes + triggers")
    expected_indexes: list[str] = [
        "idx_decisions_session_id",
        "idx_decisions_decision_key",
        "idx_decisions_superseded",
        "idx_decisions_confidence",
        "idx_decisions_active",
        "idx_decisions_session_active",
        "idx_decisions_head_trgm",
        "idx_decisions_rationale_trgm",
    ]
    with get_conn(role="retrieval") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT extname FROM pg_extension WHERE extname='pg_trgm';")
            has_trgm = bool(cur.fetchone())
            cur.execute("SELECT indexname FROM pg_indexes WHERE tablename='decisions';")
            present = {result.get("key", "")

            missing = [i for i in expected_indexes if i not in present]
            print(f"pg_trgm={'yes' if has_trgm else 'no'}; missing_indexes={missing if missing else 'none'}")

            cur.execute(
                """
                SELECT tgname FROM pg_trigger WHERE tgname='trg_decisions_set_updated_at';
                """
            )
            has_trg = bool(cur.fetchone())
            print(f"updated_at_trigger={'present' if has_trg else 'missing'}")

def check_supersedence_fks() -> None:
    print("\n[Checks] supersedence foreign keys")
    with get_conn(role="retrieval") as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT tc.constraint_name
                FROM information_schema.table_constraints tc
                WHERE tc.table_name='decision_supersedence_log'
                  AND tc.constraint_type='FOREIGN KEY'
                  AND tc.constraint_name IN (
                    'fk_supersedence_log_superseded',
                    'fk_supersedence_log_superseding'
                  );
                """
            )
            fks = {result.get("key", "")
            missing = [
                n
                for n in (
                    "fk_supersedence_log_superseded",
                    "fk_supersedence_log_superseding",
                )
                if n not in fks
            ]
            print(f"missing_fks={missing if missing else 'none'}")

def check_performance_helpers() -> None:
    print("\n[Checks] performance helpers")
    with get_conn(role="retrieval") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_proc WHERE proname='ensure_future_performance_partitions';")
            has_fn = bool(cur.fetchone())
    print(f"ensure_future_performance_partitions={'present' if has_fn else 'missing'}")

def check_retrieval_indexes() -> None:
    print("\n[Checks] retrieval indexes (document_chunks/documents)")
    expected = [
        ("document_chunks", "idx_dc_content_tsv"),
        ("document_chunks", "idx_dc_docid_chunk"),
        ("document_chunks", "idx_dc_embedding_ivfflat"),
        ("documents", "idx_documents_filename"),
    ]
    with get_conn(role="retrieval") as conn:
        with conn.cursor() as cur:
            # vector extension
            cur.execute("SELECT extname FROM pg_extension WHERE extname='vector';")
            has_vector = bool(cur.fetchone())
            # collect indexes
            present = set()
            for table, _ in expected:
                cur.execute("SELECT indexname FROM pg_indexes WHERE tablename=%s;", (table,))
                for row in cur.fetchall():
                    present.add((table, result.get("key", "")
            missing = [pair for pair in expected if pair not in present]
            print(f"vector_ext={'yes' if has_vector else 'no'}; missing={missing if missing else 'none'}")

def main() -> None:
    # Verify GUCs for two roles
    show_gucs("retrieval")
    show_gucs("writer")
    # Run idempotent setup and structural checks
    ensure_setup()
    check_decisions_indexes()
    check_supersedence_fks()
    check_performance_helpers()
    check_retrieval_indexes()
    print("\n[OK] DB smoke completed.")

if __name__ == "__main__":
    main()
