#!/usr/bin/env python3

from src.dspy_modules.rag_pipeline import RAGModule


class _ErrorRetriever:
    def forward(self, operation: str, **kwargs):
        return {"status": "error", "error": "simulated retrieval failure", "results": []}


def test_ragmodule_eval_fallback_on_error():
    rag = RAGModule(retriever=_ErrorRetriever(), k=3)

    # Phrase variants should trigger the eval fallback
    for q in [
        "run the evals",
        "how do I run evaluation",
        "ragchecker official evaluation",
        "smoke test for evals",
    ]:
        out = rag.forward(q)
        assert isinstance(out, dict)
        # Expect fallback marker and commands content
        assert out.get("fallback") == "eval_discovery"
        ans = out.get("answer", "")
        assert "ragchecker_official_evaluation.py" in ans or "run_evals.sh" in ans

