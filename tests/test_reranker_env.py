import os
from importlib import reload


def test_legacy_aliases(monkeypatch):
    from src.rag import reranker_env as env

    monkeypatch.setenv("RERANKER_ENABLED", "1")
    monkeypatch.setenv("RERANK_POOL", "40")
    monkeypatch.setenv("RERANK_TOPN", "10")
    reload(env)
    assert env.RERANK_ENABLE is True
    assert env.RERANK_INPUT_TOPK == 40
    assert env.RERANK_KEEP == 10
