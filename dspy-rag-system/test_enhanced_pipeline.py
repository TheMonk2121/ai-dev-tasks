#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced DSPy RAG System
Validates all critical fixes identified by deep research
"""

import pytest
import time
import functools
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

# Add src to path for imports
import sys
sys.path.append('src')

try:
    from dspy_modules.enhanced_rag_system import (
        EnhancedRAGSystem,
        QueryRewriter,
        QueryDecomposer,
        AnswerSynthesizer,
        ChainOfThoughtReasoner,
        ReActReasoner,
        analyze_query_complexity,
        create_domain_context,
        _complexity,
        _select_module,
        _SEL_CACHE,
        _TTL
    )
except ImportError as e:
    pytest.skip(f"Enhanced RAG system not available: {e}")

# ---------- Test Fixtures ----------

@pytest.fixture(scope="module")
def ersys():
    """Create enhanced RAG system with mocked components"""
    class DummyVS:
        """Stub vector store for testing"""
        def __call__(self, op, **kw):
            if op == "search":
                return {
                    "status": "success",
                    "results": [{"content": "Paris is the capital of France.", "document_id": "doc1"}]
                }
            return {"status": "error", "error": "Unknown operation"}
    
    class DummyLLM:
        """Stub LLM for testing"""
        def forward(self, prompt):
            return "Mocked response"
    
    # Create system with mocked components
    system = EnhancedRAGSystem("mock_db_url")
    system.vector_store = DummyVS()
    system.llm = DummyLLM()
    
    return system

@pytest.fixture
def query_rewriter():
    """Create query rewriter for testing"""
    return QueryRewriter()

@pytest.fixture
def react_reasoner():
    """Create ReAct reasoner for testing"""
    return ReActReasoner()

# ---------- SIG-1: Signature Correction Tests ----------

class TestSignatureCorrection:
    """Test that DSPy signatures properly handle domain context"""
    
    def test_signature_accepts_domain(self, query_rewriter):
        """Test that signature properly accepts domain context"""
        with patch('dspy_modules.enhanced_rag_system.dspy.Predict') as mock_predict:
            # Mock DSPy response
            mock_result = Mock()
            mock_result.rewritten_query = "What is the financial impact?"
            mock_result.sub_queries = ["What is the financial impact?"]
            mock_result.search_terms = ["financial", "impact"]
            mock_predict.return_value.return_value = mock_result
            
            # Test with domain context
            result = query_rewriter("What's the impact?", domain_context="finance")
            
            # Verify domain context was passed to signature
            mock_predict.assert_called_once()
            call_args = mock_predict.return_value.call_args
            assert call_args[1]['domain_context'] == "finance"
            assert 'rewritten_query' in result
    
    def test_signature_handles_empty_domain(self, query_rewriter):
        """Test that signature handles empty domain context"""
        with patch('dspy_modules.enhanced_rag_system.dspy.Predict') as mock_predict:
            mock_result = Mock()
            mock_result.rewritten_query = "What is this about?"
            mock_result.sub_queries = ["What is this about?"]
            mock_result.search_terms = ["about"]
            mock_predict.return_value.return_value = mock_result
            
            # Test with empty domain context
            result = query_rewriter("What is this?")
            
            # Verify empty domain context is handled
            call_args = mock_predict.return_value.call_args
            assert call_args[1]['domain_context'] == ""
            assert result['rewritten_query'] == "What is this about?"

# ---------- SIG-2: Safe Complexity Score Tests ----------

class TestSafeComplexityScore:
    """Test safe complexity score calculation with zero-division guard"""
    
    def test_complexity_no_chunks(self):
        """Test complexity calculation with empty chunk list"""
        result = _complexity([])
        assert result == 0.0
    
    def test_complexity_single_chunk(self):
        """Test complexity calculation with single chunk"""
        chunks = ["This is a test chunk with some content."]
        result = _complexity(chunks)
        assert result > 0.0
        assert isinstance(result, float)
    
    def test_complexity_multiple_chunks(self):
        """Test complexity calculation with multiple chunks"""
        chunks = [
            "First chunk with some content.",
            "Second chunk with different content.",
            "Third chunk with more content."
        ]
        result = _complexity(chunks)
        assert result > 0.0
        assert isinstance(result, float)
    
    def test_complexity_unicode_chunks(self):
        """Test complexity calculation with unicode content"""
        chunks = ["Paris est la capitale de la France.", "🚀 Rocket emoji test"]
        result = _complexity(chunks)
        assert result > 0.0
        assert isinstance(result, float)
    
    def test_complexity_special_characters(self):
        """Test complexity calculation with special characters"""
        chunks = ["Test with @#$%^&*() symbols", "Numbers 12345 and symbols !@#"]
        result = _complexity(chunks)
        assert result > 0.0
        assert isinstance(result, float)

# ---------- SIG-3: TTL Cache Tests ----------

class TestTTLCache:
    """Test TTL cache for module selector"""
    
    def test_selector_ttl_caching(self, monkeypatch):
        """Test that TTL cache works correctly"""
        calls = {"n": 0}
        
        def fake_expensive_selector(key):
            calls["n"] += 1
            return "X"
        
        monkeypatch.setattr('dspy_modules.enhanced_rag_system._expensive_selector', fake_expensive_selector)
        
        # Clear cache
        _SEL_CACHE.clear()
        
        # First call should hit expensive selector
        result1 = _select_module("q1")
        assert calls["n"] == 1
        assert result1 == "X"
        
        # Second call should use cache
        result2 = _select_module("q1")
        assert calls["n"] == 1  # Still 1, not 2
        assert result2 == "X"
    
    def test_selector_ttl_expiration(self, monkeypatch):
        """Test that TTL cache expires correctly"""
        calls = {"n": 0}
        
        def fake_expensive_selector(key):
            calls["n"] += 1
            return "X"
        
        monkeypatch.setattr('dspy_modules.enhanced_rag_system._expensive_selector', fake_expensive_selector)
        
        # Clear cache
        _SEL_CACHE.clear()
        
        # First call
        _select_module("q1")
        assert calls["n"] == 1
        
        # Simulate time passing beyond TTL
        with patch('time.monotonic') as mock_time:
            mock_time.return_value = time.monotonic() + _TTL + 0.1
            
            # Call again - should hit expensive selector again
            _select_module("q1")
            assert calls["n"] == 2
    
    def test_selector_different_keys(self, monkeypatch):
        """Test that different keys don't interfere with cache"""
        calls = {"n": 0}
        
        def fake_expensive_selector(key):
            calls["n"] += 1
            return f"result_{key}"
        
        monkeypatch.setattr('dspy_modules.enhanced_rag_system._expensive_selector', fake_expensive_selector)
        
        # Clear cache
        _SEL_CACHE.clear()
        
        # Different keys should result in different calls
        result1 = _select_module("key1")
        result2 = _select_module("key2")
        
        assert calls["n"] == 2
        assert result1 == "result_key1"
        assert result2 == "result_key2"

# ---------- SIG-4: ReAct Loop Guard Tests ----------

class TestReActLoopGuard:
    """Test ReAct loop guard to prevent infinite loops"""
    
    def test_react_loop_guard_success(self, react_reasoner, monkeypatch):
        """Test ReAct with successful completion"""
        # Mock DSPy responses that lead to completion
        responses = [
            Mock(answer="THINK step1", thought="First thought", action="analyze", observation="Found info"),
            Mock(answer="THINK step2", thought="Second thought", action="synthesize", observation="Combined info"),
            Mock(answer="FINAL: Paris is the capital of France", thought="Final thought", action="answer", observation="Complete")
        ]
        
        with patch.object(react_reasoner, 'predict') as mock_predict:
            mock_predict.side_effect = responses
            
            answer, thought, action, observation = react_reasoner._run_react_with_guard(
                "What is Paris?", "Paris is a city in France.", max_steps=5
            )
            
            assert answer == "Paris is the capital of France"
            assert "First thought" in thought
            assert action == "answer"
            assert observation == "Complete"
    
    def test_react_loop_guard_bailout(self, react_reasoner, monkeypatch):
        """Test ReAct bailout when max steps reached"""
        # Mock DSPy responses that never complete
        def never_complete(*args):
            return Mock(answer="THINK loop", thought="Another step", action="think", observation="Still thinking")
        
        with patch.object(react_reasoner, 'predict', side_effect=never_complete):
            answer, thought, action, observation = react_reasoner._run_react_with_guard(
                "What is Paris?", "Paris is a city in France.", max_steps=3
            )
            
            assert "Unable to answer confidently" in answer
            assert "Another step" in thought
    
    def test_react_loop_guard_exception(self, react_reasoner, monkeypatch):
        """Test ReAct bailout when exception occurs"""
        def failing_predict(*args):
            raise Exception("DSPy prediction failed")
        
        with patch.object(react_reasoner, 'predict', side_effect=failing_predict):
            answer, thought, action, observation = react_reasoner._run_react_with_guard(
                "What is Paris?", "Paris is a city in France.", max_steps=5
            )
            
            assert "Unable to answer confidently" in answer
            assert thought == ""
            assert action == ""
            assert observation == ""
    
    def test_react_loop_guard_final_answer_extraction(self, react_reasoner, monkeypatch):
        """Test ReAct final answer extraction from different formats"""
        test_cases = [
            ("FINAL: Paris is the capital", "Paris is the capital"),
            ("final answer: Paris is the capital", "Paris is the capital"),
            ("Paris is the capital", "Paris is the capital"),  # No FINAL indicator
        ]
        
        for response_text, expected_answer in test_cases:
            with patch.object(react_reasoner, 'predict') as mock_predict:
                mock_predict.return_value = Mock(
                    answer=response_text,
                    thought="Thought",
                    action="action",
                    observation="observation"
                )
                
                answer, thought, action, observation = react_reasoner._run_react_with_guard(
                    "What is Paris?", "Context", max_steps=1
                )
                
                assert answer == expected_answer

# ---------- Integration Tests ----------

class TestEndToEndIntegration:
    """Test complete end-to-end pipeline"""
    
    def test_end_to_end_simple_query(self, ersys):
        """Test complete pipeline with simple query"""
        with patch.object(ersys.query_rewriter, 'predict') as mock_rewrite:
            with patch.object(ersys.answer_synthesizer, 'predict') as mock_synthesize:
                # Mock query rewriting
                mock_rewrite.return_value = Mock(
                    rewritten_query="What is Paris?",
                    sub_queries=["What is Paris?"],
                    search_terms=["Paris"]
                )
                
                # Mock answer synthesis
                mock_synthesize.return_value = Mock(
                    answer="Paris is the capital of France.",
                    confidence=0.9,
                    sources=["doc1"],
                    reasoning="Based on the retrieved content..."
                )
                
                result = ersys("What is Paris?")
                
                assert result["status"] == "success"
                assert "Paris" in result["answer"]
                assert result["confidence"] == 0.9
                assert len(result["sources"]) == 1
    
    def test_end_to_end_complex_query(self, ersys):
        """Test complete pipeline with complex query requiring decomposition"""
        with patch.object(ersys.query_rewriter, 'predict') as mock_rewrite:
            with patch.object(ersys.query_decomposer, 'predict') as mock_decompose:
                with patch.object(ersys.cot_reasoner, 'predict') as mock_cot:
                    # Mock query rewriting
                    mock_rewrite.return_value = Mock(
                        rewritten_query="Complex query about Paris and London",
                        sub_queries=[],
                        search_terms=["Paris", "London"]
                    )
                    
                    # Mock query decomposition
                    mock_decompose.return_value = Mock(
                        sub_queries=["What is Paris?", "What is London?", "How do they compare?"]
                    )
                    
                    # Mock Chain-of-Thought reasoning
                    mock_cot.return_value = Mock(
                        final_answer="Paris and London are both major European capitals.",
                        reasoning_steps="Step 1: Analyze Paris. Step 2: Analyze London. Step 3: Compare."
                    )
                    
                    result = ersys("Compare Paris and London", use_cot=True)
                    
                    assert result["status"] == "success"
                    assert "Paris" in result["answer"]
                    assert "London" in result["answer"]
                    assert len(result["sub_queries"]) == 3

# ---------- Performance Tests ----------

class TestPerformance:
    """Test performance characteristics"""
    
    def test_complexity_calculation_performance(self, benchmark):
        """Test complexity calculation performance"""
        chunks = ["Test chunk " + str(i) for i in range(100)]
        
        def calculate_complexity():
            return _complexity(chunks)
        
        result = benchmark(calculate_complexity)
        assert result > 0.0
    
    def test_selector_cache_performance(self, benchmark):
        """Test module selector cache performance"""
        def select_module():
            return _select_module("test_key")
        
        result = benchmark(select_module)
        assert result in ["react", "cot", "standard"]
    
    def test_query_complexity_analysis_performance(self, benchmark):
        """Test query complexity analysis performance"""
        query = "What are the differences between the old and new systems and how do they compare in terms of performance and reliability?"
        
        def analyze_complexity():
            return analyze_query_complexity(query)
        
        result = benchmark(analyze_complexity)
        assert result["complexity_score"] >= 3

# ---------- Edge Case Tests ----------

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_query_handling(self, ersys):
        """Test handling of empty queries"""
        with patch.object(ersys.query_rewriter, 'predict') as mock_rewrite:
            mock_rewrite.return_value = Mock(
                rewritten_query="",
                sub_queries=[],
                search_terms=[]
            )
            
            result = ersys("")
            assert result["status"] == "no_results"
    
    def test_very_long_query(self, ersys):
        """Test handling of very long queries"""
        long_query = "What is " + "very " * 100 + "long?"
        
        with patch.object(ersys.query_rewriter, 'predict') as mock_rewrite:
            mock_rewrite.return_value = Mock(
                rewritten_query=long_query,
                sub_queries=[long_query],
                search_terms=["very", "long"]
            )
            
            result = ersys(long_query)
            assert result["status"] == "success"
    
    def test_special_characters_in_query(self, ersys):
        """Test handling of special characters"""
        special_query = "What about @#$%^&*() symbols?"
        
        with patch.object(ersys.query_rewriter, 'predict') as mock_rewrite:
            mock_rewrite.return_value = Mock(
                rewritten_query=special_query,
                sub_queries=[special_query],
                search_terms=["symbols"]
            )
            
            result = ersys(special_query)
            assert result["status"] == "success"
    
    def test_unicode_characters_in_query(self, ersys):
        """Test handling of unicode characters"""
        unicode_query = "What about émojis 🚀 and unicode?"
        
        with patch.object(ersys.query_rewriter, 'predict') as mock_rewrite:
            mock_rewrite.return_value = Mock(
                rewritten_query=unicode_query,
                sub_queries=[unicode_query],
                search_terms=["unicode"]
            )
            
            result = ersys(unicode_query)
            assert result["status"] == "success"

# ---------- Error Handling Tests ----------

class TestErrorHandling:
    """Test error handling and resilience"""
    
    def test_dspy_prediction_failure(self, ersys):
        """Test handling of DSPy prediction failures"""
        with patch.object(ersys.query_rewriter, 'predict', side_effect=Exception("DSPy failed")):
            result = ersys("What is Paris?")
            assert result["status"] == "error"
            assert "DSPy failed" in result["error"]
    
    def test_vector_store_failure(self, ersys):
        """Test handling of vector store failures"""
        ersys.vector_store = Mock()
        ersys.vector_store.return_value = {"status": "error", "error": "Database error"}
        
        result = ersys("What is Paris?")
        assert result["status"] == "no_results"
    
    def test_llm_failure(self, ersys):
        """Test handling of LLM failures"""
        with patch.object(ersys.llm, 'forward', side_effect=Exception("LLM failed")):
            result = ersys("What is Paris?")
            assert result["status"] == "error"
            assert "LLM failed" in result["error"]

# ---------- Main Test Runner ----------

if __name__ == "__main__":
    print("🧪 Running Enhanced DSPy RAG System Tests")
    print("=" * 50)
    print("Testing all critical fixes:")
    print("  SIG-1: DSPy signature correction")
    print("  SIG-2: Safe complexity score")
    print("  SIG-3: TTL cache for module selector")
    print("  SIG-4: ReAct loop guard")
    print("=" * 50)
    
    # Run tests
    pytest.main([__file__, "-v"]) 