"""Unit tests for the Bedrock evaluation wrapper."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import scripts.evaluation.run_eval as run_eval


@pytest.fixture()
def tmp_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    return tmp_path


def test_latest_eval_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    first.write_text("{}"); second.write_text("{}")
    monkeypatch.setattr(run_eval, "glob", lambda pattern: [str(first), str(second)])
    monkeypatch.setattr(run_eval.os.path, "getctime", lambda path: 10 if path == str(second) else 5)

    assert run_eval._latest_eval_file("*.json") == str(second)


def test_main_success(tmp_output: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    proc = MagicMock(returncode=0, stdout="done", stderr="")
    monkeypatch.setattr(run_eval.subprocess, "run", lambda *_, **__: proc)

    latest_file = tmp_output / "ragchecker_official_evaluation_test.json"
    latest_file.write_text("{}")
    monkeypatch.setattr(
        run_eval,
        "_latest_eval_file",
        lambda pattern: str(latest_file),
    )

    fixed_ts = "20240101_010203"
    monkeypatch.setattr(
        run_eval.datetime,
        "now",
        lambda: run_eval.datetime.strptime(fixed_ts, "%Y%m%d_%H%M%S"),
    )

    args = [
        "run_eval.py",
        "--output-root",
        str(tmp_output),
        "--tag",
        "TEST",
    ]
    monkeypatch.setattr(run_eval, "sys", type("S", (), {"argv": args}))

    exit_code = run_eval.main()
    assert exit_code == 0
    manifest_path = tmp_output / "TEST" / fixed_ts / "manifest.json"
    data = json.loads(manifest_path.read_text())
    assert data["env"]["EVAL_MODE"] == "bedrock_only"
    assert data["env"]["CACHE_DISABLED"] == "1"
    assert data["env"]["AWS_REGION"] == "us-east-1"


def test_main_subprocess_failure(tmp_output: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    proc = MagicMock(returncode=1, stdout="", stderr="boom")
    monkeypatch.setattr(run_eval.subprocess, "run", lambda *_, **__: proc)
    monkeypatch.setattr(run_eval, "_latest_eval_file", lambda pattern: None)

    args = ["run_eval.py", "--output-root", str(tmp_output)]
    monkeypatch.setattr(run_eval, "sys", type("S", (), {"argv": args}))

    assert run_eval.main() == 1
