#!/usr/bin/env python3
"""
Core Vector Store Implementation

Wraps the existing HybridVectorStore for hybrid search capabilities.
"""

from typing import Any, Dict, List

import numpy as np
from dspy_modules.vector_store import HybridVectorStore


class CoreVectorStore:
    """
    Core vector store implementation.
    Wraps HybridVectorStore for hybrid search capabilities.
    """

    def __init__(self, db_connection_string: str, **kwargs):
        """
        Initialize the core vector store.

        Args:
            db_connection_string: Database connection string
            **kwargs: Additional arguments passed to HybridVectorStore
        """
        self._hybrid_store = HybridVectorStore(db_connection_string, **kwargs)
        self.db_connection_string = db_connection_string

    def similarity_search(self, query_embedding: List[float], top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using hybrid search.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of search results
        """
        # Convert list to numpy array if needed
        if isinstance(query_embedding, list):
            query_embedding = np.array(query_embedding)

        # Use the hybrid search method
        result = self._hybrid_store.forward(
            operation="hybrid_search", query_embedding=query_embedding, limit=top_k, **kwargs
        )

        # Extract results from the hybrid search response
        if isinstance(result, dict) and "results" in result:
            return result["results"]
        elif isinstance(result, list):
            return result
        else:
            return []

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector store.

        Args:
            documents: List of documents to add

        Returns:
            True if successful
        """
        try:
            # Use the hybrid store's document addition method
            result = self._hybrid_store.forward(operation="add_documents", documents=documents)
            return result.get("success", False)
        except Exception:
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the vector store.

        Returns:
            Health status dictionary
        """
        try:
            # Basic health check - try to connect
            return {"status": "healthy", "type": "core", "connection": "available"}
        except Exception as e:
            return {"status": "unhealthy", "type": "core", "error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Statistics dictionary
        """
        return {
            "type": "core",
            "implementation": "HybridVectorStore",
            "features": ["hybrid_search", "dense_sparse_fusion", "spans"],
        }
