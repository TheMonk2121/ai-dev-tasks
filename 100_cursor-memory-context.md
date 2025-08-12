<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
<!-- MODULE_REFERENCE: 000_backlog.md -->
<!-- CONTEXT_INDEX
{
  "files": [
    {"path": "100_cursor-memory-context.md", "role": "entry"},
    {"path": "000_backlog.md", "role": "priorities"},
    {"path": "400_system-overview.md", "role": "architecture"},
    {"path": "400_context-priority-guide.md", "role": "navigation"},
    {"path": "104_dspy-development-context.md", "role": "dspy-context"},
    {"path": "202_setup-requirements.md", "role": "setup"},
    {"path": "400_deployment-environment-guide.md", "role": "deployment"},
    {"path": "400_integration-patterns-guide.md", "role": "integration"},
    {"path": "400_migration-upgrade-guide.md", "role": "migration"},
    {"path": "400_performance-optimization-guide.md", "role": "performance"},
    {"path": "400_testing-strategy-guide.md", "role": "testing"},
    {"path": "400_security-best-practices-guide.md", "role": "security"},
    {"path": "400_few-shot-context-examples.md", "role": "few-shot"},
    {"path": "500_research-index.md", "role": "research-index"}
  ]
}
CONTEXT_INDEX -->

# Cursor Memory Context

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Primary memory scaffold for AI rehydration and context management | At start of every new session or after major system changes | Read in order: README.md → 000_backlog.md → 400_system-overview.md |

- Single source for AI rehydration and human quick scan

- Read order: `100_cursor-memory-context.md` → `README.md` → `000_backlog.md` → `400_system-overview.md` → `400_context-priority-guide.md`

- Always follow safety rules in `400_file-analysis-guide.md`; never delete/move without the 6-step mandatory analysis checklist

- Use consolidated 400-series guides (comprehensive single-file documentation like `400_system-overview.md`, `400_testing-strategy-guide.md`, etc.) - no split modules

- Focus on Cursor-based LLM context only (no external model specifics)

- Keep changes small; update this file after major shifts

## ⚡ AI Rehydration Quick Start {#quick-start}

Read these files in order (1–2 min total):

- `100_cursor-memory-context.md` – current state and rules

- `000_backlog.md` – priorities and dependencies

- `400_system-overview.md` – architecture and components

- `400_context-priority-guide.md` – relationships and reading order

## 🛠️ Commands {#commands}

- Start tests: `./dspy-rag-system/run_tests.sh`

- Start dashboard: `./dspy-rag-system/start_mission_dashboard.sh`

- Quick inventory: `python3 scripts/documentation_navigator.py inventory`

## 🔗 Quick Links {#quick-links}

- System overview → `400_system-overview.md`

- Backlog & priorities → `000_backlog.md`

- Start here → `README.md`

- Context priority guide → `400_context-priority-guide.md`

- Critical Python code map → `400_code-criticality-guide.md`

- Testing strategy → `400_testing-strategy-guide.md`

- Deployment guide → `400_deployment-environment-guide.md`

- Migration & upgrades → `400_migration-upgrade-guide.md`

- Integration patterns → `400_integration-patterns-guide.md`

- Performance optimization → `400_performance-optimization-guide.md`

- Security best practices → `400_security-best-practices-guide.md`

- Environment setup → `202_setup-requirements.md`

- DSPy deep context → `104_dspy-development-context.md`

### Stable Anchors

- tldr

- quick-start

- quick-links

- commands

### Role → Files (at a glance)

- Planner: `400_project-overview.md`, `400_system-overview.md`, `400_context-priority-guide.md`

- Implementer: `104_dspy-development-context.md`, relevant 400-series topic guides (testing, security, performance, integration, deployment)

- Researcher: `500_research-summary.md`, `500_research-analysis-summary.md`, `500_research-implementation-summary.md`

- Ops/Setup: `202_setup-requirements.md`, `400_deployment-environment-guide.md`, `400_migration-upgrade-guide.md`

## 🛡️ Always-On Critical Rules

- Follow `400_file-analysis-guide.md` before any deletion/move/depredation

- Preserve coherence: update cross-references when editing core files

- Use consolidated guides (single-file sources) for deployment, migration, integration, performance, testing, system overview, few-shot

- Keep this file updated after architecture changes

- Prefer local-first, simple workflows; avoid unnecessary complexity

- Focus context on Cursor-based LLMs only

### Legacy Content Policy

- Exclusions: `docs/legacy/**`, `600_archives/**` are reference-only.

- Legacy integrations must not appear in active docs; keep under `600_archives/`.

- Before archiving/moving: follow `400_file-analysis-guide.md`. After changes: run `python3 scripts/update_cursor_memory.py`.

## 🚨 CRITICAL SAFETY REQUIREMENTS

- *BEFORE ANY FILE OPERATIONS:**- [ ] Read `400_file-analysis-guide.md` completely (463 lines)

- [ ] Complete 6-step mandatory analysis

- [ ] Show all cross-references

- [ ] Get explicit user approval**🤖 AI CONSTITUTION COMPLIANCE:**- [ ] Follow `400_ai-constitution.md` rules for all AI operations

- [ ] Maintain context preservation and safety requirements

- [ ] Validate against constitution rules before any changes

## 🎯 Purpose

This file serves as the **memory scaffold**for Cursor AI, providing instant context about the AI development ecosystem
without requiring the AI to read multiple files.

## 📋 Current Project State

### **Active Development Focus**-**Current Sprint**: Align with `000_backlog.md` (see Current Priorities)

- **Next Priorities**: Follow `000_backlog.md` ordering and scores

- **Validator**: Use `scripts/doc_coherence_validator.py` (or pre-commit hook) after doc changes

### **System Architecture**

```text
AI Development Ecosystem
├── Planning Layer (PRD → Tasks → Execution)
├── AI Execution Layer (Cursor Native AI + Specialized Agents)
├── Core Systems (DSPy RAG + n8n + Dashboard)
├── Extraction Layer (LangExtract → Entity/Attribute Extraction)
└── Infrastructure (PostgreSQL + Monitoring)
```

### **Key Technologies**-**AI Models**: Cursor Native AI (foundation), Specialized Agents (enhancements)

- **Framework**: DSPy with PostgreSQL vector store

- **Automation**: n8n workflows for backlog management

- **Monitoring**: Real-time mission dashboard

- **Security**: Comprehensive input validation and prompt sanitization

- **Extraction**: LangExtract (Gemini Flash) for entity/attribute extraction

## 🔄 Development Workflow

**For complete workflow details, see `400_project-overview.md`**

**Quick Workflow Overview:**

1. **Backlog Selection** → Pick top scored item from `000_backlog.md`
2. **PRD Creation** → Use `001_create-prd.md` (skip for items < 5 pts AND score≥3.0)
3. **Task Generation** → Use `002_generate-tasks.md` workflow
4. **AI Execution** → Use `003_process-task-list.md` (the execution engine)
5. **State Management** → `.ai_state.json` for context persistence

<!-- WORKFLOW_REFERENCE: 400_project-overview.md -->

### **File Organization**-**Essential**: `400_project-overview.md`, `400_system-overview.md`, `000_backlog.md`

- **Implementation**: `104_dspy-development-context.md`, `202_setup-requirements.md`

- **Analysis**: `400_file-analysis-guide.md` - **🚨 MANDATORY: File deletion/deprecation analysis methodology**-**Domain**: `100_backlog-guide.md`, `CURSOR_NATIVE_AI_STRATEGY.md`

- *⚠️ CRITICAL**: Before ANY file operations, you MUST read and follow `400_file-analysis-guide.md` completely!

## 🛠️ Development Guidelines

### **🚨 MANDATORY: File Deletion/Deprecation Analysis**

- *Before suggesting ANY file deletion or deprecation, you MUST:

1. Run the analysis checklist**: `python3 scripts/file_analysis_checklist.py <target_file>`
2. **Follow the 6-step process**in `400_file-analysis-guide.md`
3.**Complete ALL steps**before making recommendations
4.**Get explicit user approval**for high-risk operations**This is NON-NEGOTIABLE**- failure to follow these steps means you cannot suggest file deletion!

## 🚨 CRITICAL SAFETY REQUIREMENTS

### **⚠️ MANDATORY: File Analysis Before Any File Operations**

- *BEFORE suggesting ANY file deletion, deprecation, or archiving, you MUST:**1.**Read `400_file-analysis-guide.md`**- Complete the 6-step mandatory analysis
2.**Complete ALL steps**- No exceptions, no shortcuts
3.**Show cross-references**- Prove you've done the analysis
4.**Get user approval**- For any high-risk operations**🚨 FAILURE TO FOLLOW THESE STEPS MEANS YOU CANNOT SUGGEST FILE OPERATIONS!**

- *📋 Quick Checklist:**- [ ] Read `400_file-analysis-guide.md` (463 lines - READ ALL OF IT)

- [ ] Complete 6-step mandatory analysis

- [ ] Show all cross-references

- [ ] Provide detailed reasoning

- [ ] Get explicit user approval

### **📚 Complete Documentation Inventory**####**🎯 CRITICAL FILES (Read First)**-**`100_cursor-memory-context.md`**- Primary memory scaffold (this file)

- **`000_backlog.md`**- Current priorities and development roadmap

- **`400_system-overview.md`**- Technical architecture and system-of-systems

- **`400_project-overview.md`**- High-level project goals and workflow

#### **📋 WORKFLOW FILES (Development Process)**-**`001_create-prd.md`**- PRD creation workflow (skip for items < 5 pts AND score≥3.0)

- **`002_generate-tasks.md`**- Task generation workflow (parses PRD or backlog)

- **`003_process-task-list.md`**- AI execution engine (loads whether PRD created or not)

- **`100_backlog-guide.md`**- Backlog management and scoring guidelines

#### **🏗️ SYSTEM ARCHITECTURE FILES (Technical Implementation)**-**`104_dspy-development-context.md`**- DSPy framework implementation details

- **`202_setup-requirements.md`**- Environment setup and dependencies

- **`400_context-priority-guide.md`**- Memory scaffolding and file organization

- **`400_cursor-context-engineering-guide.md`**- Context engineering strategy and compatibility (appendix)

- **`400_cursor-context-engineering-guide.md`**- Context engineering implementation

#### **🔧 OPERATIONAL GUIDES (Production & Maintenance)**-**`400_testing-strategy-guide.md`**- Testing methodologies and frameworks

- **`400_security-best-practices-guide.md`**- Security implementation and validation

- **`400_performance-optimization-guide.md`**- Performance tuning and monitoring

- **`400_deployment-environment-guide.md`**- Deployment and environment management

- **`400_migration-upgrade-guide.md`**- System migration and upgrade procedures

- **`400_integration-patterns-guide.md`**- Integration patterns and best practices

- **`400_metadata-collection-guide.md`**- Metadata collection and management

- Quick metadata reference: see `400_metadata-collection-guide.md` (Quick reference section)

- **`400_few-shot-context-examples.md`**- Few-shot learning examples

- - PRD optimization: see `001_create-prd.md` (skip rule), `002_generate-tasks.md` (PRD-less path), and
`100_backlog-guide.md` (decision matrix)

- **`400_n8n-backlog-scrubber-guide.md`**- n8n workflow automation

#### **📊 RESEARCH DOCUMENTATION (500-Series)**-**`500_research-summary.md`**- Research overview and findings

- **`500_research-analysis-summary.md`**- Research analysis methodology

- **`500_research-implementation-summary.md`**- Research implementation findings

- **`500_research-infrastructure-guide.md`**- Research infrastructure setup

- **`500_dspy-research.md`**- DSPy framework research findings

- **`500_rag-system-research.md`**- RAG system research findings

- **`500_documentation-coherence-research.md`**- Documentation coherence research

- **`500_maintenance-safety-research.md`**- Repository maintenance safety

- **`500_performance-research.md`**- Performance optimization research

- **`500_monitoring-research.md`**- System monitoring research

- **`500_agent-orchestration-research.md`**- Multi-agent orchestration research

#### **📁 EXTERNAL RESEARCH (docs/research/)**-**`docs/research/papers/`**- Academic papers and research sources

- **`docs/research/articles/`**- Industry articles and blog posts

- **`docs/research/tutorials/`**- Implementation tutorials and guides

#### **🎯 DOMAIN-SPECIFIC FILES (B-Series & C-Series)**-**`CURSOR_NATIVE_AI_STRATEGY.md`**- Cursor Native AI strategy (supports B-011)

- **`B-011-PRD.md`**- Cursor Native AI + Specialized Agents PRD

- **`B-011-Tasks.md`**- Cursor Native AI implementation tasks

- **`B-011-DEPLOYMENT-GUIDE_backup_recovery.md`**- B-011 deployment guide

- **`B-011-DEVELOPER-DOCUMENTATION_api_documentation.md`**- B-011 developer docs

- **`B-011-USER-DOCUMENTATION.md`**- B-011 user documentation

- **`B-049-PRD.md`**- Domain-specific PRD

- **`B-049-Tasks.md`**- Domain-specific tasks

- **`B-072-PRD.md`**- Domain-specific PRD

- **`B-072-Tasks.md`**- Domain-specific tasks

#### **🔍 ANALYSIS & MAINTENANCE FILES**-**`400_file-analysis-guide.md`**-**🚨 MANDATORY: File deletion/deprecation analysis**-**`200_naming-conventions.md`**- File naming and organization system

- **`400_cross-reference-strengthening-plan.md`**- Cross-reference improvement plan

- **`999_repo-maintenance.md`**- Repository maintenance procedures

#### **📈 COMPLETION SUMMARIES (500-Series)**-**`500_b002-completion-summary.md`**- B-002 completion summary

- **`500_b031-completion-summary.md`**- B-031 completion summary

- **`500_b060-completion-summary.md`**- B-060 completion summary

- **`500_b065-completion-summary.md`**- B-065 completion summary

#### **🔧 IMPLEMENTATION FILES**-**`specialized_agent_framework.py`**- Specialized agent implementation

- **`cursor_ai_integration_framework.py`**- Cursor AI integration

- **`context_management_implementation.py`**- Context management

- **`agent_communication_implementation.py`**- Agent communication

- **`documentation_agent_implementation.py`**- Documentation agent

- **`coder_agent_implementation.py`**- Coder agent

- **`research_agent_implementation.py`**- Research agent

### **🎯 When to Read What: Context-Specific Guidance**####**For New Sessions (First 2-3 minutes)

1.**`100_cursor-memory-context.md`**- Current project state
2.**`000_backlog.md`**- Current priorities
3.**`400_system-overview.md`**- Technical architecture

#### **For Development Tasks:**-**Planning**: `001_create-prd.md` → `002_generate-tasks.md` → `003_process-task-list.md`

- **Implementation**: `104_dspy-development-context.md` + relevant 400-series guides

- **Testing**: `400_testing-strategy-guide.md`

- **Security**: `400_security-best-practices-guide.md`

- **Performance**: `400_performance-optimization-guide.md`

#### **For Research Tasks:**-**Overview**: `500_research-summary.md`

- **Methodology**: `500_research-analysis-summary.md`

- **Implementation**: `500_research-implementation-summary.md`

- **External Sources**: `docs/research/papers/`, `docs/research/articles/`, `docs/research/tutorials/`

#### **For File Management:**-**Analysis**: `400_file-analysis-guide.md` (MANDATORY)

- **Naming**: `200_naming-conventions.md`

- **Organization**: `400_context-priority-guide.md`

#### **For System Integration:**-**Architecture**: `400_system-overview.md`

- **Patterns**: `400_integration-patterns-guide.md`

- **Deployment**: `400_deployment-environment-guide.md`

- **Migration**: `400_migration-upgrade-guide.md`

#### **For Context Engineering:**-**Strategy**: `400_cursor-context-engineering-guide.md`

- **Compatibility**: `400_cursor-context-engineering-guide.md`

- **Implementation**: `104_dspy-development-context.md`

### **📊 Documentation Utilization Checklist**

- *Before starting any task, ensure you've checked:**- [ ]**Current state**in `100_cursor-memory-context.md`

- [ ]**Priorities**in `000_backlog.md`

- [ ]**Technical context**in `400_system-overview.md`

- [ ]**Relevant guides**in 400-series for specific tasks

- [ ]**Research findings**in 500-series for research tasks

- [ ]**Domain-specific docs**for B/C-series items

- [ ]**Analysis methodology**for file operations**📚 Quick Navigation Tools:**-**Complete inventory**: `python3 scripts/documentation_navigator.py inventory`

- **Context guidance**: `
