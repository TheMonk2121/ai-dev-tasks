# DSPy RAG System
# This is the main DSPy RAG system for evaluation purposes

from .dspy_modules.dspy_reader_program import RAGAnswer, compile_and_save
from .dspy_modules.retriever.pg import fetch_doc_chunks_by_slug, run_fused_query
from .dspy_modules.retriever.rerank import mmr_rerank, per_file_cap
from .dspy_modules.reader.entrypoint import build_reader_context
from .dspy_modules.reader.span_picker import normalize_answer, pick_span

__all__ = [
    "RAGAnswer",
    "compile_and_save",
    "fetch_doc_chunks_by_slug",
    "run_fused_query",
    "mmr_rerank",
    "per_file_cap",
    "build_reader_context",
    "normalize_answer",
    "pick_span",
]
