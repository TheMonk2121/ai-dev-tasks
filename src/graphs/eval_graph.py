from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from pydantic_graph.graph import Graph  # type: ignore
    from pydantic_graph.nodes import (
        Node,  # type: ignore[import-untyped,import-not-found,reportUnknownImportSymbol,reportAttributeAccessIssue,reportGeneralTypeIssues,reportUnknownSymbol,reportUnknownImportSymbol]
    )
else:
    # Runtime fallbacks for when pydantic_graph is not available
    class Graph:  # type: ignore
        def __init__(self, nodes: list[Node]) -> None:  # type: ignore
            self.nodes = nodes
        
        def mermaid(self) -> str:
            return "# Graph not available"
    
    class Node:  # type: ignore
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass
        
        def run(self, *_args: Any, **_kwargs: Any) -> Any:
            raise NotImplementedError("Node.run must be implemented by subclasses")

from src.schemas.eval import CaseResult, ContextChunk, RetrievalCandidate


class LoadCases(Node):  # type: ignore  # returns list of raw case dicts
    def run(self, gold_file: str) -> list[dict[str, Any]]:
        from src.utils.gold_loader import load_gold_cases

        cases = load_gold_cases(gold_file)
        # Convert GoldCase models to plain dicts for downstream simplicity
        return [c.model_dump() for c in cases]

class Retrieve(Node):  # type: ignore
    def run(self, question: str) -> list[RetrievalCandidate]:
        # Use RAG pipeline module directly
        import os
        
        from dspy_modules.rag_pipeline import RAGPipeline

        db_connection = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        rp = RAGPipeline(db_connection)
        _ = rp.answer(question)
        snapshot = getattr(rp.rag_module, "_last_retrieval_candidates_dto", [])
        return list(snapshot)

class Score(Node):  # type: ignore
    def run(
        self,
        case_id: str,
        mode: Literal["rag", "baseline", "oracle"],
        _tags: list[str],
        query: str,
        candidates: list[RetrievalCandidate],
        _used: list[ContextChunk] | None = None,
    ) -> CaseResult:
        # Minimal scoring using existing harness logic (Jaccard-based metrics)
        precision = recall = f1 = 0.0
        try:
            from src.evaluation.ragchecker_evaluator import CleanRAGCheckerEvaluator
            ev = CleanRAGCheckerEvaluator()
            precision = ev._calculate_precision("", "", query)
            recall = ev._calculate_recall("", "")
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        except Exception:
            # Fallback to default values if evaluator is not available
            pass

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
        _ = p.parent.mkdir(parents=True, exist_ok=True)
        _ = p.write_text(out)
    except Exception:
        # pydantic-graph not available; skip
        pass
