# 🧠 Cursor Memory Context

<!-- CONTEXT_REFERENCE: CONTEXT_PRIORITY_GUIDE.md -->
<!-- SYSTEM_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- BACKLOG_REFERENCE: 00_backlog.md -->
<!-- MEMORY_CONTEXT: HIGH - This file serves as the primary memory scaffold for Cursor AI -->

<!-- MODULE_REFERENCE: 102_memory-context-state.md -->
<!-- MODULE_REFERENCE: 104_memory-context-guidance.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples_memory_context_examples.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: 400_system-overview_system_architecture_macro_view.md -->
<!-- MODULE_REFERENCE: 400_system-overview_development_workflow_high_level_process.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: docs/100_ai-development-ecosystem.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
## 🎯 Purpose
This file serves as the **memory scaffold** for Cursor AI, providing instant context about the AI development ecosystem without requiring the AI to read multiple files.

## 📋 Current Project State

### **Active Development Focus**
- **Current Sprint**: B-002 (Advanced Error Recovery & Prevention) - 5 points
- **Next Priority**: B-011 (Yi-Coder-9B-Chat-Q6_K Integration) - 5 points  
- **Infrastructure**: v0.3.1-rc3 Core Hardening ✅ completed

### **System Architecture**
```
AI Development Ecosystem
├── Planning Layer (PRD → Tasks → Execution)
├── AI Execution Layer (Mistral 7B + Yi-Coder)
├── Core Systems (DSPy RAG + n8n + Dashboard)
└── Infrastructure (PostgreSQL + Monitoring)
```

### **Key Technologies**
- **AI Models**: Mistral 7B Instruct (planning), Yi-Coder-9B-Chat-Q6_K (coding)
- **Framework**: DSPy with PostgreSQL vector store
- **Automation**: n8n workflows for backlog management
- **Monitoring**: Real-time mission dashboard
- **Security**: Comprehensive input validation and prompt sanitization

## 🔄 Development Workflow

### **Current Process**
1. **Backlog Selection** → Choose from `00_backlog.md` (B-001, B-002, etc.)
2. **PRD Creation** → Use `01_create-prd.md` workflow
3. **Task Generation** → Use `02_generate-tasks.md` workflow  
4. **AI Execution** → Use `03_process-task-list.md` workflow
5. **State Management** → `.ai_state.json` for context persistence

### **File Organization**
- **Essential**: `400_project-overview.md`, `400_system-overview_advanced_features.md`, `00_backlog.md`
- **Implementation**: `104_dspy-development-context.md`, `202_setup-requirements.md`
- **Domain**: `100_backlog-guide.md`, `103_yi-coder-integration.md`

## 🎯 Current Priorities



### **Immediate Focus (Next 1-2 weeks)**
1. **B‑002**: Advanced Error Recovery & Prevention (🔥 points)
   - todo
2. **B‑011**: Yi-Coder-9B-Chat-Q6_K Integration into Cursor (🔥 points)
   - todo
3. **B‑026**: Secrets Management (🔥 points)
   - todo
### **Infrastructure Status**
- ✅ **v0.3.1-rc3 Core Hardening** - Production ready
- ✅ **Real-time Mission Dashboard** - Live AI task monitoring
- ✅ **Production Security & Monitoring** - Comprehensive security
- ✅ **n8n Backlog Scrubber** - Automated prioritization

### **Recently Completed**
- ✅ **C‑033**: n8n Workflow Integration Implementation (✅ done)
- ✅ **C‑034**: n8n Backlog Scrubber Workflow Implementation (✅ done)
- ✅ **C‑035**: Real-time Mission Dashboard Implementation (✅ done)

## 🛠️ Development Guidelines

### **When Working on Features**
1. **Check `00_backlog.md`** for current priorities and dependencies
2. **Use existing workflows** (`01_create-prd.md`, `02_generate-tasks.md`, `03_process-task-list.md`)
3. **Follow naming conventions** from `200_naming-conventions.md`
4. **Update completion summaries** when finishing major features

### **When Adding New Features**
1. **Add to backlog** with proper scoring (see `100_backlog-guide.md`)
2. **Create PRD** using `01_create-prd.md` workflow
3. **Generate tasks** using `02_generate-tasks.md` workflow
4. **Execute** using `03_process-task-list.md` workflow

### **When Debugging Issues**
1. **Check `dspy-rag-system/docs/CURRENT_STATUS.md`** for system health
2. **Review error logs** in `dspy-rag-system/src/utils/logger.py`
3. **Use retry wrapper** from `dspy-rag-system/src/utils/retry_wrapper.py`
4. **Check security validation** from `dspy-rag-system/src/utils/prompt_sanitizer.py`

## 📚 Quick Reference

### **Key Files for Context**
- **System Overview**: `400_system-overview_advanced_features.md` (745 lines)
- **Current Status**: `dspy-rag-system/docs/CURRENT_STATUS.md`
- **Backlog**: `00_backlog.md` (163 lines)
- **Setup**: `202_setup-requirements.md` (268 lines)

### **Key Directories**
- **Core System**: `dspy-rag-system/src/`
- **Documentation**: `docs/`
- **Configuration**: `config/`
- **Tests**: `tests/`

### **Key Commands**
- **Start Dashboard**: `./dspy-rag-system/start_mission_dashboard.sh`
- **Run Tests**: `./dspy-rag-system/run_tests.sh`
- **Quick Start**: `./dspy-rag-system/quick_start.sh`

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

*Last Updated: 2025-08-06*
*Next Review: When changing development focus* 