# 🏗️ System Overview & Architecture

<!-- ANCHOR_KEY: system-overview-architecture -->
<!-- ANCHOR_PRIORITY: 4 -->
<!-- ROLE_PINS: ["researcher", "implementer"] -->

## 🔍 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Canonical system and architecture overview for understanding the codebase | Need to understand the technical architecture, system components, or how everything fits together | Read 04 (Development Workflows) then 05 (Coding Standards) |

- **what this file is**: Complete technical map of the system architecture and core components.

- **read when**: When you need to understand the technical architecture, system components, or how everything fits together.

- **do next**: Read 04 (Development Workflows & Standards) then 05 (Codebase Organization & Patterns).

## 🎯 **Current Status**
- **Priority**: 🔥 **HIGH** - Essential for understanding codebase architecture
- **Phase**: 2 of 4 (Codebase Development)
- **Dependencies**: 00-02 (Memory System Foundation)

## 🎯 **Purpose**

Provide a complete architecture map, core components, interfaces, and flows across planning, development, automation, deployment, observability, and security. This file is the canonical architectural source; details live in linked guides to avoid duplication.

## 🧱 Architecture Layers

- Presentation & Tooling
  - Cursor Native AI, mission dashboard, CLI/tooling
- Application Services
  - DSPy modules, automation services, background workers (RAG, rehydrator, pipelines)
- Data Layer
  - PostgreSQL + PGVector; optional Redis; logs/metrics storage
- Observability & Security
  - Health checks, metrics, tracing, access control, validation

## 🔄 Core Flows

- Development Flow: Backlog → Plan → Implement → Test → Deploy → Observe
- Context Flow: Memory rehydration → role‑aware bundles → echo verification → self‑critique
- Automation Flow: n8n workflows, Scribe capture → notifications → dashboards

## 🗺️ Map of Topics (Anchors)

- Architecture: high‑level system map
- Context Management: memory, vector, entity expansion, RRF
- Core Components: planner/AI execution layer and services
- Workflow: end‑to‑end development flow
- Security: guardrails and controls
- Testing & Quality: strategy and quality gates
- Deployment & Ops: environments, runtime, observability

## 🛡️ Safety Ops Anchors (Constitution)

**Critical Policies**: See `100_memory/100_cursor-memory-context.md#critical-policies` for essential safety guidelines.

- **File Safety**: Pre-edit analysis and protected file tiers
- **Context Rehydration**: Entrypoints via `scripts/memory_up.sh`, memory scaffold, backlog
- **Enforcement Hooks**: Testing gates, DSPy assertions, CI validators
- **Cross-Reference Integrity**: Architecture owns canonical links between 00-12 guides

## Architecture (high‑level)

Refer to `400_system-overview.md` for the full detailed architecture and component deep dives. Key excerpted structure:

```
┌──────────────────────────────────────────────────────────────┐
│  Core Systems                                                │
│  ├─ DSPy Multi‑Agent & RAG systems                           │
│  ├─ Scribe (Context Capture & Summarization)                 │
│  ├─ n8n Workflows (Automation)                               │
│  └─ Dashboard (Monitoring)                                   │
│                                                              │
│  Supporting Infrastructure                                   │
│  ├─ PostgreSQL + PGVector                                    │
│  ├─ Optional Redis cache                                     │
│  └─ Structured tracing & logs                                │
└──────────────────────────────────────────────────────────────┘
```

See: `400_system-overview.md` (Architecture, Core Components, Testing Framework, Metadata System).

## Context Management (summary)

- **Unified Memory Orchestrator**: Single command access to all memory systems
  - Automatic database startup via `brew services start postgresql@14`
  - Automatic virtual environment activation and dependency setup
  - Health monitoring with progress indicators and timeout handling
  - Graceful degradation when database startup is slow
- **Memory System Components**:
  - **LTST Memory System**: Database-backed conversation memory with session tracking
  - **Cursor Memory**: Static documentation bundling via `memory_up.sh`
  - **Go CLI Memory**: Fast startup (<1s) with lean hybrid approach
  - **Prime Cursor**: Enhanced Cursor integration with chat capabilities
- **Context Store**: Postgres tables; vector store via PGVector
- **Context Cache**: in‑memory/Redis; TTL and invalidation policies
- **Entity Expansion**: pattern‑based extraction; adjacent retrieval
- **RRF Fusion**: combine vector + BM25; stability slider and kill‑switches

**Command**: `python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "query"`

See: `400_06_memory-and-context-systems.md` and `dspy-rag-system/src/utils/memory_rehydrator.py`.

## AI Execution Layer (summary)

- Router: IntentRouter → RetrievalAgent → CodeAgent (fast‑path bypass for trivial asks)
- Timeouts and backoff; model janitor; score‑aware prioritization
- State file: `.ai_state.json` for continuity
- **RAGChecker Evaluation**: Industry-standard RAG evaluation framework for quality assessment
- **RAGChecker + Pydantic Integration**: Enhanced data validation, type safety, and performance optimization

See: `400_07_ai-frameworks-dspy.md` and `400_05_coding-and-prompting-standards.md`.

## Observability & Runtime

- Structured tracing, cryptographic verification, echo verification, self‑critique
- Health endpoints; metrics; dashboards; alerts
- **RAGChecker Metrics**: Precision, Recall, F1 Score, Context Utilization for RAG system quality
- **Performance Monitoring**: Real-time performance tracking, alerting, and optimization for validation workflows

See: `400_11_deployments-ops-and-observability.md` and `400_observability-system.md`.

## Security & Compliance (summary)

- Input validation; access control; secrets management
- Defense‑in‑depth; environment isolation; monitoring

See: `400_10_security-compliance-and-access.md`.

## Development Workflow (pointer)

For how to build and ship changes end‑to‑end, see `400_04_development-workflow-and-standards.md`.

## 📦 Canonical References

- Memory System Overview: `400_guides/400_00_memory-system-overview.md`
- Memory System Architecture: `400_guides/400_01_memory-system-architecture.md`
- Memory Rehydration: `400_guides/400_02_memory-rehydration-context-management.md`
- Development Workflow: `400_guides/400_04_development-workflow-and-standards.md`
- Codebase Organization: `400_guides/400_05_codebase-organization-patterns.md`
- AI Frameworks (DSPy/MCP): `400_guides/400_07_ai-frameworks-dspy.md`
- RAGChecker Evaluation: `400_guides/400_07_ai-frameworks-dspy.md#ragchecker-evaluation-system`
- MCP Memory Server: `400_guides/400_01_memory-system-architecture.md#mcp-memory-server-integration`
- Integrations: `400_guides/400_08_integrations-editor-and-models.md`
- Automation & Pipelines: `400_guides/400_09_automation-and-pipelines.md`
- Security & Access: `400_guides/400_10_security-compliance-and-access.md`
- Deployments/Ops: `400_guides/400_11_deployments-ops-and-observability.md`
- Product & Roadmap: `400_guides/400_12_product-management-and-roadmap.md`

## 🧩 Design Principles

- One canonical home per topic; link instead of duplicate
- Evidence‑first documentation; all links resolve
- Progressive hardening: pre‑commit/CI gates, link validation, security checks

## 🔗 Interfaces

- Backlog: `000_core/000_backlog.md`
- Memory Context: `100_memory/100_cursor-memory-context.md`
- DSPy Modules: See `400_07_ai-frameworks-dspy.md`

## 📚 References

- System Overview (detailed): `400_system-overview.md`
- Documentation Playbook: `400_01_documentation-playbook.md`
- Security Best Practices: `400_10_security-compliance-and-access.md`
- Deployments & Ops: `400_11_deployments-ops-and-observability.md`

## 📋 Changelog
- 2025-08-28: Reconstructed full canonical overview; linked to detailed system overview and ops.
