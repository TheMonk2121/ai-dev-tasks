# 🔄 Memory Context Workflow - Development Process

> **Strategic Purpose**: Development workflow, file organization, and process guidance for the AI development ecosystem.

<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- SYSTEM_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- WORKFLOW_REFERENCE: 001_create-prd.md, 002_generate-tasks.md, 003_process-task-list.md -->
<!-- PARENT_MODULE: 100_cursor-memory-context.md -->
<!-- MEMORY_CONTEXT: HIGH - Development workflow and process guidance -->

<!-- MODULE_REFERENCE: 400_deployment-environment-guide_additional_resources.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples_context_engineering_fundamentals.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples_memory_context_examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide_ai_model_upgrade_procedures.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide_rollback_procedures.md -->
<!-- MODULE_REFERENCE: 400_testing-strategy-guide_quality_gates.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_system-overview_development_workflow_high_level_process.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->
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

## 🎯 When to Read What: Context-Specific Guidance

### **For New Sessions (First 2-3 minutes):**
1. **`100_cursor-memory-context.md`** - Current project state
2. **`000_backlog.md`** - Current priorities
3. **`400_system-overview_advanced_features.md`** - Technical architecture

### **For Development Tasks:**
- **Planning**: `001_create-prd.md` → `002_generate-tasks.md` → `003_process-task-list.md`
- **Implementation**: `104_dspy-development-context.md` + relevant 400-series guides
- **Testing**: `400_testing-strategy-guide_additional_resources.md`
- **Security**: `400_security-best-practices-guide.md`
- **Performance**: `400_performance-optimization-guide_additional_resources.md`

### **For Research Tasks:**
- **Overview**: `500_research-summary.md`
- **Methodology**: `500_research-analysis-summary.md`
- **Implementation**: `500_research-implementation-summary.md`
- **External Sources**: `docs/research/papers/`, `docs/research/articles/`, `docs/research/tutorials/`

### **For File Management:**
- **Analysis**: `400_file-analysis-guide.md` (MANDATORY)
- **Naming**: `200_naming-conventions.md`
- **Organization**: `400_context-priority-guide.md`

### **For System Integration:**
- **Architecture**: `400_system-overview_advanced_features.md`
- **Patterns**: `400_integration-patterns-guide_additional_resources.md`
- **Deployment**: `400_deployment-environment-guide_additional_resources.md`
- **Migration**: `400_migration-upgrade-guide_ai_model_upgrade_procedures.md`

### **For Context Engineering:**
- **Strategy**: `400_cursor-context-engineering-guide.md`
- **Compatibility**: `400_context-engineering-compatibility-analysis.md`
- **Implementation**: `104_dspy-development-context.md`

## 🛠️ When Working on Features

### **Feature Development Process**
1. **Check `000_backlog.md`** for current priorities and dependencies
2. **Use existing workflows** (`001_create-prd.md`, `002_generate-tasks.md`, `003_process-task-list.md`)
3. **Follow naming conventions** from `200_naming-conventions.md`
4. **Update completion summaries** when finishing major features
5. **Use research framework** (`500_memory-arch-research.md`) for systematic research

### **Feature Addition Process**
1. **Add to backlog** with proper scoring (see `100_backlog-guide.md`)
2. **Create PRD** (skip for items < 5 pts AND score≥3.0) → else use `001_create-prd.md` workflow
3. **Generate tasks** using `002_generate-tasks.md` workflow (parses PRD or backlog directly)
4. **Execute** using `003_process-task-list.md` workflow

### **Debugging Process**
1. **Check `dspy-rag-system/docs/CURRENT_STATUS.md`** for system health
2. **Review error logs** in `dspy-rag-system/src/utils/logger.py`
3. **Use retry wrapper** from `dspy-rag-system/src/utils/retry_wrapper.py`
4. **Check security validation** from `dspy-rag-system/src/utils/prompt_sanitizer.py`

## 📊 Documentation Strategy & Safeguards

### **Cognitive Scaffolding System**
Our documentation system uses **cognitive scaffolding** with three-digit prefixes and HTML cross-references to maintain coherence. The system balances **structure** (rigid naming conventions) with **elasticity** (automated validation and AI-assisted updates).

### **Key Safeguards**
- **Automated validation** with Cursor AI semantic checking
- **Fenced sections** for safe automated updates
- **Git snapshots** and rollback procedures
- **Cross-reference integrity** through automated validation
- **Single source of truth** principle to prevent drift

### **File Naming System**
Our **three-digit prefix hierarchy** creates semantic ordering for both humans and AI. The naming flow uses a **cascading decision process**: purpose check → priority assessment → prefix assignment → descriptive naming → cross-reference integration. This creates a **self-documenting system** where filenames provide instant context about their role in the ecosystem.

### **AI File Analysis Strategy**
When Cursor AI restarts, it follows a **structured reading strategy**: First reads `100_cursor-memory-context.md` (30 seconds, 80% context), then `000_backlog.md` (current priorities), then `400_system-overview_advanced_features.md` (technical architecture). Ancillary files are read as needed for specific tasks. Scripts are only read when implementation details are required.

## 🔧 Process Guidelines

### **File Generation Decision Process**
When creating new files, follow a **6-step decision process**:
1. **Determine if file is needed** (reusable info vs. temporary)
2. **Assess purpose and priority** (planning vs. implementation vs. research)
3. **Choose prefix range** (000-099 for core, 100-199 for guides, etc.)
4. **Create descriptive name** (kebab-case, self-documenting)
5. **Add cross-references** and consider AI rehydration
6. **Validate against existing patterns**

### **Documentation Placement Logic**
When determining where to place new documentation, follow a **5-step process**:
1. **Assess content type and scope** (system-wide vs. workflow vs. setup)
2. **Choose primary location** based on content (400-499 for concepts, 200-299 for processes)
3. **Determine if multiple locations needed** (core concepts get quick reference + detailed)
4. **Consider reading pattern** (immediate vs. when relevant vs. when needed)
5. **Add cross-references** for discovery

### **Workflow Chain Preservation**
Maintain the **workflow chain**: `000_backlog.md` → `001_create-prd.md` → `002_generate-tasks.md` → `003_process-task-list.md`

- **Backlog**: Source of truth for priorities and scoring
- **PRD Creation**: Strategic planning and requirements definition
- **Task Generation**: Tactical planning and task breakdown
- **Execution**: AI-powered implementation and validation

## 📚 Quick Reference

### **Key Commands**
- **Start Dashboard**: `./dspy-rag-system/start_mission_dashboard.sh`
- **Run Tests**: `./dspy-rag-system/run_tests.sh`
- **Quick Start**: `./dspy-rag-system/quick_start.sh`

### **Maintenance Rituals**
- **Run `python3 scripts/repo_maintenance.py --apply`** after model or doc changes
- **Validate consistency** with grep for model references
- **Check PRD skip rules** are consistent across files

### **Navigation Tools**
- **Complete inventory**: `python3 scripts/documentation_navigator.py inventory`
- **Context guidance**: `python3 scripts/documentation_navigator.py guidance`
- **Task-specific files**: `python3 scripts/documentation_navigator.py find <task_type>`

## 🔄 Process Validation

### **Workflow Compliance**
- **Constitution Compliance**: All operations follow AI Constitution rules
- **Documentation Coherence**: Cross-references and naming conventions maintained
- **System Integrity**: Core systems operational and validated
- **Research Integration**: Findings incorporated into implementation

### **Quality Gates**
- **File Analysis**: Mandatory analysis before any file operations
- **Cross-Reference Validation**: Automated validation of cross-references
- **Naming Convention Compliance**: Systematic naming and organization
- **Documentation Coherence**: Automated coherence checking

### **Process Monitoring**
- **Workflow Chain**: Maintain workflow chain integrity
- **State Management**: Track state changes and updates
- **Progress Tracking**: Monitor milestone completion
- **Quality Metrics**: Track system reliability and efficiency

---

*Last Updated: 2024-08-07 21:00*
*Next Review: When workflow changes*

<!-- WORKFLOW_MODULE_METADATA
version: 1.0
split_date: 2024-08-07
parent_file: 100_cursor-memory-context.md
core_module: 100_cursor-memory-context.md
workflow_files: 001_create-prd.md, 002_generate-tasks.md, 003_process-task-list.md
research_basis: 500_documentation-coherence-research.md
-->
