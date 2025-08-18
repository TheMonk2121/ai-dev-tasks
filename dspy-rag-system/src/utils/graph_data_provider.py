#!/usr/bin/env python3.12.123.11
"""
Graph Data Provider Module
--------------------------
Provides chunk relationship data for visualization with UMAP clustering,
caching, and feature flag protection.

This module implements the V1 API contract for chunk relationship visualization
with performance optimization and security controls.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import umap
from psycopg2.extras import RealDictCursor

from .database_resilience import DatabaseResilienceManager
from .logger import get_logger
from .retry_wrapper import retry

logger = get_logger("graph_data_provider")


@dataclass
class GraphNode:
    """Represents a node in the graph visualization."""

    id: str
    label: str
    anchor: str | None = None
    coords: tuple[float, float] = field(default=(0.0, 0.0))
    category: str | None = None


@dataclass
class GraphEdge:
    """Represents an edge in the graph visualization."""

    source: str
    target: str
    type: str  # "knn" or "entity"
    weight: float


@dataclass
class GraphData:
    """Complete graph data structure for V1 API contract."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
    elapsed_ms: float
    v: int = 1
    truncated: bool = False


class GraphDataProvider:
    """
    Provides chunk relationship data for visualization with UMAP clustering.

    Features:
    - UMAP-based 2D coordinate computation
    - Corpus snapshot-based caching
    - Feature flag protection
    - Performance optimization
    - Security controls (no embedding exposure)
    """

    def __init__(
        self,
        db_manager: DatabaseResilienceManager,
        max_nodes: int = 2000,
        cache_enabled: bool = True,
        feature_flag_enabled: bool = True,
    ):
        """
        Initialize GraphDataProvider.

        Args:
            db_manager: Database resilience manager
            max_nodes: Maximum number of nodes to return
            cache_enabled: Whether to enable UMAP caching
            feature_flag_enabled: Whether feature is enabled
        """
        self.db_manager = db_manager
        self.max_nodes = max_nodes
        self.cache_enabled = cache_enabled
        self.feature_flag_enabled = feature_flag_enabled

        # UMAP cache
        self._umap_cache: dict[str, tuple[Any, float]] = {}
        self._cache_lock = None
        if cache_enabled:
            import threading

            self._cache_lock = threading.Lock()

    def get_graph_data(
        self,
        query: str | None = None,
        include_knn: bool = True,
        include_entity: bool = True,
        min_sim: float = 0.5,
        max_nodes: int | None = None,
    ) -> GraphData:
        """
        Get graph data for visualization.

        Args:
            query: Optional search query to filter chunks
            include_knn: Whether to include KNN relationships
            include_entity: Whether to include entity relationships
            min_sim: Minimum similarity threshold
            max_nodes: Override max nodes limit

        Returns:
            GraphData with nodes, edges, and metadata

        Raises:
            ValueError: If feature flag is disabled
            Exception: If database or computation errors occur
        """
        start_time = time.time()

        # Check feature flag
        if not self.feature_flag_enabled:
            raise ValueError("Graph visualization feature is disabled")

        # Use provided max_nodes or default
        node_limit = max_nodes or self.max_nodes

        try:
            # Get chunk data
            chunks = self._get_chunks(query, node_limit)

            if not chunks:
                return GraphData(
                    nodes=[],
                    edges=[],
                    elapsed_ms=(time.time() - start_time) * 1000,
                    truncated=False,
                )

            # Compute UMAP coordinates
            coords = self._get_umap_coordinates(chunks)

            # Create nodes
            nodes = self._create_nodes(chunks, coords)

            # Create edges
            edges = []
            if include_knn:
                edges.extend(self._create_knn_edges(chunks, min_sim))
            if include_entity:
                edges.extend(self._create_entity_edges(chunks, min_sim))

            # Check if truncated
            truncated = len(chunks) >= node_limit

            elapsed_ms = (time.time() - start_time) * 1000

            return GraphData(
                nodes=nodes,
                edges=edges,
                elapsed_ms=elapsed_ms,
                truncated=truncated,
            )

        except Exception as e:
            logger.error(f"Error getting graph data: {e}")
            raise

    def get_cluster_data(
        self,
        query: str | None = None,
        max_nodes: int | None = None,
    ) -> GraphData:
        """
        Get cluster data (nodes only) for 2D visualization.

        Args:
            query: Optional search query to filter chunks
            max_nodes: Override max nodes limit

        Returns:
            GraphData with nodes only (no edges)
        """
        start_time = time.time()

        # Check feature flag
        if not self.feature_flag_enabled:
            raise ValueError("Graph visualization feature is disabled")

        # Use provided max_nodes or default
        node_limit = max_nodes or self.max_nodes

        try:
            # Get chunk data
            chunks = self._get_chunks(query, node_limit)

            if not chunks:
                return GraphData(
                    nodes=[],
                    edges=[],
                    elapsed_ms=(time.time() - start_time) * 1000,
                    truncated=False,
                )

            # Compute UMAP coordinates
            coords = self._get_umap_coordinates(chunks)

            # Create nodes only
            nodes = self._create_nodes(chunks, coords)

            # Check if truncated
            truncated = len(chunks) >= node_limit

            elapsed_ms = (time.time() - start_time) * 1000

            return GraphData(
                nodes=nodes,
                edges=[],
                elapsed_ms=elapsed_ms,
                truncated=truncated,
            )

        except Exception as e:
            logger.error(f"Error getting cluster data: {e}")
            raise

    @retry(max_retries=3, backoff_factor=2.0)
    def _get_chunks(
        self,
        query: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Get chunks from database with optional filtering.

        Args:
            query: Optional search query
            limit: Maximum number of chunks to return

        Returns:
            List of chunk dictionaries
        """
        with self.db_manager.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if query:
                    # Search with query
                    sql = """
                        SELECT
                            id,
                            content,
                            file_path,
                            line_start,
                            line_end,
                            is_anchor,
                            anchor_key,
                            metadata
                        FROM document_chunks
                        WHERE content_tsv @@ plainto_tsquery('english', %s)
                        ORDER BY ts_rank(content_tsv, plainto_tsquery('english', %s)) DESC
                        LIMIT %s
                    """
                    cursor.execute(sql, (query, query, limit))
                else:
                    # Get all chunks
                    sql = """
                        SELECT
                            id,
                            content,
                            file_path,
                            line_start,
                            line_end,
                            is_anchor,
                            anchor_key,
                            metadata
                        FROM document_chunks
                        ORDER BY id
                        LIMIT %s
                    """
                    cursor.execute(sql, (limit,))

                chunks = cursor.fetchall()
                return [dict(chunk) for chunk in chunks]

    def _get_umap_coordinates(self, chunks: list[dict[str, Any]]) -> np.ndarray:  # type: ignore
        """
        Compute UMAP coordinates for chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Array of 2D coordinates
        """
        if not chunks:
            return np.array([])

        # Get corpus snapshot for cache key
        cache_key = self._get_corpus_snapshot_key()

        # Check cache
        if self.cache_enabled and cache_key in self._umap_cache:
            cached_coords, cached_timestamp = self._umap_cache[cache_key]
            logger.info(f"Using cached UMAP coordinates (age: {time.time() - cached_timestamp:.2f}s)")
            return cached_coords

        # Compute embeddings (simplified - in real implementation, get from DB)
        # For now, use content length as proxy for embedding
        embeddings = np.array([[len(chunk["content"])] for chunk in chunks])

        # Apply UMAP
        logger.info(f"Computing UMAP coordinates for {len(chunks)} chunks")

        # Handle edge case where we have only 1 chunk
        if len(chunks) == 1:
            # For single chunk, return a default coordinate
            coords: np.ndarray = np.array([[0.0, 0.0]])
        else:
            reducer = umap.UMAP(
                n_components=2,
                n_neighbors=min(15, len(chunks) - 1),
                min_dist=0.1,
                random_state=42,
            )
            coords = reducer.fit_transform(embeddings)  # type: ignore
            # Ensure coords is a numpy array
            coords = np.asarray(coords)

        # Cache results
        if self.cache_enabled and self._cache_lock:
            with self._cache_lock:
                self._umap_cache[cache_key] = (coords, time.time())
            logger.info(f"Cached UMAP coordinates for {len(chunks)} chunks")

        return coords

    def _get_corpus_snapshot_key(self) -> str:
        """
        Get cache key based on corpus snapshot (MAX(documents.updated_at)).

        Returns:
            Cache key string
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT MAX(updated_at) FROM documents")
                    result = cursor.fetchone()
                    if result and result[0]:
                        # Use timestamp as cache key
                        timestamp_str = result[0].isoformat()
                        return hashlib.md5(timestamp_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not get corpus snapshot: {e}")

        # Fallback to current time
        return hashlib.md5(str(time.time()).encode()).hexdigest()

    def _create_nodes(
        self,
        chunks: list[dict[str, Any]],
        coords: np.ndarray,
    ) -> list[GraphNode]:
        """
        Create graph nodes from chunks and coordinates.

        Args:
            chunks: List of chunk dictionaries
            coords: UMAP coordinates

        Returns:
            List of GraphNode objects
        """
        nodes = []

        for i, chunk in enumerate(chunks):
            # Create label
            file_path = chunk.get("file_path", "unknown")
            line_start = chunk.get("line_start")
            line_end = chunk.get("line_end")

            if line_start and line_end:
                label = f"{file_path}:{line_start}-{line_end}"
            elif line_start:
                label = f"{file_path}:{line_start}"
            else:
                label = file_path

            # Get coordinates
            if i < len(coords):
                coords_tuple = (float(coords[i][0]), float(coords[i][1]))
            else:
                coords_tuple = (0.0, 0.0)

            # Determine category
            category = None
            if chunk.get("is_anchor"):
                category = "anchor"
            elif file_path.endswith(".md"):
                category = "documentation"
            elif file_path.endswith(".py"):
                category = "code"
            else:
                category = "other"

            node = GraphNode(
                id=f"chunk_{chunk['id']}",
                label=label,
                anchor=chunk.get("anchor_key"),
                coords=coords_tuple,
                category=category,
            )
            nodes.append(node)

        return nodes

    def _create_knn_edges(
        self,
        chunks: list[dict[str, Any]],
        min_sim: float,
    ) -> list[GraphEdge]:
        """
        Create KNN edges based on content similarity.

        Args:
            chunks: List of chunk dictionaries
            min_sim: Minimum similarity threshold

        Returns:
            List of GraphEdge objects
        """
        edges = []

        # Simplified KNN: connect chunks with similar content lengths
        # In real implementation, use actual embeddings and cosine similarity
        for i, chunk1 in enumerate(chunks):
            for j, chunk2 in enumerate(chunks[i + 1 :], i + 1):
                # Simple similarity based on content length
                len1 = len(chunk1["content"])
                len2 = len(chunk2["content"])

                if len1 == 0 or len2 == 0:
                    continue

                # Normalized similarity
                similarity = 1.0 - abs(len1 - len2) / max(len1, len2)

                if similarity >= min_sim:
                    edge = GraphEdge(
                        source=f"chunk_{chunk1['id']}",
                        target=f"chunk_{chunk2['id']}",
                        type="knn",
                        weight=similarity,
                    )
                    edges.append(edge)

        return edges

    def _create_entity_edges(
        self,
        chunks: list[dict[str, Any]],
        min_sim: float,
    ) -> list[GraphEdge]:
        """
        Create entity-based edges.

        Args:
            chunks: List of chunk dictionaries
            min_sim: Minimum similarity threshold

        Returns:
            List of GraphEdge objects
        """
        edges = []

        # Simplified entity edges: connect chunks with same anchor keys
        anchor_groups = {}

        for chunk in chunks:
            anchor_key = chunk.get("anchor_key")
            if anchor_key:
                if anchor_key not in anchor_groups:
                    anchor_groups[anchor_key] = []
                anchor_groups[anchor_key].append(chunk)

        # Create edges within anchor groups
        for anchor_key, group_chunks in anchor_groups.items():
            if len(group_chunks) > 1:
                for i, chunk1 in enumerate(group_chunks):
                    for chunk2 in group_chunks[i + 1 :]:
                        edge = GraphEdge(
                            source=f"chunk_{chunk1['id']}",
                            target=f"chunk_{chunk2['id']}",
                            type="entity",
                            weight=1.0,  # Full weight for same anchor
                        )
                        edges.append(edge)

        return edges

    def clear_cache(self) -> None:
        """Clear UMAP cache."""
        if self.cache_enabled and self._cache_lock:
            with self._cache_lock:
                self._umap_cache.clear()
            logger.info("UMAP cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_enabled:
            return {"enabled": False}

        if self._cache_lock:
            with self._cache_lock:
                return {
                    "enabled": True,
                    "cache_size": len(self._umap_cache),
                    "cache_keys": list(self._umap_cache.keys()),
                }
        return {"enabled": True, "cache_size": 0, "cache_keys": []}
