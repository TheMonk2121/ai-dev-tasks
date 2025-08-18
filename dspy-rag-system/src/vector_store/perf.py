#!/usr/bin/env python3
"""
Performance Vector Store Implementation

Adapter exposing dashboard-compatible methods while delegating to
EnhancedVectorStore.
"""

from __future__ import annotations

from typing import Any, Dict, List

from dspy_modules.enhanced_vector_store import EnhancedVectorStore


class PerfVectorStore:
    """
    Performance vector store implementation.
    Wraps EnhancedVectorStore for performance monitoring and caching.
    """

    def __init__(self, db_connection_string: str, dimension: int = 384, **kwargs):
        """
        Initialize the performance vector store.

        Args:
            db_connection_string: Database connection string
            dimension: Vector dimension
            **kwargs: Additional arguments passed to EnhancedVectorStore
        """
        self._enhanced_store = EnhancedVectorStore(
            db_connection_string, dimension, **kwargs
        )
        self.db_connection_string = db_connection_string
        self.dimension = dimension

    def similarity_search(
        self, query_embedding: List[float], top_k: int = 5, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors with performance monitoring.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of search results
        """
        return self._enhanced_store.similarity_search(
            query_embedding=query_embedding, top_k=top_k, **kwargs
        )

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector store.

        Args:
            documents: List of documents to add

        Returns:
            True if successful
        """
        return self._enhanced_store.add_documents(documents)

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the vector store.

        Returns:
            Health status dictionary
        """
        return self._enhanced_store.get_health_status()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Statistics dictionary
        """
        return {
            "type": "perf",
            "implementation": "EnhancedVectorStore",
            "features": [
                "performance_monitoring",
                "caching",
                "health_checks",
                "index_management",
            ],
            "metrics": (
                self._enhanced_store.get_performance_metrics()
                if hasattr(self._enhanced_store, "get_performance_metrics")
                else {}
            ),
        }

    # Dashboard-compatible alias
    def get_statistics(self) -> Dict[str, Any]:
        return self.get_stats()

    # Minimal parity methods (delegation)
    def store_document(self, *args: Any, **kwargs: Any) -> Any:
        # Try common names first; fallback to forward if provided
        if hasattr(self._enhanced_store, "store_document"):
            return self._enhanced_store.store_document(*args, **kwargs)
        if hasattr(self._enhanced_store, "add_document"):
            return self._enhanced_store.add_document(*args, **kwargs)
        if hasattr(self._enhanced_store, "forward"):
            return self._enhanced_store.forward(
                operation="store_document", *args, **kwargs
            )
        raise AttributeError("PerfVectorStore inner has no document store method")

    def store_chunk(self, *args: Any, **kwargs: Any) -> Any:
        if hasattr(self._enhanced_store, "store_chunk"):
            return self._enhanced_store.store_chunk(*args, **kwargs)
        if hasattr(self._enhanced_store, "add_chunk"):
            return self._enhanced_store.add_chunk(*args, **kwargs)
        if hasattr(self._enhanced_store, "forward"):
            return self._enhanced_store.forward(
                operation="store_chunk", *args, **kwargs
            )
        raise AttributeError("PerfVectorStore inner has no chunk store method")

    def get_documents(self, *args: Any, **kwargs: Any) -> Any:
        if hasattr(self._enhanced_store, "get_documents"):
            return self._enhanced_store.get_documents(*args, **kwargs)
        if hasattr(self._enhanced_store, "list_documents"):
            return self._enhanced_store.list_documents(*args, **kwargs)
        if hasattr(self._enhanced_store, "forward"):
            return self._enhanced_store.forward(
                operation="get_documents", *args, **kwargs
            )
        raise AttributeError("PerfVectorStore inner has no get/list documents method")

    # Expose additional enhanced features
    def get_performance_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance metrics."""
        if hasattr(self._enhanced_store, "get_performance_metrics"):
            return self._enhanced_store.get_performance_metrics(hours)
        return []

    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize performance."""
        if hasattr(self._enhanced_store, "optimize_performance"):
            return self._enhanced_store.optimize_performance()
        return {"status": "optimization_not_available"}
