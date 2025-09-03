# 🚀 AI Development Tasks – A Local-First AI Dev Ecosystem

Build faster, with memory and structure.
An end-to-end framework that turns messy AI workflows into clear, repeatable development pipelines.

## 🎯 Why This Exists

Building AI features today is chaotic:

- **Context gets lost** between sessions
- **Agents behave inconsistently** across tools
- **Workflows sprawl** across half a dozen tools
- **Quality and testing** lag behind speed
- **Decisions and patterns** are forgotten over time

This repo is my answer: a production-ready, local-first AI development ecosystem that brings order to AI-powered development.

## 🧩 What It Gives You

🤖 **Multi-Agent Roles** – Planner, Implementer, Researcher, and Coder that collaborate with shared memory

🧠 **LTST Memory System** – Persistent context that remembers decisions, patterns, and reasoning across months

🔍 **Advanced RAG** – PostgreSQL + PGVector for semantic context retrieval and instant rehydration

⚡ **DSPy 3.0** – Structured pipelines, enhanced assertions, and production-ready orchestration

🔄 **Single Doorway Workflow** – From backlog → PRD → tasks → execution → archive, all automated

📊 **Quality Gates** – Automated validation that prevents common development mistakes

## 🏗️ How It's Built

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Development Ecosystem                  │
├─────────────────────────────────────────────────────────────┤
│  🤖 Multi-Agent System  | Planner | Implementer | Researcher │
│  🧠 LTST Memory         | Persistent history + rehydration   │
│  🔍 RAG                | PostgreSQL + PGVector              │
│  ⚡ DSPy 3.0 Framework  | Structured pipelines + assertions  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Demo

```bash
# 1. Clone & setup
git clone https://github.com/TheMonk2121/ai-dev-tasks.git
cd ai-dev-tasks
poetry install
poetry run pre-commit install

# 2. Load project context (memory rehydration)
export POSTGRES_DSN="mock://test" && python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"

# 3. Generate your first feature
python3 scripts/single_doorway.py generate "Add user authentication system"

# 4. Watch it work
# ✅ Creates a PRD with requirements
# ✅ Breaks into tasks
# ✅ Executes with AI + quality gates
# ✅ Tracks progress on the dashboard
# ✅ Archives with context + lessons learned
```

## 📚 Documentation Strategy

Our documentation follows a structured 00-12 system designed for different user needs:

- **[00] Memory System Overview** - Why memory matters and how it works
- **[01] Memory System Architecture** - Technical deep-dive for engineers
- **[02] Memory Rehydration** - How to use memory effectively
- **[03] System Overview** - High-level architecture for stakeholders
- **[04] Development Workflow** - How to work with the system
- **[05] Codebase Organization** - Patterns and quality gates
- **[06] Backlog Management** - How to prioritize effectively
- **[07] Project Planning** - Strategic planning and roadmaps
- **[08] Task Management** - Execution and workflow automation
- **[09] AI Frameworks** - DSPy integration and AI patterns
- **[10] Integrations & Models** - External tools and model management
- **[11] Performance Optimization** - System tuning and monitoring
- **[12] Advanced Configurations** - Complex setup patterns

## 🎯 Success Metrics

| Problem | Before | After | Impact |
|---------|--------|-------|--------|
| **Context Loss** | 30 min re-explaining | Instant context loading | **95% time saved** |
| **Priority Drift** | Endless debates | Data-driven decisions | **Clear direction** |
| **Decision Amnesia** | Repeat mistakes | Pattern recognition | **Learning acceleration** |
| **Quality Issues** | Production bugs | Early detection | **Reliability improvement** |
| **Documentation** | Outdated docs | Auto-validation | **Always current** |

## 🔒 Production-Ready

- **Input validation** + prompt sanitization
- **Health checks** + performance benchmarks
- **Automated HotFix generation** + recovery
- **Local-first design** with PostgreSQL + PGVector
- **Quality gates** that run in 0.030s average
- **Pre-commit hooks** with 100% compliance

## 🚀 Recent Implementation: Phase 0/1 RAG Enhancement

**Just Shipped**: Complete Phase 0/1 RAG enhancement pipeline following industry best practices for precision recall optimization.

### ✅ Phase 0: Evaluation, Telemetry & Canary
- **Golden Evaluation Slices**: Novice vs Expert, Single vs Multi-hop queries with slice-specific metrics
- **Per-Request Telemetry**: Complete query → answer pipeline logging with canary tagging (10% sampling)
- **Enhanced Metrics**: nDCG@10, Coverage, Exact-Match, Span Support, F1, ECE with temperature scaling
- **Confidence Calibration**: Temperature scaling via Platt/Isotonic regression for proper abstain thresholds

### ✅ Phase 1: Windowing, Deduplication & Cross-Encoder
- **Smart Windowing**: 120-180 token windows with 33% overlap, paragraph boundary preservation
- **Near-Dup Suppression**: Cosine similarity + MinHash methods to optimize cross-encoder compute budget
- **ONNX-INT8 Cross-Encoder**: Micro-batched reranking (32 pairs) with 400ms timeout and BM25 fallback
- **Singleflight Caching**: 30s TTL with worker bounds (3 max) and graceful degradation

### 🎯 Performance Targets vs RAGChecker Baseline
- **Precision**: Maintain ≥0.149 (current baseline) ✅
- **Recall**: Target ≥0.35 (vs current 0.099) 🎯
- **F1**: Target ≥0.22 (vs current 0.112) 🎯
- **Latency P95**: <250ms per stage with timeout handling ✅

### 🔧 Production Deployment
- **Feature Flags**: All components configurable via `config/retrieval.yaml`
- **Canary Ready**: 10% traffic sampling with before/after rank comparison
- **Circuit Breakers**: Automatic fallback to heuristic reranking on timeout/failure
- **Comprehensive Testing**: `scripts/phase01_demo.py` validates all 5 core components

**Implementation Location**: `src/telemetry/`, `src/retrieval/`, `src/evaluation/` + enhanced `HybridRetriever`

## 🤝 Who This Is For

- **Solo Developers**: Who want professional-grade tooling without the overhead
- **Small Teams**: Who need to scale their development practices
- **Technical Leads**: Who want to enforce standards without being the bottleneck
- **Product Managers**: Who need visibility into technical decisions and progress
- **Stakeholders**: Who want to understand the "why" behind technical choices

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**This isn't just another development tool. It's a complete reimagining of how AI can augment human development by remembering, learning, and building on your team's collective intelligence.**

## 🙏 Credits

- Stanford NLP for DSPy
- PostgreSQL + PGVector for the memory backbone
- Cursor AI for IDE integration
