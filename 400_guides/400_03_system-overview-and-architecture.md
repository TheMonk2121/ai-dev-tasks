\n+## 🛡️ Safety Ops Anchors (Constitution)
\n+- File safety module: pre‑edit analysis and protected file tiers.
- Context rehydration entrypoints: `scripts/memory_up.sh`, memory scaffold, backlog.
- Enforcement hooks: testing gates, DSPy assertions, CI validators.
- Cross‑ref integrity: architecture owns the canonical links between 00–12 guides.
# System Overview and Architecture

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Canonical system and architecture overview | You need a complete technical map of the system | Start at 00; deep‑dive via sections below; see 11 for runtime & 05 for coding/testing |

## 🎯 Purpose

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

- Context Store: Postgres tables; vector store via PGVector
- Context Cache: in‑memory/Redis; TTL and invalidation policies
- Entity Expansion: pattern‑based extraction; adjacent retrieval
- RRF Fusion: combine vector + BM25; stability slider and kill‑switches

See: `400_06_memory-and-context-systems.md` and `dspy-rag-system/src/utils/memory_rehydrator.py`.

## AI Execution Layer (summary)

- Router: IntentRouter → RetrievalAgent → CodeAgent (fast‑path bypass for trivial asks)
- Timeouts and backoff; model janitor; score‑aware prioritization
- State file: `.ai_state.json` for continuity

See: `400_07_ai-frameworks-dspy.md` and `400_05_coding-and-prompting-standards.md`.

## Observability & Runtime

- Structured tracing, cryptographic verification, echo verification, self‑critique
- Health endpoints; metrics; dashboards; alerts

See: `400_11_deployments-ops-and-observability.md` and `400_observability-system.md`.

## Security & Compliance (summary)

- Input validation; access control; secrets management
- Defense‑in‑depth; environment isolation; monitoring

See: `400_10_security-compliance-and-access.md`.

## Development Workflow (pointer)

For how to build and ship changes end‑to‑end, see `400_04_development-workflow-and-standards.md`.

## 📦 Canonical References

- Getting Started: `400_00_getting-started-and-index.md`
- Development Workflow: `400_04_development-workflow-and-standards.md`
- Coding & Testing: `400_05_coding-and-prompting-standards.md`
- Memory & Context: `400_06_memory-and-context-systems.md`
- AI Frameworks (DSPy/MCP): `400_07_ai-frameworks-dspy.md`
- Integrations: `400_08_integrations-editor-and-models.md`
- Automation & Pipelines: `400_09_automation-and-pipelines.md`
- Security & Access: `400_10_security-compliance-and-access.md`
- Deployments/Ops: `400_11_deployments-ops-and-observability.md`
- Product & Roadmap: `400_12_product-management-and-roadmap.md`

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
