<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 102_memory-context-state.md -->
<!-- MODULE_REFERENCE: 103_memory-context-workflow.md -->

<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
- **400-499**: Architecture and overview (system overview, project overview, context priority guide)
- **500+**: Research and meta-documentation (completion summaries, research notes, benchmarks)

**Step 4: Descriptive Naming**
- Use clear, descriptive names that indicate content
- Follow kebab-case convention (lowercase with hyphens)
- Avoid multiple underscores or special characters
- Make the filename self-documenting

**Step 5: Cross-Reference Integration**
- Ensure the file can be referenced in the context priority guide
- Add appropriate HTML comment references
- Consider AI rehydration needs

### **Integration with Development Workflow**

The naming system **integrates seamlessly** with our development workflow. When creating new files, the process is:
1. **Check existing patterns** in the same prefix range for consistency
2. **Follow the naming conventions** documented in this file
3. **Add cross-references** using HTML comment patterns
4. **Update the context priority guide** if the file belongs in a documented tier
5. **Consider AI rehydration** - will this file be needed for context sharing?

**Quality Assurance:**
- **Consistency checks** ensure similar files use similar naming patterns
- **Cross-reference validation** ensures new files are properly linked
- **Context priority guide updates** keep the documentation hierarchy current
- **AI-friendly naming** ensures files are discoverable by Cursor AI

The result is a **living naming system** that scales with your project while maintaining the cognitive scaffolding that makes the documentation coherent and AI-friendly. Each new file automatically fits into the existing hierarchy, making it easy for both humans and AI to understand its role and importance in the overall system.

## 🔄 File Generation Decision Process

### **Step 1: Determine if a File is Needed**

**Ask these questions:**
- **Is this information that will be referenced multiple times?** (If yes → file)
- **Is this a process or workflow that others/AI will need to follow?** (If yes → file)
- **Is this context that will help with future decisions?** (If yes → file)
- **Is this a one-off note or temporary information?** (If no → don't create file)

**Examples of when to create files:**
- ✅ **Workflow processes** (`001_create-prd.md`, `002_generate-tasks.md`)
- ✅ **System documentation** (`400_system-overview_advanced_features.md`, `400_project-overview.md`)
- ✅ **Configuration guides** (`201_model-configuration.md`, `202_setup-requirements.md`)
- ✅ **Completion summaries** (`500_*` files for historical context)
- ✅ **Research findings** (`500_memory-arch-research.md`)

**Examples of when NOT to create files:**
- ❌ **Temporary notes** (use comments or inline documentation)
- ❌ **One-off decisions** (document in existing relevant files)
- ❌ **Quick fixes** (document in commit messages or existing files)

### **Step 2: Determine File Purpose and Priority**

**Analyze the content type:**
- **Planning/Strategy** → High priority (000-099, 400-499)
- **Implementation/Technical** → Medium priority (100-199, 200-299)
- **Research/Analysis** → Lower priority (500+)
- **Configuration/Setup** → Medium priority (200-299)

**Assess the audience:**
- **Essential for everyone** → High priority (read first)
- **Important for specific workflows** → Medium priority (read when relevant)
- **Specialized knowledge** → Lower priority (read when needed)

**Consider the lifecycle:**
- **Always relevant** → High priority (core documentation)
- **Sometimes relevant** → Medium priority (workflow guides)
- **Rarely relevant** → Lower priority (specialized guides)

### **Step 3: Choose the Right Prefix Range**

**000-099: Core Planning & Context**
- Backlog, project overview, system overview
- Files that give immediate understanding of the project
- Essential for anyone working on the project

**100-199: Memory & Guides**
- Memory context, backlog guide, automation patterns
- Files that help with ongoing work and decision-making
- Important for regular development activities

**200-299: Configuration & Setup**
- Naming conventions, model config, setup requirements
- Files that help with environment and tool setup
- Important when setting up or configuring

**400-499: Architecture & Overview**
- System overview, project overview, context priority guide
- Files that explain the big picture and relationships
- Essential for understanding the system architecture

**500+: Research & Meta**
- Completion summaries, research notes, benchmarks
- Files that provide historical context and analysis
- Useful for learning from past work

### **Step 4: Create Descriptive, Self-Documenting Names**

**Follow these naming principles:**
- **Clear purpose**: The name should indicate what the file contains
- **Consistent format**: `prefix_descriptive-name.md`
- **Kebab-case**: Lowercase with hyphens for readability
- **Avoid ambiguity**: Make it clear what the file is for

**Examples of good names:**
- ✅ `100_cursor-memory-context.md` (clear purpose)
- ✅ `400_system-overview_advanced_features.md` (descriptive)
- ✅ `201_model-configuration.md` (specific domain)
- ✅ `500_memory-arch-research.md` (research focus)

**Examples of bad names:**
- ❌ `misc.md` (unclear purpose)
- ❌ `stuff.md` (not descriptive)
- ❌ `temp.md` (temporary feeling)

### **Step 5: Consider Cross-References and Integration**

**Think about relationships:**
- **What other files reference this information?**
- **What files should this file reference?**
- **How does this fit into the cognitive scaffolding?**

**Add appropriate cross-references:**
- `<!-- ESSENTIAL_FILES: 400_project-overview.md, 400_system-overview_advanced_features.md -->`
- `<!-- IMPLEMENTATION_FILES: 104_dspy-development-context.md -->`

**Consider AI rehydration:**
- **Will Cursor AI need this for context?**
- **Is this information that should be loaded early or late?**
- **Does this belong in the memory context or as a reference?**

### **Step 6: Validate Against Existing Patterns**

**Check for consistency:**
- **Are there similar files in the same prefix range?**
- **Does this follow the established naming patterns?**
- **Is this the right level of detail for this priority?**

**Consider the cognitive scaffolding:**
- **Does this file help or hurt the AI's understanding?**
- **Is this information better placed in an existing file?**
- **Will this file be discoverable by the AI?**

### **Example Decision Process**

**Scenario**: Need to document a new workflow for automated testing

**Step 1**: ✅ **File needed** - This is a process others will follow
**Step 2**: **Purpose** = Implementation workflow, **Priority** = Medium (important for specific tasks)
**Step 3**: **Prefix** = 100-199 (workflow guides)
**Step 4**: **Name** = `101_automated-testing-workflow.md`
**Step 5**: **Cross-references** = Reference `400_context-priority-guide.md`, essential files
**Step 6**: **Validation** = Consistent with other workflow files, appropriate priority

**Result**: Creates `101_automated-testing-workflow.md` with proper cross-references and integration into the cognitive scaffolding system.

This process ensures that every file created serves a clear purpose, fits into the existing structure, and contributes to the overall coherence of the documentation system.

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
- `400_system-overview_advanced_features.md` - Technical architecture and system overview
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

<!-- SYSTEM_FILES: 400_system-overview_advanced_features.md --> 