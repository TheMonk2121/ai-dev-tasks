#!/usr/bin/env python3
"""
Tests for Documentation Retrieval System

Validates that the documentation retrieval system properly provides
relevant context on-demand to solve context overload.
"""

import os

# Add the dspy-rag-system to the path
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dspy-rag-system', 'src'))

from dspy_modules.documentation_retrieval import (
    ContextSynthesizer,
    DocumentationQueryProcessor,
    DocumentationRetrievalService,
    DocumentationRetriever,
    get_relevant_context,
    get_task_context,
    search_documentation,
)


class TestDocumentationRetrievalService(unittest.TestCase):
    """Test cases for the DocumentationRetrievalService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db_conn_str = "postgresql://test:test@localhost/test_db"
        self.service = DocumentationRetrievalService(self.db_conn_str)
    
    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service.query_processor)
        self.assertIsNotNone(self.service.retriever)
        self.assertIsNotNone(self.service.synthesizer)
    
    @patch('dspy_modules.documentation_retrieval.HybridVectorStore')
    @patch('dspy_modules.documentation_retrieval.EnhancedRAGSystem')
    def test_forward_method(self, mock_rag_system, mock_vector_store):
        """Test the forward method for context retrieval."""
        # Mock the query processor
        mock_query_result = {
            "processed_query": "test query",
            "search_categories": ["core", "workflow"],
            "expected_context": "test context"
        }
        
        # Mock the retriever
        mock_retrieval_result = {
            "relevant_context": "relevant documentation context",
            "context_summary": "Summary of relevant context",
            "confidence_score": 0.85,
            "context_metadata": {"sources": ["test.md"], "categories": ["core"]},
            "retrieved_chunks": [{"content": "test content", "metadata": {"file_name": "test.md"}}]
        }
        
        # Mock the synthesizer
        mock_synthesis_result = {
            "context_synthesis": "synthesized context",
            "context_priority": ["high", "medium"],
            "context_coverage": "comprehensive coverage"
        }
        
        with patch.object(self.service.query_processor, 'forward', return_value=mock_query_result), \
             patch.object(self.service.retriever, 'forward', return_value=mock_retrieval_result), \
             patch.object(self.service.synthesizer, 'forward', return_value=mock_synthesis_result):
            
            result = self.service.forward("test query", "general")
            
            self.assertIn("query", result)
            self.assertIn("context_type", result)
            self.assertIn("relevant_context", result)
            self.assertIn("confidence_score", result)
            self.assertIn("synthesis", result)
            self.assertEqual(result["query"], "test query")
            self.assertEqual(result["context_type"], "general")
    
    def test_get_context_for_task(self):
        """Test getting context for specific tasks."""
        with patch.object(self.service, 'forward') as mock_forward:
            mock_forward.return_value = {"context": "task context"}
            
            result = self.service.get_context_for_task("implement RAG", "development")
            
            mock_forward.assert_called_once()
            self.assertEqual(result["context"], "task context")
    
    def test_get_context_for_file_operation(self):
        """Test getting context for file operations."""
        with patch.object(self.service, 'forward') as mock_forward:
            mock_forward.return_value = {"context": "file operation context"}
            
            result = self.service.get_context_for_file_operation("test.md", "delete")
            
            mock_forward.assert_called_once()
            self.assertEqual(result["context"], "file operation context")
    
    def test_error_handling(self):
        """Test error handling in the service."""
        with patch.object(self.service.query_processor, 'forward', side_effect=Exception("Test error")):
            result = self.service.forward("test query")
            
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Test error")


class TestDocumentationQueryProcessor(unittest.TestCase):
    """Test cases for the DocumentationQueryProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = DocumentationQueryProcessor()
    
    def test_processor_initialization(self):
        """Test that the processor initializes correctly."""
        self.assertIsNotNone(self.processor)
        self.assertIsNotNone(self.processor.query_processor)
    
    @patch('dspy_modules.documentation_retrieval.dspy.ChainOfThought')
    def test_forward_method(self, mock_chain_of_thought):
        """Test the forward method for query processing."""
        # Mock the chain of thought result
        mock_result = MagicMock()
        mock_result.processed_query = "processed query"
        mock_result.search_categories = ["core", "workflow"]
        mock_result.expected_context = "expected context"
        
        mock_chain_of_thought.return_value.return_value = mock_result
        
        result = self.processor.forward("test query", "workflow", "search")
        
        self.assertIn("processed_query", result)
        self.assertIn("search_categories", result)
        self.assertIn("expected_context", result)
        self.assertEqual(result["original_query"], "test query")
        self.assertEqual(result["context_type"], "workflow")
        self.assertEqual(result["query_type"], "search")


class TestDocumentationRetriever(unittest.TestCase):
    """Test cases for the DocumentationRetriever class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_vector_store = MagicMock()
        self.retriever = DocumentationRetriever(self.mock_vector_store)
    
    def test_retriever_initialization(self):
        """Test that the retriever initializes correctly."""
        self.assertIsNotNone(self.retriever)
        self.assertEqual(self.retriever.vector_store, self.mock_vector_store)
    
    def test_forward_method_with_results(self):
        """Test the forward method with search results."""
        # Mock vector store results
        mock_search_results = {
            "results": [
                {"content": "test content 1", "metadata": {"file_name": "test1.md", "category": "core"}},
                {"content": "test content 2", "metadata": {"file_name": "test2.md", "category": "workflow"}}
            ]
        }
        
        self.mock_vector_store.forward.return_value = mock_search_results
        
        with patch.object(self.retriever, 'retrieval_processor') as mock_processor:
            mock_result = MagicMock()
            mock_result.relevant_context = "relevant context"
            mock_result.context_summary = "context summary"
            mock_result.confidence_score = "0.85"
            mock_result.context_metadata = "context metadata"
            
            mock_processor.return_value = mock_result
            
            result = self.retriever.forward("test query", ["core", "workflow"], 5)
            
            self.assertIn("relevant_context", result)
            self.assertIn("context_summary", result)
            self.assertIn("confidence_score", result)
            self.assertIn("context_metadata", result)
            self.assertIn("retrieved_chunks", result)
    
    def test_forward_method_no_results(self):
        """Test the forward method with no search results."""
        # Mock empty vector store results
        self.mock_vector_store.forward.return_value = {"results": []}
        
        result = self.retriever.forward("test query", ["core"], 5)
        
        self.assertEqual(result["relevant_context"], "")
        self.assertEqual(result["context_summary"], "No relevant documentation found")
        self.assertEqual(result["confidence_score"], 0.0)
        self.assertEqual(result["context_metadata"]["sources"], [])
        self.assertEqual(result["context_metadata"]["categories"], [])
    
    def test_extract_context_metadata(self):
        """Test metadata extraction from chunks."""
        chunks = [
            {"metadata": {"file_name": "test1.md", "category": "core"}},
            {"metadata": {"file_name": "test2.md", "category": "workflow"}},
            {"metadata": {"file_name": "test1.md", "category": "core"}}  # Duplicate
        ]
        
        metadata = self.retriever._extract_context_metadata(chunks)
        
        self.assertIn("sources", metadata)
        self.assertIn("categories", metadata)
        self.assertIn("chunk_count", metadata)
        self.assertEqual(len(metadata["sources"]), 2)  # Unique sources
        self.assertEqual(len(metadata["categories"]), 2)  # Unique categories
        self.assertEqual(metadata["chunk_count"], 3)


class TestContextSynthesizer(unittest.TestCase):
    """Test cases for the ContextSynthesizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.synthesizer = ContextSynthesizer()
    
    def test_synthesizer_initialization(self):
        """Test that the synthesizer initializes correctly."""
        self.assertIsNotNone(self.synthesizer)
        self.assertIsNotNone(self.synthesizer.synthesis_processor)
    
    @patch('dspy_modules.documentation_retrieval.dspy.ChainOfThought')
    def test_forward_method_with_contexts(self, mock_chain_of_thought):
        """Test the forward method with retrieved contexts."""
        # Mock the synthesis processor result
        mock_result = MagicMock()
        mock_result.context_synthesis = "synthesized context"
        mock_result.context_priority = ["high", "medium"]
        mock_result.context_coverage = "comprehensive coverage"
        
        mock_chain_of_thought.return_value.return_value = mock_result
        
        contexts = [
            {"content": "context 1", "metadata": {"file_name": "test1.md"}},
            {"content": "context 2", "metadata": {"file_name": "test2.md"}}
        ]
        
        result = self.synthesizer.forward("test query", contexts)
        
        self.assertIn("context_synthesis", result)
        self.assertIn("context_priority", result)
        self.assertIn("context_coverage", result)
        self.assertEqual(result["context_synthesis"], "synthesized context")
        self.assertEqual(result["context_priority"], ["high", "medium"])
        self.assertEqual(result["context_coverage"], "comprehensive coverage")
    
    def test_forward_method_no_contexts(self):
        """Test the forward method with no contexts."""
        result = self.synthesizer.forward("test query", [])
        
        self.assertEqual(result["context_synthesis"], "")
        self.assertEqual(result["context_priority"], [])
        self.assertEqual(result["context_coverage"], "No context available")


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    @patch('dspy_modules.documentation_retrieval.create_documentation_retrieval_service')
    def test_get_relevant_context(self, mock_create_service):
        """Test the get_relevant_context utility function."""
        mock_service = MagicMock()
        mock_service.forward.return_value = {"context": "test context"}
        mock_create_service.return_value = mock_service
        
        result = get_relevant_context("test query")
        
        mock_create_service.assert_called_once()
        mock_service.forward.assert_called_once_with("test query", "general")
        self.assertEqual(result["context"], "test context")
    
    @patch('dspy_modules.documentation_retrieval.create_documentation_retrieval_service')
    def test_search_documentation(self, mock_create_service):
        """Test the search_documentation utility function."""
        mock_service = MagicMock()
        mock_service.search_documentation.return_value = {"results": ["test result"]}
        mock_create_service.return_value = mock_service
        
        result = search_documentation("test query", "core")
        
        mock_create_service.assert_called_once()
        mock_service.search_documentation.assert_called_once_with("test query", "core")
        self.assertEqual(result["results"], ["test result"])
    
    @patch('dspy_modules.documentation_retrieval.create_documentation_retrieval_service')
    def test_get_task_context(self, mock_create_service):
        """Test the get_task_context utility function."""
        mock_service = MagicMock()
        mock_service.get_context_for_task.return_value = {"context": "task context"}
        mock_create_service.return_value = mock_service
        
        result = get_task_context("test task", "development")
        
        mock_create_service.assert_called_once()
        mock_service.get_context_for_task.assert_called_once_with("test task", "development")
        self.assertEqual(result["context"], "task context")


class TestIntegration(unittest.TestCase):
    """Integration tests for the documentation retrieval system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db_conn_str = "postgresql://test:test@localhost/test_db"
    
    @patch('dspy_modules.documentation_retrieval.HybridVectorStore')
    @patch('dspy_modules.documentation_retrieval.EnhancedRAGSystem')
    def test_full_integration(self, mock_rag_system, mock_vector_store):
        """Test full integration of the documentation retrieval system."""
        # Create service
        service = DocumentationRetrievalService(self.db_conn_str)
        
        # Mock all components
        with patch.object(service.query_processor, 'forward') as mock_query, \
             patch.object(service.retriever, 'forward') as mock_retrieve, \
             patch.object(service.synthesizer, 'forward') as mock_synthesize:
            
            # Mock query processing
            mock_query.return_value = {
                "processed_query": "processed test query",
                "search_categories": ["core", "workflow"],
                "expected_context": "expected context"
            }
            
            # Mock retrieval
            mock_retrieve.return_value = {
                "relevant_context": "relevant documentation context",
                "context_summary": "Summary of relevant context",
                "confidence_score": 0.9,
                "context_metadata": {"sources": ["test.md"], "categories": ["core"]},
                "retrieved_chunks": [{"content": "test content", "metadata": {"file_name": "test.md"}}]
            }
            
            # Mock synthesis
            mock_synthesize.return_value = {
                "context_synthesis": "synthesized context",
                "context_priority": ["high"],
                "context_coverage": "comprehensive coverage"
            }
            
            # Test full flow
            result = service.forward("test query", "workflow")
            
            # Verify all components were called
            mock_query.assert_called_once()
            mock_retrieve.assert_called_once()
            mock_synthesize.assert_called_once()
            
            # Verify result structure
            self.assertIn("query", result)
            self.assertIn("context_type", result)
            self.assertIn("relevant_context", result)
            self.assertIn("confidence_score", result)
            self.assertIn("synthesis", result)
            self.assertEqual(result["query"], "test query")
            self.assertEqual(result["context_type"], "workflow")


if __name__ == "__main__":
    unittest.main()
