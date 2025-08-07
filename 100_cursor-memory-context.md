# 🧠 Cursor Memory Context

<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- METADATA_SYSTEM: 400_metadata-collection-guide.md -->
<!-- SYSTEM_REFERENCE: 400_system-overview.md -->
<!-- BACKLOG_REFERENCE: 000_backlog.md -->
<!-- ROADMAP_REFERENCE: 400_development-roadmap.md -->
<!-- MEMORY_CONTEXT: HIGH - This file serves as the primary memory scaffold for Cursor AI -->

## 🎯 Purpose
This file serves as the **memory scaffold** for Cursor AI, providing instant context about the AI development ecosystem without requiring the AI to read multiple files.

## 📋 Current Project State

### **Active Development Focus**
- **Current Sprint**: B-011 (Cursor Native AI + Specialized Agents Integration) - 5 points
- **Next Priority**: B-031 (Vector Database Foundation Enhancement) - 3 points
- **Following**: B-032 (Memory Context System Architecture Research) - 8 points  
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
4. **AI Execution** → Execute backlog item directly (`003_process-task-list.md` is the execution engine; it loads whether or not a PRD was created)
5. **State Management** → `.ai_state.json` for context persistence (when using 003)
6. **Research Framework** → Use `500_memory-arch-research.md` for systematic research

**Note**: `003_process-task-list.md` is the execution engine; it loads whether or not a PRD was created.

### **File Organization**
- **Essential**: `400_project-overview.md`, `400_system-overview.md`, `000_backlog.md`
- **Implementation**: `104_dspy-development-context.md`, `202_setup-requirements.md`
- **Analysis**: `400_file-analysis-guide.md` - **🚨 MANDATORY: File deletion/deprecation analysis methodology**
- **Domain**: `100_backlog-guide.md`, `CURSOR_NATIVE_AI_STRATEGY.md`

## 🎯 Current Priorities




### **Immediate Focus (Next 1-2 weeks)**
1. **B‑011**: Cursor Native AI + Specialized Agents Integration (🔥 points)
   - todo
2. **B‑031**: Vector Database Foundation Enhancement (🔥 points)
   - todo
3. **B‑032**: Memory Context System Architecture Research (🔥 points)
   - todo
### **Infrastructure Status**
- ✅ **v0.3.1-rc3 Core Hardening** - Production ready
- ✅ **Real-time Mission Dashboard** - Live AI task monitoring
- ✅ **Production Security & Monitoring** - Comprehensive security
- ✅ **n8n Backlog Scrubber** - Automated prioritization

### **Recently Completed**
- ✅ **B‑065**: Error Recovery & Troubleshooting Guide (✅ done)
  - Comprehensive troubleshooting guide with emergency procedures
  - Automated recovery scripts for database and system issues
  - Integration with B-002 Advanced Error Recovery & Prevention system
  - Step-by-step workflows and monitoring procedures
- ✅ **B‑060**: Documentation Coherence Validation System (✅ done)
  - Comprehensive validation system with cross-reference checking
  - File naming convention validation and backlog reference validation
  - Memory context coherence checking and Cursor AI semantic validation
  - Pre-commit hooks, test suite, and complete documentation
- ✅ **B‑002**: Advanced Error Recovery & Prevention (✅ done)
  - Error Pattern Recognition System with 15+ error patterns
  - HotFix Template Generation with 3 template categories
  - Model-Specific Error Handling for 5+ AI models
- ✅ **C‑033**: n8n Workflow Integration Implementation (✅ done)
- ✅ **C‑034**: n8n Backlog Scrubber Workflow Implementation (✅ done)
- ✅ **C‑035**: Real-time Mission Dashboard Implementation (✅ done)
- ✅ **File Naming Convention Migration**: Three-digit prefixes implemented (✅ done)
- ✅ **Memory Context Research Framework**: Benchmark harness and research plan (✅ done)
- ✅ **Cache-Augmented Generation**: Database schema, evaluation framework, documentation (✅ done)
- ✅ **File Cleanup**: Removed duplicates, archived implementation notes (✅ done)
- ✅ **Documentation Reference Updates**: Updated all files to reference correct file names (✅ done)

## 🛠️ Development Guidelines

### **🚨 MANDATORY: File Deletion/Deprecation Analysis**
**Before suggesting ANY file deletion or deprecation, you MUST:**
1. **Run the analysis checklist**: `python3 scripts/file_analysis_checklist.py <target_file>`
2. **Follow the 6-step process** in `400_file-analysis-guide.md`
3. **Complete ALL steps** before making recommendations
4. **Get explicit user approval** for high-risk operations

**This is NON-NEGOTIABLE** - failure to follow these steps means you cannot suggest file deletion!

### **📚 Complete Documentation Inventory**

#### **🎯 CRITICAL FILES (Read First)**
- **`100_cursor-memory-context.md`** - Primary memory scaffold (this file)
- **`000_backlog.md`** - Current priorities and development roadmap
- **`400_system-overview.md`** - Technical architecture and system-of-systems
- **`400_project-overview.md`** - High-level project goals and workflow

#### **📋 WORKFLOW FILES (Development Process)**
- **`001_create-prd.md`** - PRD creation workflow (skip for items < 5 pts AND score≥3.0)
- **`002_generate-tasks.md`** - Task generation workflow (parses PRD or backlog)
- **`003_process-task-list.md`** - AI execution engine (loads whether PRD created or not)
- **`100_backlog-guide.md`** - Backlog management and scoring guidelines

#### **🏗️ SYSTEM ARCHITECTURE FILES (Technical Implementation)**
- **`104_dspy-development-context.md`** - DSPy framework implementation details
- **`202_setup-requirements.md`** - Environment setup and dependencies
- **`201_model-configuration.md`** - AI model configuration and setup
- **`400_context-priority-guide.md`** - Memory scaffolding and file organization
- **`400_context-engineering-compatibility-analysis.md`** - Context engineering compatibility
- **`400_cursor-context-engineering-guide.md`** - Context engineering implementation

#### **🔧 OPERATIONAL GUIDES (Production & Maintenance)**
- **`400_testing-strategy-guide.md`** - Testing methodologies and frameworks
- **`400_security-best-practices-guide.md`** - Security implementation and validation
- **`400_performance-optimization-guide.md`** - Performance tuning and monitoring
- **`400_deployment-environment-guide.md`** - Deployment and environment management
- **`400_migration-upgrade-guide.md`** - System migration and upgrade procedures
- **`400_integration-patterns-guide.md`** - Integration patterns and best practices
- **`400_metadata-collection-guide.md`** - Metadata collection and management
- **`400_metadata-quick-reference.md`** - Quick metadata reference
- **`400_few-shot-context-examples.md`** - Few-shot learning examples
- **`400_prd-optimization-guide.md`** - PRD optimization techniques
- **`400_n8n-backlog-scrubber-guide.md`** - n8n workflow automation
- **`400_mistral7b-instruct-integration-guide.md`** - Mistral integration (legacy)

#### **📊 RESEARCH DOCUMENTATION (500-Series)**
- **`500_research-summary.md`** - Research overview and findings
- **`500_research-analysis-summary.md`** - Research analysis methodology
- **`500_research-implementation-summary.md`** - Research implementation findings
- **`500_research-infrastructure-guide.md`** - Research infrastructure setup
- **`500_dspy-research.md`** - DSPy framework research findings
- **`500_rag-system-research.md`** - RAG system research findings
- **`500_documentation-coherence-research.md`** - Documentation coherence research
- **`500_maintenance-safety-research.md`** - Repository maintenance safety
- **`500_performance-research.md`** - Performance optimization research
- **`500_monitoring-research.md`** - System monitoring research
- **`500_agent-orchestration-research.md`** - Multi-agent orchestration research

#### **📁 EXTERNAL RESEARCH (docs/research/)**
- **`docs/research/papers/`** - Academic papers and research sources
- **`docs/research/articles/`** - Industry articles and blog posts
- **`docs/research/tutorials/`** - Implementation tutorials and guides

#### **🎯 DOMAIN-SPECIFIC FILES (B-Series & C-Series)**
- **`CURSOR_NATIVE_AI_STRATEGY.md`** - Cursor Native AI strategy (supports B-011)
- **`B-011-PRD.md`** - Cursor Native AI + Specialized Agents PRD
- **`B-011-Tasks.md`** - Cursor Native AI implementation tasks
- **`B-011-DEPLOYMENT-GUIDE.md`** - B-011 deployment guide
- **`B-011-DEVELOPER-DOCUMENTATION.md`** - B-011 developer docs
- **`B-011-USER-DOCUMENTATION.md`** - B-011 user documentation
- **`B-049-PRD.md`** - Domain-specific PRD
- **`B-049-Tasks.md`** - Domain-specific tasks
- **`B-072-PRD.md`** - Domain-specific PRD
- **`B-072-Tasks.md`** - Domain-specific tasks

#### **🔍 ANALYSIS & MAINTENANCE FILES**
- **`400_file-analysis-guide.md`** - **🚨 MANDATORY: File deletion/deprecation analysis**
- **`200_naming-conventions.md`** - File naming and organization system
- **`400_cross-reference-strengthening-plan.md`** - Cross-reference improvement plan
- **`999_repo-maintenance.md`** - Repository maintenance procedures

#### **📈 COMPLETION SUMMARIES (500-Series)**
- **`500_b002-completion-summary.md`** - B-002 completion summary
- **`500_b031-completion-summary.md`** - B-031 completion summary
- **`500_b060-completion-summary.md`** - B-060 completion summary
- **`500_b065-completion-summary.md`** - B-065 completion summary

#### **🔧 IMPLEMENTATION FILES**
- **`specialized_agent_framework.py`** - Specialized agent implementation
- **`cursor_ai_integration_framework.py`** - Cursor AI integration
- **`context_management_implementation.py`** - Context management
- **`agent_communication_implementation.py`** - Agent communication
- **`documentation_agent_implementation.py`** - Documentation agent
- **`coder_agent_implementation.py`** - Coder agent
- **`research_agent_implementation.py`** - Research agent

### **🎯 When to Read What: Context-Specific Guidance**

#### **For New Sessions (First 2-3 minutes):**
1. **`100_cursor-memory-context.md`** - Current project state
2. **`000_backlog.md`** - Current priorities
3. **`400_system-overview.md`** - Technical architecture

#### **For Development Tasks:**
- **Planning**: `001_create-prd.md` → `002_generate-tasks.md` → `003_process-task-list.md`
- **Implementation**: `104_dspy-development-context.md` + relevant 400-series guides
- **Testing**: `400_testing-strategy-guide.md`
- **Security**: `400_security-best-practices-guide.md`
- **Performance**: `400_performance-optimization-guide.md`

#### **For Research Tasks:**
- **Overview**: `500_research-summary.md`
- **Methodology**: `500_research-analysis-summary.md`
- **Implementation**: `500_research-implementation-summary.md`
- **External Sources**: `docs/research/papers/`, `docs/research/articles/`, `docs/research/tutorials/`

#### **For File Management:**
- **Analysis**: `400_file-analysis-guide.md` (MANDATORY)
- **Naming**: `200_naming-conventions.md`
- **Organization**: `400_context-priority-guide.md`

#### **For System Integration:**
- **Architecture**: `400_system-overview.md`
- **Patterns**: `400_integration-patterns-guide.md`
- **Deployment**: `400_deployment-environment-guide.md`
- **Migration**: `400_migration-upgrade-guide.md`

#### **For Context Engineering:**
- **Strategy**: `400_cursor-context-engineering-guide.md`
- **Compatibility**: `400_context-engineering-compatibility-analysis.md`
- **Implementation**: `104_dspy-development-context.md`

### **📊 Documentation Utilization Checklist**

**Before starting any task, ensure you've checked:**
- [ ] **Current state** in `100_cursor-memory-context.md`
- [ ] **Priorities** in `000_backlog.md`
- [ ] **Technical context** in `400_system-overview.md`
- [ ] **Relevant guides** in 400-series for specific tasks
- [ ] **Research findings** in 500-series for research tasks
- [ ] **Domain-specific docs** for B/C-series items
- [ ] **Analysis methodology** for file operations

**📚 Quick Navigation Tools:**
- **Complete inventory**: `python3 scripts/documentation_navigator.py inventory`
- **Context guidance**: `python3 scripts/documentation_navigator.py guidance`
- **Task-specific files**: `python3 scripts/documentation_navigator.py find <task_type>`

**This ensures full utilization of our comprehensive documentation system!** 🎯

### **Documentation Strategy & Safeguards**
Our documentation system uses **cognitive scaffolding** with three-digit prefixes and HTML cross-references to maintain coherence. The system balances **structure** (rigid naming conventions) with **elasticity** (automated validation and AI-assisted updates). Key safeguards include:
- **Automated validation** with Cursor AI semantic checking
- **Fenced sections** for safe automated updates
- **Git snapshots** and rollback procedures
- **Cross-reference integrity** through automated validation
- **Single source of truth** principle to prevent drift

See `400_context-priority-guide.md` for complete documentation strategy and file organization.

### **File Naming System**
Our **three-digit prefix hierarchy** creates semantic ordering for both humans and AI. The naming flow uses a **cascading decision process**: purpose check → priority assessment → prefix assignment → descriptive naming → cross-reference integration. This creates a **self-documenting system** where filenames provide instant context about their role in the ecosystem.

See `200_naming-conventions.md` for complete naming guidelines and decision process.

### **AI File Analysis Strategy**
When Cursor AI restarts, it follows a **structured reading strategy**: First reads `100_cursor-memory-context.md` (30 seconds, 80% context), then `000_backlog.md` (current priorities), then `400_system-overview.md` (technical architecture). Ancillary files are read as needed for specific tasks. Scripts are only read when implementation details are required.

See `400_context-priority-guide.md` for complete AI file analysis strategy and reading patterns.

### **File Generation Decision Process**
When creating new files, follow a **6-step decision process**: 1) Determine if file is needed (reusable info vs. temporary), 2) Assess purpose and priority (planning vs. implementation vs. research), 3) Choose prefix range (000-099 for core, 100-199 for guides, etc.), 4) Create descriptive name (kebab-case, self-documenting), 5) Add cross-references and consider AI rehydration, 6) Validate against existing patterns.

See `200_naming-conventions.md` for complete file generation decision process and guidelines.

### **Documentation Placement Logic**
When determining where to place new documentation, follow a **5-step process**: 1) Assess content type and scope (system-wide vs. workflow vs. setup), 2) Choose primary location based on content (400-499 for concepts, 200-299 for processes), 3) Determine if multiple locations needed (core concepts get quick reference + detailed), 4) Consider reading pattern (immediate vs. when relevant vs. when needed), 5) Add cross-references for discovery.

See `400_context-priority-guide.md` for complete documentation placement logic and guidelines.

### **When Working on Features**
1. **Check `000_backlog.md`** for current priorities and dependencies
2. **Use existing workflows** (`001_create-prd.md`, `002_generate-tasks.md`, `003_process-task-list.md`)
3. **Follow naming conventions** from `200_naming-conventions.md`
4. **Update completion summaries** when finishing major features
5. **Use research framework** (`500_memory-arch-research.md`) for systematic research

### **When Adding New Features**
1. **Add to backlog** with proper scoring (see `100_backlog-guide.md`)
2. **Create PRD** (skip for items < 5 pts AND score≥3.0) → else use `001_create-prd.md` workflow
3. **Generate tasks** using `002_generate-tasks.md` workflow (parses PRD or backlog directly)
4. **Execute** using `003_process-task-list.md` workflow

### **When Debugging Issues**
1. **Check `dspy-rag-system/docs/CURRENT_STATUS.md`** for system health
2. **Review error logs** in `dspy-rag-system/src/utils/logger.py`
3. **Use retry wrapper** from `dspy-rag-system/src/utils/retry_wrapper.py`
4. **Check security validation** from `dspy-rag-system/src/utils/prompt_sanitizer.py`

## 📚 Quick Reference

### **Key Files for Context**
- **System Overview**: `400_system-overview.md` (745 lines)
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

*Last Updated: 2024-08-06 09:15*
*Next Review: When changing development focus* 