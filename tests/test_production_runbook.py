"""Unit tests for the production runbook."""

# pyright: reportPrivateUsage=false, reportUntypedFunctionDecorator=false
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest  # type: ignore[import-untyped]

from scripts.evaluation.core.production_runbook import (  # type: ignore[import-untyped]
    PHASE_ORDER,
    DeploymentResultFailure,
    ProductionRunbook,
)


@pytest.fixture()  # type: ignore[misc]
def runbook() -> ProductionRunbook:
    return ProductionRunbook()


def _success() -> dict[str, Any]:
    return {"status": "success", "returncode": 0, "output": "ok", "error": ""}


def _failure(message: str) -> dict[str, Any]:
    return {"status": "failed", "returncode": 1, "output": "", "error": message}


def test_execute_deployment_happy_path(monkeypatch: Any, runbook: ProductionRunbook) -> None:
    for phase in PHASE_ORDER:
        monkeypatch.setattr(runbook, f"_{phase}", lambda _phase=phase: _success())

    result = runbook.execute_production_deployment()

    assert result["status"] == "success"
    assert result["run_id"].startswith("prod_run_")


def test_execute_deployment_first_phase_failure(
    monkeypatch: Any, runbook: ProductionRunbook
) -> None:
    monkeypatch.setattr(runbook, "_run_health_gated_evaluation", lambda: _failure("boom"))
    for phase in PHASE_ORDER[1:]:
        monkeypatch.setattr(runbook, f"_{phase}", lambda _phase=phase: _success())

    result = runbook.execute_production_deployment()

    assert result["status"] == "failed"
    # Type narrowing: if status is "failed", then result is DeploymentResultFailure
    failure_result: DeploymentResultFailure = result  # type: ignore[assignment]
    assert failure_result["failed_phases"] == ["health_gated_evaluation"]
    assert failure_result["error"] == "boom"


def test_run_cmd_success(monkeypatch: Any, runbook: ProductionRunbook) -> None:  # type: ignore[reportPrivateUsage]
    proc = MagicMock(returncode=0, stdout="ok", stderr="")
    monkeypatch.setattr("scripts.evaluation.core.production_runbook.subprocess.run", lambda *_, **__: proc)

    result = runbook._run_cmd(["echo", "hi"])  # type: ignore[protected-access,reportPrivateUsage]

    assert result == {
        "status": "success",
        "returncode": 0,
        "output": "ok",
        "error": "",
    }


def test_run_cmd_failure(monkeypatch: Any, runbook: ProductionRunbook) -> None:  # type: ignore[reportPrivateUsage]
    proc = MagicMock(returncode=1, stdout="oops", stderr="bad")
    monkeypatch.setattr("scripts.evaluation.core.production_runbook.subprocess.run", lambda *_, **__: proc)

    result = runbook._run_cmd(["false"])  # type: ignore[protected-access,reportPrivateUsage]

    assert result["status"] == "failed"
    assert result["returncode"] == 1
    assert result["output"] == "oops"
    assert result["error"] == "bad"
