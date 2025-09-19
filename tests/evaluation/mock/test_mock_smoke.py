from __future__ import annotations

from scripts.evaluation.ragchecker_official_evaluation import main as orchestrator_main


def test_mock_profile_smoke() -> None:
    assert orchestrator_main(["--profile", "mock"]) == 0


def test_unknown_profile_fails() -> None:
    assert orchestrator_main(["--profile", "unknown"]) == 2
