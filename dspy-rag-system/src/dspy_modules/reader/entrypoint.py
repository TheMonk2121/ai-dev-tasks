#!/usr/bin/env python3
"""
Reader entrypoint for building context from retrieved documents.
"""

from typing import Any, Dict, List, Tuple


def build_reader_context(
    rows: List[Dict[str, Any]], 
    query: str, 
    tag: str, 
    compact: bool = True
) -> Tuple[str, Dict[str, Any]]:
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
    
    # Simple context building - concatenate document content
    context_parts = []
    total_chars = 0
    
    for i, row in enumerate(rows[:10]):  # Limit to top 10 documents
        content = row.get("embedding_text", "") or row.get("content", "")
        if content:
            # Add document header
            filename = row.get("filename", f"doc_{i}")
            context_parts.append(f"=== {filename} ===")
            context_parts.append(content)
            total_chars += len(content)
    
    context_text = "\n\n".join(context_parts)
    
    # Truncate if too long (compact mode)
    if compact and len(context_text) > 4000:
        context_text = context_text[:4000] + "..."
    
    metadata = {
        "total_docs": len(rows),
        "total_chars": total_chars,
        "compact": compact,
        "query": query,
        "tag": tag
    }
    
    return context_text, metadata
