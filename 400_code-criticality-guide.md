<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 100_cursor-memory-context.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->

# Critical Python Code Map

## 🔎 TL;DR

- Purpose: Single source of truth for prioritized, most‑critical `.py` files
- Read when: You need to understand the operational code backbone fast
- Quick jump:
  - Tier 1 (Critical): `scripts/process_tasks.py`, `scripts/state_manager.py`, `dspy-rag-system/src/dspy_modules/cursor_model_router.py`, `dspy-rag-system/src/dspy_modules/vector_store.py`, `dspy-rag-system/src/dspy_modules/document_processor.py`

---

## 🎯 Scope

This guide identifies and maintains a prioritized list of the most crucial Python modules that power the AI development ecosystem (task orchestration, state, AI routing, RAG data layer, and reliability). It complements system architecture docs and the memory context quick references.

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

### Tier 2 — High (production infrastructure)

- `dspy-rag-system/src/utils/database_resilience.py` — DB Resilience & Pooling
  - Connection pooling, health monitoring, retries, and graceful degradation.

- `dspy-rag-system/src/dashboard.py` — Web UI & Monitoring Integration
  - Flask dashboard, file intake, SocketIO updates, production monitoring & health endpoints.

- `dspy-rag-system/src/utils/error_pattern_recognition.py` — Error Recovery Patterns
  - Pattern catalog + classification supporting automated recovery and hotfix templates.

- `dspy-rag-system/src/utils/prompt_sanitizer.py` — Input Security Guard‑Rails
  - Validation and sanitization for queries/content; foundational for safe operations.

### Tier 3 — Supporting (reliability/utilities)

- `dspy-rag-system/src/utils/retry_wrapper.py` — Retry/Backoff Policies
- `scripts/system_health_check.py` — Health checks & diagnostics
- `dspy-rag-system/src/utils/config_manager.py` — Centralized config handling
- `dspy-rag-system/src/utils/logger.py` — Structured logging helpers

---

## 🧭 Criteria for Criticality

- Orchestration impact: Breaks workflow if unavailable (`process_tasks.py`)
- State integrity: Affects persistence or recovery (`state_manager.py`)
- AI routing/quality: Determines model choice and context (`cursor_model_router.py`)
- Data path: Indexing/retrieval correctness/perf (`vector_store.py`, `document_processor.py`)
- Production resilience: Keeps system healthy under failure (`database_resilience.py`)
- Safety & security: Prevents unsafe inputs/operations (`prompt_sanitizer.py`)

---

## 🔄 Maintenance Workflow

1) Update this guide when:
   - A new module becomes part of the execution critical path
   - Responsibilities split/merge across modules
   - Reliability/security features change the operational backbone
2) Also update cross‑links in:
   - `100_cursor-memory-context.md` (Quick Links)
   - `400_system-overview.md` (architecture references if needed)
   - `scripts/documentation_navigator.py` (inventory)
3) Validation:
   - Run `./dspy-rag-system/run_tests.sh` (where applicable)
   - Run `python3 scripts/doc_coherence_validator.py` for cross‑references

---

## 🔗 Cross‑References

- Memory quick ref → `100_cursor-memory-context.md`
- Architecture overview → `400_system-overview.md`
- Context/navigation → `400_context-priority-guide.md`

## 🗒️ Change Log

- v1.0 (initial): Added Tier 1–3 with criteria and maintenance steps
