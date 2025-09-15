<!-- ANCHOR_KEY: reference-cards -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["coder", "implementer", "planner"] -->

# Reference Cards

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Quick reference cards for common patterns, tools, and best practices | When implementing features or making technical decisions | Use as quick lookup for established patterns and reference implementations |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Reference cards maintained and current
- **Priority**: 🔧 Medium - Important for implementation guidance
- **Points**: 2 - Moderate complexity, reference importance
- **Dependencies**: 200_setup/200_naming-conventions.md
- **Next Steps**: Add reference cards as patterns emerge from implementation

## 📋 Reference Cards Index

### **DSPy Framework**
- [DSPy 3.0 Migration](#dspy-30-migration)
- [DSPy Multi-Agent](#dspy-multi-agent)
- [DSPy Assertions](#dspy-assertions)
- [DSPy Optimization](#dspy-optimization)
- [Core DSPy Modules (Tier 1)](#core-dspy-modules)
- [Context & Observability (Tier 1)](#context-observability)
- [Production Infrastructure (Tier 2)](#production-infrastructure)
- [Supporting Infrastructure (Tier 3)](#supporting-infrastructure)

### **Development Tools**
- [GitHub Actions](#github-actions)
- [GitHub README](#github-readme)
- [Quality Gates](#quality-gates)
- [Performance Optimization](#performance-optimization)

### **Integration Patterns**
- [Ollama Integration](#ollama-integration)
- [MCP Server Architecture](#mcp-server-architecture)
- [n8n Workflows](#n8n-workflows)
- [Memory Rehydration](#memory-rehydration)

### **Documentation & Automation**
- [Documentation Generation](#documentation-generation)
- [Workflow Automation](#workflow-automation)
- [Automation Patterns](#automation-patterns)
- [Repository Safety](#repository-safety)

### **Research & Validation**
- [Research-Based Design](#research-based-design)
- [Extraction Validation](#extraction-validation)
- [Structured Extraction](#structured-extraction)
- [Extraction Services](#extraction-services)

## 🔧 DSPy Framework

### DSPy 3.0 Migration {#dspy-30-migration}

**Context**: Migration from DSPy 2.6.27 to DSPy 3.0.x for native assertion support and enhanced optimization

**Key Patterns**:
- **Parity-first approach**: Achieve functional parity before enhancements
- **Conservative scope**: Pin version, run smoke tests, validate quality gates
- **Rollback safety**: 10-15% regression threshold with proven rollback procedure
- **Baseline metrics**: Test pass rate, latency, token usage, doc coherence, lint count

**Implementation Checklist**:
- [ ] Capture baseline metrics before migration
- [ ] Create migration branch with rollback script
- [ ] Pin DSPy 3.0.x in requirements
- [ ] Run comprehensive smoke tests
- [ ] Validate performance within 15% regression
- [ ] Test rollback procedure
- [ ] Document migration results

**Common Pitfalls**:
- Over-engineering validation for solo development
- Chasing single-digit performance improvements
- Bundling enhancements with core migration
- Insufficient rollback testing

**Success Criteria**:
- All existing tests pass with DSPy 3.0.x
- Performance regression ≤15%
- Quality gates pass (lint, doc coherence)
- Proven rollback procedure

### DSPy Multi-Agent {#dspy-multi-agent}

**Context**: Implementation of true DSPy multi-agent system with local AI models

**Key Patterns**:
- **Model switching**: Sequential loading for hardware constraints
- **Role-based selection**: Task-based and role-based model selection
- **DSPy signatures**: LocalTaskSignature, MultiModelOrchestrationSignature
- **Hardware optimization**: Sequential loading within memory constraints

**Implementation Components**:
- ModelSwitcher class with task-based selection
- IntelligentModelSelector for role-based routing
- LocalTaskExecutor for model inference
- MultiModelOrchestrator for coordination

**Hardware Considerations**:
- M4 Mac with 128GB RAM constraints
- Sequential model loading to avoid OOM
- Support for Llama 3.1 8B, Mistral 7B, Phi-3.5 3.8B

### DSPy Assertions {#dspy-assertions}

**Context**: Implementation of DSPy assertions for code validation and reliability improvement

**Key Patterns**:
- **Native assertions**: Use dspy.Assert for validation
- **Custom assertion migration**: Replace custom validators with native assertions
- **Reliability improvement**: 37% → 98% reliability improvement target
- **Minimal scope**: Replace only existing assertion touchpoints

**Implementation Approach**:
- Replace two call-sites of custom assertions with dspy.Assert
- Keep behavior equivalent during migration
- No new optimization loops during assertion swap
- Rollback to custom assertions if flakiness emerges

### LangExtract Framework {#langextract}

**Context**: Research-based structured extraction system with span-level grounding and DSPy 3.0 assertion integration

**Key Patterns**:
- **Entity extraction**: Extract entities with types and confidence scores
- **Relation extraction**: Extract relations between entities with validation
- **Fact extraction**: Extract facts with schema validation
- **Span-level grounding**: Character-level span tracking for validation
- **DSPy 3.0 integration**: Native assertions with retry logic

**Implementation Components**:
- EntityExtractor: Research-based entity extraction with span-level grounding
- RelationExtractor: Relation extraction with validation and retry logic
- FactExtractor: Fact extraction with schema validation
- LangExtractSystem: Main orchestration module
- LangExtractInterface: High-level interface for extraction operations

**Usage Pattern**:
```python
from dspy_modules.lang_extract_system import create_lang_extract_interface

interface = create_lang_extract_interface()
result = interface.extract(text, extraction_type)
```

### DSPy Optimization {#dspy-optimization}

**Context**: DSPy v2 optimization techniques from Adam LK transcript

**Key Patterns**:
- **Programming not prompting**: Philosophy shift from prompt engineering
- **Four-part optimization loop**: Create → Evaluate → Optimize → Deploy
- **Advanced optimizers**: LabeledFewShot, BootstrapFewShot, MIPRO
- **Teleprompter integration**: Systematic improvement with measurable metrics

**Optimization Techniques**:
- Assertion-based validation for reliability
- Continuous improvement with measurable metrics
- Systematic optimization approach
- Performance benchmarking and validation

### Core DSPy Modules (Tier 1) {#core-dspy-modules}

**Context**: Critical DSPy system components that form the backbone of the AI development ecosystem

**Key Patterns**:
- **Type-safe integration**: Protocol interfaces and Union types for flexible module handling
- **Hybrid search**: Dense + sparse retrieval with Reciprocal Rank Fusion
- **Span-level grounding**: Character-level span tracking for validation
- **Four-part optimization**: Create → Evaluate → Optimize → Deploy cycle

**Implementation Components**:
- **CursorModelRouter**: Intelligent model selection for Cursor Native AI
- **VectorStore**: Hybrid vector store with PGVector + text search
- **DocumentProcessor**: Document ingestion and chunking with metadata extraction
- **OptimizationLoop**: Four-part optimization loop with Protocol interfaces

**Usage Pattern**:
```python
from dspy_modules.cursor_model_router import CursorModelRouter
from dspy_modules.vector_store import VectorStore
from dspy_modules.document_processor import DocumentProcessor
from dspy_modules.optimization_loop import FourPartOptimizationLoop

# Initialize core modules
router = CursorModelRouter()
vector_store = VectorStore()
processor = DocumentProcessor()
optimizer = FourPartOptimizationLoop()

# Process document with optimization
doc = processor.process("document.pdf")
vector_store.add_document(doc)
result = optimizer.run_cycle({"module": processor, "data": [doc]})
```

### Context & Observability (Tier 1) {#context-observability}

**Context**: Role-aware context assembly and industry-grade observability for AI agent systems

**Key Patterns**:
- **Role-aware hydration**: Context assembly tailored to specific roles
- **Structured tracing**: Industry-grade observability with cryptographic verification
- **Self-critique**: Anthropic-style reflection checkpoints
- **Dual implementation**: Python and Go versions for different use cases

**Implementation Components**:
- **MemoryRehydrator (Python)**: Role-aware context assembly with pinned anchors
- **MemoryRehydrator (Go)**: Go implementation with Lean Hybrid approach
- **StructuredTracer**: Industry-grade structured tracing
- **SelfCritique**: Bundle sufficiency evaluation and role-specific validation

**Usage Pattern**:
```python
from dspy_modules.utils.memory_rehydrator import MemoryRehydrator
from dspy_modules.utils.structured_tracer import StructuredTracer
from dspy_modules.utils.self_critique import SelfCritique

# Initialize observability components
rehydrator = MemoryRehydrator()
tracer = StructuredTracer()
critique = SelfCritique()

# Execute with context and tracing
with tracer.trace("task_execution"):
    context = rehydrator.rehydrate_context("planner", "task")
    result = execute_task(context)
    evaluation = critique.evaluate(result, context)
```

### Production Infrastructure (Tier 2) {#production-infrastructure}

**Context**: Production infrastructure components that ensure system reliability, security, and operational excellence

**Key Patterns**:
- **Automated workflow orchestration**: Complete automation from backlog → PRD → tasks → execution → archive
- **Documentation quality assurance**: Cross-reference validation, naming conventions, markdown compliance
- **Database resilience**: Connection pooling, health monitoring, retries, and graceful degradation
- **Error pattern recognition**: Pattern catalog + classification supporting automated recovery
- **Input security**: Validation and sanitization for queries/content, foundational for safe operations

**Implementation Components**:
- **SingleDoorwaySystem**: Core CLI for automated workflow from backlog → PRD → tasks → execution → archive
- **DocCoherenceValidator**: Primary validator for documentation integrity and cross-references
- **TaskGenerationAutomation**: Parses PRDs and backlog items, generates consistent task templates
- **DatabaseResilience**: Connection pooling, health monitoring, retries, and graceful degradation
- **Dashboard**: Flask dashboard, file intake, SocketIO updates, production monitoring
- **ErrorPatternRecognition**: Pattern catalog + classification supporting automated recovery
- **BulkDocumentProcessor**: Concurrent processing of entire document collections
- **DatabasePathCleanup**: Standardizes database path formats, resolves duplicate filenames
- **PromptSanitizer**: Validation and sanitization for queries/content, foundational for safe operations
- **RollbackDocSystem**: Git snapshot system for documentation recovery, automated snapshots
- **AnchorMetadataParser**: Extracts anchor metadata from HTML comments, maps to JSONB for memory rehydrator

**Usage Pattern**:
```python
from scripts.single_doorway import SingleDoorwaySystem
from scripts.doc_coherence_validator import DocCoherenceValidator
from scripts.task_generation_automation import TaskGenerationAutomation
from dspy_rag_system.src.utils.database_resilience import DatabaseResilience
from dspy_rag_system.src.dashboard import Dashboard
from dspy_rag_system.src.utils.error_pattern_recognition import ErrorPatternRecognition
from dspy_rag_system.bulk_add_core_documents import BulkDocumentProcessor
from dspy_rag_system.cleanup_database_paths import DatabasePathCleanup
from dspy_rag_system.src.utils.prompt_sanitizer import PromptSanitizer
from scripts.rollback_doc import RollbackDocSystem
from dspy_rag_system.src.utils.anchor_metadata_parser import AnchorMetadataParser

# Initialize production infrastructure components
single_doorway = SingleDoorwaySystem()
doc_validator = DocCoherenceValidator()
task_generator = TaskGenerationAutomation()
db_resilience = DatabaseResilience()
dashboard = Dashboard()
error_patterns = ErrorPatternRecognition()
bulk_processor = BulkDocumentProcessor()
path_cleanup = DatabasePathCleanup()
prompt_sanitizer = PromptSanitizer()
rollback_system = RollbackDocSystem()
anchor_parser = AnchorMetadataParser()

# Run complete production workflow
def run_complete_workflow(task_description: str):
    # 1. Validate documentation coherence
    doc_status = doc_validator.validate_all()

    # 2. Generate tasks from description
    tasks = task_generator.generate_tasks(task_description)

    # 3. Process with single doorway system
    workflow_result = single_doorway.run_workflow(tasks)

    # 4. Monitor via dashboard
    dashboard.update_status(workflow_result)

    return workflow_result

# Handle errors using pattern recognition and recovery
def handle_error_with_patterns(error: Exception):
    pattern = error_patterns.classify_error(error)
    recovery_action = error_patterns.get_recovery_action(pattern)

    if recovery_action.requires_rollback:
        rollback_system.create_snapshot()

    return recovery_action.execute()
```

### Supporting Infrastructure (Tier 3) {#supporting-infrastructure}

**Context**: Supporting infrastructure components that provide reliability, monitoring, and maintenance automation

**Key Patterns**:
- **Retry resilience**: Exponential backoff and circuit breaker patterns for reliable operations
- **Performance monitoring**: Comprehensive benchmarking and optimization with detailed metrics
- **Structured logging**: Context-aware logging with correlation IDs and structured output
- **Maintenance automation**: Interactive prompts and automated workflows for repository maintenance
- **Hydration monitoring**: Real-time health monitoring and performance dashboard for hydration system

**Implementation Components**:
- **RetryWrapper**: Retry/backoff policies with exponential backoff and circuit breaker patterns
- **PerformanceBenchmark**: Performance monitoring and optimization with comprehensive metrics
- **Logger**: Structured logging helpers with context and correlation IDs
- **AutoPushPrompt**: Interactive prompt for pushing changes after maintenance with git status checks
- **MaintenancePush**: Shell wrapper for auto-push prompt integration into maintenance workflows
- **HydrationBenchmark**: Comprehensive hydration performance benchmarking and analysis
- **HydrationMonitor**: n8n health monitor for hydration system with real-time alerts
- **HydrationDashboard**: Performance dashboard for hydration metrics and system health

**Usage Pattern**:
```python
from dspy_rag_system.src.utils.retry_wrapper import RetryWrapper
from scripts.performance_benchmark import PerformanceBenchmark
from dspy_rag_system.src.utils.logger import Logger
from scripts.auto_push_prompt import AutoPushPrompt
from scripts.maintenance_push import MaintenancePush
from dspy_rag_system.scripts.hydration_benchmark import HydrationBenchmark
from dspy_rag_system.src.n8n_workflows.hydration_monitor import HydrationMonitor
from dspy_rag_system.src.mission_dashboard.hydration_dashboard import HydrationDashboard

# Initialize supporting infrastructure components
retry_wrapper = RetryWrapper()
performance_benchmark = PerformanceBenchmark()
logger = Logger()
auto_push_prompt = AutoPushPrompt()
maintenance_push = MaintenancePush()
hydration_benchmark = HydrationBenchmark()
hydration_monitor = HydrationMonitor()
hydration_dashboard = HydrationDashboard()

# Run operation with resilience and logging
def run_with_resilience(operation_func, *args, **kwargs):
    logger.info("Starting operation", operation=operation_func.__name__)

    try:
        result = retry_wrapper.execute_with_retry(
            operation_func, *args, **kwargs
        )
        logger.info("Operation completed successfully")
        return result
    except Exception as e:
        logger.error("Operation failed", error=str(e))
        raise

# Benchmark operation performance
def benchmark_performance(operation_name: str, operation_func, *args, **kwargs):
    benchmark_result = performance_benchmark.run_benchmark(
        operation_name, operation_func, *args, **kwargs
    )

    # Update hydration dashboard with performance metrics
    hydration_dashboard.update_performance_metrics(benchmark_result)

    return benchmark_result

# Run comprehensive hydration benchmark
def run_hydration_benchmark():
    benchmark_result = hydration_benchmark.run_comprehensive_benchmark()

    # Monitor hydration health
    health_status = hydration_monitor.check_hydration_health()

    # Update dashboard
    hydration_dashboard.update_benchmark_results(benchmark_result, health_status)

    return benchmark_result, health_status

# Run maintenance workflow with auto-push integration
def maintenance_workflow(changes_description: str):
    # Run maintenance operations
    maintenance_result = maintenance_push.run_maintenance()

    # Prompt for push if needed
    if maintenance_result.requires_push:
        push_confirmed = auto_push_prompt.prompt_for_push(changes_description)
        if push_confirmed:
            maintenance_push.execute_push()

    return maintenance_result
```

## 🛠️ Development Tools

### GitHub Actions {#github-actions}

**Context**: CI/CD automation for repository maintenance and quality gates

**Key Patterns**:
- **Dry-run gates**: Validate changes before deployment
- **Pre-commit hooks**: Automated quality checks
- **Maintenance automation**: Automated repository upkeep
- **Safety validation**: Prevent critical file changes

**Implementation Components**:
- GitHub Action workflows for automated execution
- Pre-commit hooks for local validation
- Dry-run mode for safe testing
- Rollback procedures for failed deployments

### GitHub README {#github-readme}

**Context**: External-facing documentation for project discovery and onboarding

**Key Patterns**:
- **Zero-context onboarding**: Complete project overview without internal links
- **Professional presentation**: 500-line comprehensive README
- **External visibility**: Optimized for GitHub discovery
- **Clear value proposition**: Showcase AI development ecosystem

**Content Requirements**:
- Project overview and purpose
- Key features and capabilities
- Getting started guide
- Architecture overview
- Contributing guidelines
- License information

### Quality Gates {#quality-gates}

**Context**: Automated quality validation and enforcement

**Key Patterns**:
- **Fast execution**: <5s quality gate runtime
- **Essential checks**: Focus on actual problems
- **Reliable operation**: Boring, reliable quality gates
- **Simplified scope**: Remove overengineered complexity

**Quality Gate Components**:
- Lint checks (Ruff, Pyright)
- Documentation coherence validation
- Security checks
- Test execution
- Performance benchmarks

### Performance Optimization {#performance-optimization}

**Context**: System performance monitoring and optimization

**Key Patterns**:
- **Baseline metrics**: Capture performance benchmarks
- **Regression thresholds**: 10-15% acceptable regression
- **Monitoring integration**: Real-time performance tracking
- **Optimization targets**: Specific performance goals

**Performance Metrics**:
- Test pass rate percentage
- Median latency per role
- Average token count per run
- Memory usage and cleanup
- Response time thresholds

## 🔗 Integration Patterns

### Ollama Integration {#ollama-integration}

**Context**: Local AI model integration with Ollama/LM Studio

**Key Patterns**:
- **Local-first approach**: Avoid cloud dependencies
- **Model switching**: Support multiple local models
- **Hardware optimization**: Sequential loading for constraints
- **API integration**: Clean function interfaces

**Implementation Components**:
- ModelSwitcher for local model management
- Sequential loading for memory constraints
- API wrappers for Ollama/LM Studio
- Performance monitoring for local models

### MCP Server Architecture {#mcp-server-architecture}

**Context**: Model Context Protocol server for automated memory rehydration

**Key Patterns**:
- **Minimal server**: Wrap existing memory rehydrator
- **HTTP transport**: Standard MCP communication
- **Cursor integration**: Automatic tool exposure
- **Role auto-detection**: Context-based role selection

**Implementation Components**:
- Basic MCP server wrapper
- HTTP transport layer
- Cursor integration hooks
- Role detection logic

### n8n Workflows {#n8n-workflows}

**Context**: Workflow automation for backlog management and system operations

**Key Patterns**:
- **Stateless operations**: Avoid persistent state
- **Webhook integration**: Real-time event processing
- **Backlog automation**: Automated scoring and updates
- **Error handling**: Robust failure recovery

**Workflow Types**:
- Backlog scrubber for automated scoring
- Real-time status updates
- Event-driven processing
- Integration with existing systems

### Memory Rehydration {#memory-rehydration}

**Context**: Context-aware retrieval system for AI agents

**Key Patterns**:
- **Role-based retrieval**: Context specific to AI roles
- **Database integration**: PostgreSQL vector store
- **Stability requirements**: Configurable confidence thresholds
- **Performance optimization**: Fast context retrieval

**Implementation Components**:
- Role-based file mapping
- Semantic search capabilities
- Database integration
- Performance monitoring

## 📚 Documentation & Automation

### Documentation Generation {#documentation-generation}

**Context**: Automated documentation creation and maintenance

**Key Patterns**:
- **Anchor metadata scanning**: Extract metadata from files
- **Priority-based organization**: Tier-based documentation structure
- **Role-based grouping**: Organize by AI role requirements
- **Automatic updates**: Keep documentation current

**Generation Components**:
- Metadata extraction scripts
- Priority-based organization
- Role-based grouping
- Automatic update mechanisms

### Workflow Automation {#workflow-automation}

**Context**: Automation of development workflows and processes

**Key Patterns**:
- **Task automation**: Automated task generation and execution
- **Quality gates**: Automated quality validation
- **State management**: Automated state tracking
- **Error recovery**: Automated error handling

**Automation Components**:
- Task generation scripts
- Quality gate automation
- State management systems
- Error recovery mechanisms

### Automation Patterns {#automation-patterns}

**Context**: Reusable patterns for development automation

**Key Patterns**:
- **Deterministic execution**: Predictable automation behavior
- **Error handling**: Robust failure recovery
- **State persistence**: Maintain automation state
- **Integration patterns**: Connect with existing systems

**Pattern Components**:
- Error handling strategies
- State management approaches
- Integration techniques
- Monitoring and logging

### Repository Safety {#repository-safety}

**Context**: Safety mechanisms for repository operations

**Key Patterns**:
- **Pre-flight checks**: Validate before operations
- **Rollback procedures**: Safe rollback mechanisms
- **Critical file protection**: Prevent accidental changes
- **Validation gates**: Automated safety checks

**Safety Components**:
- Pre-flight validation scripts
- Rollback procedures
- Critical file protection
- Validation gates

## 🔬 Research & Validation

### Research-Based Design {#research-based-design}

**Context**: Design decisions based on research findings

**Key Patterns**:
- **Evidence-based patterns**: Patterns validated by research
- **Literature review**: Comprehensive research analysis
- **Benchmark validation**: Performance validation
- **Design recommendations**: Research-based guidance

**Research Components**:
- Literature review processes
- Benchmark validation
- Design recommendation extraction
- Evidence-based pattern identification

### Extraction Validation {#extraction-validation}

**Context**: Validation of data extraction quality and accuracy

**Key Patterns**:
- **Stratified validation**: Validate with representative samples
- **Quality metrics**: Measure extraction quality
- **Error analysis**: Analyze extraction errors
- **Continuous improvement**: Iterative quality improvement

**Validation Components**:
- Stratified sampling approaches
- Quality metric definition
- Error analysis procedures
- Improvement iteration cycles

### Structured Extraction {#structured-extraction}

**Context**: Structured data extraction from unstructured sources

**Key Patterns**:
- **Schema design**: Structured extraction schemas
- **Validation rules**: Data validation requirements
- **Span tracking**: Track extraction spans
- **Quality assessment**: Measure extraction quality

**Extraction Components**:
- Schema design processes
- Validation rule definition
- Span tracking mechanisms
- Quality assessment procedures

### Extraction Services {#extraction-services}

**Context**: Service-based extraction capabilities

**Key Patterns**:
- **Stateless services**: Avoid persistent state
- **API integration**: Clean service interfaces
- **Error handling**: Robust error recovery
- **Performance optimization**: Optimize extraction performance

**Service Components**:
- Stateless service design
- API interface definition
- Error handling strategies
- Performance optimization techniques

## 📊 Usage Guidelines

### When to Use Reference Cards

- **Implementation guidance**: When implementing new features
- **Pattern lookup**: When applying established patterns
- **Best practices**: When making technical decisions
- **Troubleshooting**: When resolving common issues

### How to Add New Reference Cards

1. **Identify pattern**: Recognize recurring patterns from implementation
2. **Document context**: Capture the context and purpose
3. **Extract key patterns**: Identify the essential patterns and approaches
4. **Add to index**: Include in the appropriate category
5. **Update regularly**: Keep reference cards current with implementation

### Quality Standards

- **Clear context**: Explain when and why to use the pattern
- **Concrete examples**: Include practical implementation examples
- **Common pitfalls**: Document common mistakes and how to avoid them
- **Success criteria**: Define clear success criteria
- **Related patterns**: Link to related reference cards

## 🔄 Maintenance

### Regular Updates

- **Pattern evolution**: Update patterns as they evolve
- **New discoveries**: Add new patterns from implementation
- **Deprecated patterns**: Mark deprecated patterns clearly
- **Cross-references**: Maintain accurate cross-references

### Validation

- **Implementation verification**: Verify patterns work in practice
- **Consistency checks**: Ensure patterns are consistent
- **Quality review**: Regular quality review of reference cards
- **User feedback**: Incorporate feedback from usage

## 🔗 Related Files

<!-- ESSENTIAL_FILES: 400_guides/400_system-overview.md, 400_guides/400_project-overview.md -->
