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
from ..utils.retry_wrapper import retry_llm, TimeoutError
# Import input validation utilities
from ..utils.validator import (
    sanitize_prompt, validate_string_length, validate_query_complexity,
    SecurityError, ValidationError
)
from .cursor_model_router import create_cursor_model_router, CursorModel

_LOG = logging.getLogger("enhanced_rag_system")

# ---------- helpers ----------
def _token_trim(text: str, limit: int, encoder_name: str = "cl100k_base") -> str:
    """Token-aware text truncation to prevent model crashes"""
    enc = tiktoken.get_encoding(encoder_name)
    tokens = enc.encode(text)
    if len(tokens) <= limit:
        return text
    return enc.decode(tokens[-limit:])

def _validate_input(question: str) -> str:
    """Comprehensive input validation for user queries"""
    try:
        # Validate string length
        validate_string_length(question, min_length=1, max_length=5000)
        
        # Validate query complexity
        validate_query_complexity(question, max_tokens=1000)
        
        # Sanitize prompt for security
        sanitized = sanitize_prompt(question)
        
        return sanitized
    except (SecurityError, ValidationError) as e:
        _LOG.error(f"Input validation failed: {e}")
        raise
    except Exception as e:
        _LOG.error(f"Unexpected validation error: {e}")
        raise ValidationError(f"Input validation error: {e}")

# ---------- DSPy Signatures ----------

class QueryRewriteSignature(Signature):
    """Signature for pre-RAG query rewriting and decomposition"""
    
    original_query = InputField(desc="The original user query")
    domain_context = InputField(optional=True, desc="Optional domain-specific vocabulary and context")
    rewritten_query = OutputField(desc="Clear, specific query optimized for retrieval")
    sub_queries = OutputField(desc="List of decomposed sub-queries for multi-hop reasoning")
    search_terms = OutputField(desc="Key terms to focus on during retrieval")

class AnswerSynthesisSignature(Signature):
    """Signature for post-RAG answer synthesis and structuring with research-based enhancements"""
    
    question = InputField(desc="The original question")
    retrieved_chunks = InputField(desc="Retrieved document chunks with span information")
    answer = OutputField(desc="Comprehensive, well-structured answer with citations")
    confidence = OutputField(desc="Confidence level (0-1)")
    sources = OutputField(desc="Cited source documents with span offsets")
    reasoning = OutputField(desc="Step-by-step reasoning process")
    citations = OutputField(desc="List of source documents and character spans used")

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

# ---------- TTL Cache for Module Selector (SIG-3) ----------
_SEL_CACHE = {}
_TTL = 60  # seconds

def _select_module(key: str) -> str:
    """TTL-cached module selector with automatic expiration"""
    now = time.monotonic()
    if key in _SEL_CACHE and now - _SEL_CACHE[key][1] < _TTL:
        return _SEL_CACHE[key][0]
    
    # Expensive module selection logic
    mod = _expensive_selector(key)
    _SEL_CACHE[key] = (mod, now)
    return mod

def _expensive_selector(key: str) -> str:
    """Expensive module selection logic - mocked for now"""
    # In real implementation, this would analyze query complexity
    # and select appropriate DSPy modules
    if "complex" in key.lower():
        return "react"
    elif "compare" in key.lower():
        return "cot"
    else:
        return "standard"

# ---------- Safe Complexity Score (SIG-2) ----------
def _complexity(chunks: List[str]) -> float:
    """Safe complexity score calculation with zero-division guard"""
    if not chunks:
        return 0.0
    
    # Use tiktoken for accurate token counting
    enc = tiktoken.get_encoding("cl100k_base")
    total_tokens = sum(len(enc.encode(chunk)) for chunk in chunks)
    
    # Never divide by zero - use max(len(chunks), 1)
    return total_tokens / max(len(chunks), 1)

def _should_use_fast_path(query: str, config: Dict[str, Any]) -> bool:
    """Determine if query should use fast-path bypass"""
    if not config.get("enabled", True):
        return False
    
    # Check length
    max_length = config.get("max_length", 50)
    if len(query) > max_length:
        return False
    
    # Check for excluded tokens
    exclude_tokens = config.get("exclude_tokens", ["code", "def", "class", "import"])
    query_lower = query.lower()
    for token in exclude_tokens:
        if token in query_lower:
            return False
    
    return True

def _load_fast_path_config() -> Dict[str, Any]:
    """Load fast-path configuration from system.json"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'system.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                system_config = json.load(f)
                return system_config.get("fast_path", {})
    except Exception as e:
        _LOG.warning(f"Could not load fast-path config: {e}")
    
    # Default configuration
    return {
        "enabled": True,
        "max_length": 50,
        "exclude_tokens": ["code", "def", "class", "import"]
    }

# ---------- Pre-RAG Modules ----------

class QueryRewriter(Module):
    """Pre-RAG: Rewrites and decomposes queries for better retrieval"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(QueryRewriteSignature)
    
    def forward(self, query: str, domain_context: str = "") -> Dict[str, Any]:
        """Rewrite query for better retrieval"""
        
        # Comprehensive input validation
        query = _validate_input(query)
        
        # Use DSPy to rewrite the query with domain context in signature
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
        
        query = _validate_input(query)
        
        result = self.predict(
            original_query=query,
            domain_context="Focus on breaking down complex questions into simpler, focused sub-questions"
        )
        
        return result.sub_queries if result.sub_queries else [query]

# ---------- Post-RAG Modules ----------

@dspy.assert_transform_module
class AnswerSynthesizer(Module):
    """Post-RAG: Synthesizes retrieved content into structured answers with research-based validation"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(AnswerSynthesisSignature)
    
    def forward(self, question: str, retrieved_chunks: List[Dict]) -> Dict[str, Any]:
        """Synthesize answer from retrieved chunks with research-based validation"""
        
        question = _validate_input(question)
        
        # Format retrieved chunks for DSPy with span information
        chunks_text = "\n\n".join([
            f"Source {i+1} (Doc {chunk.get('doc_id', 'unknown')}, lines {chunk.get('start_offset', 0)}-{chunk.get('end_offset', 0)}): {chunk.get('content', '')}"
            for i, chunk in enumerate(retrieved_chunks)
        ])
        
        result = self.predict(
            question=question,
            retrieved_chunks=chunks_text
        )
        
        # Research-based assertions for validation (ICML 2023)
        dspy.Assert(self.contains_citations(result.answer), "Answer must include source citations")
        dspy.Assert(len(result.answer) > 50, "Answer must be comprehensive")
        dspy.Assert(self.has_span_references(result.answer), "Answer must reference specific spans")
        
        # Validate confidence score
        confidence = float(result.confidence) if hasattr(result, 'confidence') else 0.7
        dspy.Assert(0 <= confidence <= 1, "Confidence must be between 0 and 1")
        
        return {
            "answer": result.answer,
            "confidence": confidence,
            "sources": result.sources,
            "reasoning": result.reasoning,
            "citations": result.citations if hasattr(result, 'citations') else []
        }
    
    def contains_citations(self, answer: str) -> bool:
        """Check if answer contains citations (research-based validation)"""
        import re
        citation_patterns = [r"Doc \d+", r"lines \d+-\d+", r"according to", r"source \d+"]
        return any(re.search(pattern, answer, re.IGNORECASE) for pattern in citation_patterns)
    
    def has_span_references(self, answer: str) -> bool:
        """Check if answer references specific spans (research-based validation)"""
        import re
        span_patterns = [r"lines \d+-\d+", r"character \d+", r"span \d+"]
        return any(re.search(pattern, answer, re.IGNORECASE) for pattern in span_patterns)

class ChainOfThoughtReasoner(Module):
    """Post-RAG: Uses Chain-of-Thought reasoning over retrieved content"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ChainOfThoughtSignature)
    
    def forward(self, question: str, context: str) -> Dict[str, Any]:
        """Apply Chain-of-Thought reasoning"""
        
        question = _validate_input(question)
        
        result = self.predict(
            question=question,
            context=context
        )
        
        return {
            "answer": result.final_answer,
            "reasoning": result.reasoning_steps
        }

class ReActReasoner(Module):
    """Post-RAG: Uses ReAct pattern for complex reasoning with loop guard (SIG-4)"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ReActSignature)
    
    def forward(self, question: str, context: str) -> Dict[str, Any]:
        """Apply ReAct reasoning pattern with loop guard"""
        
        question = _validate_input(question)
        
        # Use the loop-guarded ReAct implementation
        answer, thought, action, observation = self._run_react_with_guard(question, context)
        
        return {
            "answer": answer,
            "thought": thought,
            "action": action,
            "observation": observation
        }
    
    def _run_react_with_guard(self, question: str, context: str, max_steps: int = 5) -> Tuple[str, str, str, str]:
        """ReAct implementation with loop guard to prevent infinite loops"""
        
        thought = ""
        action = ""
        observation = ""
        steps = 0
        
        while steps < max_steps:
            try:
                # Use DSPy for the reasoning step
                result = self.predict(
                    question=question,
                    context=f"{thought}\n\n{context}\nQ:{question}"
                )
                
                # Check for final answer indicator
                if "FINAL" in result.answer or "final answer" in result.answer.lower():
                    # Extract final answer
                    if "FINAL:" in result.answer:
                        answer = result.answer.split("FINAL:", 1)[1].strip()
                    else:
                        answer = result.answer
                    return answer, thought, action, observation
                
                # Accumulate reasoning
                thought += result.thought + "\n"
                action = result.action
                observation = result.observation
                steps += 1
                
            except Exception as e:
                _LOG.error(f"ReAct step {steps} failed: {e}")
                break
        
        # Bailout if max steps reached or error occurred
        return "Unable to answer confidently after reasoning steps.", thought, action, observation

# ---------- Enhanced RAG System ----------

class MistralLLM(dspy.Module):
"""
ARCHIVED: Legacy Mistral-specific RAG module.
This file is preserved for historical reference. Active code paths should use Cursor-native modules.
"""
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "mistral:7b-instruct", timeout: int = None):
        super().__init__()
        self.base_url = base_url
        self.model = model
        
        # Load timeout configuration
        from ..utils.timeout_config import get_timeout_config
        timeout_config = get_timeout_config()
        self.timeout = timeout or timeout_config.llm_request_timeout
        
        # Create session with retry logic and timeout configuration
        sess = requests.Session()
        retry = Retry(
            total=4, 
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        sess.mount("http://", adapter)
        sess.mount("https://", adapter)
        
        # Set default timeout for all requests
        sess.timeout = (timeout_config.http_connect_timeout, timeout_config.http_read_timeout)
        self._session = sess
    
    def forward(self, prompt: str) -> str:
        """Generate response using Mistral 7B Instruct via Ollama"""
        
        # Use retry_llm with model-specific timeout
        @retry_llm
        def _call_ollama(prompt: str, model: str) -> str:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        
        try:
            return _call_ollama(prompt, self.model)
        except Exception as e:
            _LOG.error("Ollama call failed: %s", e, exc_info=True)
            raise

# Simple cache for responses
_response_cache = {}

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
        
        # Initialize Cursor model router for context engineering
        self.cursor_router = create_cursor_model_router()
        
        self.ctx_limit = ctx_token_limit
    
    def forward(self, question: str, max_results: int = 5, 
                use_cot: bool = True, use_react: bool = False) -> Dict[str, Any]:
        """Enhanced RAG pipeline with pre-RAG and post-RAG DSPy logic"""
        
        # Initialize start_time at the beginning
        start_time = time.time()
        
        try:
            # Comprehensive input validation
            question = _validate_input(question)
            
            # Check cache for identical queries
            cache_key = (question, max_results, use_cot, use_react)
            if cache_key in _response_cache:
                return _response_cache[cache_key]
            
            # === FAST-PATH BYPASS CHECK ===
            fast_path_config = _load_fast_path_config()
            if _should_use_fast_path(question, fast_path_config):
                _LOG.info("⚡ Fast-path: Bypassing complex routing for simple query")
                return self._fast_path_query(question, max_results, start_time)
            
            # === CONTEXT ENGINEERING: Cursor Model Routing ===
            _LOG.info("🎯 Context Engineering: Routing to best Cursor model")
            routing_result = self.cursor_router.route_query(
                query=question,
                urgency="medium",
                complexity=None  # Will be auto-analyzed
            )
            
            if routing_result["status"] == "success":
                _LOG.info(f"Selected model: {routing_result['selected_model']}")
                _LOG.info(f"Context engineering: {routing_result['context_engineering']}")
            else:
                _LOG.warning(f"Model routing failed: {routing_result.get('error', 'Unknown error')}")
            
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
            
            # Add context engineering information to response
            if routing_result["status"] == "success":
                response["context_engineering"] = {
                    "selected_model": routing_result["selected_model"],
                    "engineered_prompt": routing_result["engineered_prompt"],
                    "context_engineering": routing_result["context_engineering"],
                    "prompt_pattern": routing_result["prompt_pattern"],
                    "model_instructions": routing_result["model_instructions"],
                    "capabilities": routing_result["capabilities"],
                    "routing_metadata": routing_result["routing_metadata"]
                }
            
            # Cache the result
            _response_cache[cache_key] = response
            
            return response
            
        except Exception as e:
            _LOG.exception("Enhanced RAG system error")
            return {
                "status": "error",
                "error": str(e),
                "question": question,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
    
    def _fast_path_query(self, question: str, max_results: int, start_time: float) -> Dict[str, Any]:
        """Fast-path bypass for simple queries - direct retrieval and synthesis"""
        
        try:
            _LOG.info(f"⚡ Fast-path: Direct retrieval for '{question}'")
            
            # Direct retrieval without query rewriting
            search_results = self.vector_store("search", query=question, limit=max_results)
            
            if search_results["status"] != "success" or not search_results["results"]:
                return {
                    "status": "no_results",
                    "message": "No relevant information found in knowledge base",
                    "question": question,
                    "rewritten_query": question,  # No rewriting in fast-path
                    "latency_ms": int((time.time() - start_time) * 1000),
                    "fast_path": True
                }
            
            # Simple answer synthesis without complex reasoning
            retrieved_chunks = search_results["results"]
            context_chunks = [chunk.get("content", "") for chunk in retrieved_chunks]
            context = "\n\n".join(context_chunks)
            context = _token_trim(context, self.ctx_limit)
            
            # Use simple answer synthesis
            synthesis_result = self.answer_synthesizer(question, retrieved_chunks)
            
            response = {
                "status": "success",
                "answer": synthesis_result["answer"],
                "sources": [chunk.get("document_id", "") for chunk in retrieved_chunks],
                "question": question,
                "rewritten_query": question,  # No rewriting in fast-path
                "sub_queries": [question],  # Single query in fast-path
                "reasoning": synthesis_result.get("reasoning", ""),
                "confidence": synthesis_result.get("confidence", 0.8),
                "retrieved_chunks": len(retrieved_chunks),
                "latency_ms": int((time.time() - start_time) * 1000),
                "fast_path": True
            }
            
            return response
            
        except Exception as e:
            _LOG.exception("Fast-path query error")
            return {
                "status": "error",
                "error": str(e),
                "question": question,
                "latency_ms": int((time.time() - start_time) * 1000),
                "fast_path": True
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