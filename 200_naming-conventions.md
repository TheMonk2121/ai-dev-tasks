# File Naming Conventions & Memory Scaffolding Guidelines

<!-- MEMORY_CONTEXT: MEDIUM - File organization and documentation guidelines for maintaining memory scaffolding -->

**For memory-scaffolding patterns see 401_memory-scaffolding-guide.md**

## 📋 Overview

This document defines the file naming conventions and memory scaffolding guidelines for the AI development ecosystem. The system is designed to be understandable by both humans and large language models (LLMs).

## 🔢 Number Prefixes

Files are categorized by purpose using numeric prefixes:

- **`000-009`** – Core Workflow (PRD creation, task generation, execution)
- **`100-199`** – Automation & Tools (backlog management, memory context)
- **`200-299`** – Configuration & Setup (model config, setup requirements)
- **`300-399`** – Templates & Examples (documentation examples, templates)
- **`400-499`** – Documentation & Guides (project overview, system overview, context guides)
- **`500-599`** – Testing & Observability (test harnesses, monitoring, security validation)
- **`600-699`** – Archives & Completion Records (historical summaries, completion records)

## 📝 File Naming Rules

### ✅ Correct Examples
- `000_backlog.md` (three-digit prefix, single underscore, kebab-case)
- `100_cursor-memory-context.md` (automation category)
- `400_project-overview.md` (documentation category)
- `500_test-harness-guide.md` (testing category)

### ❌ Incorrect Examples
- `99_misc.md` (needs three-digit prefix)
- `100_backlog_automation.md` (second underscore disallowed)
- `100-backlog-automation.md` (missing required first underscore)

## 🧠 Memory Scaffolding Documentation Guidelines

### Content Structure
Each file should include:
1. **Memory Context Comment**: `<!-- MEMORY_CONTEXT: [HIGH|MEDIUM|LOW] - [description] -->`
2. **Context Reference**: `<!-- CONTEXT_REFERENCE: [related-file].md -->`
3. **Clear Purpose**: What this file is for and when to read it
4. **Related Files**: Links to other relevant documentation

### Memory Context Levels
- **HIGH**: Read first for instant context (core workflow, system overview)
- **MEDIUM**: Read when working on specific workflows (PRD creation, task generation)
- **LOW**: Read for detailed implementation (specific integrations, configurations)

### Quality Checklist
- [ ] Clear, descriptive filename
- [ ] Memory context comment included
- [ ] Purpose and usage explained
- [ ] Related files referenced
- [ ] Content is current and accurate
- [ ] Follows established patterns

## 🔄 Migration Tracking

File renames and structural changes are tracked via Git issues rather than static tables in documentation. This ensures:

- **Current Information**: No stale references in documentation
- **Version Control**: Full history of changes
- **AI-Friendly**: Easy to parse and understand
- **Human-Friendly**: Standard development workflow

## 🛠️ Implementation Tools

### Collision Detection
The `scripts/check-number-unique.sh` script runs as a warning-only pre-commit hook to detect duplicate numeric prefixes in HIGH priority files (000-099, 400-499, 500-599).

### Memory Hierarchy Display
Use `python3 scripts/show_memory_hierarchy.py` to display the current memory context hierarchy for human understanding.

### Memory Context Updates
Use `python3 scripts/update_cursor_memory.py` to automatically update memory context based on backlog priorities.

## 📚 Current Project Structure

### Core Workflow (000-009)
- `000_backlog.md` - Product backlog and current priorities
- `001_create-prd.md` - PRD creation workflow
- `002_generate-tasks.md` - Task generation workflow
- `003_process-task-list.md` - AI task execution workflow

### Automation & Tools (100-199)
- `100_cursor-memory-context.md` - Primary memory scaffold for Cursor AI
- `100_backlog-guide.md` - Backlog management guide
- `100_backlog-automation.md` - Backlog automation details
- `103_yi-coder-integration.md` - Yi-Coder integration guide
- `104_dspy-development-context.md` - DSPy development context

### Configuration & Setup (200-299)
- `200_naming-conventions.md` - This file
- `201_model-configuration.md` - AI model configuration
- `202_setup-requirements.md` - Environment setup requirements

### Templates & Examples (300-399)
- `300_documentation-example.md` - Documentation example template

### Documentation & Guides (400-499)
- `400_project-overview.md` - Project overview and workflow guide
- `400_system-overview.md` - Technical architecture and system overview
- `400_context-priority-guide.md` - Context priority guide for memory rehydration
- `400_memory-context-guide.md` - Memory context system guide
- `400_timestamp-update-guide.md` - Timestamp update procedures
- `400_current-status.md` - Current system status and health
- `400_dspy-integration-guide.md` - DSPy integration guide
- `400_mistral7b-instruct-integration-guide.md` - Mistral 7B integration guide
- `400_n8n-setup-guide.md` - n8n setup and configuration guide
- `400_mission-dashboard-guide.md` - Mission dashboard guide
- `400_n8n-backlog-scrubber-guide.md` - n8n backlog scrubber guide

### Archives & Completion Records (500-599)
- `500_c9-completion-summary.md` - Historical completion record
- `500_c10-completion-summary.md` - Historical completion record
- `500_memory-arch-benchmarks.md` - Memory architecture benchmark results
- `500_memory-arch-research.md` - Memory architecture research framework

## 🚀 Adding New Categories

### Testing & Observability (500-599)
Examples: `500_test-harness-guide.md`, `501_red-team-suite.md`, `502_monitoring-dashboard.md`

### Versioning
Use `_vN` suffix **only** when the file's public contract changes (breaking changes). For minor edits, append to the embedded **Change Log** table.

## 🔗 Related Files

<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- SYSTEM_FILES: 400_system-overview.md --> 