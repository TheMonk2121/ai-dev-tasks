import json
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from src.common.db_dsn import resolve_dsn


def test_mismatch_raises(monkeypatch: MonkeyPatch):
    """Test that mismatched DSNs raise an error when strict mode is on."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://u@prod:5432/app")
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://u@dev:5432/app")
    with pytest.raises(RuntimeError, match="DSN mismatch"):
        _ = resolve_dsn(strict=True)


def test_fallback_and_tagging(monkeypatch: MonkeyPatch):
    """Test fallback DSN and connection tagging."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://u@localhost:5432/app?sslmode=disable")

    dsn = resolve_dsn(role="evaluation", app="ai-dev-tasks")

    assert "application_name=ai-dev-tasks%3Aevaluation" in dsn
    assert "sslmode=" in dsn
    assert "target_session_attrs=" in dsn


def test_remote_dsn_safety(monkeypatch: MonkeyPatch):
    """Test remote DSN safety check."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://u@remote.example.com:5432/app")

    with pytest.raises(RuntimeError, match="Remote DSN detected"):
        _ = resolve_dsn(strict=True)

    monkeypatch.setenv("ALLOW_REMOTE_DSN", "1")
    dsn = resolve_dsn(strict=True)  # Should not raise
    assert dsn is not None


def test_no_dsn_raises(monkeypatch: MonkeyPatch):
    """Test that no DSN raises an error."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_DSN", raising=False)

    with pytest.raises(RuntimeError, match="No DATABASE_URL or POSTGRES_DSN set"):
        _ = resolve_dsn(strict=True)


def test_audit_trail_generation(monkeypatch: MonkeyPatch, tmp_path: Path):
    """Test that an audit trail is generated."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://u@localhost:5432/app")
    monkeypatch.chdir(tmp_path)

    _ = resolve_dsn(role="test", app="test-app")  # Explicitly discard return value

    audit_file = tmp_path / "metrics" / "dsn_audit.jsonl"
    assert audit_file.exists()

    with open(audit_file) as f:
        audit_line = f.readline().strip()

    assert audit_line  # Line should not be empty

    audit_data = json.loads(audit_line)

    assert audit_data["role"] == "test"
    assert audit_data["src"] == "DATABASE_URL"
    assert "dsn_redacted" in audit_data
    assert "host" in audit_data
    assert "db" in audit_data
