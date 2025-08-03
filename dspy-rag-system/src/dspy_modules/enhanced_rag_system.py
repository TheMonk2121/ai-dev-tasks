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
    domain_context = InputField(optional=True, desc="Optional domain-specific vocabulary and context")
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
    """Post-RAG: Uses ReAct pattern for complex reasoning with loop guard (SIG-4)"""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ReActSignature)
    
    def forward(self, question: str, context: str) -> Dict[str, Any]:
        """Apply ReAct reasoning pattern with loop guard"""
        
        question = _sanitize(question)
        
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
        
        self.ctx_limit = ctx_token_limit
    
    def forward(self, question: str, max_results: int = 5, 
                use_cot: bool = True, use_react: bool = False) -> Dict[str, Any]:
        """Enhanced RAG pipeline with pre-RAG and post-RAG DSPy logic"""
        
        # Initialize start_time at the beginning
        start_time = time.time()
        
        try:
            # Sanitize input
            question = _sanitize(question)
            
            # Check cache for identical queries
            cache_key = (question, max_results, use_cot, use_react)
            if cache_key in _response_cache:
                return _response_cache[cache_key]
            
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