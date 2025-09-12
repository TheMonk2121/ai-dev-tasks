#!/usr/bin/env python3
"""
Reader entrypoint for building context from retrieved documents.
"""

import os
from typing import Any

from .sentence_select import select_sentences


def build_reader_context(
    rows: list[dict[str, Any]], query: str, tag: str, compact: bool = True
) -> tuple[str, dict[str, Any]]:
    """
    Build reader context from retrieved documents.

    Args:
        rows: Retrieved document rows
        query: User query
        tag: Query tag
        compact: Whether to use compact context

    Returns:
        Tuple of (context_text, metadata)
    """
    if not rows:
        return "No relevant documents found.", {"total_docs": 0, "total_chars": 0}

    # Optional: token-budget packing powered by local counter
    enable_token_pack = bool(int(os.getenv("TOKEN_PACK_ENABLE", "0")))
    token_budget = int(os.getenv("TOKEN_PACK_BUDGET", "8192"))
    token_reserve = int(os.getenv("TOKEN_PACK_RESERVE", "1024"))
    token_family = os.getenv("TOKEN_PACK_FAMILY", "hf_fast")
    token_model = os.getenv("TOKEN_PACK_MODEL", "bert-base-uncased")
    llama_model_path = os.getenv("TOKEN_PACK_LLAMA_PATH")

    counter = None
    if enable_token_pack:
        try:
            from src.llm.token_count import make_counter

            counter = make_counter(token_family, token_model, model_path=llama_model_path)
        except Exception:
            counter = None

    # Use sentence selection for better precision
    if compact:
        try:
            from ..retriever.query_rewrite import PHRASE_HINTS

            phrase_hints = PHRASE_HINTS.get(tag, [])
            compact_sentences, chosen = select_sentences(rows, query, tag, phrase_hints, per_chunk=2, total=10)
            context_text = compact_sentences
            total_chars = len(context_text)
            # Token pack: trim context to budget if enabled
            if enable_token_pack and counter is not None:
                # Very lightweight greedy trim by paragraphs
                parts = context_text.split("\n\n")
                core_tokens = 0  # caller should account for core msg; unknown here
                budget_for_ctx = max(0, token_budget - token_reserve - core_tokens)
                acc = []
                used = 0
                for p in parts:
                    c = counter.count(p)
                    if used + c > budget_for_ctx:
                        break
                    acc.append(p)
                    used += c
                context_text = "\n\n".join(acc)
        except Exception:
            # Fallback to simple concatenation
            context_parts = []
            total_chars = 0
            for i, row in enumerate(rows[:10]):
                content = (
                    row.get("text_for_reader", "")
                    or row.get("embedding_text", "")
                    or row.get("bm25_text", "")
                    or row.get("content", "")
                )
                if content:
                    filename = row.get("filename", f"doc_{i}")
                    context_parts.append(f"=== {filename} ===")
                    context_parts.append(content)
                    total_chars += len(content)
            context_text = "\n\n".join(context_parts)
            if enable_token_pack and counter is not None:
                parts = context_text.split("\n\n")
                core_tokens = 0
                budget_for_ctx = max(0, token_budget - token_reserve - core_tokens)
                acc = []
                used = 0
                for p in parts:
                    c = counter.count(p)
                    if used + c > budget_for_ctx:
                        break
                    acc.append(p)
                    used += c
                context_text = "\n\n".join(acc)
            if len(context_text) > 4000:
                context_text = context_text[:4000] + "..."
    else:
        # Simple context building - concatenate document content
        context_parts = []
        total_chars = 0
        for i, row in enumerate(rows[:10]):  # Limit to top 10 documents
            content = (
                row.get("text_for_reader", "")
                or row.get("embedding_text", "")
                or row.get("bm25_text", "")
                or row.get("content", "")
            )
            if content:
                # Add document header
                filename = row.get("filename", f"doc_{i}")
                context_parts.append(f"=== {filename} ===")
                context_parts.append(content)
                total_chars += len(content)
        context_text = "\n\n".join(context_parts)

    metadata = {"total_docs": len(rows), "total_chars": total_chars, "compact": compact, "query": query, "tag": tag}

    return context_text, metadata
