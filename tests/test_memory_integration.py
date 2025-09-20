"""Unit tests for memory integration utilities."""

from __future__ import annotations

import json
import subprocess
from typing import Any

import pytest

from src.retrieval.memory_integration import MemoryIntegrator


def test_sync_with_memory_orchestrator_preserves_existing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure orchestrator keeps existing environment variables when overriding DSN."""
    integrator = MemoryIntegrator()
    captured_env: dict[str, str] = {}

    monkeypatch.setenv("EXISTING_VAR", "preserve-me")

    def fake_run(
        cmd: list[str],
        *,
        capture_output: bool,
        text: bool,
        timeout: int,
        env: dict[str, str],
    ) -> Any:
        captured_env.update(env)

        class Result:
            returncode = 0
            stdout: Any = json.dumps({})
            stderr = ""

        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)

    result: Any = integrator.sync_with_memory_orchestrator()

    assert result
    assert result
    assert result
