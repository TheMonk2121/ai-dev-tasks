<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 100_memory/100_cursor-memory-context.md -->
<!-- MODULE_REFERENCE: 100_memory/103_memory-context-workflow.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- markdownlint-disable MD041 -->

# Naming Conventions

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| File and directory naming standards for the project | Creating new files or organizing content | Apply conventions to
new files and update existing ones |



## TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| File and directory naming standards for the project | Creating new files or organizing content | Apply conventions to
new files and update existing ones |



## Category Table (Accepted Exceptions & Deferrals)

## 🔢 Prefix Category Table

This table clarifies the buckets for our numeric prefixes, making it easier to categorize and find files.

| Prefix Range | Category Name                 | Purpose                                                                 | Examples                                                              |
| :----------- | :---------------------------- | :----------------------------------------------------------------------
| :-------------------------------------------------------------------- |
| `000-099` | Core Workflow & Planning | Core processes, backlog, PRDs, and high-level project plans. |
`000_core/000_backlog.md`, `000_core/001_create-prd.md` |
| `100-199` | Guides & Automation | Memory context, workflow guides, and automation tools. |
`100_memory/100_cursor-memory-context.md`, `100_memory/100_backlog-guide.md` |
| `200-299` | Configuration & Setup | Environment setup, naming conventions, and tool configuration. |
`200_setup/200_naming-conventions.md`, `200_setup/202_setup-requirements.md` |
| `300-399` | Templates & Examples | Reusable templates, documentation examples, and few-shot prompts. |
`300_examples/300_documentation-example.md`, `400_guides/400_few-shot-context-examples.md` |
| `400-499` | System Architecture & Overviews | High-level system design, project overviews, and context guides. |
`400_guides/400_system-overview.md`, `400_guides/400_project-overview.md` |
| `500-599` | Research, Testing & Analysis | Research, benchmarks, testing, observability, and completion summaries. |
`500_research/500_dspy-research.md`, `500_test-harness-guide.md` |
| `600-999` | Archives & Legacy | Deprecated files, historical archives, and legacy documentation. | `600_archives/`,
`docs/legacy/` |

### Integration with Development Workflow

The naming system **integrates seamlessly**with our development workflow. When creating new files, the process is:

1.**Check existing patterns**in the same prefix range for consistency
2.**Follow the naming conventions**documented in this file
3.**Add cross-references**using HTML comment patterns
4.**Update the context priority guide**if the file belongs in a documented tier
5.**Consider AI rehydration**- will this file be needed for context sharing?

#### Quality Assurance

- **Consistency checks**ensure similar files use similar naming patterns

- **Cross-reference validation**ensures new files are properly linked

- **Context priority guide updates**keep the documentation hierarchy current

- **AI-friendly naming**ensures files are discoverable by Cursor AI

The result is a**living naming system**that scales with your project while maintaining the cognitive scaffolding that
makes the documentation coherent and AI-friendly. Each new file automatically fits into the existing hierarchy, making
it easy for both humans and AI to understand its role and importance in the overall system.

## 🔄 File Generation {#file-generation}

### Step 1: Determine if a File is Needed

#### Ask these questions

- **Is this information that will be referenced multiple times?**(If yes → file)

- **Is this a process or workflow that others/AI will need to follow?**(If yes → file)

- **Is this context that will help with future decisions?**(If yes → file)

- **Is this a one-off note or temporary information?**(If no → don't create file)

#### Examples of when to create files

- ✅**Workflow processes**(`000_core/001_create-prd.md`, `000_core/002_generate-tasks.md`)

- ✅**System documentation**(`400_guides/400_system-overview.md`, `400_guides/400_project-overview.md`)

- ✅**Configuration guides**(`200_setup/202_setup-requirements.md`)

- ✅**Completion summaries** (`500_*` files for historical context)

- ✅ **Research findings**(`500_research/500_memory-arch-research.md`)

#### Examples of when NOT to create files

- ❌**Temporary notes**(use comments or inline documentation)

- ❌**One-off decisions**(document in existing relevant files)

- ❌**Quick fixes**(document in commit messages or existing files)

### Step 2: Determine File Purpose and Priority

#### Analyze the content type

- **Planning/Strategy**→ High priority (000-099, 400-499)

- **Implementation/Technical**→ Medium priority (100-199, 200-299)

- **Research/Analysis**→ Lower priority (500+)

- **Configuration/Setup**→ Medium priority (200-299)

#### Assess the audience

- **Essential for everyone**→ High priority (read first)

- **Important for specific workflows**→ Medium priority (read when relevant)

- **Specialized knowledge**→ Lower priority (read when needed)

#### Consider the lifecycle

- **Always relevant**→ High priority (core documentation)

- **Sometimes relevant**→ Medium priority (workflow guides)

- **Rarely relevant**→ Lower priority (specialized guides)

### Step 3: Choose the Right Prefix Range**000-099: Core Planning & Context**- Backlog, project overview, system
overview

- Files that give immediate understanding of the project

- Essential for anyone working on the project**100-199: Memory & Guides**- Memory context, backlog guide, automation
patterns

- Files that help with ongoing work and decision-making

- Important for regular development activities**200-299: Configuration & Setup**- Naming conventions, model config,
setup requirements

- Files that help with environment and tool setup

- Important when setting up or configuring**400-499: Architecture & Overview**- System overview, project overview,
context priority guide

- Files that explain the big picture and relationships

- Essential for understanding the system architecture**500+: Research & Meta**- Completion summaries, research notes,
benchmarks

- Files that provide historical context and analysis

- Useful for learning from past work

### Step 4: Create Descriptive, Self-Documenting Names

#### Follow these naming principles

- **Clear purpose**: The name should indicate what the file contains

- **Consistent format**: `prefix_descriptive-name.md`

- **Kebab-case**: Lowercase with hyphens for readability

- **Avoid ambiguity**: Make it clear what the file is for

#### Examples of good names

- ✅ `100_memory/100_cursor-memory-context.md` (clear purpose)

- ✅ `400_guides/400_system-overview.md` (descriptive)

- ✅ `500_research/500_memory-arch-research.md` (research focus)

#### Examples of bad names

- ❌ `misc.md` (unclear purpose)

- ❌ `stuff.md` (not descriptive)

- ❌ `temp.md` (temporary feeling)

### Step 5: Add AI API Comments and Cross-References

#### Add appropriate AI API comments

- **HIGH priority files**: Must include CONTEXT_REFERENCE and MEMORY_CONTEXT

- **MEDIUM priority files**: Should include MODULE_REFERENCE and MEMORY_CONTEXT

- **Cross-references**: Always validate that referenced files exist

#### Examples

```markdown
<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MEMORY_CONTEXT: HIGH - Core workflow guide -->
<!-- ESSENTIAL_FILES: 400_guides/400_project-overview.md, 400_guides/400_system-overview.md -->

```

### Step 6: Validate Against Existing Patterns

#### Check for consistency

- **Are there similar files in the same prefix range?**
- **Does this follow the established naming patterns?**
- **Is this the right level of detail for this priority?**

#### Consider the cognitive scaffolding

- **Does this file help or hurt the AI's understanding?**
- **Is this information better placed in an existing file?**
- **Will this file be discoverable by the AI?**

### Example Decision Process

**Scenario**: Need to document a new workflow for automated testing

- **Step 1**: ✅ **File needed** - This is a process others will follow
- **Step 2**: **Purpose** = Implementation workflow, **Priority** = Medium (important for specific tasks)
- **Step 3**: **Prefix** = 100-199 (workflow guides)
- **Step 4**: **Name** = `101_automated-testing-workflow.md`
- **Step 5**: **AI API** = Add MODULE_REFERENCE and MEMORY_CONTEXT comments
- **Step 6**: **Validation** = Consistent with other workflow files, appropriate priority

**Result**: Creates `101_automated-testing-workflow.md` with proper AI API comments and integration into the cognitive scaffolding system.

This process ensures that every file created serves a clear purpose, fits into the existing structure, and contributes to the overall coherence of the documentation system.

<!-- Section moved earlier: Prefix Category Table -->

## 📝 File Naming Rules

### ✅ Correct Examples

- `000_core/000_backlog.md` (three-digit prefix, single underscore, kebab-case)

- `100_memory/100_cursor-memory-context.md` (automation category)

- `400_guides/400_project-overview.md` (documentation category)

- `500_test-harness-guide.md` (testing category)

### ❌ Incorrect Examples

- `99_misc.md` (needs three-digit prefix)

- `100_backlog_automation.md` (second underscore disallowed)

- `100-backlog-automation.md` (missing required first underscore)

## 📝 Formatting Standards {#formatting-standards}

### Header Structure Rules

- **Single h1 per document**: Use filename as the implicit h1 title

- **Main content starts with h2**: `## 🎯 Current Status` or `## 📋 Overview`

- **Consistent emoji usage**: Use emojis for visual hierarchy and AI parsing

- **No h1 in content**: All content headings should be h2 or lower

- **Hierarchical structure**: Use h2 for main sections, h3 for subsections, h4 for details

## 🔐 Core Documentation Invariants

- Purpose: Single normative source for core documentation requirements. Validator enforces these invariants.

### Required top metadata header (HTML comments)

- HIGH‑priority docs must include:
  - `<!-- CONTEXT_REFERENCE: <file> -->`
  - `<!-- MEMORY_CONTEXT: <LEVEL> - <description> -->`

- `MODULE_REFERENCE` is required when a closely related implementation module exists.

- See: 🤖 AI API Documentation Standards (below)

### TL;DR + At‑a‑glance

- TL;DR section is required in core docs
  - A single explicit anchor is allowed: `{#tldr}`
  - Heading: `## 🔎 TL;DR`

- Immediately after TL;DR, include a 3‑column “At‑a‑glance” table with exact headers:

| what this file is | read when | do next |
|---|---|---|
|_one‑line purpose_|_trigger moments_|_2–3 links/actions_ |

### Stable Anchors (kebab‑case)

- Required anchors per doc type (must exist as section anchors):
  - `100_memory/100_cursor-memory-context.md`: `tldr`, `quick-start`, `quick-links`, `commands`
  - `400_guides/400_project-overview.md`: `tldr`, `quick-start`, `mini-map`
  - `400_guides/400_context-priority-guide.md`: `tldr`, `critical-path`, `ai-file-analysis-strategy`, `documentation-placement-logic`
  - `000_core/000_backlog.md`: `tldr`, `p0-lane`, `ai-executable-queue-003`, `live-backlog`
  - `200_setup/200_naming-conventions.md`: `tldr`, `file-generation`, `formatting-standards`, `ai-api-standards`
  - `100_memory/100_backlog-guide.md`: `tldr`, `scoring`, `prd-rule`, `selection-criteria`

### Canonical link targets (link, don’t duplicate)

- Quick Start → `400_guides/400_project-overview.md`

- Critical Path → `400_guides/400_context-priority-guide.md`

- PRD/Scoring → `100_memory/100_backlog-guide.md`

### Anchor policy (phased)

- Only TL;DR may use an explicit HTML anchor (`{#tldr}`). All other anchors must be heading‑based.
- Rollout: validator warns first; flips to errors after link hygiene completes.

### Table Usage Mandate

Markdown tables are the **required standard** for presenting structured data:

- **Status tracking**: Use tables for backlog items, task lists, and progress tracking

- **Decision records**: Structure decisions with clear columns for date, decision, rationale, impact

- **Priority matrices**: Use tables for comparing options or categorizing items

- **Stakeholder information**: Organize roles, responsibilities, and contact information

- **Cross-reference matrices**: Map relationships between files and components

### Internal Linking Standards

- **Primary method**: Use auto-generated heading IDs `[Link Text](#-section-title)`

- **Critical sections**: Allow explicit IDs for stability `[Link Text](#explicit-id)`

- **Cross-file linking**: Use relative paths with anchor links

- **AI-friendly linking**: Include context in link text for better AI parsing

- **Validation**: Ensure all referenced sections exist

## 🤖 AI API Standards {#ai-api-standards}

The HTML comments in our documentation serve as a **formal API for AI consumption**. These comments enable cognitive scaffolding and context rehydration.

### Core Comment Types

| Key | Purpose | Example | Required For |
| :--- | :--- | :--- | :--- |
| CONTEXT_REFERENCE | Links to the main guide for context | `<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->` | HIGH priority files |
| MODULE_REFERENCE | Links to a related implementation module | `<!-- MODULE_REFERENCE: 100_memory/104_dspy-development-context.md -->` | MEDIUM priority files |
| MEMORY_CONTEXT | Specifies priority level for AI rehydration | `<!-- MEMORY_CONTEXT: HIGH - Core workflow guide -->` | All files |
| ESSENTIAL_FILES | Lists files critical for understanding | `<!-- ESSENTIAL_FILES: 400_guides/400_project-overview.md -->` | HIGH priority files |

### Usage Patterns

- **HIGH priority files**: Must include CONTEXT_REFERENCE and MEMORY_CONTEXT

- **MEDIUM priority files**: Should include MODULE_REFERENCE and MEMORY_CONTEXT

- **Cross-references**: Always validate that referenced files exist

- **Consistency**: Use consistent comment patterns across similar file types

### AI Rehydration Optimization

- **Structured data**: Use consistent patterns for status, priority, points

- **Explicit relationships**: Always include cross-references

- **Actionable information**: Include next steps and dependencies

- **Context preservation**: Use memory context comments

## 🧠 Memory Scaffolding Documentation Guidelines

### Content Structure

Each file should include:

1. **Memory Context Comment**: `<!-- MEMORY_CONTEXT: [HIGH|MEDIUM|LOW] - [description] -->`
2. **Clear Purpose**: What this file is for and when to read it
3. **Related Files**: Links to other relevant documentation
4. **Structured Status**: Use consistent status reporting format
5. **Decision Records**: Document important decisions with rationale
6. **Learning Notes**: Capture insights and implications

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

- [ ] Structured data in tables (where applicable)

- [ ] Internal links validated

- [ ] AI API comments present and accurate

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

- `000_core/000_backlog.md` - Product backlog and current priorities

- `000_core/001_create-prd.md` - PRD creation workflow

- `000_core/002_generate-tasks.md` - Task generation workflow

- `000_core/003_process-task-list.md` - AI task execution workflow

### Automation & Tools (100-199)

- `100_memory/100_cursor-memory-context.md` - Primary memory scaffold for Cursor AI

- `100_memory/100_backlog-guide.md` - Backlog management guide

- `100_memory/100_backlog-automation.md` - Backlog automation details

- `100_memory/104_dspy-development-context.md` - DSPy development context

### Configuration & Setup (200-299)

- `200_setup/200_naming-conventions.md` - This file

- `200_setup/202_setup-requirements.md` - Environment setup requirements

### Templates & Examples (300-399)

- `300_examples/300_documentation-example.md` - Documentation example template

### Documentation & Guides (400-499)

- `400_guides/400_project-overview.md` - Project overview and workflow guide

- `400_guides/400_system-overview.md` - Technical architecture and system overview

- `400_guides/400_context-priority-guide.md` - Context priority guide for memory rehydration

- `100_memory/100_cursor-memory-context.md` - Memory context system guide

- `400_guides/400_timestamp-update-guide.md` - Timestamp update procedures

- `400_current-status.md` - Current system status and health

- `400_dspy-integration-guide.md` - DSPy integration guide

- `400_guides/400_n8n-setup-guide.md` - n8n setup and configuration guide

- `400_guides/400_mission-dashboard-guide.md` - Mission dashboard guide

- `400_guides/400_n8n-backlog-scrubber-guide.md` - n8n backlog scrubber guide

### Archives & Completion Records (500-599)

- `500_c9-completion-summary.md` - Historical completion record

- `500_c10-completion-summary.md` - Historical completion record

- `500_memory-arch-benchmarks.md` - Memory architecture benchmark results

- `500_research/500_memory-arch-research.md` - Memory architecture research framework

## 🚀 Adding New Categories

### Testing & Observability (500-599)

Examples: `500_test-harness-guide.md`, `501_red-team-suite.md`, `502_monitoring-dashboard.md`

### Versioning

Use `_vN` suffix **only** when the file's public contract changes (breaking changes). For minor edits, append to the embedded **Change Log** table.

## 🔄 Living Document Policy

This naming conventions guide is a **living document** that evolves with the project. We encourage continuous improvement and welcome proposals for:

- **New patterns**: As the project grows, new documentation patterns may emerge

- **Refinements**: Improvements to existing conventions based on usage experience

- **AI enhancements**: Better ways to support AI collaboration and cognitive scaffolding

- **Automation**: Tools and scripts to enforce and validate these standards

### Proposing Changes

When proposing changes to this document:

1. **Test the pattern**: Use it in practice before formalizing
2. **Document the rationale**: Explain why the change improves the system
3. **Consider AI impact**: Ensure changes enhance rather than hinder AI collaboration
4. **Update examples**: Include practical examples of the new pattern
5. **Validate consistency**: Ensure changes align with existing cognitive scaffolding

### Continuous Improvement Process

- **Regular review**: Periodically assess how well these conventions serve the project

- **Feedback collection**: Gather input from both human developers and AI assistants

- **Pattern evolution**: Allow the system to grow organically while maintaining coherence

- **Quality preservation**: Ensure all changes maintain or improve the AI-friendly nature of the documentation

## 🔗 Related Files

<!-- SYSTEM_FILES: 400_guides/400_system-overview.md -->
<!-- markdownlint-enable MD041 -->
