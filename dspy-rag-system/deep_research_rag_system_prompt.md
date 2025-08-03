# Deep Research Analysis Request: RAG System Module

## 🎯 **CRITICAL REQUEST: Provide Test Code for Your Improvements**

For **EVERY improvement or fix you suggest**, please provide:

### **1. Complete Test Code**
- **Unit tests** for each method you modify or add
- **Integration tests** for RAG workflow and Mistral integration
- **Performance tests** for any optimizations
- **Security tests** for any security improvements
- **Resilience tests** for error handling improvements

### **2. Test Code Requirements**
- **Complete and runnable** test code
- **Proper setup and teardown** for database and Ollama tests
- **Mock implementations** where appropriate
- **Performance benchmarks** with measurement code
- **Security test cases** with vulnerability checks
- **Edge case coverage** for all scenarios

### **3. Example Test Structure**
```python
# For each improvement you suggest, provide:
def test_your_improvement():
    """Test the specific improvement you suggested"""
    # Setup
    # Test implementation
    # Assertions
    # Cleanup
```

## **Our Development Environment & Tools**

### **Core Stack:**
- **Python 3.9** (not 3.10+ for compatibility)
- **DSPy 2.4.6** for AI orchestration
- **PostgreSQL** with pgvector extension
- **Ollama** running Mistral-7B locally
- **Flask** for web dashboard
- **n8n** for workflow automation

### **Current Infrastructure:**
- **Database**: `postgresql://ai_user:ai_password@localhost:5432/ai_agency`
- **Ollama**: `http://localhost:11434` (Mistral-7B model)
- **File System**: Local file processing with watch folder
- **Logging**: Structured JSON logging with rotation

### **Testing Framework:**
- **pytest** for test execution
- **psycopg2** for database testing
- **requests** for HTTP testing
- **unittest.mock** for mocking

### **Recent Improvements Made:**
- **VectorStore**: Connection pooling, bulk inserts, UUID document IDs, pgvector adapter
- **DocumentProcessor**: Token-aware chunking, PyMuPDF, structured logging, security validation
- **Metadata**: Config-driven extraction with scoring and categorization

## **Code to Analyze: RAG System Module**

```python
#!/usr/bin/env python3
"""
DSPy RAG System
Complete RAG system using DSPy with Mistral integration.
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
import dspy
from dspy import Module, Signature, InputField, OutputField
import requests
from .vector_store import VectorStore


class MistralLLM(dspy.Module):
    """DSPy module for Mistral via Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        super().__init__()
        self.base_url = base_url
        self.model = model
    
    def forward(self, prompt: str) -> str:
        """Generate response using Mistral via Ollama"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error connecting to Mistral: {str(e)}"


class RAGSignature(Signature):
    """Signature for RAG question answering"""
    
    question = InputField(desc="The question to answer")
    context = InputField(desc="Relevant context from knowledge base")
    answer = OutputField(desc="The answer based on the context")


class RAGSystem(Module):
    """Complete DSPy RAG system with Mistral integration"""
    
    def __init__(self, db_connection_string: str, mistral_url: str = "http://localhost:11434"):
        super().__init__()
        
        # Initialize components
        self.vector_store = VectorStore(db_connection_string)
        self.llm = MistralLLM(mistral_url)
        
        # Create DSPy predictor
        self.predictor = dspy.Predict(RAGSignature)
    
    def forward(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """Answer a question using RAG system"""
        
        try:
            # 1. Search for relevant context
            search_results = self.vector_store("search", query=question, limit=max_results)
            
            if search_results["status"] != "success":
                return {
                    "status": "error",
                    "error": f"Search failed: {search_results.get('error', 'Unknown error')}"
                }
            
            # 2. Extract context from search results
            context_chunks = []
            for result in search_results["results"]:
                context_chunks.append(result["content"])
            
            context = "\n\n".join(context_chunks)
            
            if not context.strip():
                return {
                    "status": "no_results",
                    "message": "No relevant information found in knowledge base",
                    "question": question
                }
            
            # 3. Generate answer using Mistral
            prompt = f"""Based on the following context, answer the question. If the context doesn't contain enough information to answer the question, say so.

Context:
{context}

Question: {question}

Answer:"""
            
            answer = self.llm(prompt)
            
            # 4. Return results
            return {
                "status": "success",
                "question": question,
                "answer": answer,
                "context_chunks": len(context_chunks),
                "sources": [result["document_id"] for result in search_results["results"]]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "question": question
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.vector_store.get_stats()


class RAGQueryInterface:
    """Simple interface for querying the RAG system"""
    
    def __init__(self, db_connection_string: str, mistral_url: str = "http://localhost:11434"):
        self.rag_system = RAGSystem(db_connection_string, mistral_url)
    
    def ask(self, question: str) -> Dict[str, Any]:
        """Ask a question and get an answer"""
        return self.rag_system(question)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.rag_system.get_stats()


def create_rag_interface(db_url: str = None, mistral_url: str = "http://localhost:11434") -> RAGQueryInterface:
    """Create a RAG query interface"""
    
    if db_url is None:
        # Try to get from environment
        db_url = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")
    
    return RAGQueryInterface(db_url, mistral_url)


if __name__ == "__main__":
    # Test the RAG system
    import sys
    sys.path.append('src')
    
    # Create interface
    rag = create_rag_interface()
    
    # Test question
    question = "What documents have been processed?"
    result = rag.ask(question)
    
    print(f"Question: {question}")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Answer: {result['answer']}")
        print(f"Sources: {result['sources']}")
    else:
        print(f"Error: {result.get('error', result.get('message', 'Unknown error'))}")
```

## **Analysis Requirements**

### **1. Critical Issues to Identify:**
- **Performance bottlenecks** in RAG workflow
- **Error handling gaps** in Mistral integration
- **Security vulnerabilities** in prompt injection
- **Memory management** issues with large contexts
- **Connection management** for Ollama API
- **Prompt engineering** improvements
- **Context window** optimization
- **Response quality** and hallucination prevention

### **2. Production Readiness Issues:**
- **Timeout handling** for long-running queries
- **Rate limiting** for Ollama API calls
- **Caching strategies** for repeated queries
- **Monitoring and observability** gaps
- **Resource cleanup** and memory leaks
- **Concurrent request** handling
- **Fallback mechanisms** when services are unavailable

### **3. Integration Issues:**
- **DSPy signature** optimization
- **Vector store** integration efficiency
- **Error propagation** between components
- **Data flow** optimization
- **Response format** consistency

## **Specific Areas for Deep Research:**

### **🔴 Critical Priority:**
1. **Ollama API Integration**: Connection pooling, retry logic, error handling
2. **Prompt Engineering**: Context window management, hallucination prevention
3. **Performance Optimization**: Caching, batching, async operations
4. **Security**: Prompt injection prevention, input sanitization

### **🟠 High Priority:**
1. **DSPy Integration**: Signature optimization, memory management
2. **Error Handling**: Comprehensive error recovery and fallbacks
3. **Monitoring**: Request tracking, performance metrics, health checks
4. **Resource Management**: Memory cleanup, connection management

### **🟡 Medium Priority:**
1. **Response Quality**: Answer validation, confidence scoring
2. **Context Optimization**: Relevance ranking, context truncation
3. **Caching Strategy**: Query result caching, embedding caching
4. **Async Operations**: Non-blocking request handling

## **Testing Context Requirements:**

### **Database Testing:**
- Use `postgresql://ai_user:ai_password@localhost:5432/ai_agency`
- Test with pgvector extension enabled
- Include proper setup/teardown for test data

### **Ollama Testing:**
- Mock Ollama API responses for unit tests
- Test with real Ollama instance for integration tests
- Handle connection failures and timeouts

### **Performance Testing:**
- Test with large context windows (10K+ tokens)
- Measure response times and memory usage
- Test concurrent request handling

### **Security Testing:**
- Test prompt injection attempts
- Validate input sanitization
- Test rate limiting and abuse prevention

## **Expected Output Format:**

### **1. Severity-Ranked Issues**
```
🔴 Critical: [Issue description] - [Impact] - Fix: [Solution]
🟠 High: [Issue description] - [Impact] - Fix: [Solution]
🟡 Medium: [Issue description] - [Impact] - Fix: [Solution]
🟢 Low: [Issue description] - [Impact] - Fix: [Solution]
```

### **2. Complete Code Improvements**
- **Patched code** with all fixes implemented
- **New methods/classes** with complete implementations
- **Configuration updates** if needed
- **Dependency updates** if required

### **3. Comprehensive Test Suite**
- **Unit tests** for each improvement
- **Integration tests** for RAG workflow
- **Performance tests** with benchmarks
- **Security tests** for vulnerabilities
- **Resilience tests** for error scenarios
- **Mock implementations** for external dependencies

### **4. Production Deployment Guide**
- **Environment variables** configuration
- **Database migrations** if needed
- **Monitoring setup** instructions
- **Performance tuning** recommendations

## **Special Emphasis:**

**For EVERY improvement you suggest, you MUST provide the complete test code to validate that improvement works correctly.**

This ensures we can immediately implement and test your suggestions with confidence.

## **Context Integration:**

The RAG System integrates with:
- **VectorStore** (already optimized with connection pooling, bulk inserts, UUIDs)
- **DocumentProcessor** (already optimized with token-aware chunking, PyMuPDF)
- **PostgreSQL** with pgvector extension
- **Ollama** running Mistral-7B locally
- **DSPy** for AI orchestration and memory management

Please analyze this RAG System module and provide comprehensive improvements with complete test code for each suggestion. 