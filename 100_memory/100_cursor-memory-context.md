<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_system-overview.md -->
<!-- MODULE_REFERENCE: 000_core/000_backlog.md -->
<!-- DATABASE_SYNC: REQUIRED -->
<!-- CONTEXT_INDEX
{
  "files": [
    {"path": "100_memory/100_cursor-memory-context.md", "role": "entry"},
    {"path": "000_core/000_backlog.md", "role": "priorities"},
    {"path": "400_guides/400_project-overview.md", "role": "project-overview"},
    {"path": "400_guides/400_system-overview.md", "role": "architecture"},
    {"path": "400_guides/400_context-priority-guide.md", "role": "navigation"},
    {"path": "400_guides/400_ai-constitution.md", "role": "ai-safety"},
    {"path": "400_guides/400_file-analysis-guide.md", "role": "file-analysis"},
    {"path": "400_guides/400_code-criticality-guide.md", "role": "code-quality"},
    {"path": "100_memory/104_dspy-development-context.md", "role": "dspy-context"},
    {"path": "dspy-rag-system/tests/README-dev.md", "role": "test-development"},
    {"path": "200_setup/202_setup-requirements.md", "role": "setup"},
    {"path": "400_guides/400_comprehensive-coding-best-practices.md", "role": "coding-standards"},
    {"path": "400_guides/400_deployment-environment-guide.md", "role": "deployment"},
    {"path": "400_guides/400_integration-patterns-guide.md", "role": "integration"},
    {"path": "400_guides/400_migration-upgrade-guide.md", "role": "migration"},
    {"path": "400_guides/400_performance-optimization-guide.md", "role": "performance"},
    {"path": "400_guides/400_testing-strategy-guide.md", "role": "testing"},
    {"path": "400_guides/400_security-best-practices-guide.md", "role": "security"},
    {"path": "400_guides/400_few-shot-context-examples.md", "role": "few-shot"},
    {"path": "500_research-index.md", "role": "research-index"}
  ]
}
CONTEXT_INDEX -->

<!-- ANCHOR_KEY: memory-context -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

# Cursor Memory Context

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Primary memory scaffold for AI rehydration and context management | Starting new session or need current project state
| Check backlog and system overview for next priorities |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

## ⚡ AI Rehydration Quick Start {#quick-start}

Read these files in order (1–2 min total):

1. **`400_guides/400_project-overview.md`** – 5-minute overview and workflow ← **START HERE**
2. **`100_memory/100_cursor-memory-context.md`** – current state and rules
3. **`000_core/000_backlog.md`** – priorities and dependencies
4. **`400_guides/400_system-overview.md`** – architecture and components
5. **`400_guides/400_context-priority-guide.md`** – relationships and reading order

<!-- ANCHOR_KEY: quick-start -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

## 🧠 Hydration Bundle Policy {#hydration-policy}

The memory rehydrator builds role-aware context bundles with this priority:

1. **Pinned Anchors** (stable backbone - always loaded first)
   - TL;DR → quick-start → quick-links → commands
   - Role-specific pins (planner → system overview/backlog, implementer → DSPy context)

2. **Task-Scoped Retrieval** (hybrid search via vector store)
   - Top K anchor/chunk candidates based on current task
   - Uses optimized vector store with span grounding

3. **Token Budgeting** (~1,200 tokens default)
   - Pins first, then anchor-like content, then general spans
   - Trims soft layers first to keep stable anchors intact

## 🛠️ Commands {#commands}

- Start tests: `./dspy-rag-system/run_tests.sh --tiers 1 --kinds smoke` (new marker-based approach)
- Legacy tests: `./dspy-rag-system/run_tests.sh all` (legacy mode - avoid)

- Start dashboard: `./dspy-rag-system/start_mission_dashboard.sh`

- Quick inventory: `python3 scripts/documentation_navigator.py inventory`

- Quick conflict check: `python scripts/quick_conflict_check.py`

- Comprehensive conflict audit: `python scripts/conflict_audit.py --full`

## 🔧 Import Policy (CRITICAL)

### **Current Approach (Use This):**
- **Tests**: Use `conftest.py` for centralized import paths
- **Scripts**: Use `setup_imports.py` for scripts outside pytest context
- **No manual sys.path**: Remove per-file path manipulation

### **Legacy Approach (Avoid):**
- ❌ Manual `sys.path.insert()` in test files
- ❌ `comprehensive_test_suite.py` for new development
- ❌ Direct `src.utils` imports in tests

### **Test Execution:**
- ✅ **New**: `./run_tests.sh --tiers 1 --kinds smoke` (marker-based)
- ❌ **Legacy**: `./run_tests.sh all` (file-based)

<!-- ANCHOR_KEY: commands -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

## 🔗 Quick Links {#quick-links}

- System overview → `400_guides/400_system-overview.md`

- Backlog & priorities → `000_core/000_backlog.md`

- Start here → `docs/README.md`

- Context priority guide → `400_guides/400_context-priority-guide.md`

- Critical Python code map → `400_guides/400_code-criticality-guide.md`

- Testing strategy → `400_guides/400_testing-strategy-guide.md`

- Test development guide → `dspy-rag-system/tests/README-dev.md`

- Deployment guide → `400_guides/400_deployment-environment-guide.md`

- Migration & upgrades → `400_guides/400_migration-upgrade-guide.md`

- Integration patterns → `400_guides/400_integration-patterns-guide.md`

- Performance optimization → `400_guides/400_performance-optimization-guide.md`

- Security best practices → `400_guides/400_security-best-practices-guide.md`

- Environment setup → `200_setup/202_setup-requirements.md`

- DSPy deep context → `100_memory/104_dspy-development-context.md`

<!-- ANCHOR_KEY: quick-links -->
<!-- ANCHOR_PRIORITY: 20 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

- Comprehensive coding standards → `400_guides/400_comprehensive-coding-best-practices.md` (includes "Undefined Name" error fixes, database query patterns, and systematic test file patterns)

### Stable Anchors

- tldr

- quick-start

- quick-links

- commands

### Role → Files (at a glance)

- Planner: `400_guides/400_project-overview.md`, `400_guides/400_system-overview.md`,
`400_guides/400_context-priority-guide.md`

- Implementer: `100_memory/104_dspy-development-context.md`, `dspy-rag-system/tests/README-dev.md`, relevant 400-series topic guides (testing, security,
performance, integration, deployment)

- Researcher: `500_research/500_research-index.md`, `500_research/500_dspy-research.md`,
`500_research/500_rag-system-research.md`

- Ops/Setup: `200_setup/202_setup-requirements.md`, `400_guides/400_deployment-environment-guide.md`,
`400_guides/400_migration-upgrade-guide.md`

## 🛡️ Always-On Critical Rules

- Follow `400_guides/400_file-analysis-guide.md` before any deletion/move/depredation

- Preserve coherence: update cross-references when editing core files

- Use consolidated guides (single-file sources) for deployment, migration, integration, performance, testing, system
overview, few-shot

- Keep this file updated after architecture changes

- Prefer local-first, simple workflows; avoid unnecessary complexity

- Focus context on Cursor-based LLMs only

### Legacy Content Policy

- Exclusions: `docs/legacy/**`, `600_archives/**` are reference-only.

- Legacy integrations must not appear in active docs; keep under `600_archives/`.

- Before archiving/moving: follow `400_guides/400_file-analysis-guide.md`. After changes: run `python3
scripts/update_cursor_memory.py`.

## 🚨 CRITICAL SAFETY REQUIREMENTS

- *BEFORE ANY FILE OPERATIONS:**- [ ] Read `400_guides/400_file-analysis-guide.md` completely (463 lines)

- [ ] Complete 6-step mandatory analysis

- [ ] Show all cross-references

- [ ] Get explicit user approval**🤖 AI CONSTITUTION COMPLIANCE:**- [ ] Follow `400_guides/400_ai-constitution.md` rules
for all AI operations

- [ ] Maintain context preservation and safety requirements

- [ ] Validate against constitution rules before any changes

## 🎯 Purpose

This file serves as the **memory scaffold**for Cursor AI, providing instant context about the AI development ecosystem
without requiring the AI to read multiple files.

## 📋 Current Project State

### **Active Development Focus**-**Current Sprint**: Align with `000_core/000_backlog.md` (see Current Priorities)

- **Next Priorities**: Follow `000_core/000_backlog.md` ordering and scores

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

### **Key Technologies**

- **AI Models**: Cursor Native AI (foundation), Specialized Agents (enhancements). Cursor models only; legacy local model instructions are archived under `600_archives/**`.

- **Framework**: DSPy with PostgreSQL vector store

- **Automation**: n8n workflows for backlog management

- **Monitoring**: Real-time mission dashboard

- **Security**: Comprehensive input validation and prompt sanitization

- **Extraction**: LangExtract (Gemini Flash) for entity/attribute extraction

## 🔄 Development Workflow

**For complete workflow details, see `400_guides/400_project-overview.md`**

**Quick Workflow Overview:**

1. **Backlog Selection** → Pick top scored item from `000_core/000_backlog.md`
2. **PRD Creation** → Use `000_core/001_create-prd.md` (skip for items < 5 pts AND score≥3.0)
3. **Task Generation** → Use `000_core/002_generate-tasks.md` workflow
4. **AI Execution** → Use `000_core/003_process-task-list.md` (the execution engine)
5. **State Management** → `.ai_state.json` for context persistence

<!-- WORKFLOW_REFERENCE: 400_guides/400_project-overview.md -->

### **File Organization**

- **Essential**: `400_guides/400_project-overview.md`, `400_guides/400_system-overview.md`, `000_core/000_backlog.md`

- **Implementation**: `100_memory/104_dspy-development-context.md`, `200_setup/202_setup-requirements.md`

- **Analysis**: `400_guides/400_file-analysis-guide.md` - **🚨 MANDATORY: File deletion/deprecation analysis methodology**
- **Domain**: `100_memory/100_backlog-guide.md`

- *⚠️ CRITICAL**: Before ANY file operations, you MUST read and follow `400_guides/400_file-analysis-guide.md` completely!

## 🛠️ Development Guidelines

### **🚨 MANDATORY: File Deletion/Deprecation Analysis**

- *Before suggesting ANY file deletion or deprecation, you MUST:

1. Run the analysis checklist**: `python3 scripts/file_analysis_checklist.py <target_file>`
2. **Follow the 6-step process**in `400_guides/400_file-analysis-guide.md`
3.**Complete ALL steps**before making recommendations
4.**Get explicit user approval**for high-risk operations**This is NON-NEGOTIABLE**- failure to follow these steps means you cannot suggest file deletion!

## 🚨 CRITICAL SAFETY REQUIREMENTS

### **⚠️ MANDATORY: File Analysis Before Any File Operations**

- *BEFORE suggesting ANY file deletion, deprecation, or archiving, you MUST:**1.**Read `400_guides/400_file-analysis-guide.md`**- Complete the 6-step mandatory analysis
2.**Complete ALL steps**- No exceptions, no shortcuts
3.**Show cross-references**- Prove you've done the analysis
4.**Get user approval**- For any high-risk operations**🚨 FAILURE TO FOLLOW THESE STEPS MEANS YOU CANNOT SUGGEST FILE OPERATIONS!**

- *📋 Quick Checklist:**- [ ] Read `400_guides/400_file-analysis-guide.md` (463 lines - READ ALL OF IT)

- [ ] Complete 6-step mandatory analysis

- [ ] Show all cross-references

- [ ] Provide detailed reasoning

- [ ] Get explicit user approval

### **📚 Complete Documentation Inventory**

**For complete documentation inventory, see `400_guides/400_documentation-reference.md`**

**Essential Files Quick Reference:**

- **Critical**: `100_memory/100_cursor-memory-context.md`, `000_core/000_backlog.md`, `400_guides/400_system-overview.md`, `400_guides/400_project-overview.md`
- **Workflow**: `000_core/001_create-prd.md`, `000_core/002_generate-tasks.md`, `000_core/003_process-task-list.md`
- **Setup**: `200_setup/202_setup-requirements.md`
- **Architecture**: `100_memory/104_dspy-development-context.md`
- **Coding Standards**: `400_guides/400_comprehensive-coding-best-practices.md` (NEW - conflict prevention system)

### **🗄️ Vector Database Status**

**Database**: PostgreSQL with pgvector extension
**Status**: ✅ **FULLY SYNCHRONIZED** (2025-08-14)
**Coverage**: 32 documents, 1,064 chunks
**CONTEXT_INDEX**: 20/20 files indexed with role mapping

#### **Database Health:**
- **Core Files**: 11/11 files current and indexed
- **400_guides**: 14/14 files current and indexed
- **500_research**: 1/1 files current and indexed
- **Cross-References**: 35% average coverage across all guides
- **Semantic Search**: Full-text, vector similarity, and metadata search operational

#### **AI Rehydration Capability:**
- **Memory Rehydrator**: Can access all core documentation
- **Role-Aware Context**: Builds context bundles based on CONTEXT_INDEX roles
- **Task-Scoped Retrieval**: Hybrid search via vector store with span grounding
- **Token Budgeting**: ~1,200 tokens default with pinned anchors first

#### **Recent Database Updates:**
- **P0 Critical**: Updated outdated files (100_cursor-memory-context.md, 000_backlog.md)
- **P1 High**: Added 7 missing files from CONTEXT_INDEX
- **Verification**: Complete database integrity check passed
- **Cross-Reference Analysis**: All guides properly linked

<!-- DOCUMENTATION_REFERENCE: 400_guides/400_documentation-reference.md -->

### **🎯 When to Read What: Context-Specific Guidance**

**For detailed context-specific guidance, see `400_guides/400_documentation-reference.md`**

**Quick Reading Order:**

1. **New Sessions**: `400_guides/400_project-overview.md` → `100_memory/100_cursor-memory-context.md` → `000_core/000_backlog.md` → `400_guides/400_system-overview.md`
2. **Development**: `400_guides/400_project-overview.md` → workflow files → implementation guides
3. **Research**: `500_research/500_research-index.md` → `500_research/500_dspy-research.md`, `500_research/500_rag-system-research.md`
4. **File Management**: `400_guides/400_file-analysis-guide.md` (MANDATORY) → `200_setup/200_naming-conventions.md`

### **🔗 Cross-Reference System**

**Status**: ✅ **FULLY OPERATIONAL** (2025-08-14)

#### **CONTEXT_INDEX Coverage:**
- **Total Files**: 20 files with role-based indexing
- **Core Files**: 13 files (entry, priorities, architecture, navigation, etc.)
- **Specialized Files**: 7 files (deployment, integration, migration, etc.)
- **Role Mapping**: Each file assigned specific role for AI rehydration

#### **Cross-Reference Quality:**
- **High Coverage**: 400_context-priority-guide.md (72% cross-references)
- **Medium Coverage**: 400_ai-constitution.md, 400_code-criticality-guide.md (38-48%)
- **Low Coverage**: 400_deployment-environment-guide.md, 400_performance-optimization-guide.md (3-4%)
- **Average Coverage**: 35% across all 400_guides files

#### **Navigation Patterns:**
- **Safety-First**: AI constitution and file analysis guides prominently referenced
- **Quality-Focused**: Code criticality and testing strategy guides well-linked
- **Development-Oriented**: Project overview and system overview central to navigation
- **Specialized Access**: Deployment, integration, migration guides available for specific tasks

<!-- CONTEXT_GUIDANCE_REFERENCE: 400_guides/400_documentation-reference.md -->

<!-- AUTO:current_priorities:start -->
### **Current Priorities**

1. **B‑091**: Strict Anchor Enforcement (Phase 2) (🔥 points)
   - todo

2. **B‑043**: LangExtract Pilot w/ Stratified 20-doc Set (🔥 points)
   - todo

3. **B‑076**: Research-Based DSPy Assertions Implementation (🔥 points)
   - todo

4. **B‑078**: LangExtract Structured Extraction Service (🔥 points)
   - todo

5. **B‑052‑f**: Enhanced Repository Maintenance Safety System (🔥 points)
   - todo
<!-- AUTO:current_priorities:end -->

<!-- AUTO:recently_completed:start -->
No recently completed items.
<!-- AUTO:recently_completed:end -->

<!-- AUTO:doc_health:start -->
### **Documentation Health**

- Files checked: 5
- Anchor warnings: 0
- Invariant warnings: 0
- Last run: Fri Aug  8 23:58:13 CDT 2025
<!-- AUTO:doc_health:end -->
