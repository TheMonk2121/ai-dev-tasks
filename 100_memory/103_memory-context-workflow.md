<!-- ANCHOR_KEY: memory-context-workflow -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- MEMORY_CONTEXT: HIGH - Memory context workflow and development process -->
<!-- DATABASE_SYNC: REQUIRED -->
<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_guides/400_migration-upgrade-guide.md -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

# Memory Contedt Workflow

## **For Development Tasks:**{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of **For Development Tasks:**.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

- **Planning**: `000_core/001_create-prd.md` → `000_core/002_generate-tasks.md` → `000_core/003_process-task-list.md`

- **Implementation**: `100_memory/104_dspy-development-context.md` + relevant 400-series guides

- **Testing**: `400_guides/400_testing-strategy-guide.md`

- **Security**: `400_guides/400_security-best-practices-guide.md`

- **Performance**: `400_guides/400_performance-optimization-guide.md`

### **For Research Tasks:**-**Overview**: `500_research/500_research-summary.md`

- **Methodology**: `500_research-analysis-summary.md`

- **Implementation**: `500_research/500_research-implementation-summary.md`

- **External Sources**: `docs/research/papers/`, `docs/research/articles/`, `docs/research/tutorials/`

### **For File Management:**-**Analysis**: `400_guides/400_file-analysis-guide.md` (MANDATORY)

- **Naming**: `200_setup/200_naming-conventions.md`

- **Organization**: `400_guides/400_context-priority-guide.md`

### **For System Integration:**-**Architecture**: `400_guides/400_system-overview.md`

- **Patterns**: `400_guides/400_integration-patterns-guide.md`

- **Deployment**: `400_guides/400_deployment-environment-guide.md`

- **Migration**: `400_guides/400_migration-upgrade-guide.md`

### **For Context Engineering:**-**Strategy**: `400_guides/400_cursor-context-engineering-guide.md`

- **Compatibility**: `400_guides/400_cursor-context-engineering-guide.md` (appendix)

- **Implementation**: `100_memory/104_dspy-development-context.md`

## 🛠️ When Working on Features

### **Feature Development Process**

1.**Check `000_core/000_backlog.md`**for current priorities and dependencies
2.**Use existing workflows**(`000_core/001_create-prd.md`, `000_core/002_generate-tasks.md`,
`000_core/003_process-task-list.md`)
3.**Follow naming conventions**from `200_setup/200_naming-conventions.md`
4.**Update completion summaries**when finishing major features
5.**Use research framework**(`500_research/500_memory-arch-research.md`) for systematic research

### **Feature Addition Process**

1.**Add to backlog**with proper scoring (see `100_memory/100_backlog-guide.md`)
2.**Create PRD**(skip for items < 5 pts AND score≥3.0) → else use `000_core/001_create-prd.md` workflow
3.**Generate tasks**using `000_core/002_generate-tasks.md` workflow (parses PRD or backlog directly)
4.**Execute**using `000_core/003_process-task-list.md` workflow

### **Debugging Process**

1.**Check `dspy-rag-system/docs/CURRENT_STATUS.md`**for system health
2.**Review error logs**in `dspy-rag-system/src/utils/logger.py`
3.**Use retry wrapper**from `dspy-rag-system/src/utils/retry_wrapper.py`
4.**Check security validation**from `dspy-rag-system/src/utils/prompt_sanitizer.py`

## 📊 Documentation Strategy & Safeguards

### **Cognitive Scaffolding System**

Our documentation system uses **cognitive scaffolding** with three-digit prefixes and HTML cross-references to maintain
coherence. The system balances**structure**(rigid naming conventions) with**elasticity**(automated validation and
AI-assisted updates).

### **Key Safeguards**-**Automated validation**with Cursor AI semantic checking

- **Fenced sections**for safe automated updates

- **Git snapshots**and rollback procedures

- **Cross-reference integrity**through automated validation

- **Single source of truth**principle to prevent drift

### **File Naming System**

Our **three-digit prefix hierarchy** creates semantic ordering for both humans and AI. The naming flow uses a
**cascading decision process**: purpose check → priority assessment → prefix assignment → descriptive naming →
cross-reference integration. This creates a **self-documenting system**where filenames provide instant context about
their role in the ecosystem.

### **AI File Analysis Strategy**

When Cursor AI restarts, it follows a **structured reading strategy**: First reads
`100_memory/100_cursor-memory-context.md` (30
seconds, 80% context), then `000_core/000_backlog.md` (current priorities), then `400_guides/400_system-overview.md`
(technical architecture). Ancillary files are read as needed for specific tasks. Scripts are only read when
implementation details are required.

## 🔧 Process Guidelines

### **File Generation Decision Process**

When creating new files, follow a **6-step decision process**:

1. **Determine if file is needed**(reusable info vs. temporary)
2.**Assess purpose and priority**(planning vs. implementation vs. research)
3.**Choose prefix range**(000-099 for core, 100-199 for guides, etc.)
4.**Create descriptive name**(kebab-case, self-documenting)
5.**Add cross-references**and consider AI rehydration
6.**Validate against existing patterns**###**Documentation Placement Logic**When determining where to place new
documentation, follow a**5-step process**:

1.**Assess content type and scope**(system-wide vs. workflow vs. setup)
2.**Choose primary location**based on content (400-499 for concepts, 200-299 for processes)
3.**Determine if multiple locations needed**(core concepts get quick reference + detailed)
4.**Consider reading pattern**(immediate vs. when relevant vs. when needed)
5.**Add cross-references**for discovery

### **Workflow Chain Preservation**

Maintain the **workflow chain**: `000_core/000_backlog.md` → `000_core/001_create-prd.md` →
`000_core/002_generate-tasks.md` →
`000_core/003_process-task-list.md`

- **Backlog**: Source of truth for priorities and scoring

- **PRD Creation**: Strategic planning and requirements definition

- **Task Generation**: Tactical planning and task breakdown

- **Execution**: AI-powered implementation and validation

## 📚 Quick Reference

### **Key Commands**-**Start Dashboard**: `./dspy-rag-system/start_mission_dashboard.sh`

- **Run Tests**: `./dspy-rag-system/run_tests.sh`

- **Quick Start**: `./dspy-rag-system/quick_start.sh`

### **Maintenance Rituals**-**Run `python3 scripts/repo_maintenance.py --apply`**after model or doc changes

- **Validate consistency**with grep for model references

- **Check PRD skip rules**are consistent across files

### **Navigation Tools**-**Complete inventory**: `python3 scripts/documentation_navigator.py inventory`

- **Context guidance**: `python3 scripts/documentation_navigator.py guidance`

- **Task-specific files**: `python3 scripts/documentation_navigator.py find <task_type>`

## 🔄 Process Validation

### **Workflow Compliance**-**Constitution Compliance**: All operations follow AI Constitution rules

- **Documentation Coherence**: Cross-references and naming conventions maintained

- **System Integrity**: Core systems operational and validated

- **Research Integration**: Findings incorporated into implementation

### **Quality Gates**-**File Analysis**: Mandatory analysis before any file operations

- **Cross-Reference Validation**: Automated validation of cross-references

- **Naming Convention Compliance**: Systematic naming and organization

- **Documentation Coherence**: Automated coherence checking

### **Process Monitoring**-**Workflow Chain**: Maintain workflow chain integrity

- **State Management**: Track state changes and updates

- **Progress Tracking**: Monitor milestone completion

- **Quality Metrics**: Track system reliability and efficiency

- --

- Last Updated: 2024-08-07 21:00*
- Next Review: When workflow changes*

<!-- WORKFLOW_MODULE_METADATA
version: 1.0
split_date: 2024-08-07
parent_file: 100_memory/100_cursor-memory-context.md
core_module: 100_memory/100_cursor-memory-context.md
workflow_files: 000_core/001_create-prd.md, 000_core/002_generate-tasks.md, 000_core/003_process-task-list.md
research_basis: 500_documentation-coherence-research.md
- ->
