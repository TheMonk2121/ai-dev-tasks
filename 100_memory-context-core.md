# 🧠 Memory Context Core - Primary AI Entry Point

> **Strategic Purpose**: Primary memory scaffold for Cursor AI, providing instant context about the AI development ecosystem without requiring the AI to read multiple files.

<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- METADATA_SYSTEM: 400_metadata-collection-guide.md -->
<!-- SYSTEM_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- BACKLOG_REFERENCE: 000_backlog.md -->
<!-- ROADMAP_REFERENCE: 400_development-roadmap.md -->
<!-- AI_CONSTITUTION_REFERENCE: 400_ai-constitution.md -->
<!-- MEMORY_CONTEXT: HIGH - This file serves as the primary memory scaffold for Cursor AI -->
<!-- MODULE_REFERENCE: 101_memory-context-safety.md, 102_memory-context-state.md, 103_memory-context-workflow.md, 104_memory-context-guidance.md -->

<!-- MODULE_REFERENCE: 400_few-shot-context-examples_memory_context_examples.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: 400_system-overview_system_architecture_macro_view.md -->
<!-- MODULE_REFERENCE: 400_system-overview_development_workflow_high_level_process.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
## 🚨 CRITICAL SAFETY REQUIREMENTS
**BEFORE ANY FILE OPERATIONS:**
- [ ] Read `400_file-analysis-guide.md` completely (463 lines)
- [ ] Complete 6-step mandatory analysis
- [ ] Show all cross-references
- [ ] Get explicit user approval

**🤖 AI CONSTITUTION COMPLIANCE:**
- [ ] Follow `400_ai-constitution.md` rules for all AI operations
- [ ] Maintain context preservation and safety requirements
- [ ] Validate against constitution rules before any changes

## 📋 QUICK REFERENCE (30-second scan)
**Current Focus:** B-071 (Memory Context File Splitting) - 🔥 4 points
**Next Priority:** B-072 (Documentation Retrieval System Enhancement) - 🔥 5 points
**System:** Cursor Native AI + Specialized Agents + DSPy RAG
**Workflow:** Backlog → PRD → Tasks → AI Execution
**Critical Files:** `000_backlog.md`, `400_system-overview_advanced_features.md`, `400_file-analysis-guide.md`

## 🎯 Purpose
This file serves as the **primary memory scaffold** for Cursor AI, providing instant context about the AI development ecosystem. For detailed information, see the focused modules:

- **Safety & Requirements**: `101_memory-context-safety.md`
- **Current State & Priorities**: `102_memory-context-state.md`
- **Development Workflow**: `103_memory-context-workflow.md`
- **Context Guidance**: `104_memory-context-guidance.md`

## 📋 Current Project State

### **Active Development Focus**
- **Current Sprint**: B-071 (Memory Context File Splitting) - 4 points
- **Next Priority**: B-072 (Documentation Retrieval System Enhancement) - 5 points
- **Following**: B-073 (Giant Guide File Splitting) - 8 points
- **Infrastructure**: v0.3.1-rc3 Core Hardening ✅ completed

### **System Architecture**
```
AI Development Ecosystem
├── Planning Layer (PRD → Tasks → Execution)
├── AI Execution Layer (Cursor Native AI + Specialized Agents)
├── Core Systems (DSPy RAG + n8n + Dashboard)
├── Extraction Layer (LangExtract → Entity/Attribute Extraction)
└── Infrastructure (PostgreSQL + Monitoring)
```

### **Key Technologies**
- **AI Models**: Cursor Native AI (foundation), Specialized Agents (enhancements)
- **Framework**: DSPy with PostgreSQL vector store
- **Automation**: n8n workflows for backlog management
- **Monitoring**: Real-time mission dashboard
- **Security**: Comprehensive input validation and prompt sanitization
- **Extraction**: LangExtract (Gemini Flash) for entity/attribute extraction

## 🔄 Development Workflow

### **Current Process**
1. **Backlog Selection** → Pick top scored item from `000_backlog.md`
2. **PRD Creation** (skip for items < 5 pts AND score≥3.0) → else use `001_create-prd.md` workflow
3. **Task Generation** → Use `002_generate-tasks.md` workflow (parses PRD or backlog directly)
4. **AI Execution** → Execute backlog item directly (`003_process-task-list.md` is the execution engine)
5. **State Management** → `.ai_state.json` for context persistence (when using 003)
6. **Research Framework** → Use `500_memory-arch-research.md` for systematic research

**Note**: `003_process-task-list.md` is the execution engine; it loads whether or not a PRD was created.

### **File Organization**
- **Essential**: `400_project-overview.md`, `400_system-overview_advanced_features.md`, `000_backlog.md`
- **Implementation**: `104_dspy-development-context.md`, `202_setup-requirements.md`
- **Analysis**: `400_file-analysis-guide.md` - **🚨 MANDATORY: File deletion/deprecation analysis methodology**
- **Domain**: `100_backlog-guide.md`, `CURSOR_NATIVE_AI_STRATEGY.md`

**⚠️ CRITICAL**: Before ANY file operations, you MUST read and follow `400_file-analysis-guide.md` completely!

## 🎯 Current Priorities

### **Immediate Focus (Next 1-2 weeks)**
1. **B‑071**: Memory Context File Splitting (🔥 4 points) - **CURRENT TASK**
2. **B‑072**: Documentation Retrieval System Enhancement (🔥 5 points)
3. **B‑073**: Giant Guide File Splitting (📈 8 points)

### **Infrastructure Status**
- ✅ **v0.3.1-rc3 Core Hardening** - Production ready
- ✅ **Real-time Mission Dashboard** - Live AI task monitoring
- ✅ **Production Security & Monitoring** - Comprehensive security
- ✅ **n8n Backlog Scrubber** - Automated prioritization
- ✅ **AI Constitution Implementation** - Persistent safety rules

### **Recently Completed**
- ✅ **B‑070**: AI Constitution Implementation (✅ done)
  - Comprehensive AI Constitution with 5 articles
  - Compliance checker and validation framework
  - Integration with core system files
  - 16/16 tests passing with comprehensive validation

## 📚 Quick Reference

### **Key Files for Context**
- **System Overview**: `400_system-overview_advanced_features.md` (745 lines)
- **Current Status**: `dspy-rag-system/docs/CURRENT_STATUS.md`
- **Backlog**: `000_backlog.md` (163 lines)
- **Setup**: `202_setup-requirements.md` (268 lines)
- **Research**: `500_memory-arch-research.md` (research framework)
- **Benchmarks**: `500_memory-arch-benchmarks.md` (latest results)

### **Key Directories**
- **Core System**: `dspy-rag-system/src/`
- **Documentation**: `docs/`
- **Configuration**: `config/`
- **Tests**: `tests/`

### **Key Commands**
- **Start Dashboard**: `./dspy-rag-system/start_mission_dashboard.sh`
- **Run Tests**: `./dspy-rag-system/run_tests.sh`
- **Quick Start**: `./dspy-rag-system/quick_start.sh`

### **Maintenance Rituals**
- **Run `python3 scripts/repo_maintenance.py --apply`** after model or doc changes
- **Validate consistency** with grep for model references
- **Check PRD skip rules** are consistent across files

## 🔄 Memory State Updates

### **When This File Should Be Updated**
- After completing a backlog item
- When changing development focus
- When adding new major features
- When updating system architecture

### **Update Process**
1. Update current priorities section
2. Update system status
3. Update development guidelines if needed
4. Update quick reference if new files/directories added

---

*Last Updated: 2024-08-07 21:00*
*Next Review: When changing development focus*

<!-- MEMORY_CONTEXT_METADATA
version: 2.0
split_date: 2024-08-07
parent_file: 100_cursor-memory-context.md
modules: 101_memory-context-safety.md, 102_memory-context-state.md, 103_memory-context-workflow.md, 104_memory-context-guidance.md
compliance: 400_ai-constitution.md
research_basis: 500_documentation-coherence-research.md
-->
