# Deep Research Analysis Request: Enhanced DSPy RAG System

## Context for Code Review

You're reviewing an **enhanced DSPy RAG system** that implements a revolutionary approach: using DSPy **both before and after the RAG step**. This is a significant advancement over traditional RAG systems that only use LLMs for answer generation.

Your job is to act as a senior engineer performing a system-aware code review of this enhanced DSPy implementation.

### Instructions:

1. **Identify architectural strengths and weaknesses** in the pre-RAG and post-RAG DSPy modules
2. **Evaluate the reasoning patterns** (Chain-of-Thought, ReAct) for effectiveness and correctness
3. **Assess query complexity analysis** and automatic module selection logic
4. **Review domain context implementation** and its impact on query rewriting
5. **Analyze performance optimizations** and potential bottlenecks
6. **Check for edge cases** and error handling in the enhanced pipeline
7. **Suggest improvements** for production readiness and scalability
8. **Provide specific test code** for every suggested improvement

This is a **production-ready RAG system** that needs to handle real-world queries with high reliability and performance.

## Development Environment & Tools

- **Python 3.9** (not 3.10+ features like `match` statements)
- **DSPy framework** for LLM orchestration and prompt engineering
- **PostgreSQL with pgvector** for vector storage and similarity search
- **Ollama with Mistral-7B** for local LLM inference
- **Local development** - no cloud dependencies
- **Production focus** - needs to handle real-world workloads

## Recent Improvements Made

We've already implemented critical fixes in other modules:

### VectorStore Module:
- ✅ **pgvector adapter** for direct numpy storage
- ✅ **Connection pooling** with SimpleConnectionPool
- ✅ **Singleton model** with @lru_cache for SentenceTransformer
- ✅ **Bulk inserts** with execute_values for efficiency
- ✅ **UUID document IDs** to prevent collisions
- ✅ **Metadata optimization** (once per document, not per chunk)

### RAG System Module:
- ✅ **Connection pooling & retry logic** for Ollama API calls
- ✅ **Token-aware truncation** with tiktoken to prevent crashes
- ✅ **Prompt injection prevention** with input sanitization
- ✅ **LRU caching** for identical queries
- ✅ **Enhanced error handling** with structured responses

### DocumentProcessor Module:
- ✅ **UUID-based document IDs** to prevent collisions
- ✅ **PyMuPDF integration** for better PDF handling
- ✅ **Structured chunks** with rich metadata
- ✅ **Security validation** with file path and size limits
- ✅ **CSV streaming** for memory-efficient processing

### Watch Folder Module:
- ✅ **Secure subprocess execution** with command injection prevention
- ✅ **File stability polling** to prevent partial write processing
- ✅ **Concurrent processing** with ThreadPoolExecutor
- ✅ **Graceful shutdown** with context manager
- ✅ **Enhanced error handling** and resource management

## Current Code for Review

Please review the following Enhanced DSPy RAG System code:

### 1. Enhanced RAG System (`src/dspy_modules/enhanced_rag_system.py`)

```python
#!/usr/bin/env python3
"""
Enhanced DSPy RAG System
Implements pre-RAG query rewriting and post-RAG answer synthesis
"""

import os
import sys
import json
import uuid
import functools
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
import dspy
from dspy import Module, Signature, InputField, OutputField, ChainOfThought, ReAct
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import tiktoken
from .vector_store import VectorStore

_LOG = logging.getLogger("enhanced_rag_system")

# ---------- helpers ----------
def _token_trim(text: str, limit: int, encoder_name: str = "cl100k_base") -> str:
    """Token-aware text truncation to prevent model crashes"""
    enc = tiktoken.get_encoding(encoder_name)
    tokens = enc.encode(text)
    if len(tokens) <= limit:
        return text
    return enc.decode(tokens[-limit:])

def _sanitize(user_prompt: str) -> str:
    """Prevent prompt injection attacks"""
    blocklist = ["ignore previous", "system:", "assistant:", "ignore all previous"]
    lowered = user_prompt.lower()
    if any(b in lowered for b in blocklist):
        raise ValueError("Prompt contains disallowed patterns")
    return user_prompt

# ---------- DSPy Signatures ----------

class QueryRewriteSignature(Signature):
    """Signature for pre-RAG query rewriting and decomposition"""
    
    original_query = InputField(desc="The original user query")
    domain_context = InputField(desc="Domain-specific vocabulary and context")
    rewritten_query = OutputField(desc="Clear, specific query optimized for retrieval")
    sub_queries = OutputField(desc="List of decomposed sub-queries for multi-hop reasoning")
    search_terms = OutputField(desc="Key terms to focus on during retrieval")

class AnswerSynthesisSignature(Signature):
    """Signature for post-RAG answer synthesis and structuring"""
    
    question = InputField(desc="The original question")
    retrieved_chunks = InputField(desc="Retrieved document chunks")
    answer = OutputField(desc="Comprehensive, well-structured answer")
    confidence = OutputField(desc="Confidence level (0-1)")
    sources = OutputField(desc="Cited source documents")
    reasoning = OutputField(desc="Step-by-step reasoning process")

class ChainOfThoughtSignature(Signature):
    """Signature for structured reasoning over retrieved content"""
    
    question = InputField(desc="The question to answer")
    context = InputField(desc="Retrieved context")
    reasoning_steps = OutputField(desc="Step-by-step reasoning")
    final_answer = OutputField(desc="Final synthesized answer")

class ReActSignature(Signature):
    """Signature for ReAct (Reasoning + Acting) pattern"""
    
    question = InputField(desc="The question to answer")
    context = InputField(desc="Available context")
    thought = OutputField(desc="Reasoning about the question")
    action = OutputField(desc="What action to take (search, synthesize, etc.)")
    observation = OutputField(desc="Result of the action")
    answer = OutputField(desc="Final answer based on reasoning")

# ---------- Pre-RAG Modules ----------

class QueryRewriter(Module):
    """Pre-RAG: Rewrites and decomposes queries for better retrieval"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(QueryRewriteSignature)
    
    def forward(self, query: str, domain_context: str = "") -> Dict[str, Any]:
        """Rewrite query for better retrieval"""
        
        # Sanitize input
        query = _sanitize(query)
        
        # Use DSPy to rewrite the query
        result = self.predict(
            original_query=query,
            domain_context=domain_context
        )
        
        return {
            "original_query": query,
            "rewritten_query": result.rewritten_query,
            "sub_queries": result.sub_queries,
            "search_terms": result.search_terms
        }

class QueryDecomposer(Module):
    """Pre-RAG: Decomposes complex queries into simpler sub-queries"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(QueryRewriteSignature)
    
    def forward(self, query: str) -> List[str]:
        """Decompose complex query into sub-queries"""
        
        query = _sanitize(query)
        
        result = self.predict(
            original_query=query,
            domain_context="Focus on breaking down complex questions into simpler, focused sub-questions"
        )
        
        return result.sub_queries if result.sub_queries else [query]

# ---------- Post-RAG Modules ----------

class AnswerSynthesizer(Module):
    """Post-RAG: Synthesizes retrieved content into structured answers"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(AnswerSynthesisSignature)
    
    def forward(self, question: str, retrieved_chunks: List[Dict]) -> Dict[str, Any]:
        """Synthesize answer from retrieved chunks"""
        
        question = _sanitize(question)
        
        # Format retrieved chunks for DSPy
        chunks_text = "\n\n".join([
            f"Source {i+1}: {chunk.get('content', '')}"
            for i, chunk in enumerate(retrieved_chunks)
        ])
        
        result = self.predict(
            question=question,
            retrieved_chunks=chunks_text
        )
        
        return {
            "answer": result.answer,
            "confidence": result.confidence,
            "sources": result.sources,
            "reasoning": result.reasoning
        }

class ChainOfThoughtReasoner(Module):
    """Post-RAG: Uses Chain-of-Thought reasoning over retrieved content"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ChainOfThoughtSignature)
    
    def forward(self, question: str, context: str) -> Dict[str, Any]:
        """Apply Chain-of-Thought reasoning"""
        
        question = _sanitize(question)
        
        result = self.predict(
            question=question,
            context=context
        )
        
        return {
            "answer": result.final_answer,
            "reasoning": result.reasoning_steps
        }

class ReActReasoner(Module):
    """Post-RAG: Uses ReAct pattern for complex reasoning"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ReActSignature)
    
    def forward(self, question: str, context: str) -> Dict[str, Any]:
        """Apply ReAct reasoning pattern"""
        
        question = _sanitize(question)
        
        result = self.predict(
            question=question,
            context=context
        )
        
        return {
            "answer": result.answer,
            "thought": result.thought,
            "action": result.action,
            "observation": result.observation
        }

# ---------- Enhanced RAG System ----------

class MistralLLM(dspy.Module):
    """DSPy module for Mistral via Ollama with connection pooling and retry logic"""
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "mistral", timeout: int = 30):
        super().__init__()
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        
        # Create session with retry logic
        sess = requests.Session()
        retry = Retry(
            total=4, 
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504]
        )
        sess.mount("http://", HTTPAdapter(max_retries=retry))
        self._session = sess
    
    def forward(self, prompt: str) -> str:
        """Generate response using Mistral via Ollama"""
        
        try:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["response"].strip()
                
        except Exception as e:
            _LOG.error("Ollama call failed: %s", e, exc_info=True)
            raise

@functools.lru_cache(maxsize=128)
def _lru_cached_answer(key):
    raise RuntimeError

class EnhancedRAGSystem(Module):
    """Enhanced DSPy RAG system with pre-RAG and post-RAG DSPy logic"""
    
    def __init__(self, db_connection_string: str, 
                 mistral_url: str = "http://localhost:11434",
                 ctx_token_limit: int = 3500):
        super().__init__()
        
        # Initialize components
        self.vector_store = VectorStore(db_connection_string)
        self.llm = MistralLLM(mistral_url)
        
        # Pre-RAG modules
        self.query_rewriter = QueryRewriter()
        self.query_decomposer = QueryDecomposer()
        
        # Post-RAG modules
        self.answer_synthesizer = AnswerSynthesizer()
        self.cot_reasoner = ChainOfThoughtReasoner()
        self.react_reasoner = ReActReasoner()
        
        self.ctx_limit = ctx_token_limit
    
    def forward(self, question: str, max_results: int = 5, 
                use_cot: bool = True, use_react: bool = False) -> Dict[str, Any]:
        """Enhanced RAG pipeline with pre-RAG and post-RAG DSPy logic"""
        
        try:
            # Sanitize input
            question = _sanitize(question)
            
            # Check cache for identical queries
            cache_key = (question, max_results, use_cot, use_react)
            if cache_key in _lru_cached_answer.cache:
                return _lru_cached_answer.cache[cache_key]
            
            start_time = time.time()
            
            # === PRE-RAG: Query Rewriting and Decomposition ===
            _LOG.info("🔄 Pre-RAG: Rewriting query")
            query_rewrite_result = self.query_rewriter(question)
            rewritten_query = query_rewrite_result["rewritten_query"]
            
            # Check if query needs decomposition
            if len(question.split()) > 20 or "and" in question.lower() or "or" in question.lower():
                _LOG.info("🔄 Pre-RAG: Decomposing complex query")
                sub_queries = self.query_decomposer(question)
                _LOG.info(f"Generated {len(sub_queries)} sub-queries")
            else:
                sub_queries = [rewritten_query]
            
            # === RAG: Retrieval ===
            all_retrieved_chunks = []
            
            for sub_query in sub_queries:
                _LOG.info(f"🔍 Retrieving for sub-query: {sub_query}")
                search_results = self.vector_store("search", query=sub_query, limit=max_results)
                
                if search_results["status"] == "success":
                    all_retrieved_chunks.extend(search_results["results"])
            
            # Remove duplicates and limit results
            unique_chunks = []
            seen_content = set()
            for chunk in all_retrieved_chunks:
                content_hash = hash(chunk.get("content", ""))
                if content_hash not in seen_content:
                    unique_chunks.append(chunk)
                    seen_content.add(content_hash)
            
            if not unique_chunks:
                return {
                    "status": "no_results",
                    "message": "No relevant information found in knowledge base",
                    "question": question,
                    "rewritten_query": rewritten_query,
                    "latency_ms": int((time.time() - start_time) * 1000)
                }
            
            # Truncate context to token limit
            context_chunks = [chunk.get("content", "") for chunk in unique_chunks]
            context = "\n\n".join(context_chunks)
            context = _token_trim(context, self.ctx_limit)
            
            # === POST-RAG: Answer Synthesis ===
            _LOG.info("🧠 Post-RAG: Synthesizing answer")
            
            # Use different reasoning patterns based on complexity
            if use_react and len(question.split()) > 15:
                _LOG.info("Using ReAct reasoning for complex question")
                synthesis_result = self.react_reasoner(question, context)
                answer = synthesis_result["answer"]
                reasoning = synthesis_result.get("thought", "")
            elif use_cot:
                _LOG.info("Using Chain-of-Thought reasoning")
                synthesis_result = self.cot_reasoner(question, context)
                answer = synthesis_result["answer"]
                reasoning = synthesis_result.get("reasoning", "")
            else:
                _LOG.info("Using standard answer synthesis")
                synthesis_result = self.answer_synthesizer(question, unique_chunks)
                answer = synthesis_result["answer"]
                reasoning = synthesis_result.get("reasoning", "")
            
            # Prepare response
            response = {
                "status": "success",
                "answer": answer,
                "sources": [chunk.get("document_id", "") for chunk in unique_chunks],
                "question": question,
                "rewritten_query": rewritten_query,
                "sub_queries": sub_queries,
                "reasoning": reasoning,
                "confidence": synthesis_result.get("confidence", 0.8),
                "retrieved_chunks": len(unique_chunks),
                "latency_ms": int((time.time() - start_time) * 1000)
            }
            
            # Cache the result
            _lru_cached_answer.cache[cache_key] = response
            
            return response
            
        except Exception as e:
            _LOG.exception("Enhanced RAG system error")
            return {
                "status": "error",
                "error": str(e),
                "question": question,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            return self.vector_store.get_statistics()
        except Exception as e:
            _LOG.error("Failed to get stats: %s", e)
            return {"error": str(e)}

# ---------- Interface Classes ----------

class EnhancedRAGQueryInterface:
    """Enhanced interface for RAG queries with pre-RAG and post-RAG DSPy logic"""
    
    def __init__(self, db_connection_string: str, mistral_url: str = "http://localhost:11434"):
        self.rag_system = EnhancedRAGSystem(db_connection_string, mistral_url)
    
    def ask(self, question: str, use_cot: bool = True, use_react: bool = False) -> Dict[str, Any]:
        """Ask a question with enhanced DSPy processing"""
        return self.rag_system(question, use_cot=use_cot, use_react=use_react)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.rag_system.get_stats()

def create_enhanced_rag_interface(db_url: str = None, 
                                mistral_url: str = "http://localhost:11434") -> EnhancedRAGQueryInterface:
    """Create enhanced RAG interface with pre-RAG and post-RAG DSPy logic"""
    
    if db_url is None:
        db_url = os.getenv("POSTGRES_DSN", "postgresql://ai_user:ai_password@localhost:5432/ai_agency")
    
    return EnhancedRAGQueryInterface(db_url, mistral_url)

# ---------- Utility Functions ----------

def analyze_query_complexity(query: str) -> Dict[str, Any]:
    """Analyze query complexity to determine appropriate DSPy modules"""
    
    word_count = len(query.split())
    has_logical_operators = any(op in query.lower() for op in ["and", "or", "but", "however"])
    has_comparisons = any(op in query.lower() for op in ["compare", "difference", "similar", "versus"])
    has_multi_part = query.count("?") > 1 or query.count(".") > 2
    
    complexity_score = 0
    if word_count > 20:
        complexity_score += 2
    if has_logical_operators:
        complexity_score += 1
    if has_comparisons:
        complexity_score += 1
    if has_multi_part:
        complexity_score += 1
    
    return {
        "word_count": word_count,
        "has_logical_operators": has_logical_operators,
        "has_comparisons": has_comparisons,
        "has_multi_part": has_multi_part,
        "complexity_score": complexity_score,
        "recommended_modules": {
            "use_decomposition": complexity_score >= 2,
            "use_cot": complexity_score >= 1,
            "use_react": complexity_score >= 3
        }
    }

def create_domain_context(domain: str = "general") -> str:
    """Create domain-specific context for query rewriting"""
    
    domain_contexts = {
        "technical": "Focus on technical terminology, code, APIs, and system architecture",
        "academic": "Focus on research methodology, citations, and scholarly language",
        "business": "Focus on business terminology, metrics, and strategic concepts",
        "medical": "Focus on medical terminology, symptoms, and clinical concepts",
        "legal": "Focus on legal terminology, precedents, and regulatory concepts",
        "general": "Focus on clear, specific language and common terminology"
    }
    
    return domain_contexts.get(domain, domain_contexts["general"])
```

### 2. Interactive Interface (`enhanced_ask_question.py`)

The interactive interface provides:
- Query complexity analysis and display
- Domain context setting
- Forced reasoning mode selection
- Real-time response display with detailed breakdown
- Command system for different analysis modes

### 3. Test Suite (`test_enhanced_rag_system.py`)

Comprehensive test suite covering:
- Unit tests for each module
- Integration tests for complete pipeline
- Performance tests with benchmarks
- Edge case tests for boundary conditions
- Error handling tests

## Critical Request: Test Code for Every Improvement

**IMPORTANT**: For every improvement you suggest, please provide the **actual test code** to validate that improvement. This is crucial because:

1. **We want to test the implementation, not just the idea**
2. **Deep research approaches testing differently** - we want to see your testing methodology
3. **Production readiness** requires comprehensive test coverage
4. **We need specific, runnable test code** for every suggested fix

### Test Requirements:
- **Unit tests** for individual functions/methods
- **Integration tests** for complete DSPy pipeline
- **Performance tests** with benchmarks and thresholds
- **Security tests** for input validation and sanitization
- **Resilience tests** for error handling and failure scenarios
- **Edge case tests** for boundary conditions and unusual inputs
- **Complete setup/teardown** with proper isolation
- **Specific assertions** and expected outcomes
- **Performance benchmarks** where applicable

Please provide the **complete test code** for every improvement you suggest, not just test descriptions. We want to see your testing approach and implementation.

## Review Focus Areas

Given this is an enhanced DSPy RAG system, please focus on:

### **🔴 Critical Priority:**
1. **DSPy Signature Design**: Are the signatures optimal for the reasoning patterns?
2. **Query Complexity Analysis**: Is the complexity scoring accurate and useful?
3. **Module Selection Logic**: Does the automatic module selection work correctly?
4. **Reasoning Pattern Implementation**: Are Chain-of-Thought and ReAct implemented correctly?

### **🟠 High Priority:**
1. **Pre-RAG Pipeline**: Query rewriting and decomposition effectiveness
2. **Post-RAG Pipeline**: Answer synthesis and reasoning quality
3. **Performance Optimization**: Caching, token management, response times
4. **Error Handling**: Graceful failure recovery and user feedback

### **🟡 Medium Priority:**
1. **Domain Context Integration**: How well does domain context improve queries?
2. **Configuration Management**: Environment variables, validation, defaults
3. **Logging and Monitoring**: Structured logging, performance metrics
4. **Scalability**: Can this handle production workloads?

## Specific Areas of Concern:

### **1. DSPy Signature Design**
- Are the input/output fields optimal for the reasoning patterns?
- Do the signatures capture the right information for each module?
- Are there missing fields that would improve functionality?

### **2. Query Complexity Analysis**
- Is the complexity scoring algorithm accurate?
- Are the thresholds for module selection appropriate?
- Does it handle edge cases properly?

### **3. Reasoning Pattern Implementation**
- Is Chain-of-Thought implemented correctly for step-by-step reasoning?
- Is ReAct implemented correctly for complex problem solving?
- Do the reasoning patterns actually improve answer quality?

### **4. Performance and Scalability**
- Is the caching strategy optimal?
- Are there memory leaks or performance bottlenecks?
- Can this handle concurrent requests?

### **5. Error Handling and Resilience**
- How does the system handle DSPy prediction failures?
- What happens when Ollama is unavailable?
- Are there proper fallbacks for each module?

### **6. Production Readiness**
- Is the logging comprehensive enough for debugging?
- Are there proper metrics for monitoring?
- Is the configuration flexible enough for different environments?

## Advanced Analysis Request

### **DSPy-Specific Concerns:**
1. **Signature Optimization**: Are the DSPy signatures designed optimally for the reasoning patterns?
2. **Module Composition**: Is the composition of modules effective for the RAG pipeline?
3. **Prompt Engineering**: Are the implicit prompts in the signatures effective?
4. **Reasoning Pattern Accuracy**: Do Chain-of-Thought and ReAct actually improve reasoning?

### **RAG-Specific Concerns:**
1. **Query Rewriting Effectiveness**: Does query rewriting actually improve retrieval?
2. **Answer Synthesis Quality**: Does the post-RAG processing improve answer quality?
3. **Context Utilization**: Is the retrieved context used effectively?
4. **Source Attribution**: Are sources properly tracked and cited?

### **Performance Concerns:**
1. **Latency**: Are there optimizations to reduce response time?
2. **Memory Usage**: Are there memory leaks or inefficient data structures?
3. **Concurrency**: Can this handle multiple concurrent requests?
4. **Caching Strategy**: Is the caching strategy optimal?

Please provide your analysis with specific, actionable improvements and the complete test code to validate each improvement. Focus on making this production-ready for real-world RAG workloads with enhanced DSPy capabilities. 