# AI Development Stack Context Priority Guide

## Overview
This document provides a prioritized list of files in the `ai-dev-tasks` project, organized by importance from macro to micro view of the AI stack. This guide is designed for:
- **Memory rehydration** for AI assistants
- **Context sharing** with other models
- **Quick onboarding** of new team members
- **Understanding the complete AI development ecosystem**

## 🧠 Memory Scaffolding System

### **Documentation Strategy Evolution & Safeguards**

Our documentation system has evolved from a **manual, ad-hoc approach** to a **structured cognitive scaffolding system** designed specifically for AI rehydration. The key insight was recognizing that documentation serves two distinct purposes: **human comprehension** and **AI context restoration**. Our three-digit prefix system (`100_cursor-memory-context.md`, `400_system-overview.md`, etc.) creates semantic ordering that guides both humans and AI through the correct reading sequence. The HTML cross-reference comments (`<!-- CONTEXT_REFERENCE: --><!-- MODULE_REFERENCE: 101_memory-context-safety.md -->
<!-- MODULE_REFERENCE: 102_memory-context-state.md -->
<!-- MODULE_REFERENCE: 103_memory-context-workflow.md -->
<!-- MODULE_REFERENCE: 104_memory-context-guidance.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide_additional_resources.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide_environment_setup.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples_memory_context_examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide_rollback_procedures.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
<!-- MODULE_REFERENCE: 400_system-overview_system_architecture_macro_view.md -->
<!-- MODULE_REFERENCE: 400_system-overview_development_workflow_high_level_process.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
`) establish explicit relationships between files, creating a web of interconnected knowledge that prevents context fragmentation.

The breakthrough came when we realized that **static documentation** wasn't sufficient for a rapidly evolving AI development ecosystem. We needed **living documentation** that could adapt to changes while maintaining coherence. This led to the development of the memory context system (`100_cursor-memory-context.md`) as the primary AI rehydration mechanism, supported by the context priority guide (`400_context-priority-guide.md`) that maps the entire knowledge hierarchy.

**🛡️ Safeguarding Documentation Moving Forward**

Our safeguard strategy operates on **multiple layers of protection** while maintaining the flexibility needed for solo development. The foundation is **automated validation** - lightweight scripts that check for broken references, stale timestamps, and semantic drift between related documents. These tools use Cursor AI for intelligent semantic checking rather than just pattern matching, ensuring that when the backlog changes, the memory context stays synchronized.

**Recovery mechanisms** are built into the workflow through git snapshots and rollback procedures. Every documentation change creates a restore point, and broken references trigger immediate alerts. The system uses **fenced sections** (`<!-- AUTO-SNIP START -->`) to isolate automated updates from manual content, preventing accidental overwrites while allowing safe automation.

**Cross-reference integrity** is maintained through automated validation that ensures every `<!-- CONTEXT_REFERENCE: -->` points to an existing file, and the context priority guide is auto-generated from file headers rather than manually maintained. This prevents the guide from becoming stale while preserving the human-readable structure.

**⚖️ Balancing Hardness with Elasticity**

The system achieves **solidity through structure** while maintaining **elasticity through automation**. The three-digit prefix system provides a rigid framework that prevents chaos, but the automated tools allow for organic growth without manual overhead. The key is **local-first automation** - scripts that run on your machine without external dependencies, giving you control while providing safety nets.

**Elasticity comes from the AI integration** - Cursor AI can suggest related files to update when changes are made, and the semantic checking can detect when documentation has drifted from reality. The system is **self-healing** through automated validation, but **human-controlled** through dry-run defaults and manual confirmation steps.

**Future-proofing** is built into the architecture through the single source of truth principle - each aspect of the system has one authoritative file, and other documents reference rather than duplicate that information. This prevents drift while allowing the system to evolve. The naming conventions are documented but not rigidly enforced, allowing for organic growth while maintaining the cognitive scaffolding that makes the system work.

The result is a **living documentation system** that's robust enough to prevent critical failures but flexible enough to adapt to your evolving needs as a solo developer. It's designed to scale with your project while maintaining the coherence that makes it valuable to both you and the AI systems that rely on it.

### **AI File Analysis Strategy**

When Cursor AI restarts or needs to rehydrate context, it follows a **structured reading strategy** designed to maximize efficiency while maintaining comprehensive understanding:

#### ** Primary Go-To Files (Read First - 2-3 minutes)**

1. **`100_cursor-memory-context.md`** - **CRITICAL**
   - **Primary memory scaffold** for instant project state
   - Provides current development focus, recent completions, system architecture
   - **NEW**: Contains complete documentation inventory and context-specific guidance
   - Takes 30 seconds to read, provides 80% of needed context
   - Essential for understanding "what's happening right now"

2. **`000_backlog.md`** - **CRITICAL**
   - Shows current priorities and active development items
   - Reveals development roadmap and blocking dependencies
   - Essential for understanding project direction and next steps
   - Helps identify what's urgent vs. what can wait

3. **`400_system-overview.md`** - **CRITICAL**
   - Provides technical architecture and "system-of-systems" context
   - Shows how all components work together
   - Essential for understanding the broader technical landscape
   - Helps with implementation decisions and system integration

4. **`400_development-roadmap.md`** - **CRITICAL**
   - Provides comprehensive development timeline and strategic planning
   - Shows current sprint, next 3 sprints, and quarterly goals
   - Essential for understanding project milestones and progress tracking
   - Helps with strategic planning and resource allocation

#### **📋 Crucial Ancillary Files (Read as Needed)**

4. **`400_context-priority-guide.md`** - **IMPORTANT**
   - When understanding file organization and relationships
   - When finding related files for specific tasks
   - When understanding the cognitive scaffolding system
   - When navigating the documentation hierarchy

5. **`400_project-overview.md`** - **IMPORTANT**
   - When understanding high-level project purpose
   - When needing quick start information or workflow overview
   - When understanding the overall development approach
   - When onboarding to the project

6. **`200_naming-conventions.md`** - **IMPORTANT**
   - When understanding file organization principles
   - When suggesting new file names or understanding existing ones
   - When understanding the three-digit prefix system
   - When maintaining documentation consistency

#### **🔧 Script and Code Analysis Strategy**

**Scripts (Read When Relevant):**
- **`scripts/repo_maintenance.py`** - When discussing repository maintenance, file organization, or automation
- **`scripts/update_cursor_memory.py`** - When discussing memory context updates or automation
- **`dspy-rag-system/`** files - When discussing core AI system, RAG capabilities, or technical implementation

**Code Analysis Pattern:**
1. **Start with documentation** to understand system architecture
2. **Read scripts only when** task requires implementation details
3. **Focus on specific script** relevant to current task
4. **Use documentation** to understand what code should do before reading it

#### ** Reading Pattern Efficiency**

**First 2-3 minutes:**
- Read `100_cursor-memory-context.md` for instant context
- Check `000_backlog.md` for current priorities
- Scan `400_system-overview.md` for technical context

**As needed during conversation:**
- Reference `400_context-priority-guide.md` when discussing file organization
- Check specific scripts when implementation details are needed
- Use `200_naming-conventions.md` when discussing file naming

**For complex tasks:**
- Read relevant workflow files (`001_create-prd.md`, `002_generate-tasks.md`, `003_process-task-list.md`)
- Check specific domain files based on task type
- Reference completion summaries for historical context

#### ** Why This Strategy Works**

**Efficiency**: Three-digit prefix system makes finding right files quick
**Context Preservation**: Memory context file provides instant project state
**Scalability**: Can dive deeper into specific areas as needed
**AI-Friendly**: File organization designed for AI consumption

**Key Insight**: Don't need to read everything - need to read **right things in right order** for current task. Cognitive scaffolding system makes this possible by organizing files by priority and purpose.

### **Documentation Placement Logic Flow**

When determining where to place new documentation content, follow this **structured decision process** designed to maximize discoverability and coherence:

#### ** Step 1: Assess the Content Type and Scope**

**Analyze what the content is:**
- **System-wide concept** → High-level documentation (400-499)
- **Process or workflow** → Workflow documentation (000-099, 100-199)
- **Configuration or setup** → Setup documentation (200-299)
- **Research or analysis** → Research documentation (500+)
- **Memory or context** → Memory documentation (100-199)

**Determine the audience:**
- **Everyone needs to know** → Essential files (000-099, 400-499)
- **Specific workflows need** → Workflow files (100-199)
- **Setup/configuration needs** → Setup files (200-299)
- **Historical reference** → Research files (500+)

#### ** Step 2: Choose Primary Location Based on Content**

**For system-wide concepts:**
- **`400_context-priority-guide.md`** - File organization, cognitive scaffolding, AI analysis strategies
- **`400_system-overview_advanced_features.md`** - Technical architecture, system relationships
- **`400_project-overview.md`** - High-level project purpose and workflow

**For processes and workflows:**
- **`200_naming-conventions.md`** - File naming, generation processes, conventions
- **`100_backlog-guide.md`** - Backlog management processes
- **`001_create-prd.md`** - PRD creation workflows

**For memory and context:**
- **`100_cursor-memory-context.md`** - Quick reference summaries
- **`400_context-priority-guide.md`** - Detailed explanations

**For configuration and setup:**
- **`201_model-configuration.md`** - Model setup processes
- **`202_setup-requirements.md`** - Environment setup

#### ** Step 3: Determine if Multiple Locations Are Needed**

**Ask these questions:**
- **Is this a core concept that affects multiple areas?** → Multiple locations
- **Is this a specific process for one workflow?** → Single location
- **Is this a quick reference that should be easily accessible?** → Memory context + detailed location

**Examples of multi-location content:**
- **File naming system** → `200_naming-conventions.md` (detailed) + `100_cursor-memory-context.md` (quick reference)
- **AI analysis strategy** → `400_context-priority-guide.md` (detailed) + `100_cursor-memory-context.md` (quick reference)
- **Documentation strategy** → `400_context-priority-guide.md` (detailed) + `100_cursor-memory-context.md` (summary)

#### ** Step 4: Consider the Reading Pattern**

**Think about when someone would need this information:**
- **Immediate context** → Memory context file (read first)
- **When working on specific tasks** → Workflow files (read when relevant)
- **When setting up or configuring** → Setup files (read when needed)
- **When understanding the system** → Overview files (read for big picture)

**Consider the cognitive scaffolding:**
- **High priority** → Files read first (000-099, 400-499)
- **Medium priority** → Files read when relevant (100-199, 200-299)
- **Lower priority** → Files read when needed (500+)

#### ** Step 5: Add Cross-References for Discovery**

**Ensure the content is discoverable:**
- **Add cross-references** between related files
- **Update context priority guide** if it's a new concept
- **Consider AI rehydration** - will Cursor AI need this for context?

#### ** Example Decision Process**

**Scenario**: Need to document a new file naming system explanation

**Step 1: Content Analysis**
- **Type**: Process/workflow (file naming system)
- **Scope**: System-wide (affects all file creation)
- **Audience**: Everyone creating files

**Step 2: Primary Location**
- **`200_naming-conventions.md`** - Dedicated file for naming conventions
- **`100_cursor-memory-context.md`** - Quick reference for instant access

**Step 3: Multi-location Decision**
- ✅ **Multiple locations needed** - Core concept that affects multiple areas
- **Detailed explanation** in `200_naming-conventions.md`
- **Quick reference** in `100_cursor-memory-context.md`

**Step 4: Reading Pattern**
- **Memory context** - Read first for instant understanding
- **Naming conventions** - Read when working on file organization

**Step 5: Cross-References**
- **Cross-reference** between the two files
- **Update context priority guide** to include the new content

**Result**: Add comprehensive explanation to `200_naming-conventions.md` and quick reference to `100_cursor-memory-context.md` with cross-references.

#### ** Why This Logic Works**

**Efficiency**: Content goes where people will naturally look for it
**Coherence**: Related concepts are grouped together
**Accessibility**: Quick references are available in memory context
**Scalability**: System can grow without becoming disorganized
**AI-Friendly**: Content is discoverable by Cursor AI through cross-references

The key insight is that **good documentation placement follows the natural way people think about and use information**, while also considering how AI systems like Cursor will consume and navigate the content.

### **Context Sharing Protocol**
When sharing context with other AI models, use this structured approach:

#### **Level 1: Essential Context (5 files)**
```
1. 400_project-overview.md - Project overview and workflow
2. 400_system-overview_advanced_features.md - Technical architecture
3. 000_backlog.md - Current priorities and status
4. dspy-rag-system/400_project-overview.md - Core system status
5. docs/400_project-overview.md - Three-lens documentation guide
```

#### **Level 2: Implementation Context (10 files)**
Add these for implementation tasks:
```
6. 104_dspy-development-context.md - Deep technical context
7. 202_setup-requirements.md - Environment setup
8. 201_model-configuration.md - AI model configuration
9. 100_backlog-automation.md - Automation patterns
10. dspy-rag-system/docs/CURRENT_STATUS.md - Real-time status
```

#### **Level 3: Domain Context (15 files)**
Add these for domain-specific tasks:
```
11-15. Tier 3 files (Core modules & agent logic)
16-20. Tier 4 files (Config & environment)
21-25. Tier 5 files (Domain assets)
```

### **Cross-Reference System**
Use these reference patterns in other documents:

#### **In PRDs and Task Lists:**
```markdown
<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- ESSENTIAL_FILES: 400_project-overview.md, 400_system-overview_advanced_features.md, 000_backlog.md -->
<!-- IMPLEMENTATION_FILES: 104_dspy-development-context.md, 202_setup-requirements.md -->
<!-- DOMAIN_FILES: 100_backlog-guide.md, 103_yi-coder-integration.md -->
```

#### **In Code Comments:**
```python
# CONTEXT: See 400_context-priority-guide.md for file organization
# ESSENTIAL: 400_project-overview.md, 400_system-overview_advanced_features.md, 000_backlog.md
# IMPLEMENTATION: 104_dspy-development-context.md, 202_setup-requirements.md
# DOMAIN: 100_backlog-guide.md, CURSOR_NATIVE_AI_STRATEGY.md
```

#### **In Documentation:**
```markdown
> **Context Reference**: See `400_context-priority-guide.md` for complete file organization
> **Essential Files**: `400_project-overview.md`, `400_system-overview_advanced_features.md`, `000_backlog.md`
> **Implementation Files**: `104_dspy-development-context.md`, `202_setup-requirements.md`
> **Domain Files**: `100_backlog-guide.md`, `CURSOR_NATIVE_AI_STRATEGY.md`
```

## Priority Tiers (Macro → Micro)

### **Tier 1: Top-level Architecture & Purpose**
*Files that give a 5-second mental map of the whole stack*

| File | Purpose | Why First? | Cross-Reference |
|------|---------|-------------|-----------------|
| `400_project-overview.md` | Main project entry point with high-level overview, quick start, and core AI development workflow | Gives immediate understanding of the project's purpose and workflow | `<!-- CONTEXT_REFERENCE: 400_project-overview.md -->` |
| `400_system-overview_advanced_features.md` | Comprehensive technical overview of the entire AI development ecosystem | Provides the "system-of-systems" context | `<!-- CONTEXT_REFERENCE: 400_system-overview_advanced_features.md -->` |
| `dspy-rag-system/400_project-overview.md` | DSPy RAG system overview with current status and features | Shows the core AI system's capabilities | `<!-- CONTEXT_REFERENCE: dspy-rag-system/400_project-overview.md -->` |
| `dspy-rag-system/docs/CURRENT_STATUS.md` | Real-time status of all system components and features | Current operational state of the entire stack | `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/CURRENT_STATUS.md -->` |

### **Tier 2: Data-flow & Orchestration Specs**
*Files showing how components talk to each other*

| File | Purpose | Why Critical? | Cross-Reference |
|------|---------|---------------|-----------------|
| `000_backlog.md` | Central product backlog with prioritization, dependencies, and roadmap | Shows the project's direction and current priorities | `<!-- CONTEXT_REFERENCE: 000_backlog.md -->` |
| `400_development-roadmap.md` | Comprehensive development roadmap with timelines, milestones, and strategic planning | Provides strategic planning context and progress tracking | `<!-- CONTEXT_REFERENCE: 400_development-roadmap.md -->` |
| `100_backlog-automation.md` | AI-BACKLOG-META system and n8n workflow orchestration | Demonstrates automated project management | `<!-- CONTEXT_REFERENCE: 100_backlog-automation.md -->` |
| `001_create-prd.md` | Process for creating Product Requirement Documents | Defines scope → implementation flow | `<!-- CONTEXT_REFERENCE: 001_create-prd.md -->` |
| `002_generate-tasks.md` | Rules for breaking PRDs into executable task lists | Shows how high-level requirements become actionable | `<!-- CONTEXT_REFERENCE: 002_generate-tasks.md -->` |
| `003_process-task-list.md` | AI agent execution loop, state management, and error recovery | Core orchestration of AI-driven development | `<!-- CONTEXT_REFERENCE: 003_process-task-list.md -->` |
| `400_metadata-collection-guide.md` | Metadata collection system, analytics, and data-driven decision making | Comprehensive data collection and usage patterns | `<!-- CONTEXT_REFERENCE: 400_metadata-collection-guide.md -->` |
| `400_file-analysis-guide.md` | Systematic file analysis methodology for legacy detection and obsolescence assessment | Comprehensive analysis process for maintaining documentation integrity | `<!-- CONTEXT_REFERENCE: 400_file-analysis-guide.md -->` |
| `500_research-infrastructure-guide.md` | Research infrastructure for LLM-accessible knowledge management | Academic papers, articles, tutorials, and case studies | `<!-- CONTEXT_REFERENCE: 500_research-infrastructure-guide.md -->` |
| `500_research-summary.md` | Central research summary for AI development ecosystem | Research findings and implementation guidance | `<!-- CONTEXT_REFERENCE: 500_research-summary.md -->` |
| `500_dspy-research.md` | DSPy framework research and implementation guidance | DSPy patterns, best practices, and integration | `<!-- CONTEXT_REFERENCE: 500_dspy-research.md -->` |
| `dspy-rag-system/src/dashboard.py` | Main dashboard orchestration and API endpoints | Central coordination point | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/dashboard.py -->` |
| `dspy-rag-system/src/mission_dashboard/mission_dashboard.py` | Real-time mission tracking orchestration | Live AI task monitoring | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/mission_dashboard/mission_dashboard.py -->` |
| `dspy-rag-system/src/n8n_workflows/backlog_webhook.py` | n8n integration webhook server | External system integration | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/n8n_workflows/backlog_webhook.py -->` |

### **Tier 3: Core Modules & Agent Logic**
*Files explaining the brains of the operation*

| File | Purpose | Why Essential? | Cross-Reference |
|------|---------|----------------|-----------------|
| `104_dspy-development-context.md` | Deep research analysis of DSPy implementation | Explains the AI reasoning system | `<!-- CONTEXT_REFERENCE: 104_dspy-development-context.md -->` |
| `docs/ARCHITECTURE.md` | DSPy Router architecture (v0.3.1) with signatures, modules, chains | Core AI system architecture | `<!-- CONTEXT_REFERENCE: docs/ARCHITECTURE.md -->` |
| `dspy-rag-system/src/dspy_modules/` | Core DSPy agent implementations | The actual AI agents | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/dspy_modules/ -->` |
| `dspy-rag-system/src/mission_dashboard/mission_tracker.py` | Mission tracking core logic | AI task lifecycle management | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/mission_dashboard/mission_tracker.py -->` |
| `dspy-rag-system/src/monitoring/production_monitor.py` | Production monitoring core | System observability | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/monitoring/production_monitor.py -->` |
| `dspy-rag-system/src/monitoring/health_endpoints.py` | Health check and readiness logic | System reliability | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/monitoring/health_endpoints.py -->` |
| `dspy-rag-system/src/n8n_workflows/backlog_scrubber.py` | Backlog scoring and automation logic | Automated prioritization | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/n8n_workflows/backlog_scrubber.py -->` |
| `dspy-rag-system/src/watch_folder.py` | Document processing and RAG pipeline | Core RAG functionality | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/watch_folder.py -->` |

### **Tier 4: Config & Environment**
*Files for reproducing or mutating the system*

| File | Purpose | Why Important? | Cross-Reference |
|------|---------|----------------|-----------------|
| `202_setup-requirements.md` | Manual setup items (n8n, PostgreSQL, Ollama, LM Studio) | Environment reproduction | `<!-- CONTEXT_REFERENCE: 202_setup-requirements.md -->` |
| `201_model-configuration.md` | AI model configuration (Mistral, Yi-Coder) | AI model setup | `<!-- CONTEXT_REFERENCE: 201_model-configuration.md -->` |
| `docs/CONFIG_REFERENCE.md` | Comprehensive configuration reference | System configuration | `<!-- CONTEXT_REFERENCE: docs/CONFIG_REFERENCE.md -->` |
| `dspy-rag-system/requirements.txt` | Python dependencies | Dependency management | `<!-- CONTEXT_REFERENCE: dspy-rag-system/requirements.txt -->` |
| `dspy-rag-system/start_mission_dashboard.sh` | Dashboard startup script | System startup | `<!-- CONTEXT_REFERENCE: dspy-rag-system/start_mission_dashboard.sh -->` |
| `dspy-rag-system/quick_start.sh` | Quick start script | Rapid deployment | `<!-- CONTEXT_REFERENCE: dspy-rag-system/quick_start.sh -->` |
| `.gitignore` | Version control exclusions | Repository management | `<!-- CONTEXT_REFERENCE: .gitignore -->` |
| `.markdownlint.jsonc` | Documentation formatting rules | Code quality | `<!-- CONTEXT_REFERENCE: .markdownlint.jsonc -->` |

### **Tier 5: Domain Assets**
*Files needed for high-quality generation after architecture is understood*

| File | Purpose | Why Valuable? | Cross-Reference |
|------|---------|---------------|-----------------|
| `100_backlog-guide.md` | Backlog system usage guide and prioritization rules | Domain knowledge | `<!-- CONTEXT_REFERENCE: 100_backlog-guide.md -->` |
| `103_yi-coder-integration.md` | Yi-Coder integration with Cursor IDE | Tool integration | `<!-- CONTEXT_REFERENCE: 103_yi-coder-integration.md -->` |
| `TIMESTAMP_UPDATE_GUIDE.md` | Timestamp update rules and process | Process knowledge | `<!-- CONTEXT_REFERENCE: TIMESTAMP_UPDATE_GUIDE.md -->` |
| `200_naming-conventions.md` | File naming conventions | Organization standards | `<!-- CONTEXT_REFERENCE: 200_naming-conventions.md -->` |
| `dspy-rag-system/docs/MISSION_DASHBOARD_GUIDE.md` | Mission dashboard usage guide | Feature documentation | `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/MISSION_DASHBOARD_GUIDE.md -->` |
| `dspy-rag-system/docs/N8N_BACKLOG_SCRUBBER_GUIDE.md` | n8n integration guide | Integration documentation | `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/N8N_BACKLOG_SCRUBBER_GUIDE.md -->` |
| `dspy-rag-system/docs/DSPY_INTEGRATION_GUIDE.md` | DSPy integration guide | Core system documentation | `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/DSPY_INTEGRATION_GUIDE.md -->` |
| `dspy-rag-system/src/mission_dashboard/templates/mission_dashboard.html` | Dashboard UI template | User interface | `<!-- CONTEXT_REFERENCE: dspy-rag-system/src/mission_dashboard/templates/mission_dashboard.html -->` |

### **Tier 6: Reference & Edge Cases**
*Files valuable for fine-tuning or debugging*

| File | Purpose | Why Useful? | Cross-Reference |
|------|---------|-------------|-----------------|
| `C9_COMPLETION_SUMMARY.md` | B-003 completion reference | Historical context | `<!-- CONTEXT_REFERENCE: C9_COMPLETION_SUMMARY.md -->` |
| `C10_COMPLETION_SUMMARY.md` | B-010 completion reference | Historical context | `<!-- CONTEXT_REFERENCE: C10_COMPLETION_SUMMARY.md -->` |
| `dspy-rag-system/demo_mission_dashboard.py` | Mission dashboard demonstration | Feature examples | `<!-- CONTEXT_REFERENCE: dspy-rag-system/demo_mission_dashboard.py -->` |
| `dspy-rag-system/demo_backlog_scrubber.py` | Backlog scrubber demonstration | Feature examples | `<!-- CONTEXT_REFERENCE: dspy-rag-system/demo_backlog_scrubber.py -->` |
| `dspy-rag-system/demo_production_monitoring.py` | Production monitoring demonstration | Feature examples | `<!-- CONTEXT_REFERENCE: dspy-rag-system/demo_production_monitoring.py -->` |
| `dspy-rag-system/demo_database_resilience.py` | Database resilience demonstration | Feature examples | `<!-- CONTEXT_REFERENCE: dspy-rag-system/demo_database_resilience.py -->` |
| `dspy-rag-system/tests/` | Test suites for all components | Quality assurance | `<!-- CONTEXT_REFERENCE: dspy-rag-system/tests/ -->` |
| `dspy-rag-system/watch_folder.log` | System logs | Debugging | `<!-- CONTEXT_REFERENCE: dspy-rag-system/watch_folder.log -->` |
| `dspy-rag-system/watch_folder_error.log` | Error logs | Debugging | `<!-- CONTEXT_REFERENCE: dspy-rag-system/watch_folder_error.log -->` |

## **Essential Context Files for Model Rehydration**

When rehydrating an AI model's memory or sharing context with other models, start with these **top 10 files** for maximum context efficiency:

### **1. `400_project-overview.md`** 
- **Purpose**: 5-second mental map of the entire project
- **Key Info**: AI development workflow, quick start, core concepts
- **When to Use**: First file to read for any new context
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 400_project-overview.md -->`

### **2. `400_system-overview_advanced_features.md`**
- **Purpose**: Technical architecture overview
- **Key Info**: System components, security features, reliability measures
- **When to Use**: Understanding the complete technical stack
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 400_system-overview_advanced_features.md -->`

### **3. `000_backlog.md`**
- **Purpose**: Current priorities and roadmap
- **Key Info**: Active tasks, completed items, dependencies
- **When to Use**: Understanding what's being built and what's done
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 000_backlog.md -->`

### **4. `dspy-rag-system/400_project-overview.md`**
- **Purpose**: Core system status and features
- **Key Info**: DSPy RAG system capabilities, current features
- **When to Use**: Understanding the main AI system
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: dspy-rag-system/400_project-overview.md -->`

### **5. `docs/ARCHITECTURE.md`**
- **Purpose**: DSPy implementation details
- **Key Info**: Router architecture, modules, chains, agent catalog
- **When to Use**: Deep technical understanding of AI system
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: docs/ARCHITECTURE.md -->`

### **6. `104_dspy-development-context.md`**
- **Purpose**: Deep technical context
- **Key Info**: Research analysis, current architecture, critical fixes
- **When to Use**: Understanding the AI reasoning system
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 104_dspy-development-context.md -->`

### **7. `202_setup-requirements.md`**
- **Purpose**: Environment setup requirements
- **Key Info**: Manual setup items, dependencies, configuration
- **When to Use**: Reproducing or modifying the system
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 202_setup-requirements.md -->`

### **8. `201_model-configuration.md`**
- **Purpose**: AI model configuration
- **Key Info**: Mistral, Yi-Coder setup, model parameters
- **When to Use**: Understanding AI model setup and capabilities
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 201_model-configuration.md -->`

### **9. `100_backlog-automation.md`**
- **Purpose**: Orchestration patterns
- **Key Info**: AI-BACKLOG-META system, n8n workflows
- **When to Use**: Understanding automated processes
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: 100_backlog-automation.md -->`

### **10. `dspy-rag-system/docs/CURRENT_STATUS.md`**
- **Purpose**: Real-time system state
- **Key Info**: Working features, operational status
- **When to Use**: Understanding current system capabilities
- **Cross-Reference**: `<!-- CONTEXT_REFERENCE: dspy-rag-system/docs/CURRENT_STATUS.md -->`

## **Usage Guidelines**

### **For Memory Rehydration**
1. Start with Tier 1 files (README, SYSTEM_OVERVIEW)
2. Move to Tier 2 for data flow understanding
3. Reference Tier 3 for specific implementation questions
4. Use Tier 4-6 as needed for detailed context

### **For Context Sharing**
1. Share the top 10 essential files first
2. Add specific files based on the task at hand
3. Include relevant Tier 5-6 files for domain-specific questions

### **For Problem Solving**
1. Check `000_backlog.md` for current priorities
2. Review relevant Tier 3 files for implementation details
3. Reference Tier 6 files for debugging context
4. Use Tier 4 files for environment setup issues

## **File Categories by Use Case**

### **Architecture Understanding**
- Tier 1 files
- `docs/ARCHITECTURE.md`
- `104_dspy-development-context.md`

### **Current Development Status**
- `000_backlog.md`
- `dspy-rag-system/docs/CURRENT_STATUS.md`
- `dspy-rag-system/400_project-overview.md`

### **Implementation Details**
- Tier 3 files
- `dspy-rag-system/src/` directory
- `tests/` directory

### **Environment Setup**
- `202_setup-requirements.md`
- `201_model-configuration.md`
- `docs/CONFIG_REFERENCE.md`

### **Process Understanding**
- `100_backlog-automation.md`
- `001_create-prd.md`
- `002_generate-tasks.md`
- `003_process-task-list.md`
- `400_prd-optimization-guide.md`

## **Memory Scaffolding Integration**

### **Cross-Reference Implementation**
To integrate this guide with other documents, add these references:

#### **In 400_project-overview.md:**
```markdown
<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- ESSENTIAL_FILES: 400_project-overview.md, 400_system-overview_advanced_features.md, 000_backlog.md -->
```

#### **In 400_system-overview_advanced_features.md:**
```markdown
<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- ARCHITECTURE_FILES: docs/ARCHITECTURE.md, 104_dspy-development-context.md -->
```

#### **In 000_backlog.md:**
```markdown
<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- WORKFLOW_FILES: 001_create-prd.md, 002_generate-tasks.md, 003_process-task-list.md -->
```

### **AI Model Context Sharing**
When sharing context with other AI models, use this structured approach:

#### **Quick Context (5 files):**
```
400_context-priority-guide.md
400_project-overview.md
400_system-overview_advanced_features.md
000_backlog.md
dspy-rag-system/400_project-overview.md
```

#### **Full Context (15 files):**
Add these to the quick context:
```
docs/ARCHITECTURE.md
104_dspy-development-context.md
202_setup-requirements.md
201_model-configuration.md
100_backlog-automation.md
dspy-rag-system/docs/CURRENT_STATUS.md
001_create-prd.md
002_generate-tasks.md
003_process-task-list.md
100_backlog-guide.md
```

#### **Domain-Specific Context (20+ files):**
Add relevant Tier 3-6 files based on the specific task or domain.

## **Maintenance Notes**

- **Last Updated**: 2024-08-06
- **Priority Structure**: Follows "macro → micro" rule
- **Context Efficiency**: Optimized for AI model memory rehydration
- **File Count**: 45 prioritized files across 6 tiers
- **Essential Files**: 10 files provide 80% of context needed
- **Cross-Reference System**: Integrated with all major documents
- **Memory Scaffolding**: Structured for AI model context sharing

This guide ensures that any AI model can quickly understand the complete AI development stack from the highest level down to implementation details, making it perfect for memory rehydration and context sharing. 