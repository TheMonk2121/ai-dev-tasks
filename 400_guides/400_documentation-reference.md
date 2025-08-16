<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 100_memory/100_cursor-memory-context.md -->
<!-- MODULE_REFERENCE: 000_core/000_backlog.md -->
<!-- DOCUMENTATION_MASTER: This file is the complete documentation inventory and reference -->

# 📚 Documentation Reference

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete documentation inventory and reference guide | When you need to find specific documentation or understand the
full scope | Use the category sections below to locate the documentation you need |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Complete documentation inventory
- **Priority**: 🔥 Critical - Essential for documentation discovery
- **Points**: 3 - Low complexity, high importance
- **Dependencies**: 400_guides/400_context-priority-guide.md, 100_memory/100_cursor-memory-context.md
- **Next Steps**: Update as new documentation is added

## 📋 Complete Documentation Inventory

### **🎯 CRITICAL FILES (Read First)**

- **`400_guides/400_project-overview.md`** - Primary entry point and 5-minute overview ← **START HERE**
- **`100_memory/100_cursor-memory-context.md`** - Primary memory scaffold for instant context
- **`000_core/000_backlog.md`** - Current priorities and development roadmap
- **`400_guides/400_system-overview.md`** - Technical architecture and system-of-systems

### **📋 WORKFLOW FILES (Development Process)**

- **`000_core/001_create-prd.md`** - PRD creation workflow (skip for items < 5 pts AND score≥3.0)
- **`000_core/002_generate-tasks.md`** - Task generation workflow (parses PRD or backlog)
- **`000_core/003_process-task-list.md`** - AI execution engine (loads whether PRD created or not)
- **`100_memory/100_backlog-guide.md`** - Backlog management and scoring guidelines

### **🏗️ SYSTEM ARCHITECTURE FILES (Technical Implementation)**

- **`100_memory/104_dspy-development-context.md`** - DSPy framework implementation details
- **`200_setup/202_setup-requirements.md`** - Environment setup and dependencies
- **`400_guides/400_context-priority-guide.md`** - Memory scaffolding and file organization
- **`400_guides/400_guides/400_cursor-context-engineering-guide.md`** - Context engineering strategy and compatibility
(appendix)
- **`400_guides/400_guides/400_cursor-context-engineering-guide.md`** - Context engineering implementation

### **🔧 OPERATIONAL GUIDES (Production & Maintenance)**

- **`400_guides/400_testing-strategy-guide.md`** - Testing methodologies and frameworks
- **`400_guides/400_security-best-practices-guide.md`** - Security implementation and validation
- **`400_guides/400_performance-optimization-guide.md`** - Performance tuning and monitoring
- **`400_guides/400_deployment-environment-guide.md`** - Deployment and environment management
- **`400_guides/400_migration-upgrade-guide.md`** - System migration and upgrade procedures
- **`400_guides/400_integration-patterns-guide.md`** - Integration patterns and best practices
- **`400_guides/400_metadata-collection-guide.md`** - Metadata collection and management
  - Quick metadata reference: see `400_guides/400_metadata-collection-guide.md` (Quick reference section)
- **`400_guides/400_few-shot-context-examples.md`** - Few-shot learning examples
- **`400_guides/400_observability-system.md`** - Industry-grade observability with structured tracing and verification
- PRD optimization: see `000_core/001_create-prd.md` (skip rule), `000_core/002_generate-tasks.md` (PRD-less path), and
`100_memory/100_backlog-guide.md` (decision matrix)
- **`400_guides/400_n8n-backlog-scrubber-guide.md`** - n8n workflow automation

### **📊 RESEARCH DOCUMENTATION (500-Series)**

- **`500_research/500_research-summary.md`** - Research overview and findings
- **`500_research-analysis-summary.md`** - Research analysis methodology
- **`500_research/500_research-implementation-summary.md`** - Research implementation findings
- **`500_research/500_research-infrastructure-guide.md`** - Research infrastructure setup
- **`500_research/500_dspy-research.md`** - DSPy framework research findings
- **`500_research/500_rag-system-research.md`** - RAG system research findings
- **`500_research/500_documentation-coherence-research.md`** - Documentation coherence research
- **`500_research/500_maintenance-safety-research.md`** - Repository maintenance safety
- **`500_research/500_performance-research.md`** - Performance optimization research
- **`500_research/500_monitoring-research.md`** - System monitoring research
- **`500_research/500_agent-orchestration-research.md`** - Multi-agent orchestration research

### **📁 EXTERNAL RESEARCH (docs/research/)**

- **`docs/research/papers/`** - Academic papers and research sources
- **`docs/research/articles/`** - Industry articles and blog posts
- **`docs/research/tutorials/`** - Implementation tutorials and guides

### **🔍 ANALYSIS & MAINTENANCE FILES**

- **`400_guides/400_file-analysis-guide.md`** - 🚨 MANDATORY: File deletion/deprecation analysis
- **`200_setup/200_naming-conventions.md`** - File naming and organization system
- **`400_guides/400_cross-reference-strengthening-plan.md`** - Cross-reference improvement plan
- **`999_repo-maintenance.md`** - Repository maintenance procedures

### **📈 COMPLETION SUMMARIES (500-Series)**

- **`500_b002-completion-summary.md`** - B-002 completion summary
- **`500_b031-completion-summary.md`** - B-031 completion summary
- **`500_b060-completion-summary.md`** - B-060 completion summary
- **`500_b065-completion-summary.md`** - B-065 completion summary

### **🔧 IMPLEMENTATION FILES**

- **`specialized_agent_framework.py`** - Specialized agent implementation
- **`cursor_ai_integration_framework.py`** - Cursor AI integration
- **`context_management_implementation.py`** - Context management
- **`agent_communication_implementation.py`** - Agent communication
- **`documentation_agent_implementation.py`** - Documentation agent
- **`coder_agent_implementation.py`** - Coder agent
- **`research_agent_implementation.py`** - Research agent

## 🎯 When to Read What: Context-Specific Guidance

### **For New Sessions (First 2-3 minutes)**

1. **`400_guides/400_project-overview.md`** - Primary entry point and 5-minute overview ← **START HERE**
2. **`100_memory/100_cursor-memory-context.md`** - Current project state
3. **`000_core/000_backlog.md`** - Current priorities
4. **`400_guides/400_system-overview.md`** - Technical architecture

### **For Development Tasks**

- **Planning**: `000_core/001_create-prd.md` → `000_core/002_generate-tasks.md` → `000_core/003_process-task-list.md`
- **Implementation**: `100_memory/104_dspy-development-context.md` + relevant 400-series guides
- **Testing**: `400_guides/400_testing-strategy-guide.md`
- **Security**: `400_guides/400_security-best-practices-guide.md`
- **Performance**: `400_guides/400_performance-optimization-guide.md`

### **For Research Tasks**

- **Overview**: `500_research/500_research-summary.md`
- **Methodology**: `500_research-analysis-summary.md`
- **Implementation**: `500_research/500_research-implementation-summary.md`
- **External Sources**: `docs/research/papers/`, `docs/research/articles/`, `docs/research/tutorials/`

### **For File Management**

- **Analysis**: `400_guides/400_file-analysis-guide.md` (MANDATORY)
- **Naming**: `200_setup/200_naming-conventions.md`
- **Organization**: `400_guides/400_context-priority-guide.md`

### **For System Integration**

- **Architecture**: `400_guides/400_system-overview.md`
- **Patterns**: `400_guides/400_integration-patterns-guide.md`
- **Deployment**: `400_guides/400_deployment-environment-guide.md`
- **Migration**: `400_guides/400_migration-upgrade-guide.md`

### **For Context Engineering**

- **Strategy**: `400_guides/400_guides/400_cursor-context-engineering-guide.md`
- **Compatibility**: `400_guides/400_guides/400_cursor-context-engineering-guide.md`
- **Implementation**: `100_memory/104_dspy-development-context.md`

## 📖 README File Organization

### **README.md vs README-dev.md Decision Matrix**

| What you're documenting | Use | Why |
|---|---|---|
| New user feature (Nemo startup) | `README.md` | Users need to know how to use it |
| Test development guidelines | `README-dev.md` | Developers need technical details |
| System architecture | `README.md` | Users need to understand the system |
| Import path configuration | `README-dev.md` | Internal development concern |
| Quick start instructions | `README.md` | User onboarding |
| Database utility functions | `README-dev.md` | Internal development tool |
| API endpoints | `README.md` | Users need to know available APIs |
| Code organization policy | `README-dev.md` | Development team guidelines |

### **Quick Rules of Thumb**

**Use `README.md` if**:
- A user would benefit from knowing this
- It's about how to use the system
- It's about features and capabilities
- It's about getting started or workflows

**Use `README-dev.md` if**:
- Only developers need to know this
- It's about how to develop or test
- It's about internal technical details
- It's about code organization or patterns

### **README File Naming Conventions**

- **`README.md`** - Primary user-facing documentation
- **`README-dev.md`** - Developer-specific documentation
- **`README-{component}.md`** - Component-specific documentation (e.g., `README-api.md`)
- **`README-{environment}.md`** - Environment-specific documentation (e.g., `README-production.md`)

### **Content Organization Guidelines**

#### **README.md Content**
- Project overview and purpose
- Quick start instructions
- Feature descriptions and capabilities
- User workflows and examples
- System architecture (high-level)
- API endpoints and usage
- Installation and setup (user perspective)

#### **README-dev.md Content**
- Development setup and environment
- Testing guidelines and procedures
- Code organization and patterns
- Internal technical details
- Debugging and troubleshooting
- Contribution guidelines
- Build and deployment processes

### **Cross-Reference Integration**

- **README.md** should reference relevant `README-dev.md` sections
- **README-dev.md** should link back to user-facing features in `README.md`
- Both should follow the established cross-reference patterns from `200_setup/200_naming-conventions.md`
- Include memory context comments for AI rehydration

## 📊 Documentation Utilization Checklist

**Before starting any task, ensure you've checked:**

- [ ] **Current state** in `100_memory/100_cursor-memory-context.md`
- [ ] **Priorities** in `000_core/000_backlog.md`
- [ ] **Technical context** in `400_guides/400_system-overview.md`
- [ ] **Relevant guides** in 400-series for specific tasks
- [ ] **Research findings** in 500-series for research tasks
- [ ] **Domain-specific docs** for B/C-series items
- [ ] **Analysis methodology** for file operations

## 📚 Quick Navigation Tools

- **Complete inventory**: `python3 scripts/documentation_navigator.py inventory`
- **Context guidance**: `python3 scripts/documentation_navigator.py guidance`
- **Task-specific files**: `python3 scripts/documentation_navigator.py find <task_type>`

## 🔄 Maintenance Notes

- **Last Updated**: 2025-08-08
- **Update Frequency**: When new documentation is added
- **Cross-Reference**: Update `100_memory/100_cursor-memory-context.md` when this file changes
- **Validation**: Run `scripts/doc_coherence_validator.py` after updates

This file ensures full utilization of our comprehensive documentation system!
