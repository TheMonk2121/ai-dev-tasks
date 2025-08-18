<!-- CONTEXT_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_project-overview.md -->
<!-- MODULE_REFERENCE: 000_core/000_backlog.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MEMORY_CONTEXT: HIGH - File organization and cognitive scaffolding system -->
<!-- DATABASE_SYNC: REQUIRED -->

<!-- ANCHOR_KEY: context-priority -->
<!-- ANCHOR_PRIORITY: 30 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

# 🧠 Context Priority Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Guide for prioritizing context and documentation access | Organizing documentation or setting up new systems | Apply
priority system to current documentation |



## TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Guide for prioritizing context and documentation access | Organizing documentation or setting up new systems | Apply
priority system to current documentation |



## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Core documentation system

- **Priority**: 🔥 Critical - Essential for AI context rehydration

- **Points**: 5 - Moderate complexity, high importance

- **Dependencies**: 100_memory/100_cursor-memory-context.md, 000_core/000_backlog.md, 400_guides/400_system-overview.md

- **Next Steps**: Maintain cross-reference accuracy and update as system evolves

## Map of Maps (Top Navigation)

| Topic | File | Anchor | When to read | Why |
|---|---|---|---|---|
| System overview | 400_guides/400_system-overview.md | — | After memory + backlog | Architecture mental model |
| Backlog & priorities | 000_core/000_backlog.md | — | Always for work selection | Current focus and dependencies |
| Testing | 400_guides/400_testing-strategy-guide.md | — | Before writing tests | Strategy, pyramid, quality gates |
| Test development | dspy-rag-system/tests/README-dev.md | — | When writing DSPy tests | Import paths, variable management, F841 |
| Deployment | 400_guides/400_deployment-environment-guide.md | — | Before shipping | Procedures, rollback, monitoring |
| Migration | 400_guides/400_migration-upgrade-guide.md | — | Before/after breaking changes | Pre-checks, validation,
rollback |
| Integration | 400_guides/400_integration-patterns-guide.md | — | Before integrating components | Patterns, data flow,
error handling |
| Performance | 400_guides/400_performance-optimization-guide.md | — | Before/after perf changes | Metrics, tuning,
troubleshooting |
| Security | 400_guides/400_security-best-practices-guide.md | — | Before risky changes | Threat model, validation,
response |
| Setup | 200_setup/202_setup-requirements.md | — | New env or machine | One-stop environment setup |
| Model config | 200_setup/202_setup-requirements.md | — | Model/runtime changes | Clear, reproducible config |
| DSPy context | 100_memory/100_memory/104_dspy-development-context.md | — | Deep implementation | Reasoning, modules,
guard-rails |

## Critical Path

1) `400_guides/400_project-overview.md` → Primary entry point and workflow overview (5-minute overview)
2) `100_memory/100_cursor-memory-context.md` → Primary memory scaffold (30s, 80% context)
3) `000_core/000_backlog.md` → Current priorities and dependencies
4) `400_guides/400_system-overview.md` → Technical architecture and components
5) `400_guides/400_cursor-context-engineering-guide.md` → File relationships and reading order
6) Topic-specific guides based on task:

- Testing → `400_guides/400_testing-strategy-guide.md`
- Test development → `dspy-rag-system/tests/README-dev.md`
- Deployment → `400_guides/400_deployment-environment-guide.md`
- Security → `400_guides/400_security-best-practices-guide.md`
- Performance → `400_guides/400_performance-optimization-guide.md`
- Integration → `400_guides/400_integration-patterns-guide.md`

## 🧠 Hydration Integration

### Role-Based Reading Paths
- **Planner Path**: TL;DR → Backlog → System Overview → Context Priority
- **Implementer Path**: TL;DR → DSPy Context → System Architecture → Context Priority
- **Researcher Path**: TL;DR → Research Index → Context Priority

### Memory Rehydrator Integration
```python
# Planner context
bundle = build_hydration_bundle(
    role="planner",
    task="strategic planning",
    token_budget=1200
)

# Implementer context
bundle = build_hydration_bundle(
    role="implementer",
    task="code implementation",
    token_budget=1200
)
```

### Token Budget Allocation
- **Pinned anchors**: ~400 tokens (stable backbone)
- **Task-scoped content**: ~800 tokens (dynamic retrieval)
- **Total budget**: ~1200 tokens (default)

## **AI File Analysis Strategy** When Cursor AI restarts or needs to rehydrate context, it follows a **structured
reading strategy** designed to maximize efficiency while maintaining comprehensive understanding

### **Primary Go-To Files (Read First - 2-3 minutes)**

1. **`400_guides/400_project-overview.md`** - **CRITICAL**
   - **Primary entry point** for project understanding and workflow
   - Provides 5-minute overview of the entire system
   - Essential for understanding "what this project is and how to use it"

2. **`100_memory/100_cursor-memory-context.md`** - **CRITICAL**
   - **Primary memory scaffold** for instant project state
   - Provides current development focus, recent completions, system architecture
   - Takes 30 seconds to read, provides 80% of needed context
   - Essential for understanding "what's happening right now"

3. **`000_core/000_backlog.md`** - **CRITICAL**
   - Shows current priorities and active development items
   - Reveals development roadmap and blocking dependencies
   - Essential for understanding project direction and next steps
   - Helps identify what's urgent vs. what can wait

4. **`400_guides/400_system-overview.md`** - **CRITICAL**
   - Provides technical architecture and "system-of-systems" context
   - Shows how all components work together
   - Essential for understanding the broader technical landscape
   - Helps with implementation decisions and system integration

### **📋 Crucial Ancillary Files (Read as Needed)**1.**`400_guides/400_cursor-context-engineering-guide.md`**-**IMPORTANT**- When
understanding file organization and relationships

- When finding related files for specific tasks
- When understanding the cognitive scaffolding system
- When navigating the documentation hierarchy

2.**`400_guides/400_project-overview.md`**-**IMPORTANT**- When understanding high-level project purpose

- When needing quick start information or workflow overview
- When understanding the overall development approach
- When onboarding to the project

3.**`200_setup/200_setup/200_setup/200_naming-conventions.md`**-**IMPORTANT**- When understanding file organization
principles

- When suggesting new file names or understanding existing ones
- When understanding the three-digit prefix system
- When maintaining documentation consistency

### **🔧 Script and Code Analysis Strategy**

- *Scripts (Read When Relevant):**-**`scripts/repo_maintenance.py`**- When discussing repository maintenance, file
organization, or automation

- **`scripts/update_cursor_memory.py`**- When discussing memory context updates or automation

- **`dspy-rag-system/`**files - When discussing core AI system, RAG capabilities, or technical implementation**Code
Analysis Pattern:**1.**Start with documentation**to understand system architecture
2.**Read scripts only when**task requires implementation details
3.**Focus on specific script**relevant to current task
4.**Use documentation**to understand what code should do before reading it

### **Reading Pattern Efficiency**

**First 2-3 minutes:**

- Read `400_guides/400_project-overview.md` for project overview and workflow
- Read `100_memory/100_cursor-memory-context.md` for instant context
- Check `000_core/000_backlog.md` for current priorities
- Scan `400_guides/400_system-overview.md` for technical context

**As needed during conversation:**

- Reference `400_guides/400_cursor-context-engineering-guide.md` when discussing file organization
- Check specific scripts when implementation details are needed
- Use `200_setup/200_setup/200_setup/200_naming-conventions.md` when discussing file naming

**For complex tasks:**

- Read relevant workflow files (`000_core/001_create-prd.md`, `000_core/002_generate-tasks.md`,
`000_core/003_process-task-list.md`)
- Check specific domain files based on task type
- Reference completion summaries for historical context

### **Why This Strategy Works**

- *Efficiency**: Three-digit prefix system makes finding right files quick
- *Context Preservation**: Memory context file provides instant project state
- *Scalability**: Can dive deeper into specific areas as needed
- *AI-Friendly**: File organization designed for AI consumption

- *Key Insight**: Don't need to read everything - need to read **right things in right order** for current task.
Cognitive scaffolding system makes this possible by organizing files by priority and purpose.

### Find‑or‑build (code reuse) heuristic

- Before writing new code: run a quick repo search (exclude archives) and check 400_/500_ for existing modules.

- If an existing module covers ≥70% of the need, extend it; otherwise create a new module in the owner component (see
`400_guides/400_system-overview.md`).

- Add a minimal test first and backlink the module in the relevant 400_*guide; if research‑driven, add a line in the
paired 500_*file.

## **Documentation Placement Logic Flow** When determining where to place new documentation content, follow this
**structured decision process** designed to maximize discoverability and coherence

### **Step 1: Assess the Content Type and Scope**

- *Analyze what the content is:**-**System-wide concept**→ High-level documentation (400-499)

- **Process or workflow**→ Workflow documentation (000-099, 100-199)

- **Configuration or setup**→ Setup documentation (200-299)

- **Research or analysis**→ Research documentation (500+)

- **Memory or context**→ Memory documentation (100-199)**Determine the audience:**-**Everyone needs to know**→ Essential
files (000-099, 400-499)

- **Specific workflows need**→ Workflow files (100-199)

- **Setup/configuration needs**→ Setup files (200-299)

- **Historical reference**→ Research files (500+)

### **Step 2: Choose Primary Location Based on Content**

- *For system-wide concepts:**-**`400_guides/400_cursor-context-engineering-guide.md`**- File organization, cognitive scaffolding,
AI analysis strategies

- **`400_guides/400_system-overview.md`**- Technical architecture, system relationships

- **`400_guides/400_project-overview.md`**- High-level project purpose and workflow**For processes and
workflows:**-**`200_setup/200_setup/200_setup/200_naming-conventions.md`**- File naming, generation processes,
conventions

- **`100_memory/100_backlog-guide.md`**- Backlog management processes

- **`000_core/001_create-prd.md`**- PRD creation workflows**For memory and
context:**-**`100_memory/100_cursor-memory-context.md`**- Quick reference summaries

- **`400_guides/400_cursor-context-engineering-guide.md`**- Detailed explanations**For configuration and
setup:**-**`200_setup/202_setup-requirements.md`**- Environment setup and model/runtime changes

### **Step 3: Determine if Multiple Locations Are Needed**

- *Ask these questions:**-**Is this a core concept that affects multiple areas?**→ Multiple locations

- **Is this a specific process for one workflow?**→ Single location

- **Is this a quick reference that should be easily accessible?**→ Memory context + detailed location**Examples of
multi-location content:**-**File naming system**→ `200_setup/200_setup/200_setup/200_naming-conventions.md` (detailed) +
`100_memory/100_cursor-memory-context.md` (quick reference)

- **AI analysis strategy**→ `400_guides/400_cursor-context-engineering-guide.md` (detailed) +
`100_memory/100_cursor-memory-context.md` (quick reference)

- **Documentation strategy**→ `400_guides/400_cursor-context-engineering-guide.md` (detailed) +
`100_memory/100_cursor-memory-context.md` (summary)

### **Step 4: Consider the Reading Pattern**

- *Think about when someone would need this information:**-**Immediate context**→ Memory context file (read first)

- **When working on specific tasks**→ Workflow files (read when relevant)

- **When setting up or configuring**→ Setup files (read when needed)

- **When understanding the system**→ Overview files (read for big picture)**Consider the cognitive scaffolding:**-**High
priority**→ Files read first (000-099, 400-499)

- **Medium priority**→ Files read when relevant (100-199, 200-299)

- **Lower priority**→ Files read when needed (500+)

### **Step 5: Add Cross-References for Discovery**

- *Ensure the content is discoverable:**-**Add cross-references**between related files

- **Update context priority guide**if it's a new concept

- **Consider AI rehydration**- will Cursor AI need this for context?

### **Example Decision Process**

- *Scenario**: Need to document a new file naming system explanation

- *Step 1: Content Analysis**-**Type**: Process/workflow (file naming system)

- **Scope**: System-wide (affects all file creation)

- **Audience**: Everyone creating files

- *Step 2: Primary Location**-**`200_setup/200_setup/200_setup/200_naming-conventions.md`**- Dedicated file for naming
conventions

- **`100_memory/100_cursor-memory-context.md`**- Quick reference for instant access**Step 3: Multi-location Decision**-
✅**Multiple locations needed**- Core concept that affects multiple areas

- **Detailed explanation**in `200_setup/200_setup/200_setup/200_naming-conventions.md`

- **Quick reference**in `100_memory/100_cursor-memory-context.md`**Step 4: Reading Pattern**-**Memory context**- Read
first for instant understanding

- **Naming conventions**- Read when working on file organization**Step 5: Cross-References**-**Cross-reference**between
the two files

- **Update context priority guide**to include the new content**Result**: Add comprehensive explanation to
`200_setup/200_setup/200_setup/200_naming-conventions.md` and quick reference to
`100_memory/100_cursor-memory-context.md` with cross-references.

### **Why This Logic Works**

- *Efficiency**: Content goes where people will naturally look for it
- *Coherence**: Related concepts are grouped together
- *Accessibility**: Quick references are available in memory context
- *Scalability**: System can grow without becoming disorganized
- *AI-Friendly**: Content is discoverable by Cursor AI through cross-references

The key insight is that **good documentation placement follows the natural way people think about and use information**,
while also considering how AI systems like Cursor will consume and navigate the content.

## **Context Sharing Protocol**When sharing context with other AI models, use this structured approach

### **Level 1: Essential Context (5 files)**```text

1. 400_guides/400_project-overview.md - Project overview and workflow
2. 400_guides/400_system-overview.md - Technical architecture
3. 000_core/000_backlog.md - Current priorities and status
4. dspy-rag-system/400_guides/400_project-overview.md - Core system status
5. docs/400_guides/400_project-overview.md - Three-lens documentation guide

```text

### **Level 2: Implementation Context (10 files)**Add these for implementation tasks:

```text

6. 100_memory/100_memory/104_dspy-development-context.md - Deep technical context
7. 200_setup/202_setup-requirements.md - Environment setup
8. 100_memory/100_backlog-automation.md - Automation patterns
9. dspy-rag-system/docs/CURRENT_STATUS.md - Real-time status

```text

### **Level 3: Domain Context (15 files)**Add these for domain-specific tasks:

```text
11-15. Tier 3 files (Core modules & agent logic)
16-20. Tier 4 files (Config & environment)
21-25. Tier 5 files (Domain assets)

```text

## **Cross-Reference System**Use these reference patterns in other documents:

### **In PRDs and Task Lists:**```markdown
<!-- ESSENTIAL_FILES: 400_guides/400_project-overview.md, 400_guides/400_system-overview.md, 000_core/000_backlog.md -->
<!-- IMPLEMENTATION_FILES: 100_memory/100_memory/104_dspy-development-context.md, 200_setup/202_setup-requirements.md -->
<!-- DOMAIN_FILES: 100_memory/100_backlog-guide.md -->

```text

### **In Code Comments:**```python

# CONTEXT: See 400_guides/400_cursor-context-engineering-guide.md for file organization

# ESSENTIAL: 400_guides/400_project-overview.md, 400_guides/400_system-overview.md, 000_core/000_backlog.md

# IMPLEMENTATION: 100_memory/100_memory/104_dspy-development-context.md, 200_setup/202_setup-requirements.md

# DOMAIN: 100_memory/100_backlog-guide.md, CURSOR_NATIVE_AI_STRATEGY.md

```text

## **In Documentation:**```markdown
>**Context Reference**: See `400_guides/400_cursor-context-engineering-guide.md` for complete file organization
> **Essential Files**: `400_guides/400_project-overview.md`, `400_guides/400_system-overview.md`, `000_core/000_backlog.md`
> **Implementation Files**: `100_memory/100_memory/104_dspy-development-context.md`, `200_setup/202_setup-requirements.md`
> **Domain Files**: `100_memory/100_backlog-guide.md`, `CURSOR_NATIVE_AI_STRATEGY.md`

```bash

## Priority Tiers (Macro → Micro)

### **Tier 1: Top-level Architecture & Purpose**
| File | Purpose | Why First? | Cross-Reference |
|------|---------|-------------|-----------------|
| `400_guides/400_project-overview.md` | Project overview, quick start, core flow | **Primary entry point** - establishes purpose and the canonical workflow | `100_memory/100_cursor-memory-context.md` (memory), `400_guides/400_system-overview.md` |
| `100_memory/100_cursor-memory-context.md` | Memory scaffold and current state | Fast rehydration for AIs; routing and safety | `400_guides/400_cursor-context-engineering-guide.md`, `000_core/000_backlog.md` |
| `400_guides/400_system-overview.md` | Architecture, components, workflows | Provides system-of-systems context for implementation | `100_memory/100_memory/104_dspy-development-context.md` |
| `docs/README.md` | Beginner-friendly start and navigation | Bridges newcomers into the core flow quickly | `400_guides/400_project-overview.md`, `100_memory/100_cursor-memory-context.md` |

### **Tier 2: Data-flow & Orchestration Specs**| File | Purpose | Why Critical? | Cross-Reference |
|------|---------|---------------|-----------------|
| `400_guides/400_integration-patterns-guide.md` | Component/API integration patterns | Defines inter-module contracts and error handling | `400_guides/400_system-overview.md`, `100_memory/100_memory/104_dspy-development-context.md` |
| `400_guides/400_deployment-environment-guide.md` | Environments and deployment flow | Ensures repeatable deploys and operational readiness | `200_setup/202_setup-requirements.md`, `400_guides/400_migration-upgrade-guide.md` |
| `400_guides/400_migration-upgrade-guide.md` | Migration safety and rollback | Prevents breakage during upgrades | `400_guides/400_file-analysis-guide.md` |

### **Tier 3: Core Modules & Agent Logic**| File | Purpose | Why Essential? | Cross-Reference |
|------|---------|----------------|-----------------|
| `100_memory/100_memory/104_dspy-development-context.md` | DSPy modules/agents and reasoning | Directly drives implementation quality | `400_guides/400_system-overview.md` |
| `dspy-rag-system/docs/CURRENT_STATUS.md` | Live system capabilities | Ground-truth status for agent decisions | `dspy-rag-system/` code, `400_guides/400_system-overview.md` |

### **Tier 4: Config & Environment**| File | Purpose | Why Important? | Cross-Reference |
|------|---------|----------------|-----------------|
| `200_setup/202_setup-requirements.md` | Environment setup and model/runtime changes | Canonical single source for setup | `400_guides/400_deployment-environment-guide.md` |
| `400_guides/400_performance-optimization-guide.md` | Perf metrics and tuning | Avoids regressions, improves UX | `400_guides/400_system-overview.md` |
| `400_guides/400_security-best-practices-guide.md` | Security model and checklists | Reduces risk and defines guardrails | `400_guides/400_file-analysis-guide.md` |

### **Tier 5: Domain Assets**| File | Purpose | Why Valuable? | Cross-Reference |
|------|---------|---------------|-----------------|
| `100_memory/100_backlog-guide.md` | Backlog usage and scoring | Enables objective prioritization | `000_core/000_backlog.md` |
| `400_guides/400_few-shot-context-examples.md` | Few-shot prompts by task | Boosts quality and consistency | All 400-series topic guides |
| `000_core/001_create-prd.md` (skip rule) | Better PRDs, faster | Improves plan quality before implementation | `000_core/002_generate-tasks.md` |

### **Tier 6: Reference & Edge Cases**| File | Purpose | Why Useful? | Cross-Reference |
|------|---------|-------------|-----------------|
| `400_guides/400_file-analysis-guide.md` | Safe file operations | Mandatory before risky changes | All core docs |
| `400_guides/400_cross-reference-strengthening-plan.md` | Cross-ref policy | Maintains documentation integrity | `scripts/doc_coherence_validator.py` |

## **Essential Context Files for Model Rehydration**

### **1. `400_guides/400_project-overview.md`**
- **Purpose**: Primary entry point and 5-minute mental map of the entire project
- **Key Info**: AI development workflow, quick start, core concepts
- **When to Use**: **First file to read** for any new context

### **2. `100_memory/100_cursor-memory-context.md`**
- **Purpose**: Primary memory scaffold for instant project state
- **Key Info**: Current development focus, recent completions, system architecture
- **When to Use**: Second file to read for instant context rehydration

### **3. `400_guides/400_system-overview.md`**
- **Purpose**: Technical architecture overview
- **Key Info**: System components, security features, reliability measures
- **When to Use**: Understanding the complete technical stack

### **4. `000_core/000_backlog.md`**
- **Purpose**: Current priorities and roadmap
- **Key Info**: Active tasks, completed items, dependencies
- **When to Use**: Understanding what's being built and what's done

### **5. `dspy-rag-system/400_guides/400_project-overview.md`**-**Purpose**: Core system status and features

- **Key Info**: DSPy RAG system capabilities, current features

- **When to Use**: Understanding the main AI system

### **6. `docs/ARCHITECTURE.md`**-**Purpose**: DSPy implementation details

- **Key Info**: Router architecture, modules, chains, agent catalog

- **When to Use**: Deep technical understanding of AI system

### **7. `100_memory/100_memory/104_dspy-development-context.md`**-**Purpose**: Deep technical context

- **Key Info**: Research analysis, current architecture, critical fixes

- **When to Use**: Understanding the AI reasoning system

### **8. `200_setup/202_setup-requirements.md`**-**Purpose**: Environment setup requirements

- **Key Info**: Manual setup items, dependencies, configuration

- **When to Use**: Reproducing or modifying the system

<!-- Removed `201_model-configuration.md` as a standalone source; use `200_setup/202_setup-requirements.md` -->

- **Key Info**: Cursor-native AI setup, model routing at a high level

- **When to Use**: Understanding AI model setup and capabilities

### **9. `100_memory/100_backlog-automation.md`**-**Purpose**: Orchestration patterns

- **Key Info**: AI-BACKLOG-META system, n8n workflows

- **When to Use**: Understanding automated processes

### **10. `dspy-rag-system/docs/CURRENT_STATUS.md`**-**Purpose**: Real-time system state

- **Key Info**: Working features, operational status

- **When to Use**: Understanding current system capabilities

## **Usage Guidelines**###**For Memory Rehydration**1. Start with Tier 1 files (README, SYSTEM_OVERVIEW)
2. Move to Tier 2 for data flow understanding
3. Reference Tier 3 for specific implementation questions
4. Use Tier 4-6 as needed for detailed context

### **For Context Sharing**1. Share the top 10 essential files first
2. Add specific files based on the task at hand
3. Include relevant Tier 5-6 files for domain-specific questions

### **For Problem Solving**1. Check `000_core/000_backlog.md` for current priorities
2. Review relevant Tier 3 files for implementation details
3. Reference Tier 6 files for debugging context
4. Use Tier 4 files for environment setup issues

## **File Categories by Use Case**###**Architecture Understanding**- Tier 1 files

- `docs/ARCHITECTURE.md`

- `100_memory/100_memory/104_dspy-development-context.md`

### **Current Development Status**- `000_core/000_backlog.md`

- `dspy-rag-system/docs/CURRENT_STATUS.md`

- `dspy-rag-system/400_guides/400_project-overview.md`

### **Implementation Details**- Tier 3 files

- `dspy-rag-system/src/` directory

- `tests/` directory

### **Environment Setup**- `200_setup/202_setup-requirements.md`

- (CONFIG_REFERENCE archived; see 202 for config overview)

### **Process Understanding**- `100_memory/100_backlog-automation.md`

- `000_core/001_create-prd.md`

- `000_core/002_generate-tasks.md`

- `000_core/003_process-task-list.md`

## **Memory Scaffolding Integration**###**Cross-Reference Implementation**To integrate this guide with other documents, add these references:

### **In 400_guides/400_project-overview.md:**```markdown
<!-- ESSENTIAL_FILES: 400_guides/400_project-overview.md, 400_guides/400_system-overview.md, 000_core/000_backlog.md -->

```text

#### **In 400_guides/400_system-overview.md:**```markdown
<!-- ARCHITECTURE_FILES: docs/ARCHITECTURE.md, 100_memory/100_memory/104_dspy-development-context.md -->

```text

#### **In 000_core/000_backlog.md:**```markdown
<!-- WORKFLOW_FILES: 000_core/001_create-prd.md, 000_core/002_generate-tasks.md, 000_core/003_process-task-list.md -->

```text

### **AI Model Context Sharing**When sharing context with other AI models, use this structured approach:

#### **Quick Context (5 files):**```text
400_guides/400_cursor-context-engineering-guide.md
400_guides/400_project-overview.md
400_guides/400_system-overview.md
000_core/000_backlog.md
dspy-rag-system/400_guides/400_project-overview.md

```text

#### **Full Context (15 files):**Add these to the quick context:

```text
docs/ARCHITECTURE.md
100_memory/100_memory/104_dspy-development-context.md
200_setup/202_setup-requirements.md
100_memory/100_backlog-automation.md
dspy-rag-system/docs/CURRENT_STATUS.md
000_core/001_create-prd.md
000_core/002_generate-tasks.md
000_core/003_process-task-list.md
100_memory/100_backlog-guide.md

```

#### **Domain-Specific Context (20+ files):**Add relevant Tier 3-6 files based on the specific task or domain

## **Maintenance Notes**-**Last Updated**: 2024-08-06

- **Priority Structure**: Follows "macro → micro" rule

- **Context Efficiency**: Optimized for AI model memory rehydration

- **File Count**: 45 prioritized files across 6 tiers

- **Essential Files**: 10 files provide 80% of context needed

- **Cross-Reference System**: Integrated with all major documents

- **Memory Scaffolding**: Structured for AI model context sharing

This guide ensures that any AI model can quickly understand the complete AI development stack from the highest level
down to implementation details, making it perfect for memory rehydration and context sharing.

<!-- xref-autofix:begin -->
<!-- Cross-references to add: -->
- [🚀 DSPy RAG System - Current Status](dspy-rag-system/docs/CURRENT_STATUS.md)
<!-- xref-autofix:end -->

<!-- README_AUTOFIX_START -->
# Auto-generated sections for 400_context-priority-guide.md
# Generated: 2025-08-17T21:49:49.319914

## Missing sections to add:

## Last Reviewed

2025-08-17

## Owner

[Document owner/maintainer information]

## Purpose

[Describe the purpose and scope of this document]

## Usage

[Describe how to use this document or system]

<!-- README_AUTOFIX_END -->
