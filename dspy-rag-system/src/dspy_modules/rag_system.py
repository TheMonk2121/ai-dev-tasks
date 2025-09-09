#!/usr/bin/env python3
"""
DSPy RAG System
Complete RAG system using DSPy with Mistral integration.
"""

import functools
import logging
import os
import sys
import time
from typing import Any, Dict, Optional

# Apply litellm compatibility shim before importing DSPy
try:
    sys.path.insert(0, "../../../scripts")
    from litellm_compatibility_shim import patch_litellm_imports

    patch_litellm_imports()
except ImportError:
    pass  # Shim not available, continue without it

import dspy
import requests
import tiktoken  # token aware truncation
from dspy import InputField, Module, OutputField, Signature
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .vector_store import HybridVectorStore as VectorStore  # type: ignore

_LOG = logging.getLogger("rag_system")


# ---------- helpers ----------
def _token_trim(text: str, limit: int, encoder_name: str = "cl100k_base") -> str:
    """Token-aware text truncation to prevent model crashes"""
    enc = tiktoken.get_encoding(encoder_name)
    tokens = enc.encode(text)
    if len(tokens) <= limit:
        return text
    return enc.decode(tokens[-limit:])  # keep tail (most recent)


def _sanitize(user_prompt: str) -> str:
    """Prevent prompt injection attacks"""
    blocklist = ["ignore previous", "system:", "assistant:", "ignore all previous"]
    lowered = user_prompt.lower()
    if any(b in lowered for b in blocklist):
        raise ValueError("Prompt contains disallowed patterns")
    return user_prompt


class MistralLLM(dspy.Module):
    """DSPy module for Mistral 7B Instruct via Ollama with connection pooling and retry logic"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral:7b-instruct", timeout: int = 30):
        super().__init__()
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

        # Create session with retry logic
        sess = requests.Session()
        retry = Retry(total=4, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        sess.mount("http://", HTTPAdapter(max_retries=retry))
        self._session = sess

    def forward(self, prompt: str) -> str:
        """Generate response using Mistral 7B Instruct via Ollama with proper error handling"""

        try:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()["response"].strip()

        except Exception as e:
            _LOG.error("Ollama call failed: %s", e, exc_info=True)
            raise


class RAGSignature(Signature):
    """Signature for RAG question answering"""

    question = InputField(desc="The question to answer")
    answer = OutputField(desc="The answer based on the context")
    sources = OutputField(desc="Source document IDs")


# ---------- RAG core ----------
@functools.lru_cache(maxsize=128)
def _lru_cached_answer(key):  # helper for cache; populated in RAGSystem
    raise RuntimeError  # will never be called


class RAGSystem(Module):
    """Complete DSPy RAG system with Mistral integration and optimizations"""

    def __init__(
        self, db_connection_string: str, mistral_url: str = "http://localhost:11434", ctx_token_limit: int = 3500
    ):
        super().__init__()

        # Initialize components
        self.vector_store = VectorStore(db_connection_string)
        self.llm = MistralLLM(mistral_url)
        self.pred = dspy.Predict(RAGSignature)
        self.ctx_limit = ctx_token_limit

    def forward(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """Answer a question using RAG system with caching and optimizations"""

        try:
            # Sanitize input to prevent prompt injection
            question = _sanitize(question)

            # Check cache for identical queries
            cache_key = (question, max_results)
            if cache_key in _lru_cached_answer.cache:  # type: ignore
                return _lru_cached_answer.cache[cache_key]  # type: ignore

            start = time.time()

            # 1. Search for relevant context
            search_results = self.vector_store("search", query=question, limit=max_results)

            if search_results["status"] != "success":
                raise RuntimeError(search_results.get("error", "search_fail"))

            # 2. Extract and truncate context
            context_chunks = [result["content"] for result in search_results["results"]]
            context = "\n\n".join(context_chunks)
            context = _token_trim(context, self.ctx_limit)

            if not context.strip():
                return {
                    "status": "no_results",
                    "message": "No relevant information found in knowledge base",
                    "question": question,
                    "latency_ms": int((time.time() - start) * 1000),
                }

            # 3. Generate answer using Mistral with system prompt
            prompt = (
                f"You are an accurate assistant. Answer **ONLY** from context.\n\n"
                f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
            )

            answer = self.llm(prompt)

            # 4. Return results with performance metrics
            resp = {
                "status": "success",
                "question": question,
                "answer": answer,
                "context_chunks": len(context_chunks),
                "sources": [result["document_id"] for result in search_results["results"]],
                "latency_ms": int((time.time() - start) * 1000),
            }

            # Cache the result
            _lru_cached_answer.cache[cache_key] = resp  # type: ignore
            return resp

        except ValueError as e:
            # Handle sanitization errors
            return {"status": "error", "error": f"Invalid input: {str(e)}", "question": question}
        except Exception as e:
            _LOG.error("RAG system error: %s", e, exc_info=True)
            return {"status": "error", "error": str(e), "question": question}

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.vector_store.get_stats()


class RAGQueryInterface:
    """Simple interface for querying the RAG system"""

    def __init__(self, db_connection_string: str, mistral_url: str = "http://localhost:11434"):
        self.rag_system = RAGSystem(db_connection_string, mistral_url)

    def ask(self, question: str) -> Dict[str, Any]:
        """Ask a question and get an answer"""
        return self.rag_system.forward(question)

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.rag_system.get_stats()


def create_rag_interface(
    db_url: Optional[str] = None, mistral_url: str = "http://localhost:11434"
) -> RAGQueryInterface:
    """Create a RAG query interface"""

    if db_url is None:
        # Try to get from environment
        db_url = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")

    return RAGQueryInterface(db_url, mistral_url)


if __name__ == "__main__":
    # Test the RAG system
    import sys

    sys.path.append("src")

    # Create interface
    rag = create_rag_interface()

    # Test question
    question = "What documents have been processed?"
    result = rag.ask(question)

    print(f"Question: {question}")
    print(f"Status: {result['status']}")
    if result["status"] == "success":
        print(f"Answer: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print(f"Latency: {result.get('latency_ms', 'N/A')}ms")
    else:
        print(f"Error: {result.get('error', result.get('message', 'Unknown error'))}")
