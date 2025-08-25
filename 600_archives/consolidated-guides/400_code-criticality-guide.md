<!-- ANCHOR_KEY: code-criticality-guide -->
<!-- ANCHOR_PRIORITY: 20 -->

<!-- ROLE_PINS: ["coder", "implementer"] -->
# 🗺️ Critical Python Code Map

{#tldr}

## 🗺️ Critical Python Code Map

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Single source of truth for prioritized, most‑critical `.py` files | You need to understand the operational code backbone fast | Update when new critical modules are added |

- Purpose: Single source of truth for prioritized, most‑critical `.py` files

- Read when: You need to understand the operational code backbone fast

- Quick jump:
- Tier 1 (Critical): `scripts/process_tasks.py`, `scripts/state_manager.py`,
`dspy-rag-system/src/dspy_modules/cursor_model_router.py`, `dspy-rag-system/src/dspy_modules/vector_store.py`,
`dspy-rag-system/src/dspy_modules/document_processor.py`, `dspy-rag-system/src/utils/memory_rehydrator.py`
- Tier 2 (High): `scripts/doc_coherence_validator.py`, `scripts/rollback_doc.sh`, `dspy-rag-system/src/utils/anchor_metadata_parser.py`
- Tier 3 (Supporting): `scripts/performance_benchmark.py`, `scripts/auto_push_prompt.py` — Performance monitoring & maintenance automation

- --

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Maintained and current

- **Priority**: 🔥 Critical - Core system documentation

- **Points**: 3 - Low complexity, high importance

- **Dependencies**: 400_guides/400_system-overview.md, 100_memory/100_cursor-memory-context.md

- **Next Steps**: Update when new critical modules are added

## 🎯 Scope

## ✅ Prioritized List (by tiers)

### Tier 1 — Critical (never break without a plan)

1. `scripts/venv_manager.py` — Virtual Environment Manager (dev-environment)

- Ensures virtual environment is properly activated and working; validates required dependencies (psycopg2, dspy, pytest, ruff); critical for all DSPy development workflows.

2. `scripts/single_doorway.py` — Single Doorway System (orchestrator)

- Core CLI for automated workflow from backlog → PRD → tasks → execution → archive; handles orchestration, error handling, and state transitions.

2. `scripts/process_tasks.py` — Task Execution Engine (orchestrator)

- Core CLI to execute backlog items end‑to‑end; handles orchestration, error handling, and state transitions.

3. `scripts/state_manager.py` — Execution/State Persistence

- Central state tracking across task boundaries; execution history, retries, progress, and metadata.

3. `dspy-rag-system/src/dspy_modules/cursor_model_router.py` — AI Model Routing & Context Engineering

- Intelligent model selection for Cursor Native AI; validation, reasoning, and prompt/context strategies.

4. `dspy-rag-system/src/dspy_modules/vector_store.py` — Hybrid Vector Store (dense + sparse)

- PGVector + text search; storage, retrieval, span‑level grounding; core RAG data path.

5. `dspy-rag-system/src/dspy_modules/document_processor.py` — Document Ingestion & Chunking

- Validates, extracts metadata, chunks, and prepares documents for indexing and retrieval.

6. `dspy-rag-system/src/dspy_modules/optimization_loop.py` — DSPy Optimization System (Type-Safe)

- Four-part optimization loop with Protocol interfaces, Union types, type guards, and type casting; core DSPy program optimization with comprehensive type safety.

7. `dspy-rag-system/src/utils/memory_rehydrator.py` — Context Assembly & Role-Aware Hydration (Python)

- Builds role-aware context bundles from Postgres; pinned anchors + task-scoped retrieval; industry-grade observability integration; core AI agent context system.

8. `dspy-rag-system/src/utils/memory_rehydration.go` — Context Assembly & Role-Aware Hydration (Go)

- Go implementation of memory rehydration system; Lean Hybrid with Kill-Switches approach; alternative to Python version.

9. `dspy-rag-system/src/utils/structured_tracer.py` — Industry-Grade Structured Tracing

- Stanford/Berkeley/Anthropic-grade observability; cryptographic verification; multi-layer logging; core debugging infrastructure.

10. `dspy-rag-system/src/utils/self_critique.py` — Self-Critique Engine

- Anthropic-style reflection checkpoints; bundle sufficiency evaluation; role-specific validation; bundle integrity verification.

### Tier 2 — High (production infrastructure)

- `scripts/single_doorway.py` — Single Doorway System (orchestrator)
  - Core CLI for automated workflow from backlog → PRD → tasks → execution → archive; handles orchestration, error handling, and state transitions.

- `scripts/doc_coherence_validator.py` — Documentation Quality & Coherence Validation
  - Primary validator for documentation integrity; cross-references, naming conventions, markdown compliance.

- `scripts/task_generation_automation.py` — Automated Task Generation System
  - Parses PRDs and backlog items; generates consistent task templates with testing requirements and quality gates; core workflow automation.

- `dspy-rag-system/src/utils/database_resilience.py` — DB Resilience & Pooling
  - Connection pooling, health monitoring, retries, and graceful degradation.

- `dspy-rag-system/src/dashboard.py` — Web UI & Monitoring Integration
  - Flask dashboard, file intake, SocketIO updates, production monitoring & health endpoints.

- `dspy-rag-system/src/utils/error_pattern_recognition.py` — Error Recovery Patterns
  - Pattern catalog + classification supporting automated recovery and hotfix templates.

- `dspy-rag-system/bulk_add_core_documents.py` — Bulk Document Processing System
  - Concurrent processing of entire document collections; coverage analysis, intelligent path matching, and comprehensive knowledge base management.

- `dspy-rag-system/cleanup_database_paths.py` — Database Path Standardization
  - Standardizes database path formats, resolves duplicate filenames, and ensures consistency across document storage.

- `dspy-rag-system/src/utils/prompt_sanitizer.py` — Input Security Guard‑Rails
  - Validation and sanitization for queries/content; foundational for safe operations.

- `scripts/rollback_doc.sh` — Documentation Recovery & Rollback System
  - Git snapshot system for documentation recovery; automated snapshots and rollback procedures.

- `dspy-rag-system/src/utils/anchor_metadata_parser.py` — Anchor Metadata Extraction
  - Extracts anchor metadata from HTML comments; maps to JSONB for memory rehydrator; critical for context assembly.

- `dspy-rag-system/src/dspy_modules/lang_extract_system.py` — LangExtract Structured Extraction
  - Research-based entity/relation/fact extraction with span-level grounding; DSPy 3.0 assertion integration; core extraction pipeline for structured data processing.

- `scripts/single_doorway.py` — Scribe System (Context Capture & Summarization)
  - Automatic development session recording, insight extraction, and knowledge mining; session registry with context tagging; deep integration with memory rehydration and DSPy systems; core context capture infrastructure.

### Tier 3 — Supporting (reliability/utilities)

- `dspy-rag-system/src/utils/retry_wrapper.py` — Retry/Backoff Policies

- `scripts/system_health_check.py` — Health checks & diagnostics

- `scripts/performance_benchmark.py` — Performance monitoring & optimization

- `dspy-rag-system/src/utils/config_manager.py` — Centralized config handling

- `dspy-rag-system/src/utils/logger.py` — Structured logging helpers

- `scripts/auto_push_prompt.py` — Repository Maintenance Automation
  - Interactive prompt for pushing changes after maintenance; git status checks and user confirmation.

- `scripts/maintenance_push.sh` — Maintenance Push Wrapper
  - Shell wrapper for auto-push prompt integration into maintenance workflows.

- `400_guides/400_hydration-system-guide.md` — Complete Hydration System
  - Comprehensive guide covering integration, testing, and role-specific strategies for memory rehydration.

- `400_guides/demo_complete_dspy_v2_system.py` — Complete DSPy v2 System Demonstration
  - Comprehensive demonstration of DSPy v2 optimization system with all components working together.

- `400_guides/demo_assertion_framework.py` — Assertion Framework Patterns
  - DSPy assertion-based validation framework demonstration with confidence scoring and error recovery.

- `400_guides/demo_four_part_optimization_loop.py` — Optimization Loop Workflow
  - Four-part optimization loop demonstration with type safety and comprehensive metrics tracking.

- `400_guides/demo_labeled_few_shot_optimizer.py` — Few-Shot Optimization Examples
  - LabeledFewShot optimizer demonstration with example extraction and pattern recognition.

## 🧭 Criteria for Criticality

- Development environment: Breaks all DSPy workflows if unavailable (`venv_manager.py`)
- Orchestration impact: Breaks workflow if unavailable (`single_doorway.py`, `process_tasks.py`)

- State integrity: Affects persistence or recovery (`state_manager.py`)

- AI routing/quality: Determines model choice and context (`cursor_model_router.py`)

- Data path: Indexing/retrieval correctness/perf (`vector_store.py`, `document_processor.py`)
- Structured extraction: Entity/relation/fact extraction quality and validation (`lang_extract_system.py`)

- DSPy optimization: Breaks AI program optimization and type safety (`optimization_loop.py`)

- Context assembly: Breaks AI agent context building (`memory_rehydrator.py`)
- Observability: Breaks debugging and verification capabilities (`structured_tracer.py`, `self_critique.py`)

- Documentation safety: Affects recovery and rollback capabilities (`rollback_doc.sh`)

- Metadata extraction: Breaks context assembly pipeline (`anchor_metadata_parser.py`)

- Production resilience: Keeps system healthy under failure (`database_resilience.py`)

- Documentation integrity: Ensures documentation quality and coherence (`doc_coherence_validator.py`)

- Knowledge base management: Processes entire document collections efficiently (`bulk_add_core_documents.py`)

- Context capture: Breaks development session recording and knowledge mining (`scripts/single_doorway.py` scribe functionality)

- Data consistency: Standardizes database path formats and resolves inconsistencies (`cleanup_database_paths.py`)

- Safety & security: Prevents unsafe inputs/operations (`prompt_sanitizer.py`)

- Maintenance automation: Supports repository maintenance workflows (`auto_push_prompt.py`, `maintenance_push.sh`)

- Role-specific context: Optimizes context assembly for different roles (`400_guides/400_hydration-system-guide.md`)

- Testing & validation: Ensures system quality and performance (`400_guides/400_hydration-system-guide.md`, `dspy-rag-system/tests/test_hydration_quality.py`, `dspy-rag-system/scripts/hydration_benchmark.py`)

- Integration & automation: Provides monitoring and workflow automation (`dspy-rag-system/src/n8n_workflows/hydration_monitor.py`, `dspy-rag-system/src/mission_dashboard/hydration_dashboard.py`, `400_guides/400_hydration-system-guide.md`)

- Learning & examples: Provides essential demonstrations and learning resources (`400_guides/demo_*.py`)

- --

## 🔄 Maintenance Workflow

1) Update this guide when:

- A new module becomes part of the execution critical path
- Responsibilities split/merge across modules
- Reliability/security features change the operational backbone

2) Also update cross‑links in:

- `100_memory/100_cursor-memory-context.md` (Quick Links)
- `400_guides/400_system-overview.md` (architecture references if needed)
- `scripts/documentation_navigator.py` (inventory)

3) Validation:

- Run tests: `python -m pytest -v -m 'tier1 or tier2'` (preferred)
- Also supported (shim): `./dspy-rag-system/run_tests.sh --tiers 1 --kinds unit`
- Run `python3.12 scripts/doc_coherence_validator.py` for cross‑references

## 🛡️ Code Quality Standards for Critical Files

### Tier 1 & 2 Files Must:
- **Pass all linter checks** (no F841, E501, etc.)
- **Have comprehensive test coverage** (80%+ for Tier 1, 70%+ for Tier 2)
- **Follow unused variable best practices** (see `400_guides/400_comprehensive-coding-best-practices.md`)
- **Use proper import patterns** (conftest.py for tests, no manual sys.path)
- **Have clear error handling** and logging
- **Follow DSPy type safety standards** (Protocol interfaces, Union types, type guards, type casting)
- **Implement comprehensive error handling** (retry logic, graceful degradation, error recovery)

### Quality Gates:
- **Pre-commit**: All linter checks pass for Tier 1/2 files
- **CI/CD**: F841 errors treated as failures for Tier 1/2 files
- **Code Review**: Unused variable patterns reviewed
- **Test Coverage**: Minimum coverage thresholds enforced
- **DSPy Type Safety**: Protocol interfaces, Union types, type guards validated
- **Error Handling**: Comprehensive error recovery and retry logic verified

### Linting Standards:
```bash
# Tier 1 & 2 files must pass all checks
ruff check --select E,F,I dspy-rag-system/src/ scripts/

# Test files should follow F841 best practices
ruff check --select F841 dspy-rag-system/tests/
```

### F841 Error Prevention:
- **Tier 1 files**: Zero F841 errors allowed
- **Tier 2 files**: Zero F841 errors allowed
- **Tier 3 files**: F841 errors should be reviewed and fixed when possible
- **Test files**: Follow test variable management guidelines

### Examples of Quality Standards:
```python
# ✅ Good: Tier 1/2 file with proper variable management
def process_critical_data(data: Dict[str, Any]) -> Dict[str, Any]:
    validated_data = validate_input(data)
    processed_result = transform_data(validated_data)
    return processed_result

# ❌ Bad: Unused variable in critical file
def process_critical_data(data: Dict[str, Any]) -> Dict[str, Any]:
    validated_data = validate_input(data)
    unused_var = calculate_extra(data)  # F841 error - not allowed in Tier 1/2
    processed_result = transform_data(validated_data)
    return processed_result

# ✅ Good: DSPy type safety with Protocol interfaces
from typing import Protocol, Union, cast, Any
from dspy import Module

class HasForward(Protocol):
    def forward(self, *args, **kwargs) -> Any:
        ...

def process_module(module: Union[Module, HasForward]) -> dict:
    if hasattr(module, 'forward') and callable(getattr(module, 'forward')):
        result = module.forward("test")
        return {"success": True, "result": result}
    else:
        dspy_module = cast(Module, module)
        return {"success": False, "error": "Incompatible module"}

# ❌ Bad: No type safety in DSPy operations
def process_module(module):  # No type hints
    result = module.forward("test")  # No type checking
    return {"success": True, "result": result}
```

- --

## 🔗 Cross‑References

- Memory quick ref → `100_memory/100_cursor-memory-context.md`

- Architecture overview → `400_guides/400_system-overview.md`

- Context/navigation → `400_guides/400_context-priority-guide.md`

## 🗒️ Change Log

- v1.9: Added essential demo files (Tier 3) - Complete DSPy v2 system demonstration, assertion framework patterns, optimization loop workflow, and few-shot optimization examples
- v1.8: Added Scribe system (Tier 2) - Context capture and summarization system with session registry, insight extraction, and knowledge mining capabilities
- v1.7: Added DSPy optimization system (Tier 1) - Type-safe optimization with Protocol interfaces, Union types, type guards, and comprehensive error handling
- v1.6: Added bulk document processing system (Tier 2) - Bulk document processing and database path standardization
- v1.5: Added hydration integration framework (Tier 3) - n8n health monitor, performance dashboard, and integration guide
- v1.4: Added hydration testing framework (Tier 3) - Testing framework, quality validation, and performance benchmarking
- v1.3: Added role-specific hydration guides (Tier 3) - Planner and implementer context strategies
- v1.2: Added memory rehydrator (Tier 1), rollback system and anchor parser (Tier 2), maintenance automation (Tier 3) - Context assembly and documentation safety
- v1.1: Added `doc_coherence_validator.py` to Tier 2 (High) - Documentation quality validation
- v1.0 (initial): Added Tier 1–3 with criteria and maintenance steps
