<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->

- [ ] Maintain context preservation and safety requirements
- [ ] Validate against constitution rules before any changes
- [ ] Use constitution compliance checker for validation

## 🛠️ Development Guidelines

### **🚨 MANDATORY: File Deletion/Deprecation Analysis**
**Before suggesting ANY file deletion or deprecation, you MUST:**
1. **Run the analysis checklist**: `python3 scripts/file_analysis_checklist.py <target_file>`
2. **Follow the 6-step process** in `400_file-analysis-guide.md`
3. **Complete ALL steps** before making recommendations
4. **Get explicit user approval** for high-risk operations

**This is NON-NEGOTIABLE** - failure to follow these steps means you cannot suggest file deletion!

## 📚 Complete Documentation Inventory

### **🎯 CRITICAL FILES (Read First)**
- **`100_cursor-memory-context.md`** - Primary memory scaffold (this file)
- **`000_backlog.md`** - Current priorities and development roadmap
- **`400_system-overview_advanced_features.md`** - Technical architecture and system-of-systems
- **`400_project-overview.md`** - High-level project goals and workflow

### **📋 WORKFLOW FILES (Development Process)**
- **`001_create-prd.md`** - PRD creation workflow (skip for items < 5 pts AND score≥3.0)
- **`002_generate-tasks.md`** - Task generation workflow (parses PRD or backlog)
- **`003_process-task-list.md`** - AI execution engine (loads whether PRD created or not)
- **`100_backlog-guide.md`** - Backlog management and scoring guidelines

### **🏗️ SYSTEM ARCHITECTURE FILES (Technical Implementation)**
- **`104_dspy-development-context.md`** - DSPy framework implementation details
- **`202_setup-requirements.md`** - Environment setup and dependencies
- **`400_context-priority-guide.md`** - Memory scaffolding and file organization
- **`400_context-engineering-compatibility-analysis.md`** - Context engineering compatibility
- **`400_cursor-context-engineering-guide.md`** - Context engineering implementation

### **🔧 OPERATIONAL GUIDES (Production & Maintenance)**
- **`400_testing-strategy-guide_additional_resources.md`** - Testing methodologies and frameworks
- **`400_security-best-practices-guide.md`** - Security implementation and validation
- **`400_performance-optimization-guide_additional_resources.md`** - Performance tuning and monitoring
- **`400_deployment-environment-guide_additional_resources.md`** - Deployment and environment management
- **`400_migration-upgrade-guide_ai_model_upgrade_procedures.md`** - System migration and upgrade procedures
- **`400_integration-patterns-guide_additional_resources.md`** - Integration patterns and best practices
- **`400_metadata-collection-guide.md`** - Metadata collection and management
- **`400_metadata-quick-reference.md`** - Quick metadata reference
- **`400_few-shot-context-examples_additional_resources.md`** - Few-shot learning examples
- **`400_prd-optimization-guide.md`** - PRD optimization techniques
- **`400_n8n-backlog-scrubber-guide.md`** - n8n workflow automation
- **`400_mistral7b-instruct-integration-guide.md`** - Mistral integration (legacy)

### **📊 RESEARCH DOCUMENTATION (500-Series)**
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

### **📁 EXTERNAL RESEARCH (docs/research/)**
- **`docs/research/papers/`** - Academic papers and research sources
- **`docs/research/articles/`** - Industry articles and blog posts
- **`docs/research/tutorials/`** - Implementation tutorials and guides

### **🎯 DOMAIN-SPECIFIC FILES (B-Series & C-Series)**
- **`CURSOR_NATIVE_AI_STRATEGY.md`** - Cursor Native AI strategy (supports B-011)
- **`B-011-PRD.md`** - Cursor Native AI + Specialized Agents PRD
- **`B-011-Tasks.md`** - Cursor Native AI implementation tasks
- **`B-011-DEPLOYMENT-GUIDE_backup_recovery.md`** - B-011 deployment guide
- **`B-011-DEVELOPER-DOCUMENTATION_api_documentation.md`** - B-011 developer docs
- **`B-011-USER-DOCUMENTATION.md`** - B-011 user documentation
- **`B-049-PRD.md`** - Domain-specific PRD
- **`B-049-Tasks.md`** - Domain-specific tasks
- **`B-072-PRD.md`** - Domain-specific PRD
- **`B-072-Tasks.md`** - Domain-specific tasks

### **🔍 ANALYSIS & MAINTENANCE FILES**
- **`400_file-analysis-guide.md`** - **🚨 MANDATORY: File deletion/deprecation analysis**
- **`200_naming-conventions.md`** - File naming and organization system
- **`400_cross-reference-strengthening-plan.md`** - Cross-reference improvement plan
- **`999_repo-maintenance.md`** - Repository maintenance procedures

### **📈 COMPLETION SUMMARIES (500-Series)**
- **`500_b002-completion-summary.md`** - B-002 completion summary
- **`500_b031-completion-summary.md`** - B-031 completion summary
- **`500_b060-completion-summary.md`** - B-060 completion summary
- **`500_b065-completion-summary.md`** - B-065 completion summary
- **`500_b070-completion-summary.md`** - B-070 completion summary

### **🔧 IMPLEMENTATION FILES**
- **`specialized_agent_framework.py`** - Specialized agent implementation
- **`cursor_ai_integration_framework.py`** - Cursor AI integration
- **`context_management_implementation.py`** - Context management
- **`agent_communication_implementation.py`** - Agent communication
- **`documentation_agent_implementation.py`** - Documentation agent
- **`coder_agent_implementation.py`** - Coder agent
- **`research_agent_implementation.py`** - Research agent

## 🔍 File Analysis Strategy

### **AI File Analysis Strategy**
When Cursor AI restarts, it follows a **structured reading strategy**: First reads `100_cursor-memory-context.md` (30 seconds, 80% context), then `000_backlog.md` (current priorities), then `400_system-overview_advanced_features.md` (technical architecture). Ancillary files are read as needed for specific tasks. Scripts are only read when implementation details are required.

### **File Generation Decision Process**
When creating new files, follow a **6-step decision process**: 1) Determine if file is needed (reusable info vs. temporary), 2) Assess purpose and priority (planning vs. implementation vs. research), 3) Choose prefix range (000-099 for core, 100-199 for guides, etc.), 4) Create descriptive name (kebab-case, self-documenting), 5) Add cross-references and consider AI rehydration, 6) Validate against existing patterns.

### **Documentation Placement Logic**
When determining where to place new documentation, follow a **5-step process**: 1) Assess content type and scope (system-wide vs. workflow vs. setup), 2) Choose primary location based on content (400-499 for concepts, 200-299 for processes), 3) Determine if multiple locations needed (core concepts get quick reference + detailed), 4) Consider reading pattern (immediate vs. when relevant vs. when needed), 5) Add cross-references for discovery.

## 📊 Documentation Utilization Checklist

**Before starting any task, ensure you've checked:**
- [ ] **Current state** in `100_cursor-memory-context.md`
- [ ] **Priorities** in `000_backlog.md`
- [ ] **Technical context** in `400_system-overview_advanced_features.md`
- [ ] **Relevant guides** in 400-series for specific tasks
- [ ] **Research findings** in 500-series for research tasks
- [ ] **Domain-specific docs** for B/C-series items
- [ ] **Analysis methodology** for file operations

**📚 Quick Navigation Tools:**
- **Complete inventory**: `python3 scripts/documentation_navigator.py inventory`
- **Context guidance**: `python3 scripts/documentation_navigator.py guidance`
- **Task-specific files**: `python3 scripts/documentation_navigator.py find <task_type>`

**This ensures full utilization of our comprehensive documentation system!** 🎯

## 🔒 Safety Validation

### **Constitution Compliance**
All operations must comply with the AI Constitution (`400_ai-constitution.md`):
- **File Safety**: Validate against constitution rules before any file operations
- **Context Preservation**: Maintain context integrity across all operations
- **Error Prevention**: Follow systematic error prevention and recovery patterns
- **Documentation Coherence**: Preserve cross-reference and naming convention integrity

### **Validation Framework**
Use the constitution compliance checker for validation:
- **Pre-Operation Checks**: Validate against constitution rules before any operation
- **During Operation Monitoring**: Monitor for constitution rule violations
- **Post-Operation Validation**: Verify constitution compliance after operations
- **Violation Logging**: Log violations to `constitution_violations.jsonl` for tracking

---

*Last Updated: 2024-08-07 21:00*
*Next Review: When safety requirements change*

<!-- SAFETY_MODULE_METADATA
version: 1.0
split_date: 2024-08-07
parent_file: 100_cursor-memory-context.md
core_module: 100_cursor-memory-context.md
compliance: 400_ai-constitution.md
research_basis: 500_documentation-coherence-research.md
-->
