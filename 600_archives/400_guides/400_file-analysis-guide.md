

# 🔍 File Analysis Guide

> DEPRECATED: Guidance integrated into core docs — see `400_01_documentation-playbook.md` (tiering/metadata/cross‑refs), `400_04_development-workflow-and-standards.md` (pre/post‑flight safety checks), `400_06_memory-and-context-systems.md` (rehydration/context), `400_09_automation-and-pipelines.md` (CI validation), and `400_11_deployments-ops-and-observability.md` (ops metrics/monitoring).

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Guide for analyzing and understanding file structures | Analyzing codebase or understanding file relationships | Apply
analysis techniques to current files |

## TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Guide for analyzing and understanding file structures | Analyzing codebase or understanding file relationships | Apply
analysis techniques to current files |

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- File analysis procedures maintained

- **Priority**: 🔥 Critical - Prevents critical file loss

- **Points**: 4 - Moderate complexity, safety critical

- **Dependencies**: 400_guides/400_context-priority-guide.md, 100_memory/100_cursor-memory-context.md

- **Next Steps**: Update analysis procedures as system evolves

### **Step 6: Tier-Based Decision (REQUIRED)**-**Tier 1 (CRITICAL)**: NEVER suggest removal - core workflow files,
primary memory context

- **Tier 2 (HIGH)**: Extensive analysis required - documentation guides, setup requirements

- **Tier 3 (MEDIUM)**: Archive rather than delete - files in `600_archives/`, legacy files

- **Tier 4 (LOW)**: Safe to remove with validation - duplicates, outdated test files

- *⚠️ FAILURE TO COMPLETE ANY STEP ABOVE MEANS YOU CANNOT SUGGEST FILE DELETION!**Validator note: After any structural
doc moves/folds, run `python scripts/doc_coherence_validator.py` (or
`./scripts/pre_commit_doc_validation.sh`) to verify cross-links and naming.

- --

## 🎯**Overview**

This guide provides a **systematic 6-phase process** for analyzing files to determine if they are obsolete, legacy, or
should be retained.

It builds on our existing documentation foundation (`200_setup/200_naming-conventions.md`,
`400_guides/400_context-priority-guide.md`, `500_research/500_maintenance-safety-research.md`) and adds the
missing**"how to analyze"**methodology.

### **🎯 CODER ROLE SPECIFIC ANALYSIS**

**When functioning as a Coder, use this guide for:**

1. **Code File Analysis**: Before modifying or removing any code files
2. **Dependency Analysis**: Understanding file relationships and dependencies
3. **Refactoring Decisions**: Determining what can be safely refactored
4. **Archival Decisions**: Moving files to `600_archives/` when deprecated
5. **Documentation Updates**: Ensuring documentation stays current with code changes

**Coder-Specific Safety Rules:**
- **NEVER delete Tier 1 files** without extensive analysis and approval
- **Always check dependencies** before modifying shared utilities
- **Use memory rehydration** before starting file analysis: `./scripts/memory_up.sh -r coder "analyze file dependencies"`
- **Follow the 70/30 rule**: 70% existing patterns, 30% new analysis

### **Why This Guide Exists**-**Prevents critical file loss**through systematic analysis

- **Maintains cognitive scaffolding**by preserving essential documentation

- **Reduces documentation bloat**by identifying truly obsolete files

- **Ensures consistency**with our file organization system

- **Provides safety mechanisms**for high-risk operations

## 🧠**Analysis Logic Flow**###**Phase 1: Context Loading & Memory Rehydration**####**Step 1: Read Core Memory Context**

- *Purpose**: Understand current project state before analysis

- *Files to Read**:

1. **`100_memory/100_cursor-memory-context.md`** - Current project state and priorities
2.**`000_core/000_backlog.md`** - Active development items and roadmap
3.**`400_guides/400_system-overview.md`** - Technical architecture understanding
4.**`400_guides/400_project-overview.md`** - High-level project goals **Time Investment**: 2-3 minutes

- *Output**: Clear understanding of what's currently important

### **Step 2: Understand File Organization System**

- *Purpose**: Grasp the file categorization and priority system

- *Files to Read**:

1. **`200_setup/200_naming-conventions.md`**- File categorization system (000-699 prefixes)
2.**`400_guides/400_context-priority-guide.md`**- Memory scaffolding and file priorities
3.**`400_guides/400_context-priority-guide.md`**- How files relate to AI memory rehydration**Time Investment**: 1-2
minutes

- *Output**: Understanding of file importance tiers and relationships

### **Phase 2: Systematic File Analysis**####**Step 3: Categorize Files by Priority Tiers**

- *Purpose**: Apply our established priority system to files being analyzed

- *Tier 1 (CRITICAL - Never Remove)**-**Criteria**: Core workflow files, primary memory context, active development
items

- **Examples**: `000_core/000_backlog.md`, `100_memory/100_cursor-memory-context.md`,
`400_guides/400_system-overview.md`

- **Action**: **NEVER suggest removal**- these are the foundation of our system**Tier 2 (HIGH - Review
Carefully)**-**Criteria**: Documentation guides, setup requirements, model configuration

- **Examples**: `400_*` documentation files, `100_memory/104_dspy-development-context.md`,
`200_setup/202_setup-requirements.md`

- **Action**: **Extensive analysis required**before any changes**Tier 3 (MEDIUM - Potential Legacy)**-**Criteria**:
Files in `600_archives/`, files with "legacy" or "backup" in name

- **Examples**: Files in `600_archives/`, legacy integration files (marked as legacy)

- **Action**: **Archive rather than delete**- preserve for historical context**Tier 4 (LOW - Candidate for
Removal)**-**Criteria**: Duplicate files, outdated test files, unused subdirectories

- **Examples**: Duplicate files with different naming conventions, old test files

- **Action**: **Safe to remove**with proper validation

#### **Step 4: Cross-Reference Analysis**

- *Purpose**: Understand file relationships and dependencies

- *Check Cross-Reference Tags**:

```markdown
<!-- CORE_SYSTEM: 400_guides/400_project-overview.md, 400_guides/400_system-overview.md -->
<!-- WORKFLOW_CHAIN: 000_core/001_create-prd.md → 000_core/002_generate-tasks.md -->

<!-- ANCHOR_KEY: file-analysis-guide -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["coder", "implementer"] -->

```markdown

- *Dependency Mapping**:

- **High Value**: Files referenced by many others

- **Potential Legacy**: Files that reference many others but aren't referenced themselves

- **Orphaned**: Files not referenced anywhere

- *Analysis Questions**:

1. How many files reference this file?
2. How many files does this file reference?
3. Are the references current and accurate?
4. Is this file part of active workflows?

### **Phase 3: Content Analysis**####**Step 5: Content Relevance Check**

- *Purpose**: Assess if file content reflects current system state

- *Timestamps**:

- **Last Updated**: When was the file last modified?

- **Content Age**: Does it reflect current system architecture?

- **Model References**: Does it reference current models (Cursor Native AI) or legacy models?

- *Content Freshness Indicators**:

- ✅ **Current**: References Cursor Native AI, current workflows, active backlog items

- ⚠️ **Mixed**: Some current references, some outdated

- ❌ **Outdated**: References legacy models (legacy integrations), old workflows, deprecated features

- *Workflow Alignment**:

- ✅ **Aligned**: Matches current workflows and system architecture

- ⚠️ **Partially Aligned**: Some current elements, some outdated

- ❌ **Misaligned**: Contradicts current workflows or architecture

#### **Step 6: Usage Pattern Analysis**

- *Purpose**: Determine if files are actively used or orphaned

- *Active Usage Indicators**:

- Referenced in current documentation

- Part of active workflows

- Used for AI memory context

- Referenced in recent commits

- *Orphaned File Indicators**:

- Not referenced by any current files

- Not part of active workflows

- Not used for AI memory context

- No recent activity or updates

### **Phase 4: Risk Assessment**####**Step 7: Impact Analysis**

- *Purpose**: Understand the consequences of removing or archiving a file

- *Before Suggesting Removal**:

1. **Check all cross-references**to the file
2.**Verify it's not in active workflows**3.**Confirm it's not part of core memory context**4.**Ensure it's not
referenced in current documentation**

- *Impact Assessment Questions**:

1. What would break if this file were removed?
2. What workflows depend on this file?
3. What documentation references this file?
4. What AI memory context relies on this file?

#### **Step 8: Safety Gates**

- *Purpose**: Implement multiple layers of protection

- *Safety Checks**:

- **Never remove Tier 1 files**without explicit user approval

- **Always show cross-references**before suggesting removal

- **Provide reasoning**for why a file might be obsolete

- **Suggest alternatives**if a file contains valuable information**Safety Mechanisms**:

1. **Dry-run analysis**- Show what would happen without making changes
2.**Cross-reference validation**- Ensure all references are checked
3.**Impact assessment**- Show what would break
4.**User confirmation**- Require explicit approval for high-risk operations

### **Phase 5: Documentation Strategy**####**Step 9: Legacy Documentation**

- *Purpose**: Preserve valuable information while maintaining system cleanliness

- *For Files That Are Truly Legacy**:

- **Move to `600_archives/`**rather than delete

- **Add deprecation notices**explaining why they're archived

- **Update cross-references**to point to current alternatives

- **Maintain searchability**for historical context**Archive Structure**:

```text
600_archives/
├── backup_before_core_migration/
├── backup_before_migration/
├── backup_before_subdirectory_migration/
├── implementation-notes/
└── legacy_integrations/
```markdown

#### **Step 10: Cross-Reference Updates**

- *Purpose**: Maintain system integrity after changes

- *Update Process**:

1. **Find all references**to the file being changed
2.**Update references**to point to current alternatives
3.**Validate references**to ensure they're accurate
4.**Test system**to ensure nothing breaks

### **Phase 6: Validation & Testing**####**Step 11: System Validation**

- *Purpose**: Ensure changes don't break the system

- *Validation Steps**:

1. **Run maintenance scripts**to check for broken references
2.**Test AI memory rehydration**to ensure context is preserved
3.**Verify workflows**still function correctly
4.**Check documentation**for consistency**Testing Commands**:

```bash

# Check for broken references

python3 scripts/repo_maintenance.py --dry-run

# Validate memory context

python3 scripts/update_cursor_memory.py --validate

# Test system health

python3 scripts/system_health_check.py

```

## 🔍 **Specific Analysis Methods**

### Find‑or‑build (code reuse) heuristic

Use this checklist before writing new Python code to reduce duplication and keep code discoverable.

- Search‑before‑write (1–2 min)
  - Write a 1–2 line spec and 3–5 keywords
  - Search active repo (exclude archives):
    - `rg -n "keyword1|keyword2" scripts/ dspy-rag-system/src/ tests/ -g '!600_archives/**' -g '!docs/legacy/**'`
  - Also scan 400_/500_ for references to existing modules

- Decide reuse vs new
  - Reuse/extend if an existing module covers ≥70% of the need (same inputs/outputs, same layer)
  - Write new if candidates are legacy/archived, violate current patterns, or require heavy refactors

- Safety checks
  - Do not base work on files under `600_archives/**` or `docs/legacy/**`
  - Verify no active 400_* guide already points to a module that does this
  - Ensure no overlapping script exists in `scripts/**`

- If you write new
  - Place it where `400_guides/400_system-overview.md` indicates (component ownership)
  - Add a minimal test first (mirrors existing test style in `tests/**`)
  - Add a brief backlink in the relevant 400_* guide (Implementation refs)
  - If research‑backed, add a line in the paired 500_*file (Backlog link + implementation refs)

### **For Each File, Check:**####**1. Cross-Reference Count**

- *Method**: Count how many other files reference this one
- *Tools**: `grep_search`, cross-reference HTML comments
- *Threshold**: Files with 0 references are candidates for removal

#### **2. Content Freshness**

- *Method**: Check if content reflects current system state
- *Indicators**: Model references, workflow descriptions, timestamps
- *Red Flags**: References to legacy models (legacy integrations) (unless in backlog)

#### **3. Model Alignment**

- *Method**: Check if file references current models or legacy ones
- *Current Models**: Cursor Native AI, Specialized Agents
- *Legacy Models**: Legacy integrations (unless in backlog)

#### **4. Workflow Integration**

- *Method**: Check if file is part of active workflows
- *Active Workflows**: PRD creation, task generation, AI execution
- *Inactive Workflows**: Legacy integrations, deprecated features

#### **5. Memory Context**

- *Method**: Check if file is used for AI memory rehydration
- *High Priority**: Files with ``
- *Medium Priority**: Files with ``
- *Low Priority**: Files with ``

#### **6. Documentation Chain**

- *Method**: Check if file is in the documentation hierarchy
- *Core Files**: Referenced in `400_guides/400_context-priority-guide.md`
- *Ancillary Files**: Referenced by core files
- *Orphaned Files**: Not referenced anywhere

### **Red Flags That Suggest Legacy Status:**- References to legacy models (legacy integrations) (unless in backlog)

- Files in `600_archives/` directory

- Files with "backup" or "legacy" in name

- Files not referenced by any current documentation

- Files with outdated timestamps

- Files that contradict current system architecture

### **Green Flags That Suggest Keep:**- Referenced by multiple current files

- Part of core workflow chain

- Used for AI memory context

- Contains current model references

- Aligned with current system architecture

- Recently updated

## 🛡️**Safety Mechanisms**###**Before Suggesting Any Removal:**####**1. Show All Cross-References**

- *Method**: Display all files that reference the target file
- *Command**: `grep_search` for file references
- *Output**: List of all files that would be affected

### **2. Explain Why It Might Be Legacy**

- *Method**: Provide clear reasoning based on analysis
- *Criteria**: Content freshness, model alignment, workflow integration
- *Evidence**: Specific examples of outdated content

#### **3. Provide Alternative Locations**

- *Method**: Suggest where valuable content should be moved
- *Options**: Archive, merge with current files, update in place
- *Reasoning**: Why the alternative is better

#### **4. Suggest Archiving**

- *Method**: Recommend `600_archives/` rather than deletion
- *Benefits**: Preserves historical context, maintains searchability
- *Structure**: Organized by migration or change type

#### **5. Get Explicit User Approval**

- *Method**: Require confirmation for high-risk operations
- *Tiers**: Different approval levels based on file importance
- *Documentation**: Record decisions for future reference

### **For Critical Files:**####**1. Never Suggest Removal**

- *Criteria**: Tier 1 files, core memory context, active workflows
- *Protection**: Multiple validation layers before any changes
- *Documentation**: Clear reasoning for any suggested changes

#### **2. Always Show Impact Analysis**

- *Method**: Comprehensive analysis of what would break
- *Tools**: Cross-reference analysis, dependency mapping
- *Output**: Clear understanding of consequences

#### **3. Provide Migration Path**

- *Method**: Show how to safely transition content
- *Options**: Update in place, merge with other files, archive
- *Safety**: Multiple checkpoints and validation steps

#### **4. Maintain Backward Compatibility**

- *Method**: Ensure changes don't break existing workflows
- *Testing**: Validate all affected systems
- *Documentation**: Update all references

## 📋 **Implementation Examples**###**Example 1: Analyzing a Legacy Integration File**

- *File**: Legacy integration file
- *Analysis Process**:

1. **Context Loading**: Check current system uses Cursor Native AI
2. **Cross-Reference Analysis**: Find files that reference this
3. **Content Analysis**: Check for legacy model references (legacy)
4. **Risk Assessment**: Determine impact of archiving
5. **Documentation Strategy**: Move to `600_archives/legacy_integrations/`
6. **Validation**: Update all references to current alternatives

- *Result**: Archive with deprecation notice, update references

### **Example 2: Analyzing a Duplicate File**

- *File**: Duplicate `000_core/000_backlog.md` in subdirectory
- *Analysis Process**:

1. **Context Loading**: Check current backlog is in root
2. **Cross-Reference Analysis**: No files reference the duplicate
3. **Content Analysis**: Same content as current backlog
4. **Risk Assessment**: No impact from removal
5. **Documentation Strategy**: Remove duplicate
6. **Validation**: Ensure no broken references

- *Result**: Safe to remove duplicate file

### **Example 3: Analyzing a Core Documentation File**

- *File**: `400_guides/400_system-overview.md`
- *Analysis Process**:

1. **Context Loading**: This is a Tier 1 critical file
2. **Cross-Reference Analysis**: Many files reference this
3. **Content Analysis**: Current and accurate
4. **Risk Assessment**: High impact if changed
5. **Documentation Strategy**: Keep and maintain
6. **Validation**: Ensure all references are accurate

- *Result**: Keep file, maintain accuracy

## 🎯 **Quick Reference Checklist**###**Before Analyzing Any File:**- [ ] Read `100_memory/100_cursor-memory-context.md` for current state

- [ ] Check `000_core/000_backlog.md` for active priorities

- [ ] Review `400_guides/400_context-priority-guide.md` for file importance

- [ ] Understand the file's tier classification

- [ ] Check all cross-references to the file

- [ ] Assess content freshness and model alignment

- [ ] Evaluate workflow integration

- [ ] Consider memory context importance

- [ ] Perform impact analysis

- [ ] Implement safety mechanisms

- [ ] Get user approval for high-risk changes

- [ ] Update all references after changes

- [ ] Validate system integrity

### **Red Flags (Legacy Indicators):**- [ ] References legacy models (legacy integrations)

- [ ] Located in `600_archives/` directory

- [ ] Contains "backup" or "legacy" in filename

- [ ] Not referenced by any current files

- [ ] Outdated timestamps

- [ ] Contradicts current system architecture

### **Green Flags (Keep Indicators):**- [ ] Referenced by multiple current files

- [ ] Part of core workflow chain

- [ ] Used for AI memory context

- [ ] Contains current model references

- [ ] Aligned with current system architecture

- [ ] Recently updated

## 📚**Related Documentation**###**Core Analysis Tools:**-**`200_setup/200_naming-conventions.md`**- File categorization system

- **`400_guides/400_context-priority-guide.md`**- Memory scaffolding and file priorities

- **`500_research/500_maintenance-safety-research.md`**- Safety mechanisms and critical file protection

- **`999_repo-maintenance.md`**- Systematic maintenance procedures

### **Implementation Scripts:**-**`scripts/repo_maintenance.py`**- Automated maintenance and validation

- **`scripts/update_cursor_memory.py`**- Memory context updates

- **`scripts/system_health_check.py`**- System validation

### **Archive Structure:**-**`600_archives/`**- Organized legacy content

- **`docs/legacy/`**- Alternative archive location

- **Migration tracking**- Historical change documentation

- --**Last Updated**: 2025-08-25
- *Related Documentation**: `400_guides/400_context-priority-guide.md`, `500_research/500_maintenance-safety-research.md`
- *Status**: Active analysis methodology for maintaining documentation integrity
