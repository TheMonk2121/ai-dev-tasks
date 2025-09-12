from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Literal
from typing import Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from pydantic_graph.graph import Graph  # type: ignore[import-untyped]
    from pydantic_graph.nodes import End, Node  # type: ignore[import-untyped]
else:
    Graph = object  # type: ignore[assignment]
    End = object  # type: ignore[assignment]
    class Node:  # type: ignore
        # Allow subscript syntax Node[T] when graph lib is not installed
        def __class_getitem__(cls, item):  # type: ignore[no-redef]
            return cls

from src.schemas.eval import CaseResult, ContextChunk, RetrievalCandidate


class LoadCases(Node[list[dict]]):  # returns list of raw case dicts
    def run(self, gold_file: str) -> list[dict]:
        from src.utils.gold_loader import load_gold_cases

        cases = load_gold_cases(gold_file)
        # Convert GoldCase models to plain dicts for downstream simplicity
        return [c.model_dump() for c in cases]


class Retrieve(Node[list[RetrievalCandidate]]):
    def run(self, question: str) -> list[RetrievalCandidate]:
        """Fetch retrieval candidates via RAG pipeline, with safe fallbacks.

        - If the RAG pipeline module is unavailable, returns an empty list.
        - If database connectivity or pipeline execution fails, returns an empty list.
        - Always fails-closed (never raises) to keep eval graph resilient.
        """
        try:
            import os

            try:
                # Local import to avoid hard dependency when not present
                from dspy_modules.rag_pipeline import RAGPipeline  # type: ignore[import-untyped]
            except Exception:
                return []

            db_connection = os.getenv("POSTGRES_DSN", "postgresql://localhost:5432/ai_agency")
            try:
                rp = RAGPipeline(db_connection)
                _ = rp.answer(question)
                snapshot = getattr(rp.rag_module, "_last_retrieval_candidates_dto", [])
                return list(snapshot)
            except Exception:
                # Any runtime failure (DB/connectivity/model) → degrade gracefully
                return []
        except Exception:
            return []


class Score(Node[CaseResult]):
    def run(
        self,
        case_id: str,
        mode: Literal["rag", "baseline", "oracle"],
        tags: list[str],
        query: str,
        candidates: list[RetrievalCandidate],
        used: list[ContextChunk] | None = None,
    ) -> CaseResult:
        # Minimal scoring using existing harness logic (Jaccard-based metrics)
        try:
            from scripts._ragchecker_eval_impl import CleanRAGCheckerEvaluator  # type: ignore[import-untyped]
        except Exception:
            CleanRAGCheckerEvaluator = None  # type: ignore[assignment]

        precision = recall = f1 = 0.0
        if CleanRAGCheckerEvaluator is not None:
            ev = CleanRAGCheckerEvaluator()
            precision = ev._calculate_precision("", "", query)
            recall = ev._calculate_recall("", "")
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Convert candidates to ContextChunk list for schema compatibility
        retrieved_context = [
            ContextChunk(source_id=c.doc_id, text=c.chunk) for c in candidates[:12]
        ]

        return CaseResult(
            case_id=case_id,
            mode=mode,
            query=query,
            predicted_answer="",
            retrieved_context=retrieved_context,
            retrieval_snapshot=candidates,
            precision=precision,
            recall=recall,
            f1=f1,
        )


def build_graph() -> Any:
    g = Graph(nodes=[LoadCases(), Retrieve(), Score()])  # type: ignore
    return g


def export_mermaid(path: str = "docs/graphs/eval_graph.mmd") -> None:
    try:
        g = build_graph()
        out = g.mermaid()
        from pathlib import Path

        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(out)
    except Exception:
        # pydantic-graph not available; skip
        pass
