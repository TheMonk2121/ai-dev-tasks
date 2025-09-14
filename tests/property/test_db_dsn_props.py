from __future__ import annotations

import os

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.common.db_dsn import CANON_ENV, FALLBACK_ENV, resolve_dsn

#!/usr/bin/env python3
"""
Property tests for DB DSN resolver.
"""





def _safe_dsn() -> str:
    return "postgresql://user@localhost:5432/db"


@pytest.mark.prop
@given(st.just(_safe_dsn()), st.just(_safe_dsn()))
@settings(max_examples=3, deadline=100)
def test_resolve_dsn_picks_primary(primary: str, fallback: str):
    os.environ[CANON_ENV] = primary
    os.environ[FALLBACK_ENV] = fallback
    chosen = resolve_dsn(strict=False, emit_warning=False)
    assert chosen == primary
    os.environ.pop(CANON_ENV, None)
    os.environ.pop(FALLBACK_ENV, None)


@pytest.mark.prop
def test_resolve_dsn_none_when_unset():
    os.environ.pop(CANON_ENV, None)
    os.environ.pop(FALLBACK_ENV, None)
    chosen = resolve_dsn(strict=False, emit_warning=False)
    assert chosen is None