

# DSPy Development Context

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Deep technical context for DSPy integration and RAG system implementation | When working with DSPy modules,
implementing RAG systems, or debugging AI agents | Review the architecture overview and implementation status, then
check the roadmap for next steps |

- **Purpose**: Deep technical context for DSPy integration and RAG
- **Read after**: `100_memory/100_cursor-memory-context.md` → `000_core/000_backlog.md` →
`400_guides/400_system-overview.md`
- **Key**: modules, guard-rails, fast-path, vector store, document processor, roadmap

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

<!-- ANCHOR: quick-start -->
{#quick-start}

## ⚡ Quick Start

- Run dashboard: `python3 dspy-rag-system/src/dashboard.py`
- Ask questions: Use the web dashboard or run `python3 dspy-rag-system/src/dashboard.py`
- Run tests: `./dspy-rag-system/run_tests.sh`

### AI Development Ecosystem Context

This DSPy implementation is part of a comprehensive AI-powered development ecosystem that transforms ideas into working
software using AI agents (Cursor Native AI + Specialized Agents). The ecosystem provides structured workflows, automated
task processing, and intelligent error recovery to make AI-assisted development efficient and reliable.

**Key Components:**

- **Planning Layer**: PRD Creation, Task Generation, Process Management
- **AI Execution Layer**: Cursor Native AI (Foundation), Specialized Agents (Enhancements)
- **Core Systems**: DSPy RAG System, N8N Workflows, Dashboard, Testing Framework
- **Supporting Infrastructure**: PostgreSQL + PGVector, File Watching, Notification System

<!-- ANCHOR_KEY: quick-start -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

<!-- ANCHOR: system-overview -->

## 🎯 System Overview

High-level summary of DSPy's role in the ecosystem and implementation status.

### Current Implementation Status

- **Status**: ✅ **DSPy Multi-Agent System COMPLETED**
- **B-1003**: ✅ **COMPLETED** - True local model inference with Cursor AI integration
- **Model Integration**: Cursor Native AI (orchestration) + Local DSPy Models (Llama 3.1 8B, Mistral 7B, Phi-3.5 3.8B)
- **Architecture**: Multi-Agent DSPy with sequential model switching
- **Database**: PostgreSQL with pgvector extension
- **Framework**: DSPy with full signatures, modules, and structured programming
- **Hardware Optimization**: Sequential loading for M4 Mac (128GB RAM) constraints
- **Research Integration**: ✅ **READY**
  - DSPy assertions, teleprompter optimization, hybrid search

<!-- ANCHOR: core-components -->

### Core Components

1. **Model Switcher** (`src/dspy_modules/model_switcher.py`) - ✅ **COMPLETED**
   - Sequential model switching for hardware constraints
   - Task-based and role-based model selection
   - Full DSPy signatures and structured I/O

2. **Cursor Integration** (`cursor_integration.py`) - ✅ **COMPLETED**
   - Clean interface for Cursor AI to orchestrate local models
   - Specialized functions for different task types
   - Error handling and fallback mechanisms

3. **Vector Store** (`src/dspy_modules/vector_store.py`)
4. **Document Processor** (`src/dspy_modules/document_processor.py`)
5. **Web Dashboard** (`src/dashboard.py`)

## 🎉 **B-1003 DSPy Multi-Agent System: COMPLETED**

### **✅ Implementation Summary**

**B-1003 DSPy Multi-Agent System Implementation** has been successfully completed, delivering a production-ready system that replaces Cursor context engineering with true local model inference.

### **🚀 Key Achievements**

1. **True DSPy Implementation**
   - ✅ Full DSPy signatures: `LocalTaskSignature`, `MultiModelOrchestrationSignature`, `ModelSelectionSignature`
   - ✅ Enhanced modules: `IntelligentModelSelector`, `LocalTaskExecutor`, `MultiModelOrchestrator`
   - ✅ Structured I/O with proper input/output contracts

2. **Local Model Integration**
   - ✅ **Ollama Integration**: Direct connection to local models via `dspy.LM("ollama/model_name")`
   - ✅ **Model Support**: Llama 3.1 8B, Mistral 7B, Phi-3.5 3.8B
   - ✅ **Hardware Optimization**: Sequential loading for M4 Mac (128GB RAM) constraints

3. **Cursor AI Integration Bridge**
   - ✅ **Clean Interface**: `cursor_integration.py` with simple function calls
   - ✅ **Specialized Functions**: `quick_task()`, `code_generation()`, `smart_orchestration()`
   - ✅ **Error Handling**: Graceful fallbacks to Cursor AI when local models fail

4. **Multi-Model Orchestration**
   - ✅ **Plan → Execute → Review**: Multi-model workflow
   - ✅ **Task-Based Selection**: Intelligent model routing based on task type
   - ✅ **Role-Based Selection**: Different models for different AI roles

### **🔧 Technical Architecture**

```python
# Model Switcher Configuration
LOCAL_MODEL_CAPABILITIES = {
    LocalModel.LLAMA_3_1_8B: ModelCapabilities(
        model=LocalModel.LLAMA_3_1_8B,
        max_context=8192,
        reasoning_strength=0.8,
        code_generation=0.8,
        speed=0.85,
        memory_usage_gb=16.0,
        best_for=["planning", "research", "reasoning", "general_purpose", "moderate_coding"],
        load_time_seconds=15.0,
    ),
    # ... Mistral 7B and Phi-3.5 3.8B configurations
}

# Cursor AI Integration
def quick_task(task: str, task_type: str = "general_purpose") -> str:
    """Quick single-model task execution for Cursor AI"""
    result = cursor_execute_task(task, task_type, "general")
    return result["result"] if result["success"] else f"Error: {result['error']}"
```

### **📊 Performance Metrics**

- **Models Supported**: 3 (Llama 3.1 8B, Mistral 7B, Phi-3.5 3.8B)
- **DSPy Signatures**: 3 (LocalTask, MultiModelOrchestration, ModelSelection)
- **Integration Functions**: 7 (quick_task, smart_orchestration, code_generation, etc.)
- **Test Results**: ✅ All tests passing with local model inference
- **Hardware Efficiency**: Sequential loading within memory constraints

### **🎯 Usage Examples**

```python
# Cursor AI can now call these functions:
from cursor_integration import quick_task, smart_orchestration, code_generation

# Quick single-model task
result = quick_task("Write a Python function to calculate fibonacci numbers")

# Multi-model orchestration
orchestration = smart_orchestration("Create a complete web application")

# Specialized code generation
code = code_generation("function to sort a list", "python")
```

### **🔗 Integration Points**

- **Cursor AI**: Orchestrates local models via clean function interfaces
- **Existing DSPy System**: Integrates with vector store and document processor
- **Hardware Constraints**: Optimized for M4 Mac with 128GB RAM
- **Error Handling**: Graceful fallbacks to Cursor AI when needed

---

## 🚀 Enhanced Architecture: v0.3.2 Research-Optimized Router

### Phase 1: Research-Enhanced Implementation

```python
# v0.3.2 Research-Optimized Configuration

ENABLED_AGENTS = ["IntentRouter", "RetrievalAgent", "CodeAgent", "PlanAgent", "ResearchAgent"]
MODELS = {
    "cursor-native-ai": "always",  # Always available
    "specialized-agents": "on-demand"  # Load when needed
}
FEATURE_FLAGS = {
    "DEEP_REASONING": 0,
    "CLARIFIER": 0,
    "DSPY_ASSERTIONS": 1,  # Enable DSPy assertions for validation
    "TELEPROMPTER_OPTIMIZATION": 1,  # Enable automatic prompt optimization
    "HYBRID_SEARCH": 1,  # Enable hybrid search (dense + sparse)
    "SPAN_LEVEL_GROUNDING": 1  # Enable precise source attribution
}
MEMORY_STORE = "postgres_diff_no_tombstones"
DSPY_CACHE_ENABLED = True  # Enable DSPy caching for performance
```

<!-- ANCHOR: runtime-guard-rails -->

## Runtime Guard-Rails

Operational safety checks to prevent overload and maintain stability.

```python
# RAM pressure check before loading
if psutil.virtual_memory().percent > 85:
    raise ResourceBusyError("High RAM pressure, try again later.")

# Model janitor coroutine
for name, mdl in model_pool.items():
    if mdl.last_used > 600 and mdl.size_gb > 15:
        mdl.unload()

```html

<!-- ANCHOR: fast-path -->

## Fast-Path Bypass

Short-circuit path for trivial queries that don't need deep reasoning.

```python
# Fast-path bypass (<50 chars & no code tokens)
def is_fast_path(query: str) -> bool:
    return len(query) < 50 and "code" not in query.lower()

# Two flows:
# Fast path → RetrievalAgent
# Full path → Clarifier → Intent → Plan → loop
```html

## 📊 Current Architecture

<!-- ANCHOR: module-structure -->

### DSPy Module Structure

Excerpts only; see `src/dspy_modules/vector_store.py` and related modules for full implementations.

#### 1. Hybrid Vector Store (`dspy_modules/vector_store.py`)

```python
# Core DSPy Signatures

class QueryRewriteSignature(Signature):
    original_query = InputField(desc="The original user query")
    domain_context = InputField(optional=True, desc="Optional domain-specific vocabulary and context")
    rewritten_query = OutputField(desc="Clear, specific query optimized for retrieval")
    sub_queries = OutputField(desc="List of decomposed sub-queries for multi-hop reasoning")
    search_terms = OutputField(desc="Key terms to focus on during retrieval")

class AnswerSynthesisSignature(Signature):
    question = InputField(desc="The original question")
    retrieved_chunks = InputField(desc="Retrieved document chunks with span information")
    answer = OutputField(desc="Comprehensive, well-structured answer with citations")
    confidence = OutputField(desc="Confidence level (0-1)")
    sources = OutputField(desc="Cited source documents with span offsets")
    reasoning = OutputField(desc="Step-by-step reasoning process")
    citations = OutputField(desc="List of source documents and character spans used")

class ChainOfThoughtSignature(Signature):
    question = InputField(desc="The question to answer")
    context = InputField(desc="Retrieved context")
    reasoning_steps = OutputField(desc="Step-by-step reasoning")
    final_answer = OutputField(desc="Final synthesized answer")

class ReActSignature(Signature):
    question = InputField(desc="The question to answer")
    context = InputField(desc="Available context")
    thought = OutputField(desc="Reasoning about the question")
    action = OutputField(desc="What action to take (search, synthesize, etc.)")
    observation = OutputField(desc="Result of the action")
    answer = OutputField(desc="Final answer based on reasoning")

## 2. Core DSPy Modules

**QueryRewriter Module:**
```python
class QueryRewriter(Module):
    def forward(self, query: str, domain_context: str = "") -> Dict[str, Any]:
        # Pre-RAG query rewriting and decomposition
        # Handles complex queries with logical operators
        # Generates sub-queries for multi-hop reasoning

**AnswerSynthesizer Module:**
```python
@dspy.assert_transform_module
class AnswerSynthesizer(Module):
    def forward(self, question: str, retrieved_chunks: List[Dict]) -> Dict[str, Any]:
        # Post-RAG answer synthesis and structuring with research-based validation
        # Combines retrieved chunks into coherent answers
        # Provides confidence scores and source citations

        # Generate answer with DSPy optimization
        answer = self.lm(f"Question: {question}\nContext: {retrieved_chunks}\nAnswer:")

        # Research-based assertions for validation
        dspy.Assert(self.contains_citations(answer), "Answer must include source citations")
        dspy.Assert(len(answer) > 50, "Answer must be comprehensive")
        dspy.Assert(self.has_span_references(answer), "Answer must reference specific spans")

        # Extract confidence and validate
        confidence = self.extract_confidence(answer)
        dspy.Assert(0 <= confidence <= 1, "Confidence must be between 0 and 1")

        return {
            "answer": answer,
            "confidence": confidence,
            "sources": self.extract_sources(answer),
            "citations": self.extract_citations(answer)
        }
```

**ChainOfThoughtReasoner Module:**
```python
class ChainOfThoughtReasoner(Module):
    def forward(self, question: str, context: str) -> Dict[str, Any]:
        # Structured reasoning over retrieved content
        # Step-by-step logical analysis
        # Final answer synthesis with reasoning steps
```

**ReActReasoner Module:**
```python
class ReActReasoner(Module):
    def forward(self, question: str, context: str) -> Dict[str, Any]:
        # ReAct (Reasoning + Acting) pattern
        # Iterative reasoning with action planning
        # Guarded against infinite loops (max 5 steps)
```

**Research-Based Specialized Agent Modules:**

**PlanAgent Module:**
```python
@dspy.assert_transform_module
class PlanAgent(Module):
    def forward(self, task: str, context: str) -> Dict[str, Any]:
        # Task planning and decomposition with validation

        plan = self.lm(f"Task: {task}\nContext: {context}\nPlan:")

        # Assert plan is structured and actionable
        dspy.Assert(self.is_structured_plan(plan), "Plan must be structured and actionable")
        dspy.Assert(len(plan.split('\n')) >= 3, "Plan must have at least 3 steps")

        return {"plan": plan, "steps": self.extract_steps(plan)}
```

**CodeAgent Module:**
```python
@dspy.assert_transform_module
class CodeAgent(Module):
    def forward(self, requirements: str, context: str) -> Dict[str, Any]:
        # Code generation with compilation validation

        code = self.lm(f"Requirements: {requirements}\nContext: {context}\nCode:")

        # Assert code compiles (research-based validation)
        dspy.Assert(self.code_compiles(code), "Generated code must compile")
        dspy.Assert(self.has_tests(code), "Code must include tests")
        dspy.Assert(self.follows_style_guide(code), "Code must follow style guide")

        return {"code": code, "tests": self.extract_tests(code)}
```

**Coder Role Integration with CodeAgent:**
The coder role in the memory rehydration system leverages the CodeAgent module for focused coding tasks:

**When to Use Coder vs Implementer Role:**
- **Coder Role**: For specific coding tasks, implementation details, and best practices
  - Use when: Writing functions, debugging code, applying coding standards
  - Context: `400_guides/400_comprehensive-coding-best-practices.md`, `400_guides/400_code-criticality-guide.md`
- **Implementer Role**: For broader system implementation and architecture
  - Use when: System design, integration, architectural decisions
  - Context: `100_memory/104_dspy-development-context.md`, DSPy framework details

**Coder Role Usage Examples:**
```bash
# For specific coding tasks
python3 scripts/cursor_memory_rehydrate.py coder "implement authentication function with proper error handling"

# For debugging and code review
python3 scripts/cursor_memory_rehydrate.py coder "fix undefined variable error in database query"

# For best practices application
python3 scripts/cursor_memory_rehydrate.py coder "apply Python 3.12 typing best practices to function"
```

**Best Practices for Coding Context:**
- Always include specific requirements and constraints
- Reference existing code patterns when applicable
- Focus on implementation details rather than architecture
- Include error handling and testing considerations

**🔧 COMPREHENSIVE CODER ROLE INSTRUCTIONS**

**Core Coder Role Behavior - ALWAYS FOLLOW:**

1. **Memory Rehydration Protocol**: Start every coding session with `python3 scripts/cursor_memory_rehydrate.py coder "task description"`
2. **Example-First Approach**: Before writing new code, search existing codebase for patterns
3. **Code Reuse Heuristic**: Apply find-or-build approach (search-before-write, 70% reuse, tests-first)
4. **Python 3.12 Standards**: Use absolute imports, PEP 585 generics, type hints
5. **Comprehensive Error Handling**: Include try/catch blocks, validation, conflict prevention
6. **Test-First Development**: Create unit tests before implementation (TDD)
7. **Use Existing Tools**: Leverage extensive toolchain already built
8. **File Analysis Protocol**: Use 6-phase analysis process for any file operations
9. **Security First**: Input validation, prompt sanitization, access controls
10. **Critical File Protection**: Understand Tier 1 (critical) vs Tier 2/3 files
11. **Exclusions Policy**: Never reference `600_archives/**` or `docs/legacy/**`

**Technical Standards - REQUIRED:**
- **Python 3.12** with absolute imports (no sys.path hacks)
- **Type hints** for all functions using PEP 585 generics
- **Google style docstrings** with comprehensive documentation
- **Black formatting** with Ruff linting
- **Comprehensive error handling** with specific exception types
- **Unit tests** for all new functionality
- **Pre-commit validation** using existing scripts
- **Maximum function length**: 50 lines
- **Code reuse target**: 70% existing code, 30% new code
- **Documentation**: TL;DR section required for new modules

**Safety Protocol - BEFORE ANY CHANGES:**
1. Read core memory context (`100_memory/100_cursor-memory-context.md`)
2. Check current backlog (`000_core/000_backlog.md`)
3. Understand file organization (000-699 prefixes)
4. Apply tier-based analysis for any file operations
5. Run conflict detection (`python scripts/conflict_audit.py`)
6. Validate documentation (`python scripts/doc_coherence_validator.py`)

**Critical File Protection:**
- **Tier 1 files**: NEVER suggest removal - core workflow files
- **Tier 2 files**: Extensive analysis required - documentation guides
- **Tier 3 files**: Archive rather than delete - legacy files
- **Tier 4 files**: Safe to remove with validation

**Quality Gates - MUST PASS:**
- **Code Review**: Standards compliance, logic correctness
- **Testing**: Unit tests, integration tests
- **Documentation**: Completeness and clarity
- **Security**: Vulnerability prevention
- **Performance**: Efficiency validation

**⚡ CODER ROLE QUICK REFERENCE**

**Essential Commands:**
```bash
# Core development workflow
python3.12 scripts/single_doorway.py generate "description"
python3.12 scripts/process_tasks.py --execute-all
python scripts/error_handler.py --test

# Validation and testing
python scripts/conflict_audit.py --full
python scripts/doc_coherence_validator.py --check-all
./dspy-rag-system/run_tests.sh --tiers 1 --kinds smoke

# System health and status
python scripts/system_health_check.py --deep
./dspy-rag-system/check_status.sh

# Memory and context
python scripts/cursor_memory_rehydrate.py coder "task description"
python scripts/update_cursor_memory.py

# Quick testing commands
python3 -m pytest -m "unit and not deprecated" -v                    # Unit tests
python3 -m pytest -m "integration and not deprecated" -v             # Integration tests
python3 -m pytest -m "performance and not deprecated" -v             # Performance tests
python3 -m pytest -m "security and not deprecated" -v                # Security tests
./dspy-rag-system/run_comprehensive_tests.sh                         # All system tests

# Code quality tools
black src/ scripts/ tests/                                           # Format code
ruff check src/ scripts/ tests/                                      # Lint code
pyright src/ scripts/ tests/                                         # Type check
```

**Safety Checklist - BEFORE ANY CHANGES:**
- [ ] Read `100_memory/100_cursor-memory-context.md` (current state)
- [ ] Check `000_core/000_backlog.md` (active priorities)
- [ ] Understand file organization (000-699 prefixes)
- [ ] Apply tier-based analysis for file operations
- [ ] Run `python scripts/conflict_audit.py --full`
- [ ] Validate with `python scripts/doc_coherence_validator.py --check-all`

**Critical File Tiers:**
- **Tier 1**: NEVER remove - core workflow files (`scripts/process_tasks.py`, etc.)
- **Tier 2**: Extensive analysis required - documentation guides
- **Tier 3**: Archive rather than delete - legacy files
- **Tier 4**: Safe to remove with validation

**File Priority System (Reading Order):**
- **HIGH Priority**: `100_memory/100_cursor-memory-context.md`, `400_guides/400_system-overview.md`
- **MEDIUM Priority**: `100_memory/104_dspy-development-context.md`, coding guides in `400_guides/`
- **LOW Priority**: `100_memory/100_backlog-guide.md`, research files in `500_research/`

**Exclusions Policy:**
- **NEVER reference**: `600_archives/**` or `docs/legacy/**`
- **Route legacy code**: Move to `600_archives/` when deprecated
- **Update memory**: Run `python scripts/update_cursor_memory.py` after major changes

**Example-First Approach:**
1. Search existing codebase for similar patterns
2. Check `400_guides/` for relevant examples
3. Review `600_archives/` for lessons learned
4. Reference production systems in `dspy-rag-system/src/`
5. Use existing scripts as templates

**Tool Usage Standards:**
- **Prefer `codebase_search`** over grep for semantic searches
- **Use `todo_write`** for tracking multi-step tasks
- **Use `update_memory`** for important project decisions
- **Run linter checks** before committing changes
- **Use existing scripts** rather than creating new ones

**Quality Gates Checklist:**
- [ ] Code follows Python 3.12 standards
- [ ] Type hints included (PEP 585)
- [ ] Google style docstrings
- [ ] Unit tests written and passing
- [ ] Error handling comprehensive
- [ ] Security validation passed
- [ ] Documentation updated
- [ ] Pre-commit validation passed
- [ ] Function length ≤ 50 lines
- [ ] Code reuse target met (70% existing, 30% new)
- [ ] TL;DR section added for new modules

**Documentation Standards:**
- **All documentation** must follow markdown standards
- **Each document** must have a single h1 title matching filename
- **TL;DR section** required at top of core docs
- **Cross-references** must be maintained between related files
- **Documentation hierarchy**: 000-099 (core), 100-199 (guides), etc.

**Git Workflow:**
- **Commit messages** must be descriptive and reference issues
- **PRs require** documentation updates when applicable
- **Feature branches** named: `feature/description`
- **Bug fix branches** named: `fix/description`
- **Squash commits** before merging

**🧪 COMPREHENSIVE TESTING GUIDE**

**Test Categories and When to Run:**

**Unit Tests:**
```bash
# Run unit tests for specific module
python3 -m pytest tests/test_specific_module.py -v

# Run all unit tests (excluding deprecated)
python3 -m pytest -m "unit and not deprecated" -v

# Run unit tests with coverage
python3 -m pytest -m "unit and not deprecated" --cov=src --cov-report=html
```

**Integration Tests:**
```bash
# Run integration tests
python3 -m pytest -m "integration and not deprecated" -v

# Run specific integration test
python3 -m pytest tests/test_integration.py::test_specific_function -v
```

**Performance Tests:**
```bash
# Run performance benchmarks
python3 -m pytest -m "performance and not deprecated" -v

# Run specific performance test
python3 -m pytest tests/test_performance.py::test_response_time -v
```

**Security Tests:**
```bash
# Run security validation
python3 -m pytest -m "security and not deprecated" -v

# Run security scanning
python scripts/security_scan.py --full
```

**System Tests:**
```bash
# Run comprehensive system tests
./dspy-rag-system/run_comprehensive_tests.sh

# Run specific test tiers
./dspy-rag-system/run_tests.sh --tiers 1 --kinds smoke
./dspy-rag-system/run_tests.sh --tiers 1,2 --kinds unit,integration
```

**Test Markers and Selection:**
```bash
# Test by complexity tiers
python3 -m pytest -m "tier1 and not deprecated"  # Critical functionality
python3 -m pytest -m "tier2 and not deprecated"  # Important functionality
python3 -m pytest -m "tier3 and not deprecated"  # Supporting functionality

# Test by kind
python3 -m pytest -m "smoke and not deprecated"     # Quick validation
python3 -m pytest -m "unit and not deprecated"      # Individual components
python3 -m pytest -m "integration and not deprecated" # Component interaction
python3 -m pytest -m "performance and not deprecated" # Speed and efficiency
python3 -m pytest -m "security and not deprecated"   # Security validation
```

**🔧 TOOL USAGE GUIDE**

**When to Use Which Tools:**

**Code Quality Tools:**
```bash
# Code formatting (run before commits)
black src/ scripts/ tests/
ruff check src/ scripts/ tests/
ruff format src/ scripts/ tests/

# Type checking
pyright src/ scripts/ tests/

# Import sorting
isort src/ scripts/ tests/
```

**Validation Tools:**
```bash
# Conflict detection (before major changes)
python scripts/conflict_audit.py --full

# Documentation validation (before commits)
python scripts/doc_coherence_validator.py --check-all

# System health check (periodic)
python scripts/system_health_check.py --deep

# Security scanning (before deployment)
python scripts/security_scan.py --full
```

**Development Workflow Tools:**
```bash
# Start new development workflow
python3.12 scripts/single_doorway.py generate "feature description"

# Execute backlog items
python3.12 scripts/process_tasks.py --execute-all

# Error handling and recovery
python scripts/error_handler.py --test

# State management
python scripts/state_manager.py --status
```

**Testing Tools:**
```bash
# Run specific test suites
./dspy-rag-system/run_tests.sh --tiers 1 --kinds smoke
./dspy-rag-system/run_tests.sh --tiers 1,2 --kinds unit,integration

# Performance testing
python scripts/performance_benchmark.py --full

# Memory testing
python scripts/memory_benchmark.py --test
```

**Monitoring and Debugging:**
```bash
# System status
./dspy-rag-system/check_status.sh

# Mission dashboard
./dspy-rag-system/start_mission_dashboard.sh

# Production monitoring
python src/monitoring/production_monitor.py &

# Database health
python scripts/database_sync_check.py --auto-update
```

**Memory and Context Tools:**
```bash
# Memory rehydration for specific roles
python3 scripts/cursor_memory_rehydrate.py coder "task description"
python3 scripts/cursor_memory_rehydrate.py implementer "task description"
python3 scripts/cursor_memory_rehydrate.py planner "task description"

# Memory context updates
python scripts/update_cursor_memory.py

# Few-shot scaffolding
python scripts/few_shot_cognitive_scaffolding.py --role coder --task "description"
```

**Pre-commit Validation:**
```bash
# Run all pre-commit checks
./scripts/pre_commit_doc_validation.sh

# Individual validation steps
python scripts/conflict_audit.py --quick
python scripts/doc_coherence_validator.py --check-all
black --check src/ scripts/ tests/
ruff check src/ scripts/ tests/
pyright src/ scripts/ tests/
```

**Emergency and Recovery:**
```bash
# Database recovery
python scripts/auto_recover_database.py

# System rollback
./scripts/rollback_doc.sh

# Error recovery
python scripts/error_handler.py --recover

# State reset
python scripts/state_manager.py --reset
```

**ResearchAgent Module:**
```python
@dspy.assert_transform_module
class ResearchAgent(Module):
    def forward(self, query: str, documents: List[str]) -> Dict[str, Any]:
        # Research and documentation analysis with validation

        analysis = self.lm(f"Query: {query}\nDocuments: {documents}\nAnalysis:")

        # Assert analysis includes citations
        dspy.Assert(self.contains_citations(analysis), "Analysis must include citations")
        dspy.Assert(self.has_span_references(analysis), "Analysis must reference specific spans")

        return {"analysis": analysis, "citations": self.extract_citations(analysis)}
```

<!-- ANCHOR: vector-store -->

### 3. Enhanced Vector Store Integration (Research-Based)

```python
class HybridVectorStore(Module):
    def forward(self, operation: str, **kwargs) -> Dict[str, Any]:
        # Research-based hybrid search: PGVector (dense) + PostgreSQL full-text (sparse)
        # Span-level grounding with character offsets
        # Intelligent chunking using prefix boundaries

        if operation == "search":
            query = kwargs.get("query")
            top_k = kwargs.get("top_k", 10)

            # Hybrid search implementation
            dense_results = self.vector_search(query, top_k)
            sparse_results = self.text_search(query, top_k)

            # Merge and rank results (research-based approach)
            merged_results = self.merge_hybrid_results(dense_results, sparse_results)

            # Add span information for grounding
            results_with_spans = self.add_span_information(merged_results)

            return {"results": results_with_spans, "search_type": "hybrid"}

        elif operation == "insert":
            # Enhanced insertion with span tracking
            document = kwargs.get("document")
            spans = kwargs.get("spans", {})

            # Store with span metadata
            return self.insert_with_spans(document, spans)

    def merge_hybrid_results(self, dense_results, sparse_results):
        # Research-based merging strategy
        # Boost results found by both methods
        # Ensure at least some pure keyword hits
        # Apply intelligent ranking
        pass

    def add_span_information(self, results):
        # Add character offsets for precise citations
        for result in results:
            result["span_start"] = result.get("start_offset", 0)
            result["span_end"] = result.get("end_offset", len(result["text"]))
        return results
```

<!-- ANCHOR: document-processor -->

#### 4. Document Processor

```python
class DocumentProcessor(Module):
    def forward(self, document_path: str) -> Dict[str, Any]:
        # Token-aware chunking with overlap
        # Multi-format support (PDF, CSV, TXT, MD)
        # Config-driven metadata extraction
        # Security validation and file path checking
```

## 🔧 Critical Fixes Implemented

### Enhanced DSPy RAG System Fixes

- ✅ **SIG-1: DSPy Signature Correction**
  - Domain context properly handled in signatures
- ✅ **SIG-2: Safe Complexity Score**
  - Zero-division guard for empty chunks
- ✅ **SIG-3: TTL Cache**
  - Module selector with 60-second expiration
- ✅ **SIG-4: ReAct Loop Guard**
  - Prevents infinite loops with max steps

### Performance Optimizations

- **Connection Pooling**: SimpleConnectionPool for database connections
- **Model Caching**: @lru_cache for SentenceTransformer singleton
- **Bulk Operations**: execute_values for efficient database inserts
- **Token-Aware Chunking**: Prevents context overflow
- **TTL Cache**: Module selector with automatic expiration

### Security Enhancements

- **Path Validation**: Prevents directory traversal attacks
- **Input Sanitization**: Blocklist for prompt injection prevention
- **File Size Limits**: Prevents memory exhaustion
- **UUID Generation**: Prevents document ID collisions
- **Subprocess Security**: Command injection prevention

## 📈 Current Performance Metrics

### System Statistics

- **Total Chunks**: 65+ stored in PostgreSQL
- **File Types**: .txt, .md, .pdf, .csv
- **Database**: PostgreSQL with pgvector
- **LLM**: Cursor Native AI via Cursor IDE
- **Framework**: DSPy with enhanced pre-RAG and post-RAG logic

### Enhanced Capabilities

- **Query Complexity Analysis**: Automatic analysis and module selection
- **Domain Context**: Technical, academic, business, general domains
- **Multi-hop Reasoning**: Sub-query decomposition for complex questions
- **Chain-of-Thought**: Step-by-step reasoning over retrieved content
- **ReAct Reasoning**: Iterative reasoning with action planning

## 🎯 Current Usage Patterns

### Interactive Interface

```bash
# Run enhanced interface
python3 enhanced_ask_question.py

# Available commands:
analyze "What is DSPy?"           # Analyze query complexity
domain technical                  # Set technical domain context
cot "Explain the benefits"        # Force Chain-of-Thought
react "Compare approaches"        # Force ReAct reasoning
```

## Web Dashboard

```bash
# Run hardened web dashboard
python3 src/dashboard.py

# Features:
# - File upload with security validation
# - RAG queries with enhanced processing
# - Real-time system monitoring
# - Document metadata visualization
```

## Programmatic Usage

```python
from utils.rag_compatibility_shim import create_rag_interface

# Create enhanced interface
rag = create_rag_interface()

# Ask questions with different reasoning modes
response = rag.ask("What is DSPy?", use_cot=True, use_react=False)
```

## 🔍 Current Limitations & Areas for Improvement

### Technical Limitations

1. **Model Dependency**: Currently tied to Cursor Native AI
2. **Context Window**: Limited to 3500 tokens for Cursor Native AI
3. **Single Database**: PostgreSQL only, no distributed storage
4. **Local Only**: No cloud deployment or scaling
5. **Memory Usage**: Large models require significant VRAM

### Feature Gaps

1. **Multi-modal Support**: No image or audio processing
2. **Real-time Updates**: No WebSocket-based live updates
3. **Advanced Caching**: No Redis or distributed caching
4. **Model Switching**: No automatic model selection
5. **Advanced Reasoning**: Limited to CoT and ReAct patterns

### Integration Opportunities

1. **External Model Integration**: Not yet integrated for code generation
2. **Dashboard Enhancement**: Could leverage DSPy for metadata extraction
3. **Backlog Integration**: No automated backlog processing
4. **Testing Framework**: Limited DSPy-specific testing
5. **Monitoring**: No advanced performance monitoring

<!-- ANCHOR: roadmap -->

## 🚀 Development Roadmap

### Phase 1: Ultra-Minimal Implementation (1 week)

✅ **COMPLETED**

1. **Core Agents**: IntentRouter, RetrievalAgent, CodeAgent
2. **Model Management**: Cursor Native AI (warm), External models (lazy)
3. **Fast-Path Bypass**: Skip complex routing for simple queries
4. **RAM Pressure Guards**: Prevent memory exhaustion
5. **Postgres Delta Snapshots**: Memory persistence without tombstones
6. **Error Policy & Retry Logic**: Configurable retry with backoff
7. **Environment-Driven Pool**: POOL_MIN/POOL_MAX configuration
8. **RAM Guard Variables**: MODEL_IDLE_EVICT_SECS, MAX_RAM_PRESSURE

### Phase 2: Enhanced Features (1 week)

🔄 **IN PROGRESS**

1. **ReasoningAgent**: Add when DEEP_REASONING=1
2. **Large Model Integration**: Lazy loading for complex reasoning
3. **Performance Monitoring**: Measure latency and memory usage
4. **Error Recovery**: Improved error handling and retry logic
5. **Documentation**: Complete API documentation
6. **Implement regex prompt-sanitiser**: Enhanced security with block-list and whitelist
7. **Add llm_timeout_seconds per-agent setting**: Configurable timeouts for large models

### Phase 3: Advanced Features (1 week)

1. **ClarifierAgent**: Add when CLARIFIER=1
2. **SelfAnswerAgent**: For simple queries
3. **GeneratePlan**: For complex planning tasks
4. **Redis Cache**: For embeddings and frequent queries
5. **WebSocket Streaming**: Real-time updates

## 📊 Current Code Quality

### Strengths

- **Modular Design**: Clean separation of concerns
- **Error Handling**: Comprehensive exception handling
- **Security**: Input validation and sanitization
- **Performance**: Optimized database operations
- **Testing**: Good test coverage for critical components

### Areas for Improvement

- **Code Documentation**: Some modules lack detailed docstrings
- **Type Hints**: Incomplete type annotations
- **Configuration**: Hardcoded values in some places
- **Logging**: Inconsistent logging patterns
- **Error Messages**: Some error messages could be more descriptive

## 🔧 Technical Debt

### Immediate Issues

1. **Hardcoded Configuration**: Some settings should be environment variables
2. **Error Recovery**: Limited retry logic for transient failures
3. **Resource Management**: Some connections not properly closed
4. **Memory Management**: Large documents could cause memory issues
5. **Concurrency**: Limited support for concurrent operations

### Architectural Debt

1. **Tight Coupling**: Some modules are tightly coupled
2. **Interface Inconsistency**: Different modules have different interfaces
3. **Configuration Management**: No centralized configuration system
4. **Dependency Management**: Some dependencies could be optional
5. **Version Compatibility**: Limited testing across different versions

## 🎯 Research-Based Enhancements (Implementation Ready)

### 1. Teleprompter Optimization (Research-Based)

```python
class TeleprompterOptimizer(Module):
    def forward(self, module: Module, training_examples: List[Dict]) -> Module:
        # Research-based automatic prompt optimization
        # Continuous improvement of prompts for accuracy and cost
        # Auto-generate few-shot examples and instructions

        # Configure teleprompter for optimization
        teleprompter = dspy.Teleprompter(module)

        # Optimize using training examples
        optimized_module = teleprompter.compile(
            training_examples,
            metric=self.evaluation_metric
        )

        return optimized_module

    def evaluation_metric(self, example, pred, trace=None):
        # Custom evaluation metric for our use case
        # Consider accuracy, comprehensiveness, citation quality
        pass
```

### 2. DSPy Caching Configuration (Research-Based)

```python
# Enable DSPy caching for performance optimization
dspy.settings.configure(cache_dir="./dspy_cache")

class CachedDSPyModule(Module):
    def __init__(self):
        super().__init__()
        # Enable caching for repeated calls
        self.cache_enabled = True

    def forward(self, *args, **kwargs):
        # DSPy automatically caches LLM call results
        # Repeated calls with identical input won't hit API twice
        # Significant cost and time savings for iterative agents
        pass
```

## 3. Enhanced Document Processor (Research-Based)

```python
class EnhancedDocumentProcessor(Module):
    def forward(self, document_path: str) -> Dict[str, Any]:
        # Research-based intelligent chunking using prefix boundaries
        # Span-level tracking for precise citations
        # Multi-format support with enhanced processing

        # Use prefix boundaries as semantic chunk units
        chunks = self.semantic_chunking(document_path)

        # Add span information for grounding
        chunks_with_spans = self.add_span_tracking(chunks)

        return {"chunks": chunks_with_spans, "metadata": self.extract_metadata(document_path)}

    def semantic_chunking(self, document_path):
        # Use our three-digit prefix system as chunk boundaries
        # Avoid blind size-based splitting
        # Implement sliding windows for large documents
        pass

    def add_span_tracking(self, chunks):
        # Add character offsets for precise citations
        for chunk in chunks:
            chunk["span_start"] = chunk.get("start_offset", 0)
            chunk["span_end"] = chunk.get("end_offset", len(chunk["text"]))
        return chunks
```

### 4. Expected Performance Improvements (Research-Based)

- **Code Quality**: 25-40% improvement over expert-written prompt-chains
- **RAG Accuracy**: 10-25% improvement with hybrid search
- **Response Time**: 30-50% faster with intelligent routing
- **Cost Reduction**: 40-60% savings with model routing and caching
- **Reliability**: 37% → 98% improvement with DSPy assertions

### 5. Implementation Timeline (Research-Based)

- **Week 1-2**: DSPy assertions and optimization
- **Week 3-4**: Hybrid search and span-level grounding
- **Week 5-6**: Teleprompter optimization and caching
- **Week 7-8**: Specialized agent implementation
- **Week 9-10**: Performance monitoring and validation

## 🎯 Research Questions for Deep Analysis

### Architecture & Design

1. How well does the current DSPy implementation scale with larger datasets?
2. What are the bottlenecks in the current pre-RAG and post-RAG pipeline?
3. How effective is the current module selection strategy?
4. What improvements could be made to the reasoning patterns?

### Performance & Optimization

1. How does the system perform with different query complexities?
2. What are the memory usage patterns and optimization opportunities?
3. How effective is the current caching strategy?
4. What performance improvements could be made to the database operations?

### Integration & Extensibility

1. How well does the system integrate with the broader AI Dev Tasks workflow?
2. What opportunities exist for integrating with external models and other AI systems?
3. How extensible is the current DSPy module architecture?
4. What new DSPy patterns could be implemented?

### Quality & Reliability

1. How robust is the current error handling and recovery?
2. What security vulnerabilities exist in the current implementation?
3. How well does the system handle edge cases and failures?
4. What improvements could be made to the testing strategy?

### User Experience

1. How intuitive is the current interface for different user types?
2. What improvements could be made to the query analysis and recommendations?
3. How effective is the current domain context system?
4. What new features would provide the most value to users?

## 📚 Key Files for Analysis

### Core DSPy Implementation

- `src/dspy_modules/vector_store.py` - Hybrid vector store implementation
- `src/dspy_modules/rag_system.py` - Basic RAG system
- `src/dspy_modules/vector_store.py` - Vector storage and retrieval
- `src/dspy_modules/document_processor.py` - Document processing

### User Interfaces

- `enhanced_ask_question.py` - Interactive command-line interface
- `src/dashboard.py` - Web dashboard interface
- `src/templates/dashboard.html` - Dashboard template

### Configuration & Utilities

- `src/utils/metadata_extractor.py` - Metadata extraction
- `src/utils/tokenizer.py` - Token-aware chunking
- `src/utils/logger.py` - Structured logging
- `config/metadata_rules.yaml` - Metadata extraction rules

### Testing & Documentation

- `tests/` - Comprehensive test suite
- `docs/` - System documentation
- `dspy-rag-system/docs/CURRENT_STATUS.md` - Current implementation status

## 🎯 Success Metrics

### Current Performance

- **Query Response Time**: < 5 seconds for simple queries
- **Complex Query Handling**: Multi-hop reasoning for complex questions
- **Accuracy**: High-quality answers with source citations
- **Reliability**: Robust error handling and recovery
- **Scalability**: Handles 1000+ document chunks efficiently

### Quality Indicators

- **Code Quality**: Clean, maintainable, well-documented code
- **Test Coverage**: Comprehensive testing of critical components
- **Security**: Input validation and sanitization
- **Performance**: Optimized database and model operations
- **User Experience**: Intuitive interfaces and helpful error messages

---

This DSPy implementation represents a sophisticated RAG system with enhanced reasoning capabilities, ready for deep research analysis and further development.
