#!/usr/bin/env python3
"""
Unit tests for GraphDataProvider module.

Tests all public methods, cache logic, error handling, and edge cases
as specified in the task requirements.
"""

import time
from unittest import TestCase
from unittest.mock import Mock, patch

import numpy as np
import pytest
from psycopg2.extras import RealDictRow

from src.utils.database_resilience import DatabaseResilienceManager
from src.utils.graph_data_provider import (
    GraphDataProvider,
)


class TestGraphDataProvider(TestCase):
    """Test cases for GraphDataProvider class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_manager = Mock(spec=DatabaseResilienceManager)
        self.provider = GraphDataProvider(
            db_manager=self.mock_db_manager,
            max_nodes=100,
            cache_enabled=True,
            feature_flag_enabled=True,
        )

    def _setup_mock_database(self, mock_chunks):
        """Helper method to set up mock database with proper context managers."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [RealDictRow(chunk) for chunk in mock_chunks]
        # Make the cursor a context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor
        # Make the connection a context manager
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        self.mock_db_manager.get_connection.return_value = mock_conn
        return mock_cursor

    def test_init_defaults(self):
        """Test GraphDataProvider initialization with defaults."""
        provider = GraphDataProvider(self.mock_db_manager)
        self.assertEqual(provider.max_nodes, 2000)
        self.assertTrue(provider.cache_enabled)
        self.assertTrue(provider.feature_flag_enabled)

    def test_init_custom_values(self):
        """Test GraphDataProvider initialization with custom values."""
        provider = GraphDataProvider(
            db_manager=self.mock_db_manager,
            max_nodes=500,
            cache_enabled=False,
            feature_flag_enabled=False,
        )
        self.assertEqual(provider.max_nodes, 500)
        self.assertFalse(provider.cache_enabled)
        self.assertFalse(provider.feature_flag_enabled)

    def test_get_graph_data_feature_flag_disabled(self):
        """Test get_graph_data raises ValueError when feature flag is disabled."""
        provider = GraphDataProvider(
            db_manager=self.mock_db_manager,
            feature_flag_enabled=False,
        )

        with self.assertRaises(ValueError) as context:
            provider.get_graph_data()

        self.assertIn("disabled", str(context.exception))

    def test_get_graph_data_empty_chunks(self):
        """Test get_graph_data with empty chunks returns empty result."""
        # Mock empty database result
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        # Make the cursor a context manager
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor
        # Make the connection a context manager
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        self.mock_db_manager.get_connection.return_value = mock_conn

        result = self.provider.get_graph_data()

        self.assertEqual(len(result.nodes), 0)
        self.assertEqual(len(result.edges), 0)
        self.assertFalse(result.truncated)
        self.assertGreaterEqual(result.elapsed_ms, 0)

    def test_get_graph_data_with_chunks(self):
        """Test get_graph_data with actual chunks."""
        # Mock database result
        mock_chunks = [
            {
                "id": 1,
                "content": "Test content 1",
                "file_path": "test1.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
            {
                "id": 2,
                "content": "Test content 2",
                "file_path": "test2.py",
                "line_start": 15,
                "line_end": 25,
                "is_anchor": True,
                "anchor_key": "test_anchor",
                "metadata": {},
            },
        ]

        self._setup_mock_database(mock_chunks)

        # Mock UMAP computation
        with patch.object(self.provider, "_get_umap_coordinates") as mock_umap:
            mock_umap.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])

            result = self.provider.get_graph_data()

        self.assertEqual(len(result.nodes), 2)
        self.assertGreater(len(result.edges), 0)
        self.assertFalse(result.truncated)

    def test_get_cluster_data_nodes_only(self):
        """Test get_cluster_data returns nodes only (no edges)."""
        # Mock database result
        mock_chunks = [
            {
                "id": 1,
                "content": "Test content",
                "file_path": "test.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
        ]

        self._setup_mock_database(mock_chunks)

        # Mock UMAP computation
        with patch.object(self.provider, "_get_umap_coordinates") as mock_umap:
            mock_umap.return_value = np.array([[0.1, 0.2]])

            result = self.provider.get_cluster_data()

        self.assertEqual(len(result.nodes), 1)
        self.assertEqual(len(result.edges), 0)  # No edges for cluster data

    def test_max_nodes_limit_enforcement(self):
        """Test max_nodes limit enforcement with truncated flag."""
        # Mock database result with more chunks than limit
        mock_chunks = [
            {
                "id": i,
                "content": f"Test content {i}",
                "file_path": f"test{i}.md",
                "line_start": i * 10,
                "line_end": i * 10 + 10,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            }
            for i in range(150)  # More than max_nodes (100)
        ]

        self._setup_mock_database(mock_chunks[:100])

        # Mock UMAP computation
        with patch.object(self.provider, "_get_umap_coordinates") as mock_umap:
            mock_umap.return_value = np.random.rand(100, 2)

            result = self.provider.get_graph_data()

        self.assertEqual(len(result.nodes), 100)  # Limited to max_nodes
        self.assertTrue(result.truncated)  # Should be marked as truncated

    def test_query_filtering(self):
        """Test query filtering in database queries."""
        mock_cursor = self._setup_mock_database([])

        self.provider.get_graph_data(query="test query")

        # Verify SQL query was executed with search parameters
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        self.assertIn("content_tsv @@ plainto_tsquery", call_args[0])
        self.assertEqual(call_args[1], ("test query", "test query", 100))

    def test_umap_caching(self):
        """Test UMAP caching functionality."""
        # Mock database result
        mock_chunks = [
            {
                "id": 1,
                "content": "Test content",
                "file_path": "test.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
        ]

        self._setup_mock_database(mock_chunks)

        # Mock corpus snapshot key
        with patch.object(self.provider, "_get_corpus_snapshot_key") as mock_key:
            mock_key.return_value = "test_cache_key"

            # First call should compute UMAP
            self.provider.get_graph_data()

            # Second call should use cache
            self.provider.get_graph_data()

            # Verify cache was used
            self.assertIn("test_cache_key", self.provider._umap_cache)

    def test_cache_disabled(self):
        """Test behavior when cache is disabled."""
        provider = GraphDataProvider(
            db_manager=self.mock_db_manager,
            cache_enabled=False,
        )

        # Mock database result
        mock_chunks = [
            {
                "id": 1,
                "content": "Test content",
                "file_path": "test.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
        ]

        self._setup_mock_database(mock_chunks)

        # Mock corpus snapshot key
        with patch.object(provider, "_get_corpus_snapshot_key") as mock_key:
            mock_key.return_value = "test_cache_key"

            provider.get_graph_data()

            # Verify no cache was used
            self.assertEqual(len(provider._umap_cache), 0)

    def test_create_nodes_with_coordinates(self):
        """Test node creation with UMAP coordinates."""
        chunks = [
            {
                "id": 1,
                "content": "Test content",
                "file_path": "test.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
        ]
        coords = np.array([[0.1, 0.2]])

        nodes = self.provider._create_nodes(chunks, coords)

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "chunk_1")
        self.assertEqual(nodes[0].label, "test.md:10-20")
        self.assertEqual(nodes[0].coords, (0.1, 0.2))
        self.assertEqual(nodes[0].category, "documentation")

    def test_create_nodes_anchor_category(self):
        """Test node creation with anchor category."""
        chunks = [
            {
                "id": 1,
                "content": "Test content",
                "file_path": "test.py",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": True,
                "anchor_key": "test_anchor",
                "metadata": {},
            },
        ]
        coords = np.array([[0.1, 0.2]])

        nodes = self.provider._create_nodes(chunks, coords)

        self.assertEqual(nodes[0].category, "anchor")
        self.assertEqual(nodes[0].anchor, "test_anchor")

    def test_create_knn_edges(self):
        """Test KNN edge creation."""
        chunks = [
            {
                "id": 1,
                "content": "Short content",
                "file_path": "test1.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
            {
                "id": 2,
                "content": "Short content too",
                "file_path": "test2.md",
                "line_start": 15,
                "line_end": 25,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
        ]

        edges = self.provider._create_knn_edges(chunks, min_sim=0.5)

        self.assertGreater(len(edges), 0)
        for edge in edges:
            self.assertEqual(edge.type, "knn")
            self.assertGreaterEqual(edge.weight, 0.5)

    def test_create_entity_edges(self):
        """Test entity edge creation."""
        chunks = [
            {
                "id": 1,
                "content": "Test content 1",
                "file_path": "test1.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": "same_anchor",
                "metadata": {},
            },
            {
                "id": 2,
                "content": "Test content 2",
                "file_path": "test2.md",
                "line_start": 15,
                "line_end": 25,
                "is_anchor": False,
                "anchor_key": "same_anchor",
                "metadata": {},
            },
            {
                "id": 3,
                "content": "Test content 3",
                "file_path": "test3.md",
                "line_start": 20,
                "line_end": 30,
                "is_anchor": False,
                "anchor_key": "different_anchor",
                "metadata": {},
            },
        ]

        edges = self.provider._create_entity_edges(chunks, min_sim=0.5)

        # Should have one edge between chunks 1 and 2 (same anchor)
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].type, "entity")
        self.assertEqual(edges[0].weight, 1.0)

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Add some data to cache
        self.provider._umap_cache["test_key"] = (np.array([[0.1, 0.2]]), time.time())

        self.provider.clear_cache()

        self.assertEqual(len(self.provider._umap_cache), 0)

    def test_get_cache_stats(self):
        """Test cache statistics retrieval."""
        # Add some data to cache
        self.provider._umap_cache["test_key"] = (np.array([[0.1, 0.2]]), time.time())

        stats = self.provider.get_cache_stats()

        self.assertTrue(stats["enabled"])
        self.assertEqual(stats["cache_size"], 1)
        self.assertIn("test_key", stats["cache_keys"])

    def test_get_cache_stats_disabled(self):
        """Test cache statistics when cache is disabled."""
        provider = GraphDataProvider(
            db_manager=self.mock_db_manager,
            cache_enabled=False,
        )

        stats = provider.get_cache_stats()

        self.assertFalse(stats["enabled"])

    def test_database_error_handling(self):
        """Test database error handling."""
        self.mock_db_manager.get_connection.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.provider.get_graph_data()

        self.assertIn("Database error", str(context.exception))

    def test_umap_computation_error_handling(self):
        """Test UMAP computation error handling."""
        # Mock database result
        mock_chunks = [
            {
                "id": 1,
                "content": "Test content 1",
                "file_path": "test1.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
            {
                "id": 2,
                "content": "Test content 2",
                "file_path": "test2.md",
                "line_start": 15,
                "line_end": 25,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
        ]

        self._setup_mock_database(mock_chunks)

        # Mock UMAP to raise exception
        with patch("umap.UMAP") as mock_umap_class:
            mock_umap_instance = Mock()
            mock_umap_instance.fit_transform.side_effect = Exception("UMAP error")
            mock_umap_class.return_value = mock_umap_instance

            with self.assertRaises(Exception) as context:
                self.provider.get_graph_data()

            self.assertIn("UMAP error", str(context.exception))

    def test_edge_case_empty_content(self):
        """Test edge case with empty content."""
        chunks = [
            {
                "id": 1,
                "content": "",
                "file_path": "test1.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
            {
                "id": 2,
                "content": "Non-empty content",
                "file_path": "test2.md",
                "line_start": 15,
                "line_end": 25,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
        ]

        edges = self.provider._create_knn_edges(chunks, min_sim=0.5)

        # Should handle empty content gracefully
        self.assertIsInstance(edges, list)

    def test_edge_case_missing_coordinates(self):
        """Test edge case with missing coordinates."""
        chunks = [
            {
                "id": 1,
                "content": "Test content",
                "file_path": "test.md",
                "line_start": 10,
                "line_end": 20,
                "is_anchor": False,
                "anchor_key": None,
                "metadata": {},
            },
        ]
        coords = np.array([])  # Empty coordinates

        nodes = self.provider._create_nodes(chunks, coords)

        # Should handle missing coordinates gracefully
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].coords, (0.0, 0.0))  # Default coordinates


if __name__ == "__main__":
    pytest.main([__file__])
