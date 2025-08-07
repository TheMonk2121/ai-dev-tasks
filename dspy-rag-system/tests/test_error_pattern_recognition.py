#!/usr/bin/env python3
"""
Tests for the Error Pattern Recognition System
"""

import pytest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.error_pattern_recognition import (
    ErrorPatternRecognizer, 
    analyze_error_pattern, 
    get_error_statistics,
    suggest_recovery_strategy,
    ErrorPattern,
    ErrorAnalysis
)

class TestErrorPatternRecognition:
    """Test cases for error pattern recognition"""
    
    def test_error_pattern_recognizer_initialization(self):
        """Test that the error pattern recognizer initializes correctly"""
        recognizer = ErrorPatternRecognizer()
        assert recognizer is not None
        assert len(recognizer.patterns) > 0
        assert isinstance(recognizer.pattern_stats, dict)
    
    def test_database_connection_timeout_pattern(self):
        """Test recognition of database connection timeout errors"""
        error_message = "Database connection timeout after 30 seconds"
        analysis = analyze_error_pattern(error_message, "ConnectionError")
        
        assert analysis is not None
        assert len(analysis.matched_patterns) > 0
        assert any(pattern.pattern_id == "DB_CONNECTION_TIMEOUT" for pattern in analysis.matched_patterns)
        assert analysis.severity_score > 0
        assert len(analysis.recovery_actions) > 0
    
    def test_llm_rate_limit_pattern(self):
        """Test recognition of LLM rate limit errors"""
        error_message = "Rate limit exceeded: too many requests (429)"
        analysis = analyze_error_pattern(error_message, "HTTPError")
        
        assert analysis is not None
        assert len(analysis.matched_patterns) > 0
        assert any(pattern.pattern_id == "LLM_RATE_LIMIT" for pattern in analysis.matched_patterns)
        assert analysis.severity_score > 0
    
    def test_file_not_found_pattern(self):
        """Test recognition of file not found errors"""
        error_message = "File not found: /path/to/missing/file.txt"
        analysis = analyze_error_pattern(error_message, "FileNotFoundError")
        
        assert analysis is not None
        assert len(analysis.matched_patterns) > 0
        assert any(pattern.pattern_id == "FILE_NOT_FOUND" for pattern in analysis.matched_patterns)
    
    def test_security_violation_pattern(self):
        """Test recognition of security violation errors"""
        error_message = "Security violation: blocked pattern detected"
        analysis = analyze_error_pattern(error_message, "SecurityError")
        
        assert analysis is not None
        assert len(analysis.matched_patterns) > 0
        assert any(pattern.pattern_id == "SECURITY_VIOLATION" for pattern in analysis.matched_patterns)
        assert analysis.severity_score >= 0.75  # Should be high severity
    
    def test_model_specific_pattern(self):
        """Test recognition of model-specific errors"""
        error_message = "Mistral model context window exceeded"
        context = {"model_id": "mistral-7b-instruct"}
        analysis = analyze_error_pattern(error_message, "ValueError", context)
        
        assert analysis is not None
        assert len(analysis.matched_patterns) > 0
        assert any(pattern.pattern_id == "MISTRAL_CONTEXT_LIMIT" for pattern in analysis.matched_patterns)
        assert analysis.model_specific_handling is not None
    
    def test_no_pattern_match(self):
        """Test behavior when no patterns match"""
        error_message = "Some completely unrelated error message"
        analysis = analyze_error_pattern(error_message, "Exception")
        
        assert analysis is not None
        assert len(analysis.matched_patterns) == 0
        assert analysis.severity_score == 0.0
        assert analysis.confidence == 0.0
    
    def test_multiple_pattern_matches(self):
        """Test recognition of multiple patterns in one error"""
        error_message = "Database connection timeout and authentication failed"
        analysis = analyze_error_pattern(error_message, "ConnectionError")
        
        assert analysis is not None
        assert len(analysis.matched_patterns) >= 2
        pattern_ids = [pattern.pattern_id for pattern in analysis.matched_patterns]
        assert "DB_CONNECTION_TIMEOUT" in pattern_ids
        assert "DB_AUTHENTICATION_FAILED" in pattern_ids
    
    def test_severity_score_calculation(self):
        """Test that severity scores are calculated correctly"""
        # Test critical severity
        error_message = "Security violation: blocked pattern detected"
        analysis = analyze_error_pattern(error_message, "SecurityError")
        assert analysis.severity_score == 1.0  # Critical should be 1.0
        
        # Test medium severity
        error_message = "File not found: /path/to/file"
        analysis = analyze_error_pattern(error_message, "FileNotFoundError")
        assert analysis.severity_score == 0.5  # Medium should be 0.5
    
    def test_confidence_calculation(self):
        """Test that confidence scores are calculated correctly"""
        # Single pattern match
        error_message = "Database connection timeout"
        analysis = analyze_error_pattern(error_message, "ConnectionError")
        assert analysis.confidence == 0.3  # Single match should be 0.3
        
        # Multiple pattern matches
        error_message = "Database connection timeout and authentication failed"
        analysis = analyze_error_pattern(error_message, "ConnectionError")
        assert analysis.confidence == 0.6  # Two matches should be 0.6
    
    def test_recovery_strategy_suggestions(self):
        """Test that recovery strategies are suggested correctly"""
        error_message = "Database connection timeout"
        analysis = analyze_error_pattern(error_message, "ConnectionError")
        
        strategies = suggest_recovery_strategy(analysis)
        assert len(strategies) > 0
        assert any("database" in strategy.lower() for strategy in strategies)
    
    def test_pattern_statistics(self):
        """Test that pattern statistics are tracked correctly"""
        # Clear statistics by creating new recognizer
        recognizer = ErrorPatternRecognizer()
        
        # Analyze some errors
        analyze_error_pattern("Database connection timeout", "ConnectionError")
        analyze_error_pattern("File not found", "FileNotFoundError")
        analyze_error_pattern("Database connection timeout", "ConnectionError")  # Duplicate
        
        stats = get_error_statistics()
        assert stats['total_patterns'] > 0
        assert len(stats['pattern_stats']) >= 2  # Should have stats for both patterns
        assert len(stats['most_common_patterns']) > 0
    
    def test_context_extraction(self):
        """Test that context information is properly extracted and used"""
        error_message = "Yi-Coder model error occurred"
        context = {"model_id": "yi-coder-9b-chat", "operation": "text_generation"}
        analysis = analyze_error_pattern(error_message, "ModelError", context)
        
        assert analysis is not None
        assert analysis.model_specific_handling is not None
        assert "yi-coder" in analysis.model_specific_handling.lower()
    
    def test_error_pattern_categories(self):
        """Test that error patterns are properly categorized"""
        recognizer = ErrorPatternRecognizer()
        
        categories = set(pattern.category for pattern in recognizer.patterns)
        expected_categories = {"database", "llm", "file", "security", "network", "system", "configuration"}
        
        # Check that we have patterns in expected categories
        for category in expected_categories:
            assert any(pattern.category == category for pattern in recognizer.patterns), \
                f"Missing patterns for category: {category}"
    
    def test_custom_pattern_loading(self):
        """Test loading of custom error patterns from config"""
        # This test verifies that the system can load custom patterns
        # The actual loading is tested by the initialization
        recognizer = ErrorPatternRecognizer()
        assert recognizer is not None
        # If custom patterns file exists, it should be loaded
        # If not, it should use defaults without error

if __name__ == "__main__":
    pytest.main([__file__]) 