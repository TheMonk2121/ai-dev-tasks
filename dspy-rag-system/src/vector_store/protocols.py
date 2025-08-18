#!/usr/bin/env python3
"""
Vector Store Protocols

Defines the unified interface for vector store implementations.
"""

from typing import Any, Dict, List, Protocol


class IVectorStore(Protocol):
    """Unified interface for vector store implementations."""

    def similarity_search(self, query_embedding: List[float], top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        ...

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store."""
        ...

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the vector store."""
        ...

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        ...
