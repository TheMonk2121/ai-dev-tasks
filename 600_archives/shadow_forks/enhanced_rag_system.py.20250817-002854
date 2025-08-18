#!/usr/bin/env python3

"""Enhanced RAG System Delegator"""

from typing import Any, Dict

from utils.rag_compatibility_shim import create_enhanced_rag_interface


def _load_fast_path_config() -> Dict[str, Any]:
    """Load fast-path configuration."""
    return {"enabled": True, "max_length": 50, "exclude_tokens": ["code", "def", "class", "import"]}


def _should_use_fast_path(query: str, config: Dict[str, Any]) -> bool:
    """Determine if a query should use fast-path processing."""
    if not config.get("enabled", True):
        return False

    # Check query length
    if len(query) > config.get("max_length", 50):
        return False

    # Check for exclude tokens (case-insensitive)
    query_lower = query.lower()
    exclude_tokens = config.get("exclude_tokens", [])

    for token in exclude_tokens:
        if token.lower() in query_lower:
            return False

    return True


class EnhancedRAGSystem:
    """Enhanced RAG System for testing."""

    def __init__(self):
        self.rag_interface = create_enhanced_rag_interface()

    def query(self, query: str):
        """Query the RAG system."""
        return self.rag_interface.ask(query)
