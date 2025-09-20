"""Unit tests for the eval graph runner."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import scripts.evaluation.run_eval_graph as run_eval_graph


@pytest.fixture()
def graph_mocks(monkeypatch: pytest.MonkeyPatch) -> tuple[MagicMock, MagicMock, MagicMock]:
    persistence = MagicMock()
    graph = MagicMock()
    load_node = MagicMock()
    retrieve_node = MagicMock()
    score_node = MagicMock()
    graph.nodes = [load_node, retrieve_node, score_node]
    monkeypatch.setattr(run_eval_graph, "PgStatePersistence", lambda run_id: persistence)
    monkeypatch.setattr(run_eval_graph, "build_graph", lambda: graph)
    return persistence, load_node, retrieve_node, score_node


def test_main_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, graph_mocks) -> None:
    persistence, load_node, retrieve_node, score_node = graph_mocks

    load_node.run.return_value = [
        {"id": "case1", "query": "q", "mode": "m", "tags": ["t"]},
    ]
    retrieve_node.run.return_value = ["cand"]
    score_result = MagicMock()
    score_result.model_dump_json.return_value = json.dumps({"score": 1})
    score_node.run.return_value = score_result

    args = [
        "run_eval_graph.py",
        "--run-id",
        "r1",
        "--gold-file",
        "gold.jsonl",
        "--out",
        str(tmp_path),
    ]
    monkeypatch.setattr(run_eval_graph, "sys", type("S", (), {"argv": args}))
    monkeypatch.setattr(run_eval_graph.time, "time", lambda: 1234)

    run_eval_graph.main()

    load_node.run.assert_called_once_with("gold.jsonl")
    retrieve_node.run.assert_called_once_with("q")
    score_node.run.assert_called_once()
    log_path = tmp_path / "r1.json"
    assert log_path.exists()


def test_main_no_cases(monkeypatch: pytest.MonkeyPatch, graph_mocks) -> None:
    _, load_node, *_ = graph_mocks
    load_node.run.return_value = []

    monkeypatch.setattr(run_eval_graph, "sys", type("S", (), {"argv": ["run_eval_graph.py"]}))
    with pytest.raises(SystemExit) as excinfo:
        run_eval_graph.main()
    assert str(excinfo.value) == "No cases loaded"


def test_main_persistence_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run_eval_graph, "PgStatePersistence", lambda _: (_ for _ in ()).throw(Exception("boom")))
    monkeypatch.setattr(run_eval_graph, "build_graph", MagicMock())
    monkeypatch.setattr(run_eval_graph, "sys", type("S", (), {"argv": ["run_eval_graph.py"]}))

    with pytest.raises(SystemExit):
        run_eval_graph.main()
