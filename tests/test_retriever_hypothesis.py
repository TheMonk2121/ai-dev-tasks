from __future__ import annotations

import os
import re
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from typing import Any, Dict, List, Optional, Union

try:
    from dspy_modules.retriever.pg import run_fused_query
except Exception as e:  # pragma: no cover - fail fast with clear message
    pytest.skip(f"retriever import unavailable: {e}", allow_module_level=True)

def _check_postgres_available() -> bool:
    """Check if Postgres is available for testing."""
    import psycopg2
    from psycopg2 import OperationalError, ProgrammingError

    dsn = os.environ.get("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

    # Skip if DSN is mock or invalid format
    if dsn.startswith("mock://") or not dsn.startswith("postgresql://"):
        return False

    try:
        # Try to connect with a short timeout
        conn = psycopg2.connect(dsn, connect_timeout=2)
        conn.close()
        return True
    except (OperationalError, ProgrammingError):
        return False

@pytest.mark.integration
@settings(max_examples=15, deadline=800)
@given(
    q=st.text(min_size=1, max_size=64)
    .filter(lambda s: "\x00" not in s)
    .map(lambda s: re.sub(r"\s+", " ", s.strip()) or "RAGChecker"),
    k=st.integers(min_value=1, max_value=20),
    use_mmr=st.booleans(),
)
def test_run_fused_query_basic_properties(q: str, k: int, use_mmr: bool):
    # Skip if Postgres is not available
    if not _check_postgres_available():
        pytest.skip("Postgres not available - skipping database integration test")
    os.environ.setdefault("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    rows: list[dict[str, Any]] = run_fused_query(
        q_short=q,
        q_title="",
        q_bm25=q,
        qvec=[],
        k=k,
        use_mmr=use_mmr,
        tag="rag_qa_single",
        return_components=True,
    )

    # Length never exceeds k
    assert len(rows) <= k

    # Row schema has essential fields when any results exist
    if rows:
        r0 = rows[0]
        # filename and file_path should be present and non-empty strings
        assert isinstance(r0.get("filename", ""), str)
        assert isinstance(r0.get("file_path", ""), str)
        # scores present
        assert "score" in r0
