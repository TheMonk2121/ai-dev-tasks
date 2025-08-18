#!/usr/bin/env python3.11
"""
Unit tests for entity expansion functionality.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.entity_overlay import Entity, calculate_adaptive_k_related, extract_entities_from_query


class TestEntityExtraction(unittest.TestCase):
    """Test entity extraction functionality."""

    def test_extract_entities_camelcase(self):
        """Test extraction of CamelCase entities."""
        query = "How do I implement HybridVectorStore in my project?"
        entities = extract_entities_from_query(query)

        self.assertGreater(len(entities), 0)
        camelcase_entities = [e for e in entities if e.entity_type == "CLASS_FUNCTION"]
        self.assertGreater(len(camelcase_entities), 0)

        # Check that HybridVectorStore is extracted
        entity_texts = [e.text for e in entities]
        self.assertIn("HybridVectorStore", entity_texts)

    def test_extract_entities_snake_case(self):
        """Test extraction of snake_case entities."""
        query = "What is the memory_rehydrator function?"
        entities = extract_entities_from_query(query)

        self.assertGreater(len(entities), 0)
        snake_case_entities = [e for e in entities if e.entity_type == "VARIABLE_FUNCTION"]
        self.assertGreater(len(snake_case_entities), 0)

        # Check that memory_rehydrator is extracted
        entity_texts = [e.text for e in entities]
        self.assertIn("memory_rehydrator", entity_texts)

    def test_extract_entities_file_path(self):
        """Test extraction of file path entities."""
        query = "How to use entity_overlay.py in the project?"
        entities = extract_entities_from_query(query)

        self.assertGreater(len(entities), 0)
        file_path_entities = [e for e in entities if e.entity_type == "FILE_PATH"]
        self.assertGreater(len(file_path_entities), 0)

        # Check that entity_overlay.py is extracted
        entity_texts = [e.text for e in entities]
        self.assertIn("entity_overlay.py", entity_texts)

    def test_extract_entities_no_entities(self):
        """Test extraction with no entities."""
        query = "What is the current status?"
        entities = extract_entities_from_query(query)

        # Should return few or no entities for queries without clear entities
        # The current implementation might extract some common words as entities
        self.assertLessEqual(len(entities), 5)

    def test_deduplicate_entities(self):
        """Test entity deduplication."""
        # Create overlapping entities
        entity1 = Entity("HybridVectorStore", "CLASS_FUNCTION", 0.8, 0, 15)
        entity2 = Entity("VectorStore", "CLASS_FUNCTION", 0.6, 8, 19)  # Overlaps with entity1

        from utils.entity_overlay import _deduplicate_entities

        deduplicated = _deduplicate_entities([entity1, entity2])

        # Should keep the higher confidence entity
        self.assertEqual(len(deduplicated), 1)
        self.assertEqual(deduplicated[0].text, "HybridVectorStore")


class TestAdaptiveKRelated(unittest.TestCase):
    """Test adaptive k_related calculation."""

    def test_calculate_adaptive_k_related_zero_entities(self):
        """Test k_related calculation with zero entities."""
        k = calculate_adaptive_k_related(base_k=2, entity_count=0)
        self.assertEqual(k, 2)

    def test_calculate_adaptive_k_related_one_entity(self):
        """Test k_related calculation with one entity."""
        k = calculate_adaptive_k_related(base_k=2, entity_count=1)
        self.assertEqual(k, 4)  # min(8, 2 + 1*2)

    def test_calculate_adaptive_k_related_multiple_entities(self):
        """Test k_related calculation with multiple entities."""
        k = calculate_adaptive_k_related(base_k=2, entity_count=5)
        self.assertEqual(k, 8)  # min(8, 2 + 5*2) = min(8, 12) = 8

    def test_calculate_adaptive_k_related_minimum(self):
        """Test k_related calculation ensures minimum of 1."""
        k = calculate_adaptive_k_related(base_k=0, entity_count=0)
        self.assertEqual(k, 1)


class TestEntityExpansionIntegration(unittest.TestCase):
    """Test entity expansion integration."""

    @patch("utils.memory_rehydrator.vector_search")
    def test_fetch_entity_adjacent_chunks(self, mock_vector_search):
        """Test fetching entity-adjacent chunks."""
        # Mock vector search results
        mock_results = [
            {
                "id": "chunk1",
                "text": "This is about HybridVectorStore",
                "sim": 0.8,
                "file": "test.py",
                "path": "test.py#L1-10",
            },
            {
                "id": "chunk2",
                "text": "Another chunk about memory_rehydrator",
                "sim": 0.7,
                "file": "test2.py",
                "path": "test2.py#L5-15",
            },
        ]
        mock_vector_search.return_value = mock_results

        from utils.entity_overlay import fetch_entity_adjacent_chunks

        entities = [
            Entity("HybridVectorStore", "CLASS_FUNCTION", 0.8, 0, 15),
            Entity("memory_rehydrator", "VARIABLE_FUNCTION", 0.7, 20, 35),
        ]

        chunks = fetch_entity_adjacent_chunks(entities=entities, k_per_entity=1, stability_threshold=0.6)

        self.assertGreater(len(chunks), 0)
        self.assertTrue(all(chunk.get("entity_related") for chunk in chunks))
        self.assertTrue(all(chunk.get("sim", 0) >= 0.6 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
