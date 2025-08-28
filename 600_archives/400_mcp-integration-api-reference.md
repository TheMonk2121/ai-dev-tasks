# MCP Integration API Reference

> DEPRECATED: Content integrated into core guides — see `400_guides/400_07_ai-frameworks-dspy.md` (DSPy integrations/patterns), `400_guides/400_08_integrations-editor-and-models.md` (MCP-style pipelines, editor/model integrations), `400_guides/400_09_automation-and-pipelines.md` (CLI/CI wiring, performance tuning), `400_guides/400_11_deployments-ops-and-observability.md` (monitoring/metrics), and `400_guides/400_00_getting-started-and-index.md` (index). Implementation lives under `dspy-rag-system/src/` and `dspy-rag-system/src/utils/mcp_integration/`.

## Overview

The MCP (Model Context Protocol) Integration system provides a comprehensive framework for document processing across multiple sources and formats. This system extends the DSPy RAG capabilities with standardized document ingestion, processing, and integration.

## Table of Contents

1. [Core Components](#core-components)
2. [MCP Servers](#mcp-servers)
3. [DSPy Integration](#dspy-integration)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Error Handling](#error-handling)
7. [Performance Tuning](#performance-tuning)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

## Core Components

### Base Classes

#### `MCPServer`
Base class for all MCP servers providing document processing capabilities.

```python
from utils.mcp_integration import MCPServer, MCPConfig

class CustomMCPServer(MCPServer):
    def __init__(self, config: MCPConfig):
        super().__init__(config)

    def validate_source(self, source: str) -> bool:
        """Validate if source is supported by this server."""
        pass

    async def process_document(self, source: str) -> ProcessedDocument:
        """Process document from source."""
        pass

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        pass

    async def cleanup(self) -> None:
        """Cleanup resources."""
        pass
```

#### `MCPConfig`
Configuration class for MCP servers.

```python
from utils.mcp_integration import MCPConfig

config = MCPConfig(
    server_name="my_server",
    server_version="1.0.0",
    max_file_size=50 * 1024 * 1024,  # 50MB
    timeout=30,
    retry_attempts=3
)
```

#### `DocumentMetadata`
Metadata structure for processed documents.

```python
from utils.mcp_integration import DocumentMetadata

metadata = DocumentMetadata(
    source="file:///path/to/document.pdf",
    content_type="application/pdf",
    size=1024,
    created_at="2025-08-25T10:00:00",
    title="Document Title",
    author="Author Name",
    language="en",
    word_count=500,
    page_count=10,
    processing_time=1.5
)
```

#### `ProcessedDocument`
Result structure for processed documents.

```python
from utils.mcp_integration import ProcessedDocument

document = ProcessedDocument(
    content="Extracted text content...",
    metadata=metadata,
    success=True
)
```

## MCP Servers

### File System Server

Processes local files and directories.

```python
from utils.mcp_integration import FileSystemMCPServer, MCPConfig

config = MCPConfig(server_name="file_system_server")
server = FileSystemMCPServer(config)

# Process a single file
document = await server.process_document("/path/to/document.txt")

# Process a directory
document = await server.process_document("/path/to/documents/")

# Validate source
is_valid = server.validate_source("/path/to/file.pdf")  # True
is_valid = server.validate_source("https://example.com")  # False
```

**Supported Formats:**
- Text files (.txt, .md, .py, .js, etc.)
- Configuration files (.json, .yaml, .toml, .ini)
- Log files (.log)
- Code files (.py, .js, .ts, .java, .cpp, etc.)

### Web Server

Processes web content including HTML pages and RSS feeds.

```python
from utils.mcp_integration import WebMCPServer, MCPConfig

config = MCPConfig(server_name="web_server")
server = WebMCPServer(config)

# Process a web page
document = await server.process_document("https://example.com/article")

# Process an RSS feed
document = await server.process_document("https://example.com/feed.xml")

# Validate source
is_valid = server.validate_source("https://example.com")  # True
is_valid = server.validate_source("ftp://example.com")  # False
```

**Supported Formats:**
- HTML pages
- RSS/Atom feeds
- XML documents
- JSON APIs (with content-type headers)

### PDF Server

Processes PDF documents with text extraction and metadata.

```python
from utils.mcp_integration import PDFMCPServer, MCPConfig

config = MCPConfig(server_name="pdf_server")
server = PDFMCPServer(config)

# Process a local PDF
document = await server.process_document("/path/to/document.pdf")

# Process a PDF from URL
document = await server.process_document("https://example.com/document.pdf")

# Validate source
is_valid = server.validate_source("document.pdf")  # True
is_valid = server.validate_source("document.txt")  # False
```

**Features:**
- Text extraction with formatting preservation
- Metadata extraction (title, author, creation date)
- Page-by-page processing
- OCR support (when available)

### GitHub Server

Processes GitHub repositories, issues, and pull requests.

```python
from utils.mcp_integration import GitHubMCPServer, MCPConfig

config = MCPConfig(
    server_name="github_server",
    github_token="your_github_token"  # Optional
)
server = GitHubMCPServer(config)

# Process a repository
document = await server.process_document("https://github.com/user/repo")

# Process an issue
document = await server.process_document("https://github.com/user/repo/issues/123")

# Process a pull request
document = await server.process_document("https://github.com/user/repo/pull/456")

# Validate source
is_valid = server.validate_source("https://github.com/user/repo")  # True
is_valid = server.validate_source("https://gitlab.com/user/repo")  # False
```

**Features:**
- Repository content processing
- Issue and PR discussion extraction
- README and documentation processing
- Code file analysis
- Rate limiting and authentication

### Database Server

Processes database content including schemas and query results.

```python
from utils.mcp_integration import DatabaseMCPServer, MCPConfig

config = MCPConfig(
    server_name="database_server",
    database_url="sqlite:///path/to/database.db"
)
server = DatabaseMCPServer(config)

# Process database schema
document = await server.process_document("sqlite:///path/to/database.db")

# Execute and process query
result = await server.execute_query("SELECT * FROM users LIMIT 10")

# Export data
exported = await server.export_data("users", format="json")

# Validate source
is_valid = server.validate_source("sqlite:///database.db")  # True
is_valid = server.validate_source("postgresql://user:pass@host/db")  # True
is_valid = server.validate_source("https://example.com")  # False
```

**Supported Databases:**
- SQLite
- PostgreSQL (planned)
- MySQL (planned)

**Features:**
- Schema extraction and documentation
- Query execution and result processing
- Data export in multiple formats
- SQL injection protection

### Office Server

Processes Microsoft Office documents (Word, Excel, PowerPoint).

```python
from utils.mcp_integration import OfficeMCPServer, MCPConfig

config = MCPConfig(server_name="office_server")
server = OfficeMCPServer(config)

# Process Word document
document = await server.process_document("/path/to/document.docx")

# Process Excel spreadsheet
document = await server.process_document("/path/to/spreadsheet.xlsx")

# Process PowerPoint presentation
document = await server.process_document("/path/to/presentation.pptx")

# Validate source
is_valid = server.validate_source("document.docx")  # True
is_valid = server.validate_source("document.txt")  # False
```

**Supported Formats:**
- Word documents (.docx, .doc)
- Excel spreadsheets (.xlsx, .xls)
- PowerPoint presentations (.pptx, .ppt)

**Features:**
- Text extraction with formatting
- Table and structure preservation
- Metadata extraction (author, title, dates)
- Corrupted file handling

## DSPy Integration

### MCPDocumentProcessor

Main processor for integrating MCP servers with DSPy workflows.

```python
from dspy_modules.mcp_document_processor import MCPDocumentProcessor
from utils.mcp_integration import MCPConfig

# Initialize processor with all available servers
processor = MCPDocumentProcessor()

# Process a document (automatically routes to appropriate server)
result = await processor.process_document("https://example.com/article")

# Process multiple documents
documents = [
    "file:///path/to/document.pdf",
    "https://github.com/user/repo",
    "sqlite:///path/to/database.db"
]
results = await processor.process_documents(documents)

# Get processing statistics
stats = processor.get_processing_stats()
print(f"Processed {stats['total_documents']} documents")
print(f"Success rate: {stats['success_rate']:.2%}")

# Cleanup resources
await processor.cleanup()
```

### MCPDocumentIngestionPipeline

Complete pipeline for document ingestion with vector store integration.

```python
from dspy_modules.mcp_document_processor import MCPDocumentIngestionPipeline
from utils.vector_store import VectorStore

# Initialize pipeline with vector store
vector_store = VectorStore()
pipeline = MCPDocumentIngestionPipeline(vector_store=vector_store)

# Process and ingest documents
documents = [
    "file:///path/to/documents/",
    "https://example.com/docs",
    "https://github.com/user/repo"
]

result = await pipeline.process_and_ingest(documents)

print(f"Processed {result.total_documents} documents")
print(f"Successfully ingested {result.successful_ingestions} documents")
print(f"Processing time: {result.elapsed_time:.2f} seconds")

# Cleanup
await pipeline.cleanup()
```

### StandardizedIngestionPipeline

High-level pipeline for standardized document processing workflows.

```python
from dspy_modules.standardized_pipeline import StandardizedIngestionPipeline

# Initialize pipeline
pipeline = StandardizedIngestionPipeline(
    pipeline_id="my_pipeline",
    vector_store=vector_store
)

# Process single document
result = await pipeline.forward("https://example.com/article")

# Process multiple documents
documents = ["doc1.pdf", "doc2.docx", "doc3.html"]
result = await pipeline.forward(documents)

# Get pipeline progress
progress = pipeline.get_progress()
print(f"Progress: {progress.completed}/{progress.total} documents")

# Get pipeline statistics
stats = pipeline.get_statistics()
print(f"Average processing time: {stats.avg_processing_time:.2f}s")
```

## Configuration

### Server Configuration

Each MCP server can be configured with specific settings:

```python
from utils.mcp_integration import MCPConfig

# File System Server
file_config = MCPConfig(
    server_name="file_system",
    max_file_size=100 * 1024 * 1024,  # 100MB
    supported_extensions=[".txt", ".md", ".py", ".json"]
)

# Web Server
web_config = MCPConfig(
    server_name="web_server",
    timeout=60,
    max_redirects=5,
    user_agent="MyBot/1.0"
)

# PDF Server
pdf_config = MCPConfig(
    server_name="pdf_server",
    max_file_size=50 * 1024 * 1024,  # 50MB
    extract_images=True,
    ocr_enabled=True
)

# GitHub Server
github_config = MCPConfig(
    server_name="github_server",
    github_token="your_token",
    rate_limit_per_hour=5000,
    max_file_size=10 * 1024 * 1024  # 10MB
)

# Database Server
db_config = MCPConfig(
    server_name="database_server",
    database_url="postgresql://user:pass@host/db",
    max_query_time=30,
    max_result_rows=10000
)

# Office Server
office_config = MCPConfig(
    server_name="office_server",
    max_file_size=50 * 1024 * 1024,  # 50MB
    extract_images=False,
    preserve_formatting=True
)
```

### Global Configuration

Configure the entire MCP integration system:

```python
from utils.mcp_integration import MCPIntegrationConfig

config = MCPIntegrationConfig(
    default_timeout=30,
    max_concurrent_requests=10,
    retry_attempts=3,
    retry_delay=1.0,
    enable_caching=True,
    cache_ttl=3600,
    log_level="INFO"
)
```

## Usage Examples

### Basic Document Processing

```python
import asyncio
from utils.mcp_integration import FileSystemMCPServer, MCPConfig

async def process_local_files():
    config = MCPConfig(server_name="file_processor")
    server = FileSystemMCPServer(config)

    try:
        # Process a text file
        document = await server.process_document("/path/to/document.txt")
        print(f"Title: {document.metadata.title}")
        print(f"Content length: {len(document.content)}")
        print(f"Word count: {document.metadata.word_count}")

        # Process a directory
        document = await server.process_document("/path/to/documents/")
        print(f"Processed {document.metadata.page_count} files")

    finally:
        await server.cleanup()

asyncio.run(process_local_files())
```

### Multi-Source Document Processing

```python
import asyncio
from dspy_modules.mcp_document_processor import MCPDocumentProcessor

async def process_multiple_sources():
    processor = MCPDocumentProcessor()

    try:
        sources = [
            "file:///path/to/local/document.pdf",
            "https://example.com/article",
            "https://github.com/user/repo",
            "sqlite:///path/to/database.db",
            "/path/to/document.docx"
        ]

        results = await processor.process_documents(sources)

        for i, result in enumerate(results):
            print(f"Source {i+1}: {result.metadata.source}")
            print(f"  Type: {result.metadata.content_type}")
            print(f"  Success: {result.success}")
            print(f"  Content length: {len(result.content)}")
            print()

    finally:
        await processor.cleanup()

asyncio.run(process_multiple_sources())
```

### DSPy Integration Example

```python
import dspy
from dspy_modules.mcp_document_processor import MCPDocumentProcessor

class DocumentAnalysisSignature(dspy.Signature):
    """Analyze document content and extract key insights."""

    document_source = dspy.InputField(desc="Source of the document")
    document_content = dspy.InputField(desc="Content of the document")

    key_insights = dspy.OutputField(desc="Key insights from the document")
    summary = dspy.OutputField(desc="Brief summary of the document")
    recommendations = dspy.OutputField(desc="Recommendations based on content")

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
print(f"Key insights: {result.key_insights}")
print(f"Summary: {result.summary}")
print(f"Recommendations: {result.recommendations}")
```

### Vector Store Integration

```python
import asyncio
from dspy_modules.mcp_document_processor import MCPDocumentIngestionPipeline
from utils.vector_store import VectorStore

async def ingest_documents_to_vector_store():
    # Initialize vector store
    vector_store = VectorStore(
        embedding_model="text-embedding-ada-002",
        index_name="documents"
    )

    # Initialize pipeline
    pipeline = MCPDocumentIngestionPipeline(vector_store=vector_store)

    try:
        # Process and ingest documents
        documents = [
            "file:///path/to/documents/",
            "https://example.com/docs",
            "https://github.com/user/repo"
        ]

        result = await pipeline.process_and_ingest(documents)

        print(f"Successfully processed {result.total_documents} documents")
        print(f"Ingested {result.successful_ingestions} documents to vector store")
        print(f"Processing time: {result.elapsed_time:.2f} seconds")

        # Search in vector store
        query = "machine learning algorithms"
        search_results = await vector_store.search(query, top_k=5)

        for i, result in enumerate(search_results):
            print(f"Result {i+1}: {result.metadata.title}")
            print(f"  Source: {result.metadata.source}")
            print(f"  Score: {result.score:.3f}")
            print()

    finally:
        await pipeline.cleanup()

asyncio.run(ingest_documents_to_vector_store())
```

## Error Handling

### Common Error Types

```python
from utils.mcp_integration import MCPError

try:
    document = await server.process_document("invalid_source")
except MCPError as e:
    print(f"MCP Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Error Handling Best Practices

```python
import asyncio
from utils.mcp_integration import MCPError

async def robust_document_processing(sources):
    processor = MCPDocumentProcessor()
    results = []

    try:
        for source in sources:
            try:
                result = await processor.process_document(source)
                results.append(result)
                print(f"✅ Successfully processed: {source}")

            except MCPError as e:
                print(f"❌ MCP Error processing {source}: {e}")
                # Continue with next document

            except Exception as e:
                print(f"❌ Unexpected error processing {source}: {e}")
                # Log error and continue

    finally:
        await processor.cleanup()

    return results

# Usage
sources = [
    "file:///path/to/valid.pdf",
    "https://invalid-url.com",
    "file:///nonexistent/file.txt",
    "https://example.com/valid-article"
]

results = await robust_document_processing(sources)
print(f"Successfully processed {len(results)} out of {len(sources)} documents")
```

## Performance Tuning

### Configuration Optimization

```python
from utils.mcp_integration import MCPConfig

# Optimize for high-throughput processing
high_throughput_config = MCPConfig(
    server_name="high_throughput",
    max_concurrent_requests=20,
    timeout=60,
    retry_attempts=2,
    enable_caching=True,
    cache_ttl=7200  # 2 hours
)

# Optimize for large files
large_file_config = MCPConfig(
    server_name="large_file_processor",
    max_file_size=500 * 1024 * 1024,  # 500MB
    chunk_size=1024 * 1024,  # 1MB chunks
    timeout=300  # 5 minutes
)

# Optimize for real-time processing
realtime_config = MCPConfig(
    server_name="realtime_processor",
    timeout=10,
    retry_attempts=1,
    enable_caching=False,
    max_concurrent_requests=5
)
```

### Batch Processing

```python
import asyncio
from dspy_modules.standardized_pipeline import StandardizedIngestionPipeline

async def batch_process_documents(documents, batch_size=10):
    pipeline = StandardizedIngestionPipeline()

    try:
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1} ({len(batch)} documents)")

            result = await pipeline.forward(batch)

            print(f"  Completed: {result.completed_documents}")
            print(f"  Failed: {result.failed_documents}")
            print(f"  Time: {result.elapsed_time:.2f}s")

    finally:
        await pipeline.cleanup()

# Usage
documents = [f"document_{i}.pdf" for i in range(100)]
await batch_process_documents(documents, batch_size=20)
```

### Memory Management

```python
import asyncio
import gc
from utils.mcp_integration import FileSystemMCPServer, MCPConfig

async def memory_efficient_processing(large_file_list):
    config = MCPConfig(
        server_name="memory_efficient",
        max_file_size=100 * 1024 * 1024,  # 100MB limit
        chunk_size=1024 * 1024  # 1MB chunks
    )

    server = FileSystemMCPServer(config)

    try:
        for file_path in large_file_list:
            try:
                document = await server.process_document(file_path)

                # Process document content
                process_content(document.content)

                # Clear document from memory
                del document
                gc.collect()

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    finally:
        await server.cleanup()

def process_content(content):
    # Process content without storing large objects
    words = content.split()
    word_count = len(words)
    # ... other processing
    return word_count
```

## Security Best Practices

### Input Validation

```python
import re
from urllib.parse import urlparse
from utils.mcp_integration import MCPError

def validate_source_security(source: str) -> bool:
    """Validate source for security concerns."""

    # Check for path traversal attempts
    if ".." in source or "//" in source:
        return False

    # Validate URL schemes
    if source.startswith(("http://", "https://")):
        parsed = urlparse(source)
        if not parsed.hostname:
            return False

        # Block potentially dangerous domains
        dangerous_domains = ["malicious.com", "evil.org"]
        if parsed.hostname in dangerous_domains:
            return False

    # Validate file paths
    if source.startswith("file://"):
        # Ensure path is within allowed directory
        allowed_dirs = ["/safe/documents/", "/public/docs/"]
        if not any(source.startswith(f"file://{d}" for d in allowed_dirs)):
            return False

    return True

# Usage in server
class SecureMCPServer(MCPServer):
    def validate_source(self, source: str) -> bool:
        if not validate_source_security(source):
            raise MCPError("Security validation failed")
        return super().validate_source(source)
```

### Rate Limiting

```python
import asyncio
import time
from collections import defaultdict

class RateLimitedMCPServer(MCPServer):
    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.request_counts = defaultdict(list)
        self.max_requests_per_minute = 60

    async def process_document(self, source: str) -> ProcessedDocument:
        # Check rate limit
        current_time = time.time()
        client_id = self._get_client_id(source)

        # Clean old requests
        self.request_counts[client_id] = [
            req_time for req_time in self.request_counts[client_id]
            if current_time - req_time < 60
        ]

        # Check if limit exceeded
        if len(self.request_counts[client_id]) >= self.max_requests_per_minute:
            raise MCPError("Rate limit exceeded")

        # Add current request
        self.request_counts[client_id].append(current_time)

        # Process document
        return await super().process_document(source)

    def _get_client_id(self, source: str) -> str:
        """Extract client identifier from source."""
        if source.startswith(("http://", "https://")):
            return urlparse(source).hostname
        return "local"
```

### Content Sanitization

```python
import html
import re
from utils.mcp_integration import MCPError

def sanitize_content(content: str) -> str:
    """Sanitize content to prevent XSS and other attacks."""

    # Remove potentially dangerous HTML tags
    dangerous_tags = re.compile(r'<(script|iframe|object|embed|form)[^>]*>.*?</\1>', re.IGNORECASE | re.DOTALL)
    content = dangerous_tags.sub('', content)

    # Escape HTML entities
    content = html.escape(content)

    # Remove null bytes
    content = content.replace('\x00', '')

    # Limit content length
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise MCPError("Content too large")

    return content

# Usage in document processing
class SecureDocumentProcessor:
    def process_content(self, content: str) -> str:
        try:
            sanitized = sanitize_content(content)
            return sanitized
        except Exception as e:
            raise MCPError(f"Content sanitization failed: {e}")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'docx'`

**Solution**: Install required dependencies
```bash
pip install python-docx openpyxl python-pptx
```

#### 2. File Size Limits

**Problem**: `MCPError: File too large`

**Solution**: Increase file size limits
```python
config = MCPConfig(max_file_size=100 * 1024 * 1024)  # 100MB
```

#### 3. Network Timeouts

**Problem**: `MCPError: Request timeout`

**Solution**: Increase timeout settings
```python
config = MCPConfig(timeout=120)  # 2 minutes
```

#### 4. Rate Limiting

**Problem**: `MCPError: Rate limit exceeded`

**Solution**: Implement exponential backoff
```python
import asyncio
import random

async def process_with_backoff(source, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await server.process_document(source)
        except MCPError as e:
            if "rate limit" in str(e).lower():
                delay = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)
                continue
            raise
    raise MCPError("Max retries exceeded")
```

#### 5. Memory Issues

**Problem**: `MemoryError` during large file processing

**Solution**: Use streaming processing
```python
async def stream_process_large_file(file_path):
    chunk_size = 1024 * 1024  # 1MB chunks

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            # Process chunk
            await process_chunk(chunk)

            # Clear memory
            del chunk
            gc.collect()
```

### Debugging Tips

#### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable debug logging for MCP servers
logging.getLogger('utils.mcp_integration').setLevel(logging.DEBUG)
```

#### Performance Profiling

```python
import cProfile
import pstats
import io

def profile_document_processing():
    profiler = cProfile.Profile()
    profiler.enable()

    # Run document processing
    asyncio.run(process_documents())

    profiler.disable()

    # Print statistics
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats()
    print(s.getvalue())
```

#### Memory Profiling

```python
import tracemalloc

def profile_memory_usage():
    tracemalloc.start()

    # Run document processing
    asyncio.run(process_documents())

    # Get memory statistics
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")

    # Get top memory allocations
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("Top 10 memory allocations:")
    for stat in top_stats[:10]:
        print(stat)

    tracemalloc.stop()
```

### Getting Help

For additional support:

1. **Check the logs** for detailed error messages
2. **Review the test suite** for usage examples
3. **Validate your configuration** against the examples above
4. **Test with simple cases** before processing complex documents
5. **Monitor system resources** during processing

## API Versioning

The MCP Integration API follows semantic versioning (SemVer):

- **Major version changes** may include breaking changes
- **Minor version changes** add new features while maintaining compatibility
- **Patch version changes** include bug fixes and improvements

Current version: `1.0.0`

### Migration Guide

When upgrading between major versions, check the migration guide for breaking changes and required updates to your code.
