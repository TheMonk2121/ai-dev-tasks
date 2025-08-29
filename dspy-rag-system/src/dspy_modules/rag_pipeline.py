#!/usr/bin/env python3
"""
RAG Pipeline Module - Enforces context consumption and provides citations
"""

from typing import Any, Dict, List

import dspy

from .hit_adapter import _rescale, adapt_rows, pack_hits
from .vector_store import HybridVectorStore


class QAWithContext(dspy.Signature):
    """Answer strictly from provided context. If missing, say 'Not in context.' Cite filenames."""

    question: str = dspy.InputField()
    context: str = dspy.InputField()
    answer: str = dspy.OutputField()
    citations: List[str] = dspy.OutputField()


class RAGModule(dspy.Module):
    """DSPy RAG module that enforces context consumption and provides citations."""

    def __init__(self, retriever: HybridVectorStore, k: int = 6, reranker=None):
        super().__init__()
        self.retriever = retriever
        self.reranker = reranker
        self.k = k
        self.generate = dspy.Predict(QAWithContext)

    def forward(self, question: str) -> Dict[str, Any]:
        """Forward pass with retrieval, optional reranking, and context-aware generation."""

        # 1) Retrieve
        result = self.retriever.forward("search", query=question, limit=max(2 * self.k, 12))

        if result["status"] != "success":
            return {
                "answer": "Error: Retrieval failed",
                "citations": [],
                "context_used": False,
                "retrieval_error": result.get("error", "Unknown error"),
            }

        # 2) Adapt rows to guaranteed Hits
        rows = result["results"]
        hits = adapt_rows(rows)

        # 3) Optional rescale to balance vector vs BM25 scores
        hits = _rescale(hits)

        # 4) Optional rerank
        if self.reranker and hits:
            # TODO: Implement reranker integration
            hits = hits[: self.k]
        else:
            hits = hits[: self.k]

        # 5) Guardrails: require at least 1 valid hit with text
        if not hits:
            return {"answer": "Not in context.", "citations": [], "context_used": False, "retrieval_count": 0}

        # 6) Pack context using guaranteed packer
        context = pack_hits(hits)

        # Check if context is too small
        if len(context.split()) < 50:  # Less than 50 words
            return {
                "answer": "Not in context.",
                "citations": [],
                "context_used": False,
                "context_size": len(context.split()),
            }

        # Check if context is too small
        if len(context.split()) < 50:  # Less than 50 words
            return {
                "answer": "Not in context.",
                "citations": [],
                "context_used": False,
                "context_size": len(context.split()),
            }

        # 7) Generate with context
        try:
            out = self.generate(question=question, context=context)

            # Handle DSPy output properly
            answer = getattr(out, "answer", str(out)) if hasattr(out, "answer") else str(out)

            # Extract citations from hits
            citations = [h.metadata.get("filename") or f"doc:{h.metadata.get('document_id')}" for h in hits[:3]]

            return {
                "answer": answer,
                "citations": citations,  # Top 3 citations
                "context_used": True,
                "retrieval_count": len(hits),
                "context_size": len(context.split()),
                "context_preview": context[:200] + "..." if len(context) > 200 else context,
            }

        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "citations": [h.metadata.get("filename") or f"doc:{h.metadata.get('document_id')}" for h in hits[:3]],
                "context_used": True,
                "generation_error": str(e),
            }


class RAGPipeline:
    """High-level RAG pipeline with teleprompter optimization."""

    def __init__(self, db_connection_string: str):
        self.retriever = HybridVectorStore(db_connection_string)
        self.rag_module = RAGModule(self.retriever, k=6)

        # TODO: Add teleprompter with grounding metric
        # self.teleprompter = self._create_teleprompter()
        # self.optimized_rag = self.teleprompter.compile(self.rag_module)

    def _create_teleprompter(self):
        """Create teleprompter with grounding metric."""
        from dspy.teleprompt import BootstrapFewShot

        def grounding_metric(pred, gold):
            """Metric that rewards grounding in context and citations."""
            has_cite = any(c in (pred.get("citations", []) or []) for c in gold.get("citations", []))
            mentions_key = all(k.lower() in pred.get("answer", "").lower() for k in gold.get("must", []))
            context_used = pred.get("context_used", False)

            return 0.4 * has_cite + 0.3 * mentions_key + 0.3 * context_used

        return BootstrapFewShot(metric=grounding_metric, max_bootstrapped_demos=6)

    def answer(self, question: str) -> Dict[str, Any]:
        """Answer a question using the RAG pipeline."""
        return self.rag_module.forward(question)

    def debug_retrieval(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Debug retrieval without generation."""
        result = self.retriever.forward("search", query=question, limit=k)

        if result["status"] == "success":
            hits = result["results"]
            return {
                "status": "success",
                "hits": [
                    {
                        "score": hit.get("score"),
                        "title": hit.get("file_path"),
                        "content": hit.get("content", "")[:200] + "...",
                        "has_context_index": "CONTEXT_INDEX" in hit.get("content", ""),
                    }
                    for hit in hits
                ],
            }
        else:
            return {"status": "error", "error": result.get("error", "Unknown error")}
