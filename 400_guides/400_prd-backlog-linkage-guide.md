# PRD-Backlog Linkage Guide

## TL;DR

**What**: Enhanced system for linking Product Requirements Documents (PRDs) with backlog items, including dependency tracking and impact scope documentation.

**Why**: Ensures complete traceability, prevents orphaned documentation, and improves project planning through clear dependency chains.

**How**: Standardized PRD headers with dependency information, automated validation, and Cursor rule enforcement.

**Impact**: Complete visibility into project dependencies, improved planning accuracy, and consistent documentation standards.

---

## Overview

The PRD-Backlog Linkage System ensures that every Product Requirements Document (PRD) is properly connected to its corresponding backlog item, with comprehensive dependency and impact information. This system provides complete traceability and prevents documentation drift.

## Core Components

### 1. Enhanced PRD Headers

Every PRD must include the following standardized header:

```markdown
# PRD: [Title]

**Backlog Item**: B-XXX
**Status**: [Ready for Implementation | In Progress | Completed]
**Estimated Hours**: X hours

**Dependencies**:
- **Upstream**: [Items that must be completed first]
- **Downstream**: [Items that depend on this completion]
- **Blocking**: [Items that block this implementation]

**Impact Scope**:
- **Direct**: [Immediate changes required]
- **Indirect**: [Systems/components affected]
- **Public Contracts**: [APIs, schemas, interfaces changed]

## TL;DR
```

### 2. Validation Script

**File**: `scripts/validate_prd_backlog_linkage.py`

**Purpose**: Automated validation of PRD-backlog linkages

**Usage**:
```bash
python3 scripts/validate_prd_backlog_linkage.py
```

**Checks**:
- PRD files reference valid backlog items
- Backlog items with PRDs reference the PRD files
- Dependency consistency between backlog and PRDs
- Impact scope documentation completeness

### 3. Cursor Rule

**File**: `.cursorrules`

**Enforcement**: Automatic reminder when creating/updating PRDs

**Requirements**:
1. Every PRD must reference its backlog item
2. Every backlog item with PRD must reference the PRD file
3. Status must be synchronized between backlog and PRD
4. Dependencies must be clearly documented
5. Impact scope must be defined
6. Run validation script after changes

## Workflow

### Creating a New PRD

1. **Select backlog item** from `000_core/000_backlog.md`
2. **Use PRD template** from `000_core/001_create-prd.md`
3. **Include enhanced header** with all required fields
4. **Run validation script** to ensure compliance
5. **Update backlog metadata** to reference the PRD

### Updating Existing PRDs

1. **Update PRD content** as needed
2. **Ensure header compliance** with new standards
3. **Run validation script** to check for issues
4. **Synchronize status** between backlog and PRD

### Archiving PRDs

1. **Move PRD file** to `600_archives/prds/`
2. **Update backlog status** to reflect completion
3. **Remove PRD reference** from backlog metadata
4. **Run validation script** to confirm cleanup

## Dependency Types

### Upstream Dependencies
- **Definition**: Items that must be completed before this item
- **Example**: "B-182 (Bug-Fix Playbook must be implemented first)"
- **Impact**: Blocks implementation until dependencies are complete

### Downstream Dependencies
- **Definition**: Items that depend on this item's completion
- **Example**: "B-183 (Feature Refactor Framework depends on this)"
- **Impact**: Affects planning and resource allocation

### Blocking Dependencies
- **Definition**: Items that actively block this implementation
- **Example**: "B-XXX (Database migration blocking this feature)"
- **Impact**: Requires immediate resolution to proceed

## Impact Scope Categories

### Direct Impact
- **Definition**: Immediate changes required by this item
- **Example**: "Debugging workflow, Cursor integration, CI validation"
- **Scope**: Code, configuration, and immediate system changes

### Indirect Impact
- **Definition**: Systems and components affected by this item
- **Example**: "All future bugfixes, development velocity, regression prevention"
- **Scope**: Workflow, process, and long-term system effects

### Public Contracts
- **Definition**: APIs, schemas, or interfaces changed by this item
- **Example**: "Schema generation APIs, validation APIs"
- **Scope**: External interfaces and breaking changes

## Validation Rules

### Required Fields
- ✅ **Backlog Item**: Must reference valid B-XXX item
- ✅ **Status**: Must be one of the defined status values
- ✅ **Estimated Hours**: Must be a numeric value
- ✅ **Dependencies**: Must include all three categories (upstream, downstream, blocking)
- ✅ **Impact Scope**: Must include all three categories (direct, indirect, public contracts)

### Consistency Checks
- ✅ **Backlog Reference**: PRD must reference existing backlog item
- ✅ **PRD Reference**: Backlog item must reference PRD if it exists
- ✅ **Status Sync**: Status must match between backlog and PRD
- ✅ **Dependency Validity**: Referenced dependencies must exist

### Quality Checks
- ✅ **No Orphaned PRDs**: All PRDs must have backlog references
- ✅ **No Missing PRDs**: Backlog items mentioning PRDs must have PRD files
- ✅ **Complete Documentation**: All required fields must be populated

## Examples

### Example 1: Independent Feature
```markdown
**Backlog Item**: B-182
**Status**: Ready for Implementation
**Estimated Hours**: 4 hours

**Dependencies**:
- **Upstream**: None (can be implemented independently)
- **Downstream**: B-183 (Feature Refactor Framework depends on this)
- **Blocking**: None

**Impact Scope**:
- **Direct**: Debugging workflow, Cursor integration, CI validation
- **Indirect**: All future bugfixes, development velocity, regression prevention
- **Public Contracts**: None (internal tooling only)
```

### Example 2: Dependent Feature
```markdown
**Backlog Item**: B-183
**Status**: Ready for Implementation
**Estimated Hours**: 5 hours

**Dependencies**:
- **Upstream**: B-182 (Bug-Fix Playbook must be implemented first)
- **Downstream**: Future architectural changes, governance improvements
- **Blocking**: None

**Impact Scope**:
- **Direct**: Refactor workflow, consensus process, CI validation
- **Indirect**: All future refactors, architectural decisions, governance maturity
- **Public Contracts**: May affect system architecture and design patterns
```

## Troubleshooting

### Common Issues

#### "PRD missing backlog item reference"
**Cause**: PRD header doesn't include `**Backlog Item**: B-XXX`
**Solution**: Add the backlog item reference to the PRD header

#### "Backlog item has PRD but no reference"
**Cause**: Backlog item exists but doesn't reference its PRD in metadata
**Solution**: Add PRD reference to backlog item's reference_cards metadata

#### "Non-existent upstream dependency"
**Cause**: PRD references a backlog item that doesn't exist
**Solution**: Either create the missing backlog item or correct the dependency reference

#### "Status mismatch"
**Cause**: Status in PRD doesn't match status in backlog
**Solution**: Synchronize status between both files

### Validation Script Output

#### Success
```
✅ All PRD-Backlog linkages are valid!
🎉 PRD-Backlog linkage validation passed!
```

#### Errors
```
❌ Errors:
   - PRD PRD-B-XXX missing backlog item reference
   - PRD PRD-B-XXX references non-existent backlog item B-XXX

❌ Critical errors found. Please fix before proceeding.
```

#### Warnings
```
⚠️  Warnings:
   - Backlog item B-XXX has PRD but no reference in backlog metadata
   - PRD PRD-B-XXX references non-existent downstream dependency B-XXX

✅ No critical errors found, but check warnings above.
```

## Integration Points

### With Existing Workflows
- **PRD Creation**: `000_core/001_create-prd.md` includes enhanced header template
- **Backlog Management**: `100_memory/100_backlog-guide.md` includes linkage requirements
- **Task Generation**: `000_core/002_generate-tasks.md` can reference PRD dependencies
- **AI Execution**: `000_core/003_process-task-list.md` can validate dependencies

### With Development Tools
- **Cursor IDE**: `.cursorrules` enforces PRD standards
- **CI/CD**: Validation script can be integrated into build pipeline
- **Documentation**: Cross-references maintained automatically

## Best Practices

### Documentation
1. **Always include TL;DR section** for quick understanding
2. **Use clear, specific language** in dependency descriptions
3. **Keep impact scope descriptions concise** but comprehensive
4. **Update status promptly** when work progresses

### Validation
1. **Run validation script** after every PRD change
2. **Fix errors immediately** to prevent accumulation
3. **Review warnings regularly** to maintain quality
4. **Archive completed PRDs** to keep validation focused

### Maintenance
1. **Regular validation runs** to catch drift
2. **Dependency updates** as project evolves
3. **Status synchronization** between backlog and PRDs
4. **Archive cleanup** for completed items

## Future Enhancements

### Planned Features
- **Visual dependency graphs** for complex dependency chains
- **Impact analysis tools** for change assessment
- **Automated status updates** based on commit messages
- **Integration with project management tools**

### Potential Extensions
- **Risk assessment** based on dependency complexity
- **Resource planning** based on dependency chains
- **Timeline estimation** using dependency relationships
- **Change impact analysis** for architectural decisions

---

## Quick Reference

### Required PRD Header Format
```markdown
# PRD: [Title]

**Backlog Item**: B-XXX
**Status**: [Ready for Implementation | In Progress | Completed]
**Estimated Hours**: X hours

**Dependencies**:
- **Upstream**: [Items that must be completed first]
- **Downstream**: [Items that depend on this completion]
- **Blocking**: [Items that block this implementation]

**Impact Scope**:
- **Direct**: [Immediate changes required]
- **Indirect**: [Systems/components affected]
- **Public Contracts**: [APIs, schemas, interfaces changed]

## TL;DR
```

### Validation Command
```bash
python3 scripts/validate_prd_backlog_linkage.py
```

### Cursor Rule Location
- **File**: `.cursorrules`
- **Section**: "PRD-Backlog Linkage Requirements"
