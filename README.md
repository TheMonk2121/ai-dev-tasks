# AI Development Tasks - Advanced AI Development Ecosystem

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![DSPy 3.0](https://img.shields.io/badge/DSPy-3.0.1-green.svg)](https://github.com/stanfordnlp/dspy)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Advanced AI Development Ecosystem** with hybrid memory retrieval, multi-agent orchestration, closed-loop lessons→backlog, and optional voice I/O.

## 🚀 TL;DR

This is a **sophisticated AI development ecosystem** that provides:

- **🤖 Multi-Agent AI System** with specialized roles (Planner, Implementer, Researcher, Coder)
- **🧠 LTST Memory Foundation (B‑1012)** – flags + hook points + eval harness
- **🔍 Hybrid Retrieval (B‑1025)** – dense ∪ Postgres FTS union + local reranker, rolling summary, light facts
- **🔁 Closed‑Loop Lessons (B‑1026)** – proxy scratchpad capture → lessons/decisions → backlog integration
- **🔊 Voice I/O (B‑1027)** – push‑to‑talk + wake‑word, faster‑whisper STT, Piper/Coqui TTS, per‑role voices
- **⚡ DSPy 3.0** – latest framework with modular pipelines and assertions
- **🧭 Workflow** – single doorway scripts, traceable commits, feature‑flagged rollouts

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Development Ecosystem                  │
├─────────────────────────────────────────────────────────────┤
│  🤖 Multi-Agent System                                      │
│  ├── Planner (Strategic Planning)                           │
│  ├── Implementer (Code Implementation)                      │
│  ├── Researcher (Analysis & Research)                       │
│  └── Coder (Development Tooling)                            │
├─────────────────────────────────────────────────────────────┤
│  🧠 LTST Memory System                                      │
│  ├── Conversation History                                   │
│  ├── User Preferences                                       │
│  ├── Session Management                                     │
│  └── Context Merging                                        │
├─────────────────────────────────────────────────────────────┤
│  🔍 Advanced RAG System                                     │
│  ├── PostgreSQL + PGVector                                  │
│  ├── Semantic Search                                        │
│  ├── Context Retrieval                                      │
│  └── Memory Rehydration                                     │
├─────────────────────────────────────────────────────────────┤
│  ⚡ DSPy 3.0 Framework                                      │
│  ├── Optimized Pipelines                                    │
│  ├── Enhanced Assertions                                    │
│  ├── Performance Monitoring                                 │
│  └── Production Deployment                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### **🤖 Multi-Agent AI System**
- **Planner**: Strategic planning, backlog management, and project prioritization
- **Implementer**: Code implementation, technical architecture, and system design
- **Researcher**: Research analysis, documentation, and knowledge synthesis
- **Coder**: Development tooling, configuration, and automation tasks

### **🧠 LTST Memory System (B‑1012)**
- **Lightweight foundation**: feature flags, hook sites, eval seed, instrumentation
- **Exact pgvector + Postgres FTS** by default (BM25 only via extension later)
- **No pruner/episodic** yet (kept lean and measurable)

### **🔍 Hybrid Retrieval (B‑1025)**
- **Dense ∪ Sparse union**: pgvector exact + Postgres FTS (tsvector + ts_rank)
- **Local reranker**: cross‑encoder (ONNX INT8), recency as tiebreak
- **Rolling summary** (200–300 tokens) pinned at prompt edge
- **Light facts** with versioning + contradiction handling
- **A/B harness**: Recall/MRR/latency; feature‑flagged rollback
### **🔁 Closed‑Loop Lessons (B‑1026)**
- **Proxy logging** (OpenAI‑compatible) with secret masking
- **Structured scratchpad** (Cursor Rules) → runs/steps/lessons/decisions
- **Backlog integration**: lessons link to PRDs/items; auto‑suggest backlog candidates

### **🔊 Voice I/O (B‑1027)**
- **Push‑to‑talk + wake‑word** (openWakeWord), WebRTC VAD endpointing
- **STT**: faster‑whisper (CTranslate2); **TTS**: Piper default (Coqui optional)
- **Per‑role voices** and barge‑in; **hybrid moderator** (addressable + roundtable)
- **Dual‑mode troubleshooting (B‑1024)**: View‑Only guidance and VM Privileged (approved actions)

### **⚡ DSPy 3.0 Integration**
- **Latest Framework Migration** from DSPy 2.6.27 to 3.0.1
- **Enhanced Assertions** and validation capabilities
- **Optimized Pipelines** for better performance
- **Production Deployment** with comprehensive testing

### **🔄 Automated Workflows**
- **Single Doorway System** for streamlined development
- **Backlog Management** with automated prioritization
- **PRD Generation** and task creation
- **Quality Gates** and validation checks

## 🛠️ Core Modules

### **DSPy RAG System** (`dspy-rag-system/`)
Advanced retrieval-augmented generation system with PostgreSQL + PGVector integration, providing intelligent context retrieval and memory management.

### **LTST Memory System**
ChatGPT-like Long-Term Short-Term memory system with persistent conversation history, user preferences, and intelligent session management.

### **Multi-Agent AI System**
Specialized AI agents for different development tasks with role-based coordination and task distribution.

### **Memory Rehydrator**
Intelligent context management system that provides instant access to project documentation, state, and conversation history.

### **Single Doorway Workflow**
Automated backlog management, PRD generation, task creation, and execution pipeline with quality gates and validation.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 15+ with PGVector extension
- 128GB RAM (for local model execution)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-dev-tasks.git
cd ai-dev-tasks

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database
export POSTGRES_DSN="postgresql://username@localhost:5432/ai_agency"
```

### Basic Usage

```bash
# Start the mission dashboard
./dspy-rag-system/start_mission_dashboard.sh

# Run memory rehydration (Python wrapper around memory bundle)
python scripts/memory_rehydrate.py --role planner --query "current project status"

# Execute a backlog item (single‑doorway)
python scripts/single_doorway.py
```

## 📚 Documentation

### **Core Guides**
- [System Overview](400_guides/400_system-overview.md) - High-level system architecture and technical implementation
- [Development Workflow](400_guides/400_development-workflow.md) - Complete development workflow and quality assurance
- [Coding Best Practices](600_archives/consolidated-guides/400_comprehensive-coding-best-practices.md) - Development standards
- [Getting Started](400_guides/400_getting-started.md) - Quick start guide and project overview

### **Development Workflows**
- [Backlog Management](000_core/000_backlog.md) - Current priorities and roadmap (traceability policy in B‑1008)
- [PRD Creation](000_core/001_create-prd.md) - Product requirements workflow
- [Task Generation](000_core/002_generate-tasks.md) - Task breakdown workflow
- [Task Execution](000_core/003_process-task-list.md) - Implementation workflow

### **Technical Documentation**
- [DSPy Integration](400_guides/400_dspy-v2-technical-implementation-guide.md) - Framework integration
- [Cursor AI Integration](400_guides/400_cursor-ai-integration-guide.md) - IDE integration
- [Deployment Operations](400_guides/400_deployment-operations.md) - Production deployment and operations

## 🎯 Status Snapshot

### ✅ Landed recently
- **DSPy 3.0 baseline** and multi‑agent orchestration
- **Traceability (B‑1008)**: commit/branch policy, doc headers, helper

### 🚧 In progress / next
- **B‑1012** LTST foundation (flags/hooks/eval/logs)
- **B‑1025** Hybrid retrieval + reranker + summary + facts
- **B‑1026** Closed‑loop lessons/decisions linked to backlog
- **B‑1027** Voice I/O and dual‑mode troubleshooting UI

## 🏗️ System Architecture

### **Database Layer**
- **PostgreSQL 15+** with PGVector extension for vector operations
- **Messages + Facts** (minimal) with embedding_version and FTS (B‑1025)
- **Session Management** with automatic cleanup and archiving

### **AI Framework Layer**
- **DSPy 3.0** with optimized pipelines and enhanced assertions
- **Multi-Agent Orchestration** with role-based task distribution
- **Memory Rehydration** for instant context access

### **Application Layer**
- **Single Doorway Workflow** for streamlined development
- **Quality Gates** and validation checks
- **Production Monitoring** with health endpoints

### **Integration Layer**
- **Cursor AI Integration** for seamless IDE experience
- **Automated Workflows** with n8n orchestration
- **Proxy logs + Scratchpad** (B‑1026) and **Voice I/O** (B‑1027)

## 🧩 Feature Flags & Rollback
- FEATURE_HYBRID, FEATURE_RERANK, FEATURE_ROLLING_SUMMARY, FEATURE_FACTS
- FEATURE_PROXY_LOGS, FEATURE_SCRATCHPAD, FEATURE_LESSONS
- FEATURE_STT, FEATURE_TTS, FEATURE_VOICE_ROLES, FEATURE_VOICE_ROUNDTABLE

Flags default off; rollout is one‑flip; turning flags off reverts to LTST baseline.
- **Real-time Dashboards** for system monitoring

## 🔧 Development

### **Code Quality**
- **Ruff** for linting and formatting
- **Pyright** for type checking
- **Pytest** for comprehensive testing
- **Pre-commit hooks** for quality gates and traceability checks (B‑1008)

### **Testing Strategy**
- **Unit Tests** for all core components
- **Integration Tests** for end-to-end workflows
- **Performance Benchmarks** for optimization
- **Security Validation** for production readiness

### **Deployment**
- **Local-First Development** with minimal external dependencies
- **Production-Ready Infrastructure** with monitoring and health checks
- **Automated Quality Gates** for deployment validation

## 🤝 Contributing

This is a **solo development project** focused on local-first AI development workflows. The system is designed for personal productivity and research purposes.

## 🔗 PRDs (Selected)
- B‑1012: `artifacts/prds/PRD-B-1012-LTST-Foundation.md`
- B‑1025: `artifacts/prds/PRD-B-1025-Lean-Hybrid-Memory.md`
- B‑1026: `artifacts/prds/PRD-B-1026-Closed-Loop-Lessons.md`
- B‑1024 (dual‑mode reference): `artifacts/prds/PRD-B-1024-5-Layer-Memory-System.md` (legacy discussion baseline)


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Stanford NLP** for the DSPy framework
- **PostgreSQL** and **PGVector** for vector database capabilities
- **Cursor AI** for the integrated development experience

---

**Built with ❤️ for advanced AI development workflows**
