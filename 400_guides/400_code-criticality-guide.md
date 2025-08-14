<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 100_memory/100_cursor-memory-context.md -->
<!-- MODULE_REFERENCE: 400_guides/400_system-overview.md -->
<!-- MEMORY_CONTEXT: HIGH - Critical code identification and prioritization -->
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

1. `scripts/process_tasks.py` — Task Execution Engine (orchestrator)

- Core CLI to execute backlog items end‑to‑end; handles orchestration, error handling, and state transitions.

2. `scripts/state_manager.py` — Execution/State Persistence

- Central state tracking across task boundaries; execution history, retries, progress, and metadata.

3. `dspy-rag-system/src/dspy_modules/cursor_model_router.py` — AI Model Routing & Context Engineering

- Intelligent model selection for Cursor Native AI; validation, reasoning, and prompt/context strategies.

4. `dspy-rag-system/src/dspy_modules/vector_store.py` — Hybrid Vector Store (dense + sparse)

- PGVector + text search; storage, retrieval, span‑level grounding; core RAG data path.

5. `dspy-rag-system/src/dspy_modules/document_processor.py` — Document Ingestion & Chunking

- Validates, extracts metadata, chunks, and prepares documents for indexing and retrieval.

6. `dspy-rag-system/src/utils/memory_rehydrator.py` — Context Assembly & Role-Aware Hydration

- Builds role-aware context bundles from Postgres; pinned anchors + task-scoped retrieval; core AI agent context system.

### Tier 2 — High (production infrastructure)

- `scripts/doc_coherence_validator.py` — Documentation Quality & Coherence Validation
  - Primary validator for documentation integrity; cross-references, naming conventions, markdown compliance.

- `dspy-rag-system/src/utils/database_resilience.py` — DB Resilience & Pooling
  - Connection pooling, health monitoring, retries, and graceful degradation.

- `dspy-rag-system/src/dashboard.py` — Web UI & Monitoring Integration
  - Flask dashboard, file intake, SocketIO updates, production monitoring & health endpoints.

- `dspy-rag-system/src/utils/error_pattern_recognition.py` — Error Recovery Patterns
  - Pattern catalog + classification supporting automated recovery and hotfix templates.

- `dspy-rag-system/src/utils/prompt_sanitizer.py` — Input Security Guard‑Rails
  - Validation and sanitization for queries/content; foundational for safe operations.

- `scripts/rollback_doc.sh` — Documentation Recovery & Rollback System
  - Git snapshot system for documentation recovery; automated snapshots and rollback procedures.

- `dspy-rag-system/src/utils/anchor_metadata_parser.py` — Anchor Metadata Extraction
  - Extracts anchor metadata from HTML comments; maps to JSONB for memory rehydrator; critical for context assembly.

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

- `400_guides/400_planner-hydration-guide.md` — Planner Context Strategy
  - Role-specific context assembly for strategic planning tasks.

- `400_guides/400_implementer-hydration-guide.md` — Implementer Context Strategy
  - Role-specific context assembly for technical implementation tasks.

## 🧭 Criteria for Criticality

- Orchestration impact: Breaks workflow if unavailable (`process_tasks.py`)

- State integrity: Affects persistence or recovery (`state_manager.py`)

- AI routing/quality: Determines model choice and context (`cursor_model_router.py`)

- Data path: Indexing/retrieval correctness/perf (`vector_store.py`, `document_processor.py`)

- Context assembly: Breaks AI agent context building (`memory_rehydrator.py`)

- Documentation safety: Affects recovery and rollback capabilities (`rollback_doc.sh`)

- Metadata extraction: Breaks context assembly pipeline (`anchor_metadata_parser.py`)

- Production resilience: Keeps system healthy under failure (`database_resilience.py`)

- Documentation integrity: Ensures documentation quality and coherence (`doc_coherence_validator.py`)

- Safety & security: Prevents unsafe inputs/operations (`prompt_sanitizer.py`)

- Maintenance automation: Supports repository maintenance workflows (`auto_push_prompt.py`, `maintenance_push.sh`)

- Role-specific context: Optimizes context assembly for different roles (`400_guides/400_planner-hydration-guide.md`, `400_guides/400_implementer-hydration-guide.md`)

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

- Run `./dspy-rag-system/run_tests.sh` (where applicable)
- Run `python3 scripts/doc_coherence_validator.py` for cross‑references

- --

## 🔗 Cross‑References

- Memory quick ref → `100_memory/100_cursor-memory-context.md`

- Architecture overview → `400_guides/400_system-overview.md`

- Context/navigation → `400_guides/400_context-priority-guide.md`

## 🗒️ Change Log

- v1.3: Added role-specific hydration guides (Tier 3) - Planner and implementer context strategies
- v1.2: Added memory rehydrator (Tier 1), rollback system and anchor parser (Tier 2), maintenance automation (Tier 3) - Context assembly and documentation safety
- v1.1: Added `doc_coherence_validator.py` to Tier 2 (High) - Documentation quality validation
- v1.0 (initial): Added Tier 1–3 with criteria and maintenance steps
