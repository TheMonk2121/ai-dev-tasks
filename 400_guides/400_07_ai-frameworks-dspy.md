## 🧩 Constitution Integration Points (DSPy)

- Use DSPy assertions to enforce safety and correctness at runtime.
- Apply teleprompter optimization and few‑shot scaffolding as governance aids.
- Surface constitution violations via metrics/logs for observability.

### Runtime Signature Validation (from Schema Reference)
- Use `DSPySignatureValidator` to validate inputs/outputs for key signatures (e.g., `LocalTaskSignature`).
- Prefer `validate_inputs` before execution and `validate_outputs` after; record metrics for ops.
- For production wrappers, call validation and capture timing and pass/fail counts.

### DSPy Type‑Safety Patterns (from Comprehensive Guide)
- Protocols for forward‑compatible modules; Union types; type guards; safe casting with `cast`
- Prefer assertions/validators to guard critical logic paths
\n+## 🧩 Constitution Integration Points (DSPy)
\n+- Use DSPy assertions to enforce safety and correctness at runtime.
- Apply teleprompter optimization and few‑shot scaffolding as governance aids.
- Surface constitution violations via metrics/logs for observability.
# AI Frameworks: DSPy

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete DSPy framework reference, technical implementation, integration patterns, and system demonstration | Implementing DSPy modules, debugging AI systems, or integrating components | Use signature examples, follow implementation patterns, and reference system architecture |

## 🎯 Purpose

This guide covers comprehensive DSPy framework integration and usage including:
- **DSPy framework overview and architecture**
- **DSPy integration patterns and best practices**
- **DSPy schema and configuration**
- **DSPy v2/v3 technical implementation**
- **DSPy performance optimization**
- **Complete DSPy signature catalog and schema reference**
- **System demonstration and integration patterns**
- **Model switching and optimization systems**

## 📋 When to Use This Guide

- **Working with DSPy framework**
- **Implementing AI agent systems**
- **Integrating DSPy with existing systems**
- **Optimizing DSPy performance**
- **Understanding DSPy architecture**
- **Implementing DSPy modules**
- **Debugging AI systems**

## 🎯 Expected Outcomes

- **Effective DSPy integration** and usage
- **Optimized AI agent performance** and efficiency
- **Reliable DSPy system operation** and stability
- **Clear DSPy architecture understanding** and implementation
- **Comprehensive DSPy testing** and validation
- **Complete signature compliance** and system integration
- **Performance standards** meeting benchmarks

## 📋 Policies

### DSPy Integration
- **Standardized integration patterns** across all systems
- **Consistent configuration** and setup procedures
- **Performance optimization** and monitoring
- **Error handling** and recovery mechanisms
- **Testing and validation** requirements

### DSPy Architecture
- **Modular design** with clear component boundaries
- **Scalable architecture** for growing needs
- **Maintainable codebase** with clear documentation
- **Security considerations** and access control
- **Monitoring and observability** throughout

### DSPy Development
- **Signature compliance** following DSPy patterns
- **System integration** with seamless component interaction
- **Performance standards** meeting established benchmarks
- **Code quality** following assertion framework requirements

## 🤖 DSPY FRAMEWORK OVERVIEW

### **DSPy-MCP Integration System**

#### **MCP Memory Server Integration**
**Production-ready MCP server for memory rehydration with DSPy integration.**

**Purpose**: Database-based memory rehydration for Cursor AI with automatic caching, monitoring, and performance optimization.

**Key Features**:
- **MCP Protocol Compliance**: Standard MCP endpoints for tool integration
- **Role-Aware Context**: Role-specific memory rehydration (planner, implementer, researcher)
- **Response Caching**: 5-minute TTL with LRU eviction (170x performance improvement)
- **Real-time Monitoring**: Health checks, metrics, and status dashboard
- **Automatic Recovery**: LaunchAgent integration with Python 3.12 compatibility

**Available Tools**:
- **`rehydrate_memory`**: Get role-aware context from PostgreSQL database
  - **Parameters**:
    - `role` (string): AI role for context selection (planner, implementer, researcher)
    - `task` (string): Specific task or query for context (required)
    - `limit` (integer): Maximum number of sections to return (default: 8)
    - `token_budget` (integer): Token budget for context (default: 1200)

**Role Access**:
- **Planner**: Full access to planning and strategy context
- **Implementer**: Access to implementation and technical context
- **Researcher**: Access to research and analysis context
- **Coder**: Access to code-specific context (via implementer role)
- **Reviewer**: Access to review and quality context (via planner role)

**Performance Metrics**:
- **Cache Hit Rate**: 71.43% (excellent efficiency)
- **Average Response Time**: 24.41ms (65% improvement)
- **Cache Performance**: 170x faster for cached requests

**Usage Examples**:
```bash
# Start the server
./scripts/start_mcp_server.sh

# Memory rehydration for planner role
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "rehydrate_memory", "arguments": {"role": "planner", "task": "project planning", "limit": 5, "token_budget": 1000}}'

# View metrics and status
curl http://localhost:3000/metrics
open http://localhost:3000/status
```

**Full Documentation**: See `400_06_memory-and-context-systems.md#mcp-memory-server-integration`

#### **MCP Integration Architecture**
**Complete MCP integration system with multiple server types and DSPy modules.**

**Core Components**:
- **MCP Memory Server**: HTTP server for memory rehydration (`scripts/mcp_memory_server.py`)
- **MCP Document Processor**: DSPy module for document processing (`dspy_modules/mcp_document_processor.py`)
- **MCP Integration Layer**: Base server and specialized servers (`utils/mcp_integration/`)

**Available MCP Servers**:
- **File System Server**: Local file processing (`file_system_server.py`)
- **Web Server**: Web content processing (`web_server.py`)
- **PDF Server**: PDF document processing (`pdf_server.py`)
- **GitHub Server**: GitHub repository processing (`github_server.py`)
- **Office Server**: Office document processing (`office_server.py`)
- **Database Server**: Database content processing (`database_server.py`)

**DSPy Integration**:
- **MCPDocumentProcessor**: Unified document processing with MCP integration
- **MCPDocumentIngestionPipeline**: Complete ingestion pipeline
- **MCPDocumentSignature**: DSPy signatures for MCP processing

**Configuration**:
```python
from utils.mcp_integration import MCPConfig
from dspy_modules.mcp_document_processor import MCPDocumentProcessor

# Configure MCP server
config = MCPConfig(
    server_name="document_processor",
    timeout=30,
    max_file_size=100 * 1024 * 1024  # 100MB
)

# Initialize processor
processor = MCPDocumentProcessor(
    mcp_timeout=30,
    max_file_size=100 * 1024 * 1024
)
```

**Usage Examples**:
```python
# Process document with MCP
result = processor.process_document(
    document_source="https://example.com/document.pdf",
    processing_config={"extract_text": True, "extract_metadata": True}
)

# Complete ingestion pipeline
pipeline = MCPDocumentIngestionPipeline()
result = pipeline.ingest_document(
    document_source="file:///path/to/document.docx",
    vector_store=vector_store
)
```

#### **DSPy-MCP Integration Guide**

**Purpose**: Advanced RAG applications with Model Context Protocol integration for enhanced document processing and analysis.

**Key Components**:
- **DSPy-MCP Integration**: Advanced RAG applications with Model Context Protocol
- **Document Processing Workflows**: Multi-source processing and analysis pipelines
- **DSPy Signatures**: Structured input/output patterns for document analysis
- **MCPDocumentProcessor**: Core document processing component
- **StandardizedIngestionPipeline**: Multi-source document ingestion
- **Document Comparison**: Multi-document analysis and difference identification
- **Content Summarization**: Automated document summarization with key points

**Integration Architecture**:
- **Multi-Source Processing**: Support for multiple document sources and formats
- **Analysis Pipelines**: Structured workflows for document analysis
- **Structured I/O**: DSPy signatures for consistent input/output patterns
- **Content Processing**: Automated content extraction and summarization

#### **MCP Integration API Reference**

**Purpose**: Complete API reference for MCP integration with DSPy, including server types, security, and performance optimization.

**API Components**:
- **Server Types**: Different server configurations for various use cases
- **DSPy Integration**: Seamless integration with DSPy framework
- **Security Measures**: Comprehensive security and access control
- **Performance Optimization**: API performance tuning and monitoring
- **Error Handling**: Robust error handling and recovery mechanisms

**Integration Patterns**:
- **RESTful API**: Standard REST API for MCP operations
- **GraphQL Support**: GraphQL interface for complex queries
- **WebSocket Communication**: Real-time communication for live updates
- **Authentication**: JWT-based authentication and authorization
- **Rate Limiting**: Token bucket algorithm for API protection

#### **MCP Troubleshooting FAQ**

**Purpose**: Comprehensive troubleshooting guide for MCP integration, covering common issues, installation, configuration, and debugging.

**Common Issues**:
- **Installation Problems**: Common installation issues and solutions
- **Configuration Errors**: Configuration problems and fixes
- **Performance Issues**: Performance optimization and troubleshooting
- **Error Messages**: Common error messages and their solutions
- **Integration Problems**: DSPy integration issues and resolutions

**Debugging Techniques**:
- **Log Analysis**: How to analyze logs for troubleshooting
- **Performance Monitoring**: Tools and techniques for performance monitoring
- **Error Tracking**: Error tracking and analysis methods
- **System Diagnostics**: System health checks and diagnostics

#### **Multi-Tenant Indexing Strategy**

**Purpose**: Advanced indexing strategy for multi-tenant environments with RLS, performance optimization, and migration support.

**Key Features**:
- **Row-Level Security (RLS)**: Tenant isolation and data protection
- **Performance Optimization**: Query optimization and indexing strategies
- **Migration Support**: Seamless migration from single-tenant to multi-tenant
- **Scalability**: Horizontal scaling for growing tenant base

**Architecture Components**:
- **Database Design**: Multi-tenant database schema and design
- **Indexing Strategy**: Optimized indexing for multi-tenant queries
- **Security Implementation**: RLS implementation and security measures
- **Performance Monitoring**: Multi-tenant performance monitoring and optimization

### **Current Status**
- **Status**: ✅ **ACTIVE** - DSPy framework fully operational
- **Priority**: 🔥 Critical - Essential for AI development and system integration
- **Version**: DSPy 3.0 Optimization System
- **Project**: B-1004 DSPy 3.0 Optimization
- **Next Steps**: Use signature examples and follow implementation patterns

## 🛠️ Troubleshooting and FAQ (DSPy/MCP)

### Common Issues

- Import errors and fixes
  - Office libs: `pip install python-docx openpyxl python-pptx`
  - PDFs: `pip install PyPDF2`
  - HTTP client: `pip install httpx`
- File size limits
  - `MCPConfig(max_file_size=100 * 1024 * 1024)` for 100MB
- Network timeouts
  - `MCPConfig(timeout=120)` (seconds)
- Rate limiting (exponential backoff)
  - Retry `(2**attempt) + random.uniform(0, 1)`; `await asyncio.sleep(delay)`
- Memory issues (large processing)
  - Stream, batch, free objects, call `gc.collect()` in loops

### Installation Problems

- Python version: use Python 3.8+ (`python --version`)
- Virtual environment: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Permissions: prefer `pip install --user package_name` over `sudo pip install`

### Configuration Issues

- Validation errors: ensure correct `MCPConfig(server_name, max_file_size, timeout)` structure
- Missing env vars: set `GITHUB_TOKEN`, `DATABASE_URL`
- File path issues: prefer absolute paths; validate with `os.path.exists`

### Performance Problems

- Slow processing
  - Enable caching: `MCPConfig(enable_caching=True, cache_ttl=3600)`
  - Batch with `asyncio.gather` over slices
  - Tune `max_file_size` and `chunk_size`
- High memory usage
  - Stream in chunks; smaller `batch_size` (e.g., 5); `gc.collect()`
- Network bottlenecks
  - `MCPConfig(max_concurrent_requests=20)`
  - Reuse `httpx.AsyncClient` (connection pooling)

### Error Messages and Canonical Fixes

- `MCPError: Unsupported document type`: check supported formats; convert if needed
- `MCPError: Invalid source format`: validate URLs with `urlparse`; handle `file://` and local paths
- `MCPError: Processing failed`: enable detailed logging
  - `logging.getLogger('utils.mcp_integration').setLevel(logging.DEBUG)`
- `MCPError: Authentication required`: use `MCPConfig(github_token=..., api_key=...)`

### Frequently Asked Questions (APIs and Patterns)

- Process multiple document types
```python
from dspy_modules.mcp_document_processor import MCPDocumentProcessor

processor = MCPDocumentProcessor()
results = await processor.process_documents(["document.pdf", "spreadsheet.xlsx", "https://example.com"])
```

- Handle large files efficiently
```python
config = MCPConfig(max_file_size=100 * 1024 * 1024, chunk_size=1024 * 1024)

async def process_large_files(sources, batch_size=5):
    for i in range(0, len(sources), batch_size):
        batch = sources[i:i + batch_size]
        results = await asyncio.gather(*[server.process_document(s) for s in batch])
        yield results
```

- Vector store integration
```python
from dspy_modules.mcp_document_processor import MCPDocumentIngestionPipeline

pipeline = MCPDocumentIngestionPipeline(vector_store=vector_store)
result = await pipeline.process_and_ingest(sources)
```

- Robust error handling
```python
async def robust_processing(sources):
    results, failed = [], []
    for s in sources:
        try:
            results.append(await server.process_document(s))
        except Exception:
            failed.append(s)
    return results, failed
```

- Monitor processing performance
```python
stats = processor.get_processing_stats()
print(stats["total_documents"], stats["success_rate"], stats["avg_processing_time"])
```

- Configure servers
```python
# File system
file_config = MCPConfig(server_name="file_system", max_file_size=100 * 1024 * 1024)

# Web
web_config = MCPConfig(server_name="web_server", timeout=60, max_redirects=5)

# GitHub
github_config = MCPConfig(server_name="github_server", github_token="your_token")
```

- Custom server extension
```python
from utils.mcp_integration import MCPServer, MCPConfig

class CustomMCPServer(MCPServer):
    def __init__(self, config: MCPConfig):
        super().__init__(config)
    def validate_source(self, source: str) -> bool:
        return source.endswith('.custom')
    async def process_document(self, source: str) -> ProcessedDocument:
        # implement extraction
        return ProcessedDocument(content="...", metadata={}, success=True)
```

### Debugging Techniques

- Enable debug logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('utils.mcp_integration').setLevel(logging.DEBUG)
logging.getLogger('dspy_modules').setLevel(logging.DEBUG)
```

- Performance profiling (cProfile + pstats)
```python
def profile_processing():
    import cProfile, pstats, io, asyncio
    profiler = cProfile.Profile(); profiler.enable()
    asyncio.run(process_documents())
    profiler.disable(); s = io.StringIO()
    pstats.Stats(profiler, stream=s).sort_stats('cumulative').print_stats()
    print(s.getvalue())
```

- Memory profiling (tracemalloc)
```python
import tracemalloc
tracemalloc.start()
# ... run workload ...
# print current/peak and top allocations
```

- Step-by-step debug
```python
async def debug_processing(source):
    if not server.validate_source(source):
        return
    try:
        result = await server.process_document(source)
        return result
    except Exception as e:
        raise
```

- Network debugging
```python
import httpx
async with httpx.AsyncClient() as client:
    r = await client.get("https://example.com")
    print(r.status_code, len(r.content))
```

### Getting Help

- Documentation
  - API Reference: `dspy-rag-system/docs/mcp-integration-api-reference.md`
  - DSPy Integration Guide: `dspy-rag-system/docs/dspy-integration-guide.md`
  - System Overview: `400_03_system-overview-and-architecture.md`
- Run tests
  - `python -m pytest tests/ -v`
  - Specific files; with coverage: `--cov=src --cov-report=html`
- Validate configuration
```python
from utils.mcp_integration import MCPConfig
config = MCPConfig(server_name="test_server", max_file_size=50 * 1024 * 1024)
```
- System requirements
  - Print Python, platform, arch; verify packages: `dspy`, `httpx`, `pydantic`, `pytest`, `asyncio`

### **Tech Stack Integration**

#### **1. Cursor - Your AI-Powered Code Editor**
- **What it is**: A code editor that has AI built right into it
- **What you're doing**: Using it to write and manage your AI system
- **Why it's cool**: You can ask it to help you write code, just like you're doing right now!

#### **2. Mistral-7B - Your AI Brain**
- **What it is**: A large language model (think of it as a very smart AI that can understand and generate text)
- **How you're running it**: Through Ollama (a tool that lets you run AI models on your own computer)
- **Model**: Mistral 7B Instruct
- **What it does**: Takes your questions and generates intelligent answers

#### **3. DSPy - Your AI's Programming Framework**
- **What DSPy is**: A framework that helps you program AI models more systematically
- **What it does for you**:
  - **Structures your AI interactions** - Instead of just chatting, it creates organized workflows
  - **Improves prompt engineering** - Makes your AI prompts more effective and reliable
  - **Enables memory and learning** - Your AI can remember past interactions and learn from them
  - **Creates reusable components** - Build AI modules you can use over and over

#### **4. RAG System - Your AI's Memory**
- **What RAG means**: "Retrieval Augmented Generation" (fancy way of saying "find relevant info, then generate an answer")
- **How it works**:
  1. You ask a question
  2. The system searches through your documents to find relevant information
  3. It gives that information to Mistral-7B
  4. Mistral-7B generates an answer based on your documents

#### **5. Vector Database (PostgreSQL) - Your AI's Filing Cabinet**
- **What it is**: A special database that stores your documents in a way that makes them easy to search
- **How it works**:
  - Breaks your documents into small pieces (chunks)
  - Converts each piece into numbers (vectors) that represent meaning
  - When you ask a question, it finds the most similar pieces
- **Why it's smart**: It can find relevant information even if you don't use the exact same words

### **How DSPy Makes This Different from ChatGPT**

#### **ChatGPT (Standard LLM):**
```
You: "What's in my documents?"
ChatGPT: "I don't have access to your documents. I can only help with general knowledge."
```

#### **Your DSPy RAG System:**
```
You: "What's in my documents?"
DSPy RAG:
1. Searches your actual documents
2. Finds relevant information
3. Uses Mistral-7B to generate an answer
4. Gives you: "Based on your documents, here's what I found..."
```

### **The DSPy Pipeline:**
```
Your Question → DSPy RAGSystem → Vector Search → Mistral-7B → Answer
```

### **Step-by-Step Process:**

1. **You ask a question** → "Who has the highest salary?"

2. **DSPy RAGSystem** takes over:
   - **Searches your documents** using vector similarity
   - **Finds relevant chunks** from your CSV data
   - **Prepares context** for Mistral-7B

3. **Mistral-7B** receives:
   - Your original question
   - Relevant document chunks
   - DSPy's structured prompt

4. **Mistral-7B generates** an answer based on your actual data

5. **You get** a thoughtful, informed response

## 📋 DSPY SIGNATURE CATALOG

### **Model Switcher Signatures**

#### **LocalTaskSignature**
**Location**: `dspy-rag-system/src/dspy_modules/model_switcher.py:516`

```python
class LocalTaskSignature(Signature):
    """Signature for local model task execution with structured I/O"""

    task = InputField(desc="The task to perform")
    task_type = InputField(desc="Type of task (planning, coding, analysis, etc.)")
    role = InputField(desc="AI role (planner, implementer, coder, researcher)")
    complexity = InputField(desc="Task complexity (simple, moderate, complex)")

    result = OutputField(desc="Task execution result")
    confidence = OutputField(desc="Confidence score (0-1)")
    model_used = OutputField(desc="Model that was used for this task")
    reasoning = OutputField(desc="Reasoning for model selection and approach")
```

**Usage Example**:
```python
from dspy_modules.model_switcher import ModelSwitcher

switcher = ModelSwitcher()
result = switcher.forward(
    task="Implement a new feature",
    task_type="coding",
    role="coder",
    complexity="moderate"
)
```

#### **MultiModelOrchestrationSignature**
**Location**: `dspy-rag-system/src/dspy_modules/model_switcher.py:530`

```python
class MultiModelOrchestrationSignature(Signature):
    """Signature for multi-model task orchestration"""

    task = InputField(desc="The main task to orchestrate")
    task_type = InputField(desc="Type of task")
    role = InputField(desc="Primary AI role")

    plan = OutputField(desc="Planning phase result")
    execution = OutputField(desc="Execution phase result")
    review = OutputField(desc="Review phase result")
    final_result = OutputField(desc="Final orchestrated result")
    orchestration_notes = OutputField(desc="Notes about the orchestration process")
```

**Usage Example**:
```python
# Multi-model orchestration for complex tasks
result = switcher.orchestrate_task(
    task="Build a complete feature with planning and review",
    task_type="development",
    role="implementer"
)
```

#### **ModelSelectionSignature**
**Location**: `dspy-rag-system/src/dspy_modules/model_switcher.py:544`

```python
class ModelSelectionSignature(Signature):
    """Signature for intelligent model selection"""

    task = InputField(desc="Task description")
    task_type = InputField(desc="Type of task")
    complexity = InputField(desc="Task complexity")
    context_size = InputField(desc="Estimated context size")

    selected_model = OutputField(desc="Selected model for the task")
    reasoning = OutputField(desc="Reasoning for model selection")
    confidence = OutputField(desc="Confidence in selection (0-1)")
```

### **RAG System Signatures**

#### **RAGQuerySignature**
**Location**: `dspy-rag-system/src/dspy_modules/rag_system.py:45`

```python
class RAGQuerySignature(Signature):
    """Signature for RAG system queries"""

    query = InputField(desc="The query to search for")
    context = InputField(desc="Additional context for the query")
    max_results = InputField(desc="Maximum number of results to return")

    results = OutputField(desc="Search results from vector database")
    sources = OutputField(desc="Source documents for results")
    confidence = OutputField(desc="Confidence in results (0-1)")
```

#### **RAGAnswerSignature**
**Location**: `dspy-rag-system/src/dspy_modules/rag_system.py:60`

```python
class RAGAnswerSignature(Signature):
    """Signature for RAG system answer generation"""

    query = InputField(desc="Original query")
    context = InputField(desc="Retrieved context")
    sources = InputField(desc="Source documents")

    answer = OutputField(desc="Generated answer based on context")
    reasoning = OutputField(desc="Reasoning for the answer")
    sources_used = OutputField(desc="Sources actually used in answer")
```

### **Assertion Framework Signatures**

#### **CodeQualityValidatorSignature**
**Location**: `dspy-rag-system/src/dspy_modules/assertions.py:25`

```python
class CodeQualityValidatorSignature(Signature):
    """Signature for code quality validation"""

    code = InputField(desc="Code to validate")
    language = InputField(desc="Programming language")
    standards = InputField(desc="Quality standards to apply")

    is_valid = OutputField(desc="Whether code meets standards")
    issues = OutputField(desc="List of quality issues found")
    suggestions = OutputField(desc="Suggestions for improvement")
    score = OutputField(desc="Quality score (0-100)")
```

#### **LogicValidatorSignature**
**Location**: `dspy-rag-system/src/dspy_modules/assertions.py:40`

```python
class LogicValidatorSignature(Signature):
    """Signature for logic validation"""

    logic = InputField(desc="Logic to validate")
    requirements = InputField(desc="Requirements to check against")
    context = InputField(desc="Context for validation")

    is_valid = OutputField(desc="Whether logic is valid")
    errors = OutputField(desc="Logic errors found")
    warnings = OutputField(desc="Logic warnings")
    recommendations = OutputField(desc="Recommendations for improvement")
```

## 🏗️ DSPY 3.0 TECHNICAL IMPLEMENTATION

### **System Architecture**

#### **Core Components**
```
DSPy 3.0 Optimization System
├── ModelSwitcher (Enhanced)
│   ├── Optimizer Integration
│   ├── Model Selection
│   └── Performance Monitoring
├── Optimizers
│   ├── LabeledFewShotOptimizer
│   ├── DSPyOptimizerManager
│   └── OptimizationResult
├── Assertion Framework
│   ├── CodeQualityValidator
│   ├── LogicValidator
│   ├── PerformanceValidator
│   └── SecurityValidator
├── Optimization Loop
│   ├── CreatePhase
│   ├── EvaluatePhase
│   ├── OptimizePhase
│   └── DeployPhase
├── Metrics Dashboard
│   ├── MetricSeries
│   ├── Alert Management
│   └── Dashboard Views
├── System Integration
│   ├── DSPySystemIntegration
│   ├── IntegrationConfig
│   └── SystemStatus
├── LangExtract System
│   ├── EntityExtractor
│   ├── RelationExtractor
│   ├── FactExtractor
│   ├── LangExtractSystem
│   └── LangExtractInterface
├── Core DSPy Modules (Tier 1)
│   ├── CursorModelRouter
│   ├── VectorStore
│   ├── DocumentProcessor
│   └── OptimizationLoop
├── Context & Observability (Tier 1)
│   ├── MemoryRehydrator (Python)
│   ├── MemoryRehydrator (Go)
│   ├── StructuredTracer
│   └── SelfCritique
├── Production Infrastructure (Tier 2)
│   ├── SingleDoorwaySystem
│   ├── DocCoherenceValidator
│   ├── TaskGenerationAutomation
│   ├── DatabaseResilience
│   ├── Dashboard
│   ├── ErrorPatternRecognition
│   ├── BulkDocumentProcessor
│   ├── DatabasePathCleanup
│   ├── PromptSanitizer
│   ├── RollbackDocSystem
│   └── AnchorMetadataParser
├── Supporting Infrastructure (Tier 3)
│   ├── RetryWrapper
│   ├── PerformanceBenchmark
│   ├── Logger
│   ├── AutoPushPrompt
│   ├── MaintenancePush
│   ├── HydrationBenchmark
│   ├── HydrationMonitor
│   └── HydrationDashboard
└── Role Refinement
    ├── RoleRefinementSystem
    ├── RoleDefinition
    └── RoleRefinementResult
```

#### **Data Flow**
```
Input Task → System Integration → Optimization Loop → Metrics Dashboard
    ↓              ↓                    ↓                ↓
ModelSwitcher → Assertion Framework → Role Refinement → Performance Tracking
```

### **Implementation Patterns**

#### **1. Virtual Environment Management**
```python
# Virtual environment setup for DSPy
import subprocess
import sys
from pathlib import Path

def setup_dspy_environment():
    """Set up DSPy virtual environment with all dependencies."""

    # Create virtual environment
    venv_path = Path("dspy_env")
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)])

    # Install DSPy and dependencies
    pip_path = venv_path / "bin" / "pip"
    subprocess.run([str(pip_path), "install", "dspy-ai", "torch", "transformers"])

    return venv_path
```

#### **2. Model Configuration**
```python
# DSPy model configuration
import dspy
from dspy.teleprompt import BootstrapFewShot

def configure_dspy_models():
    """Configure DSPy with multiple model options."""

    # Configure primary model (Mistral-7B via Ollama)
    dspy.configure(
        lm=dspy.Ollama(model="mistral:7b-instruct"),
        rm=dspy.ColBERTv2(endpoint="http://localhost:8893/colbertv2"
    )

    # Configure backup models
    backup_models = {
        "gpt-4": dspy.OpenAI(model="gpt-4"),
        "claude": dspy.Anthropic(model="claude-3-sonnet-20240229")
    }

    return backup_models
```

#### **3. Optimization Loop Implementation**
```python
# DSPy optimization loop
class DSPyOptimizationLoop:
    """Implements the DSPy optimization loop."""

    def __init__(self, predictor, optimizer):
        self.predictor = predictor
        self.optimizer = optimizer
        self.metrics = []

    def optimize(self, training_data, validation_data, max_iterations=10):
        """Run optimization loop."""

        for iteration in range(max_iterations):
            # Create phase
            self.predictor = self.optimizer.optimize(
                self.predictor,
                training_data
            )

            # Evaluate phase
            metrics = self.evaluate(validation_data)
            self.metrics.append(metrics)

            # Check convergence
            if self.check_convergence():
                break

        return self.predictor, self.metrics
```

### **Integration Patterns**

#### **1. RAG System Integration**
```python
# DSPy RAG system integration
from dspy_modules.rag_system import RAGSystem
from dspy_modules.model_switcher import ModelSwitcher

class DSPyRAGIntegration:
    """Integrates DSPy with RAG system."""

    def __init__(self):
        self.rag_system = RAGSystem()
        self.model_switcher = ModelSwitcher()

    def query_with_rag(self, question: str, context: str = None):
        """Query using RAG system with DSPy."""

        # Get relevant context
        if not context:
            context = self.rag_system.search(question)

        # Use model switcher to select best model
        result = self.model_switcher.forward(
            task=question,
            task_type="qa",
            context=context,
            role="researcher"
        )

        return result
```

#### **2. Assertion Framework Integration**
```python
# DSPy assertion framework integration
from dspy_modules.assertions import CodeQualityValidator, LogicValidator

class DSPyAssertionIntegration:
    """Integrates DSPy with assertion framework."""

    def __init__(self):
        self.code_validator = CodeQualityValidator()
        self.logic_validator = LogicValidator()

    def validate_code(self, code: str, language: str = "python"):
        """Validate code using assertion framework."""

        result = self.code_validator.forward(
            code=code,
            language=language,
            standards="pep8"
        )

        return result

    def validate_logic(self, logic: str, requirements: dict):
        """Validate logic using assertion framework."""

        result = self.logic_validator.forward(
            logic=logic,
            requirements=requirements,
            context="development"
        )

        return result
```

## 🔧 How-To

### DSPy Integration
1. **Understand DSPy architecture** and components
2. **Set up DSPy configuration** and environment
3. **Implement integration patterns** and best practices
4. **Configure performance monitoring** and optimization
5. **Test and validate** DSPy integration

### DSPy v2/v3 Implementation
1. **Review DSPy v2/v3 architecture** and changes
2. **Update existing integrations** to v2/v3 patterns
3. **Implement new v2/v3 features** and capabilities
4. **Optimize performance** for v2/v3 requirements
5. **Validate and test** v2/v3 implementation

### Signature Implementation
1. **Design appropriate signatures** for your tasks
2. **Implement signature patterns** following DSPy conventions
3. **Test signature functionality** with sample data
4. **Optimize signature performance** and efficiency
5. **Integrate signatures** with existing systems

### RAG System Integration
1. **Set up RAG system** with vector database
2. **Configure DSPy RAG signatures** and patterns
3. **Implement query processing** and answer generation
4. **Optimize retrieval** and generation performance
5. **Test and validate** RAG system integration

## 📋 Checklists

### DSPy Integration Checklist
- [ ] **DSPy architecture understood** and documented
- [ ] **Configuration and environment** set up properly
- [ ] **Integration patterns implemented** and tested
- [ ] **Performance monitoring and optimization** in place
- [ ] **Error handling and recovery mechanisms** implemented
- [ ] **Testing and validation completed**

### DSPy v2/v3 Implementation Checklist
- [ ] **DSPy v2/v3 architecture reviewed** and understood
- [ ] **Existing integrations updated** to v2/v3 patterns
- [ ] **New v2/v3 features implemented** and tested
- [ ] **Performance optimized** for v2/v3 requirements
- [ ] **Validation and testing completed** for v2/v3
- [ ] **Documentation updated** for v2/v3 implementation

### Signature Implementation Checklist
- [ ] **Signatures designed** for specific tasks
- [ ] **Signature patterns implemented** following conventions
- [ ] **Signature functionality tested** with sample data
- [ ] **Signature performance optimized** and efficient
- [ ] **Signatures integrated** with existing systems
- [ ] **Signature documentation** complete and accurate

### RAG System Checklist
- [ ] **RAG system set up** with vector database
- [ ] **DSPy RAG signatures configured** and tested
- [ ] **Query processing implemented** and optimized
- [ ] **Answer generation working** correctly
- [ ] **Performance benchmarks** met
- [ ] **Integration testing** completed

## 🔗 Interfaces

### DSPy Framework
- **DSPy Core**: Main framework functionality and APIs
- **DSPy Agents**: Agent system implementation and management
- **DSPy Schema**: Configuration and schema management
- **DSPy Performance**: Performance monitoring and optimization

### Integration Points
- **Memory Systems**: Context and state management integration
- **External APIs**: Connection to external services and data sources
- **Monitoring Systems**: Performance and health monitoring
- **Security Systems**: Access control and authentication

### RAG System
- **Vector Database**: PostgreSQL with pgvector for document storage
- **Search Engine**: BM25 and vector similarity search
- **Model Integration**: Mistral-7B via Ollama for generation
- **Context Management**: Memory systems for context preservation

## 📚 Examples

### DSPy Integration Example
```python
# DSPy integration example
import dspy
from dspy.teleprompt import BootstrapFewShot

# Configure DSPy
dspy.configure(lm=dspy.OpenAI(model="gpt-4"))

# Define signature
class TaskSignature(dspy.Signature):
    """Complete the given task."""
    task = dspy.InputField()
    solution = dspy.OutputField(desc="The solution to the task")

# Create predictor
predictor = dspy.Predict(TaskSignature)

# Use predictor
result = predictor(task="Implement a simple calculator")
print(result.solution)
```

### DSPy v2/v3 Example
```python
# DSPy v2/v3 implementation example
import dspy
from dspy.primitives import ChainOfThought

# Configure DSPy v2/v3
dspy.configure(lm=dspy.OpenAI(model="gpt-4"))

# Define v2/v3 signature with improved structure
class EnhancedTaskSignature(dspy.Signature):
    """Enhanced task completion with reasoning."""
    task = dspy.InputField(desc="The task to complete")
    reasoning = dspy.OutputField(desc="Step-by-step reasoning")
    solution = dspy.OutputField(desc="The final solution")

# Create v2/v3 predictor with chain of thought
predictor = ChainOfThought(EnhancedTaskSignature)

# Use enhanced predictor
result = predictor(task="Design a user authentication system")
print(f"Reasoning: {result.reasoning}")
print(f"Solution: {result.solution}")
```

### RAG System Example
```python
# DSPy RAG system example
from dspy_modules.rag_system import RAGSystem

# Initialize RAG system
rag = RAGSystem()

# Query with RAG
result = rag.query(
    query="What are the main features of our system?",
    max_results=5
)

print(f"Answer: {result.answer}")
print(f"Sources: {result.sources}")
```

### Model Switcher Example
```python
# DSPy model switcher example
from dspy_modules.model_switcher import ModelSwitcher

# Initialize model switcher
switcher = ModelSwitcher()

# Use model switcher for different tasks
coding_result = switcher.forward(
    task="Write a Python function",
    task_type="coding",
    role="coder",
    complexity="simple"
)

planning_result = switcher.forward(
    task="Plan a new feature",
    task_type="planning",
    role="planner",
    complexity="complex"
)

print(f"Coding: {coding_result.result}")
print(f"Planning: {planning_result.result}")
```

## 🔗 Related Guides

- **Getting Started**: `400_00_getting-started-and-index.md`
- **System Overview**: `400_03_system-overview-and-architecture.md`
- **Memory Systems**: `400_06_memory-and-context-systems.md`
- **Coding Standards**: `400_05_coding-and-prompting-standards.md`

## 📚 References

- **Migration Map**: `migration_map.csv`
- **PRD**: `artifacts/prd/PRD-B-1035-400_guides-Consolidation.md`
- **Original DSPy**: Various DSPy-related files (now stubs)
- **DSPy Documentation**: Official DSPy framework documentation
- **Model Switcher**: `dspy-rag-system/src/dspy_modules/model_switcher.py`
- **RAG System**: `dspy-rag-system/src/dspy_modules/rag_system.py`
- **Assertion Framework**: `dspy-rag-system/src/dspy_modules/assertions.py`

## 📋 Changelog

- **2025-08-28**: Created as part of B-1035 consolidation
- **2025-08-28**: Consolidated DSPy framework guides
- **2025-08-28**: Merged content from:
  - `400_dspy-ai-framework.md`
  - `400_dspy-integration-guide.md`
  - `400_dspy-schema-reference.md`
  - `400_dspy-v2-technical-implementation-guide.md`
