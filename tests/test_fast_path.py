#!/usr/bin/env python3
"""
Test suite for fast-path bypass functionality.
"""

import os
import sys
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dspy-rag-system', 'src'))

from dspy_modules.enhanced_rag_system import EnhancedRAGSystem, _load_fast_path_config, _should_use_fast_path


class TestFastPathDetection:
    """Test fast-path detection logic"""

    def test_simple_query_fast_path(self):
        """Test that simple queries use fast-path"""
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Simple query under 50 chars
        query = "What is Python?"
        assert _should_use_fast_path(query, config) is True

    def test_long_query_full_path(self):
        """Test that long queries use full-path"""
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Long query over 50 chars
        query = "What are the differences between Python and JavaScript programming languages?"
        assert _should_use_fast_path(query, config) is False

    def test_code_token_full_path(self):
        """Test that queries with code tokens use full-path"""
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Query with code token
        query = "Show me the code for this"
        assert _should_use_fast_path(query, config) is False

    def test_def_token_full_path(self):
        """Test that queries with def tokens use full-path"""
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Query with def token
        query = "How to def a function"
        assert _should_use_fast_path(query, config) is False

    def test_class_token_full_path(self):
        """Test that queries with class tokens use full-path"""
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Query with class token
        query = "Create a class for this"
        assert _should_use_fast_path(query, config) is False

    def test_import_token_full_path(self):
        """Test that queries with import tokens use full-path"""
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Query with import token
        query = "How to import modules"
        assert _should_use_fast_path(query, config) is False

    def test_case_insensitive_detection(self):
        """Test case-insensitive token detection"""
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Query with uppercase tokens
        query = "Show me the CODE"
        assert _should_use_fast_path(query, config) is False

        query = "How to DEF a function"
        assert _should_use_fast_path(query, config) is False

    def test_disabled_fast_path(self):
        """Test that fast-path can be disabled"""
        config = {
            "enabled": False,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Simple query should not use fast-path when disabled
        query = "What is Python?"
        assert _should_use_fast_path(query, config) is False

class TestFastPathConfiguration:
    """Test fast-path configuration loading"""

    @patch('builtins.open')
    @patch('json.load')
    def test_load_fast_path_config_success(self, mock_json_load, mock_open):
        """Test successful fast-path config loading"""
        mock_config = {
            "fast_path": {
                "enabled": True,
                "max_length": 60,
                "exclude_tokens": ["code", "def", "class", "import", "function"]
            }
        }
        mock_json_load.return_value = mock_config

        config = _load_fast_path_config()

        assert config["enabled"] is True
        assert config["max_length"] == 60
        assert "function" in config["exclude_tokens"]

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_fast_path_config_missing_file(self, mock_open):
        """Test fast-path config loading with missing file"""
        config = _load_fast_path_config()

        # Should return default config
        assert config["enabled"] is True
        assert config["max_length"] == 50
        assert "code" in config["exclude_tokens"]

    @patch('builtins.open')
    @patch('json.load', side_effect=Exception("JSON error"))
    def test_load_fast_path_config_invalid_json(self, mock_json_load, mock_open):
        """Test fast-path config loading with invalid JSON"""
        config = _load_fast_path_config()

        # Should return default config
        assert config["enabled"] is True
        assert config["max_length"] == 50

class TestFastPathIntegration:
    """Test fast-path integration with EnhancedRAGSystem"""

    @patch('dspy_rag_system.src.dspy_modules.enhanced_rag_system._load_fast_path_config')
    @patch('dspy_rag_system.src.dspy_modules.enhanced_rag_system._should_use_fast_path')
    def test_fast_path_routing(self, mock_should_use, mock_load_config):
        """Test that fast-path queries use fast-path routing"""
        # Mock configuration
        mock_load_config.return_value = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Mock fast-path detection
        mock_should_use.return_value = True

        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.return_value = {
            "status": "success",
            "results": [
                {"content": "Python is a programming language", "document_id": "doc1"}
            ]
        }

        # Mock answer synthesizer
        mock_synthesizer = Mock()
        mock_synthesizer.return_value = {
            "answer": "Python is a programming language",
            "confidence": 0.9,
            "reasoning": "Based on the retrieved content"
        }

        # Create system with mocked components
        system = EnhancedRAGSystem("mock_connection")
        system.vector_store = mock_vector_store
        system.answer_synthesizer = mock_synthesizer

        # Test fast-path query
        result = system("What is Python?")

        # Verify fast-path was used
        assert result["fast_path"] is True
        assert result["status"] == "success"
        assert "Python is a programming language" in result["answer"]

    @patch('dspy_rag_system.src.dspy_modules.enhanced_rag_system._load_fast_path_config')
    @patch('dspy_rag_system.src.dspy_modules.enhanced_rag_system._should_use_fast_path')
    def test_full_path_routing(self, mock_should_use, mock_load_config):
        """Test that complex queries use full-path routing"""
        # Mock configuration
        mock_load_config.return_value = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Mock full-path detection
        mock_should_use.return_value = False

        # Mock components for full-path
        mock_vector_store = Mock()
        mock_vector_store.return_value = {
            "status": "success",
            "results": [
                {"content": "Complex answer", "document_id": "doc1"}
            ]
        }

        mock_rewriter = Mock()
        mock_rewriter.return_value = {
            "rewritten_query": "What is Python programming language?",
            "sub_queries": ["What is Python programming language?"],
            "search_terms": ["Python", "programming", "language"]
        }

        mock_synthesizer = Mock()
        mock_synthesizer.return_value = {
            "answer": "Complex answer",
            "confidence": 0.8,
            "reasoning": "Complex reasoning"
        }

        # Create system with mocked components
        system = EnhancedRAGSystem("mock_connection")
        system.vector_store = mock_vector_store
        system.query_rewriter = mock_rewriter
        system.answer_synthesizer = mock_synthesizer

        # Test complex query
        result = system("What are the differences between Python and JavaScript programming languages?")

        # Verify full-path was used (no fast_path flag)
        assert "fast_path" not in result
        assert result["status"] == "success"

class TestFastPathPerformance:
    """Test fast-path performance benchmarks"""

    def test_fast_path_latency_benchmark(self):
        """Test that fast-path queries meet latency benchmarks"""
        # This would be an integration test with actual system
        # For now, we test the logic
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Simple query should be fast-path
        query = "What is Python?"
        assert _should_use_fast_path(query, config) is True

        # Complex query should be full-path
        query = "What are the differences between Python and JavaScript programming languages?"
        assert _should_use_fast_path(query, config) is False

    def test_token_detection_performance(self):
        """Test token detection performance"""
        config = {
            "enabled": True,
            "max_length": 50,
            "exclude_tokens": ["code", "def", "class", "import"]
        }

        # Test multiple queries for performance
        queries = [
            "What is Python?",
            "Show me the code",
            "How to def a function",
            "Create a class",
            "How to import modules"
        ]

        results = []
        for query in queries:
            results.append(_should_use_fast_path(query, config))

        # Should have mix of fast-path and full-path
        assert any(results)  # Some should be fast-path
        assert not all(results)  # Not all should be fast-path

class TestFastPathErrorHandling:
    """Test fast-path error handling"""

    def test_fast_path_with_invalid_config(self):
        """Test fast-path with invalid configuration"""
        config = {
            "enabled": True,
            # Missing max_length and exclude_tokens
        }

        # Should use defaults
        query = "What is Python?"
        result = _should_use_fast_path(query, config)
        assert result is True  # Should work with defaults

    def test_fast_path_with_empty_config(self):
        """Test fast-path with empty configuration"""
        config = {}

        # Should use defaults
        query = "What is Python?"
        result = _should_use_fast_path(query, config)
        assert result is True  # Should work with defaults

if __name__ == "__main__":
    pytest.main([__file__])
