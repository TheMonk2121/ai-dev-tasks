from __future__ import annotations

from collections.abc import Iterable


try:
    from pydantic_graph.graph import Graph
    from pydantic_graph.nodes import End, Node
except Exception:
    # Defer hard dependency: allow import in environments without pydantic-graph installed
    Graph = object  # type: ignore
    End = object  # type: ignore
    Node = object  # type: ignore

from src.schemas.eval import CaseResult, ContextChunk, RetrievalCandidate


class LoadCases(Node[list[dict]]):  # returns list of raw case dicts
    def run(self, gold_file: str) -> list[dict]:
        from src.utils.gold_loader import load_gold_cases

        cases = load_gold_cases(gold_file)
        # Convert GoldCase models to plain dicts for downstream simplicity
        return [c.model_dump() for c in cases]


class Retrieve(Node[list[RetrievalCandidate]]):
    def run(self, question: str) -> list[RetrievalCandidate]:
        # Use RAG pipeline module directly
        import os

        from dspy_modules.rag_pipeline import RAGPipeline

        db_connection = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        rp = RAGPipeline(db_connection)
        out = rp.answer(question)
        snapshot = getattr(rp.rag_module, "_last_retrieval_candidates_dto", [])
        return list(snapshot)


class Score(Node[CaseResult]):
    def run(
        self,
        case_id: str,
        mode: str,
        tags: list[str],
        query: str,
        candidates: list[RetrievalCandidate],
        used: list[ContextChunk] | None = None,
    ) -> CaseResult:
        # Minimal scoring using existing harness logic (Jaccard-based metrics)
        from scripts._ragchecker_eval_impl import CleanRAGCheckerEvaluator

        ev = CleanRAGCheckerEvaluator()
        # Build a faux case_result payload and reuse evaluator compute helpers
        retrieved_context = [c.chunk for c in candidates][:12]
        precision = ev._calculate_precision("", "", query)
        recall = ev._calculate_recall("", "")
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        return CaseResult(
            id=case_id,
            mode=mode,
            tags=tags,
            query=query,
            predicted_answer="",
            retrieved_context=retrieved_context,
            retrieval_snapshot=candidates,
            metrics={"precision": precision, "recall": recall, "f1": f1},
            timings={},
        )


def build_graph() -> Graph:
    g = Graph(nodes=[LoadCases(), Retrieve(), Score()])
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
