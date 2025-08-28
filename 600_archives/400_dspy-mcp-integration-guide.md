# DSPy Integration Guide

> DEPRECATED: Content integrated into core guides — see `400_guides/400_07_ai-frameworks-dspy.md` (DSPy modules/signatures/patterns), `400_guides/400_08_integrations-editor-and-models.md` (editor/model integrations, MCP-style pipelines), `400_guides/400_09_automation-and-pipelines.md` (CLI/CI wiring), and `400_guides/400_11_deployments-ops-and-observability.md` (metrics/monitoring). Use `400_00_getting-started-and-index.md` for navigation. Implementation lives under `dspy-rag-system/src/`.

## Overview

This guide demonstrates how to integrate the MCP (Model Context Protocol) document processing system with DSPy workflows for advanced RAG (Retrieval-Augmented Generation) applications.

## Quick Start

### Basic Integration

```python
import dspy
from dspy_modules.mcp_document_processor import MCPDocumentProcessor

# Initialize MCP processor
processor = MCPDocumentProcessor()

# Create DSPy signature for document analysis
class DocumentAnalysisSignature(dspy.Signature):
    """Analyze document content and extract insights."""

    document_source = dspy.InputField(desc="Source of the document")
    document_content = dspy.InputField(desc="Content of the document")

    key_insights = dspy.OutputField(desc="Key insights from the document")
    summary = dspy.OutputField(desc="Brief summary")
    recommendations = dspy.OutputField(desc="Recommendations based on content")

# Create DSPy module
class DocumentAnalysisModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.processor = MCPDocumentProcessor()
        self.analyzer = dspy.ChainOfThought("document_analysis")

    def forward(self, document_source):
        # Process document using MCP
        document = await self.processor.process_document(document_source)

        # Analyze with DSPy
        analysis = self.analyzer(
            document_source=document_source,
            document_content=document.content
        )

        return analysis

# Usage
module = DocumentAnalysisModule()
result = await module.forward("https://example.com/article")
```

### Multi-Source Processing

```python
from dspy_modules.standardized_pipeline import StandardizedIngestionPipeline

# Initialize pipeline
pipeline = StandardizedIngestionPipeline(
    pipeline_id="multi_source_analysis",
    vector_store=vector_store
)

# Process multiple document sources
sources = [
    "file:///path/to/local/document.pdf",
    "https://example.com/article",
    "https://github.com/user/repo",
    "sqlite:///path/to/database.db"
]

# Process and analyze
results = await pipeline.forward(sources)

# Access results
for result in results:
    print(f"Source: {result.metadata.source}")
    print(f"Content length: {len(result.content)}")
    print(f"Success: {result.success}")
```

## Advanced Workflows

### Document Comparison

```python
class DocumentComparisonSignature(dspy.Signature):
    """Compare multiple documents and identify differences."""

    document1_content = dspy.InputField(desc="Content of first document")
    document2_content = dspy.InputField(desc="Content of second document")

    similarities = dspy.OutputField(desc="Key similarities between documents")
    differences = dspy.OutputField(desc="Key differences between documents")
    recommendations = dspy.OutputField(desc="Recommendations for alignment")

class DocumentComparisonModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.processor = MCPDocumentProcessor()
        self.comparator = dspy.ChainOfThought("document_comparison")

    def forward(self, source1, source2):
        # Process both documents
        doc1 = await self.processor.process_document(source1)
        doc2 = await self.processor.process_document(source2)

        # Compare with DSPy
        comparison = self.comparator(
            document1_content=doc1.content,
            document2_content=doc2.content
        )

        return comparison

# Usage
comparator = DocumentComparisonModule()
result = await comparator.forward(
    "https://example.com/doc1",
    "https://example.com/doc2"
)
```

### Content Summarization Pipeline

```python
class ContentSummarizationSignature(dspy.Signature):
    """Summarize document content with key points."""

    document_content = dspy.InputField(desc="Document content to summarize")
    summary_length = dspy.InputField(desc="Desired summary length (short/medium/long)")

    summary = dspy.OutputField(desc="Document summary")
    key_points = dspy.OutputField(desc="Key points from the document")
    action_items = dspy.OutputField(desc="Action items identified")

class ContentSummarizationPipeline:
    def __init__(self):
        self.processor = MCPDocumentProcessor()
        self.summarizer = dspy.ChainOfThought("content_summarization")

    async def summarize_documents(self, sources, summary_length="medium"):
        results = []

        for source in sources:
            # Process document
            document = await self.processor.process_document(source)

            # Summarize with DSPy
            summary = self.summarizer(
                document_content=document.content,
                summary_length=summary_length
            )

            results.append({
                "source": source,
                "metadata": document.metadata,
                "summary": summary
            })

        return results

# Usage
pipeline = ContentSummarizationPipeline()
summaries = await pipeline.summarize_documents([
    "https://example.com/article1",
    "https://example.com/article2"
])
```

### Knowledge Base Construction

```python
from dspy_modules.mcp_document_processor import MCPDocumentIngestionPipeline

class KnowledgeBaseBuilder:
    def __init__(self, vector_store):
        self.pipeline = MCPDocumentIngestionPipeline(vector_store=vector_store)
        self.processor = MCPDocumentProcessor()

    async def build_knowledge_base(self, sources):
        """Build a knowledge base from multiple sources."""

        # Process and ingest documents
        result = await self.pipeline.process_and_ingest(sources)

        print(f"Processed {result.total_documents} documents")
        print(f"Successfully ingested {result.successful_ingestions} documents")

        return result

    async def query_knowledge_base(self, query, top_k=5):
        """Query the knowledge base."""
        results = await self.vector_store.search(query, top_k=top_k)
        return results

# Usage
vector_store = VectorStore()
kb_builder = KnowledgeBaseBuilder(vector_store)

# Build knowledge base
sources = [
    "file:///path/to/documents/",
    "https://example.com/docs",
    "https://github.com/user/repo"
]

await kb_builder.build_knowledge_base(sources)

# Query knowledge base
results = await kb_builder.query_knowledge_base("machine learning algorithms")
```

## Error Handling and Resilience

### Robust Document Processing

```python
import asyncio
from utils.mcp_integration import MCPError

class RobustDocumentProcessor:
    def __init__(self):
        self.processor = MCPDocumentProcessor()

    async def process_with_fallback(self, sources, max_retries=3):
        """Process documents with retry logic and fallback handling."""

        results = []
        failed_sources = []

        for source in sources:
            for attempt in range(max_retries):
                try:
                    result = await self.processor.process_document(source)
                    results.append(result)
                    print(f"✅ Successfully processed: {source}")
                    break

                except MCPError as e:
                    if attempt == max_retries - 1:
                        print(f"❌ Failed to process {source}: {e}")
                        failed_sources.append(source)
                    else:
                        print(f"⚠️  Retry {attempt + 1} for {source}: {e}")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff

                except Exception as e:
                    print(f"❌ Unexpected error processing {source}: {e}")
                    failed_sources.append(source)
                    break

        return results, failed_sources

# Usage
robust_processor = RobustDocumentProcessor()
results, failed = await robust_processor.process_with_fallback([
    "https://example.com/valid",
    "https://invalid-url.com",
    "https://example.com/another-valid"
])
```

## Performance Optimization

### Batch Processing

```python
class BatchDocumentProcessor:
    def __init__(self, batch_size=10):
        self.processor = MCPDocumentProcessor()
        self.batch_size = batch_size

    async def process_in_batches(self, sources):
        """Process documents in batches for better performance."""

        all_results = []

        for i in range(0, len(sources), self.batch_size):
            batch = sources[i:i + self.batch_size]
            print(f"Processing batch {i//self.batch_size + 1} ({len(batch)} documents)")

            # Process batch concurrently
            tasks = [self.processor.process_document(source) for source in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    print(f"❌ Error processing {batch[j]}: {result}")
                else:
                    all_results.append(result)
                    print(f"✅ Processed {batch[j]}")

        return all_results

# Usage
batch_processor = BatchDocumentProcessor(batch_size=5)
results = await batch_processor.process_in_batches([
    f"document_{i}.pdf" for i in range(20)
])
```

### Caching and Optimization

```python
import hashlib
import json
from functools import lru_cache

class OptimizedDocumentProcessor:
    def __init__(self):
        self.processor = MCPDocumentProcessor()
        self.cache = {}

    def _get_cache_key(self, source, config):
        """Generate cache key for document source and configuration."""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(f"{source}:{config_str}".encode()).hexdigest()

    async def process_with_caching(self, source, config=None, use_cache=True):
        """Process document with optional caching."""

        if config is None:
            config = {}

        cache_key = self._get_cache_key(source, config)

        if use_cache and cache_key in self.cache:
            print(f"📋 Using cached result for {source}")
            return self.cache[cache_key]

        # Process document
        result = await self.processor.process_document(source)

        if use_cache:
            self.cache[cache_key] = result
            print(f"💾 Cached result for {source}")

        return result

# Usage
optimized_processor = OptimizedDocumentProcessor()

# First call - processes and caches
result1 = await optimized_processor.process_with_caching("https://example.com/article")

# Second call - uses cache
result2 = await optimized_processor.process_with_caching("https://example.com/article")
```

## Integration with Vector Stores

### Advanced Vector Store Integration

```python
class AdvancedVectorStoreIntegration:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.pipeline = MCPDocumentIngestionPipeline(vector_store=vector_store)

    async def smart_ingestion(self, sources, chunk_size=1000, overlap=200):
        """Smart document ingestion with chunking and metadata."""

        for source in sources:
            try:
                # Process document
                document = await self.pipeline.processor.process_document(source)

                # Create chunks with metadata
                chunks = self._create_chunks(document.content, chunk_size, overlap)

                # Ingest chunks with enhanced metadata
                for i, chunk in enumerate(chunks):
                    enhanced_metadata = {
                        **document.metadata.__dict__,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk),
                        "source_chunk": chunk[:100] + "..." if len(chunk) > 100 else chunk
                    }

                    await self.vector_store.add_document(
                        content=chunk,
                        metadata=enhanced_metadata
                    )

                print(f"✅ Ingested {len(chunks)} chunks from {source}")

            except Exception as e:
                print(f"❌ Failed to ingest {source}: {e}")

    def _create_chunks(self, content, chunk_size, overlap):
        """Create overlapping chunks from content."""
        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start = end - overlap

        return chunks

    async def semantic_search(self, query, filters=None, top_k=10):
        """Perform semantic search with filtering."""

        search_params = {
            "query": query,
            "top_k": top_k
        }

        if filters:
            search_params["filters"] = filters

        results = await self.vector_store.search(**search_params)
        return results

# Usage
vector_store = VectorStore()
advanced_integration = AdvancedVectorStoreIntegration(vector_store)

# Smart ingestion
sources = [
    "https://example.com/long-article",
    "file:///path/to/large-document.pdf"
]

await advanced_integration.smart_ingestion(sources, chunk_size=500, overlap=50)

# Semantic search with filtering
results = await advanced_integration.semantic_search(
    query="machine learning",
    filters={"content_type": "application/pdf"},
    top_k=5
)
```

## Best Practices

### 1. Resource Management

```python
class ResourceManagedProcessor:
    def __init__(self):
        self.processor = None

    async def __aenter__(self):
        self.processor = MCPDocumentProcessor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.processor:
            await self.processor.cleanup()

# Usage with context manager
async with ResourceManagedProcessor() as processor:
    result = await processor.processor.process_document("https://example.com/article")
```

### 2. Configuration Management

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ProcessingConfig:
    max_file_size: int = 50 * 1024 * 1024
    timeout: int = 30
    retry_attempts: int = 3
    enable_caching: bool = True
    chunk_size: int = 1000
    overlap: int = 200

class ConfigurableProcessor:
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.processor = MCPDocumentProcessor()

    async def process_with_config(self, source):
        # Apply configuration
        # ... implementation details
        pass
```

### 3. Monitoring and Logging

```python
import logging
import time
from typing import List

class MonitoredProcessor:
    def __init__(self):
        self.processor = MCPDocumentProcessor()
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "processed_documents": 0,
            "failed_documents": 0,
            "total_processing_time": 0
        }

    async def process_with_monitoring(self, sources: List[str]):
        start_time = time.time()

        for source in sources:
            try:
                doc_start = time.time()
                result = await self.processor.process_document(source)
                doc_time = time.time() - doc_start

                self.metrics["processed_documents"] += 1
                self.metrics["total_processing_time"] += doc_time

                self.logger.info(f"Processed {source} in {doc_time:.2f}s")

            except Exception as e:
                self.metrics["failed_documents"] += 1
                self.logger.error(f"Failed to process {source}: {e}")

        total_time = time.time() - start_time
        self.logger.info(f"Processing complete: {self.metrics}")

        return self.metrics
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Memory Issues**: Use batch processing and cleanup resources
3. **Network Timeouts**: Implement retry logic with exponential backoff
4. **Rate Limiting**: Add delays between requests for external APIs

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Monitor specific components
logging.getLogger('utils.mcp_integration').setLevel(logging.DEBUG)
logging.getLogger('dspy_modules').setLevel(logging.DEBUG)
```

This integration guide provides a comprehensive foundation for building robust DSPy workflows with MCP document processing capabilities.
