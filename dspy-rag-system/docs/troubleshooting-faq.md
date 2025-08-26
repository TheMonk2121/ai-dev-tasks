# Troubleshooting and FAQ Guide

## Table of Contents

1. [Common Issues](#common-issues)
2. [Installation Problems](#installation-problems)
3. [Configuration Issues](#configuration-issues)
4. [Performance Problems](#performance-problems)
5. [Error Messages](#error-messages)
6. [Frequently Asked Questions](#frequently-asked-questions)
7. [Debugging Techniques](#debugging-techniques)
8. [Getting Help](#getting-help)

## Common Issues

### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'docx'`

**Solution**: Install the required Office processing libraries:
```bash
pip install python-docx openpyxl python-pptx
```

**Problem**: `ModuleNotFoundError: No module named 'PyPDF2'`

**Solution**: Install PDF processing library:
```bash
pip install PyPDF2
```

**Problem**: `ModuleNotFoundError: No module named 'httpx'`

**Solution**: Install HTTP client library:
```bash
pip install httpx
```

### 2. File Size Limits

**Problem**: `MCPError: File too large`

**Solution**: Increase the file size limit in your configuration:
```python
from utils.mcp_integration import MCPConfig

config = MCPConfig(
    max_file_size=100 * 1024 * 1024  # 100MB
)
```

### 3. Network Timeouts

**Problem**: `MCPError: Request timeout`

**Solution**: Increase timeout settings:
```python
config = MCPConfig(
    timeout=120  # 2 minutes
)
```

### 4. Rate Limiting

**Problem**: `MCPError: Rate limit exceeded`

**Solution**: Implement exponential backoff:
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

### 5. Memory Issues

**Problem**: `MemoryError` during large file processing

**Solution**: Use streaming processing and batch operations:
```python
import gc

async def memory_efficient_processing(sources):
    for source in sources:
        try:
            result = await server.process_document(source)
            # Process result
            del result
            gc.collect()
        except Exception as e:
            print(f"Error processing {source}: {e}")
```

## Installation Problems

### 1. Python Version Issues

**Problem**: `SyntaxError` or compatibility issues

**Solution**: Ensure you're using Python 3.8+:
```bash
python --version
# Should be 3.8 or higher
```

### 2. Virtual Environment Issues

**Problem**: Packages not found in virtual environment

**Solution**: Activate your virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Permission Issues

**Problem**: `PermissionError` when installing packages

**Solution**: Use user installation or fix permissions:
```bash
# User installation
pip install --user package_name

# Or fix permissions
sudo pip install package_name
```

## Configuration Issues

### 1. Invalid Configuration

**Problem**: `ValidationError` in configuration

**Solution**: Check your configuration structure:
```python
from utils.mcp_integration import MCPConfig

# Correct configuration
config = MCPConfig(
    server_name="my_server",
    max_file_size=50 * 1024 * 1024,
    timeout=30
)
```

### 2. Missing Environment Variables

**Problem**: `KeyError` for environment variables

**Solution**: Set required environment variables:
```bash
export GITHUB_TOKEN="your_github_token"
export DATABASE_URL="postgresql://user:pass@host/db"
```

### 3. File Path Issues

**Problem**: `FileNotFoundError` for local files

**Solution**: Use absolute paths or check file existence:
```python
import os

# Check if file exists
if os.path.exists(file_path):
    result = await server.process_document(file_path)
else:
    print(f"File not found: {file_path}")
```

## Performance Problems

### 1. Slow Processing

**Problem**: Document processing is very slow

**Solutions**:

**A. Enable caching:**
```python
config = MCPConfig(
    enable_caching=True,
    cache_ttl=3600  # 1 hour
)
```

**B. Use batch processing:**
```python
async def batch_process(sources, batch_size=10):
    for i in range(0, len(sources), batch_size):
        batch = sources[i:i + batch_size]
        tasks = [server.process_document(source) for source in batch]
        results = await asyncio.gather(*tasks)
```

**C. Optimize file size limits:**
```python
config = MCPConfig(
    max_file_size=10 * 1024 * 1024,  # 10MB for faster processing
    chunk_size=1024 * 1024  # 1MB chunks
)
```

### 2. High Memory Usage

**Problem**: Memory usage spikes during processing

**Solutions**:

**A. Use streaming processing:**
```python
async def stream_process_large_file(file_path):
    chunk_size = 1024 * 1024  # 1MB chunks

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            await process_chunk(chunk)
            del chunk
            gc.collect()
```

**B. Process in smaller batches:**
```python
batch_size = 5  # Smaller batches
```

### 3. Network Bottlenecks

**Problem**: Slow network requests

**Solutions**:

**A. Increase concurrent connections:**
```python
config = MCPConfig(
    max_concurrent_requests=20
)
```

**B. Use connection pooling:**
```python
import httpx

async with httpx.AsyncClient() as client:
    # Reuse client for multiple requests
    pass
```

## Error Messages

### Common Error Messages and Solutions

#### 1. `MCPError: Unsupported document type`

**Cause**: The server doesn't support the file format

**Solution**: Check supported formats and convert if needed:
```python
# Check if source is supported
if server.validate_source(source):
    result = await server.process_document(source)
else:
    print(f"Unsupported source: {source}")
```

#### 2. `MCPError: Invalid source format`

**Cause**: The source URL or path is malformed

**Solution**: Validate source format:
```python
from urllib.parse import urlparse

def validate_source(source):
    if source.startswith(('http://', 'https://')):
        parsed = urlparse(source)
        return bool(parsed.hostname)
    elif source.startswith('file://'):
        return os.path.exists(source[7:])
    else:
        return os.path.exists(source)
```

#### 3. `MCPError: Processing failed`

**Cause**: Generic processing error

**Solution**: Enable detailed logging and check specific error:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('utils.mcp_integration').setLevel(logging.DEBUG)
```

#### 4. `MCPError: Authentication required`

**Cause**: API requires authentication

**Solution**: Provide authentication credentials:
```python
config = MCPConfig(
    github_token="your_token",
    api_key="your_api_key"
)
```

## Frequently Asked Questions

### Q1: How do I process multiple document types?

**A**: Use the `MCPDocumentProcessor` which automatically routes to the appropriate server:

```python
from dspy_modules.mcp_document_processor import MCPDocumentProcessor

processor = MCPDocumentProcessor()

sources = [
    "document.pdf",
    "spreadsheet.xlsx",
    "https://example.com/article",
    "https://github.com/user/repo"
]

results = await processor.process_documents(sources)
```

### Q2: How do I handle large files efficiently?

**A**: Use streaming and chunking:

```python
config = MCPConfig(
    max_file_size=100 * 1024 * 1024,  # 100MB
    chunk_size=1024 * 1024  # 1MB chunks
)

# Process in batches
async def process_large_files(sources, batch_size=5):
    for i in range(0, len(sources), batch_size):
        batch = sources[i:i + batch_size]
        results = await asyncio.gather(*[
            server.process_document(source) for source in batch
        ])
        yield results
```

### Q3: How do I integrate with vector stores?

**A**: Use the `MCPDocumentIngestionPipeline`:

```python
from dspy_modules.mcp_document_processor import MCPDocumentIngestionPipeline

pipeline = MCPDocumentIngestionPipeline(vector_store=vector_store)
result = await pipeline.process_and_ingest(sources)
```

### Q4: How do I handle errors gracefully?

**A**: Implement robust error handling:

```python
async def robust_processing(sources):
    results = []
    failed = []

    for source in sources:
        try:
            result = await server.process_document(source)
            results.append(result)
        except MCPError as e:
            print(f"MCP Error for {source}: {e}")
            failed.append(source)
        except Exception as e:
            print(f"Unexpected error for {source}: {e}")
            failed.append(source)

    return results, failed
```

### Q5: How do I monitor processing performance?

**A**: Use the built-in statistics:

```python
# Get processing statistics
stats = processor.get_processing_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Average processing time: {stats['avg_processing_time']:.2f}s")
```

### Q6: How do I configure different servers?

**A**: Configure each server individually:

```python
# File system server
file_config = MCPConfig(
    server_name="file_system",
    max_file_size=100 * 1024 * 1024
)

# Web server
web_config = MCPConfig(
    server_name="web_server",
    timeout=60,
    max_redirects=5
)

# GitHub server
github_config = MCPConfig(
    server_name="github_server",
    github_token="your_token"
)
```

### Q7: How do I test the system?

**A**: Use the provided test scripts:

```bash
# Run unit tests
python -m pytest tests/

# Run validation scripts
python test_file_system_server.py
python test_web_server.py
python test_pdf_server.py
python test_github_server.py
python test_database_server.py
python test_office_server.py
```

### Q8: How do I extend the system with custom servers?

**A**: Create a custom server by extending `MCPServer`:

```python
from utils.mcp_integration import MCPServer, MCPConfig

class CustomMCPServer(MCPServer):
    def __init__(self, config: MCPConfig):
        super().__init__(config)

    def validate_source(self, source: str) -> bool:
        # Implement source validation
        return source.endswith('.custom')

    async def process_document(self, source: str) -> ProcessedDocument:
        # Implement document processing
        content = self._extract_content(source)
        metadata = self._extract_metadata(source)
        return ProcessedDocument(content=content, metadata=metadata, success=True)
```

## Debugging Techniques

### 1. Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable specific component logging
logging.getLogger('utils.mcp_integration').setLevel(logging.DEBUG)
logging.getLogger('dspy_modules').setLevel(logging.DEBUG)
```

### 2. Performance Profiling

```python
import cProfile
import pstats
import io

def profile_processing():
    profiler = cProfile.Profile()
    profiler.enable()

    # Run your processing code
    asyncio.run(process_documents())

    profiler.disable()

    # Print statistics
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats()
    print(s.getvalue())
```

### 3. Memory Profiling

```python
import tracemalloc

def profile_memory():
    tracemalloc.start()

    # Run your processing code
    asyncio.run(process_documents())

    # Get memory statistics
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")

    # Get top allocations
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    for stat in top_stats[:10]:
        print(stat)

    tracemalloc.stop()
```

### 4. Step-by-Step Debugging

```python
async def debug_processing(source):
    print(f"1. Validating source: {source}")

    if not server.validate_source(source):
        print("❌ Source validation failed")
        return

    print("2. Starting document processing")
    try:
        result = await server.process_document(source)
        print(f"3. Processing successful: {len(result.content)} characters")
        return result
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        raise
```

### 5. Network Debugging

```python
import httpx

# Enable HTTP debugging
async with httpx.AsyncClient() as client:
    response = await client.get("https://example.com")
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content length: {len(response.content)}")
```

## Getting Help

### 1. Check Documentation

- Review the [API Reference](mcp-integration-api-reference.md)
- Check the [DSPy Integration Guide](dspy-integration-guide.md)
- Read the [System Overview](../../400_guides/400_system-overview.md)

### 2. Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_file_system_server.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### 3. Validate Configuration

```python
# Validate your configuration
from utils.mcp_integration import MCPConfig

try:
    config = MCPConfig(
        server_name="test_server",
        max_file_size=50 * 1024 * 1024
    )
    print("✅ Configuration is valid")
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

### 4. Check System Requirements

```python
import sys
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()}")

# Check required packages
required_packages = [
    'dspy', 'httpx', 'pydantic', 'pytest', 'asyncio'
]

for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package} is installed")
    except ImportError:
        print(f"❌ {package} is missing")
```

### 5. Common Debugging Checklist

- [ ] Check Python version (3.8+)
- [ ] Verify all dependencies are installed
- [ ] Validate configuration parameters
- [ ] Check file permissions and paths
- [ ] Verify network connectivity
- [ ] Review error logs
- [ ] Test with simple examples first
- [ ] Monitor system resources

### 6. Reporting Issues

When reporting issues, include:

1. **Environment details**:
   - Python version
   - Operating system
   - Package versions

2. **Error details**:
   - Full error message
   - Stack trace
   - Steps to reproduce

3. **Configuration**:
   - Relevant configuration settings
   - Source URLs/paths being processed

4. **Expected vs actual behavior**:
   - What you expected to happen
   - What actually happened

Example issue report:
```
Environment:
- Python 3.12.11
- macOS 14.4.0
- MCP Integration 1.0.0

Error:
MCPError: File too large

Steps to reproduce:
1. Configure max_file_size=10MB
2. Try to process 20MB PDF file
3. Error occurs

Expected: File should be processed or clear error message
Actual: Generic "File too large" error
```

This troubleshooting guide should help you resolve most common issues with the MCP integration system.
