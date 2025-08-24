

<!-- ANCHOR_KEY: context-priority -->
<!-- ANCHOR_PRIORITY: 30 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

# 🧠 Context Priority Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Auto-generated guide for prioritizing context and documentation access | Organizing documentation or setting up new systems | Apply priority system to current documentation |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Auto-generated documentation system
- **Priority**: 🔥 Critical - Essential for AI context rehydration
- **Points**: 5 - Moderate complexity, high importance
- **Dependencies**: 100_memory/100_memory/100_cursor-memory-context.md, 000_core/000_core/000_backlog.md, 400_guides/400_system-overview.md
- **Next Steps**: Maintain cross-reference accuracy and update as system evolves
## 🧠 Memory Scaffolding System

### **Documentation Strategy Evolution & Safeguards**

Our documentation system has evolved from a **manual, ad-hoc approach** to a **structured cognitive scaffolding system** designed specifically for AI rehydration. The key insight was recognizing that documentation serves two distinct purposes: **human comprehension** and **AI context restoration**. Our three-digit prefix system (`100_memory/100_cursor-memory-context.md`, `400_system-overview.md`, etc.) creates semantic ordering that guides both humans and AI through the correct reading sequence. The HTML cross-reference comments (`<!-- CONTEXT_REFERENCE: -->`) establish explicit relationships between files, creating a web of interconnected knowledge that prevents context fragmentation.

The breakthrough came when we realized that **static documentation** wasn't sufficient for a rapidly evolving AI development ecosystem. We needed **living documentation** that could adapt to changes while maintaining coherence. This led to the development of the memory context system (`100_memory/100_cursor-memory-context.md`) as the primary AI rehydration mechanism, supported by the context priority guide (`400_guides/400_context-priority-guide.md`) that maps the entire knowledge hierarchy.

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

1. **`100_memory/100_cursor-memory-context.md`** - **CRITICAL**
   - **Primary memory scaffold** for instant project state
   - Provides current development focus, recent completions, system architecture
   - Takes 30 seconds to read, provides 80% of needed context
   - Essential for understanding "what's happening right now"

2. **`000_core/000_backlog.md`** - **CRITICAL**
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

4. **`400_guides/400_context-priority-guide.md`** - **IMPORTANT**
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
- Read `100_memory/100_cursor-memory-context.md` for instant context
- Check `000_core/000_backlog.md` for current priorities
- Scan `400_system-overview.md` for technical context

**As needed during conversation:**
- Reference `400_guides/400_context-priority-guide.md` when discussing file organization
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
- **`400_guides/400_context-priority-guide.md`** - File organization, cognitive scaffolding, AI analysis strategies
- **`400_system-overview.md`** - Technical architecture, system relationships
- **`400_project-overview.md`** - High-level project purpose and workflow

**For processes and workflows:**
- **`200_naming-conventions.md`** - File naming, generation processes, conventions
- **`100_backlog-guide.md`** - Backlog management processes
- **`001_create-prd.md`** - PRD creation workflows

**For memory and context:**
- **`100_memory/100_cursor-memory-context.md`** - Quick reference summaries
- **`400_guides/400_context-priority-guide.md`** - Detailed explanations

**For configuration and setup:**
- **`201_model-configuration.md`** - Model setup processes
- **`202_setup-requirements.md`** - Environment setup

#### ** Step 3: Determine if Multiple Locations Are Needed**

**Ask these questions:**
- **Is this a core concept that affects multiple areas?** → Multiple locations
- **Is this a specific process for one workflow?** → Single location
- **Is this a quick reference that should be easily accessible?** → Memory context + detailed location

**Examples of multi-location content:**
- **File naming system** → `200_naming-conventions.md` (detailed) + `100_memory/100_cursor-memory-context.md` (quick reference)
- **AI analysis strategy** → `400_guides/400_context-priority-guide.md` (detailed) + `100_memory/100_cursor-memory-context.md` (quick reference)
- **Documentation strategy** → `400_guides/400_context-priority-guide.md` (detailed) + `100_memory/100_cursor-memory-context.md` (summary)

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
- **`100_memory/100_cursor-memory-context.md`** - Quick reference for instant access

**Step 3: Multi-location Decision**
- ✅ **Multiple locations needed** - Core concept that affects multiple areas
- **Detailed explanation** in `200_naming-conventions.md`
- **Quick reference** in `100_memory/100_cursor-memory-context.md`

**Step 4: Reading Pattern**
- **Memory context** - Read first for instant understanding
- **Naming conventions** - Read when working on file organization

**Step 5: Cross-References**
- **Cross-reference** between the two files
- **Update context priority guide** to include the new content

**Result**: Add comprehensive explanation to `200_naming-conventions.md` and quick reference to `100_memory/100_cursor-memory-context.md` with cross-references.

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
2. 400_system-overview.md - Technical architecture
3. 000_core/000_backlog.md - Current priorities and status
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
<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- ESSENTIAL_FILES: 400_project-overview.md, 400_system-overview.md, 000_core/000_backlog.md -->
<!-- IMPLEMENTATION_FILES: 104_dspy-development-context.md, 202_setup-requirements.md -->
<!-- DOMAIN_FILES: 100_backlog-guide.md, 103_yi-coder-integration.md -->
```

#### **In Code Comments:**
```python
# CONTEXT: See 400_guides/400_context-priority-guide.md for file organization
# ESSENTIAL: 400_project-overview.md, 400_system-overview.md, 000_core/000_backlog.md
# IMPLEMENTATION: 104_dspy-development-context.md, 202_setup-requirements.md
# DOMAIN: 100_backlog-guide.md, CURSOR_NATIVE_AI_STRATEGY.md
```

#### **In Documentation:**
```markdown
> **Context Reference**: See `400_guides/400_context-priority-guide.md` for complete file organization
> **Essential Files**: `400_project-overview.md`, `400_system-overview.md`, `000_core/000_backlog.md`
> **Implementation Files**: `104_dspy-development-context.md`, `202_setup-requirements.md`
> **Domain Files**: `100_backlog-guide.md`, `CURSOR_NATIVE_AI_STRATEGY.md`
```

## Priority Tiers (Macro → Micro)
- **Last Generated**: 2025-08-21 19:08:36

## 📋 Priority-Based Organization

### P0 (Critical)

| File | Anchor | Priority | Roles | Context Reference |
|------|--------|----------|-------|-------------------|
| 100_memory/100_memory/100_cursor-memory-context.md | tldr | 0 | planner, implementer, researcher, coder | — |
| 100_memory/104_dspy-development-context.md | tldr | 0 | implementer, coder | — |
| 500_research/500_superwhisper-integration-research.md | tldr | 0 | researcher, planner | — |
| 600_archives/documentation-duplicates/100_memory/100_cursor-memory-context.md | tldr | 0 | planner, implementer, researcher | — |
| 600_archives/documentation-duplicates/104_dspy-development-context.md | tldr | 0 | implementer | — |

### P1 (High)

| File | Anchor | Priority | Roles | Context Reference |
|------|--------|----------|-------|-------------------|
| 000_core/000_core/000_backlog.md | backlog | 10 | planner | — |
| 100_memory/105_cspell-automation-memory.md | tldr | 10 | coder | — |
| 600_archives/documentation-duplicates/000_core/000_backlog.md | backlog | 10 | planner | — |

### P2 (Medium)

| File | Anchor | Priority | Roles | Context Reference |
|------|--------|----------|-------|-------------------|
| 400_guides/400_graph-visualization-guide.md | tldr | 12 | planner, implementer, coder | — |
| 400_guides/400_system-overview.md | tldr | 15 | planner, implementer | — |
| 600_archives/documentation-duplicates/400_system-overview.md | tldr | 15 | planner, implementer | — |
| 400_guides/400_observability-system.md | tldr | 20 | implementer, planner, researcher | — |
| 400_guides/400_lean-hybrid-memory-system.md | tldr | 25 | implementer, planner | — |
| 400_guides/400_scribe-v2-system-guide.md | tldr | 30 | implementer, planner, coder | — |
| 400_guides/demo_complete_dspy_v2_system.py | tldr | 35 | implementer, coder | — |
| 400_guides/demo_assertion_framework.py | tldr | 35 | implementer, coder | — |
| 400_guides/demo_four_part_optimization_loop.py | tldr | 35 | implementer, coder | — |
| 400_guides/demo_labeled_few_shot_optimizer.py | tldr | 35 | implementer, coder | — |

## 🎭 Role-Based Organization

### Coder Role

| File | Anchor | Priority | Context Reference |
|------|--------|----------|-------------------|
| 100_memory/105_cspell-automation-memory.md | tldr | 10 | — |
| 400_guides/400_graph-visualization-guide.md | tldr | 12 | — |
| 400_guides/400_scribe-v2-system-guide.md | tldr | 30 | — |
| 400_guides/demo_complete_dspy_v2_system.py | tldr | 35 | — |
| 400_guides/demo_assertion_framework.py | tldr | 35 | — |
| 400_guides/demo_four_part_optimization_loop.py | tldr | 35 | — |
| 400_guides/demo_labeled_few_shot_optimizer.py | tldr | 35 | — |
| 100_memory/100_memory/100_cursor-memory-context.md | tldr | 0 | — |
| 100_memory/104_dspy-development-context.md | tldr | 0 | — |

### Implementer Role

| File | Anchor | Priority | Context Reference |
|------|--------|----------|-------------------|
| 400_guides/400_graph-visualization-guide.md | tldr | 12 | — |
| 400_guides/400_system-overview.md | tldr | 15 | — |
| 600_archives/documentation-duplicates/400_system-overview.md | tldr | 15 | — |
| 400_guides/400_observability-system.md | tldr | 20 | — |
| 400_guides/400_lean-hybrid-memory-system.md | tldr | 25 | — |
| 400_guides/400_scribe-v2-system-guide.md | tldr | 30 | — |
| 400_guides/demo_complete_dspy_v2_system.py | tldr | 35 | — |
| 400_guides/demo_assertion_framework.py | tldr | 35 | — |
| 400_guides/demo_four_part_optimization_loop.py | tldr | 35 | — |
| 400_guides/demo_labeled_few_shot_optimizer.py | tldr | 35 | — |
| 100_memory/100_memory/100_cursor-memory-context.md | tldr | 0 | — |
| 100_memory/104_dspy-development-context.md | tldr | 0 | — |
| 600_archives/documentation-duplicates/100_memory/100_cursor-memory-context.md | tldr | 0 | — |
| 600_archives/documentation-duplicates/104_dspy-development-context.md | tldr | 0 | — |

### Planner Role

| File | Anchor | Priority | Context Reference |
|------|--------|----------|-------------------|
| 000_core/000_core/000_backlog.md | backlog | 10 | — |
| 600_archives/documentation-duplicates/000_core/000_backlog.md | backlog | 10 | — |
| 400_guides/400_graph-visualization-guide.md | tldr | 12 | — |
| 400_guides/400_system-overview.md | tldr | 15 | — |
| 600_archives/documentation-duplicates/400_system-overview.md | tldr | 15 | — |
| 400_guides/400_observability-system.md | tldr | 20 | — |
| 400_guides/400_lean-hybrid-memory-system.md | tldr | 25 | — |
| 400_guides/400_scribe-v2-system-guide.md | tldr | 30 | — |
| 100_memory/100_memory/100_cursor-memory-context.md | tldr | 0 | — |
| 500_research/500_superwhisper-integration-research.md | tldr | 0 | — |
| 600_archives/documentation-duplicates/100_memory/100_cursor-memory-context.md | tldr | 0 | — |

### Researcher Role

| File | Anchor | Priority | Context Reference |
|------|--------|----------|-------------------|
| 400_guides/400_observability-system.md | tldr | 20 | — |
| 100_memory/100_memory/100_cursor-memory-context.md | tldr | 0 | — |
| 500_research/500_superwhisper-integration-research.md | tldr | 0 | — |
| 600_archives/documentation-duplicates/100_memory/100_cursor-memory-context.md | tldr | 0 | — |

## 🚀 Critical Path

1. **Memory Context**: `100_memory/100_memory/100_cursor-memory-context.md` - Primary memory scaffold
2. **Backlog**: `000_core/000_core/000_backlog.md` - Current priorities and dependencies
3. **System Overview**: `400_guides/400_system-overview.md` - Technical architecture
4. **Project Overview**: `400_guides/400_project-overview.md` - High-level project structure
5. **Context Priority**: `400_guides/400_guides/400_context-priority-guide.md` - This file (reading order)

## 🔗 Quick Navigation

| Topic | File | Anchor | When to read |
|-------|------|--------|--------------|
| System overview | 400_guides/400_system-overview.md | system-overview | After memory + backlog |
| Backlog & priorities | 000_core/000_core/000_backlog.md | backlog | Always for work selection |
| Memory context | 100_memory/100_memory/100_cursor-memory-context.md | memory-context | Starting new session |
| DSPy context | 100_memory/104_dspy-development-context.md | dspy-context | Deep implementation |
| Testing strategy | 400_guides/400_testing-strategy-guide.md | testing-strategy | Before writing tests |
| Scribe system | 400_guides/400_scribe-v2-system-guide.md | scribe-system | Using context capture |

## 🔄 Auto-Generation

This guide is automatically generated from file headers using `scripts/regen_guide.py`.
To regenerate this guide, run:

```bash
python3 scripts/regen_guide.py --generate
```

### Generation Criteria

- **Priority Tiers**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
- **Role Pins**: Files are tagged with role-specific access patterns
- **Context References**: Cross-references to related documentation
- **Anchor Keys**: Unique identifiers for direct navigation

### File Requirements

To be included in this guide, files must have:
- `<!-- ANCHOR_KEY: name -->` - Unique identifier
- `<!-- ANCHOR_PRIORITY: number -->` - Priority level (0-999)
- `<!-- ROLE_PINS: ["role1", "role2"] -->` - Role access patterns

Optional metadata:
- `` - Related documentation
- `` - Module dependencies
- `` - Memory context level
- `` - Database synchronization status
