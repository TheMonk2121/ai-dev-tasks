<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: B-011-DEPLOYMENT-GUIDE_production_deployment.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_integration-patterns-guide.md -->

# RAG Tutorials

> **External Research**: Tutorials and guides for RAG system implementation.

## 📚 **Tutorials**

### **Hybrid Search Implementation**
- **Source**: Industry Best Practices
- **Key Insight**: Combining dense and sparse retrieval methods
- **Application**: Guides our hybrid search implementation
- **Link**: [To be added]
- **Implementation Steps**:
  - Add PostgreSQL full-text search alongside PGVector
  - Implement result merging with weighting heuristics
  - Use three-digit prefix system for semantic chunking
  - Enable hybrid search for all RAG operations

### **Multi-stage Retrieval**
- **Source**: Research Best Practices
- **Key Insight**: Query decomposition and iterative refinement
- **Application**: Guides our complex query handling
- **Link**: [To be added]
- **Implementation Steps**:
  - Break complex questions into sub-questions
  - Generate related terms for expanded retrieval
  - Enable "Find X then using that find Y" queries
  - Allow agents to refine queries based on initial results

### **Span-level Grounding**
- **Source**: LangExtract Documentation (2025)
- **Key Insight**: Character offset tracking and citation
- **Application**: Informs our extraction and citation system
- **Link**: [To be added]
- **Implementation Steps**:
  - Store character offsets in vector metadata
  - Implement span-level citations in answers
  - Enable precise source attribution
  - Add validation against original text

### **DSPy RAG Integration**
- **Source**: DSPy Documentation
- **Key Insight**: Multi-step and async chains for RAG implementation
- **Application**: Guides our DSPy RAG integration
- **Link**: [To be added]
- **Implementation Steps**:
  - Integrate retrieval calls with LLM calls in loops
  - Run external calls (DB queries, API calls) as needed
  - Structure long workflows as DSPy modules
  - Enable parallel execution for independent modules

## 🔗 **Related Documentation**
- `500_rag-system-research.md` - Our internal RAG research summary
- `104_dspy-development-context.md` - Our DSPy implementation

## 📖 **Key Insights**
- Step-by-step implementation guides
- Best practices for production deployment
- Integration patterns and examples
- Hybrid search implementation patterns
- Multi-stage retrieval techniques

## 🎯 **Implementation Impact**
These tutorials provide practical implementation guidance for our RAG system.
