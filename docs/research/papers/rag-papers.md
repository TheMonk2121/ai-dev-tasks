<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->

# RAG Research Papers

<a id="tldr"></a>

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of RAG Research Papers.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.


> **External Research**: Academic papers and research sources for RAG (Retrieval-Augmented Generation) systems.

## 📚 **Papers**

### **"Searching for Best Practices in RAG" (ACL 2024)**

- **Authors**: ACL 2024 Research Team

- **Key Insight**: Hybrid search (dense + sparse) significantly improves RAG performance

- **Application**: Informs our hybrid search implementation with PGVector + PostgreSQL full-text

- **Citation**: [Full citation to be added]

- **Key Findings**:
  - Relying solely on vector similarity can miss exact matches or rare terms
  - Combined dense vectors (semantic recall) + sparse search (BM25/keyword) for precise matches
  - Significantly improves real-world QA recall compared to pure vector search
  - Many vector DBs (like Qdrant) added BM25 in 2024

### **Microsoft GraphRAG (2024)**

- **Authors**: Microsoft Research

- **Key Insight**: Knowledge graphs can augment traditional RAG for complex reasoning

- **Application**: Guides our knowledge graph integration approach

- **Citation**: [Full citation to be added]

- **Key Findings**:
  - Use LLMs to build knowledge graphs from document corpus
  - Multi-hop reasoning through relationships that pure vector search misses
  - Integrate structured and unstructured information
  - Handle queries requiring connecting disparate facts

### **KAG: Knowledge-Augmented Generation (2024)**

- **Authors**: [Research Team]

- **Key Insight**: Advanced knowledge integration techniques

- **Application**: Guides our knowledge integration approach

- **Citation**: [Full citation to be added]

## 🔗 **Related Documentation**

- `500_rag-system-research.md` - Our internal RAG research summary

- `400_system-overview_advanced_features.md` - System architecture overview

- `dspy-rag-system/` - Our RAG implementation

## 📖 **Key Insights**

- Hybrid retrieval is essential for optimal performance

- Span-level grounding improves citation accuracy

- Multi-stage retrieval helps with complex queries

- Knowledge graphs enhance reasoning capabilities

- Intelligent chunking strategies significantly impact results

## 🎯 **Implementation Impact**

This research directly informs our RAG system design and implementation choices.